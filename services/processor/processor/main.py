"""
ElevatedIQ News Feed Processor - Main Entry Point
Kafka consumer that processes raw content through AI analysis pipeline
"""

import asyncio
import json
import signal
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import structlog
from kafka import KafkaConsumer, KafkaProducer
from prometheus_client import Counter, Histogram, start_http_server

from .analyzer import ContentAnalyzer
from .config import get_settings
from .database import DatabaseClient
from .embeddings import EmbeddingGenerator

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Prometheus metrics
MESSAGES_PROCESSED = Counter(
    "news_feed_messages_processed_total",
    "Total number of messages processed",
    ["status", "platform"],
)
PROCESSING_TIME = Histogram(
    "news_feed_processing_seconds",
    "Time spent processing content",
    ["platform"],
)
AI_ANALYSIS_TIME = Histogram(
    "news_feed_ai_analysis_seconds", "Time spent on AI analysis"
)
EMBEDDING_TIME = Histogram(
    "news_feed_embedding_seconds", "Time spent generating embeddings"
)


class NewsProcessor:
    """Main processor class that orchestrates content analysis"""

    def __init__(self):
        self.settings = get_settings()
        self.running = True
        self.consumer: Optional[KafkaConsumer] = None
        self.producer: Optional[KafkaProducer] = None
        self.analyzer: Optional[ContentAnalyzer] = None
        self.embedding_gen: Optional[EmbeddingGenerator] = None
        self.db: Optional[DatabaseClient] = None

    async def initialize(self):
        """Initialize all components"""
        logger.info(
            "Initializing News Feed Processor",
            environment=self.settings.environment,
        )

        # Initialize Kafka consumer with retry
        kafka_retry_count = 0
        kafka_max_retries = 10
        kafka_retry_delay = 5

        while kafka_retry_count < kafka_max_retries:
            try:
                logger.info(
                    "Attempting to connect to Kafka",
                    attempt=kafka_retry_count + 1,
                )
                self.consumer = KafkaConsumer(
                    self.settings.kafka_input_topic,
                    bootstrap_servers=(
                        self.settings.kafka_bootstrap_servers.split(",")
                    ),
                    group_id=self.settings.kafka_consumer_group,
                    auto_offset_reset="earliest",
                    enable_auto_commit=False,
                    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                    max_poll_records=self.settings.batch_size,
                )
                logger.info("Kafka consumer connected successfully")
                break
            except Exception as e:
                kafka_retry_count += 1
                logger.warning(
                    "Failed to connect to Kafka",
                    attempt=kafka_retry_count,
                    max_retries=kafka_max_retries,
                    error=str(e),
                )
                if kafka_retry_count >= kafka_max_retries:
                    logger.error("Max Kafka connection retries reached, giving up")
                    raise
                await asyncio.sleep(kafka_retry_delay)

        # Initialize Kafka producer
        self.producer = KafkaProducer(
            bootstrap_servers=(self.settings.kafka_bootstrap_servers.split(",")),
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            acks="all",
            retries=3,
        )

        # Initialize AI components
        self.analyzer = ContentAnalyzer()
        self.embedding_gen = EmbeddingGenerator()

        # Initialize database connection
        self.db = DatabaseClient(self.settings.postgres_dsn)
        await self.db.connect()

        logger.info("Initialization complete")

    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down processor")
        self.running = False

        if self.consumer:
            self.consumer.close()
        if self.producer:
            self.producer.close()
        if self.db:
            await self.db.disconnect()

        logger.info("Shutdown complete")

    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single content message through the AI pipeline"""
        content_id = message.get("id")
        platform = message.get("platform", "unknown")

        logger.info("Processing content", content_id=content_id, platform=platform)

        try:
            # Extract text content for analysis
            title = message.get("title", "")
            description = message.get("description", "")
            raw_content = message.get("raw_content", {})

            # Combine text for analysis
            text_content = f"{title}\n\n{description}"
            if raw_content.get("transcript"):
                text_content += f"\n\n{raw_content['transcript']}"

            # Run AI analysis with Claude
            with AI_ANALYSIS_TIME.time():
                if self.analyzer:
                    analysis = await self.analyzer.analyze(
                        text=text_content,
                        platform=platform,
                        metadata=message.get("metadata", {}),
                    )
                else:
                    analysis = {}

            # Generate embeddings
            with EMBEDDING_TIME.time():
                if self.embedding_gen:
                    embedding = await self.embedding_gen.generate(text_content)
                else:
                    embedding = []

            # Build processed content
            geo_class = analysis.get("geo_classification", "global")
            processed = {
                **message,
                "processing_status": "completed",
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "summary": analysis.get("summary"),
                "category": analysis.get("category"),
                "tags": analysis.get("tags", []),
                "sentiment": analysis.get("sentiment", 0.0),
                "quality_score": analysis.get("quality_score", 0.0),
                "geo_classification": geo_class,
                "ai_analysis": {
                    "key_points": analysis.get("key_points", []),
                    "entities": analysis.get("entities", []),
                    "topics": analysis.get("topics", []),
                    "credibility_score": analysis.get("credibility_score", 0.0),
                    "bias_assessment": analysis.get("bias_assessment"),
                    "model_used": self.settings.claude_model,
                    "analyzed_at": datetime.now(timezone.utc).isoformat(),
                },
                "embedding": embedding,
            }

            # Update database
            if self.db and content_id:
                await self.db.update_content(content_id, processed)

            MESSAGES_PROCESSED.labels(status="success", platform=platform).inc()

            return processed

        except Exception as e:
            logger.error("Processing failed", content_id=content_id, error=str(e))

            MESSAGES_PROCESSED.labels(status="error", platform=platform).inc()

            # Return error state
            return {
                **message,
                "processing_status": "failed",
                "error_message": str(e),
                "processed_at": datetime.now(timezone.utc).isoformat(),
            }

    async def run(self):
        """Main processing loop"""
        await self.initialize()

        logger.info(
            "Starting processing loop",
            input_topic=self.settings.kafka_input_topic,
            output_topic=self.settings.kafka_output_topic,
        )

        try:
            while self.running:
                # Poll for messages
                messages = self.consumer.poll(timeout_ms=1000)

                if not messages:
                    continue

                for topic_partition, records in messages.items():
                    for record in records:
                        platform = record.value.get("platform", "unknown")

                        with PROCESSING_TIME.labels(platform=platform).time():
                            processed = await self.process_message(record.value)

                        # Publish processed content
                        self.producer.send(
                            self.settings.kafka_output_topic, value=processed
                        )

                # Commit offsets after successful processing
                self.consumer.commit()

        except Exception as e:
            logger.error("Processing loop error", error=str(e))
            raise
        finally:
            await self.shutdown()


def main():
    """Entry point"""
    # Start Prometheus metrics server
    start_http_server(9090)

    processor = NewsProcessor()

    # Handle shutdown signals
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(processor.shutdown()))

    try:
        loop.run_until_complete(processor.run())
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    finally:
        loop.close()


if __name__ == "__main__":
    main()
