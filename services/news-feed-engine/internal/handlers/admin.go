// Package handlers provides HTTP handlers for admin configuration endpoints
// These endpoints are designed for Appsmith integration
package handlers

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/kushin77/elevatedIQ/services/news-feed-engine/internal/database"
	"github.com/kushin77/elevatedIQ/services/news-feed-engine/internal/middleware"
)

// AdminHandler handles admin configuration operations
type AdminHandler struct {
	configRepo    *database.ConfigRepository
	sourceRepo    *database.SourceRepository
	templateRepo  *database.TemplateRepository
	analyticsRepo *database.AnalyticsRepository
}

// NewAdminHandler creates a new admin handler with repository dependencies
func NewAdminHandler(
	configRepo *database.ConfigRepository,
	sourceRepo *database.SourceRepository,
	templateRepo *database.TemplateRepository,
	analyticsRepo *database.AnalyticsRepository,
) *AdminHandler {
	return &AdminHandler{
		configRepo:    configRepo,
		sourceRepo:    sourceRepo,
		templateRepo:  templateRepo,
		analyticsRepo: analyticsRepo,
	}
}

// GetConfig returns the current tenant configuration from database
func (h *AdminHandler) GetConfig(c *gin.Context) {
	tenantID := middleware.GetTenantID(c)

	config, err := h.configRepo.Get(c.Request.Context(), tenantID)
	if err != nil {
		// Return default config if not found
		c.JSON(http.StatusOK, SuccessResponse{
			Success: true,
			Data: map[string]interface{}{
				"tenant_id":           tenantID,
				"ingestion_interval":  "15m",
				"max_concurrent_jobs": 3,
				"default_video_voice": "alloy",
				"video_resolution":    "1080p",
				"content_retention":   "90d",
				"auto_publish":        true,
				"moderation_enabled":  true,
				"ai_analysis_enabled": true,
				"enabled_platforms":   []string{"youtube", "twitter", "reddit", "rss"},
				"enabled_categories":  []string{"technology", "business", "science", "health", "politics"},
				"geo_classifications": []string{"local", "regional", "national", "global"},
			},
		})
		return
	}

	c.JSON(http.StatusOK, SuccessResponse{
		Success: true,
		Data:    config,
	})
}

// UpdateConfig updates the tenant configuration in database
func (h *AdminHandler) UpdateConfig(c *gin.Context) {
	tenantID := middleware.GetTenantID(c)

	var request map[string]interface{}
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "bad_request",
			Message: "invalid request body",
		})
		return
	}

	// Remove protected fields from updates
	delete(request, "tenant_id")
	delete(request, "id")
	delete(request, "created_at")
	delete(request, "updated_at")

	if len(request) == 0 {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "bad_request",
			Message: "no fields to update",
		})
		return
	}

	if err := h.configRepo.Update(c.Request.Context(), tenantID, request); err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "failed to update configuration",
		})
		return
	}

	c.JSON(http.StatusOK, SuccessResponse{
		Success: true,
		Message: "configuration updated",
		Data: map[string]interface{}{
			"tenant_id": tenantID,
			"updated":   request,
		},
	})
}

// GetSourcesConfig returns configured content sources from database
func (h *AdminHandler) GetSourcesConfig(c *gin.Context) {
	tenantID := middleware.GetTenantID(c)

	sources, err := h.sourceRepo.List(c.Request.Context(), tenantID, database.SourceListOptions{})
	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "failed to retrieve sources",
		})
		return
	}

	c.JSON(http.StatusOK, SuccessResponse{
		Success: true,
		Data: map[string]interface{}{
			"tenant_id": tenantID,
			"sources":   sources,
			"count":     len(sources),
		},
	})
}

// UpdateSourcesConfig updates content source configuration in database
func (h *AdminHandler) UpdateSourcesConfig(c *gin.Context) {
	tenantID := middleware.GetTenantID(c)

	var request struct {
		Sources []database.SourceUpdate `json:"sources"`
	}

	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "bad_request",
			Message: "invalid request body",
		})
		return
	}

	// Process each source update
	updated := 0
	errors := make([]string, 0)
	for _, source := range request.Sources {
		if err := h.sourceRepo.Update(c.Request.Context(), tenantID, source.ID, source); err != nil {
			errors = append(errors, source.ID)
		} else {
			updated++
		}
	}

	c.JSON(http.StatusOK, SuccessResponse{
		Success: true,
		Message: "sources configuration updated",
		Data: map[string]interface{}{
			"tenant_id":     tenantID,
			"sources_count": updated,
			"errors":        errors,
		},
	})
}

// GetVideoTemplates returns available video generation templates from database
func (h *AdminHandler) GetVideoTemplates(c *gin.Context) {
	tenantID := middleware.GetTenantID(c)

	templates, err := h.templateRepo.List(c.Request.Context(), tenantID, database.TemplateListOptions{})
	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "failed to retrieve templates",
		})
		return
	}

	c.JSON(http.StatusOK, SuccessResponse{
		Success: true,
		Data: map[string]interface{}{
			"tenant_id": tenantID,
			"templates": templates,
			"count":     len(templates),
		},
	})
}

// UpdateVideoTemplates updates video generation templates in database
func (h *AdminHandler) UpdateVideoTemplates(c *gin.Context) {
	tenantID := middleware.GetTenantID(c)

	var request struct {
		Templates []database.TemplateUpdate `json:"templates"`
	}

	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "bad_request",
			Message: "invalid request body",
		})
		return
	}

	// Process each template update
	updated := 0
	errors := make([]string, 0)
	for _, template := range request.Templates {
		if err := h.templateRepo.Update(c.Request.Context(), tenantID, template.ID, template); err != nil {
			errors = append(errors, template.ID)
		} else {
			updated++
		}
	}

	c.JSON(http.StatusOK, SuccessResponse{
		Success: true,
		Message: "video templates updated",
		Data: map[string]interface{}{
			"tenant_id":       tenantID,
			"templates_count": updated,
			"errors":          errors,
		},
	})
}

// GetAnalyticsOverview returns overview analytics from database
func (h *AdminHandler) GetAnalyticsOverview(c *gin.Context) {
	tenantID := middleware.GetTenantID(c)
	timeRange := c.DefaultQuery("range", "7d")

	// Parse days from range
	days := 7
	if len(timeRange) > 1 && timeRange[len(timeRange)-1] == 'd' {
		if d, err := strconv.Atoi(timeRange[:len(timeRange)-1]); err == nil {
			days = d
		}
	}

	overview, err := h.analyticsRepo.GetOverview(c.Request.Context(), tenantID, days)
	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "failed to retrieve analytics",
		})
		return
	}

	overview["tenant_id"] = tenantID
	overview["time_range"] = timeRange

	c.JSON(http.StatusOK, SuccessResponse{
		Success: true,
		Data:    overview,
	})
}

// GetContentAnalytics returns content-specific analytics from database
func (h *AdminHandler) GetContentAnalytics(c *gin.Context) {
	tenantID := middleware.GetTenantID(c)
	timeRange := c.DefaultQuery("range", "7d")
	category := c.Query("category")
	platform := c.Query("platform")

	// Parse days from range
	days := 7
	if len(timeRange) > 1 && timeRange[len(timeRange)-1] == 'd' {
		if d, err := strconv.Atoi(timeRange[:len(timeRange)-1]); err == nil {
			days = d
		}
	}

	opts := database.ContentAnalyticsOptions{
		Days:     days,
		Category: category,
		Platform: platform,
	}

	analytics, err := h.analyticsRepo.GetContentAnalytics(c.Request.Context(), tenantID, opts)
	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "failed to retrieve content analytics",
		})
		return
	}

	analytics["tenant_id"] = tenantID
	analytics["time_range"] = timeRange
	analytics["category"] = category
	analytics["platform"] = platform

	c.JSON(http.StatusOK, SuccessResponse{
		Success: true,
		Data:    analytics,
	})
}

// GetCreatorAnalytics returns creator-specific analytics from database
func (h *AdminHandler) GetCreatorAnalytics(c *gin.Context) {
	tenantID := middleware.GetTenantID(c)
	timeRange := c.DefaultQuery("range", "7d")

	// Parse days from range
	days := 7
	if len(timeRange) > 1 && timeRange[len(timeRange)-1] == 'd' {
		if d, err := strconv.Atoi(timeRange[:len(timeRange)-1]); err == nil {
			days = d
		}
	}

	analytics, err := h.analyticsRepo.GetCreatorAnalytics(c.Request.Context(), tenantID, days)
	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "failed to retrieve creator analytics",
		})
		return
	}

	analytics["tenant_id"] = tenantID
	analytics["time_range"] = timeRange

	c.JSON(http.StatusOK, SuccessResponse{
		Success: true,
		Data:    analytics,
	})
}
