// Package handlers provides HTTP handlers for creator-related endpoints
package handlers

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/kushin77/elevatedIQ/services/news-feed-engine/internal/database"
	"github.com/kushin77/elevatedIQ/services/news-feed-engine/internal/middleware"
	"github.com/kushin77/elevatedIQ/services/news-feed-engine/internal/models"
)

// CreatorHandler handles creator-related operations
type CreatorHandler struct {
	repo        *database.CreatorRepository
	contentRepo *database.ContentRepository
}

// NewCreatorHandler creates a new creator handler
func NewCreatorHandler(repo *database.CreatorRepository, contentRepo *database.ContentRepository) *CreatorHandler {
	return &CreatorHandler{
		repo:        repo,
		contentRepo: contentRepo,
	}
}

// ListCreators returns a paginated list of content creators
func (h *CreatorHandler) ListCreators(c *gin.Context) {
	tenantID := middleware.GetTenantID(c)
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "20"))
	platform := c.Query("platform")
	tier := c.Query("tier")
	verifiedOnly := c.Query("verified") == "true"

	// Validate pagination
	if page < 1 {
		page = 1
	}
	if limit < 1 || limit > 100 {
		limit = 20
	}

	opts := database.CreatorListOptions{
		Page:         page,
		Limit:        limit,
		Platform:     platform,
		Tier:         tier,
		VerifiedOnly: verifiedOnly,
		SortBy:       c.DefaultQuery("sort", "created_at"),
		Order:        c.DefaultQuery("order", "desc"),
	}

	creators, total, err := h.repo.List(c.Request.Context(), tenantID, opts)
	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "Failed to retrieve creators",
		})
		return
	}

	totalPages := (total + limit - 1) / limit

	c.JSON(http.StatusOK, PaginatedResponse{
		Data: creators,
		Pagination: Pagination{
			Page:       page,
			Limit:      limit,
			TotalItems: int64(total),
			TotalPages: totalPages,
			HasMore:    page < totalPages,
		},
	})
}

// GetCreator returns a single creator by ID
func (h *CreatorHandler) GetCreator(c *gin.Context) {
	tenantID := middleware.GetTenantID(c)
	creatorIDStr := c.Param("id")

	creatorID, err := uuid.Parse(creatorIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "invalid_id",
			Message: "Invalid creator ID format",
		})
		return
	}

	creator, err := h.repo.GetByID(c.Request.Context(), tenantID, creatorID)
	if err != nil {
		if err.Error() == "creator not found" {
			c.JSON(http.StatusNotFound, ErrorResponse{
				Error:   "not_found",
				Message: "Creator not found",
			})
			return
		}
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "Failed to retrieve creator",
		})
		return
	}

	c.JSON(http.StatusOK, SuccessResponse{
		Success: true,
		Data:    creator,
	})
}

// GetCreatorsByTier returns creators filtered by tier
func (h *CreatorHandler) GetCreatorsByTier(c *gin.Context) {
	tenantID := middleware.GetTenantID(c)
	tier := c.Param("tier")
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "20"))

	// Validate tier
	validTiers := map[string]bool{
		"platinum":   true,
		"gold":       true,
		"silver":     true,
		"bronze":     true,
		"unverified": true,
	}
	if !validTiers[tier] {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "bad_request",
			Message: "invalid tier value",
			Code:    "INVALID_TIER",
		})
		return
	}

	// Validate pagination
	if page < 1 {
		page = 1
	}
	if limit < 1 || limit > 100 {
		limit = 20
	}

	opts := database.CreatorListOptions{
		Page:   page,
		Limit:  limit,
		Tier:   tier,
		SortBy: c.DefaultQuery("sort", "follower_count"),
		Order:  c.DefaultQuery("order", "desc"),
	}

	creators, total, err := h.repo.List(c.Request.Context(), tenantID, opts)
	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "Failed to retrieve creators",
		})
		return
	}

	totalPages := (total + limit - 1) / limit

	c.JSON(http.StatusOK, PaginatedResponse{
		Data: creators,
		Pagination: Pagination{
			Page:       page,
			Limit:      limit,
			TotalItems: int64(total),
			TotalPages: totalPages,
			HasMore:    page < totalPages,
		},
	})
}

// GetCreatorContent returns content from a specific creator
func (h *CreatorHandler) GetCreatorContent(c *gin.Context) {
	tenantID := middleware.GetTenantID(c)
	creatorIDStr := c.Param("id")
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "20"))
	contentType := c.Query("type")

	// Validate creator ID
	creatorID, err := uuid.Parse(creatorIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "invalid_id",
			Message: "Invalid creator ID format",
		})
		return
	}

	// Validate pagination
	if page < 1 {
		page = 1
	}
	if limit < 1 || limit > 100 {
		limit = 20
	}

	// Verify creator exists
	_, err = h.repo.GetByID(c.Request.Context(), tenantID, creatorID)
	if err != nil {
		if err.Error() == "creator not found" {
			c.JSON(http.StatusNotFound, ErrorResponse{
				Error:   "not_found",
				Message: "Creator not found",
			})
			return
		}
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "Failed to verify creator",
		})
		return
	}

	// Get content by creator using ContentRepository
	opts := database.ListOptions{
		Page:     page,
		Limit:    limit,
		Category: contentType, // Using category field for content type filtering
		SortBy:   "published_at",
		Order:    "desc",
	}

	contents, total, err := h.contentRepo.ListByCreator(c.Request.Context(), tenantID, creatorID, opts)
	if err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "Failed to retrieve creator content",
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

// CreateCreator creates a new content creator
func (h *CreatorHandler) CreateCreator(c *gin.Context) {
	tenantID := middleware.GetTenantID(c)

	var request struct {
		Name            string                 `json:"name" binding:"required"`
		Platform        string                 `json:"platform" binding:"required"`
		PlatformID      string                 `json:"platform_id" binding:"required"`
		AvatarURL       string                 `json:"avatar_url"`
		Bio             string                 `json:"bio"`
		Tier            string                 `json:"tier"`
		TopicsExpertise []string               `json:"topics_expertise"`
		SocialLinks     map[string]interface{} `json:"social_links"`
	}

	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "bad_request",
			Message: "invalid request body: " + err.Error(),
		})
		return
	}

	// Validate platform
	validPlatforms := map[string]bool{
		"youtube": true, "twitter": true, "reddit": true, "rss": true, "internal": true,
	}
	if !validPlatforms[request.Platform] {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "invalid_platform",
			Message: "Platform must be one of: youtube, twitter, reddit, rss, internal",
		})
		return
	}

	// Default tier
	tier := models.CreatorTierUnverified
	if request.Tier != "" {
		tier = models.CreatorTier(request.Tier)
	}

	creator := &models.Creator{
		TenantID:        tenantID,
		Name:            request.Name,
		Platform:        models.Platform(request.Platform),
		PlatformID:      request.PlatformID,
		AvatarURL:       request.AvatarURL,
		Bio:             request.Bio,
		Tier:            tier,
		TopicsExpertise: request.TopicsExpertise,
		SocialLinks:     models.JSONB(request.SocialLinks),
		Active:          true,
	}

	if err := h.repo.Create(c.Request.Context(), creator); err != nil {
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "Failed to create creator",
		})
		return
	}

	c.JSON(http.StatusCreated, SuccessResponse{
		Success: true,
		Message: "creator created successfully",
		Data:    creator,
	})
}

// UpdateCreator updates an existing creator
func (h *CreatorHandler) UpdateCreator(c *gin.Context) {
	creatorIDStr := c.Param("id")

	creatorID, err := uuid.Parse(creatorIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "invalid_id",
			Message: "Invalid creator ID format",
		})
		return
	}

	var request struct {
		Name            string   `json:"name"`
		AvatarURL       string   `json:"avatar_url"`
		Bio             string   `json:"bio"`
		Tier            string   `json:"tier"`
		TopicsExpertise []string `json:"topics_expertise"`
		Active          *bool    `json:"active"`
	}

	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "bad_request",
			Message: "invalid request body",
		})
		return
	}

	// Build updates map
	updates := make(map[string]interface{})
	if request.Name != "" {
		updates["name"] = request.Name
	}
	if request.AvatarURL != "" {
		updates["avatar_url"] = request.AvatarURL
	}
	if request.Bio != "" {
		updates["bio"] = request.Bio
	}
	if request.Tier != "" {
		updates["tier"] = request.Tier
	}
	if len(request.TopicsExpertise) > 0 {
		updates["topics_expertise"] = request.TopicsExpertise
	}
	if request.Active != nil {
		updates["active"] = *request.Active
	}

	if len(updates) == 0 {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "bad_request",
			Message: "No fields to update",
		})
		return
	}

	if err := h.repo.Update(c.Request.Context(), creatorID, updates); err != nil {
		if err.Error() == "creator not found" {
			c.JSON(http.StatusNotFound, ErrorResponse{
				Error:   "not_found",
				Message: "Creator not found",
			})
			return
		}
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "Failed to update creator",
		})
		return
	}

	c.JSON(http.StatusOK, SuccessResponse{
		Success: true,
		Message: "creator updated successfully",
		Data: map[string]interface{}{
			"creator_id": creatorID.String(),
			"updated":    updates,
		},
	})
}

// DeleteCreator removes a creator (soft delete)
func (h *CreatorHandler) DeleteCreator(c *gin.Context) {
	tenantID := middleware.GetTenantID(c)
	creatorIDStr := c.Param("id")

	creatorID, err := uuid.Parse(creatorIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "invalid_id",
			Message: "Invalid creator ID format",
		})
		return
	}

	if err := h.repo.SoftDelete(c.Request.Context(), tenantID, creatorID); err != nil {
		if err.Error() == "creator not found" {
			c.JSON(http.StatusNotFound, ErrorResponse{
				Error:   "not_found",
				Message: "Creator not found",
			})
			return
		}
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "Failed to delete creator",
		})
		return
	}

	c.JSON(http.StatusOK, SuccessResponse{
		Success: true,
		Message: "creator deleted successfully",
		Data: map[string]interface{}{
			"creator_id": creatorID.String(),
			"tenant_id":  tenantID,
		},
	})
}

// VerifyCreator updates creator verification status
func (h *CreatorHandler) VerifyCreator(c *gin.Context) {
	tenantID := middleware.GetTenantID(c)
	creatorIDStr := c.Param("id")

	creatorID, err := uuid.Parse(creatorIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "invalid_id",
			Message: "Invalid creator ID format",
		})
		return
	}

	var request struct {
		Tier   string `json:"tier" binding:"required"`
		Reason string `json:"reason"`
	}

	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "bad_request",
			Message: "invalid request body",
		})
		return
	}

	// Validate tier
	validTiers := map[string]bool{
		"platinum":   true,
		"gold":       true,
		"silver":     true,
		"bronze":     true,
		"unverified": true,
	}
	if !validTiers[request.Tier] {
		c.JSON(http.StatusBadRequest, ErrorResponse{
			Error:   "bad_request",
			Message: "invalid tier value",
			Code:    "INVALID_TIER",
		})
		return
	}

	if err := h.repo.Verify(c.Request.Context(), tenantID, creatorID, request.Tier); err != nil {
		if err.Error() == "creator not found" {
			c.JSON(http.StatusNotFound, ErrorResponse{
				Error:   "not_found",
				Message: "Creator not found",
			})
			return
		}
		c.JSON(http.StatusInternalServerError, ErrorResponse{
			Error:   "database_error",
			Message: "Failed to verify creator",
		})
		return
	}

	c.JSON(http.StatusOK, SuccessResponse{
		Success: true,
		Message: "creator verification updated successfully",
		Data: map[string]interface{}{
			"creator_id": creatorID.String(),
			"tenant_id":  tenantID,
			"tier":       request.Tier,
			"reason":     request.Reason,
		},
	})
}
