# Multi-Agent System

**Epic:** #28 — AI Multi-Agent Conversation & Collaboration

## 🗣️ Purpose

Orchestrates conversations between multiple AI agents (creator, personas, analysts, policy checker) to collaboratively generate high-quality, compliant content.

## 🏗️ Architecture

```
Content Generation Request
    ├── Topic: "Crypto investing guide"
    ├── Target platform: YouTube
    └── Creator preferences: educational, accessible
    ↓
Agent Orchestrator Initializes
    ├── Creator Agent (idea generation + scripting)
    ├── AI Persona (personality + voice)
    ├── Analyst Agent (research + fact-checking)
    └── Policy Agent (brand safety)
    ↓
Multi-Turn Conversation
    Turn 1: Creator Agent proposes outline
    Turn 2: Analyst Agent validates claims + suggests sources
    Turn 3: Persona Agent adapts voice/tone for persona
    Turn 4: Policy Agent checks for compliance
    Turn 5: Creator Agent refines based on feedback
    ↓
Consensus Mechanism
    ├── Decision Framework (majority vote + weighted expertise)
    ├── Reasoning Alignment (all agents agree on approach)
    └── Quality Checks (engagement prediction + safety)
    ↓
Final Output (ready for creator review)
```

## 🔧 Implementation Components

### Core Services
- `agent_orchestrator.py` — Manage agent lifecycle + communication
- `conversation_engine.py` — Multi-turn dialogue orchestration
- `agent_registry.py` — Agent discovery + capability lookup
- `message_broker.py` — Inter-agent message passing (Kafka/RabbitMQ)
- `decision_framework.py` — Consensus + voting mechanisms

### Agent Types
1. **Creator Agent** (#45) — Content ideation + scripting
2. **Curator Agent** — Content relevance + audience fit
3. **Analyst Agent** — Research validation + fact-checking
4. **Policy Agent** — Brand safety + compliance checking
5. **Persona Agent** (#29) — Voice/tone adaptation

### Communication Patterns
- **Async Messaging:** Kafka topics for agent-to-agent communication
- **Request-Reply:** Synchronous calls for quick checks (policy validation)
- **Broadcast:** Policy updates / rule changes sent to all agents
- **Aggregation:** Coordinator collects votes + reaches consensus

### Infrastructure
- Kafka (message queue for agent communication)
- PostgreSQL (conversation state + decision history)
- LangChain (agent orchestration + tool use)
- Redis (agent state caching)

## 📊 Acceptance Criteria

- ✅ Throughput: 1000 conversations/day with <5s latency per turn
- ✅ Quality: agent-generated collaborative content scores 7.5/10+ in manual review
- ✅ Consensus: 90%+ of agent conversations reach well-reasoned conclusions
- ✅ Safety: 0 policy violations across all agent outputs
- ✅ Scalability: support 50+ concurrent agent conversations

## 🚀 API Endpoints (Draft)

```python
# Start multi-agent collaboration
POST /v1/agents/collaborate
{
  "topic": "str",
  "target_platform": "tiktok|youtube",
  "content_type": "tutorial|story|news",
  "agents_to_include": ["creator", "analyst", "policy", "persona"],
  "creator_id": "uuid"
}
→ { "collaboration_id": "uuid", "status": "started" }

# Get conversation transcript
GET /v1/agents/collaborate/{collaboration_id}/transcript
→ {
    "turns": [
      {
        "agent": "creator",
        "message": "str",
        "reasoning": "str",
        "timestamp": "2026-03-12T12:00:00Z"
      },
      ...
    ],
    "status": "in_progress",
    "progress": 60
  }

# Get current consensus status
GET /v1/agents/collaborate/{collaboration_id}/consensus
→ {
    "consensus_reached": false,
    "vote_status": {
      "quality": { "votes_pass": 3, "votes_fail": 1, "threshold": "majority" },
      "safety": { "votes_pass": 4, "votes_fail": 0, "threshold": "unanimous" }
    },
    "blocker": "Analyst Agent requiring citation for claim X"
  }

# Add constraint or feedback
POST /v1/agents/collaborate/{collaboration_id}/feedback
{
  "role": "creator",
  "feedback": "Make it more engaging for Gen Z audience"
}
→ { "status": "feedback_added", "new_turn_generated": true }

# Get final collaborative output
GET /v1/agents/collaborate/{collaboration_id}/output
→ {
    "final_script": "str",
    "engagement_prediction": 0.87,
    "safety_score": 0.99,
    "agent_reasoning": {
      "creator": "Optimized for platform algorithm",
      "analyst": "All claims verified with sources",
      "policy": "0 violations detected"
    },
    "ready_for_creator_review": true
  }

# Get agent performance metrics
GET /v1/agents/metrics
→ {
    "total_conversations": 12400,
    "avg_conversation_turns": 4.2,
    "consensus_achievement_rate": 0.91,
    "avg_latency_per_turn_ms": 2300,
    "policy_violation_rate": 0.0,
    "quality_score_avg": 7.6
  }
```

## 📈 Success Metrics

| Metric | Target |
|--------|--------|
| Conversation Throughput | 1000/day |
| Latency per Turn | < 5 seconds |
| Content Quality Score | 7.5/10+ |
| Consensus Rate | ≥ 90% |
| Policy Violation Rate | 0% |
| Max Concurrent Conversations | 50+ |

## 🔐 Safety & Governance

- **Unanimous Policy Votes:** Policy agent must approve (not just majority)
- **Audit Trail:** All agent conversations logged for review
- **Escalation:** Controversial decisions escalated to human review
- **Rollback:** Can restart conversation with different agent configuration
- **Monitoring:** Real-time alerts for unusual agent behavior

## 📋 Dependencies

- #45 (Creator Agent)
- #29 (AI Personas)
- Kafka setup
- PostgreSQL for state persistence

---

**Status:** Design Phase Complete | **Effort:** 6 days | **Priority:** P2

_Milestone 90 Component — Implementation Ready_
