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

// TwitterIntegration handles Twitter API v2 interactions
type TwitterIntegration struct {
	bearerToken string
	httpClient  *http.Client
	logger      *zap.Logger
}

// Tweet represents a Twitter tweet
type Tweet struct {
	ID               string            `json:"id"`
	Text             string            `json:"text"`
	AuthorID         string            `json:"author_id"`
	AuthorUsername   string            `json:"author_username"`
	AuthorName       string            `json:"author_name"`
	CreatedAt        time.Time         `json:"created_at"`
	ConversationID   string            `json:"conversation_id"`
	PublicMetrics    TweetMetrics      `json:"public_metrics"`
	Entities         *TweetEntities    `json:"entities,omitempty"`
	ReferencedTweets []ReferencedTweet `json:"referenced_tweets,omitempty"`
}

// TweetMetrics contains engagement metrics for a tweet
type TweetMetrics struct {
	RetweetCount    int `json:"retweet_count"`
	ReplyCount      int `json:"reply_count"`
	LikeCount       int `json:"like_count"`
	QuoteCount      int `json:"quote_count"`
	BookmarkCount   int `json:"bookmark_count"`
	ImpressionCount int `json:"impression_count"`
}

// TweetEntities contains entities extracted from tweet text
type TweetEntities struct {
	Hashtags []struct {
		Tag   string `json:"tag"`
		Start int    `json:"start"`
		End   int    `json:"end"`
	} `json:"hashtags"`
	Mentions []struct {
		Username string `json:"username"`
		ID       string `json:"id"`
		Start    int    `json:"start"`
		End      int    `json:"end"`
	} `json:"mentions"`
	URLs []struct {
		URL         string `json:"url"`
		ExpandedURL string `json:"expanded_url"`
		DisplayURL  string `json:"display_url"`
		Start       int    `json:"start"`
		End         int    `json:"end"`
	} `json:"urls"`
}

// ReferencedTweet represents a tweet that this tweet references
type ReferencedTweet struct {
	Type string `json:"type"` // retweeted, quoted, replied_to
	ID   string `json:"id"`
}

// TwitterUser represents a Twitter user
type TwitterUser struct {
	ID              string    `json:"id"`
	Username        string    `json:"username"`
	Name            string    `json:"name"`
	Description     string    `json:"description"`
	ProfileImageURL string    `json:"profile_image_url"`
	FollowersCount  int       `json:"followers_count"`
	FollowingCount  int       `json:"following_count"`
	TweetCount      int       `json:"tweet_count"`
	Verified        bool      `json:"verified"`
	CreatedAt       time.Time `json:"created_at"`
}

// NewTwitterIntegration creates a new Twitter integration
func NewTwitterIntegration(bearerToken string, logger *zap.Logger) *TwitterIntegration {
	return &TwitterIntegration{
		bearerToken: bearerToken,
		httpClient: &http.Client{
			Timeout: 30 * time.Second,
		},
		logger: logger,
	}
}

// GetUser retrieves user information by username
func (t *TwitterIntegration) GetUser(ctx context.Context, username string) (*TwitterUser, error) {
	params := url.Values{
		"user.fields": {"id,name,username,description,profile_image_url,public_metrics,verified,created_at"},
	}

	endpoint := fmt.Sprintf("users/by/username/%s", username)
	resp, err := t.makeRequest(ctx, endpoint, params)
	if err != nil {
		return nil, fmt.Errorf("failed to get user: %w", err)
	}

	var result struct {
		Data struct {
			ID              string `json:"id"`
			Username        string `json:"username"`
			Name            string `json:"name"`
			Description     string `json:"description"`
			ProfileImageURL string `json:"profile_image_url"`
			PublicMetrics   struct {
				FollowersCount int `json:"followers_count"`
				FollowingCount int `json:"following_count"`
				TweetCount     int `json:"tweet_count"`
			} `json:"public_metrics"`
			Verified  bool   `json:"verified"`
			CreatedAt string `json:"created_at"`
		} `json:"data"`
		Errors []struct {
			Message string `json:"message"`
		} `json:"errors"`
	}

	if err := json.Unmarshal(resp, &result); err != nil {
		return nil, fmt.Errorf("failed to parse user response: %w", err)
	}

	if len(result.Errors) > 0 {
		return nil, fmt.Errorf("Twitter API error: %s", result.Errors[0].Message)
	}

	createdAt, _ := time.Parse(time.RFC3339, result.Data.CreatedAt)

	return &TwitterUser{
		ID:              result.Data.ID,
		Username:        result.Data.Username,
		Name:            result.Data.Name,
		Description:     result.Data.Description,
		ProfileImageURL: result.Data.ProfileImageURL,
		FollowersCount:  result.Data.PublicMetrics.FollowersCount,
		FollowingCount:  result.Data.PublicMetrics.FollowingCount,
		TweetCount:      result.Data.PublicMetrics.TweetCount,
		Verified:        result.Data.Verified,
		CreatedAt:       createdAt,
	}, nil
}

// GetUserByID retrieves user information by user ID
func (t *TwitterIntegration) GetUserByID(ctx context.Context, userID string) (*TwitterUser, error) {
	params := url.Values{
		"user.fields": {"id,name,username,description,profile_image_url,public_metrics,verified,created_at"},
	}

	endpoint := fmt.Sprintf("users/%s", userID)
	resp, err := t.makeRequest(ctx, endpoint, params)
	if err != nil {
		return nil, fmt.Errorf("failed to get user: %w", err)
	}

	var result struct {
		Data struct {
			ID              string `json:"id"`
			Username        string `json:"username"`
			Name            string `json:"name"`
			Description     string `json:"description"`
			ProfileImageURL string `json:"profile_image_url"`
			PublicMetrics   struct {
				FollowersCount int `json:"followers_count"`
				FollowingCount int `json:"following_count"`
				TweetCount     int `json:"tweet_count"`
			} `json:"public_metrics"`
			Verified  bool   `json:"verified"`
			CreatedAt string `json:"created_at"`
		} `json:"data"`
	}

	if err := json.Unmarshal(resp, &result); err != nil {
		return nil, fmt.Errorf("failed to parse user response: %w", err)
	}

	createdAt, _ := time.Parse(time.RFC3339, result.Data.CreatedAt)

	return &TwitterUser{
		ID:              result.Data.ID,
		Username:        result.Data.Username,
		Name:            result.Data.Name,
		Description:     result.Data.Description,
		ProfileImageURL: result.Data.ProfileImageURL,
		FollowersCount:  result.Data.PublicMetrics.FollowersCount,
		FollowingCount:  result.Data.PublicMetrics.FollowingCount,
		TweetCount:      result.Data.PublicMetrics.TweetCount,
		Verified:        result.Data.Verified,
		CreatedAt:       createdAt,
	}, nil
}

// GetUserTweets retrieves recent tweets from a user
func (t *TwitterIntegration) GetUserTweets(ctx context.Context, userID string, maxResults int, startTime *time.Time) ([]Tweet, error) {
	params := url.Values{
		"tweet.fields": {"id,text,author_id,created_at,conversation_id,public_metrics,entities,referenced_tweets"},
		"user.fields":  {"id,name,username"},
		"expansions":   {"author_id"},
		"max_results":  {fmt.Sprintf("%d", maxResults)},
	}

	if startTime != nil {
		params.Set("start_time", startTime.Format(time.RFC3339))
	}

	endpoint := fmt.Sprintf("users/%s/tweets", userID)
	resp, err := t.makeRequest(ctx, endpoint, params)
	if err != nil {
		return nil, fmt.Errorf("failed to get user tweets: %w", err)
	}

	var result struct {
		Data []struct {
			ID             string `json:"id"`
			Text           string `json:"text"`
			AuthorID       string `json:"author_id"`
			CreatedAt      string `json:"created_at"`
			ConversationID string `json:"conversation_id"`
			PublicMetrics  struct {
				RetweetCount    int `json:"retweet_count"`
				ReplyCount      int `json:"reply_count"`
				LikeCount       int `json:"like_count"`
				QuoteCount      int `json:"quote_count"`
				BookmarkCount   int `json:"bookmark_count"`
				ImpressionCount int `json:"impression_count"`
			} `json:"public_metrics"`
			Entities         *TweetEntities    `json:"entities,omitempty"`
			ReferencedTweets []ReferencedTweet `json:"referenced_tweets,omitempty"`
		} `json:"data"`
		Includes struct {
			Users []struct {
				ID       string `json:"id"`
				Name     string `json:"name"`
				Username string `json:"username"`
			} `json:"users"`
		} `json:"includes"`
	}

	if err := json.Unmarshal(resp, &result); err != nil {
		return nil, fmt.Errorf("failed to parse tweets response: %w", err)
	}

	// Create user lookup map
	userMap := make(map[string]struct {
		Name     string
		Username string
	})
	for _, user := range result.Includes.Users {
		userMap[user.ID] = struct {
			Name     string
			Username string
		}{Name: user.Name, Username: user.Username}
	}

	tweets := make([]Tweet, 0, len(result.Data))
	for _, item := range result.Data {
		createdAt, _ := time.Parse(time.RFC3339, item.CreatedAt)

		tweet := Tweet{
			ID:             item.ID,
			Text:           item.Text,
			AuthorID:       item.AuthorID,
			CreatedAt:      createdAt,
			ConversationID: item.ConversationID,
			PublicMetrics: TweetMetrics{
				RetweetCount:    item.PublicMetrics.RetweetCount,
				ReplyCount:      item.PublicMetrics.ReplyCount,
				LikeCount:       item.PublicMetrics.LikeCount,
				QuoteCount:      item.PublicMetrics.QuoteCount,
				BookmarkCount:   item.PublicMetrics.BookmarkCount,
				ImpressionCount: item.PublicMetrics.ImpressionCount,
			},
			Entities:         item.Entities,
			ReferencedTweets: item.ReferencedTweets,
		}

		if user, ok := userMap[item.AuthorID]; ok {
			tweet.AuthorName = user.Name
			tweet.AuthorUsername = user.Username
		}

		tweets = append(tweets, tweet)
	}

	return tweets, nil
}

// SearchTweets searches for tweets matching a query
func (t *TwitterIntegration) SearchTweets(ctx context.Context, query string, maxResults int) ([]Tweet, error) {
	params := url.Values{
		"query":        {query},
		"tweet.fields": {"id,text,author_id,created_at,conversation_id,public_metrics,entities"},
		"user.fields":  {"id,name,username"},
		"expansions":   {"author_id"},
		"max_results":  {fmt.Sprintf("%d", maxResults)},
	}

	resp, err := t.makeRequest(ctx, "tweets/search/recent", params)
	if err != nil {
		return nil, fmt.Errorf("failed to search tweets: %w", err)
	}

	var result struct {
		Data []struct {
			ID             string `json:"id"`
			Text           string `json:"text"`
			AuthorID       string `json:"author_id"`
			CreatedAt      string `json:"created_at"`
			ConversationID string `json:"conversation_id"`
			PublicMetrics  struct {
				RetweetCount int `json:"retweet_count"`
				ReplyCount   int `json:"reply_count"`
				LikeCount    int `json:"like_count"`
				QuoteCount   int `json:"quote_count"`
			} `json:"public_metrics"`
			Entities *TweetEntities `json:"entities,omitempty"`
		} `json:"data"`
		Includes struct {
			Users []struct {
				ID       string `json:"id"`
				Name     string `json:"name"`
				Username string `json:"username"`
			} `json:"users"`
		} `json:"includes"`
	}

	if err := json.Unmarshal(resp, &result); err != nil {
		return nil, fmt.Errorf("failed to parse search response: %w", err)
	}

	// Create user lookup map
	userMap := make(map[string]struct {
		Name     string
		Username string
	})
	for _, user := range result.Includes.Users {
		userMap[user.ID] = struct {
			Name     string
			Username string
		}{Name: user.Name, Username: user.Username}
	}

	tweets := make([]Tweet, 0, len(result.Data))
	for _, item := range result.Data {
		createdAt, _ := time.Parse(time.RFC3339, item.CreatedAt)

		tweet := Tweet{
			ID:             item.ID,
			Text:           item.Text,
			AuthorID:       item.AuthorID,
			CreatedAt:      createdAt,
			ConversationID: item.ConversationID,
			PublicMetrics: TweetMetrics{
				RetweetCount: item.PublicMetrics.RetweetCount,
				ReplyCount:   item.PublicMetrics.ReplyCount,
				LikeCount:    item.PublicMetrics.LikeCount,
				QuoteCount:   item.PublicMetrics.QuoteCount,
			},
			Entities: item.Entities,
		}

		if user, ok := userMap[item.AuthorID]; ok {
			tweet.AuthorName = user.Name
			tweet.AuthorUsername = user.Username
		}

		tweets = append(tweets, tweet)
	}

	return tweets, nil
}

// GetTweet retrieves a single tweet by ID
func (t *TwitterIntegration) GetTweet(ctx context.Context, tweetID string) (*Tweet, error) {
	params := url.Values{
		"tweet.fields": {"id,text,author_id,created_at,conversation_id,public_metrics,entities,referenced_tweets"},
		"user.fields":  {"id,name,username"},
		"expansions":   {"author_id"},
	}

	endpoint := fmt.Sprintf("tweets/%s", tweetID)
	resp, err := t.makeRequest(ctx, endpoint, params)
	if err != nil {
		return nil, fmt.Errorf("failed to get tweet: %w", err)
	}

	var result struct {
		Data struct {
			ID             string `json:"id"`
			Text           string `json:"text"`
			AuthorID       string `json:"author_id"`
			CreatedAt      string `json:"created_at"`
			ConversationID string `json:"conversation_id"`
			PublicMetrics  struct {
				RetweetCount    int `json:"retweet_count"`
				ReplyCount      int `json:"reply_count"`
				LikeCount       int `json:"like_count"`
				QuoteCount      int `json:"quote_count"`
				BookmarkCount   int `json:"bookmark_count"`
				ImpressionCount int `json:"impression_count"`
			} `json:"public_metrics"`
			Entities         *TweetEntities    `json:"entities,omitempty"`
			ReferencedTweets []ReferencedTweet `json:"referenced_tweets,omitempty"`
		} `json:"data"`
		Includes struct {
			Users []struct {
				ID       string `json:"id"`
				Name     string `json:"name"`
				Username string `json:"username"`
			} `json:"users"`
		} `json:"includes"`
	}

	if err := json.Unmarshal(resp, &result); err != nil {
		return nil, fmt.Errorf("failed to parse tweet response: %w", err)
	}

	createdAt, _ := time.Parse(time.RFC3339, result.Data.CreatedAt)

	tweet := &Tweet{
		ID:             result.Data.ID,
		Text:           result.Data.Text,
		AuthorID:       result.Data.AuthorID,
		CreatedAt:      createdAt,
		ConversationID: result.Data.ConversationID,
		PublicMetrics: TweetMetrics{
			RetweetCount:    result.Data.PublicMetrics.RetweetCount,
			ReplyCount:      result.Data.PublicMetrics.ReplyCount,
			LikeCount:       result.Data.PublicMetrics.LikeCount,
			QuoteCount:      result.Data.PublicMetrics.QuoteCount,
			BookmarkCount:   result.Data.PublicMetrics.BookmarkCount,
			ImpressionCount: result.Data.PublicMetrics.ImpressionCount,
		},
		Entities:         result.Data.Entities,
		ReferencedTweets: result.Data.ReferencedTweets,
	}

	if len(result.Includes.Users) > 0 {
		tweet.AuthorName = result.Includes.Users[0].Name
		tweet.AuthorUsername = result.Includes.Users[0].Username
	}

	return tweet, nil
}

// makeRequest makes an HTTP request to Twitter API v2
func (t *TwitterIntegration) makeRequest(ctx context.Context, endpoint string, params url.Values) ([]byte, error) {
	apiURL := fmt.Sprintf("https://api.twitter.com/2/%s?%s", endpoint, params.Encode())

	req, err := http.NewRequestWithContext(ctx, http.MethodGet, apiURL, nil)
	if err != nil {
		return nil, err
	}

	req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", t.bearerToken))

	resp, err := t.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("Twitter API error: %s - %s", resp.Status, string(body))
	}

	return body, nil
}
