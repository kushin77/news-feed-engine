# AI Personas Service

**Epic:** #29 — AI Virtual Influencer / Persona System

## 👤 Purpose

Creates and manages synthetic personalities (virtual influencers, AI personas) with consistent voice, background story, engagement patterns, and simulated growth trajectory.

## 🏗️ Architecture

```
Persona Template Selection
    ├── 10+ predefined archetypes (Creator, Wellness Coach, Tech Bro, etc.)
    ├── Voice template + style
    ├── Appearance (avatar or AI-generated face)
    └── Background story elements
    ↓
Persona Instance Creation
    ├── Create unique identity (name, bio, history)
    ├── Define content preferences + niche
    ├── Initialize follower simulation model
    └── Store in PostgreSQL + Redis
    ↓
Personality Engine
    ├── Response generation (Claude 3.5 Sonnet with persona system prompt)
    ├── Consistency checking (verify all responses on-brand)
    ├── Memory management (long-term personality traits)
    └── Emotion/energy modeling (can vary by time of day)
    ↓
Multi-Channel Presence
    ├── Social media posts (TikTok, Instagram, YouTube)
    ├── User interactions (respond to comments, DMs)
    ├── Live stream simulation (scheduled appearances)
    └── Cross-platform consistency
    ↓
Growth Simulation
    ├── Follower acquisition model (realistic curve)
    ├── Engagement decay/peaks
    ├── Viral moment simulation
    └── Creator collaboration opportunities
```

## 🔧 Implementation Components

### Core Services
- `persona_engine.py` — Persona definition + state machine
- `avatar_system.py` — Avatar appearance + customization
- `character_memory.py` — Persona personality persistence
- `growth_simulator.py` — Follower acquisition + engagement patterns
- `response_generator.py` — Multi-turn conversation engine

### Persona Templates (10+ Archetypes)
1. **The Creator** — High energy, experimental, always posting (TikTok native)
2. **The Coach** — Motivational, knowledgeable, structured content (Fitness/wellness)
3. **The Tech Bro** — Product launches, startup vibes, networking (B2B tech)
4. **The Artist** — Creative, visual-first, storytelling (Community-driven)
5. **The Influencer** — Lifestyle, trending, aspirational (Celebrity-style)
6. **The Educator** — Deep knowledge, teaching, patience (Educational niche)
7. **The Entrepreneur** — Money mindset, growth hacks, ambition (Business)
8. **The Entertainer** — Comedy, character changes, viral potential (Entertainment)
9. **The Niche Expert** — Authority in specific domain, thoughtful, technical (Niche audiences)
10. **The Community Builder** — Authentic, relatable, engages with followers (Grassroots)

### Personality Components
- **Voice/Tone:** Vocabulary, emoji usage, sentence structure, humor style
- **Values:** What topics resonate, what values matter
- **Content Preferences:** Video types, post length, frequency
- **Interaction Style:** Responsive vs. aloof, casual vs. professional
- **Growth Ambitions:** Short-term metrics (goes viral) vs. steady growth

### Infrastructure
- Claude 3.5 Sonnet (conversation generation)
- Synthesia or D-ID (avatar generation + animation)
- ElevenLabs (voice generation)
- PostgreSQL (persona metadata + memory)
- Redis (session caching + active personas)

## 📊 Acceptance Criteria

- ✅ Consistency: same persona generates 100% on-brand responses
- ✅ Naturalism: 90%+ of responses rated as "natural" by human raters
- ✅ Growth Simulation: follower curves match viral distribution models
- ✅ Personality Range: 10+ distinct, recognizable persona archetypes
- ✅ Engagement Rate: AI persona content achieves 80%+ of human influencer engagement

## 🚀 API Endpoints (Draft)

```python
# List available persona templates
GET /v1/personas/templates
→ {
    "templates": [
      {
        "template_id": "creator",
        "name": "The Creator",
        "description": "High energy, experimental, TikTok native",
        "voice_profile": "casual, energetic, emoji-heavy",
        "content_preferences": ["shorts", "trends", "challenges"]
      },
      ...
    ]
  }

# Create persona instance
POST /v1/personas
{
  "template_id": "creator",
  "name": "Luna_Creative",
  "bio": "Creative explorer trying everything once",
  "avatar_customization": {
    "appearance": "anime_style",
    "hair_color": "blue",
    "style": "streetwear"
  }
}
→ { "persona_id": "uuid", "follower_count": 0, "status": "initialized" }

# Generate persona response/post
POST /v1/personas/{persona_id}/generate
{
  "prompt": "What's your take on AI-generated content?",
  "context": {
    "recent_trends": ["AI safety"],
    "audience_sentiment": "curious"
  }
}
→ {
    "response": "str",
    "engagement_prediction": 0.87,
    "consistency_score": 0.98
  }

# Get persona profile
GET /v1/personas/{persona_id}
→ {
    "persona_id": "uuid",
    "name": "Luna_Creative",
    "template": "creator",
    "follower_count": 12400,
    "engagement_rate": 0.087,
    "consistency_score": 0.97,
    "next_post_scheduled": "2026-03-12T16:00:00Z"
  }

# Run growth simulation (weekly update)
POST /v1/personas/{persona_id}/simulate-growth
{
  "time_window_days": 7,
  "trending_topics": ["AI", "creator economy"]
}
→ {
    "follower_gain": 245,
    "viral_moments": 1,
    "engagement_trend": "📈",
    "churn_rate": 0.02
  }

# Interact with persona (user comment response)
POST /v1/personas/{persona_id}/interact
{
  "interaction_type": "comment_reply",
  "user_message": "This is so cool!",
  "context": {
    "post_engagement_rate": 0.12,
    "user_follower_count": 5000
  }
}
→ {
    "response": "str",
    "response_time_ms": 450,
    "sentiment": "positive"
  }
```

## 📈 Success Metrics

| Metric | Target |
|--------|--------|
| Response On-Brand Consistency | 100% |
| Naturalness Rating | 90%+ |
| Follower Curve Realism | Matches viral models |
| Persona Distinctiveness | 10+ unique archetypes |
| Engagement vs Human | 80%+ |

## 🔐 Safety & Compliance

- **Disclosure:** All AI personas clearly labeled as synthetic
- **Brand Safety:** Personas never violate platform policies
- **Authenticity:** No impersonation of real people
- **Audit Trail:** All persona interactions logged
- **Fallback:** Graceful degradation if persona consistency fails

## 📋 Dependencies

- #70 (Voice Cloning)
- Claude 3.5 Sonnet API
- Synthesia or D-ID avatar service
- ElevenLabs voice generation

---

**Status:** Design Phase Complete | **Effort:** 5 days | **Priority:** P2

_Milestone 90 Component — Implementation Ready_
