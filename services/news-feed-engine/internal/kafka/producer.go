// Package kafka provides Kafka producer and consumer functionality
package kafka

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"github.com/IBM/sarama"
	"go.uber.org/zap"
)

// Producer wraps a Kafka producer for publishing messages
type Producer struct {
	producer sarama.SyncProducer
	logger   *zap.Logger
}

// Message represents a Kafka message to be published
type Message struct {
	Topic     string
	Key       string
	Value     interface{}
	Headers   map[string]string
	Timestamp time.Time
}

// NewProducer creates a new Kafka producer
func NewProducer(brokers []string, logger *zap.Logger) (*Producer, error) {
	config := sarama.NewConfig()
	config.Producer.Return.Successes = true
	config.Producer.Return.Errors = true
	config.Producer.RequiredAcks = sarama.WaitForAll // Wait for all replicas
	config.Producer.Retry.Max = 3
	config.Producer.Compression = sarama.CompressionSnappy
	config.Producer.Idempotent = true // Ensure exactly-once semantics
	config.Net.MaxOpenRequests = 1    // Required for idempotent producer

	producer, err := sarama.NewSyncProducer(brokers, config)
	if err != nil {
		return nil, fmt.Errorf("failed to create Kafka producer: %w", err)
	}

	logger.Info("Kafka producer created successfully", zap.Strings("brokers", brokers))

	return &Producer{
		producer: producer,
		logger:   logger,
	}, nil
}

// NewNoopProducer returns a producer that performs no network operations.
// Useful for development or testing when Kafka is unavailable.
func NewNoopProducer(logger *zap.Logger) *Producer {
	if logger == nil {
		// fall back to a no-op logger if nil
		noop, _ := zap.NewDevelopment()
		logger = noop
	}
	logger.Info("Kafka producer running in noop mode")
	return &Producer{producer: nil, logger: logger}
}

// Publish sends a message to Kafka
func (p *Producer) Publish(ctx context.Context, msg Message) error {
	// No-op if underlying producer is not configured (development mode)
	if p == nil || p.producer == nil {
		if p != nil && p.logger != nil {
			p.logger.Debug("Kafka publish skipped: noop producer")
		}
		return nil
	}
	// Set timestamp if not provided
	if msg.Timestamp.IsZero() {
		msg.Timestamp = time.Now()
	}

	// Serialize value to JSON
	valueBytes, err := json.Marshal(msg.Value)
	if err != nil {
		return fmt.Errorf("failed to marshal message value: %w", err)
	}

	// Build Kafka message
	kafkaMsg := &sarama.ProducerMessage{
		Topic:     msg.Topic,
		Key:       sarama.StringEncoder(msg.Key),
		Value:     sarama.ByteEncoder(valueBytes),
		Timestamp: msg.Timestamp,
	}

	// Add headers if provided
	if len(msg.Headers) > 0 {
		kafkaMsg.Headers = make([]sarama.RecordHeader, 0, len(msg.Headers))
		for key, value := range msg.Headers {
			kafkaMsg.Headers = append(kafkaMsg.Headers, sarama.RecordHeader{
				Key:   []byte(key),
				Value: []byte(value),
			})
		}
	}

	// Publish message
	partition, offset, err := p.producer.SendMessage(kafkaMsg)
	if err != nil {
		p.logger.Error("Failed to publish message to Kafka",
			zap.String("topic", msg.Topic),
			zap.String("key", msg.Key),
			zap.Error(err))
		return fmt.Errorf("failed to publish message: %w", err)
	}

	p.logger.Debug("Message published successfully",
		zap.String("topic", msg.Topic),
		zap.String("key", msg.Key),
		zap.Int32("partition", partition),
		zap.Int64("offset", offset))

	return nil
}

// PublishBatch sends multiple messages to Kafka in a single batch
func (p *Producer) PublishBatch(ctx context.Context, messages []Message) error {
	// No-op if underlying producer is not configured
	if p == nil || p.producer == nil {
		if p != nil && p.logger != nil {
			p.logger.Debug("Kafka publish batch skipped: noop producer")
		}
		return nil
	}

	if len(messages) == 0 {
		return nil
	}

	kafkaMessages := make([]*sarama.ProducerMessage, 0, len(messages))

	for _, msg := range messages {
		// Set timestamp if not provided
		if msg.Timestamp.IsZero() {
			msg.Timestamp = time.Now()
		}

		// Serialize value to JSON
		valueBytes, err := json.Marshal(msg.Value)
		if err != nil {
			return fmt.Errorf("failed to marshal message value: %w", err)
		}

		// Build Kafka message
		kafkaMsg := &sarama.ProducerMessage{
			Topic:     msg.Topic,
			Key:       sarama.StringEncoder(msg.Key),
			Value:     sarama.ByteEncoder(valueBytes),
			Timestamp: msg.Timestamp,
		}

		// Add headers if provided
		if len(msg.Headers) > 0 {
			kafkaMsg.Headers = make([]sarama.RecordHeader, 0, len(msg.Headers))
			for key, value := range msg.Headers {
				kafkaMsg.Headers = append(kafkaMsg.Headers, sarama.RecordHeader{
					Key:   []byte(key),
					Value: []byte(value),
				})
			}
		}

		kafkaMessages = append(kafkaMessages, kafkaMsg)
	}

	// Send batch
	err := p.producer.SendMessages(kafkaMessages)
	if err != nil {
		p.logger.Error("Failed to publish batch to Kafka",
			zap.Int("count", len(messages)),
			zap.Error(err))
		return fmt.Errorf("failed to publish batch: %w", err)
	}

	p.logger.Debug("Batch published successfully",
		zap.Int("count", len(messages)))

	return nil
}

// Close closes the Kafka producer
func (p *Producer) Close() error {
	if p == nil {
		return nil
	}
	if p.producer != nil {
		if err := p.producer.Close(); err != nil {
			if p.logger != nil {
				p.logger.Error("Failed to close Kafka producer", zap.Error(err))
			}
			return fmt.Errorf("failed to close producer: %w", err)
		}
		if p.logger != nil {
			p.logger.Info("Kafka producer closed successfully")
		}
	} else {
		if p.logger != nil {
			p.logger.Debug("Kafka noop producer close called")
		}
	}
	return nil
}

// ContentIngestionMessage represents a content ingestion job message
type ContentIngestionMessage struct {
	TenantID    string                 `json:"tenant_id"`
	SourceType  string                 `json:"source_type"` // youtube, twitter, reddit, rss
	SourceID    string                 `json:"source_id"`
	URL         string                 `json:"url"`
	Priority    int                    `json:"priority"`
	Metadata    map[string]interface{} `json:"metadata,omitempty"`
	RequestedAt time.Time              `json:"requested_at"`
}

// ContentProcessingMessage represents a content processing job message
type ContentProcessingMessage struct {
	TenantID   string                 `json:"tenant_id"`
	ContentID  string                 `json:"content_id"`
	ActionType string                 `json:"action_type"` // summarize, analyze_sentiment, extract_entities, generate_thumbnail
	Priority   int                    `json:"priority"`
	Metadata   map[string]interface{} `json:"metadata,omitempty"`
	QueuedAt   time.Time              `json:"queued_at"`
}

// VideoGenerationMessage represents a video generation job message
type VideoGenerationMessage struct {
	TenantID    string                 `json:"tenant_id"`
	ContentID   string                 `json:"content_id"`
	TemplateID  string                 `json:"template_id"`
	VoiceID     string                 `json:"voice_id"`
	AvatarID    string                 `json:"avatar_id"`
	Options     map[string]interface{} `json:"options,omitempty"`
	Priority    int                    `json:"priority"`
	RequestedAt time.Time              `json:"requested_at"`
}

// WebhookEventMessage represents a webhook event message
type WebhookEventMessage struct {
	TenantID   string                 `json:"tenant_id"`
	SourceType string                 `json:"source_type"` // youtube, twitter, generic
	EventType  string                 `json:"event_type"`
	Payload    map[string]interface{} `json:"payload"`
	ReceivedAt time.Time              `json:"received_at"`
}
