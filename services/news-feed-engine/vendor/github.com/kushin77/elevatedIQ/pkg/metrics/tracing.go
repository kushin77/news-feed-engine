package metrics

import (
	"context"
	"fmt"
	"sync"
	"time"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/codes"
	"go.opentelemetry.io/otel/sdk/resource"
	tracesdk "go.opentelemetry.io/otel/sdk/trace"
	"go.opentelemetry.io/otel/trace"
)

// TracingConfig holds tracing configuration
type TracingConfig struct {
	ServiceName    string
	Version        string
	Environment    string
	JaegerEndpoint string
	Enabled        bool
	SampleRate     float64
}

// TracingProvider manages OpenTelemetry tracing
type TracingProvider struct {
	tracer   trace.Tracer
	shutdown func(ctx context.Context) error
	mu       sync.RWMutex
}

// NewTracingProvider creates a new tracing provider
// Note: For production use with Jaeger, implement the exporter separately
func NewTracingProvider(config TracingConfig) (*TracingProvider, error) {
	if !config.Enabled {
		return &TracingProvider{
			tracer: otel.Tracer("disabled"),
		}, nil
	}

	// Create resource
	res, err := resource.New(context.Background(),
		resource.WithAttributes(
			attribute.String("service.name", config.ServiceName),
			attribute.String("service.version", config.Version),
			attribute.String("deployment.environment", config.Environment),
		),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create resource: %w", err)
	}

	// Create trace provider with no-op exporter for testing
	// In production, add a Jaeger exporter via go.opentelemetry.io/otel/exporters/jaeger
	tp := tracesdk.NewTracerProvider(
		tracesdk.WithResource(res),
	)

	otel.SetTracerProvider(tp)

	return &TracingProvider{
		tracer: tp.Tracer(config.ServiceName),
		shutdown: func(ctx context.Context) error {
			return tp.Shutdown(ctx)
		},
	}, nil
}

// Shutdown shuts down the tracing provider
func (tp *TracingProvider) Shutdown(ctx context.Context) error {
	tp.mu.Lock()
	defer tp.mu.Unlock()

	if tp.shutdown != nil {
		return tp.shutdown(ctx)
	}

	return nil
}

// SpanOptions holds options for creating a span
type SpanOptions struct {
	Attributes  map[string]interface{}
	StartTime   time.Time
	RecordError bool
}

// StartSpan starts a new span
func (tp *TracingProvider) StartSpan(ctx context.Context, name string, opts *SpanOptions) (context.Context, trace.Span) {
	tp.mu.RLock()
	defer tp.mu.RUnlock()

	if opts == nil {
		opts = &SpanOptions{}
	}

	spanOpts := []trace.SpanStartOption{}

	if !opts.StartTime.IsZero() {
		spanOpts = append(spanOpts, trace.WithTimestamp(opts.StartTime))
	}

	ctx, span := tp.tracer.Start(ctx, name, spanOpts...)

	if opts.Attributes != nil {
		for k, v := range opts.Attributes {
			span.SetAttributes(attribute.String(k, fmt.Sprintf("%v", v)))
		}
	}

	return ctx, span
}

// EndSpan ends a span
func (tp *TracingProvider) EndSpan(span trace.Span, err error) {
	if err != nil {
		span.RecordError(err)
		span.SetStatus(codes.Error, err.Error())
	}
	span.End()
}

// TraceOperation traces an operation with automatic span management
func (tp *TracingProvider) TraceOperation(ctx context.Context, name string, fn func(ctx context.Context) error) error {
	_, span := tp.StartSpan(ctx, name, nil)
	defer tp.EndSpan(span, nil)

	err := fn(ctx)
	if err != nil {
		tp.EndSpan(span, err)
	}

	return err
}

// TraceOperationWithValue traces an operation and returns a value
func (tp *TracingProvider) TraceOperationWithValue(ctx context.Context, name string, fn func(ctx context.Context) (interface{}, error)) (interface{}, error) {
	_, span := tp.StartSpan(ctx, name, nil)
	defer span.End()

	result, err := fn(ctx)
	if err != nil {
		span.RecordError(err)
		span.SetStatus(codes.Error, err.Error())
	}

	return result, err
}

// SpanContext represents span context information
type SpanContext struct {
	TraceID    string
	SpanID     string
	TraceFlags string
}

// ExtractSpanContext extracts span context from trace span
func ExtractSpanContext(span trace.Span) *SpanContext {
	sc := span.SpanContext()
	return &SpanContext{
		TraceID:    sc.TraceID().String(),
		SpanID:     sc.SpanID().String(),
		TraceFlags: sc.TraceFlags().String(),
	}
}

// InjectSpanContext injects span context into a context
func InjectSpanContext(ctx context.Context, spanCtx *SpanContext) context.Context {
	// This is typically handled by OpenTelemetry's context propagation
	return ctx
}

// GlobalTracingProvider is the default tracing provider
var (
	GlobalTracingProvider *TracingProvider
	globalTracingMu       sync.RWMutex
)

// InitGlobalTracingProvider initializes the global tracing provider
func InitGlobalTracingProvider(config TracingConfig) error {
	globalTracingMu.Lock()
	defer globalTracingMu.Unlock()

	tp, err := NewTracingProvider(config)
	if err != nil {
		return err
	}

	GlobalTracingProvider = tp
	return nil
}

// GetGlobalTracingProvider returns the global tracing provider
func GetGlobalTracingProvider() *TracingProvider {
	globalTracingMu.RLock()
	defer globalTracingMu.RUnlock()

	return GlobalTracingProvider
}

// StartGlobalSpan starts a span using the global tracing provider
func StartGlobalSpan(ctx context.Context, name string, opts *SpanOptions) (context.Context, trace.Span) {
	tp := GetGlobalTracingProvider()
	if tp == nil {
		return ctx, trace.SpanFromContext(ctx)
	}

	return tp.StartSpan(ctx, name, opts)
}

// EndGlobalSpan ends a span using the global tracing provider
func EndGlobalSpan(span trace.Span, err error) {
	tp := GetGlobalTracingProvider()
	if tp == nil {
		return
	}

	tp.EndSpan(span, err)
}

// TraceGlobalOperation traces an operation using the global tracing provider
func TraceGlobalOperation(ctx context.Context, name string, fn func(ctx context.Context) error) error {
	tp := GetGlobalTracingProvider()
	if tp == nil {
		return fn(ctx)
	}

	return tp.TraceOperation(ctx, name, fn)
}

// TraceGlobalOperationWithValue traces an operation and returns a value using the global tracing provider
func TraceGlobalOperationWithValue(ctx context.Context, name string, fn func(ctx context.Context) (interface{}, error)) (interface{}, error) {
	tp := GetGlobalTracingProvider()
	if tp == nil {
		return fn(ctx)
	}

	return tp.TraceOperationWithValue(ctx, name, fn)
}
