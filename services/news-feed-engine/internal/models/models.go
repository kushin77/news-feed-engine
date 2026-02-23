// Package models defines the data structures for the News Feed Engine
package models

import (
	"database/sql/driver"
	"encoding/json"
	"time"

	"github.com/google/uuid"
)

// Platform represents content source platforms
type Platform string

const (
	PlatformYouTube  Platform = "youtube"
	PlatformTwitter  Platform = "twitter"
	PlatformReddit   Platform = "reddit"
	PlatformRSS      Platform = "rss"
	PlatformInternal Platform = "internal"
)

// ContentType represents the type of content
type ContentType string

const (
	ContentTypeArticle    ContentType = "article"
	ContentTypeVideo      ContentType = "video"
	ContentTypePost       ContentType = "post"
	ContentTypePodcast    ContentType = "podcast"
	ContentTypeNewsletter ContentType = "newsletter"
)

// CreatorTier represents creator verification tiers
type CreatorTier string

const (
	CreatorTierPlatinum   CreatorTier = "platinum"
	CreatorTierGold       CreatorTier = "gold"
	CreatorTierSilver     CreatorTier = "silver"
	CreatorTierBronze     CreatorTier = "bronze"
	CreatorTierUnverified CreatorTier = "unverified"
)

// GeoClassification represents geographic classification
type GeoClassification string

const (
	GeoLocal    GeoClassification = "local"
	GeoRegional GeoClassification = "regional"
	GeNational  GeoClassification = "national"
	GeoGlobal   GeoClassification = "global"
)

// ProcessingStatus represents content processing status
type ProcessingStatus string

const (
	StatusPending    ProcessingStatus = "pending"
	StatusProcessing ProcessingStatus = "processing"
	StatusCompleted  ProcessingStatus = "completed"
	StatusFailed     ProcessingStatus = "failed"
)

// JSONB is a custom type for PostgreSQL JSONB columns
type JSONB map[string]interface{}

// Value implements driver.Valuer for JSONB
func (j JSONB) Value() (driver.Value, error) {
	return json.Marshal(j)
}

// Scan implements sql.Scanner for JSONB
func (j *JSONB) Scan(value interface{}) error {
	if value == nil {
		*j = nil
		return nil
	}
	return json.Unmarshal(value.([]byte), j)
}

// Float32Slice is a custom type for PostgreSQL vector columns
type Float32Slice []float32

// Value implements driver.Valuer for Float32Slice
func (f Float32Slice) Value() (driver.Value, error) {
	return json.Marshal(f)
}

// Scan implements sql.Scanner for Float32Slice
func (f *Float32Slice) Scan(value interface{}) error {
	if value == nil {
		*f = nil
		return nil
	}
	return json.Unmarshal(value.([]byte), f)
}

// Creator represents a content creator
type Creator struct {
	ID              uuid.UUID   `json:"id" db:"id"`
	TenantID        string      `json:"tenant_id" db:"tenant_id"`
	Name            string      `json:"name" db:"name"`
	Platform        Platform    `json:"platform" db:"platform"`
	PlatformID      string      `json:"platform_id" db:"platform_id"`
	AvatarURL       string      `json:"avatar_url,omitempty" db:"avatar_url"`
	Bio             string      `json:"bio,omitempty" db:"bio"`
	Tier            CreatorTier `json:"tier" db:"tier"`
	VerifiedAt      *time.Time  `json:"verified_at,omitempty" db:"verified_at"`
	FollowerCount   int64       `json:"follower_count" db:"follower_count"`
	ContentCount    int         `json:"content_count" db:"content_count"`
	EngagementRate  float64     `json:"engagement_rate" db:"engagement_rate"`
	TopicsExpertise []string    `json:"topics_expertise,omitempty" db:"topics_expertise"`
	SocialLinks     JSONB       `json:"social_links,omitempty" db:"social_links"`
	Metadata        JSONB       `json:"metadata,omitempty" db:"metadata"`
	Active          bool        `json:"active" db:"active"`
	CreatedAt       time.Time   `json:"created_at" db:"created_at"`
	UpdatedAt       time.Time   `json:"updated_at" db:"updated_at"`
}

// Content represents aggregated content from various sources
type Content struct {
	ID                uuid.UUID         `json:"id" db:"id"`
	TenantID          string            `json:"tenant_id" db:"tenant_id"`
	CreatorID         uuid.UUID         `json:"creator_id" db:"creator_id"`
	Platform          Platform          `json:"platform" db:"platform"`
	PlatformContentID string            `json:"platform_content_id" db:"platform_content_id"`
	ContentType       ContentType       `json:"content_type" db:"content_type"`
	Title             string            `json:"title" db:"title"`
	Description       string            `json:"description,omitempty" db:"description"`
	OriginalURL       string            `json:"original_url" db:"original_url"`
	ThumbnailURL      string            `json:"thumbnail_url,omitempty" db:"thumbnail_url"`
	Summary           string            `json:"summary,omitempty" db:"summary"`
	Category          string            `json:"category,omitempty" db:"category"`
	Tags              []string          `json:"tags,omitempty" db:"tags"`
	GeoClassification GeoClassification `json:"geo_classification" db:"geo_classification"`
	SourceLocation    string            `json:"source_location,omitempty" db:"source_location"`
	Sentiment         float64           `json:"sentiment" db:"sentiment"`
	QualityScore      float64           `json:"quality_score" db:"quality_score"`
	EngagementScore   float64           `json:"engagement_score" db:"engagement_score"`
	ViewCount         int64             `json:"view_count" db:"view_count"`
	LikeCount         int64             `json:"like_count" db:"like_count"`
	CommentCount      int64             `json:"comment_count" db:"comment_count"`
	ShareCount        int64             `json:"share_count" db:"share_count"`
	ProcessingStatus  ProcessingStatus  `json:"processing_status" db:"processing_status"`
	ProcessedAt       *time.Time        `json:"processed_at,omitempty" db:"processed_at"`
	PublishedAt       time.Time         `json:"published_at" db:"published_at"`
	Embedding         Float32Slice      `json:"-" db:"embedding"`
	RawContent        JSONB             `json:"-" db:"raw_content"`
	AIAnalysis        JSONB             `json:"ai_analysis,omitempty" db:"ai_analysis"`
	Metadata          JSONB             `json:"metadata,omitempty" db:"metadata"`
	FeaturedUntil     *time.Time        `json:"featured_until,omitempty" db:"featured_until"`
	CreatedAt         time.Time         `json:"created_at" db:"created_at"`
	UpdatedAt         time.Time         `json:"updated_at" db:"updated_at"`

	// Joined fields (not stored in DB)
	Creator *Creator `json:"creator,omitempty" db:"-"`
}

// VideoSummary represents an AI-generated video summary
type VideoSummary struct {
	ID             uuid.UUID        `json:"id" db:"id"`
	TenantID       string           `json:"tenant_id" db:"tenant_id"`
	ContentID      uuid.UUID        `json:"content_id" db:"content_id"`
	Title          string           `json:"title" db:"title"`
	Script         string           `json:"script" db:"script"`
	VoiceID        string           `json:"voice_id" db:"voice_id"`
	AvatarID       string           `json:"avatar_id,omitempty" db:"avatar_id"`
	VideoURL       string           `json:"video_url,omitempty" db:"video_url"`
	ThumbnailURL   string           `json:"thumbnail_url,omitempty" db:"thumbnail_url"`
	Duration       int              `json:"duration" db:"duration"`
	FileSize       int64            `json:"file_size" db:"file_size"`
	Resolution     string           `json:"resolution" db:"resolution"`
	Format         string           `json:"format" db:"format"`
	Status         ProcessingStatus `json:"status" db:"status"`
	ErrorMessage   string           `json:"error_message,omitempty" db:"error_message"`
	ViewCount      int64            `json:"view_count" db:"view_count"`
	LikeCount      int64            `json:"like_count" db:"like_count"`
	ShareCount     int64            `json:"share_count" db:"share_count"`
	GeneratedAt    *time.Time       `json:"generated_at,omitempty" db:"generated_at"`
	GenerationTime int              `json:"generation_time" db:"generation_time"`
	Metadata       JSONB            `json:"metadata,omitempty" db:"metadata"`
	CreatedAt      time.Time        `json:"created_at" db:"created_at"`
	UpdatedAt      time.Time        `json:"updated_at" db:"updated_at"`

	// Joined fields
	Content *Content `json:"content,omitempty" db:"-"`
}

// VideoQueueStats represents video generation queue statistics
type VideoQueueStats struct {
	TenantID   string `json:"tenant_id"`
	Queued     int    `json:"queued"`
	Processing int    `json:"processing"`
	Completed  int    `json:"completed"`
	Failed     int    `json:"failed"`
}

// TenantConfig represents white-label tenant configuration
type TenantConfig struct {
	ID                uuid.UUID `json:"id" db:"id"`
	TenantID          string    `json:"tenant_id" db:"tenant_id"`
	DisplayName       string    `json:"display_name" db:"display_name"`
	LogoURL           string    `json:"logo_url,omitempty" db:"logo_url"`
	FaviconURL        string    `json:"favicon_url,omitempty" db:"favicon_url"`
	PrimaryColor      string    `json:"primary_color" db:"primary_color"`
	SecondaryColor    string    `json:"secondary_color" db:"secondary_color"`
	AccentColor       string    `json:"accent_color" db:"accent_color"`
	FontFamily        string    `json:"font_family" db:"font_family"`
	CustomCSS         string    `json:"custom_css,omitempty" db:"custom_css"`
	CustomDomain      string    `json:"custom_domain,omitempty" db:"custom_domain"`
	EnabledPlatforms  []string  `json:"enabled_platforms" db:"enabled_platforms"`
	EnabledCategories []string  `json:"enabled_categories" db:"enabled_categories"`
	DefaultVoiceID    string    `json:"default_voice_id" db:"default_voice_id"`
	VideoWatermark    string    `json:"video_watermark,omitempty" db:"video_watermark"`
	AnalyticsID       string    `json:"analytics_id,omitempty" db:"analytics_id"`
	Settings          JSONB     `json:"settings,omitempty" db:"settings"`
	Active            bool      `json:"active" db:"active"`
	CreatedAt         time.Time `json:"created_at" db:"created_at"`
	UpdatedAt         time.Time `json:"updated_at" db:"updated_at"`
}

// ContentSource represents a configurable content source
type ContentSource struct {
	ID            uuid.UUID  `json:"id" db:"id"`
	TenantID      string     `json:"tenant_id" db:"tenant_id"`
	Name          string     `json:"name" db:"name"`
	Platform      Platform   `json:"platform" db:"platform"`
	SourceType    string     `json:"source_type" db:"source_type"`
	Identifier    string     `json:"identifier" db:"identifier"`
	Category      string     `json:"category" db:"category"`
	Priority      int        `json:"priority" db:"priority"`
	IngestionCron string     `json:"ingestion_cron" db:"ingestion_cron"`
	LastIngested  *time.Time `json:"last_ingested,omitempty" db:"last_ingested"`
	ItemCount     int        `json:"item_count" db:"item_count"`
	ErrorCount    int        `json:"error_count" db:"error_count"`
	LastError     string     `json:"last_error,omitempty" db:"last_error"`
	Config        JSONB      `json:"config,omitempty" db:"config"`
	Active        bool       `json:"active" db:"active"`
	CreatedAt     time.Time  `json:"created_at" db:"created_at"`
	UpdatedAt     time.Time  `json:"updated_at" db:"updated_at"`
}

// VideoTemplate represents a video generation template
type VideoTemplate struct {
	ID           uuid.UUID `json:"id" db:"id"`
	TenantID     string    `json:"tenant_id" db:"tenant_id"`
	Name         string    `json:"name" db:"name"`
	Description  string    `json:"description,omitempty" db:"description"`
	Category     string    `json:"category" db:"category"`
	VoiceID      string    `json:"voice_id" db:"voice_id"`
	AvatarID     string    `json:"avatar_id,omitempty" db:"avatar_id"`
	Resolution   string    `json:"resolution" db:"resolution"`
	Duration     int       `json:"duration" db:"duration"`
	IntroScript  string    `json:"intro_script,omitempty" db:"intro_script"`
	OutroScript  string    `json:"outro_script,omitempty" db:"outro_script"`
	MusicTrack   string    `json:"music_track,omitempty" db:"music_track"`
	WatermarkURL string    `json:"watermark_url,omitempty" db:"watermark_url"`
	Config       JSONB     `json:"config,omitempty" db:"config"`
	IsDefault    bool      `json:"is_default" db:"is_default"`
	Active       bool      `json:"active" db:"active"`
	CreatedAt    time.Time `json:"created_at" db:"created_at"`
	UpdatedAt    time.Time `json:"updated_at" db:"updated_at"`
}
