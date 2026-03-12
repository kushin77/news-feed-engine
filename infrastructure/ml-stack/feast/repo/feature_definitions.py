# Feast Feature Store Configuration
# Define features for: user profiles, content attributes, engagement signals

from datetime import timedelta
from feast import Entity, Feature, FeatureView, Field, FileSource, RedisOnlineStore
from feast.types import Float32, Int32, Int64, String
import os

# === ENTITIES ===
user = Entity(
    name="user_id",
    description="User ID for personalization features",
    value_type=String()
)

content = Entity(
    name="content_id",
    description="Content ID for content-specific features",
    value_type=String()
)

creator = Entity(
    name="creator_id",
    description="Creator ID for creator-specific features",
    value_type=String()
)

# === DATA SOURCES ===
# In production, these would be BigQuery tables updated daily

user_profile_source = FileSource(
    name="user_profiles",
    path="s3://elevatediq-ml/features/user_profiles/*.parquet",
    timestamp_field="event_timestamp",
)

content_attributes_source = FileSource(
    name="content_attributes",
    path="s3://elevatediq-ml/features/content_attributes/*.parquet",
    timestamp_field="event_timestamp",
)

engagement_signals_source = FileSource(
    name="engagement_signals",
    path="s3://elevatediq-ml/features/engagement_signals/*.parquet",
    timestamp_field="event_timestamp",
)

trend_features_source = FileSource(
    name="trend_features",
    path="s3://elevatediq-ml/features/trends/*.parquet",
    timestamp_field="event_timestamp",
)

# === FEATURE VIEWS ===

user_features_view = FeatureView(
    name="user_features",
    entities=[user],
    ttl=timedelta(hours=24),
    source=user_profile_source,
    features=[
        Field(name="age_bracket", dtype=String, description="User age group: 13-17, 18-24, 25-34, 35+"),
        Field(name="country", dtype=String, description="User country code (ISO 3166)"),
        Field(name="interests", dtype=String, description="Comma-separated user interests"),
        Field(name="content_type_preferences", dtype=String, description="Preferred content types"),
        Field(name="avg_watch_time_minutes", dtype=Float32, description="Average watch time per session"),
        Field(name="engagement_rate", dtype=Float32, description="(likes + shares + saves) / content_viewed"),
        Field(name="follower_count", dtype=Int32, description="User follower count"),
        Field(name="creator_score", dtype=Float32, description="0-1 score of content quality if creator"),
        Field(name="last_active_timestamp", dtype=Int64, description="Unix timestamp of last activity"),
        Field(name="device_type", dtype=String, description="Primary device: mobile, tablet, desktop"),
        Field(name="platform", dtype=String, description="Primary platform: web, ios, android"),
    ],
)

content_features_view = FeatureView(
    name="content_features",
    entities=[content],
    ttl=timedelta(hours=12),
    source=content_attributes_source,
    features=[
        Field(name="category", dtype=String, description="Content category: news, entertainment, education, etc"),
        Field(name="sentiment", dtype=String, description="Content sentiment: positive, negative, neutral"),
        Field(name="emotional_tone", dtype=String, description="Emotion: happy, sad, angry, surprised, fearful"),
        Field(name="length_minutes", dtype=Float32, description="Content duration in minutes"),
        Field(name="language", dtype=String, description="Content language code (ISO 639)"),
        Field(name="has_video", dtype=Int32, description="1 if has video, 0 otherwise"),
        Field(name="has_audio", dtype=Int32, description="1 if has audio, 0 otherwise"),
        Field(name="creator_id", dtype=String, description="Creator ID"),
        Field(name="publish_timestamp", dtype=Int64, description="Unix timestamp when published"),
        Field(name="quality_score", dtype=Float32, description="0-1 quality score from AI analysis"),
    ],
)

engagement_features_view = FeatureView(
    name="engagement_features",
    entities=[user, content],
    ttl=timedelta(hours=6),
    source=engagement_signals_source,
    features=[
        Field(name="likes_count", dtype=Int32, description="Number of likes"),
        Field(name="shares_count", dtype=Int32, description="Number of shares"),
        Field(name="saves_count", dtype=Int32, description="Number of saves"),
        Field(name="comments_count", dtype=Int32, description="Number of comments"),
        Field(name="views_count", dtype=Int32, description="Number of views"),
        Field(name="watch_time_seconds", dtype=Int32, description="Total watch time in seconds"),
        Field(name="completion_rate", dtype=Float32, description="% of content watched (0-1)"),
        Field(name="dwell_time_seconds", dtype=Int32, description="Time spent on content"),
    ],
)

trend_features_view = FeatureView(
    name="trend_features",
    entities=[content],
    ttl=timedelta(hours=4),
    source=trend_features_source,
    features=[
        Field(name="trend_name", dtype=String, description="Name of the trend"),
        Field(name="trend_score", dtype=Float32, description="0-100 trend strength"),
        Field(name="growth_rate", dtype=Float32, description="% growth in last 24h"),
        Field(name="momentum", dtype=Float32, description="Trend acceleration (0-1)"),
        Field(name="forecast_7d_probability", dtype=Float32, description="Likelihood trend continues 7d"),
        Field(name="forecast_14d_probability", dtype=Float32, description="Likelihood trend continues 14d"),
        Field(name="source_count", dtype=Int32, description="Number of sources mentioning trend"),
        Field(name="age_hours", dtype=Int32, description="How long trend has been active"),
    ],
)

creator_features_view = FeatureView(
    name="creator_features",
    entities=[creator],
    ttl=timedelta(hours=24),
    source=FileSource(
        name="creator_features",
        path="s3://elevatediq-ml/features/creators/*.parquet",
        timestamp_field="event_timestamp",
    ),
    features=[
        Field(name="subscriber_count", dtype=Int32, description="Creator subscriber count"),
        Field(name="avg_views_per_video", dtype=Int32, description="Average views per publication"),
        Field(name="category", dtype=String, description="Creator content category"),
        Field(name="engagement_rate", dtype=Float32, description="Average engagement rate"),
        Field(name="content_quality_score", dtype=Float32, description="0-1 quality rating"),
        Field(name="posting_frequency", dtype=String, description="How often creator posts: daily, weekly, etc"),
        Field(name="audience_demographics_json", dtype=String, description="JSON of audience breakdown"),
    ],
)
