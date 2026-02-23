// Package handlers provides HTTP handlers for the News Feed Engine API
package handlers

import (
	"context"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/kushin77/elevatedIQ/services/news-feed-engine/internal/database"
	"github.com/kushin77/elevatedIQ/services/news-feed-engine/internal/kafka"
)

// ServiceStatus represents the overall service health status
type ServiceStatus struct {
	Status    string            `json:"status"`
	Service   string            `json:"service"`
	Version   string            `json:"version"`
	Timestamp string            `json:"timestamp"`
	Checks    map[string]string `json:"checks,omitempty"`
}

// HealthCheck holds dependencies for health checks
type HealthCheck struct {
	db       *database.DB
	producer *kafka.Producer
}

// NewHealthCheck creates a new health check handler
func NewHealthCheck(db *database.DB, producer *kafka.Producer) *HealthCheck {
	return &HealthCheck{
		db:       db,
		producer: producer,
	}
}

// HealthHandler returns basic service health status
func HealthHandler(c *gin.Context) {
	c.JSON(http.StatusOK, ServiceStatus{
		Status:    "healthy",
		Service:   "news-feed-engine",
		Version:   "1.0.0",
		Timestamp: time.Now().UTC().Format(time.RFC3339),
	})
}

// ReadinessHandler checks if the service is ready to accept traffic
func ReadinessHandler(c *gin.Context) {
	// Basic readiness without DB checks (for backwards compatibility)
	checks := map[string]string{
		"postgres": "healthy",
		"kafka":    "healthy",
	}

	c.JSON(http.StatusOK, ServiceStatus{
		Status:    "ready",
		Service:   "news-feed-engine",
		Version:   "1.0.0",
		Timestamp: time.Now().UTC().Format(time.RFC3339),
		Checks:    checks,
	})
}

// Readiness checks if the service is ready to accept traffic with actual dependency checks
func (h *HealthCheck) Readiness(c *gin.Context) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), 5*time.Second)
	defer cancel()

	checks := make(map[string]string)
	allHealthy := true

	// Check PostgreSQL connection
	if h.db != nil {
		if err := h.db.PingContext(ctx); err != nil {
			checks["postgres"] = "unhealthy: " + err.Error()
			allHealthy = false
		} else {
			checks["postgres"] = "healthy"
		}
	} else {
		checks["postgres"] = "not_configured"
	}

	// Check Kafka connection
	if h.producer != nil {
		// Kafka producer is considered healthy if it was initialized
		// A more thorough check could send a test message to a health topic
		checks["kafka"] = "healthy"
	} else {
		checks["kafka"] = "not_configured"
	}

	status := "ready"
	httpStatus := http.StatusOK
	if !allHealthy {
		status = "not_ready"
		httpStatus = http.StatusServiceUnavailable
	}

	c.JSON(httpStatus, ServiceStatus{
		Status:    status,
		Service:   "news-feed-engine",
		Version:   "1.0.0",
		Timestamp: time.Now().UTC().Format(time.RFC3339),
		Checks:    checks,
	})
}

// Liveness returns basic health for liveness probes
func (h *HealthCheck) Liveness(c *gin.Context) {
	c.JSON(http.StatusOK, ServiceStatus{
		Status:    "healthy",
		Service:   "news-feed-engine",
		Version:   "1.0.0",
		Timestamp: time.Now().UTC().Format(time.RFC3339),
	})
}

// PaginatedResponse represents a paginated API response
type PaginatedResponse struct {
	Data       interface{} `json:"data"`
	Pagination Pagination  `json:"pagination"`
}

// Pagination represents pagination metadata
type Pagination struct {
	Page       int   `json:"page"`
	Limit      int   `json:"limit"`
	TotalItems int64 `json:"total_items"`
	TotalPages int   `json:"total_pages"`
	HasMore    bool  `json:"has_more"`
}

// ErrorResponse represents an API error response
type ErrorResponse struct {
	Error   string `json:"error"`
	Message string `json:"message"`
	Code    string `json:"code,omitempty"`
}

// SuccessResponse represents a successful API response
type SuccessResponse struct {
	Success bool        `json:"success"`
	Message string      `json:"message,omitempty"`
	Data    interface{} `json:"data,omitempty"`
}
