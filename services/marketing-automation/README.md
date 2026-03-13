# Marketing Automation - Behavioral Email Nurture & Funnel Automation

**Epic:** #34 — Marketing Funnel Automation (Lead → Trial → Paid Conversion)

## 📧 Purpose

Automates creator onboarding, trial-to-paid conversion, and retention through behavioral email sequences triggered by real-time events.

## 🏗️ Architecture

```
Creator Sign-Up Event
    ↓
Lead Magnet Sequence (7 emails)
    ├── Day 0: Magnet delivery + welcome
    ├── Day 1: Top mistake (social proof)
    ├── Day 3: Case study (social proof)
    ├── Day 5: Feature spotlight
    ├── Day 7: Testimonials
    ├── Day 10: Objection handling
    └── Day 14: Limited offer (14-day free trial)
    ↓
Trial Started
    ↓
Trial Activation Sequence (5 emails)
    ├── Day 0: Welcome + first post checklist
    ├── Day 1: Platform connection trigger (behavioral)
    ├── Day 3: Usage incentive (behavioral)
    ├── Day 5: Feature tutorial
    └── Day 7: Upgrade prompt
    ↓
Conversion Decision Point
    ├── Converted → Retention sequences
    └── Churned → Win-back sequences
    ↓
Churn Win-Back (3 emails)
    ├── Day 1: Exit survey + discount
    ├── Day 15: Feature updates
    └── Day 30: Alumni offer (30% off)
    ↓
Ongoing Retention
    ├── Weekly tips
    ├── Feature announcements
    ├── Usage milestones
    └── Re-engagement offers
```

## 🔧 Implementation Components

### Sequence Engine

- `lead_magnet_sequence.py` — 7-email nurture flow
- `trial_activation.py` — 5-email trial onboarding
- `winback_sequence.py` — 3-email churn recovery
- `retention_sequences.py` — Ongoing engagement library

### Behavioral Triggers

- `event_listener.py` — Kafka consumer for sign-up, Trial start, post, payment
- `trigger_processor.py` — Rule evaluation (which sequence applies?)
- `sequence_orchestrator.py` — Schedule emails at optimal time

### Personalization

- `content_engine.py` — Variable substitution ({first_name}, {top_platform}, etc.)
- `subject_optimizer.py` — A/B test subject lines, auto-select winner
- `timing_optimizer.py` — Send time optimization per user timezone

### Analytics

- `funnel_tracker.py` — Lead → trial → paid conversion tracking
- `segment_performance.py` — Conversion rates by creator segment
- `cohort_analysis.py` — Retention by onboarding cohort

### Platform Integration

- Customer.io workspace setup
- Event schema definition
- Template management
- Compliance (GDPR/CAN-SPAM unsubscribe)

## 📊 Email Sequences

### Lead Magnet Nurture (7 emails, 14 days)

```
Day 0: Lead magnet delivery + welcome
Subject: "Welcome! Your free guide is attached → [Guide PDF]"

Day 1: Top mistake
Subject: "The #1 mistake 90% of creators make (and how to avoid it)"

Day 3: Case study
Subject: "How [Brand X] grew 50K followers in 30 days with ElevateIQ"

Day 5: Feature spotlight
Subject: "Why our AI content engine is different (3 reasons)"

Day 7: Social proof (3 testimonials + video)
Subject: "Watch what top creators say about ElevateIQ"

Day 10: Objection handling
Subject: "But I don't have time to learn a new tool... (yes you do)"

Day 14: Limited offer
Subject: "14-day free trial + onboarding call ⏰ Ends today"
```

### Trial Activation (5 emails, 7 days)

```
Day 0: Welcome checklist
Subject: "Your first post in 5 minutes — start here"

Day 1: Platform trigger (behavioral)
Subject: "You haven't connected TikTok yet — here's why you should"
(Only sent if no platform connected)

Day 3: Usage incentive (behavioral)
Subject: "Here's what users who post within 48 hours see..."

Day 5: Feature tutorial
Subject: "Master AI content creation in 10 minutes"

Day 7: Upgrade prompt
Subject: "Your trial ends in 7 days — here's how to keep going"
```

### Churn Win-Back (3 emails, 30 days)

```
Day 1: Exit survey + offer
Subject: "We noticed you left — what happened? 30% off to come back"

Day 15: Feature updates
Subject: "Things have changed since you left — new features inside"

Day 30: Alumni offer
Subject: "One last chance: 30% off first month back"
```

## 📊 Acceptance Criteria

- ✅ Lead magnet: ≥25% open rate on day 0
- ✅ Trial activation: +20% improvement in trial-to-paid vs no sequence
- ✅ Win-back recovery: ≥5% of churned users return
- ✅ GDPR compliance: Unsubscribe honored <24 hours
- ✅ Email rendering: Correct in Gmail, Outlook, Apple Mail
- ✅ Personalization: All variables populated correctly
- ✅ Subject A/B: Test runs automatically, winner deployed after 500 sends

## 🚀 API Endpoints (Draft)

```python
# Trigger sequence
POST /v1/marketing/sequences/trigger
{
  "creator_id": "uuid",
  "sequence": "lead_magnet"
}
→ { "status": "triggered", "first_email_time": "2026-03-12T17:00:00Z" }

# Get sequence status
GET /v1/marketing/creators/{creator_id}/sequence-status
→ {
    "current_sequence": "trial_activation",
    "emails_sent": 2,
    "next_email": "Day 3 usage incentive",
    "next_send_time": "2026-03-14T09:00:00Z"
  }

# Get funnel metrics
GET /v1/marketing/metrics/funnel
→ {
    "lead_magnet_starts": 1000,
    "lead_magnet_conversions": 120,
    "conversion_rate": 0.12,
    "trial_to_paid": 0.18,
    "avg_ltv": 450
  }
```

## 📈 Success Metrics

| Metric | Target |
|--------|--------|
| Lead Magnet Open Rate | ≥25% |
| Trial-to-Paid Lift | +20% |
| Win-back Recovery | ≥5% |
| GDPR Compliance | <24h |
| Email Rendering | 100% correct |
|Personalization Accuracy | 100% |
| Subject Line A/B | Automated |

## 🔐 Compliance

- **GDPR:** Unsubscribe honored <24h
- **CAN-SPAM:** Company address, unsubscribe link on all emails
- **Rendering:** Tested in Gmail, Outlook, Apple Mail, Mobile
- **Database:** Creator consent tracked for audit trail

## 📋 Dependencies

- #31 (Revenue engine) — for trial/paid tracking
- Customer.io API
- Kafka event stream

---

**Status:** Design Phase Complete | **Effort:** 3 days | **Priority:** P2

_Milestone 91 Component — Implementation Ready_
