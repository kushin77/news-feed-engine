"""
Analytics Pipeline Module - Event Processing & Metrics

This module implements:
- Kafka event streaming for content pipeline events
- Prometheus metrics exporters
- Real-time analytics processing
- Performance tracking and alerting

Elite AI Implementation - Complete observability stack
"""

import asyncio
import hashlib
import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

try:
    from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False

try:
    from prometheus_client import CONTENT_TYPE_LATEST  # noqa: F401
    from prometheus_client import Info  # noqa: F401
    from prometheus_client import (
        CollectorRegistry,
        Counter,
        Gauge,
        Histogram,
        Summary,  # noqa: F401
        generate_latest,
        push_to_gateway,
        start_http_server,
    )

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

from .config import settings, utc_now

logger = logging.getLogger(__name__)


# ============================================================================
# Event Types
# ============================================================================


class EventType(str, Enum):
    """Pipeline event types"""

    # Content Events
    CONTENT_CREATED = "content.created"
    CONTENT_CURATED = "content.curated"
    CONTENT_REJECTED = "content.rejected"

    # Video Events
    SCRIPT_GENERATED = "video.script.generated"
    VOICE_SYNTHESIZED = "video.voice.synthesized"
    VIDEO_PRODUCED = "video.produced"
    VIDEO_FAILED = "video.failed"

    # Publishing Events
    PUBLISH_STARTED = "publish.started"
    PUBLISH_SUCCESS = "publish.success"
    PUBLISH_FAILED = "publish.failed"

    # Engagement Events
    VIEW = "engagement.view"
    LIKE = "engagement.like"
    COMMENT = "engagement.comment"
    SHARE = "engagement.share"

    # System Events
    AGENT_STARTED = "system.agent.started"
    AGENT_STOPPED = "system.agent.stopped"
    AGENT_ERROR = "system.agent.error"
    PIPELINE_HEALTH = "system.pipeline.health"


@dataclass
class PipelineEvent:
    """Event flowing through the analytics pipeline"""

    event_id: str
    event_type: EventType
    timestamp: datetime
    source: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "data": self.data,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PipelineEvent":
        return cls(
            event_id=data["event_id"],
            event_type=EventType(data["event_type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            source=data["source"],
            data=data["data"],
            metadata=data.get("metadata", {}),
        )


# ============================================================================
# Kafka Event Producer
# ============================================================================


class EventProducer:
    """
    Kafka-based event producer for pipeline events.
    Falls back to in-memory queue if Kafka unavailable.
    """

    def __init__(
        self, bootstrap_servers: Optional[str] = None, topic_prefix: str = "newsfeed"
    ):
        self.bootstrap_servers = bootstrap_servers or getattr(
            settings, "KAFKA_BOOTSTRAP_SERVERS", "127.0.0.1:9092"
        )
        self.topic_prefix = topic_prefix
        self._producer: Optional[Any] = None
        self._fallback_queue: asyncio.Queue = asyncio.Queue()
        self._started = False

    async def start(self):
        """Start the producer"""
        if self._started:
            return

        if KAFKA_AVAILABLE:
            try:
                self._producer = AIOKafkaProducer(
                    bootstrap_servers=self.bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                    key_serializer=lambda k: k.encode("utf-8") if k else None,
                    acks="all",
                    enable_idempotence=True,
                )
                await self._producer.start()
                self._started = True
                logger.info(f"Kafka producer started: {self.bootstrap_servers}")
            except Exception as e:
                logger.warning(f"Kafka unavailable, using fallback queue: {e}")
                self._started = True
        else:
            logger.info("Kafka not available, using in-memory fallback")
            self._started = True

    async def stop(self):
        """Stop the producer"""
        if self._producer:
            await self._producer.stop()
        self._started = False

    async def send_event(
        self, event: PipelineEvent, topic_suffix: Optional[str] = None
    ):
        """Send an event to Kafka or fallback queue"""
        if not self._started:
            await self.start()

        topic = f"{self.topic_prefix}.{topic_suffix or event.event_type.value.replace('.', '-')}"

        if self._producer:
            try:
                await self._producer.send_and_wait(
                    topic=topic, key=event.event_id, value=event.to_dict()
                )
                logger.debug(f"Event sent to Kafka: {event.event_type}")
            except Exception as e:
                logger.error(f"Kafka send error: {e}")
                await self._fallback_queue.put(event)
        else:
            await self._fallback_queue.put(event)

    async def send_batch(self, events: List[PipelineEvent]):
        """Send multiple events"""
        for event in events:
            await self.send_event(event)

    def create_event(
        self,
        event_type: EventType,
        source: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PipelineEvent:
        """Create a new event"""
        return PipelineEvent(
            event_id=hashlib.md5(
                f"{event_type.value}{utc_now().isoformat()}{source}".encode(),
                usedforsecurity=False,
            ).hexdigest()[:16],
            event_type=event_type,
            timestamp=utc_now(),
            source=source,
            data=data,
            metadata=metadata or {},
        )


# ============================================================================
# Kafka Event Consumer
# ============================================================================


class EventConsumer:
    """
    Kafka-based event consumer for processing pipeline events.
    """

    def __init__(
        self,
        bootstrap_servers: Optional[str] = None,
        group_id: str = "analytics-processor",
        topics: Optional[List[str]] = None,
    ):
        self.bootstrap_servers = bootstrap_servers or getattr(
            settings, "KAFKA_BOOTSTRAP_SERVERS", "elevatediq-kafka:9092"
        )
        self.group_id = group_id
        self.topics = topics or ["newsfeed.*"]
        self._consumer: Optional[Any] = None
        self._handlers: Dict[EventType, List[Callable]] = defaultdict(list)
        self._running = False

    def register_handler(self, event_type: EventType, handler: Callable):
        """Register an event handler"""
        self._handlers[event_type].append(handler)

    async def start(self):
        """Start consuming events"""
        if KAFKA_AVAILABLE:
            try:
                self._consumer = AIOKafkaConsumer(
                    *self.topics,
                    bootstrap_servers=self.bootstrap_servers,
                    group_id=self.group_id,
                    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                    auto_offset_reset="latest",
                    enable_auto_commit=True,
                )
                await self._consumer.start()
                logger.info(f"Kafka consumer started: {self.group_id}")
            except Exception as e:
                logger.error(f"Kafka consumer start error: {e}")
                return
        else:
            logger.warning("Kafka not available for consumer")
            return

        self._running = True

        try:
            async for msg in self._consumer:
                if not self._running:
                    break

                try:
                    event = PipelineEvent.from_dict(msg.value)
                    await self._dispatch_event(event)
                except Exception as e:
                    logger.error(f"Event processing error: {e}")
        finally:
            await self._consumer.stop()

    async def stop(self):
        """Stop the consumer"""
        self._running = False

    async def _dispatch_event(self, event: PipelineEvent):
        """Dispatch event to registered handlers"""
        handlers = self._handlers.get(event.event_type, [])

        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Handler error for {event.event_type}: {e}")


# ============================================================================
# Prometheus Metrics
# ============================================================================


class MetricsExporter:
    """
    Prometheus metrics exporter for pipeline observability.
    """

    def __init__(self, namespace: str = "newsfeed"):
        self.namespace = namespace
        self.registry = CollectorRegistry() if PROMETHEUS_AVAILABLE else None

        if PROMETHEUS_AVAILABLE:
            self._init_metrics()

    def _init_metrics(self):
        """Initialize Prometheus metrics"""
        # Content Metrics
        self.content_created = Counter(
            f"{self.namespace}_content_created_total",
            "Total content items created",
            ["category", "source"],
            registry=self.registry,
        )

        self.content_curated = Counter(
            f"{self.namespace}_content_curated_total",
            "Total content items curated",
            ["category", "approved"],
            registry=self.registry,
        )

        self.curation_score = Histogram(
            f"{self.namespace}_curation_score",
            "Content curation scores",
            ["category"],
            buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
            registry=self.registry,
        )

        # Video Production Metrics
        self.videos_produced = Counter(
            f"{self.namespace}_videos_produced_total",
            "Total videos produced",
            ["status"],
            registry=self.registry,
        )

        self.video_production_duration = Histogram(
            f"{self.namespace}_video_production_seconds",
            "Video production duration in seconds",
            [],
            buckets=(10, 30, 60, 120, 300, 600, 1200),
            registry=self.registry,
        )

        self.script_length = Histogram(
            f"{self.namespace}_script_length_chars",
            "Script length in characters",
            [],
            buckets=(100, 250, 500, 750, 1000, 1500, 2000),
            registry=self.registry,
        )

        # Publishing Metrics
        self.publish_attempts = Counter(
            f"{self.namespace}_publish_attempts_total",
            "Total publish attempts",
            ["platform", "status"],
            registry=self.registry,
        )

        self.publish_latency = Histogram(
            f"{self.namespace}_publish_latency_seconds",
            "Publishing latency per platform",
            ["platform"],
            buckets=(0.5, 1, 2, 5, 10, 30, 60),
            registry=self.registry,
        )

        # Engagement Metrics
        self.engagement_events = Counter(
            f"{self.namespace}_engagement_events_total",
            "Total engagement events",
            ["platform", "event_type"],
            registry=self.registry,
        )

        self.engagement_rate = Gauge(
            f"{self.namespace}_engagement_rate",
            "Current engagement rate",
            ["platform", "content_id"],
            registry=self.registry,
        )

        # Trend Metrics
        self.trends_tracked = Gauge(
            f"{self.namespace}_trends_tracked",
            "Number of trends being tracked",
            ["source"],
            registry=self.registry,
        )

        self.trend_score = Gauge(
            f"{self.namespace}_trend_score",
            "Current trend score",
            ["trend_name", "source"],
            registry=self.registry,
        )

        # Agent Metrics
        self.agent_state = Gauge(
            f"{self.namespace}_agent_state",
            "Agent operational state (1=active, 0=inactive)",
            ["agent_name"],
            registry=self.registry,
        )

        self.agent_decisions = Counter(
            f"{self.namespace}_agent_decisions_total",
            "Total agent decisions",
            ["agent_name", "decision_type"],
            registry=self.registry,
        )

        self.agent_decision_confidence = Histogram(
            f"{self.namespace}_agent_decision_confidence",
            "Agent decision confidence scores",
            ["agent_name"],
            buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
            registry=self.registry,
        )

        # System Metrics
        self.pipeline_health = Gauge(
            f"{self.namespace}_pipeline_health",
            "Pipeline health score (0-1)",
            [],
            registry=self.registry,
        )

        self.queue_depth = Gauge(
            f"{self.namespace}_queue_depth",
            "Current queue depth",
            ["queue_name"],
            registry=self.registry,
        )

        self.processing_errors = Counter(
            f"{self.namespace}_processing_errors_total",
            "Total processing errors",
            ["component", "error_type"],
            registry=self.registry,
        )

        # Info metric
        self.info = Info(
            f"{self.namespace}_info",
            "Information about the news feed engine",
            registry=self.registry,
        )
        self.info.info(
            {
                "version": "2.0.0",
                "ai_model": "claude-3-opus",
                "environment": getattr(settings, "ENVIRONMENT", "development"),
            }
        )

    # Metric Recording Methods
    def record_content_created(self, category: str, source: str):
        if self.content_created:
            self.content_created.labels(category=category, source=source).inc()

    def record_content_curated(self, category: str, approved: bool, score: float):
        if self.content_curated:
            self.content_curated.labels(category=category, approved=str(approved)).inc()
        if self.curation_score:
            self.curation_score.labels(category=category).observe(score)

    def record_video_produced(
        self, success: bool, duration_seconds: float, script_length: int
    ):
        if self.videos_produced:
            self.videos_produced.labels(status="success" if success else "failed").inc()
        if self.video_production_duration and success:
            self.video_production_duration.observe(duration_seconds)
        if self.script_length:
            self.script_length.observe(script_length)

    def record_publish(self, platform: str, success: bool, latency_seconds: float):
        if self.publish_attempts:
            self.publish_attempts.labels(
                platform=platform, status="success" if success else "failed"
            ).inc()
        if self.publish_latency and success:
            self.publish_latency.labels(platform=platform).observe(latency_seconds)

    def record_engagement(
        self, platform: str, event_type: str, content_id: str, rate: float
    ):
        if self.engagement_events:
            self.engagement_events.labels(
                platform=platform, event_type=event_type
            ).inc()
        if self.engagement_rate:
            self.engagement_rate.labels(platform=platform, content_id=content_id).set(
                rate
            )

    def record_trend(self, trend_name: str, source: str, score: float):
        if self.trend_score:
            self.trend_score.labels(trend_name=trend_name, source=source).set(score)

    def set_trends_tracked(self, source: str, count: int):
        if self.trends_tracked:
            self.trends_tracked.labels(source=source).set(count)

    def record_agent_decision(
        self, agent_name: str, decision_type: str, confidence: float
    ):
        if self.agent_decisions:
            self.agent_decisions.labels(
                agent_name=agent_name, decision_type=decision_type
            ).inc()
        if self.agent_decision_confidence:
            self.agent_decision_confidence.labels(agent_name=agent_name).observe(
                confidence
            )

    def set_agent_state(self, agent_name: str, active: bool):
        if self.agent_state:
            self.agent_state.labels(agent_name=agent_name).set(1 if active else 0)

    def set_pipeline_health(self, score: float):
        if self.pipeline_health:
            self.pipeline_health.set(score)

    def set_queue_depth(self, queue_name: str, depth: int):
        if self.queue_depth:
            self.queue_depth.labels(queue_name=queue_name).set(depth)

    def record_error(self, component: str, error_type: str):
        if self.processing_errors:
            self.processing_errors.labels(
                component=component, error_type=error_type
            ).inc()

    def get_metrics(self) -> bytes:
        """Get current metrics in Prometheus format"""
        if self.registry:
            return generate_latest(self.registry)
        return b""

    async def start_server(self, port: int = 9090):
        """Start Prometheus metrics HTTP server"""
        if PROMETHEUS_AVAILABLE:
            start_http_server(port, registry=self.registry)
            logger.info(f"Prometheus metrics server started on port {port}")

    async def push_metrics(self, gateway: str, job: str = "newsfeed"):
        """Push metrics to Prometheus Pushgateway"""
        if PROMETHEUS_AVAILABLE and self.registry:
            try:
                push_to_gateway(gateway, job=job, registry=self.registry)
                logger.debug(f"Metrics pushed to {gateway}")
            except Exception as e:
                logger.error(f"Metrics push error: {e}")


# ============================================================================
# Analytics Processor
# ============================================================================


class AnalyticsProcessor:
    """
    Real-time analytics processor for pipeline events.

    Features:
    - Event aggregation
    - Metric calculation
    - Alerting
    - Dashboard data generation
    """

    def __init__(self, metrics: MetricsExporter):
        self.metrics = metrics
        self._aggregations: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self._alerts: List[Dict[str, Any]] = []
        self._alert_thresholds = {
            "error_rate": 0.1,  # 10% error rate
            "latency_p99": 30,  # 30 seconds
            "queue_depth": 1000,
            "engagement_drop": 0.3,  # 30% drop
        }

    async def process_event(self, event: PipelineEvent):
        """Process a single pipeline event"""
        event_type = event.event_type

        # Route to specific handlers
        if event_type == EventType.CONTENT_CREATED:
            await self._handle_content_created(event)
        elif event_type == EventType.CONTENT_CURATED:
            await self._handle_content_curated(event)
        elif event_type == EventType.VIDEO_PRODUCED:
            await self._handle_video_produced(event)
        elif event_type == EventType.VIDEO_FAILED:
            await self._handle_video_failed(event)
        elif event_type in (EventType.PUBLISH_SUCCESS, EventType.PUBLISH_FAILED):
            await self._handle_publish(event)
        elif event_type in (
            EventType.VIEW,
            EventType.LIKE,
            EventType.COMMENT,
            EventType.SHARE,
        ):
            await self._handle_engagement(event)
        elif event_type == EventType.PIPELINE_HEALTH:
            await self._handle_health_check(event)

        # Update aggregations
        await self._update_aggregations(event)

        # Check alerts
        await self._check_alerts()

    async def _handle_content_created(self, event: PipelineEvent):
        """Handle content creation event"""
        data = event.data
        self.metrics.record_content_created(
            category=data.get("category", "unknown"),
            source=data.get("source", "unknown"),
        )

    async def _handle_content_curated(self, event: PipelineEvent):
        """Handle content curation event"""
        data = event.data
        self.metrics.record_content_curated(
            category=data.get("category", "unknown"),
            approved=data.get("approved", False),
            score=data.get("score", 0.0),
        )

    async def _handle_video_produced(self, event: PipelineEvent):
        """Handle video production event"""
        data = event.data
        self.metrics.record_video_produced(
            success=True,
            duration_seconds=data.get("duration", 0),
            script_length=data.get("script_length", 0),
        )

    async def _handle_video_failed(self, event: PipelineEvent):
        """Handle video production failure"""
        data = event.data
        self.metrics.record_video_produced(
            success=False, duration_seconds=0, script_length=0
        )
        self.metrics.record_error(
            component="video_producer", error_type=data.get("error_type", "unknown")
        )

    async def _handle_publish(self, event: PipelineEvent):
        """Handle publish event"""
        data = event.data
        success = event.event_type == EventType.PUBLISH_SUCCESS

        self.metrics.record_publish(
            platform=data.get("platform", "unknown"),
            success=success,
            latency_seconds=data.get("latency", 0),
        )

        if not success:
            self.metrics.record_error(
                component="publisher",
                error_type=data.get("error_type", "publish_failed"),
            )

    async def _handle_engagement(self, event: PipelineEvent):
        """Handle engagement event"""
        data = event.data
        event_map = {
            EventType.VIEW: "view",
            EventType.LIKE: "like",
            EventType.COMMENT: "comment",
            EventType.SHARE: "share",
        }

        self.metrics.record_engagement(
            platform=data.get("platform", "unknown"),
            event_type=event_map.get(event.event_type, "unknown"),
            content_id=data.get("content_id", "unknown"),
            rate=data.get("engagement_rate", 0.0),
        )

    async def _handle_health_check(self, event: PipelineEvent):
        """Handle pipeline health check"""
        data = event.data
        self.metrics.set_pipeline_health(data.get("score", 0.0))

        for queue_name, depth in data.get("queues", {}).items():
            self.metrics.set_queue_depth(queue_name, depth)

    async def _update_aggregations(self, event: PipelineEvent):
        """Update rolling aggregations"""
        now = utc_now()
        window = now.strftime("%Y-%m-%d-%H")

        key = f"{event.event_type.value}_{window}"

        if key not in self._aggregations:
            self._aggregations[key] = {
                "count": 0,
                "first_seen": now,
                "last_seen": now,
                "data_samples": [],
            }

        agg = self._aggregations[key]
        agg["count"] += 1
        agg["last_seen"] = now

        # Keep sample of recent data
        if len(agg["data_samples"]) < 100:
            agg["data_samples"].append(event.data)

        # Cleanup old aggregations (keep last 24 hours)
        cutoff = now - timedelta(hours=24)
        to_remove = [
            k for k, v in self._aggregations.items() if v["last_seen"] < cutoff
        ]
        for k in to_remove:
            del self._aggregations[k]

    async def _check_alerts(self):
        """Check alert thresholds"""
        # Calculate current error rate
        total_events = sum(a["count"] for a in self._aggregations.values())
        error_events = sum(
            a["count"]
            for k, a in self._aggregations.items()
            if "failed" in k or "error" in k
        )

        if total_events > 100:
            error_rate = error_events / total_events
            if error_rate > self._alert_thresholds["error_rate"]:
                await self._create_alert(
                    "high_error_rate",
                    f"Error rate is {error_rate:.2%}",
                    severity="warning",
                )

    async def _create_alert(
        self, alert_type: str, message: str, severity: str = "info"
    ):
        """Create an alert"""
        alert = {
            "id": hashlib.md5(
                f"{alert_type}{utc_now()}".encode(), usedforsecurity=False
            ).hexdigest()[:12],
            "type": alert_type,
            "message": message,
            "severity": severity,
            "timestamp": utc_now().isoformat(),
        }

        self._alerts.append(alert)

        # Keep last 100 alerts
        if len(self._alerts) > 100:
            self._alerts = self._alerts[-100:]

        logger.warning(f"Alert [{severity}]: {message}")

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for dashboard visualization"""
        return {
            "aggregations": {
                k: {
                    "count": v["count"],
                    "first_seen": v["first_seen"].isoformat(),
                    "last_seen": v["last_seen"].isoformat(),
                }
                for k, v in self._aggregations.items()
            },
            "alerts": self._alerts[-20:],
            "total_events": sum(a["count"] for a in self._aggregations.values()),
        }


# ============================================================================
# Analytics Pipeline
# ============================================================================


class AnalyticsPipeline:
    """
    Main analytics pipeline orchestrator.

    Combines:
    - Event production
    - Event consumption
    - Metrics export
    - Analytics processing
    """

    def __init__(self):
        self.producer = EventProducer()
        self.consumer = EventConsumer()
        self.metrics = MetricsExporter()
        self.processor = AnalyticsProcessor(self.metrics)
        self._running = False

    async def start(self):
        """Start the analytics pipeline"""
        if self._running:
            return

        # Start components
        await self.producer.start()

        # Register event handlers
        for event_type in EventType:
            self.consumer.register_handler(event_type, self.processor.process_event)

        # Start metrics server
        await self.metrics.start_server(
            port=int(getattr(settings, "PROMETHEUS_PORT", 9090))
        )

        self._running = True
        logger.info("Analytics pipeline started")

    async def stop(self):
        """Stop the analytics pipeline"""
        await self.producer.stop()
        await self.consumer.stop()
        self._running = False
        logger.info("Analytics pipeline stopped")

    async def emit_event(
        self,
        event_type: EventType,
        source: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Emit an event to the pipeline"""
        event = self.producer.create_event(event_type, source, data, metadata)
        await self.producer.send_event(event)

        # Also process locally for immediate metrics
        await self.processor.process_event(event)

    def get_metrics(self) -> bytes:
        """Get current Prometheus metrics"""
        return self.metrics.get_metrics()

    def get_dashboard(self) -> Dict[str, Any]:
        """Get dashboard data"""
        return self.processor.get_dashboard_data()


# ============================================================================
# Grafana Dashboard Config Generator
# ============================================================================


def generate_grafana_dashboard() -> Dict[str, Any]:
    """
    Generate Grafana dashboard configuration for news feed metrics.
    """
    return {
        "dashboard": {
            "id": None,
            "uid": "newsfeed-elite",
            "title": "News Feed AI - Elite Analytics",
            "tags": ["newsfeed", "ai", "production"],
            "timezone": "browser",
            "schemaVersion": 38,
            "version": 1,
            "refresh": "10s",
            "panels": [
                # Row 1: Overview
                {
                    "id": 1,
                    "title": "Pipeline Health",
                    "type": "gauge",
                    "gridPos": {"h": 6, "w": 4, "x": 0, "y": 0},
                    "targets": [{"expr": "newsfeed_pipeline_health", "refId": "A"}],
                    "fieldConfig": {
                        "defaults": {
                            "min": 0,
                            "max": 1,
                            "thresholds": {
                                "steps": [
                                    {"color": "red", "value": 0},
                                    {"color": "yellow", "value": 0.7},
                                    {"color": "green", "value": 0.9},
                                ]
                            },
                        }
                    },
                },
                {
                    "id": 2,
                    "title": "Content Created (24h)",
                    "type": "stat",
                    "gridPos": {"h": 6, "w": 4, "x": 4, "y": 0},
                    "targets": [
                        {
                            "expr": "sum(increase(newsfeed_content_created_total[24h]))",
                            "refId": "A",
                        }
                    ],
                },
                {
                    "id": 3,
                    "title": "Videos Produced (24h)",
                    "type": "stat",
                    "gridPos": {"h": 6, "w": 4, "x": 8, "y": 0},
                    "targets": [
                        {
                            "expr": "sum(increase(newsfeed_videos_produced_total{status='success'}[24h]))",
                            "refId": "A",
                        }
                    ],
                },
                {
                    "id": 4,
                    "title": "Publish Success Rate",
                    "type": "gauge",
                    "gridPos": {"h": 6, "w": 4, "x": 12, "y": 0},
                    "targets": [
                        {
                            "expr": "sum(rate(newsfeed_publish_attempts_total{status='success'}[1h])) / sum(rate(newsfeed_publish_attempts_total[1h]))",
                            "refId": "A",
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {"min": 0, "max": 1, "unit": "percentunit"}
                    },
                },
                {
                    "id": 5,
                    "title": "Active Agents",
                    "type": "stat",
                    "gridPos": {"h": 6, "w": 4, "x": 16, "y": 0},
                    "targets": [{"expr": "sum(newsfeed_agent_state)", "refId": "A"}],
                },
                {
                    "id": 6,
                    "title": "Error Rate",
                    "type": "stat",
                    "gridPos": {"h": 6, "w": 4, "x": 20, "y": 0},
                    "targets": [
                        {
                            "expr": "sum(rate(newsfeed_processing_errors_total[1h]))",
                            "refId": "A",
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "thresholds": {
                                "steps": [
                                    {"color": "green", "value": 0},
                                    {"color": "yellow", "value": 0.01},
                                    {"color": "red", "value": 0.05},
                                ]
                            }
                        }
                    },
                },
                # Row 2: Throughput
                {
                    "id": 7,
                    "title": "Content Pipeline Throughput",
                    "type": "timeseries",
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 6},
                    "targets": [
                        {
                            "expr": "rate(newsfeed_content_created_total[5m])",
                            "legendFormat": "Created",
                            "refId": "A",
                        },
                        {
                            "expr": "rate(newsfeed_content_curated_total{approved='True'}[5m])",
                            "legendFormat": "Curated",
                            "refId": "B",
                        },
                        {
                            "expr": "rate(newsfeed_videos_produced_total{status='success'}[5m])",
                            "legendFormat": "Produced",
                            "refId": "C",
                        },
                        {
                            "expr": "rate(newsfeed_publish_attempts_total{status='success'}[5m])",
                            "legendFormat": "Published",
                            "refId": "D",
                        },
                    ],
                },
                {
                    "id": 8,
                    "title": "Publishing by Platform",
                    "type": "timeseries",
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 6},
                    "targets": [
                        {
                            "expr": "rate(newsfeed_publish_attempts_total{status='success'}[5m])",
                            "legendFormat": "{{platform}}",
                            "refId": "A",
                        }
                    ],
                },
                # Row 3: Latency
                {
                    "id": 9,
                    "title": "Video Production Duration",
                    "type": "histogram",
                    "gridPos": {"h": 8, "w": 8, "x": 0, "y": 14},
                    "targets": [
                        {
                            "expr": "histogram_quantile(0.95, rate(newsfeed_video_production_seconds_bucket[5m]))",
                            "legendFormat": "p95",
                            "refId": "A",
                        }
                    ],
                },
                {
                    "id": 10,
                    "title": "Publish Latency by Platform",
                    "type": "timeseries",
                    "gridPos": {"h": 8, "w": 8, "x": 8, "y": 14},
                    "targets": [
                        {
                            "expr": "histogram_quantile(0.95, rate(newsfeed_publish_latency_seconds_bucket[5m]))",
                            "legendFormat": "{{platform}} p95",
                            "refId": "A",
                        }
                    ],
                },
                {
                    "id": 11,
                    "title": "Agent Decision Confidence",
                    "type": "timeseries",
                    "gridPos": {"h": 8, "w": 8, "x": 16, "y": 14},
                    "targets": [
                        {
                            "expr": "histogram_quantile(0.5, rate(newsfeed_agent_decision_confidence_bucket[5m]))",
                            "legendFormat": "{{agent_name}}",
                            "refId": "A",
                        }
                    ],
                },
                # Row 4: Engagement
                {
                    "id": 12,
                    "title": "Engagement Events",
                    "type": "timeseries",
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 22},
                    "targets": [
                        {
                            "expr": "rate(newsfeed_engagement_events_total[5m])",
                            "legendFormat": "{{platform}} - {{event_type}}",
                            "refId": "A",
                        }
                    ],
                },
                {
                    "id": 13,
                    "title": "Trends Tracked",
                    "type": "timeseries",
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 22},
                    "targets": [
                        {
                            "expr": "newsfeed_trends_tracked",
                            "legendFormat": "{{source}}",
                            "refId": "A",
                        }
                    ],
                },
                # Row 5: Errors and Queues
                {
                    "id": 14,
                    "title": "Processing Errors",
                    "type": "timeseries",
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 30},
                    "targets": [
                        {
                            "expr": "rate(newsfeed_processing_errors_total[5m])",
                            "legendFormat": "{{component}} - {{error_type}}",
                            "refId": "A",
                        }
                    ],
                },
                {
                    "id": 15,
                    "title": "Queue Depths",
                    "type": "timeseries",
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 30},
                    "targets": [
                        {
                            "expr": "newsfeed_queue_depth",
                            "legendFormat": "{{queue_name}}",
                            "refId": "A",
                        }
                    ],
                },
            ],
        }
    }


# ============================================================================
# Factory Functions
# ============================================================================


def create_analytics_pipeline() -> AnalyticsPipeline:
    """Factory function to create the analytics pipeline"""
    return AnalyticsPipeline()


def create_metrics_exporter() -> MetricsExporter:
    """Factory function to create standalone metrics exporter"""
    return MetricsExporter()


# ============================================================================
# Example Usage
# ============================================================================


async def main():
    """Example usage of analytics pipeline"""
    pipeline = create_analytics_pipeline()

    await pipeline.start()

    # Emit some test events
    await pipeline.emit_event(
        EventType.CONTENT_CREATED,
        source="curator",
        data={"category": "technology", "source": "google_trends"},
    )

    await pipeline.emit_event(
        EventType.VIDEO_PRODUCED,
        source="producer",
        data={"duration": 120, "script_length": 500},
    )

    await pipeline.emit_event(
        EventType.PUBLISH_SUCCESS,
        source="distributor",
        data={"platform": "youtube", "latency": 2.5},
    )

    # Get dashboard data
    dashboard = pipeline.get_dashboard()
    print(json.dumps(dashboard, indent=2))

    # Generate Grafana config
    grafana_config = generate_grafana_dashboard()
    print(json.dumps(grafana_config, indent=2))

    await asyncio.sleep(5)
    await pipeline.stop()


if __name__ == "__main__":
    asyncio.run(main())
