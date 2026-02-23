package metrics

import (
	"context"
	"time"

	"github.com/gin-gonic/gin"
	"go.opentelemetry.io/otel/attribute"
)

// ServiceHealthChecks provides standard health checks for all services
type ServiceHealthChecks struct {
	registry *HealthCheckRegistry
	db       interface{} // Can be *sql.DB or other DB types
	cache    interface{} // Can be *redis.Client or other cache types
}

// NewServiceHealthChecks creates a new service health checks instance
func NewServiceHealthChecks(registry *HealthCheckRegistry) *ServiceHealthChecks {
	return &ServiceHealthChecks{
		registry: registry,
	}
}

// RegisterDatabaseCheck registers a database health check
func (shc *ServiceHealthChecks) RegisterDatabaseCheck(checker HealthChecker) error {
	return shc.registry.Register("database", checker)
}

// RegisterCacheCheck registers a cache health check
func (shc *ServiceHealthChecks) RegisterCacheCheck(checker HealthChecker) error {
	return shc.registry.Register("cache", checker)
}

// RegisterServiceCheck registers a service-specific health check
func (shc *ServiceHealthChecks) RegisterServiceCheck(name string, checker HealthChecker) error {
	return shc.registry.Register(name, checker)
}

// GetRegistry returns the underlying health check registry
func (shc *ServiceHealthChecks) GetRegistry() *HealthCheckRegistry {
	return shc.registry
}

// CreateHealthHandler creates a Gin handler for health checks
func (shc *ServiceHealthChecks) CreateHealthHandler() gin.HandlerFunc {
	handler := NewHealthCheckHandler(shc.registry)
	return handler.GetHealthCheckHandler()
}

// CreateLivenessHandler creates a Gin handler for liveness probes
func (shc *ServiceHealthChecks) CreateLivenessHandler() gin.HandlerFunc {
	handler := NewHealthCheckHandler(shc.registry)
	return handler.GetLivenessHandler()
}

// CreateReadinessHandler creates a Gin handler for readiness probes
func (shc *ServiceHealthChecks) CreateReadinessHandler() gin.HandlerFunc {
	handler := NewHealthCheckHandler(shc.registry)
	return handler.GetReadinessHandler()
}

// CreateMetricsHandler creates a Gin handler for metrics
func (shc *ServiceHealthChecks) CreateMetricsHandler() gin.HandlerFunc {
	handler := NewHealthCheckHandler(shc.registry)
	return handler.GetMetricsHandler()
}

// RegisterDefaultChecks registers common service health checks
func (shc *ServiceHealthChecks) RegisterDefaultChecks(serviceName string) error {
	// Register a basic service health check
	return shc.registry.Register(serviceName, func(ctx context.Context) HealthCheckResult {
		return HealthCheckResult{
			Name:      serviceName,
			Status:    HealthStatusHealthy,
			Message:   "Service is running",
			Timestamp: time.Now(),
		}
	})
}

// RegisterRoutes registers all health check routes with a Gin engine
func (shc *ServiceHealthChecks) RegisterRoutes(router *gin.Engine) {
	RegisterHealthCheckRoutes(router, NewHealthCheckHandler(shc.registry))
}

// RegisterRoutesOnGroup registers health check routes on a router group
func (shc *ServiceHealthChecks) RegisterRoutesOnGroup(group *gin.RouterGroup) {
	RegisterHealthCheckRoutesOnGroup(group, NewHealthCheckHandler(shc.registry))
}

// InitializeTracingProvider initializes the global tracing provider
func InitializeTracingProvider(serviceName, version, environment, jaegerEndpoint string, enabled bool) error {
	config := TracingConfig{
		ServiceName:    serviceName,
		Version:        version,
		Environment:    environment,
		JaegerEndpoint: jaegerEndpoint,
		Enabled:        enabled,
	}

	tp, err := NewTracingProvider(config)
	if err != nil {
		return err
	}

	GlobalTracingProvider = tp
	return nil
}

// ShutdownTracingProvider shuts down the global tracing provider
func ShutdownTracingProvider(ctx context.Context) error {
	if GlobalTracingProvider == nil {
		return nil
	}
	return GlobalTracingProvider.Shutdown(ctx)
}

// TracingMiddleware creates a Gin middleware for tracing HTTP requests
func TracingMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		ctx := c.Request.Context()
		_, span := StartGlobalSpan(ctx, "http-request", &SpanOptions{
			Attributes: map[string]interface{}{
				"method": c.Request.Method,
				"path":   c.Request.URL.Path,
				"remote": c.ClientIP(),
			},
		})

		c.Request = c.Request.WithContext(ctx)
		c.Next()

		if c.Writer.Status() >= 400 {
			span.SetAttributes(
				attribute.Bool("error", true),
				attribute.Int("status", c.Writer.Status()),
			)
		}

		EndGlobalSpan(span, nil)
	}
}

// NewDefaultRegistry creates a health check registry with common checks
func NewDefaultRegistry() *HealthCheckRegistry {
	return NewHealthCheckRegistry()
}
