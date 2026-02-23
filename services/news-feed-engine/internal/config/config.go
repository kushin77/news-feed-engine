// Package config handles configuration loading from environment variables and GCP Secret Manager
package config

import (
	"context"
	"fmt"
	"os"
	"strconv"
	"strings"
	"time"

	secretmanager "cloud.google.com/go/secretmanager/apiv1"
	secretmanagerpb "cloud.google.com/go/secretmanager/apiv1/secretmanagerpb"
)

// Config holds all service configuration
type Config struct {
	// Server settings
	Port        string
	Environment string

	// Database connections
	PostgresDSN string
	MongoURI    string
	RedisURL    string

	// Kafka settings
	KafkaBrokers        []string
	KafkaConsumerGroup  string
	KafkaRawTopic       string
	KafkaProcessedTopic string
	KafkaVideoTopic     string

	// API Keys (loaded from GCP Secret Manager)
	YouTubeAPIKey    string
	TwitterAPIKey    string
	TwitterAPISecret string
	RedditClientID   string
	RedditClientSec  string
	ClaudeAPIKey     string
	OpenAIAPIKey     string
	ElevenLabsAPIKey string
	DIDAPIKey        string

	// Webhook secrets
	YouTubeWebhookSecret  string
	TwitterConsumerSecret string

	// Auth settings
	JWTSecret string

	// CORS settings
	CORSAllowedOrigins []string

	// Rate limiting
	RateLimitRequests int
	RateLimitWindow   time.Duration

	// Content settings
	DefaultContentLimit int
	MaxContentLimit     int
	IngestionInterval   time.Duration

	// Video generation settings
	VideoOutputDir      string
	MaxConcurrentVideos int

	// White-label settings
	EnableWhiteLabel    bool
	DefaultTenantID     string
	DefaultBrandingLogo string
	DefaultBrandingName string

	// GCP settings
	GCPProjectID string
}

// Load loads configuration from environment variables and GCP Secret Manager
func Load() (*Config, error) {
	cfg := &Config{
		// Server defaults
		Port:        getEnv("PORT", "8080"),
		Environment: getEnv("ELEVATEDIQ_ENVIRONMENT", "development"),

		// Database connections
		PostgresDSN: getEnv("POSTGRES_DSN", "postgres://postgres:postgres@elevatediq-postgres:5432/news_feed?sslmode=disable"),
		MongoURI:    getEnv("MONGO_URI", "mongodb://elevatediq-mongodb:27017/news_feed"),
		RedisURL:    getEnv("REDIS_URL", "redis://elevatediq-redis:6379/0"),

		// Kafka settings
		KafkaBrokers:        strings.Split(getEnv("KAFKA_BROKERS", "elevatediq-kafka:9092"), ","),
		KafkaConsumerGroup:  getEnv("KAFKA_CONSUMER_GROUP", "news-feed-engine"),
		KafkaRawTopic:       getEnv("KAFKA_RAW_TOPIC", "news-feed-raw-content"),
		KafkaProcessedTopic: getEnv("KAFKA_PROCESSED_TOPIC", "news-feed-processed-content"),
		KafkaVideoTopic:     getEnv("KAFKA_VIDEO_TOPIC", "news-feed-video-jobs"),

		// CORS
		CORSAllowedOrigins: strings.Split(getEnv("CORS_ALLOWED_ORIGINS", "https://dev.elevatediq.ai,https://elevatediq.ai,https://dev.purebliss.app,https://purebliss.app"), ","),

		// Rate limiting
		RateLimitRequests: getEnvInt("RATE_LIMIT_REQUESTS", 100),
		RateLimitWindow:   time.Duration(getEnvInt("RATE_LIMIT_WINDOW_SECONDS", 60)) * time.Second,

		// Content settings
		DefaultContentLimit: getEnvInt("DEFAULT_CONTENT_LIMIT", 20),
		MaxContentLimit:     getEnvInt("MAX_CONTENT_LIMIT", 100),
		IngestionInterval:   time.Duration(getEnvInt("INGESTION_INTERVAL_MINUTES", 15)) * time.Minute,

		// Video settings
		VideoOutputDir:      getEnv("VIDEO_OUTPUT_DIR", "/data/videos"),
		MaxConcurrentVideos: getEnvInt("MAX_CONCURRENT_VIDEOS", 3),

		// White-label settings
		EnableWhiteLabel:    getEnvBool("ENABLE_WHITE_LABEL", true),
		DefaultTenantID:     getEnv("DEFAULT_TENANT_ID", "elevatediq"),
		DefaultBrandingLogo: getEnv("DEFAULT_BRANDING_LOGO", "/assets/logo.png"),
		DefaultBrandingName: getEnv("DEFAULT_BRANDING_NAME", "ElevatedIQ News"),

		// GCP settings
		GCPProjectID: getEnv("GCP_PROJECT_ID", "elevatediq-production"),
	}

	// Load secrets from GCP Secret Manager or environment
	// Skip Secret Manager in development if credentials not available
	useSecretManager := getEnv("USE_SECRET_MANAGER", "false") == "true"

	if cfg.Environment == "development" && !useSecretManager {
		// In development without Secret Manager, load from environment
		cfg.loadSecretsFromEnv()
	} else {
		// Production or development with Secret Manager enabled
		if err := cfg.loadSecrets(); err != nil {
			// Fall back to environment variables if Secret Manager fails
			if cfg.Environment == "development" {
				cfg.loadSecretsFromEnv()
			} else {
				return nil, fmt.Errorf("failed to load secrets: %w", err)
			}
		}
	}

	return cfg, nil
}

// loadSecrets loads API keys from GCP Secret Manager
func (c *Config) loadSecrets() error {
	ctx := context.Background()
	client, err := secretmanager.NewClient(ctx)
	if err != nil {
		return fmt.Errorf("failed to create secret manager client: %w", err)
	}
	defer client.Close()

	secrets := map[string]*string{
		"news-feed-youtube-api-key":         &c.YouTubeAPIKey,
		"news-feed-twitter-api-key":         &c.TwitterAPIKey,
		"news-feed-twitter-api-secret":      &c.TwitterAPISecret,
		"news-feed-reddit-client-id":        &c.RedditClientID,
		"news-feed-reddit-client-secret":    &c.RedditClientSec,
		"news-feed-claude-api-key":          &c.ClaudeAPIKey,
		"news-feed-openai-api-key":          &c.OpenAIAPIKey,
		"news-feed-elevenlabs-api-key":      &c.ElevenLabsAPIKey,
		"news-feed-did-api-key":             &c.DIDAPIKey,
		"news-feed-jwt-secret":              &c.JWTSecret,
		"news-feed-youtube-webhook-secret":  &c.YouTubeWebhookSecret,
		"news-feed-twitter-consumer-secret": &c.TwitterConsumerSecret,
	}

	for secretName, target := range secrets {
		value, err := c.accessSecret(ctx, client, secretName)
		if err != nil {
			return fmt.Errorf("failed to access secret %s: %w", secretName, err)
		}
		*target = value
	}

	return nil
}

// accessSecret retrieves a secret value from GCP Secret Manager
func (c *Config) accessSecret(ctx context.Context, client *secretmanager.Client, secretID string) (string, error) {
	name := fmt.Sprintf("projects/%s/secrets/%s/versions/latest", c.GCPProjectID, secretID)

	req := &secretmanagerpb.AccessSecretVersionRequest{
		Name: name,
	}

	result, err := client.AccessSecretVersion(ctx, req)
	if err != nil {
		return "", err
	}

	return string(result.Payload.Data), nil
}

// loadSecretsFromEnv loads secrets from environment variables (for development)
func (c *Config) loadSecretsFromEnv() {
	c.YouTubeAPIKey = getEnv("YOUTUBE_API_KEY", "")
	c.TwitterAPIKey = getEnv("TWITTER_API_KEY", "")
	c.TwitterAPISecret = getEnv("TWITTER_API_SECRET", "")
	c.RedditClientID = getEnv("REDDIT_CLIENT_ID", "")
	c.RedditClientSec = getEnv("REDDIT_CLIENT_SECRET", "")
	c.ClaudeAPIKey = getEnv("CLAUDE_API_KEY", "")
	c.OpenAIAPIKey = getEnv("OPENAI_API_KEY", "")
	c.ElevenLabsAPIKey = getEnv("ELEVENLABS_API_KEY", "")
	c.DIDAPIKey = getEnv("DID_API_KEY", "")
	c.JWTSecret = getEnv("JWT_SECRET", "development-secret-key")
	c.YouTubeWebhookSecret = getEnv("YOUTUBE_WEBHOOK_SECRET", "")
	c.TwitterConsumerSecret = getEnv("TWITTER_CONSUMER_SECRET", "")
}

// Helper functions
func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getEnvInt(key string, defaultValue int) int {
	if value := os.Getenv(key); value != "" {
		if intValue, err := strconv.Atoi(value); err == nil {
			return intValue
		}
	}
	return defaultValue
}

func getEnvBool(key string, defaultValue bool) bool {
	if value := os.Getenv(key); value != "" {
		if boolValue, err := strconv.ParseBool(value); err == nil {
			return boolValue
		}
	}
	return defaultValue
}
