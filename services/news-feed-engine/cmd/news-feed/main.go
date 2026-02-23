// Package main is the entry point for the ElevatedIQ News Feed Engine
// Elite AI-powered news aggregation platform with multi-platform content ingestion
package main

import (
	"context"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gin-contrib/cors"
	ginzap "github.com/gin-contrib/zap"
	"github.com/gin-gonic/gin"
	"github.com/kushin77/elevatedIQ/pkg/metrics"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"go.uber.org/zap"

	"github.com/kushin77/elevatedIQ/services/news-feed-engine/internal/config"
	"github.com/kushin77/elevatedIQ/services/news-feed-engine/internal/database"
	"github.com/kushin77/elevatedIQ/services/news-feed-engine/internal/embeddings"
	"github.com/kushin77/elevatedIQ/services/news-feed-engine/internal/handlers"
	"github.com/kushin77/elevatedIQ/services/news-feed-engine/internal/kafka"
	"github.com/kushin77/elevatedIQ/services/news-feed-engine/internal/middleware"
)

const (
	serviceName    = "news-feed-engine"
	serviceVersion = "1.0.0"
)

func main() {
	// Initialize logger
	logger, err := initLogger()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to initialize logger: %v\n", err)
		os.Exit(1)
	}
	defer logger.Sync()

	logger.Info("Starting News Feed Engine",
		zap.String("service", serviceName),
		zap.String("version", serviceVersion),
	)

	// Initialize metrics and health checks
	healthRegistry := metrics.NewHealthCheckRegistry()

	// Load configuration
	cfg, err := config.Load()
	if err != nil {
		logger.Fatal("Failed to load configuration", zap.Error(err))
	}

	// Initialize database connection
	db, err := database.Connect(cfg.PostgresDSN)
	if err != nil {
		logger.Fatal("Failed to connect to database", zap.Error(err))
	}
	defer db.Close()

	// Register database health check (pass underlying *sql.DB from sqlx wrapper)
	healthRegistry.Register("database", metrics.CreateDatabaseHealthChecker(db.DB.DB))

	logger.Info("Database connected successfully")

	// Initialize Kafka producer
	skipKafka := os.Getenv("SKIP_KAFKA_INIT") == "true"
	var kafkaProducer *kafka.Producer
	if skipKafka {
		logger.Info("Skipping Kafka initialization due to SKIP_KAFKA_INIT=true")
		kafkaProducer = kafka.NewNoopProducer(logger)
	} else {
		p, err := kafka.NewProducer(cfg.KafkaBrokers, logger)
		if err != nil {
			// In development allow fallback to noop producer so services can run without Kafka
			if cfg.Environment == "development" {
				logger.Warn("Failed to create Kafka producer; falling back to noop producer in development mode", zap.Error(err))
				kafkaProducer = kafka.NewNoopProducer(logger)
			} else {
				logger.Fatal("Failed to create Kafka producer", zap.Error(err))
			}
		} else {
			kafkaProducer = p
			logger.Info("Kafka producer initialized successfully",
				zap.Strings("brokers", cfg.KafkaBrokers),
				zap.String("raw_topic", cfg.KafkaRawTopic),
				zap.String("processed_topic", cfg.KafkaProcessedTopic),
				zap.String("video_topic", cfg.KafkaVideoTopic),
			)
		}
	}
	if kafkaProducer != nil {
		defer kafkaProducer.Close()
	}

	// Register Kafka health check
	healthRegistry.Register("kafka", metrics.NewHealthyChecker("kafka"))

	// Register service health check
	healthRegistry.Register("news-feed-engine", metrics.NewHealthyChecker("news-feed-engine"))

	// Initialize tracing (optional)
	jaegerEndpoint := os.Getenv("JAEGER_ENDPOINT")
	if jaegerEndpoint == "" {
		jaegerEndpoint = "127.0.0.1:6831"
	}

	tracingEnabled := os.Getenv("TRACING_ENABLED") == "true"
	if err := metrics.InitializeTracingProvider(serviceName, serviceVersion, cfg.Environment, jaegerEndpoint, tracingEnabled); err != nil {
		logger.Warn("Failed to initialize tracing", zap.Error(err))
	}

	// Initialize repositories
	contentRepo := database.NewContentRepository(db)
	videoRepo := database.NewVideoRepository(db)
	creatorRepo := database.NewCreatorRepository(db)
	configRepo := database.NewConfigRepository(db)
	sourceRepo := database.NewSourceRepository(db)
	templateRepo := database.NewTemplateRepository(db)
	analyticsRepo := database.NewAnalyticsRepository(db)

	// Initialize embedding service
	embeddingService := embeddings.NewOpenAIService(cfg.OpenAIAPIKey)

	// Initialize handlers
	contentHandler := handlers.NewContentHandler(contentRepo, kafkaProducer, embeddingService, cfg.KafkaRawTopic, cfg.KafkaProcessedTopic)
	videoHandler := handlers.NewVideoHandler(videoRepo, kafkaProducer, cfg.KafkaVideoTopic)
	creatorHandler := handlers.NewCreatorHandler(creatorRepo, contentRepo)
	adminHandler := handlers.NewAdminHandler(configRepo, sourceRepo, templateRepo, analyticsRepo)
	webhookHandler := handlers.NewWebhookHandler(kafkaProducer, cfg.KafkaRawTopic, cfg.YouTubeWebhookSecret, cfg.TwitterConsumerSecret)
	whitelabelHandler := handlers.NewWhitelabelHandler(configRepo)
	healthCheck := handlers.NewHealthCheck(db, kafkaProducer)
	// ensure variable is used to avoid unused var compile error (handlers register routes elsewhere)
	_ = healthCheck

	// Set Gin mode based on environment
	if cfg.Environment == "production" {
		gin.SetMode(gin.ReleaseMode)
	}

	// Initialize router
	router := gin.New()

	// Add middleware
	router.Use(ginzap.Ginzap(logger, time.RFC3339, true))
	router.Use(ginzap.RecoveryWithZap(logger, true))
	router.Use(cors.New(cors.Config{
		AllowOrigins:     cfg.CORSAllowedOrigins,
		AllowMethods:     []string{"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Accept", "Authorization", "X-Tenant-ID"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
		MaxAge:           12 * time.Hour,
	}))

	// Add tracing middleware if enabled
	if tracingEnabled {
		router.Use(metrics.TracingMiddleware())
	}

	router.Use(middleware.TenantMiddleware())
	router.Use(middleware.RateLimiter(cfg.RateLimitRequests, cfg.RateLimitWindow))

	// Health and metrics endpoints
	healthHandler := metrics.NewHealthCheckHandler(healthRegistry)
	router.GET("/health", healthHandler.GetHealthCheckHandler())
	router.GET("/health/live", healthHandler.GetLivenessHandler())
	router.GET("/health/ready", healthHandler.GetReadinessHandler())
	router.GET("/ready", healthHandler.GetReadinessHandler()) // Keep for backward compatibility
	router.GET("/metrics", gin.WrapH(promhttp.Handler()))

	// API v1 routes
	v1 := router.Group("/api/v1")
	{
		// Content endpoints
		content := v1.Group("/content")
		{
			content.GET("", contentHandler.ListContent)
			content.GET("/:id", contentHandler.GetContent)
			content.GET("/category/:category", contentHandler.GetContentByCategory)
			content.GET("/geo/:classification", contentHandler.GetContentByGeo)
			content.GET("/trending", contentHandler.GetTrendingContent)
			content.GET("/search", contentHandler.SearchContent)
		}

		// Creator endpoints
		creators := v1.Group("/creators")
		{
			creators.GET("", creatorHandler.ListCreators)
			creators.GET("/:id", creatorHandler.GetCreator)
			creators.GET("/tier/:tier", creatorHandler.GetCreatorsByTier)
			creators.GET("/:id/content", creatorHandler.GetCreatorContent)
		}

		// Video endpoints
		videos := v1.Group("/videos")
		{
			videos.GET("", videoHandler.ListVideos)
			videos.GET("/:id", videoHandler.GetVideo)
			videos.GET("/:id/transcript", videoHandler.GetVideoTranscript)
		}

		// Admin endpoints (requires auth)
		admin := v1.Group("/admin")
		admin.Use(middleware.AuthMiddleware(cfg.JWTSecret))
		{
			// Content management
			admin.POST("/content/ingest", contentHandler.TriggerIngestion)
			admin.POST("/content/:id/process", contentHandler.ProcessContent)
			admin.DELETE("/content/:id", contentHandler.DeleteContent)

			// Creator management
			admin.POST("/creators", creatorHandler.CreateCreator)
			admin.PUT("/creators/:id", creatorHandler.UpdateCreator)
			admin.DELETE("/creators/:id", creatorHandler.DeleteCreator)
			admin.POST("/creators/:id/verify", creatorHandler.VerifyCreator)

			// Video generation
			admin.POST("/videos/generate", videoHandler.GenerateVideo)
			admin.GET("/videos/queue", videoHandler.GetVideoQueue)

			// Configuration (Appsmith integration)
			admin.GET("/config", adminHandler.GetConfig)
			admin.PUT("/config", adminHandler.UpdateConfig)
			admin.GET("/config/sources", adminHandler.GetSourcesConfig)
			admin.PUT("/config/sources", adminHandler.UpdateSourcesConfig)
			admin.GET("/config/templates", adminHandler.GetVideoTemplates)
			admin.PUT("/config/templates", adminHandler.UpdateVideoTemplates)

			// Analytics
			admin.GET("/analytics/overview", adminHandler.GetAnalyticsOverview)
			admin.GET("/analytics/content", adminHandler.GetContentAnalytics)
			admin.GET("/analytics/creators", adminHandler.GetCreatorAnalytics)

			// White-label configuration
			admin.GET("/whitelabel", whitelabelHandler.GetWhitelabelConfig)
			admin.PUT("/whitelabel", whitelabelHandler.UpdateWhitelabelConfig)
		}

		// Webhook endpoints for platform integrations
		webhooks := v1.Group("/webhooks")
		{
			webhooks.POST("/youtube", webhookHandler.YouTubeWebhook)
			webhooks.GET("/youtube", webhookHandler.YouTubeWebhook)
			webhooks.POST("/twitter", webhookHandler.TwitterWebhook)
			webhooks.GET("/twitter", webhookHandler.TwitterWebhook)
			webhooks.POST("/reddit", webhookHandler.RedditWebhook)
		}
	}

	// Create HTTP server
	srv := &http.Server{
		Addr:              fmt.Sprintf(":%s", cfg.Port),
		Handler:           router,
		ReadTimeout:       30 * time.Second,
		ReadHeaderTimeout: 5 * time.Second,
		WriteTimeout:      30 * time.Second,
		IdleTimeout:       60 * time.Second,
		MaxHeaderBytes:    1 << 20, // 1 MB
	}

	// Start server in goroutine
	go func() {
		logger.Info("Starting HTTP server",
			zap.String("port", cfg.Port),
			zap.String("environment", cfg.Environment),
		)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logger.Fatal("Failed to start server", zap.Error(err))
		}
	}()

	// Wait for interrupt signal
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	logger.Info("Shutting down server...")

	// Graceful shutdown with 30 second timeout
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		logger.Error("Server forced to shutdown", zap.Error(err))
	}

	logger.Info("Server exited properly")
}

func initLogger() (*zap.Logger, error) {
	env := os.Getenv("ELEVATEDIQ_ENVIRONMENT")
	if env == "production" {
		return zap.NewProduction()
	}
	return zap.NewDevelopment()
}
