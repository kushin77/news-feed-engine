package metrics

import (
	"context"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
)

// HealthCheckHandler represents an HTTP handler for health checks
type HealthCheckHandler struct {
	registry *HealthCheckRegistry
}

// NewHealthCheckHandler creates a new health check handler
func NewHealthCheckHandler(registry *HealthCheckRegistry) *HealthCheckHandler {
	if registry == nil {
		registry = GlobalHealthCheckRegistry
	}

	return &HealthCheckHandler{
		registry: registry,
	}
}

// HealthResponse represents the response from health check endpoints
type HealthResponse struct {
	Status      string                           `json:"status"`
	Timestamp   time.Time                        `json:"timestamp"`
	Checks      map[string]HealthCheckResultJSON `json:"checks,omitempty"`
	Description string                           `json:"description,omitempty"`
}

// HealthCheckResultJSON represents a health check result in JSON format
type HealthCheckResultJSON struct {
	Name      string    `json:"name"`
	Status    string    `json:"status"`
	Message   string    `json:"message,omitempty"`
	Timestamp time.Time `json:"timestamp"`
	Duration  int64     `json:"duration_ms"`
}

// GetHealthCheckHandler returns the main health endpoint handler
func (hch *HealthCheckHandler) GetHealthCheckHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()

		report := hch.registry.GenerateHealthReport(ctx)

		response := HealthResponse{
			Status:    string(report.Status),
			Timestamp: report.Timestamp,
			Checks:    make(map[string]HealthCheckResultJSON),
		}

		for name, result := range report.Checks {
			response.Checks[name] = HealthCheckResultJSON{
				Name:      result.Name,
				Status:    string(result.Status),
				Message:   result.Message,
				Timestamp: result.Timestamp,
				Duration:  result.Duration.Milliseconds(),
			}
		}

		statusCode := http.StatusOK
		if report.Status == HealthStatusUnhealthy {
			statusCode = http.StatusServiceUnavailable
		} else if report.Status == HealthStatusDegraded {
			statusCode = http.StatusOK // Still return 200 for degraded
		}

		c.JSON(statusCode, response)
	}
}

// GetLivenessHandler returns the liveness probe handler
func (hch *HealthCheckHandler) GetLivenessHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()

		// Check if service is alive
		results := hch.registry.CheckAll(ctx)

		// If any check is unhealthy, service is not alive
		for _, result := range results {
			if result.Status == HealthStatusUnhealthy {
				c.JSON(http.StatusServiceUnavailable, gin.H{
					"status": "unhealthy",
					"error":  result.Message,
				})
				return
			}
		}

		c.JSON(http.StatusOK, gin.H{
			"status": "alive",
		})
	}
}

// GetReadinessHandler returns the readiness probe handler
func (hch *HealthCheckHandler) GetReadinessHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()

		// Check critical services
		criticalChecks := []string{"database", "cache"}
		ready := true

		for _, checkName := range criticalChecks {
			result, err := hch.registry.CheckOne(ctx, checkName)
			if err != nil {
				// Check doesn't exist, skip
				continue
			}

			if result.Status != HealthStatusHealthy {
				ready = false
				break
			}
		}

		if !ready {
			c.JSON(http.StatusServiceUnavailable, gin.H{
				"status": "not-ready",
				"reason": "critical services not healthy",
			})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"status": "ready",
		})
	}
}

// GetCheckHandler returns a handler for a specific health check
func (hch *HealthCheckHandler) GetCheckHandler(checkName string) gin.HandlerFunc {
	return func(c *gin.Context) {
		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()

		result, err := hch.registry.CheckOne(ctx, checkName)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{
				"error": "Check not found",
			})
			return
		}

		response := HealthCheckResultJSON{
			Name:      result.Name,
			Status:    string(result.Status),
			Message:   result.Message,
			Timestamp: result.Timestamp,
			Duration:  result.Duration.Milliseconds(),
		}

		statusCode := http.StatusOK
		if result.Status == HealthStatusUnhealthy {
			statusCode = http.StatusServiceUnavailable
		}

		c.JSON(statusCode, response)
	}
}

// RegisterHealthCheckRoutes registers health check routes to a gin engine
func RegisterHealthCheckRoutes(router *gin.Engine, handler *HealthCheckHandler) {
	router.GET("/health", handler.GetHealthCheckHandler())
	router.GET("/health/live", handler.GetLivenessHandler())
	router.GET("/health/ready", handler.GetReadinessHandler())
	router.GET("/health/check/:name", func(c *gin.Context) {
		name := c.Param("name")
		handler.GetCheckHandler(name)(c)
	})
}

// RegisterHealthCheckRoutesOnGroup registers health check routes to a gin router group
func RegisterHealthCheckRoutesOnGroup(group *gin.RouterGroup, handler *HealthCheckHandler) {
	group.GET("", handler.GetHealthCheckHandler())
	group.GET("/live", handler.GetLivenessHandler())
	group.GET("/ready", handler.GetReadinessHandler())
	group.GET("/check/:name", func(c *gin.Context) {
		name := c.Param("name")
		handler.GetCheckHandler(name)(c)
	})
}

// MetricsResponse represents metrics data
type MetricsResponse struct {
	Timestamp  time.Time              `json:"timestamp"`
	Metrics    map[string]interface{} `json:"metrics"`
	Health     HealthResponse         `json:"health"`
	SystemInfo map[string]interface{} `json:"system_info,omitempty"`
}

// GetMetricsHandler returns a comprehensive metrics endpoint
func (hch *HealthCheckHandler) GetMetricsHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()

		report := hch.registry.GenerateHealthReport(ctx)

		healthResponse := HealthResponse{
			Status:    string(report.Status),
			Timestamp: report.Timestamp,
			Checks:    make(map[string]HealthCheckResultJSON),
		}

		for name, result := range report.Checks {
			healthResponse.Checks[name] = HealthCheckResultJSON{
				Name:      result.Name,
				Status:    string(result.Status),
				Message:   result.Message,
				Timestamp: result.Timestamp,
				Duration:  result.Duration.Milliseconds(),
			}
		}

		response := MetricsResponse{
			Timestamp: time.Now(),
			Metrics:   make(map[string]interface{}),
			Health:    healthResponse,
		}

		c.JSON(http.StatusOK, response)
	}
}
