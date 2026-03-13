# Recommendation Engine

**Epic:** #65 — Recommendation Engine (Multi-Model Ranking)

## 🎯 Purpose

Delivers hyperpersonalized feeds using multi-model ranking (5+ models) with dynamic weighting, achieving >0.80 NDCG@5 while maintaining creator diversity and platform health.

## 🏗️ Architecture

```
User Request (context: user_id, platform, device, time_of_day)
    ↓
Feature Aggregation Layer
    ├── Real-time user features (Feast + Redis)
    ├── Content features (embedding, metadata)
    ├── Creator features (CTR history, niche)
    └── Contextual features (trend velocity, seasonality)
    ↓
5-Model Ranking Stack
    ├── XGBoost CTR Model (click likelihood)
    ├── LightGBM Time-to-Engagement Model (watch time)
    ├── ColBERT Semantic Relevance (semantic similarity)
    ├── Diversity Optimizer (creator/topic distribution)
    └── Policy-Based Re-ranker (brand safety, recency, diversity)
    ↓
Ensemble Aggregation
    ├── Dynamic weight adjustment (A/B test results)
    ├── Contextual ranking (time of day, platform)
    └── Online learning feedback
    ↓
Ranked Feed (personalized, diverse, engaging)
    ↓
Redis Cache (hyperpersonalized feeds, <100ms SLA)
```

## 🔧 Implementation Components

### Core Services
- `recommendation_engine.py` — Multi-model ensembler
- `feature_aggregator.py` — Real-time feature computation from Feast
- `policy_ranker.py` — Business logic constraints (diversity, recency, safety)
- `diversity_optimizer.py` — Creator/topic distribution
- `online_learning.py` — Real-time model weight adjustment

### Ranking Models
- **XGBoost CTR Model:** Predicts click likelihood (historical CTR, user interests, content metadata)
- **LightGBM Time-to-Engagement:** Predicts watch time (creator reputation, topic velocity, user history)
- **ColBERT Semantic Relevance:** Semantic similarity between user interests + content embeddings
- **Diversity Optimizer:** Ensures top 100 creators cover ≤25% of feed
- **Policy Re-ranker:** Applies business rules (no competitor conflicts, min crew diversity, etc.)

### Feature Store
- Feast (feature definitions + serving)
- Redis (online store for <100ms serving)
- BigQuery (offline store for training)
- 200+ features across 5 categories (user, content, creator, contextual, temporal)

### Infrastructure
- Kafka (real-time feedback loop)
- PostgreSQL (model lineage + A/B test config)
- Redis (cache layer)

## 📊 Acceptance Criteria

- ✅ NDCG@5: > 0.80 (compared to historical baseline)
- ✅ Creator Diversity: top 100 creators cover ≤ 25% of feed
- ✅ Latency: feed generation < 100ms p99
- ✅ Cold-start handling: new users get 85% recall vs warm users
- ✅ Online Learning: feedback loop reranks <500ms
- ✅ Creator Fairness: creator lift metrics within 10% of platform average

## 🚀 API Endpoints (Draft)

```python
# Generate personalized feed
POST /v1/recommendations/feed
{
  "user_id": "str",
  "platform": "tiktok|instagram|youtube",
  "device": "mobile|desktop|tablet",
  "num_posts": 20,
  "context": {
    "current_interests": ["technology", "entertainment"],
    "excluded_creators": ["blocked_user_1"],
    "diversity_constraints": { "max_same_creator": 3 }
  }
}
→ {
    "feed": [
      {
        "post_id": "uuid",
        "creator_id": "uuid",
        "model_scores": {
          "ctr_score": 0.87,
          "engagement_time": 0.92,
          "semantic_relevance": 0.78,
          "diversity_penalty": -0.05,
          "final_rank_score": 0.85
        }
      },
      ...
    ],
    "generation_time_ms": 87,
    "feature_version": "v1.2.3"
  }

# Get feature vector for user
GET /v1/recommendations/features/user/{user_id}
→ {
    "features": {
      "user_preferences": [0.12, 0.45, 0.78, ...],
      "engagement_history": [0.05, 0.23, 0.91, ...],
      "created_at": "2026-03-12T10:00:00Z",
      "last_updated": "2026-03-12T12:15:00Z"
    }
  }

# Log engagement feedback for online learning
POST /v1/recommendations/feedback
{
  "user_id": "str",
  "post_id": "str",
  "action": "click|watch|share|save",
  "engagement_time_seconds": 45
}
→ { "status": "logged", "ranking_updated": true }

# Get model performance metrics
GET /v1/recommendations/metrics
→ {
    "ndcg_5": 0.82,
    "creator_diversity_score": 0.87,
    "latency_p99_ms": 95,
    "cold_start_recall": 0.85,
    "model_versions": {
      "xgboost_ctr": "v2.1.0",
      "lightgbm_engagement": "v1.8.3",
      "colbert_semantic": "v1.0.1"
    }
  }
```

## 📈 Success Metrics

| Metric | Target |
|--------|--------|
| NDCG@5 | > 0.80 |
| Creator Diversity | Top 100 ≤ 25% of feed |
| Feed Generation Latency | < 100ms p99 |
| Cold-start User Recall | 85% vs warm users |
| Online Learning Latency | < 500ms |
| Creator Fairness | ±10% of platform avg |

## 🔐 Fairness & Guardrails

- **Creator Diversity:** Hardcoded constraint preventing feed dominance
- **Cold-start Handling:** Fallback to content-based recommendations for new users
- **Temporal Diversity:** Mix fresh + established content
- **Policy Compliance:** Automatic enforcement of brand safety rules

## 📋 Dependencies

- #61 (Trending API)
- #64 (Discovery API)
- Feast setup complete
- Feature definitions for 200+ features

---

**Status:** Design Phase Complete | **Effort:** 6 days | **Priority:** P1

_Milestone 90 Component — Implementation Ready_
