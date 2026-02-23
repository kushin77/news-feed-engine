package integrations

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"time"

	"go.uber.org/zap"
)

// BlogIntegration handles integration with the ElevatedIQ blog platform
type BlogIntegration struct {
	baseURL    string
	apiKey     string
	httpClient *http.Client
	logger     *zap.Logger
}

// BlogPost represents a blog post from the platform
type BlogPost struct {
	ID            string     `json:"id"`
	Title         string     `json:"title"`
	Slug          string     `json:"slug"`
	Excerpt       string     `json:"excerpt"`
	Content       string     `json:"content"`
	HTMLContent   string     `json:"html_content"`
	Author        BlogAuthor `json:"author"`
	Categories    []string   `json:"categories"`
	Tags          []string   `json:"tags"`
	FeaturedImage string     `json:"featured_image"`
	Status        string     `json:"status"` // draft, published, scheduled
	PublishedAt   time.Time  `json:"published_at"`
	CreatedAt     time.Time  `json:"created_at"`
	UpdatedAt     time.Time  `json:"updated_at"`
	ViewCount     int64      `json:"view_count"`
	LikeCount     int64      `json:"like_count"`
	CommentCount  int64      `json:"comment_count"`
	SEO           BlogSEO    `json:"seo"`
}

// BlogAuthor represents a blog author
type BlogAuthor struct {
	ID        string `json:"id"`
	Name      string `json:"name"`
	Email     string `json:"email"`
	AvatarURL string `json:"avatar_url"`
	Bio       string `json:"bio"`
}

// BlogSEO contains SEO metadata for a blog post
type BlogSEO struct {
	MetaTitle       string   `json:"meta_title"`
	MetaDescription string   `json:"meta_description"`
	MetaKeywords    []string `json:"meta_keywords"`
	CanonicalURL    string   `json:"canonical_url"`
	OGImage         string   `json:"og_image"`
}

// BlogComment represents a comment on a blog post
type BlogComment struct {
	ID        string    `json:"id"`
	PostID    string    `json:"post_id"`
	UserID    string    `json:"user_id"`
	UserName  string    `json:"user_name"`
	Content   string    `json:"content"`
	ParentID  string    `json:"parent_id,omitempty"`
	CreatedAt time.Time `json:"created_at"`
	LikeCount int       `json:"like_count"`
}

// BlogCategory represents a blog category
type BlogCategory struct {
	ID          string `json:"id"`
	Name        string `json:"name"`
	Slug        string `json:"slug"`
	Description string `json:"description"`
	PostCount   int    `json:"post_count"`
	ParentID    string `json:"parent_id,omitempty"`
}

// NewBlogIntegration creates a new blog integration
func NewBlogIntegration(baseURL, apiKey string, logger *zap.Logger) *BlogIntegration {
	return &BlogIntegration{
		baseURL: baseURL,
		apiKey:  apiKey,
		httpClient: &http.Client{
			Timeout: 30 * time.Second,
		},
		logger: logger,
	}
}

// GetPosts retrieves blog posts with filtering options
func (b *BlogIntegration) GetPosts(ctx context.Context, opts GetPostsOptions) ([]BlogPost, int, error) {
	params := url.Values{
		"page":     {fmt.Sprintf("%d", opts.Page)},
		"per_page": {fmt.Sprintf("%d", opts.PerPage)},
		"status":   {"published"},
	}

	if opts.Category != "" {
		params.Set("category", opts.Category)
	}
	if opts.Tag != "" {
		params.Set("tag", opts.Tag)
	}
	if opts.AuthorID != "" {
		params.Set("author_id", opts.AuthorID)
	}
	if opts.Search != "" {
		params.Set("search", opts.Search)
	}
	if !opts.Since.IsZero() {
		params.Set("since", opts.Since.Format(time.RFC3339))
	}
	if opts.SortBy != "" {
		params.Set("sort_by", opts.SortBy)
		params.Set("sort_order", opts.SortOrder)
	}

	resp, err := b.makeRequest(ctx, "GET", "/api/v1/posts", params, nil)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to get posts: %w", err)
	}

	var result struct {
		Posts []BlogPost `json:"posts"`
		Total int        `json:"total"`
	}

	if err := json.Unmarshal(resp, &result); err != nil {
		return nil, 0, fmt.Errorf("failed to parse posts response: %w", err)
	}

	return result.Posts, result.Total, nil
}

// GetPostsOptions contains options for filtering blog posts
type GetPostsOptions struct {
	Page      int
	PerPage   int
	Category  string
	Tag       string
	AuthorID  string
	Search    string
	Since     time.Time
	SortBy    string // created_at, published_at, view_count, like_count
	SortOrder string // asc, desc
}

// GetPost retrieves a single blog post by ID or slug
func (b *BlogIntegration) GetPost(ctx context.Context, idOrSlug string) (*BlogPost, error) {
	resp, err := b.makeRequest(ctx, "GET", fmt.Sprintf("/api/v1/posts/%s", idOrSlug), nil, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to get post: %w", err)
	}

	var post BlogPost
	if err := json.Unmarshal(resp, &post); err != nil {
		return nil, fmt.Errorf("failed to parse post response: %w", err)
	}

	return &post, nil
}

// GetCategories retrieves all blog categories
func (b *BlogIntegration) GetCategories(ctx context.Context) ([]BlogCategory, error) {
	resp, err := b.makeRequest(ctx, "GET", "/api/v1/categories", nil, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to get categories: %w", err)
	}

	var result struct {
		Categories []BlogCategory `json:"categories"`
	}

	if err := json.Unmarshal(resp, &result); err != nil {
		return nil, fmt.Errorf("failed to parse categories response: %w", err)
	}

	return result.Categories, nil
}

// GetComments retrieves comments for a blog post
func (b *BlogIntegration) GetComments(ctx context.Context, postID string, page, perPage int) ([]BlogComment, error) {
	params := url.Values{
		"page":     {fmt.Sprintf("%d", page)},
		"per_page": {fmt.Sprintf("%d", perPage)},
	}

	resp, err := b.makeRequest(ctx, "GET", fmt.Sprintf("/api/v1/posts/%s/comments", postID), params, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to get comments: %w", err)
	}

	var result struct {
		Comments []BlogComment `json:"comments"`
	}

	if err := json.Unmarshal(resp, &result); err != nil {
		return nil, fmt.Errorf("failed to parse comments response: %w", err)
	}

	return result.Comments, nil
}

// PublishToFeed publishes a content item to the news feed
func (b *BlogIntegration) PublishToFeed(ctx context.Context, post *BlogPost, tenantID string) error {
	payload := map[string]interface{}{
		"content_type":  "article",
		"source":        "blog",
		"source_id":     post.ID,
		"title":         post.Title,
		"summary":       post.Excerpt,
		"content":       post.Content,
		"source_url":    fmt.Sprintf("%s/blog/%s", b.baseURL, post.Slug),
		"thumbnail_url": post.FeaturedImage,
		"author_id":     post.Author.ID,
		"author_name":   post.Author.Name,
		"category":      getFirstCategory(post.Categories),
		"tags":          post.Tags,
		"published_at":  post.PublishedAt,
		"tenant_id":     tenantID,
	}

	_, err := b.makeRequest(ctx, "POST", "/api/v1/content/import", nil, payload)
	if err != nil {
		return fmt.Errorf("failed to publish to feed: %w", err)
	}

	return nil
}

// WebhookPayload represents a webhook payload from the blog
type WebhookPayload struct {
	Event     string    `json:"event"` // post.created, post.updated, post.published, post.deleted
	Timestamp time.Time `json:"timestamp"`
	Post      BlogPost  `json:"post"`
	TenantID  string    `json:"tenant_id"`
}

// HandleWebhook processes incoming webhooks from the blog platform
func (b *BlogIntegration) HandleWebhook(payload *WebhookPayload) error {
	switch payload.Event {
	case "post.published":
		b.logger.Info("Blog post published",
			zap.String("post_id", payload.Post.ID),
			zap.String("title", payload.Post.Title),
			zap.String("tenant_id", payload.TenantID),
		)
		// This would trigger content ingestion
		return nil

	case "post.updated":
		b.logger.Info("Blog post updated",
			zap.String("post_id", payload.Post.ID),
			zap.String("title", payload.Post.Title),
		)
		return nil

	case "post.deleted":
		b.logger.Info("Blog post deleted",
			zap.String("post_id", payload.Post.ID),
		)
		// This would trigger content removal from feed
		return nil

	default:
		b.logger.Debug("Unhandled blog webhook event",
			zap.String("event", payload.Event),
		)
		return nil
	}
}

// makeRequest makes an HTTP request to the blog API
func (b *BlogIntegration) makeRequest(ctx context.Context, method, endpoint string, params url.Values, body interface{}) ([]byte, error) {
	apiURL := b.baseURL + endpoint
	if params != nil {
		apiURL += "?" + params.Encode()
	}

	var bodyReader *jsonReader
	if body != nil {
		bodyReader = newJSONReader(body)
	}

	req, err := http.NewRequestWithContext(ctx, method, apiURL, bodyReader)
	if err != nil {
		return nil, err
	}

	req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", b.apiKey))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Accept", "application/json")

	resp, err := b.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	respBody, err := readBody(resp)
	if err != nil {
		return nil, err
	}

	if resp.StatusCode >= 400 {
		return nil, fmt.Errorf("blog API error: %s - %s", resp.Status, string(respBody))
	}

	return respBody, nil
}

// Helper functions
func getFirstCategory(categories []string) string {
	if len(categories) > 0 {
		return categories[0]
	}
	return "general"
}

type jsonReader struct {
	data []byte
	pos  int
}

func newJSONReader(v interface{}) *jsonReader {
	data, _ := json.Marshal(v)
	return &jsonReader{data: data}
}

func (r *jsonReader) Read(p []byte) (n int, err error) {
	if r.pos >= len(r.data) {
		return 0, http.ErrBodyReadAfterClose
	}
	n = copy(p, r.data[r.pos:])
	r.pos += n
	return n, nil
}

func readBody(resp *http.Response) ([]byte, error) {
	body := make([]byte, 0, 1024)
	buf := make([]byte, 1024)
	for {
		n, err := resp.Body.Read(buf)
		if n > 0 {
			body = append(body, buf[:n]...)
		}
		if err != nil {
			break
		}
	}
	return body, nil
}
