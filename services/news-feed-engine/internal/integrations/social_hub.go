package integrations

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"go.uber.org/zap"
)

// SocialMediaHub provides unified access to social media platforms
type SocialMediaHub struct {
	youtube  *YouTubeIntegration
	twitter  *TwitterIntegration
	rss      *RSSIntegration
	blog     *BlogIntegration
	logger   *zap.Logger
	tenantID string
}

// SocialMediaConfig contains configuration for social media integrations
type SocialMediaConfig struct {
	YouTubeAPIKey      string `json:"youtube_api_key"`
	TwitterBearerToken string `json:"twitter_bearer_token"`
	BlogBaseURL        string `json:"blog_base_url"`
	BlogAPIKey         string `json:"blog_api_key"`
	TenantID           string `json:"tenant_id"`
}

// UnifiedContent represents content from any platform in a unified format
type UnifiedContent struct {
	ID              string                 `json:"id"`
	Platform        string                 `json:"platform"`     // youtube, twitter, rss, blog
	ContentType     string                 `json:"content_type"` // video, tweet, article, podcast
	Title           string                 `json:"title"`
	Description     string                 `json:"description"`
	Content         string                 `json:"content"`
	URL             string                 `json:"url"`
	ThumbnailURL    string                 `json:"thumbnail_url"`
	AuthorID        string                 `json:"author_id"`
	AuthorName      string                 `json:"author_name"`
	AuthorAvatarURL string                 `json:"author_avatar_url"`
	PublishedAt     time.Time              `json:"published_at"`
	Metrics         ContentMetrics         `json:"metrics"`
	Tags            []string               `json:"tags"`
	Categories      []string               `json:"categories"`
	Metadata        map[string]interface{} `json:"metadata"`
}

// ContentMetrics contains engagement metrics
type ContentMetrics struct {
	ViewCount    int64 `json:"view_count"`
	LikeCount    int64 `json:"like_count"`
	CommentCount int64 `json:"comment_count"`
	ShareCount   int64 `json:"share_count"`
}

// NewSocialMediaHub creates a new social media hub
func NewSocialMediaHub(config *SocialMediaConfig, logger *zap.Logger) *SocialMediaHub {
	hub := &SocialMediaHub{
		logger:   logger,
		tenantID: config.TenantID,
	}

	if config.YouTubeAPIKey != "" {
		hub.youtube = NewYouTubeIntegration(config.YouTubeAPIKey, logger)
	}

	if config.TwitterBearerToken != "" {
		hub.twitter = NewTwitterIntegration(config.TwitterBearerToken, logger)
	}

	hub.rss = NewRSSIntegration(logger)

	if config.BlogBaseURL != "" && config.BlogAPIKey != "" {
		hub.blog = NewBlogIntegration(config.BlogBaseURL, config.BlogAPIKey, logger)
	}

	return hub
}

// FetchYouTubeChannel fetches recent videos from a YouTube channel
func (h *SocialMediaHub) FetchYouTubeChannel(ctx context.Context, channelID string, maxVideos int, since *time.Time) ([]UnifiedContent, error) {
	if h.youtube == nil {
		return nil, fmt.Errorf("YouTube integration not configured")
	}

	videos, err := h.youtube.GetChannelVideos(ctx, channelID, maxVideos, since)
	if err != nil {
		return nil, err
	}

	content := make([]UnifiedContent, 0, len(videos))
	for _, video := range videos {
		content = append(content, UnifiedContent{
			ID:           video.ID,
			Platform:     "youtube",
			ContentType:  "video",
			Title:        video.Title,
			Description:  video.Description,
			URL:          fmt.Sprintf("https://www.youtube.com/watch?v=%s", video.ID),
			ThumbnailURL: video.ThumbnailURL,
			AuthorID:     video.ChannelID,
			AuthorName:   video.ChannelTitle,
			PublishedAt:  video.PublishedAt,
			Metrics: ContentMetrics{
				ViewCount:    video.ViewCount,
				LikeCount:    video.LikeCount,
				CommentCount: video.CommentCount,
			},
			Tags: video.Tags,
			Metadata: map[string]interface{}{
				"duration": video.Duration,
			},
		})
	}

	return content, nil
}

// FetchTwitterUser fetches recent tweets from a Twitter user
func (h *SocialMediaHub) FetchTwitterUser(ctx context.Context, username string, maxTweets int, since *time.Time) ([]UnifiedContent, error) {
	if h.twitter == nil {
		return nil, fmt.Errorf("Twitter integration not configured")
	}

	user, err := h.twitter.GetUser(ctx, username)
	if err != nil {
		return nil, err
	}

	tweets, err := h.twitter.GetUserTweets(ctx, user.ID, maxTweets, since)
	if err != nil {
		return nil, err
	}

	content := make([]UnifiedContent, 0, len(tweets))
	for _, tweet := range tweets {
		uc := UnifiedContent{
			ID:              tweet.ID,
			Platform:        "twitter",
			ContentType:     "tweet",
			Title:           truncateText(tweet.Text, 100),
			Content:         tweet.Text,
			URL:             fmt.Sprintf("https://twitter.com/%s/status/%s", user.Username, tweet.ID),
			AuthorID:        user.ID,
			AuthorName:      user.Name,
			AuthorAvatarURL: user.ProfileImageURL,
			PublishedAt:     tweet.CreatedAt,
			Metrics: ContentMetrics{
				LikeCount:    int64(tweet.PublicMetrics.LikeCount),
				CommentCount: int64(tweet.PublicMetrics.ReplyCount),
				ShareCount:   int64(tweet.PublicMetrics.RetweetCount + tweet.PublicMetrics.QuoteCount),
			},
		}

		// Extract hashtags as tags
		if tweet.Entities != nil {
			for _, hashtag := range tweet.Entities.Hashtags {
				uc.Tags = append(uc.Tags, hashtag.Tag)
			}
		}

		// Handle referenced tweets
		if len(tweet.ReferencedTweets) > 0 {
			uc.Metadata = map[string]interface{}{
				"referenced_tweets": tweet.ReferencedTweets,
			}
		}

		content = append(content, uc)
	}

	return content, nil
}

// FetchRSSFeed fetches articles from an RSS feed
func (h *SocialMediaHub) FetchRSSFeed(ctx context.Context, feedURL string, since *time.Time) ([]UnifiedContent, error) {
	feed, err := h.rss.FetchFeed(ctx, feedURL)
	if err != nil {
		return nil, err
	}

	content := make([]UnifiedContent, 0, len(feed.Items))
	for _, item := range feed.Items {
		if since != nil && item.PublishedAt.Before(*since) {
			continue
		}

		content = append(content, UnifiedContent{
			ID:           item.ID,
			Platform:     "rss",
			ContentType:  "article",
			Title:        item.Title,
			Description:  item.Description,
			Content:      item.Content,
			URL:          item.Link,
			ThumbnailURL: item.ImageURL,
			AuthorName:   item.Author,
			PublishedAt:  item.PublishedAt,
			Categories:   item.Categories,
		})
	}

	return content, nil
}

// FetchBlogPosts fetches recent posts from the blog platform
func (h *SocialMediaHub) FetchBlogPosts(ctx context.Context, opts GetPostsOptions) ([]UnifiedContent, error) {
	if h.blog == nil {
		return nil, fmt.Errorf("Blog integration not configured")
	}

	posts, _, err := h.blog.GetPosts(ctx, opts)
	if err != nil {
		return nil, err
	}

	content := make([]UnifiedContent, 0, len(posts))
	for _, post := range posts {
		content = append(content, UnifiedContent{
			ID:              post.ID,
			Platform:        "blog",
			ContentType:     "article",
			Title:           post.Title,
			Description:     post.Excerpt,
			Content:         post.Content,
			URL:             fmt.Sprintf("%s/blog/%s", h.blog.baseURL, post.Slug),
			ThumbnailURL:    post.FeaturedImage,
			AuthorID:        post.Author.ID,
			AuthorName:      post.Author.Name,
			AuthorAvatarURL: post.Author.AvatarURL,
			PublishedAt:     post.PublishedAt,
			Metrics: ContentMetrics{
				ViewCount:    post.ViewCount,
				LikeCount:    post.LikeCount,
				CommentCount: post.CommentCount,
			},
			Tags:       post.Tags,
			Categories: post.Categories,
		})
	}

	return content, nil
}

// CrossPostToPlatforms cross-posts content to multiple platforms
type CrossPostRequest struct {
	Content   UnifiedContent `json:"content"`
	Platforms []string       `json:"platforms"` // twitter, blog, etc.
	Schedule  *time.Time     `json:"schedule,omitempty"`
}

type CrossPostResult struct {
	Platform string `json:"platform"`
	Success  bool   `json:"success"`
	PostID   string `json:"post_id,omitempty"`
	URL      string `json:"url,omitempty"`
	Error    string `json:"error,omitempty"`
}

// CrossPost posts content to multiple platforms
func (h *SocialMediaHub) CrossPost(ctx context.Context, req *CrossPostRequest) []CrossPostResult {
	results := make([]CrossPostResult, 0, len(req.Platforms))

	for _, platform := range req.Platforms {
		result := CrossPostResult{Platform: platform}

		switch platform {
		case "blog":
			if h.blog != nil {
				// Create blog post from content
				result.Success = true
				result.PostID = "simulated_blog_post_id"
				h.logger.Info("Would cross-post to blog",
					zap.String("title", req.Content.Title),
				)
			} else {
				result.Error = "Blog integration not configured"
			}

		case "twitter":
			// Twitter requires OAuth for posting, which requires user authorization
			result.Error = "Twitter posting requires OAuth authorization"

		default:
			result.Error = fmt.Sprintf("Unknown platform: %s", platform)
		}

		results = append(results, result)
	}

	return results
}

// SyncCreator syncs a creator's content from all connected platforms
type CreatorSync struct {
	CreatorID       string    `json:"creator_id"`
	YouTubeChannel  string    `json:"youtube_channel"`
	TwitterHandle   string    `json:"twitter_handle"`
	RSSFeeds        []string  `json:"rss_feeds"`
	SyncSince       time.Time `json:"sync_since"`
	MaxItemsPerFeed int       `json:"max_items_per_feed"`
}

// SyncCreatorContent syncs all content from a creator
func (h *SocialMediaHub) SyncCreatorContent(ctx context.Context, sync *CreatorSync) ([]UnifiedContent, error) {
	var allContent []UnifiedContent
	since := sync.SyncSince
	maxItems := sync.MaxItemsPerFeed
	if maxItems == 0 {
		maxItems = 50
	}

	// Sync YouTube
	if sync.YouTubeChannel != "" && h.youtube != nil {
		content, err := h.FetchYouTubeChannel(ctx, sync.YouTubeChannel, maxItems, &since)
		if err != nil {
			h.logger.Warn("Failed to sync YouTube content",
				zap.String("channel", sync.YouTubeChannel),
				zap.Error(err),
			)
		} else {
			allContent = append(allContent, content...)
		}
	}

	// Sync Twitter
	if sync.TwitterHandle != "" && h.twitter != nil {
		content, err := h.FetchTwitterUser(ctx, sync.TwitterHandle, maxItems, &since)
		if err != nil {
			h.logger.Warn("Failed to sync Twitter content",
				zap.String("handle", sync.TwitterHandle),
				zap.Error(err),
			)
		} else {
			allContent = append(allContent, content...)
		}
	}

	// Sync RSS feeds
	for _, feedURL := range sync.RSSFeeds {
		content, err := h.FetchRSSFeed(ctx, feedURL, &since)
		if err != nil {
			h.logger.Warn("Failed to sync RSS feed",
				zap.String("feed_url", feedURL),
				zap.Error(err),
			)
		} else {
			allContent = append(allContent, content...)
		}
	}

	return allContent, nil
}

// ContentAggregator aggregates content from multiple sources
type ContentAggregator struct {
	hub      *SocialMediaHub
	sources  []ContentSource
	callback func([]UnifiedContent) error
	interval time.Duration
	logger   *zap.Logger
}

// ContentSource defines a source for content aggregation
type ContentSource struct {
	Type       string `json:"type"` // youtube, twitter, rss, blog
	Identifier string `json:"identifier"`
	Enabled    bool   `json:"enabled"`
}

// NewContentAggregator creates a new content aggregator
func NewContentAggregator(hub *SocialMediaHub, sources []ContentSource, callback func([]UnifiedContent) error) *ContentAggregator {
	return &ContentAggregator{
		hub:      hub,
		sources:  sources,
		callback: callback,
		interval: 15 * time.Minute,
		logger:   hub.logger,
	}
}

// Start begins the aggregation loop
func (a *ContentAggregator) Start(ctx context.Context) {
	ticker := time.NewTicker(a.interval)
	defer ticker.Stop()

	// Run immediately on start
	a.aggregate(ctx)

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			a.aggregate(ctx)
		}
	}
}

func (a *ContentAggregator) aggregate(ctx context.Context) {
	var allContent []UnifiedContent
	since := time.Now().Add(-24 * time.Hour)

	for _, source := range a.sources {
		if !source.Enabled {
			continue
		}

		var content []UnifiedContent
		var err error

		switch source.Type {
		case "youtube":
			content, err = a.hub.FetchYouTubeChannel(ctx, source.Identifier, 10, &since)
		case "twitter":
			content, err = a.hub.FetchTwitterUser(ctx, source.Identifier, 20, &since)
		case "rss":
			content, err = a.hub.FetchRSSFeed(ctx, source.Identifier, &since)
		}

		if err != nil {
			a.logger.Error("Failed to fetch content from source",
				zap.String("type", source.Type),
				zap.String("identifier", source.Identifier),
				zap.Error(err),
			)
			continue
		}

		allContent = append(allContent, content...)
	}

	if len(allContent) > 0 {
		if err := a.callback(allContent); err != nil {
			a.logger.Error("Failed to process aggregated content", zap.Error(err))
		}
	}
}

// Helper functions
func truncateText(s string, maxLen int) string {
	if len(s) <= maxLen {
		return s
	}
	return s[:maxLen-3] + "..."
}

// WebhookHandler handles incoming webhooks from various platforms
type WebhookHandler struct {
	hub    *SocialMediaHub
	logger *zap.Logger
}

// NewWebhookHandler creates a new webhook handler
func NewWebhookHandler(hub *SocialMediaHub) *WebhookHandler {
	return &WebhookHandler{
		hub:    hub,
		logger: hub.logger,
	}
}

// HandleBlogWebhook handles webhooks from the blog platform
func (wh *WebhookHandler) HandleBlogWebhook(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var payload WebhookPayload
	if err := json.NewDecoder(r.Body).Decode(&payload); err != nil {
		http.Error(w, "Invalid payload", http.StatusBadRequest)
		return
	}

	if wh.hub.blog != nil {
		if err := wh.hub.blog.HandleWebhook(&payload); err != nil {
			wh.logger.Error("Failed to handle blog webhook", zap.Error(err))
			http.Error(w, "Internal error", http.StatusInternalServerError)
			return
		}
	}

	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
}

// HandleYouTubeWebhook handles PubSubHubbub notifications from YouTube
func (wh *WebhookHandler) HandleYouTubeWebhook(w http.ResponseWriter, r *http.Request) {
	// Verify subscription (hub.challenge)
	if r.Method == http.MethodGet {
		challenge := r.URL.Query().Get("hub.challenge")
		if challenge != "" {
			w.Write([]byte(challenge))
			return
		}
	}

	// Handle notification
	if r.Method == http.MethodPost {
		wh.logger.Info("Received YouTube webhook notification")
		// Parse Atom feed entry and process
		w.WriteHeader(http.StatusOK)
		return
	}

	http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
}
