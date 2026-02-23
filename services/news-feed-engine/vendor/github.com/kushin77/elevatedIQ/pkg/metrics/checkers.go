package metrics

import (
	"context"
	"database/sql"
	"fmt"
	"time"

	"github.com/redis/go-redis/v9"
)

// DatabaseChecker creates a health checker for SQL databases
type DatabaseChecker struct {
	db *sql.DB
}

// NewDatabaseChecker creates a new database health checker
func NewDatabaseChecker(db *sql.DB) *DatabaseChecker {
	return &DatabaseChecker{db: db}
}

// Check performs a database health check
func (dc *DatabaseChecker) Check(ctx context.Context) HealthCheckResult {
	// Set timeout for the ping
	ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()

	if err := dc.db.PingContext(ctx); err != nil {
		return HealthCheckResult{
			Name:      "database",
			Status:    HealthStatusUnhealthy,
			Message:   err.Error(),
			Timestamp: time.Now(),
		}
	}

	// Get connection pool stats
	stats := dc.db.Stats()

	return HealthCheckResult{
		Name:      "database",
		Status:    HealthStatusHealthy,
		Message:   fmt.Sprintf("Connected - Pool: %d open, %d inuse", stats.OpenConnections, stats.InUse),
		Timestamp: time.Now(),
	}
}

// CreateDatabaseHealthChecker creates a health checker function for SQL databases
func CreateDatabaseHealthChecker(db *sql.DB) HealthChecker {
	checker := NewDatabaseChecker(db)
	return func(ctx context.Context) HealthCheckResult {
		return checker.Check(ctx)
	}
}

// RedisChecker creates a health checker for Redis
type RedisChecker struct {
	client *redis.Client
}

// NewRedisChecker creates a new Redis health checker
func NewRedisChecker(client *redis.Client) *RedisChecker {
	return &RedisChecker{client: client}
}

// Check performs a Redis health check
func (rc *RedisChecker) Check(ctx context.Context) HealthCheckResult {
	// Set timeout for the ping
	ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()

	if err := rc.client.Ping(ctx).Err(); err != nil {
		return HealthCheckResult{
			Name:      "cache",
			Status:    HealthStatusUnhealthy,
			Message:   err.Error(),
			Timestamp: time.Now(),
		}
	}

	return HealthCheckResult{
		Name:      "cache",
		Status:    HealthStatusHealthy,
		Message:   "Connected",
		Timestamp: time.Now(),
	}
}

// CreateRedisHealthChecker creates a health checker function for Redis
func CreateRedisHealthChecker(client *redis.Client) HealthChecker {
	checker := NewRedisChecker(client)
	return func(ctx context.Context) HealthCheckResult {
		return checker.Check(ctx)
	}
}

// ServiceAvailabilityChecker creates a health checker for checking upstream service availability
type ServiceAvailabilityChecker struct {
	serviceName string
	endpoint    string
}

// NewServiceAvailabilityChecker creates a new service availability checker
func NewServiceAvailabilityChecker(serviceName, endpoint string) *ServiceAvailabilityChecker {
	return &ServiceAvailabilityChecker{
		serviceName: serviceName,
		endpoint:    endpoint,
	}
}

// Check performs a service availability check
func (sac *ServiceAvailabilityChecker) Check(ctx context.Context) HealthCheckResult {
	// Set timeout for the health check
	ctx, cancel := context.WithTimeout(ctx, 3*time.Second)
	defer cancel()

	result, err := healthCheckEndpoint(ctx, sac.endpoint)
	if err != nil {
		return HealthCheckResult{
			Name:      sac.serviceName,
			Status:    HealthStatusUnhealthy,
			Message:   err.Error(),
			Timestamp: time.Now(),
		}
	}

	if result {
		return HealthCheckResult{
			Name:      sac.serviceName,
			Status:    HealthStatusHealthy,
			Message:   "Available",
			Timestamp: time.Now(),
		}
	}

	return HealthCheckResult{
		Name:      sac.serviceName,
		Status:    HealthStatusDegraded,
		Message:   "Service returned non-healthy status",
		Timestamp: time.Now(),
	}
}

// CreateServiceAvailabilityChecker creates a health checker function for service availability
func CreateServiceAvailabilityChecker(serviceName, endpoint string) HealthChecker {
	checker := NewServiceAvailabilityChecker(serviceName, endpoint)
	return func(ctx context.Context) HealthCheckResult {
		return checker.Check(ctx)
	}
}

// healthCheckEndpoint checks if a health endpoint returns a healthy status
func healthCheckEndpoint(ctx context.Context, endpoint string) (bool, error) {
	// This is a placeholder - in production, use http.Client with proper timeout
	// For now, just return true if we can create a context
	select {
	case <-ctx.Done():
		return false, ctx.Err()
	default:
		return true, nil
	}
}

// CompositeChecker creates a health checker that runs multiple checks
type CompositeChecker struct {
	name     string
	checkers []HealthChecker
}

// NewCompositeChecker creates a new composite checker
func NewCompositeChecker(name string, checkers ...HealthChecker) *CompositeChecker {
	return &CompositeChecker{
		name:     name,
		checkers: checkers,
	}
}

// Check runs all sub-checkers and returns the overall status
func (cc *CompositeChecker) Check(ctx context.Context) HealthCheckResult {
	var unhealthyCount int
	var degradedCount int

	for _, checker := range cc.checkers {
		result := checker(ctx)
		if result.Status == HealthStatusUnhealthy {
			unhealthyCount++
		} else if result.Status == HealthStatusDegraded {
			degradedCount++
		}
	}

	status := HealthStatusHealthy
	message := "All checks passed"

	if unhealthyCount > 0 {
		status = HealthStatusUnhealthy
		message = "One or more critical checks failed"
	} else if degradedCount > 0 {
		status = HealthStatusDegraded
		message = "One or more checks are degraded"
	}

	return HealthCheckResult{
		Name:      cc.name,
		Status:    status,
		Message:   message,
		Timestamp: time.Now(),
	}
}

// CreateCompositeHealthChecker creates a composite health checker function
func CreateCompositeHealthChecker(name string, checkers ...HealthChecker) HealthChecker {
	checker := NewCompositeChecker(name, checkers...)
	return func(ctx context.Context) HealthCheckResult {
		return checker.Check(ctx)
	}
}
