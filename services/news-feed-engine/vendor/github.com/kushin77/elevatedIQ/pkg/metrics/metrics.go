package metrics

import (
	"context"
	"sync"
	"sync/atomic"
	"time"
)

// MetricType represents the type of metric being collected
type MetricType string

const (
	MetricTypeCounter   MetricType = "counter"
	MetricTypeGauge     MetricType = "gauge"
	MetricTypeHistogram MetricType = "histogram"
	MetricTypeSummary   MetricType = "summary"
	MetricTypeTimer     MetricType = "timer"
)

// MetricValue represents a single metric measurement
type MetricValue struct {
	Type      MetricType
	Name      string
	Value     float64
	Timestamp time.Time
	Labels    map[string]string
	Unit      string
}

// Counter represents a monotonically increasing metric
type Counter struct {
	name   string
	value  atomic.Int64
	labels map[string]string
	mu     sync.RWMutex
}

// NewCounter creates a new counter metric
func NewCounter(name string, labels map[string]string) *Counter {
	if labels == nil {
		labels = make(map[string]string)
	}
	return &Counter{
		name:   name,
		labels: labels,
	}
}

// Increment adds 1 to the counter
func (c *Counter) Increment() {
	c.value.Add(1)
}

// Add increments the counter by n
func (c *Counter) Add(n int64) {
	c.value.Add(n)
}

// Value returns the current counter value
func (c *Counter) Value() int64 {
	return c.value.Load()
}

// Reset resets the counter to 0
func (c *Counter) Reset() {
	c.value.Store(0)
}

// Gauge represents a metric that can go up or down
type Gauge struct {
	name   string
	value  atomic.Int64
	labels map[string]string
	mu     sync.RWMutex
}

// NewGauge creates a new gauge metric
func NewGauge(name string, labels map[string]string) *Gauge {
	if labels == nil {
		labels = make(map[string]string)
	}
	return &Gauge{
		name:   name,
		labels: labels,
	}
}

// Set sets the gauge to a specific value (as int64)
func (g *Gauge) Set(value int64) {
	g.value.Store(value)
}

// SetFloat sets the gauge to a float value (stored as int64 bits)
func (g *Gauge) SetFloat(value float64) {
	g.mu.Lock()
	defer g.mu.Unlock()
	// For simplicity, we convert to int64
	// In production, use a separate float field
	g.value.Store(int64(value))
}

// Increment increments the gauge by 1
func (g *Gauge) Increment() {
	g.value.Add(1)
}

// Decrement decrements the gauge by 1
func (g *Gauge) Decrement() {
	g.value.Add(-1)
}

// Value returns the current gauge value
func (g *Gauge) Value() int64 {
	return g.value.Load()
}

// Histogram represents the distribution of values
type Histogram struct {
	name    string
	values  []int64
	buckets []int64
	count   atomic.Int64
	sum     atomic.Int64
	min     atomic.Int64
	max     atomic.Int64
	labels  map[string]string
	mu      sync.RWMutex
}

// NewHistogram creates a new histogram with specified buckets
func NewHistogram(name string, buckets []int64, labels map[string]string) *Histogram {
	if labels == nil {
		labels = make(map[string]string)
	}
	if len(buckets) == 0 {
		buckets = []int64{1, 10, 100, 1000, 10000}
	}
	return &Histogram{
		name:    name,
		buckets: buckets,
		labels:  labels,
		min:     atomic.Int64{},
		max:     atomic.Int64{},
	}
}

// Observe records a new observation in the histogram
func (h *Histogram) Observe(value int64) {
	h.mu.Lock()
	h.values = append(h.values, value)
	h.mu.Unlock()

	h.count.Add(1)
	h.sum.Add(value)

	// Update min and max
	for {
		currentMin := h.min.Load()
		if currentMin == 0 || value < currentMin {
			if h.min.CompareAndSwap(currentMin, value) {
				break
			}
		} else {
			break
		}
	}

	for {
		currentMax := h.max.Load()
		if value > currentMax {
			if h.max.CompareAndSwap(currentMax, value) {
				break
			}
		} else {
			break
		}
	}
}

// Count returns the number of observations
func (h *Histogram) Count() int64 {
	return h.count.Load()
}

// Sum returns the sum of all observations
func (h *Histogram) Sum() int64 {
	return h.sum.Load()
}

// Mean returns the mean of observations
func (h *Histogram) Mean() float64 {
	count := h.Count()
	if count == 0 {
		return 0
	}
	return float64(h.Sum()) / float64(count)
}

// Min returns the minimum observed value
func (h *Histogram) Min() int64 {
	return h.min.Load()
}

// Max returns the maximum observed value
func (h *Histogram) Max() int64 {
	return h.max.Load()
}

// Timer measures elapsed time
type Timer struct {
	name      string
	histogram *Histogram
	labels    map[string]string
	startTime time.Time
	running   atomic.Bool
}

// NewTimer creates a new timer
func NewTimer(name string, labels map[string]string) *Timer {
	if labels == nil {
		labels = make(map[string]string)
	}
	return &Timer{
		name:      name,
		histogram: NewHistogram(name, nil, labels),
		labels:    labels,
	}
}

// Start starts the timer
func (t *Timer) Start() {
	t.startTime = time.Now()
	t.running.Store(true)
}

// Stop stops the timer and records the duration (in milliseconds)
func (t *Timer) Stop() time.Duration {
	if !t.running.Load() {
		return 0
	}

	duration := time.Since(t.startTime)
	t.histogram.Observe(duration.Milliseconds())
	t.running.Store(false)
	return duration
}

// Mean returns the mean duration in milliseconds
func (t *Timer) Mean() float64 {
	return t.histogram.Mean()
}

// Count returns the number of measurements
func (t *Timer) Count() int64 {
	return t.histogram.Count()
}

// Context returns a context with timer information
func (t *Timer) Context(ctx context.Context) context.Context {
	return context.WithValue(ctx, "timer", t)
}

// MetricsRegistry manages all metrics
type MetricsRegistry struct {
	counters   map[string]*Counter
	gauges     map[string]*Gauge
	histograms map[string]*Histogram
	timers     map[string]*Timer
	mu         sync.RWMutex
}

// NewMetricsRegistry creates a new metrics registry
func NewMetricsRegistry() *MetricsRegistry {
	return &MetricsRegistry{
		counters:   make(map[string]*Counter),
		gauges:     make(map[string]*Gauge),
		histograms: make(map[string]*Histogram),
		timers:     make(map[string]*Timer),
	}
}

// RegisterCounter registers a new counter
func (mr *MetricsRegistry) RegisterCounter(name string, labels map[string]string) *Counter {
	mr.mu.Lock()
	defer mr.mu.Unlock()

	if counter, exists := mr.counters[name]; exists {
		return counter
	}

	counter := NewCounter(name, labels)
	mr.counters[name] = counter
	return counter
}

// RegisterGauge registers a new gauge
func (mr *MetricsRegistry) RegisterGauge(name string, labels map[string]string) *Gauge {
	mr.mu.Lock()
	defer mr.mu.Unlock()

	if gauge, exists := mr.gauges[name]; exists {
		return gauge
	}

	gauge := NewGauge(name, labels)
	mr.gauges[name] = gauge
	return gauge
}

// RegisterHistogram registers a new histogram
func (mr *MetricsRegistry) RegisterHistogram(name string, buckets []int64, labels map[string]string) *Histogram {
	mr.mu.Lock()
	defer mr.mu.Unlock()

	if histogram, exists := mr.histograms[name]; exists {
		return histogram
	}

	histogram := NewHistogram(name, buckets, labels)
	mr.histograms[name] = histogram
	return histogram
}

// RegisterTimer registers a new timer
func (mr *MetricsRegistry) RegisterTimer(name string, labels map[string]string) *Timer {
	mr.mu.Lock()
	defer mr.mu.Unlock()

	if timer, exists := mr.timers[name]; exists {
		return timer
	}

	timer := NewTimer(name, labels)
	mr.timers[name] = timer
	return timer
}

// GetCounter retrieves a counter by name
func (mr *MetricsRegistry) GetCounter(name string) *Counter {
	mr.mu.RLock()
	defer mr.mu.RUnlock()
	return mr.counters[name]
}

// GetGauge retrieves a gauge by name
func (mr *MetricsRegistry) GetGauge(name string) *Gauge {
	mr.mu.RLock()
	defer mr.mu.RUnlock()
	return mr.gauges[name]
}

// GetHistogram retrieves a histogram by name
func (mr *MetricsRegistry) GetHistogram(name string) *Histogram {
	mr.mu.RLock()
	defer mr.mu.RUnlock()
	return mr.histograms[name]
}

// GetTimer retrieves a timer by name
func (mr *MetricsRegistry) GetTimer(name string) *Timer {
	mr.mu.RLock()
	defer mr.mu.RUnlock()
	return mr.timers[name]
}

// Snapshot returns a snapshot of all metrics at a point in time
type Snapshot struct {
	Timestamp  time.Time
	Counters   map[string]int64
	Gauges     map[string]int64
	Histograms map[string]HistogramSnapshot
	Timers     map[string]TimerSnapshot
}

// HistogramSnapshot represents a snapshot of histogram data
type HistogramSnapshot struct {
	Count int64
	Sum   int64
	Min   int64
	Max   int64
	Mean  float64
}

// TimerSnapshot represents a snapshot of timer data
type TimerSnapshot struct {
	Count int64
	Mean  float64
	Min   int64
	Max   int64
}

// Snapshot captures all current metric values
func (mr *MetricsRegistry) Snapshot() *Snapshot {
	mr.mu.RLock()
	defer mr.mu.RUnlock()

	snapshot := &Snapshot{
		Timestamp:  time.Now(),
		Counters:   make(map[string]int64),
		Gauges:     make(map[string]int64),
		Histograms: make(map[string]HistogramSnapshot),
		Timers:     make(map[string]TimerSnapshot),
	}

	for name, counter := range mr.counters {
		snapshot.Counters[name] = counter.Value()
	}

	for name, gauge := range mr.gauges {
		snapshot.Gauges[name] = gauge.Value()
	}

	for name, histogram := range mr.histograms {
		snapshot.Histograms[name] = HistogramSnapshot{
			Count: histogram.Count(),
			Sum:   histogram.Sum(),
			Min:   histogram.Min(),
			Max:   histogram.Max(),
			Mean:  histogram.Mean(),
		}
	}

	for name, timer := range mr.timers {
		snapshot.Timers[name] = TimerSnapshot{
			Count: timer.Count(),
			Mean:  timer.Mean(),
			Min:   timer.histogram.Min(),
			Max:   timer.histogram.Max(),
		}
	}

	return snapshot
}

// Reset resets all metrics
func (mr *MetricsRegistry) Reset() {
	mr.mu.Lock()
	defer mr.mu.Unlock()

	for _, counter := range mr.counters {
		counter.Reset()
	}

	mr.counters = make(map[string]*Counter)
	mr.gauges = make(map[string]*Gauge)
	mr.histograms = make(map[string]*Histogram)
	mr.timers = make(map[string]*Timer)
}

// MetricCount returns the total number of registered metrics
func (mr *MetricsRegistry) MetricCount() int {
	mr.mu.RLock()
	defer mr.mu.RUnlock()

	return len(mr.counters) + len(mr.gauges) + len(mr.histograms) + len(mr.timers)
}

// GlobalRegistry is the default metrics registry
var GlobalRegistry = NewMetricsRegistry()

// RegisterCounter registers a counter in the global registry
func RegisterCounter(name string, labels map[string]string) *Counter {
	return GlobalRegistry.RegisterCounter(name, labels)
}

// RegisterGauge registers a gauge in the global registry
func RegisterGauge(name string, labels map[string]string) *Gauge {
	return GlobalRegistry.RegisterGauge(name, labels)
}

// RegisterHistogram registers a histogram in the global registry
func RegisterHistogram(name string, buckets []int64, labels map[string]string) *Histogram {
	return GlobalRegistry.RegisterHistogram(name, buckets, labels)
}

// RegisterTimer registers a timer in the global registry
func RegisterTimer(name string, labels map[string]string) *Timer {
	return GlobalRegistry.RegisterTimer(name, labels)
}
