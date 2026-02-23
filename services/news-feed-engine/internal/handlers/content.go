// Package handlers provides HTTP handlers for content-related endpoints
package handlers

import (
	"net/http"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/kushin77/elevatedIQ/services/news-feed-engine/internal/database"
	"github.com/kushin77/elevatedIQ/services/news-feed-engine/internal/embeddings"
	"github.com/kushin77/elevatedIQ/services/news-feed-engine/internal/kafka"
	"github.com/kushin77/elevatedIQ/services/news-feed-engine/internal/middleware"
)

// ContentHandler handles content-related operations
type ContentHandler struct {
	repo              *database.ContentRepository
	kafkaProducer     *kafka.Producer
	embeddingService  embeddings.Service
	kafkaRawTopic     string
	kafkaProcessTopic string
}

// NewContentHandler creates a new content handler
func NewContentHandler(repo *database.ContentRepository, kafkaProducer *kafka.Producer, embeddingService embeddings.Service, rawTopic, processTopic string) *ContentHandler {
	return &ContentHandler{
		repo:              repo,
		kafkaProducer:     kafkaProducer,
		embeddingService:  embeddingService,
		kafkaRawTopic:     rawTopic,
		kafkaProcessTopic: processTopic,
	}
}

// ListContent returns a paginated list of content items
func (h *ContentHandler) ListContent(c *gin.Context) {
	tenantID := middleware.GetTenantID(c)
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "20"))
	category := c.Query("category")
	platform := c.Query("platform")
	geoClass := c.Query("geo")
	sortBy := c.DefaultQuery("sort", "published_at")
	order := c.DefaultQuery("order", "desc")

	// Validate pagination
	if page < 1 {
		page = 1
	}
	if limit < 1 || limit > 100 {
		limit = 20
	}

	opts := database.ListOptions{
		Page:              page,
		Limit:             limit,
		Category:          category,
		Platform:          platform,
		GeoClassification: geoClass,
		SortBy:            sortBy,
		Order:             order,
	}

	contents, total, err := h.repo.List(c.Request.Context(), tenantID, opts)
	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "Failed to retrieve content",
		})
		return
	}

	totalPages := (total + limit - 1) / limit

	c.JSON(http.StatusOK, PaginatedResponse{
		Data: contents,
		Pagination: Pagination{
			Page:       page,
			Limit:      limit,
			TotalItems: int64(total),
			TotalPages: totalPages,
			HasMore:    page < totalPages,
		},
	})
}

// GetContent returns a single content item by ID
func (h *ContentHandler) GetContent(c *gin.Context) {
	tenantID := middleware.GetTenantID(c)
	contentIDStr := c.Param("id")

	contentID, err := uuid.Parse(contentIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "invalid_id",
			Message: "Invalid content ID format",
		})
		return
	}

	content, err := h.repo.GetByID(c.Request.Context(), tenantID, contentID)
	if err != nil {
		if err.Error() == "content not found" {
			c.JSON(http.StatusNotFound, ErrorResponse{
				Error:   "not_found",
				Message: "Content not found",
			})
			return
		}
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "Failed to retrieve content",
		})
		return
	}

	c.JSON(http.StatusOK, SuccessResponse{
		Success: true,
		Data:    content,
	})
}

// GetContentByCategory returns content filtered by category
func (h *ContentHandler) GetContentByCategory(c *gin.Context) {
	tenantID := middleware.GetTenantID(c)
	category := c.Param("category")
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "20"))

	if page < 1 {
		page = 1
	}
	if limit < 1 || limit > 100 {
		limit = 20
	}

	opts := database.ListOptions{
		Page:     page,
		Limit:    limit,
		Category: category,
	}

	contents, total, err := h.repo.List(c.Request.Context(), tenantID, opts)
	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "Failed to retrieve content",
		})
		return
	}

	totalPages := (total + limit - 1) / limit

	c.JSON(http.StatusOK, PaginatedResponse{
		Data: contents,
		Pagination: Pagination{
			Page:       page,
			Limit:      limit,
			TotalItems: int64(total),
			TotalPages: totalPages,
			HasMore:    page < totalPages,
		},
	})
}

// GetContentByGeo returns content filtered by geographic classification
func (h *ContentHandler) GetContentByGeo(c *gin.Context) {
	tenantID := middleware.GetTenantID(c)
	geoClassification := c.Param("classification")
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "20"))

	if page < 1 {
		page = 1
	}
	if limit < 1 || limit > 100 {
		limit = 20
	}

	opts := database.ListOptions{
		Page:              page,
		Limit:             limit,
		GeoClassification: geoClassification,
	}

	contents, total, err := h.repo.List(c.Request.Context(), tenantID, opts)
	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "Failed to retrieve content",
		})
		return
	}

	totalPages := (total + limit - 1) / limit

	c.JSON(http.StatusOK, PaginatedResponse{
		Data: contents,
		Pagination: Pagination{
			Page:       page,
			Limit:      limit,
			TotalItems: int64(total),
			TotalPages: totalPages,
			HasMore:    page < totalPages,
		},
	})
}

// GetTrendingContent returns trending content across all sources
func (h *ContentHandler) GetTrendingContent(c *gin.Context) {
	tenantID := middleware.GetTenantID(c)
	timeRange := c.DefaultQuery("range", "24h")
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "20"))

	if limit < 1 || limit > 100 {
		limit = 20
	}

	contents, err := h.repo.GetTrending(c.Request.Context(), tenantID, timeRange, limit)
	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "Failed to retrieve trending content",
		})
		return
	}

	c.JSON(http.StatusOK, PaginatedResponse{
		Data: contents,
		Pagination: Pagination{
			Page:       1,
			Limit:      limit,
			TotalItems: int64(len(contents)),
			TotalPages: 1,
			HasMore:    false,
		},
	})
}

// SearchContent performs semantic search across content
func (h *ContentHandler) SearchContent(c *gin.Context) {
	tenantID := middleware.GetTenantID(c)
	query := c.Query("q")
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "20"))
	category := c.Query("category")
	dateFrom := c.Query("from")
	dateTo := c.Query("to")

	if query == "" {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "bad_request",
			Message: "search query is required",
			Code:    "MISSING_QUERY",
		})
		return
	}

	if page < 1 {
		page = 1
	}
	if limit < 1 || limit > 100 {
		limit = 20
	}

	// Generate embedding for semantic search
	embedding, err := h.embeddingService.Generate(c.Request.Context(), query)
	if err != nil {
		// Fall back to text-based filtering if embedding generation fails
		opts := database.ListOptions{
			Page:     page,
			Limit:    limit,
			Category: category,
			DateFrom: dateFrom,
			DateTo:   dateTo,
		}
		contents, total, err := h.repo.List(c.Request.Context(), tenantID, opts)
		if err != nil {
			c.JSON(http.StatusInternalServerError, ErrorResponse{
				Error:   "database_error",
				Message: "Failed to search content",
			})
			return
		}
		totalPages := int((int64(total) + int64(limit) - 1) / int64(limit))
		c.JSON(http.StatusOK, PaginatedResponse{
			Data: contents,
			Pagination: Pagination{
				Page:       page,
				Limit:      limit,
				TotalItems: int64(total),
				TotalPages: totalPages,
				HasMore:    page < totalPages,
			},
		})
		return
	}

	// Use semantic search with pgvector
	opts := database.ListOptions{
		Page:     page,
		Limit:    limit,
		Category: category,
		DateFrom: dateFrom,
		DateTo:   dateTo,
	}
	contents, total, err := h.repo.SearchSemantic(c.Request.Context(), tenantID, embedding, opts)
	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "Failed to search content",
		})
		return
	}

	totalPages := (total + limit - 1) / limit

	c.JSON(http.StatusOK, PaginatedResponse{
		Data: contents,
		Pagination: Pagination{
			Page:       page,
			Limit:      limit,
			TotalItems: int64(total),
			TotalPages: totalPages,
			HasMore:    page < totalPages,
		},
	})
}

// TriggerIngestion triggers content ingestion from configured sources
func (h *ContentHandler) TriggerIngestion(c *gin.Context) {
	tenantID := middleware.GetTenantID(c)

	var request struct {
		Sources  []string `json:"sources"`  // List of source URLs or IDs to ingest
		Platform string   `json:"platform"` // youtube, twitter, reddit, rss
		Force    bool     `json:"force"`    // Force re-ingestion even if already processed
		Priority int      `json:"priority"` // Job priority (1-10, 10 = highest)
	}

	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "bad_request",
			Message: "invalid request body",
		})
		return
	}

	// Validate platform
	validPlatforms := map[string]bool{
		"youtube": true,
		"twitter": true,
		"reddit":  true,
		"rss":     true,
	}

	if request.Platform != "" && !validPlatforms[request.Platform] {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "invalid_platform",
			Message: "Platform must be one of: youtube, twitter, reddit, rss",
		})
		return
	}

	// Default priority
	if request.Priority == 0 {
		request.Priority = 5
	}

	// Publish ingestion jobs to Kafka (one message per source)
	jobsQueued := 0
	for _, sourceURL := range request.Sources {
		msg := kafka.ContentIngestionMessage{
			TenantID:   tenantID,
			SourceType: request.Platform,
			SourceID:   sourceURL,
			URL:        sourceURL,
			Priority:   request.Priority,
			Metadata: map[string]interface{}{
				"force": request.Force,
			},
			RequestedAt: time.Now(),
		}

		err := h.kafkaProducer.Publish(c.Request.Context(), kafka.Message{
			Topic: h.kafkaRawTopic,
			Key:   tenantID + "/" + request.Platform + "/" + sourceURL,
			Value: msg,
		})

		if err != nil {
			// Log error but continue with other sources
			continue
		}
		jobsQueued++
	}

	if jobsQueued == 0 {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "kafka_error",
			Message: "Failed to queue any ingestion jobs",
		})
		return
	}

	c.JSON(http.StatusAccepted, SuccessResponse{
		Success: true,
		Message: "ingestion jobs queued successfully",
		Data: map[string]interface{}{
			"tenant_id":   tenantID,
			"sources":     len(request.Sources),
			"jobs_queued": jobsQueued,
			"platform":    request.Platform,
			"priority":    request.Priority,
		},
	})
}

// ProcessContent triggers AI processing for a specific content item
func (h *ContentHandler) ProcessContent(c *gin.Context) {
	tenantID := middleware.GetTenantID(c)
	contentID := c.Param("id")

	var request struct {
		ActionType string                 `json:"action_type"` // summarize, analyze_sentiment, extract_entities, generate_thumbnail
		Priority   int                    `json:"priority"`
		Metadata   map[string]interface{} `json:"metadata,omitempty"`
	}

	if err := c.ShouldBindJSON(&request); err != nil {
		// Default action if not provided
		request.ActionType = "summarize"
		request.Priority = 5
	}

	// Validate content ID format
	if _, err := uuid.Parse(contentID); err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "invalid_id",
			Message: "Invalid content ID format",
		})
		return
	}

	// Publish processing job to Kafka
	msg := kafka.ContentProcessingMessage{
		TenantID:   tenantID,
		ContentID:  contentID,
		ActionType: request.ActionType,
		Priority:   request.Priority,
		Metadata:   request.Metadata,
		QueuedAt:   time.Now(),
	}

	err := h.kafkaProducer.Publish(c.Request.Context(), kafka.Message{
		Topic: h.kafkaProcessTopic,
		Key:   tenantID + "/" + contentID,
		Value: msg,
	})

	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "kafka_error",
			Message: "Failed to queue processing job",
		})
		return
	}

	c.JSON(http.StatusAccepted, SuccessResponse{
		Success: true,
		Message: "content processing queued successfully",
		Data: map[string]interface{}{
			"content_id":  contentID,
			"tenant_id":   tenantID,
			"action_type": request.ActionType,
			"priority":    request.Priority,
		},
	})
}

// DeleteContent removes a content item (soft delete)
func (h *ContentHandler) DeleteContent(c *gin.Context) {
	tenantID := middleware.GetTenantID(c)
	contentIDStr := c.Param("id")

	contentID, err := uuid.Parse(contentIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "invalid_id",
			Message: "Invalid content ID format",
		})
		return
	}

	if err := h.repo.SoftDelete(c.Request.Context(), tenantID, contentID); err != nil {
		if err.Error() == "content not found" {
			c.JSON(http.StatusNotFound, ErrorResponse{
				Error:   "not_found",
				Message: "Content not found",
			})
			return
		}
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "Failed to delete content",
		})
		return
	}

	c.JSON(http.StatusOK, SuccessResponse{
		Success: true,
		Message: "content deleted",
		Data: map[string]interface{}{
			"content_id": contentID,
			"tenant_id":  tenantID,
		},
	})
}
