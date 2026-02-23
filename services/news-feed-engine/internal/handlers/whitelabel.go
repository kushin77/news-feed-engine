// Package handlers provides HTTP handlers for white-label configuration
package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/kushin77/elevatedIQ/services/news-feed-engine/internal/database"
	"github.com/kushin77/elevatedIQ/services/news-feed-engine/internal/middleware"
)

// WhitelabelHandler handles white-label configuration operations
type WhitelabelHandler struct {
	configRepo *database.ConfigRepository
}

// NewWhitelabelHandler creates a new whitelabel handler
func NewWhitelabelHandler(configRepo *database.ConfigRepository) *WhitelabelHandler {
	return &WhitelabelHandler{
		configRepo: configRepo,
	}
}

// GetWhitelabelConfig returns the white-label configuration for a tenant from database
func (h *WhitelabelHandler) GetWhitelabelConfig(c *gin.Context) {
	tenantID := middleware.GetTenantID(c)

	// Retrieve configuration from database
	config, err := h.configRepo.Get(c.Request.Context(), tenantID)
	if err != nil {
		// Return default configuration if not found
		c.JSON(http.StatusOK, SuccessResponse{
			Success: true,
			Data: map[string]interface{}{
				"tenant_id":          tenantID,
				"display_name":       "ElevatedIQ News",
				"logo_url":           "/assets/logo.png",
				"favicon_url":        "/assets/favicon.ico",
				"primary_color":      "#1a73e8",
				"secondary_color":    "#4285f4",
				"accent_color":       "#fbbc04",
				"font_family":        "Inter, system-ui, sans-serif",
				"custom_css":         "",
				"custom_domain":      "",
				"enabled_platforms":  []string{"youtube", "twitter", "reddit", "rss"},
				"enabled_categories": []string{"technology", "business", "science", "health", "politics"},
				"default_voice_id":   "alloy",
				"video_watermark":    "",
				"analytics_id":       "",
				"social_links": map[string]string{
					"twitter":  "",
					"facebook": "",
					"linkedin": "",
					"youtube":  "",
				},
				"footer_text":          "© 2024 ElevatedIQ. All rights reserved.",
				"contact_email":        "support@elevatediq.com",
				"privacy_policy_url":   "/privacy",
				"terms_of_service_url": "/terms",
				"settings": map[string]interface{}{
					"show_creator_profiles":  true,
					"show_engagement_stats":  true,
					"enable_comments":        false,
					"enable_sharing":         true,
					"enable_bookmarks":       true,
					"default_content_layout": "grid",
					"items_per_page":         20,
					"video_autoplay":         false,
				},
			},
		})
		return
	}

	c.JSON(http.StatusOK, SuccessResponse{
		Success: true,
		Data:    config,
	})
}

// UpdateWhitelabelConfig updates the white-label configuration in database
func (h *WhitelabelHandler) UpdateWhitelabelConfig(c *gin.Context) {
	tenantID := middleware.GetTenantID(c)

	var request map[string]interface{}
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "bad_request",
			Message: "invalid request body: " + err.Error(),
		})
		return
	}

	// Remove protected fields
	delete(request, "tenant_id")
	delete(request, "id")
	delete(request, "created_at")
	delete(request, "updated_at")

	// Validate color formats if provided
	if primaryColor, ok := request["primary_color"].(string); ok && primaryColor != "" {
		if !isValidColor(primaryColor) {
			c.JSON(http.StatusBadRequest, ErrorResponse{
				Error:   "bad_request",
				Message: "invalid primary_color format",
				Code:    "INVALID_COLOR",
			})
			return
		}
	}

	if secondaryColor, ok := request["secondary_color"].(string); ok && secondaryColor != "" {
		if !isValidColor(secondaryColor) {
			c.JSON(http.StatusBadRequest, ErrorResponse{
				Error:   "bad_request",
				Message: "invalid secondary_color format",
				Code:    "INVALID_COLOR",
			})
			return
		}
	}

	if accentColor, ok := request["accent_color"].(string); ok && accentColor != "" {
		if !isValidColor(accentColor) {
			c.JSON(http.StatusBadRequest, ErrorResponse{
				Error:   "bad_request",
				Message: "invalid accent_color format",
				Code:    "INVALID_COLOR",
			})
			return
		}
	}

	if len(request) == 0 {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "bad_request",
			Message: "no fields to update",
		})
		return
	}

	// Update configuration in database
	if err := h.configRepo.Update(c.Request.Context(), tenantID, request); err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "failed to update configuration",
		})
		return
	}

	c.JSON(http.StatusOK, SuccessResponse{
		Success: true,
		Message: "white-label configuration updated",
		Data: map[string]interface{}{
			"tenant_id": tenantID,
			"updated":   request,
		},
	})
}

// isValidColor validates a hex color string
func isValidColor(color string) bool {
	if len(color) != 7 && len(color) != 4 {
		return false
	}
	if color[0] != '#' {
		return false
	}
	for _, c := range color[1:] {
		if !((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f') || (c >= 'A' && c <= 'F')) {
			return false
		}
	}
	return true
}
