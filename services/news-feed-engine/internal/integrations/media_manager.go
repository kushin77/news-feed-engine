package integrations

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"go.uber.org/zap"
)

// MediaManagerClient provides integration with the Media Manager service
type MediaManagerClient struct {
	baseURL    string
	apiKey     string
	tenantID   string
	httpClient *http.Client
	logger     *zap.Logger
}

// MediaAsset represents a unified asset across the platform
type MediaAsset struct {
	ID             string            `json:"id"`
	TenantID       string            `json:"tenant_id"`
	Type           string            `json:"type"` // image, video, audio, document
	SourcePlatform string            `json:"source_platform"`
	URLs           AssetURLs         `json:"urls"`
	Filename       string            `json:"filename"`
	FileSize       int64             `json:"file_size"`
	MimeType       string            `json:"mime_type"`
	Width          *int              `json:"width,omitempty"`
	Height         *int              `json:"height,omitempty"`
	Duration       *float64          `json:"duration,omitempty"`
	AIAnalysis     *AIAssetAnalysis  `json:"ai_analysis,omitempty"`
	UsageRights    *UsageRights      `json:"usage_rights,omitempty"`
	Performance    *AssetPerformance `json:"performance,omitempty"`
	CustomTags     []string          `json:"custom_tags"`
	Metadata       map[string]any    `json:"metadata"`
	CreatedAt      time.Time         `json:"created_at"`
	UpdatedAt      time.Time         `json:"updated_at"`
}

// AssetURLs contains URLs for different versions of an asset
type AssetURLs struct {
	Original   string            `json:"original"`
	CDN        string            `json:"cdn"`
	Thumbnails map[string]string `json:"thumbnails"` // small, medium, large
	Optimized  map[string]string `json:"optimized"`  // webp, avif, etc
	Transcoded map[string]string `json:"transcoded"` // various resolutions
}

// AIAssetAnalysis contains AI-generated analysis of a media asset
type AIAssetAnalysis struct {
	Objects          []DetectedObject `json:"objects"`
	Scenes           []string         `json:"scenes"`
	Colors           ColorPalette     `json:"colors"`
	Text             []ExtractedText  `json:"text"`
	Faces            []DetectedFace   `json:"faces"`
	BrandSafetyScore float64          `json:"brand_safety_score"`
	ContentRating    string           `json:"content_rating"`
	AutoTags         []string         `json:"auto_tags"`
	Embeddings       []float32        `json:"embeddings,omitempty"`
}

// DetectedObject represents an object detected in media
type DetectedObject struct {
	Label       string  `json:"label"`
	Confidence  float64 `json:"confidence"`
	BoundingBox *struct {
		X      float64 `json:"x"`
		Y      float64 `json:"y"`
		Width  float64 `json:"width"`
		Height float64 `json:"height"`
	} `json:"bounding_box,omitempty"`
}

// ColorPalette represents the dominant colors in media
type ColorPalette struct {
	Dominant   string   `json:"dominant"`
	Primary    []string `json:"primary"`
	Accent     []string `json:"accent"`
	Background string   `json:"background"`
}

// ExtractedText represents text extracted from media
type ExtractedText struct {
	Text       string  `json:"text"`
	Confidence float64 `json:"confidence"`
	Language   string  `json:"language"`
}

// DetectedFace represents a face detected in media
type DetectedFace struct {
	Confidence float64 `json:"confidence"`
	Emotion    string  `json:"emotion,omitempty"`
	Age        *int    `json:"age,omitempty"`
}

// UsageRights contains usage rights information for an asset
type UsageRights struct {
	Type                string    `json:"type"` // owned, licensed, creative_commons
	LicenseName         string    `json:"license_name,omitempty"`
	AttributionRequired bool      `json:"attribution_required"`
	AttributionText     string    `json:"attribution_text,omitempty"`
	ExpiresAt           time.Time `json:"expires_at,omitempty"`
	AllowedPlatforms    []string  `json:"allowed_platforms"`
	Restrictions        []string  `json:"restrictions"`
}

// AssetPerformance contains performance metrics for an asset
type AssetPerformance struct {
	UsageCount             int       `json:"usage_count"`
	AvgEngagementRate      float64   `json:"avg_engagement_rate"`
	BestPerformingPlatform string    `json:"best_performing_platform,omitempty"`
	LastUsed               time.Time `json:"last_used,omitempty"`
}

// RecommendedAsset contains an asset with recommendation context
type RecommendedAsset struct {
	Asset                   MediaAsset `json:"asset"`
	RelevanceScore          float64    `json:"relevance_score"`
	UsageSuggestion         string     `json:"usage_suggestion"`
	PlacementRecommendation string     `json:"placement_recommendation"`
}

// NewMediaManagerClient creates a new Media Manager client
func NewMediaManagerClient(baseURL, apiKey, tenantID string, logger *zap.Logger) *MediaManagerClient {
	return &MediaManagerClient{
		baseURL:  baseURL,
		apiKey:   apiKey,
		tenantID: tenantID,
		httpClient: &http.Client{
			Timeout: 30 * time.Second,
		},
		logger: logger,
	}
}

// GetAsset retrieves an asset by ID
func (c *MediaManagerClient) GetAsset(ctx context.Context, assetID string) (*MediaAsset, error) {
	req, err := c.newRequest(ctx, "GET", fmt.Sprintf("/api/v1/assets/%s", assetID), nil)
	if err != nil {
		return nil, err
	}

	var asset MediaAsset
	if err := c.doRequest(req, &asset); err != nil {
		return nil, err
	}

	return &asset, nil
}

// ListAssets lists assets with optional filtering
type ListAssetsOptions struct {
	Type   string   `json:"type,omitempty"`
	Tags   []string `json:"tags,omitempty"`
	Limit  int      `json:"limit,omitempty"`
	Offset int      `json:"offset,omitempty"`
}

type ListAssetsResponse struct {
	Items []MediaAsset `json:"items"`
	Total int          `json:"total"`
}

func (c *MediaManagerClient) ListAssets(ctx context.Context, opts ListAssetsOptions) (*ListAssetsResponse, error) {
	url := "/api/v1/assets"
	params := []string{}

	if opts.Type != "" {
		params = append(params, fmt.Sprintf("type=%s", opts.Type))
	}
	if opts.Limit > 0 {
		params = append(params, fmt.Sprintf("limit=%d", opts.Limit))
	}
	if opts.Offset > 0 {
		params = append(params, fmt.Sprintf("offset=%d", opts.Offset))
	}

	if len(params) > 0 {
		url += "?" + joinParams(params)
	}

	req, err := c.newRequest(ctx, "GET", url, nil)
	if err != nil {
		return nil, err
	}

	var response ListAssetsResponse
	if err := c.doRequest(req, &response); err != nil {
		return nil, err
	}

	return &response, nil
}

// SemanticSearch performs semantic search for assets
type SemanticSearchRequest struct {
	Query     string    `json:"query,omitempty"`
	Embedding []float32 `json:"embedding,omitempty"`
	Type      string    `json:"type,omitempty"`
	Limit     int       `json:"limit,omitempty"`
}

func (c *MediaManagerClient) SemanticSearch(ctx context.Context, search SemanticSearchRequest) ([]MediaAsset, error) {
	body, err := json.Marshal(search)
	if err != nil {
		return nil, err
	}

	req, err := c.newRequest(ctx, "POST", "/api/v1/assets/search/semantic", bytes.NewReader(body))
	if err != nil {
		return nil, err
	}

	var response struct {
		Items []MediaAsset `json:"items"`
	}
	if err := c.doRequest(req, &response); err != nil {
		return nil, err
	}

	return response.Items, nil
}

// GetRecommendations gets asset recommendations for content
type RecommendationRequest struct {
	ContentText     string `json:"content_text"`
	ContentCategory string `json:"content_category"`
	AssetType       string `json:"asset_type,omitempty"`
	UsagePurpose    string `json:"usage_purpose,omitempty"`
	Limit           int    `json:"limit,omitempty"`
}

func (c *MediaManagerClient) GetRecommendations(ctx context.Context, req RecommendationRequest) ([]RecommendedAsset, error) {
	body, err := json.Marshal(req)
	if err != nil {
		return nil, err
	}

	httpReq, err := c.newRequest(ctx, "POST", "/api/v1/assets/recommend", bytes.NewReader(body))
	if err != nil {
		return nil, err
	}

	var response struct {
		Recommendations []RecommendedAsset `json:"recommendations"`
	}
	if err := c.doRequest(httpReq, &response); err != nil {
		return nil, err
	}

	return response.Recommendations, nil
}

// UploadAsset uploads a new asset
type UploadAssetRequest struct {
	FileData []byte         `json:"-"`
	Filename string         `json:"filename"`
	Type     string         `json:"type"`
	Tags     []string       `json:"tags,omitempty"`
	Metadata map[string]any `json:"metadata,omitempty"`
}

func (c *MediaManagerClient) UploadAsset(ctx context.Context, upload UploadAssetRequest) (*MediaAsset, error) {
	// For multipart upload, we'd use a different implementation
	// This is a placeholder showing the structure

	c.logger.Info("Uploading asset to Media Manager",
		zap.String("filename", upload.Filename),
		zap.String("type", upload.Type),
		zap.Int("size", len(upload.FileData)),
	)

	// Placeholder - actual implementation would use multipart form
	return nil, fmt.Errorf("upload not implemented - use multipart form")
}

// AnalyzeAsset triggers AI analysis for an asset
func (c *MediaManagerClient) AnalyzeAsset(ctx context.Context, assetID string) (*AIAssetAnalysis, error) {
	req, err := c.newRequest(ctx, "POST", fmt.Sprintf("/api/v1/assets/%s/analyze", assetID), nil)
	if err != nil {
		return nil, err
	}

	var analysis AIAssetAnalysis
	if err := c.doRequest(req, &analysis); err != nil {
		return nil, err
	}

	return &analysis, nil
}

// SyncAssetFromContent syncs an asset from content
func (c *MediaManagerClient) SyncAssetFromContent(ctx context.Context, content *UnifiedContent) (*MediaAsset, error) {
	// Determine asset type from content type
	assetType := "image"
	if content.ContentType == "video" {
		assetType = "video"
	}

	// Build asset metadata
	metadata := map[string]any{
		"source_platform": content.Platform,
		"source_id":       content.ID,
		"source_url":      content.URL,
		"author_id":       content.AuthorID,
		"author_name":     content.AuthorName,
	}

	// Create asset record
	body, err := json.Marshal(map[string]any{
		"url":       content.ThumbnailURL,
		"type":      assetType,
		"tags":      content.Tags,
		"metadata":  metadata,
		"source_id": content.ID,
	})
	if err != nil {
		return nil, err
	}

	req, err := c.newRequest(ctx, "POST", "/api/v1/assets/sync", bytes.NewReader(body))
	if err != nil {
		return nil, err
	}

	var asset MediaAsset
	if err := c.doRequest(req, &asset); err != nil {
		return nil, err
	}

	c.logger.Info("Asset synced to Media Manager",
		zap.String("asset_id", asset.ID),
		zap.String("content_id", content.ID),
	)

	return &asset, nil
}

// Helper methods

func (c *MediaManagerClient) newRequest(ctx context.Context, method, path string, body io.Reader) (*http.Request, error) {
	url := c.baseURL + path
	req, err := http.NewRequestWithContext(ctx, method, url, body)
	if err != nil {
		return nil, err
	}

	req.Header.Set("Authorization", "Bearer "+c.apiKey)
	req.Header.Set("X-Tenant-ID", c.tenantID)
	req.Header.Set("Content-Type", "application/json")

	return req, nil
}

func (c *MediaManagerClient) doRequest(req *http.Request, result any) error {
	resp, err := c.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("API error %d: %s", resp.StatusCode, string(body))
	}

	if result != nil {
		if err := json.NewDecoder(resp.Body).Decode(result); err != nil {
			return fmt.Errorf("failed to decode response: %w", err)
		}
	}

	return nil
}

func joinParams(params []string) string {
	result := ""
	for i, p := range params {
		if i > 0 {
			result += "&"
		}
		result += p
	}
	return result
}

// MediaManagerIntegration provides high-level integration methods
type MediaManagerIntegration struct {
	client     *MediaManagerClient
	cdnManager *CDNManager
	aiAnalyzer *AIAssetAnalyzer
	logger     *zap.Logger
}

// CDNManager manages CDN uploads and optimizations
type CDNManager struct {
	cdnBaseURL string
	cdnAPIKey  string
	logger     *zap.Logger
}

// AIAssetAnalyzer provides AI analysis for assets
type AIAssetAnalyzer struct {
	logger *zap.Logger
}

// NewMediaManagerIntegration creates a new integration instance
func NewMediaManagerIntegration(
	baseURL, apiKey, tenantID string,
	cdnBaseURL, cdnAPIKey string,
	logger *zap.Logger,
) *MediaManagerIntegration {
	return &MediaManagerIntegration{
		client: NewMediaManagerClient(baseURL, apiKey, tenantID, logger),
		cdnManager: &CDNManager{
			cdnBaseURL: cdnBaseURL,
			cdnAPIKey:  cdnAPIKey,
			logger:     logger,
		},
		aiAnalyzer: &AIAssetAnalyzer{logger: logger},
		logger:     logger,
	}
}

// SyncAsset performs full asset sync workflow
func (m *MediaManagerIntegration) SyncAsset(ctx context.Context, content *UnifiedContent) (*MediaAsset, error) {
	m.logger.Info("Starting asset sync",
		zap.String("content_id", content.ID),
		zap.String("platform", content.Platform),
	)

	// 1. Sync to Media Manager
	asset, err := m.client.SyncAssetFromContent(ctx, content)
	if err != nil {
		return nil, fmt.Errorf("failed to sync asset: %w", err)
	}

	// 2. Trigger AI analysis
	analysis, err := m.client.AnalyzeAsset(ctx, asset.ID)
	if err != nil {
		m.logger.Warn("AI analysis failed, continuing without it",
			zap.String("asset_id", asset.ID),
			zap.Error(err),
		)
	} else {
		asset.AIAnalysis = analysis
	}

	m.logger.Info("Asset sync complete",
		zap.String("asset_id", asset.ID),
	)

	return asset, nil
}

// GetRecommendationsForContent gets asset recommendations for content
func (m *MediaManagerIntegration) GetRecommendationsForContent(
	ctx context.Context,
	content *UnifiedContent,
	assetType string,
	limit int,
) ([]RecommendedAsset, error) {
	req := RecommendationRequest{
		ContentText:     content.Title + " " + content.Description,
		ContentCategory: getCategory(content),
		AssetType:       assetType,
		Limit:           limit,
	}

	return m.client.GetRecommendations(ctx, req)
}

func getCategory(content *UnifiedContent) string {
	if len(content.Categories) > 0 {
		return content.Categories[0]
	}
	return "general"
}
