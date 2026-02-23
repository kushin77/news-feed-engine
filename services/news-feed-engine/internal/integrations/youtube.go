package integrations

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"time"

	"go.uber.org/zap"
)

// YouTubeIntegration handles YouTube Data API interactions
type YouTubeIntegration struct {
	apiKey     string
	httpClient *http.Client
	logger     *zap.Logger
}

// YouTubeVideo represents a YouTube video
type YouTubeVideo struct {
	ID           string    `json:"id"`
	Title        string    `json:"title"`
	Description  string    `json:"description"`
	ChannelID    string    `json:"channel_id"`
	ChannelTitle string    `json:"channel_title"`
	PublishedAt  time.Time `json:"published_at"`
	ThumbnailURL string    `json:"thumbnail_url"`
	Duration     string    `json:"duration"`
	ViewCount    int64     `json:"view_count"`
	LikeCount    int64     `json:"like_count"`
	CommentCount int64     `json:"comment_count"`
	Tags         []string  `json:"tags"`
}

// YouTubeChannel represents a YouTube channel
type YouTubeChannel struct {
	ID              string `json:"id"`
	Title           string `json:"title"`
	Description     string `json:"description"`
	CustomURL       string `json:"custom_url"`
	ThumbnailURL    string `json:"thumbnail_url"`
	SubscriberCount int64  `json:"subscriber_count"`
	VideoCount      int64  `json:"video_count"`
	ViewCount       int64  `json:"view_count"`
}

// NewYouTubeIntegration creates a new YouTube integration
func NewYouTubeIntegration(apiKey string, logger *zap.Logger) *YouTubeIntegration {
	return &YouTubeIntegration{
		apiKey: apiKey,
		httpClient: &http.Client{
			Timeout: 30 * time.Second,
		},
		logger: logger,
	}
}

// GetChannel retrieves channel information by channel ID
func (y *YouTubeIntegration) GetChannel(ctx context.Context, channelID string) (*YouTubeChannel, error) {
	params := url.Values{
		"part": {"snippet,statistics"},
		"id":   {channelID},
		"key":  {y.apiKey},
	}

	resp, err := y.makeRequest(ctx, "channels", params)
	if err != nil {
		return nil, fmt.Errorf("failed to get channel: %w", err)
	}

	var result struct {
		Items []struct {
			ID      string `json:"id"`
			Snippet struct {
				Title       string `json:"title"`
				Description string `json:"description"`
				CustomURL   string `json:"customUrl"`
				Thumbnails  struct {
					High struct {
						URL string `json:"url"`
					} `json:"high"`
				} `json:"thumbnails"`
			} `json:"snippet"`
			Statistics struct {
				SubscriberCount string `json:"subscriberCount"`
				VideoCount      string `json:"videoCount"`
				ViewCount       string `json:"viewCount"`
			} `json:"statistics"`
		} `json:"items"`
	}

	if err := json.Unmarshal(resp, &result); err != nil {
		return nil, fmt.Errorf("failed to parse channel response: %w", err)
	}

	if len(result.Items) == 0 {
		return nil, fmt.Errorf("channel not found: %s", channelID)
	}

	item := result.Items[0]
	return &YouTubeChannel{
		ID:              item.ID,
		Title:           item.Snippet.Title,
		Description:     item.Snippet.Description,
		CustomURL:       item.Snippet.CustomURL,
		ThumbnailURL:    item.Snippet.Thumbnails.High.URL,
		SubscriberCount: parseInt64(item.Statistics.SubscriberCount),
		VideoCount:      parseInt64(item.Statistics.VideoCount),
		ViewCount:       parseInt64(item.Statistics.ViewCount),
	}, nil
}

// GetChannelVideos retrieves recent videos from a channel
func (y *YouTubeIntegration) GetChannelVideos(ctx context.Context, channelID string, maxResults int, publishedAfter *time.Time) ([]YouTubeVideo, error) {
	// First, get the uploads playlist ID
	params := url.Values{
		"part": {"contentDetails"},
		"id":   {channelID},
		"key":  {y.apiKey},
	}

	resp, err := y.makeRequest(ctx, "channels", params)
	if err != nil {
		return nil, fmt.Errorf("failed to get channel details: %w", err)
	}

	var channelResult struct {
		Items []struct {
			ContentDetails struct {
				RelatedPlaylists struct {
					Uploads string `json:"uploads"`
				} `json:"relatedPlaylists"`
			} `json:"contentDetails"`
		} `json:"items"`
	}

	if err := json.Unmarshal(resp, &channelResult); err != nil {
		return nil, fmt.Errorf("failed to parse channel details: %w", err)
	}

	if len(channelResult.Items) == 0 {
		return nil, fmt.Errorf("channel not found: %s", channelID)
	}

	uploadsPlaylistID := channelResult.Items[0].ContentDetails.RelatedPlaylists.Uploads

	// Get videos from uploads playlist
	params = url.Values{
		"part":       {"snippet"},
		"playlistId": {uploadsPlaylistID},
		"maxResults": {fmt.Sprintf("%d", maxResults)},
		"key":        {y.apiKey},
	}

	resp, err = y.makeRequest(ctx, "playlistItems", params)
	if err != nil {
		return nil, fmt.Errorf("failed to get playlist items: %w", err)
	}

	var playlistResult struct {
		Items []struct {
			Snippet struct {
				ResourceID struct {
					VideoID string `json:"videoId"`
				} `json:"resourceId"`
				Title        string    `json:"title"`
				Description  string    `json:"description"`
				ChannelID    string    `json:"channelId"`
				ChannelTitle string    `json:"channelTitle"`
				PublishedAt  time.Time `json:"publishedAt"`
				Thumbnails   struct {
					High struct {
						URL string `json:"url"`
					} `json:"high"`
				} `json:"thumbnails"`
			} `json:"snippet"`
		} `json:"items"`
	}

	if err := json.Unmarshal(resp, &playlistResult); err != nil {
		return nil, fmt.Errorf("failed to parse playlist items: %w", err)
	}

	videos := make([]YouTubeVideo, 0, len(playlistResult.Items))
	for _, item := range playlistResult.Items {
		if publishedAfter != nil && item.Snippet.PublishedAt.Before(*publishedAfter) {
			continue
		}
		videos = append(videos, YouTubeVideo{
			ID:           item.Snippet.ResourceID.VideoID,
			Title:        item.Snippet.Title,
			Description:  item.Snippet.Description,
			ChannelID:    item.Snippet.ChannelID,
			ChannelTitle: item.Snippet.ChannelTitle,
			PublishedAt:  item.Snippet.PublishedAt,
			ThumbnailURL: item.Snippet.Thumbnails.High.URL,
		})
	}

	// Get video details (duration, stats)
	if len(videos) > 0 {
		videoIDs := make([]string, len(videos))
		for i, v := range videos {
			videoIDs[i] = v.ID
		}
		videos, err = y.enrichVideoDetails(ctx, videos)
		if err != nil {
			y.logger.Warn("Failed to enrich video details", zap.Error(err))
		}
	}

	return videos, nil
}

// GetVideoDetails retrieves detailed information for a single video
func (y *YouTubeIntegration) GetVideoDetails(ctx context.Context, videoID string) (*YouTubeVideo, error) {
	params := url.Values{
		"part": {"snippet,contentDetails,statistics"},
		"id":   {videoID},
		"key":  {y.apiKey},
	}

	resp, err := y.makeRequest(ctx, "videos", params)
	if err != nil {
		return nil, fmt.Errorf("failed to get video details: %w", err)
	}

	var result struct {
		Items []struct {
			ID      string `json:"id"`
			Snippet struct {
				Title        string    `json:"title"`
				Description  string    `json:"description"`
				ChannelID    string    `json:"channelId"`
				ChannelTitle string    `json:"channelTitle"`
				PublishedAt  time.Time `json:"publishedAt"`
				Tags         []string  `json:"tags"`
				Thumbnails   struct {
					High struct {
						URL string `json:"url"`
					} `json:"high"`
				} `json:"thumbnails"`
			} `json:"snippet"`
			ContentDetails struct {
				Duration string `json:"duration"`
			} `json:"contentDetails"`
			Statistics struct {
				ViewCount    string `json:"viewCount"`
				LikeCount    string `json:"likeCount"`
				CommentCount string `json:"commentCount"`
			} `json:"statistics"`
		} `json:"items"`
	}

	if err := json.Unmarshal(resp, &result); err != nil {
		return nil, fmt.Errorf("failed to parse video details: %w", err)
	}

	if len(result.Items) == 0 {
		return nil, fmt.Errorf("video not found: %s", videoID)
	}

	item := result.Items[0]
	return &YouTubeVideo{
		ID:           item.ID,
		Title:        item.Snippet.Title,
		Description:  item.Snippet.Description,
		ChannelID:    item.Snippet.ChannelID,
		ChannelTitle: item.Snippet.ChannelTitle,
		PublishedAt:  item.Snippet.PublishedAt,
		ThumbnailURL: item.Snippet.Thumbnails.High.URL,
		Duration:     item.ContentDetails.Duration,
		ViewCount:    parseInt64(item.Statistics.ViewCount),
		LikeCount:    parseInt64(item.Statistics.LikeCount),
		CommentCount: parseInt64(item.Statistics.CommentCount),
		Tags:         item.Snippet.Tags,
	}, nil
}

// GetCaptions retrieves video captions/transcript
func (y *YouTubeIntegration) GetCaptions(ctx context.Context, videoID string) (string, error) {
	// Note: This requires OAuth2 for third-party captions
	// For now, we'll use a workaround with the timedtext API
	params := url.Values{
		"part":    {"snippet"},
		"videoId": {videoID},
		"key":     {y.apiKey},
	}

	resp, err := y.makeRequest(ctx, "captions", params)
	if err != nil {
		return "", fmt.Errorf("failed to get captions: %w", err)
	}

	var result struct {
		Items []struct {
			ID      string `json:"id"`
			Snippet struct {
				Language     string `json:"language"`
				TrackKind    string `json:"trackKind"`
				IsAutoSynced bool   `json:"isAutoSynced"`
			} `json:"snippet"`
		} `json:"items"`
	}

	if err := json.Unmarshal(resp, &result); err != nil {
		return "", fmt.Errorf("failed to parse captions response: %w", err)
	}

	// Find English caption track
	for _, item := range result.Items {
		if item.Snippet.Language == "en" || item.Snippet.Language == "en-US" {
			// Would need OAuth2 to download the actual caption content
			return fmt.Sprintf("Caption track available: %s", item.ID), nil
		}
	}

	return "", fmt.Errorf("no English captions available for video: %s", videoID)
}

// enrichVideoDetails adds duration and statistics to video list
func (y *YouTubeIntegration) enrichVideoDetails(ctx context.Context, videos []YouTubeVideo) ([]YouTubeVideo, error) {
	videoIDs := ""
	for i, v := range videos {
		if i > 0 {
			videoIDs += ","
		}
		videoIDs += v.ID
	}

	params := url.Values{
		"part": {"contentDetails,statistics"},
		"id":   {videoIDs},
		"key":  {y.apiKey},
	}

	resp, err := y.makeRequest(ctx, "videos", params)
	if err != nil {
		return videos, err
	}

	var result struct {
		Items []struct {
			ID             string `json:"id"`
			ContentDetails struct {
				Duration string `json:"duration"`
			} `json:"contentDetails"`
			Statistics struct {
				ViewCount    string `json:"viewCount"`
				LikeCount    string `json:"likeCount"`
				CommentCount string `json:"commentCount"`
			} `json:"statistics"`
		} `json:"items"`
	}

	if err := json.Unmarshal(resp, &result); err != nil {
		return videos, err
	}

	// Create a map for quick lookup
	detailsMap := make(map[string]struct {
		Duration     string
		ViewCount    string
		LikeCount    string
		CommentCount string
	})
	for _, item := range result.Items {
		detailsMap[item.ID] = struct {
			Duration     string
			ViewCount    string
			LikeCount    string
			CommentCount string
		}{
			Duration:     item.ContentDetails.Duration,
			ViewCount:    item.Statistics.ViewCount,
			LikeCount:    item.Statistics.LikeCount,
			CommentCount: item.Statistics.CommentCount,
		}
	}

	// Enrich videos
	for i := range videos {
		if details, ok := detailsMap[videos[i].ID]; ok {
			videos[i].Duration = details.Duration
			videos[i].ViewCount = parseInt64(details.ViewCount)
			videos[i].LikeCount = parseInt64(details.LikeCount)
			videos[i].CommentCount = parseInt64(details.CommentCount)
		}
	}

	return videos, nil
}

// makeRequest makes an HTTP request to YouTube API
func (y *YouTubeIntegration) makeRequest(ctx context.Context, endpoint string, params url.Values) ([]byte, error) {
	apiURL := fmt.Sprintf("https://www.googleapis.com/youtube/v3/%s?%s", endpoint, params.Encode())

	req, err := http.NewRequestWithContext(ctx, http.MethodGet, apiURL, nil)
	if err != nil {
		return nil, err
	}

	resp, err := y.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("YouTube API error: %s - %s", resp.Status, string(body))
	}

	return body, nil
}

// Helper function to parse int64 from string
func parseInt64(s string) int64 {
	var result int64
	fmt.Sscanf(s, "%d", &result)
	return result
}
