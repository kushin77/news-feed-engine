# Creator AI Agent

**Epic:** #45 — Build Content Creator Agent (Autonomous Content Creation)

## 🤖 Purpose

AI agent that autonomously creates, curates, and publishes content on behalf of creators, generating 8-12 posts/day while learning from engagement patterns.

## 🏗️ Architecture

```
Creator Settings & Instructions
    ├── Brand voice + tone guide
    ├── Content preferences (topics, formats)
    ├── Publishing schedule
    └── Creator approved caption templates
    ↓
Agent Daily Loop (runs 4x/day)
    ├── Trend Detection (Grok-2 API)
    │   ├── Trending topics (24h window)
    │   ├── Cultural zeitgeist
    │   └── Relevance scoring to creator niche
    │
    ├── Content Generation (Claude 3.5 Sonnet)
    │   ├── Idea brainstorming (5-10 post ideas)
    │   ├── Caption generation (multiple variants)
    │   └── Visual/format selection
    │
    ├── Integration Tools
    │   ├── Search remix_engine (content variants)
    │   ├── Query recommendation_engine (trending content)
    │   └── Check policy enforcement (brand safety)
    │
    ├── Publisher Selection
    │   ├── Optimal posting time (engagement history)
    │   ├── Platform selector (link to #27 publisher)
    │   └── Engagement prediction (recommendation model)
    │
    └── Creator Review & Approval
        ├── Show top 3 post drafts
        ├── Creator edits caption (optional)
        └── One-click publish or reject
    ↓
Published Across Platforms
    ↓
Engagement Feedback Loop
    ├── Track post performance
    ├── Update creator interest model
    └── Adjust caption style weights
```

## 🔧 Implementation Components

### Core Services
- `agent.py` — Main ReAct loop (reasoning + acting)
- `tools.py` — Claude tools for content operations
  - `write_caption()` — Generate captions
  - `search_trending()` — Grok-2 trend lookup
  - `remix_existing()` — Call remix_engine
  - `publish_variant()` — Multi-platform publishing
- `memory.py` — Agent state + creator preference learning
- `feedback_loop.py` — Engagement tracking + model updates

### Agent Capabilities
- **ReAct Framework:** Reason through content strategy, then act on decisions
- **Tool Use:** Call remix engine, recommendation engine, publisher API
- **Learning:** Updates creator interest model based on engagement (which posts did well?)
- **Safety:** All outputs checked against policy guard rails before publishing

### External Integrations
- Grok-2 API (trend awareness + cultural relevance)
- Claude 3.5 Sonnet (reasoning + content generation)
- Remix Engine API (#74)
- Recommendation Engine API (#65)
- Publisher API (#27)

### Infrastructure
- PostgreSQL (agent state, creator preferences, engagement history)
- Kafka (event sourcing for all agent decisions)
- LangChain (agent orchestration + memory management)

## 📊 Acceptance Criteria

- ✅ Content Quality: AI-generated captions score 7.5/10+ in manual review
- ✅ Throughput: 1 agent → 8-12 posts/day
- ✅ Trend Response: agent publishes trending content <2 hours of trend spike
- ✅ Creator Control: 70%+ of agent suggestions accepted with minor edits
- ✅ Safety: 0 policy-violating posts (manual review 100%)
- ✅ Engagement: AI-authored content achieves 85%+ engagement of human-authored

## 🚀 API Endpoints (Draft)

```python
# Create creator agent instance
POST /v1/agents/creator
{
  "creator_id": "str",
  "brand_voice_guide": "str",
  "content_preferences": ["topic1", "topic2"],
  "publishing_schedule": "[0-23]",  # hours to publish
  "approved_caption_templates": ["str"]
}
→ { "agent_id": "uuid", "status": "initialized" }

# Get today's generated post drafts
GET /v1/agents/{agent_id}/drafts/today
→ {
    "drafts": [
      {
        "draft_id": "uuid",
        "caption_variants": [
          { "variant": "str", "predicted_engagement": 0.87 },
          { "variant": "str", "predicted_engagement": 0.84 }
        ],
        "remix_variants": ["variant_id_1", "variant_id_2"],
        "predicted_platform": "tiktok",
        "optimal_publishing_time": "2026-03-12T18:30:00Z"
      },
      ...
    ]
  }

# Approve and publish post
POST /v1/agents/{agent_id}/drafts/{draft_id}/publish
{
  "caption": "str",  # creator can override
  "variant_id": "uuid"
}
→ { "post_id": "uuid", "status": "published", "platforms": ["tiktok", "instagram"] }

# Reject post draft
POST /v1/agents/{agent_id}/drafts/{draft_id}/reject
{ "reason": "str" }
→ { "status": "rejected", "next_draft_available": "2026-03-12T16:00:00Z" }

# Get agent performance metrics
GET /v1/agents/{agent_id}/metrics
→ {
    "posts_generated_today": 12,
    "creator_approval_rate": 0.72,
    "avg_engagement_vs_human": 0.87,
    "trending_topics_captured": 4,
    "policy_violations": 0
  }

# Update agent preferences
PUT /v1/agents/{agent_id}/preferences
{
  "content_topics": ["new_topic"],
  "tone_adjust": "more_energetic"
}
→ { "status": "updated", "effective_next_cycle": "2026-03-12T14:00:00Z" }
```

## 📈 Success Metrics

| Metric | Target |
|--------|--------|
| Caption Quality Score | 7.5/10+ |
| Daily Post Generation | 8-12 posts |
| Trend Response Time | < 2 hours |
| Creator Approval Rate | ≥ 70% |
| Policy Violations | 0 |
| Engagement vs Human | ≥ 85% |

## 🔐 Safety & Control

- **Creator Approval:** All posts require creator approval before publishing
- **Policy Enforcement:** Automated content moderation before showing to creator
- **Transparency:** Creator can see all agent reasoning (why it chose this post)
- **Fallback:** Agent fails gracefully if external APIs unavailable
- **Audit Trail:** All agent decisions logged for review

## 📋 Dependencies

- #74 (Remix Engine)
- #65 (Recommendation Engine)
- #27 (Publishing API)
- Claude 3.5 Sonnet API
- Grok-2 API

---

**Status:** Design Phase Complete | **Effort:** 7 days | **Priority:** P1

_Milestone 90 Component — Implementation Ready_
