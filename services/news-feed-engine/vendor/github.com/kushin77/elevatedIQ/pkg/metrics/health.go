package metrics

import (
	"context"
	"fmt"
	"sync"
	"time"
)

// HealthStatus represents the status of a health check
type HealthStatus string

const (
	HealthStatusHealthy   HealthStatus = "healthy"
	HealthStatusUnhealthy HealthStatus = "unhealthy"
	HealthStatusDegraded  HealthStatus = "degraded"
)

// HealthCheckResult represents the result of a health check
type HealthCheckResult struct {
	Name      string
	Status    HealthStatus
	Message   string
	Timestamp time.Time
	Duration  time.Duration
}

// HealthChecker is a function that performs a health check
type HealthChecker func(ctx context.Context) HealthCheckResult

// HealthCheckRegistry manages multiple health checks
type HealthCheckRegistry struct {
	checks map[string]HealthChecker
	mu     sync.RWMutex
}

// NewHealthCheckRegistry creates a new health check registry
func NewHealthCheckRegistry() *HealthCheckRegistry {
	return &HealthCheckRegistry{
		checks: make(map[string]HealthChecker),
	}
}

// Register registers a new health check
func (hcr *HealthCheckRegistry) Register(name string, checker HealthChecker) error {
	if name == "" {
		return fmt.Errorf("health check name cannot be empty")
	}

	if checker == nil {
		return fmt.Errorf("health checker cannot be nil")
	}

	hcr.mu.Lock()
	defer hcr.mu.Unlock()

	hcr.checks[name] = checker
	return nil
}

// Unregister removes a health check
func (hcr *HealthCheckRegistry) Unregister(name string) error {
	hcr.mu.Lock()
	defer hcr.mu.Unlock()

	if _, exists := hcr.checks[name]; !exists {
		return fmt.Errorf("health check %q not found", name)
	}

	delete(hcr.checks, name)
	return nil
}

// CheckAll runs all registered health checks
func (hcr *HealthCheckRegistry) CheckAll(ctx context.Context) map[string]HealthCheckResult {
	hcr.mu.RLock()
	checks := make(map[string]HealthChecker)
	for name, checker := range hcr.checks {
		checks[name] = checker
	}
	hcr.mu.RUnlock()

	results := make(map[string]HealthCheckResult)
	for name, checker := range checks {
		start := time.Now()
		result := checker(ctx)
		result.Duration = time.Since(start)
		results[name] = result
	}

	return results
}

// CheckOne runs a specific health check
func (hcr *HealthCheckRegistry) CheckOne(ctx context.Context, name string) (HealthCheckResult, error) {
	hcr.mu.RLock()
	checker, exists := hcr.checks[name]
	hcr.mu.RUnlock()

	if !exists {
		return HealthCheckResult{}, fmt.Errorf("health check %q not found", name)
	}

	start := time.Now()
	result := checker(ctx)
	result.Duration = time.Since(start)
	return result, nil
}

// OverallStatus determines the overall health status from all checks
func (hcr *HealthCheckRegistry) OverallStatus(ctx context.Context) HealthStatus {
	results := hcr.CheckAll(ctx)

	if len(results) == 0 {
		return HealthStatusHealthy
	}

	hasUnhealthy := false
	hasDegraded := false

	for _, result := range results {
		if result.Status == HealthStatusUnhealthy {
			hasUnhealthy = true
		}
		if result.Status == HealthStatusDegraded {
			hasDegraded = true
		}
	}

	if hasUnhealthy {
		return HealthStatusUnhealthy
	}

	if hasDegraded {
		return HealthStatusDegraded
	}

	return HealthStatusHealthy
}

// HealthReport represents a complete health check report
type HealthReport struct {
	Status      HealthStatus
	Timestamp   time.Time
	Checks      map[string]HealthCheckResult
	Description string
}

// GenerateHealthReport generates a comprehensive health report
func (hcr *HealthCheckRegistry) GenerateHealthReport(ctx context.Context) *HealthReport {
	results := hcr.CheckAll(ctx)
	status := hcr.OverallStatus(ctx)

	return &HealthReport{
		Status:    status,
		Timestamp: time.Now(),
		Checks:    results,
	}
}

// ReadinessChecker checks if the service is ready to receive traffic
type ReadinessChecker struct {
	readyFunc func(ctx context.Context) bool
	mu        sync.RWMutex
}

// NewReadinessChecker creates a new readiness checker
func NewReadinessChecker(readyFunc func(ctx context.Context) bool) *ReadinessChecker {
	return &ReadinessChecker{
		readyFunc: readyFunc,
	}
}

// IsReady checks if the service is ready
func (rc *ReadinessChecker) IsReady(ctx context.Context) bool {
	rc.mu.RLock()
	defer rc.mu.RUnlock()

	if rc.readyFunc == nil {
		return true
	}

	return rc.readyFunc(ctx)
}

// SetReadyFunc sets the readiness function
func (rc *ReadinessChecker) SetReadyFunc(readyFunc func(ctx context.Context) bool) {
	rc.mu.Lock()
	defer rc.mu.Unlock()

	rc.readyFunc = readyFunc
}

// LivenessChecker checks if the service is alive/functioning
type LivenessChecker struct {
	aliveFunc func(ctx context.Context) bool
	mu        sync.RWMutex
}

// NewLivenessChecker creates a new liveness checker
func NewLivenessChecker(aliveFunc func(ctx context.Context) bool) *LivenessChecker {
	return &LivenessChecker{
		aliveFunc: aliveFunc,
	}
}

// IsAlive checks if the service is alive
func (lc *LivenessChecker) IsAlive(ctx context.Context) bool {
	lc.mu.RLock()
	defer lc.mu.RUnlock()

	if lc.aliveFunc == nil {
		return true
	}

	return lc.aliveFunc(ctx)
}

// SetAliveFunc sets the liveness function
func (lc *LivenessChecker) SetAliveFunc(aliveFunc func(ctx context.Context) bool) {
	lc.mu.Lock()
	defer lc.mu.Unlock()

	lc.aliveFunc = aliveFunc
}

// NewHealthyChecker creates a health checker that always returns healthy
func NewHealthyChecker(name string) HealthChecker {
	return func(ctx context.Context) HealthCheckResult {
		return HealthCheckResult{
			Name:      name,
			Status:    HealthStatusHealthy,
			Message:   "OK",
			Timestamp: time.Now(),
		}
	}
}

// NewErrorChecker creates a health checker that returns an error
func NewErrorChecker(name, message string) HealthChecker {
	return func(ctx context.Context) HealthCheckResult {
		return HealthCheckResult{
			Name:      name,
			Status:    HealthStatusUnhealthy,
			Message:   message,
			Timestamp: time.Now(),
		}
	}
}

// NewDegradedChecker creates a health checker that returns degraded status
func NewDegradedChecker(name, message string) HealthChecker {
	return func(ctx context.Context) HealthCheckResult {
		return HealthCheckResult{
			Name:      name,
			Status:    HealthStatusDegraded,
			Message:   message,
			Timestamp: time.Now(),
		}
	}
}

// NewTimeoutChecker creates a health checker with a timeout
func NewTimeoutChecker(name string, checker HealthChecker, timeout time.Duration) HealthChecker {
	return func(ctx context.Context) HealthCheckResult {
		ctx, cancel := context.WithTimeout(ctx, timeout)
		defer cancel()

		resultChan := make(chan HealthCheckResult, 1)
		go func() {
			resultChan <- checker(ctx)
		}()

		select {
		case result := <-resultChan:
			return result
		case <-ctx.Done():
			return HealthCheckResult{
				Name:      name,
				Status:    HealthStatusUnhealthy,
				Message:   "Health check timeout",
				Timestamp: time.Now(),
			}
		}
	}
}

// GlobalHealthCheckRegistry is the default health check registry
var GlobalHealthCheckRegistry = NewHealthCheckRegistry()

// RegisterHealthCheck registers a health check in the global registry
func RegisterHealthCheck(name string, checker HealthChecker) error {
	return GlobalHealthCheckRegistry.Register(name, checker)
}

// CheckAllHealth runs all health checks in the global registry
func CheckAllHealth(ctx context.Context) map[string]HealthCheckResult {
	return GlobalHealthCheckRegistry.CheckAll(ctx)
}

// OverallHealth returns the overall health status from the global registry
func OverallHealth(ctx context.Context) HealthStatus {
	return GlobalHealthCheckRegistry.OverallStatus(ctx)
}
