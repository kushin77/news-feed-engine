// Package handlers provides HTTP handlers for video-related endpoints
package handlers

import (
	"net/http"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/kushin77/elevatedIQ/services/news-feed-engine/internal/database"
	"github.com/kushin77/elevatedIQ/services/news-feed-engine/internal/kafka"
	"github.com/kushin77/elevatedIQ/services/news-feed-engine/internal/middleware"
)

// VideoHandler handles video-related operations
type VideoHandler struct {
	repo            *database.VideoRepository
	kafkaProducer   *kafka.Producer
	kafkaVideoTopic string
}

// NewVideoHandler creates a new video handler
func NewVideoHandler(repo *database.VideoRepository, kafkaProducer *kafka.Producer, videoTopic string) *VideoHandler {
	return &VideoHandler{
		repo:            repo,
		kafkaProducer:   kafkaProducer,
		kafkaVideoTopic: videoTopic,
	}
}

// ListVideos returns a paginated list of generated video summaries
func (h *VideoHandler) ListVideos(c *gin.Context) {
	tenantID := middleware.GetTenantID(c)
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "20"))
	status := c.Query("status")
	contentIDStr := c.Query("content_id")

	// Validate pagination
	if page < 1 {
		page = 1
	}
	if limit < 1 || limit > 100 {
		limit = 20
	}

	// Parse content ID if provided
	var contentID *uuid.UUID
	if contentIDStr != "" {
		if parsed, err := uuid.Parse(contentIDStr); err == nil {
			contentID = &parsed
		}
	}

	opts := database.VideoListOptions{
		Page:      page,
		Limit:     limit,
		Status:    status,
		ContentID: contentID,
		SortBy:    c.DefaultQuery("sort", "created_at"),
		Order:     c.DefaultQuery("order", "desc"),
	}

	videos, total, err := h.repo.List(c.Request.Context(), tenantID, opts)
	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "Failed to retrieve videos",
		})
		return
	}

	totalPages := (total + limit - 1) / limit

	c.JSON(http.StatusOK, PaginatedResponse{
		Data: videos,
		Pagination: Pagination{
			Page:       page,
			Limit:      limit,
			TotalItems: int64(total),
			TotalPages: totalPages,
			HasMore:    page < totalPages,
		},
	})
}

// GetVideo returns a single video by ID
func (h *VideoHandler) GetVideo(c *gin.Context) {
	tenantID := middleware.GetTenantID(c)
	videoIDStr := c.Param("id")

	videoID, err := uuid.Parse(videoIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "invalid_id",
			Message: "Invalid video ID format",
		})
		return
	}

	video, err := h.repo.GetByID(c.Request.Context(), tenantID, videoID)
	if err != nil {
		if err.Error() == "video not found" {
			c.JSON(http.StatusNotFound, ErrorResponse{
				Error:   "not_found",
				Message: "Video not found",
			})
			return
		}
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "Failed to retrieve video",
		})
		return
	}

	c.JSON(http.StatusOK, SuccessResponse{
		Success: true,
		Data:    video,
	})
}

// GetVideoTranscript returns the transcript for a video
func (h *VideoHandler) GetVideoTranscript(c *gin.Context) {
	tenantID := middleware.GetTenantID(c)
	videoIDStr := c.Param("id")
	format := c.DefaultQuery("format", "text")

	// Validate format
	validFormats := map[string]bool{
		"text": true,
		"srt":  true,
		"vtt":  true,
		"json": true,
	}
	if !validFormats[format] {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "bad_request",
			Message: "invalid format, must be one of: text, srt, vtt, json",
			Code:    "INVALID_FORMAT",
		})
		return
	}

	videoID, err := uuid.Parse(videoIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "invalid_id",
			Message: "Invalid video ID format",
		})
		return
	}

	transcript, err := h.repo.GetTranscript(c.Request.Context(), tenantID, videoID)
	if err != nil {
		if err.Error() == "video not found" {
			c.JSON(http.StatusNotFound, ErrorResponse{
				Error:   "not_found",
				Message: "Video not found",
			})
			return
		}
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "Failed to retrieve transcript",
		})
		return
	}

	// TODO: Format conversion (SRT, VTT, JSON) - for now just return text
	c.JSON(http.StatusOK, SuccessResponse{
		Success: true,
		Data: map[string]interface{}{
			"video_id":   videoID.String(),
			"tenant_id":  tenantID,
			"format":     format,
			"transcript": transcript,
		},
	})
}

// GenerateVideo queues a new video generation job
func (h *VideoHandler) GenerateVideo(c *gin.Context) {
	tenantID := middleware.GetTenantID(c)

	var request struct {
		ContentID  string                 `json:"content_id" binding:"required"`
		TemplateID string                 `json:"template_id"`
		VoiceID    string                 `json:"voice_id"`
		AvatarID   string                 `json:"avatar_id"`
		Resolution string                 `json:"resolution"`
		Priority   int                    `json:"priority"`
		Options    map[string]interface{} `json:"options,omitempty"`
	}

	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "bad_request",
			Message: "invalid request body: " + err.Error(),
		})
		return
	}

	// Validate content ID
	if _, err := uuid.Parse(request.ContentID); err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "invalid_content_id",
			Message: "Invalid content ID format",
		})
		return
	}

	// Validate resolution if provided
	validResolutions := map[string]bool{
		"720p":  true,
		"1080p": true,
		"4k":    true,
	}
	if request.Resolution != "" && !validResolutions[request.Resolution] {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "bad_request",
			Message: "invalid resolution, must be one of: 720p, 1080p, 4k",
			Code:    "INVALID_RESOLUTION",
		})
		return
	}

	// Default priority
	if request.Priority == 0 {
		request.Priority = 5
	}

	// Publish video generation job to Kafka
	msg := kafka.VideoGenerationMessage{
		TenantID:    tenantID,
		ContentID:   request.ContentID,
		TemplateID:  request.TemplateID,
		VoiceID:     request.VoiceID,
		AvatarID:    request.AvatarID,
		Options:     request.Options,
		Priority:    request.Priority,
		RequestedAt: time.Now(),
	}

	err := h.kafkaProducer.Publish(c.Request.Context(), kafka.Message{
		Topic: h.kafkaVideoTopic,
		Key:   tenantID + "/" + request.ContentID,
		Value: msg,
	})

	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "kafka_error",
			Message: "Failed to queue video generation job",
		})
		return
	}

	c.JSON(http.StatusAccepted, SuccessResponse{
		Success: true,
		Message: "video generation job queued successfully",
		Data: map[string]interface{}{
			"tenant_id":   tenantID,
			"content_id":  request.ContentID,
			"template_id": request.TemplateID,
			"priority":    request.Priority,
			"status":      "queued",
		},
	})
}

// GetVideoQueue returns the current video generation queue status
func (h *VideoHandler) GetVideoQueue(c *gin.Context) {
	tenantID := middleware.GetTenantID(c)

	stats, err := h.repo.GetQueueStats(c.Request.Context(), tenantID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "Failed to retrieve queue statistics",
		})
		return
	}

	c.JSON(http.StatusOK, SuccessResponse{
		Success: true,
		Data:    stats,
	})
}
