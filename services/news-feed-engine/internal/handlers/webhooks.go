// Package handlers provides HTTP handlers for platform webhook integrations
package handlers

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"encoding/xml"
	"io"
	"net/http"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/kushin77/elevatedIQ/services/news-feed-engine/internal/kafka"
	"github.com/kushin77/elevatedIQ/services/news-feed-engine/internal/middleware"
)

// WebhookHandler handles platform webhook integrations
type WebhookHandler struct {
	producer              *kafka.Producer
	rawTopic              string
	youtubeWebhookSecret  string
	twitterConsumerSecret string
}

// NewWebhookHandler creates a new webhook handler
func NewWebhookHandler(producer *kafka.Producer, rawTopic, youtubeSecret, twitterSecret string) *WebhookHandler {
	return &WebhookHandler{
		producer:              producer,
		rawTopic:              rawTopic,
		youtubeWebhookSecret:  youtubeSecret,
		twitterConsumerSecret: twitterSecret,
	}
}

// AtomFeed represents a YouTube PubSubHubbub Atom feed
type AtomFeed struct {
	XMLName xml.Name    `xml:"feed"`
	Entries []AtomEntry `xml:"entry"`
}

// AtomEntry represents an entry in the Atom feed
type AtomEntry struct {
	ID        string     `xml:"id"`
	VideoID   string     `xml:"videoId"`
	ChannelID string     `xml:"channelId"`
	Title     string     `xml:"title"`
	Link      AtomLink   `xml:"link"`
	Author    AtomAuthor `xml:"author"`
	Published string     `xml:"published"`
	Updated   string     `xml:"updated"`
}

// AtomLink represents a link in the Atom feed
type AtomLink struct {
	Href string `xml:"href,attr"`
	Rel  string `xml:"rel,attr"`
}

// AtomAuthor represents an author in the Atom feed
type AtomAuthor struct {
	Name string `xml:"name"`
	URI  string `xml:"uri"`
}

// YouTubeWebhook handles incoming YouTube PubSubHubbub notifications
func (h *WebhookHandler) YouTubeWebhook(c *gin.Context) {
	// Handle verification challenge
	if c.Request.Method == "GET" {
		challenge := c.Query("hub.challenge")
		mode := c.Query("hub.mode")

		if mode == "subscribe" || mode == "unsubscribe" {
			c.String(http.StatusOK, challenge)
			return
		}

		c.Status(http.StatusBadRequest)
		return
	}

	tenantID := middleware.GetTenantID(c)

	// Read request body
	body, err := io.ReadAll(c.Request.Body)
	if err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "bad_request",
			Message: "failed to read request body",
		})
		return
	}

	// Verify HMAC signature if secret is configured
	if h.youtubeWebhookSecret != "" {
		signature := c.GetHeader("X-Hub-Signature")
		if !h.verifyHMACSignature(body, signature, h.youtubeWebhookSecret) {
			c.JSON(http.StatusUnauthorized, ErrorResponse{
				Error:   "🔐 YouTube webhook signature verification failed",
				Message: "The request signature doesn't match our records. Please verify your webhook secret is correct and try again",
			})
			return
		}
	}

	// Parse Atom feed
	var feed AtomFeed
	if err := xml.Unmarshal(body, &feed); err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "bad_request",
			Message: "failed to parse Atom feed",
		})
		return
	}

	// Process each entry and publish to Kafka
	published := 0
	for _, entry := range feed.Entries {
		msg := kafka.Message{
			Topic: h.rawTopic,
			Key:   entry.VideoID,
			Value: kafka.ContentIngestionMessage{
				TenantID:   tenantID,
				SourceType: "youtube",
				SourceID:   entry.ChannelID,
				URL:        entry.Link.Href,
				Priority:   1,
				Metadata: map[string]interface{}{
					"video_id":   entry.VideoID,
					"channel_id": entry.ChannelID,
					"title":      entry.Title,
					"author":     entry.Author.Name,
				},
				RequestedAt: time.Now(),
			},
			Timestamp: time.Now(),
		}

		if err := h.producer.Publish(c.Request.Context(), msg); err != nil {
			continue
		}
		published++
	}

	c.JSON(http.StatusOK, SuccessResponse{
		Success: true,
		Message: "notification processed",
		Data: map[string]interface{}{
			"platform":  "youtube",
			"entries":   len(feed.Entries),
			"published": published,
		},
	})
}

// TwitterWebhook handles incoming Twitter webhook events
func (h *WebhookHandler) TwitterWebhook(c *gin.Context) {
	// Handle CRC challenge for webhook registration
	if c.Request.Method == "GET" {
		crcToken := c.Query("crc_token")
		if crcToken != "" && h.twitterConsumerSecret != "" {
			mac := hmac.New(sha256.New, []byte(h.twitterConsumerSecret))
			mac.Write([]byte(crcToken))
			responseToken := "sha256=" + hex.EncodeToString(mac.Sum(nil))

			c.JSON(http.StatusOK, gin.H{
				"response_token": responseToken,
			})
			return
		}
		c.Status(http.StatusBadRequest)
		return
	}

	tenantID := middleware.GetTenantID(c)

	// Read and verify signature
	body, err := io.ReadAll(c.Request.Body)
	if err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "bad_request",
			Message: "failed to read request body",
		})
		return
	}

	// Verify HMAC signature
	if h.twitterConsumerSecret != "" {
		signature := c.GetHeader("X-Twitter-Webhooks-Signature")
		if !h.verifyHMACSignature(body, signature, h.twitterConsumerSecret) {
			c.JSON(http.StatusUnauthorized, ErrorResponse{
				Error:   "🐦 Twitter webhook signature verification failed",
				Message: "The request signature doesn't match our records. Please verify your Twitter API credentials and webhook secret",
			})
			return
		}
	}

	// Parse event
	var event map[string]interface{}
	if err := c.ShouldBindJSON(&event); err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "bad_request",
			Message: "invalid JSON body",
		})
		return
	}

	// Process different event types
	published := 0

	// Handle tweet_create_events
	if tweets, ok := event["tweet_create_events"].([]interface{}); ok {
		for _, tweet := range tweets {
			if t, ok := tweet.(map[string]interface{}); ok {
				tweetID := ""
				if id, ok := t["id_str"].(string); ok {
					tweetID = id
				}

				tweetURL := ""
				screenName := ""
				if user, ok := t["user"].(map[string]interface{}); ok {
					if sn, ok := user["screen_name"].(string); ok {
						screenName = sn
						tweetURL = "https://twitter.com/" + sn + "/status/" + tweetID
					}
				}

				msg := kafka.Message{
					Topic: h.rawTopic,
					Key:   tweetID,
					Value: kafka.ContentIngestionMessage{
						TenantID:   tenantID,
						SourceType: "twitter",
						SourceID:   screenName,
						URL:        tweetURL,
						Priority:   1,
						Metadata: map[string]interface{}{
							"tweet_id":    tweetID,
							"screen_name": screenName,
							"text":        t["text"],
							"raw_event":   t,
						},
						RequestedAt: time.Now(),
					},
					Timestamp: time.Now(),
				}

				if err := h.producer.Publish(c.Request.Context(), msg); err != nil {
					continue
				}
				published++
			}
		}
	}

	c.JSON(http.StatusOK, SuccessResponse{
		Success: true,
		Message: "event processed",
		Data: map[string]interface{}{
			"platform":  "twitter",
			"published": published,
		},
	})
}

// RedditWebhook handles incoming Reddit webhook events (custom integration)
func (h *WebhookHandler) RedditWebhook(c *gin.Context) {
	tenantID := middleware.GetTenantID(c)

	// Read request body
	body, err := io.ReadAll(c.Request.Body)
	if err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "bad_request",
			Message: "failed to read request body",
		})
		return
	}

	// Validate source IP or API key header
	apiKey := c.GetHeader("X-Reddit-Webhook-Key")
	if apiKey == "" {
		c.JSON(http.StatusUnauthorized, ErrorResponse{
			Error:   "🔑 Reddit webhook API key required",
			Message: "Please include your webhook API key in the X-Reddit-Webhook-Key header",
		})
		return
	}

	var event map[string]interface{}
	if err := c.ShouldBindJSON(&event); err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "bad_request",
			Message: "invalid JSON body",
		})
		return
	}

	// Extract post details
	postID := ""
	if id, ok := event["id"].(string); ok {
		postID = id
	}

	subreddit := ""
	if s, ok := event["subreddit"].(string); ok {
		subreddit = s
	}

	postURL := ""
	if permalink, ok := event["permalink"].(string); ok {
		postURL = "https://reddit.com" + permalink
	}

	msg := kafka.Message{
		Topic: h.rawTopic,
		Key:   postID,
		Value: kafka.ContentIngestionMessage{
			TenantID:   tenantID,
			SourceType: "reddit",
			SourceID:   subreddit,
			URL:        postURL,
			Priority:   1,
			Metadata: map[string]interface{}{
				"post_id":   postID,
				"subreddit": subreddit,
				"title":     event["title"],
				"author":    event["author"],
				"raw_data":  string(body),
			},
			RequestedAt: time.Now(),
		},
		Timestamp: time.Now(),
	}

	if err := h.producer.Publish(c.Request.Context(), msg); err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "publish_error",
			Message: "failed to publish event",
		})
		return
	}

	c.JSON(http.StatusOK, SuccessResponse{
		Success: true,
		Message: "event processed",
		Data: map[string]interface{}{
			"platform": "reddit",
			"post_id":  postID,
		},
	})
}

// verifyHMACSignature verifies HMAC-SHA256 signature
func (h *WebhookHandler) verifyHMACSignature(body []byte, signature, secret string) bool {
	if signature == "" {
		return false
	}

	// Remove "sha256=" prefix if present
	signature = strings.TrimPrefix(signature, "sha256=")

	mac := hmac.New(sha256.New, []byte(secret))
	mac.Write(body)
	expectedSignature := hex.EncodeToString(mac.Sum(nil))

	return hmac.Equal([]byte(signature), []byte(expectedSignature))
}
