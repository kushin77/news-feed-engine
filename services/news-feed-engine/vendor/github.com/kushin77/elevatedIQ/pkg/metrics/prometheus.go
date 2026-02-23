package metrics

import (
	"fmt"
	"strings"
	"time"
)

// PrometheusExporter converts metrics to Prometheus format
type PrometheusExporter struct {
	registry  *MetricsRegistry
	namespace string
	subsystem string
}

// NewPrometheusExporter creates a new Prometheus exporter
func NewPrometheusExporter(registry *MetricsRegistry, namespace, subsystem string) *PrometheusExporter {
	if registry == nil {
		registry = GlobalRegistry
	}
	return &PrometheusExporter{
		registry:  registry,
		namespace: namespace,
		subsystem: subsystem,
	}
}

// sanitizeMetricName sanitizes a metric name for Prometheus
func (pe *PrometheusExporter) sanitizeMetricName(name string) string {
	// Replace invalid characters with underscores
	replacer := strings.NewReplacer(
		" ", "_",
		"-", "_",
		".", "_",
		":", "_",
	)
	return replacer.Replace(name)
}

// buildFullMetricName builds the full metric name with namespace and subsystem
func (pe *PrometheusExporter) buildFullMetricName(name, suffix string) string {
	parts := []string{}

	if pe.namespace != "" {
		parts = append(parts, pe.namespace)
	}
	if pe.subsystem != "" {
		parts = append(parts, pe.subsystem)
	}

	parts = append(parts, pe.sanitizeMetricName(name))

	if suffix != "" {
		parts = append(parts, suffix)
	}

	return strings.Join(parts, "_")
}

// formatLabels formats labels in Prometheus format
func (pe *PrometheusExporter) formatLabels(labels map[string]string) string {
	if len(labels) == 0 {
		return ""
	}

	parts := []string{}
	for k, v := range labels {
		parts = append(parts, fmt.Sprintf(`%s="%s"`, k, v))
	}

	return "{" + strings.Join(parts, ",") + "}"
}

// ExportMetrics exports all metrics in Prometheus format
func (pe *PrometheusExporter) ExportMetrics() string {
	snapshot := pe.registry.Snapshot()
	output := strings.Builder{}

	// Export counters
	output.WriteString("# HELP counters Counters (total increments)\n")
	output.WriteString("# TYPE counters counter\n")
	for name, value := range snapshot.Counters {
		fullName := pe.buildFullMetricName(name, "total")
		output.WriteString(fmt.Sprintf("%s %d %d\n", fullName, value, snapshot.Timestamp.UnixMilli()))
	}

	output.WriteString("\n")

	// Export gauges
	output.WriteString("# HELP gauges Gauges (can go up or down)\n")
	output.WriteString("# TYPE gauges gauge\n")
	for name, value := range snapshot.Gauges {
		fullName := pe.buildFullMetricName(name, "")
		output.WriteString(fmt.Sprintf("%s %d %d\n", fullName, value, snapshot.Timestamp.UnixMilli()))
	}

	output.WriteString("\n")

	// Export histograms
	output.WriteString("# HELP histograms Histograms\n")
	output.WriteString("# TYPE histograms histogram\n")
	for name, hist := range snapshot.Histograms {
		fullName := pe.buildFullMetricName(name, "")
		output.WriteString(fmt.Sprintf("%s_count %d %d\n", fullName, hist.Count, snapshot.Timestamp.UnixMilli()))
		output.WriteString(fmt.Sprintf("%s_sum %d %d\n", fullName, hist.Sum, snapshot.Timestamp.UnixMilli()))
		output.WriteString(fmt.Sprintf("%s_min %d %d\n", fullName, hist.Min, snapshot.Timestamp.UnixMilli()))
		output.WriteString(fmt.Sprintf("%s_max %d %d\n", fullName, hist.Max, snapshot.Timestamp.UnixMilli()))
	}

	output.WriteString("\n")

	// Export timers
	output.WriteString("# HELP timers Timers (duration measurements)\n")
	output.WriteString("# TYPE timers histogram\n")
	for name, timer := range snapshot.Timers {
		fullName := pe.buildFullMetricName(name, "")
		output.WriteString(fmt.Sprintf("%s_count %d %d\n", fullName, timer.Count, snapshot.Timestamp.UnixMilli()))
		output.WriteString(fmt.Sprintf("%s_mean %f %d\n", fullName, timer.Mean, snapshot.Timestamp.UnixMilli()))
		output.WriteString(fmt.Sprintf("%s_min %d %d\n", fullName, timer.Min, snapshot.Timestamp.UnixMilli()))
		output.WriteString(fmt.Sprintf("%s_max %d %d\n", fullName, timer.Max, snapshot.Timestamp.UnixMilli()))
	}

	return output.String()
}

// ExportMetricsText exports metrics in simple text format
func (pe *PrometheusExporter) ExportMetricsText() string {
	snapshot := pe.registry.Snapshot()
	output := strings.Builder{}

	output.WriteString("=== METRICS SNAPSHOT ===\n")
	output.WriteString(fmt.Sprintf("Timestamp: %s\n\n", snapshot.Timestamp.Format(time.RFC3339)))

	output.WriteString("COUNTERS:\n")
	for name, value := range snapshot.Counters {
		output.WriteString(fmt.Sprintf("  %s: %d\n", name, value))
	}

	output.WriteString("\nGAUGES:\n")
	for name, value := range snapshot.Gauges {
		output.WriteString(fmt.Sprintf("  %s: %d\n", name, value))
	}

	output.WriteString("\nHISTOGRAMS:\n")
	for name, hist := range snapshot.Histograms {
		output.WriteString(fmt.Sprintf("  %s:\n", name))
		output.WriteString(fmt.Sprintf("    count: %d, sum: %d, min: %d, max: %d, mean: %.2f\n",
			hist.Count, hist.Sum, hist.Min, hist.Max, hist.Mean))
	}

	output.WriteString("\nTIMERS:\n")
	for name, timer := range snapshot.Timers {
		output.WriteString(fmt.Sprintf("  %s:\n", name))
		output.WriteString(fmt.Sprintf("    count: %d, mean: %.2fms, min: %dms, max: %dms\n",
			timer.Count, timer.Mean, timer.Min, timer.Max))
	}

	return output.String()
}

// ExportMetricsJSON exports metrics in JSON format
func (pe *PrometheusExporter) ExportMetricsJSON() string {
	snapshot := pe.registry.Snapshot()
	output := strings.Builder{}

	output.WriteString("{\n")
	output.WriteString(fmt.Sprintf(`  "timestamp": "%s",`, snapshot.Timestamp.Format(time.RFC3339)))
	output.WriteString("\n")

	output.WriteString(`  "counters": {`)
	first := true
	for name, value := range snapshot.Counters {
		if !first {
			output.WriteString(",")
		}
		output.WriteString(fmt.Sprintf(`"%s": %d`, name, value))
		first = false
	}
	output.WriteString("},\n")

	output.WriteString(`  "gauges": {`)
	first = true
	for name, value := range snapshot.Gauges {
		if !first {
			output.WriteString(",")
		}
		output.WriteString(fmt.Sprintf(`"%s": %d`, name, value))
		first = false
	}
	output.WriteString("},\n")

	output.WriteString(`  "histograms": {`)
	first = true
	for name, hist := range snapshot.Histograms {
		if !first {
			output.WriteString(",")
		}
		output.WriteString(fmt.Sprintf(`"%s": {"count": %d, "sum": %d, "min": %d, "max": %d, "mean": %.2f}`,
			name, hist.Count, hist.Sum, hist.Min, hist.Max, hist.Mean))
		first = false
	}
	output.WriteString("}\n")

	output.WriteString("}\n")

	return output.String()
}
