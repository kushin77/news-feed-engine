# Attribution Engine - Server-Side Event Tracking & Purchase Attribution

**Task:** #50 — Build Server-Side Attribution

## 📊 Purpose

Tracks all user actions (post views, clicks, purchases) with 99%+ accuracy for complete revenue attribution across all monetization channels.

## 🏗️ Architecture

```
Post Published
    ├── Add tracking pixel + deep links
    └── Generate unique post ID
    ↓
User Sees Post
    ├── Pixel fires: POST /events/view
    ├── Event logged: { user_id, post_id, platform, timestamp }
    ├── Redis: Increment post view counter
    └── Kafka: Stream event for analytics
    ↓
User Clicks Link (Commerce/Affiliate/Ads)
    ├── Redirect through tracking URL
    ├── Server logs: { user_id, post_id, link_id, timestamp, referrer }
    ├── Redis: Increment click counter
    ├── Return: Destination URL (Amazon, course, etc.)
    └── Kafka: Stream to attribution engine
    ↓
Purchase Confirmation (Platform Webhook)
    ├── TikTok Shop: purchase confirmed
    ├── Amazon Associates: referral conversion
    ├── Stripe: payment successful
    ├── Server receives webhook
    ├── Join: previous click event + purchase event
    ├── Calculate: revenue, commission, creator share
    └── Update: Billing engine + creator dashboard
    ↓
Revenue Attribution Complete
    ├── Track: post_id → clicks → purchases → revenue
    ├── Update: creator earnings
    ├── Update: platform commission
    └── Archive: for audit trail
```

## 🔧 Implementation Components

### Event Tracking Server

- `pixel_server.go` — Fast view tracking (<50ms latency)
- `redirect_server.go` — Click tracking + destination redirect
- `event_store.py` — PostgreSQL event persistence
- `event_deduplication.py` — Prevent double-counting

### Webhook Handlers

- `tiktok_webhook.py` — TikTok Shop purchase confirmation
- `amazon_webhook.py` — Amazon Associates referral conversion
- `stripe_webhook.py` — Payment successful
- `instagram_webhook.py` — Instagram Shopping purchase

### Attribution Engine

- `click_purchase_matcher.py` — Join clicks + purchases
- `revenue_calculator.py` — Calculate creator share, platform commission
- `segment_attribution.py` — Attribute revenue to segment features

### Analytics & Monitoring

- `ClickHouse` — Real-time analytics queries
- `Grafana` — Attribution dashboard
- `alerting` — Anomaly detection (unusual click patterns, fraud)

## 📊 Acceptance Criteria

- ✅ Latency: <50ms per event
- ✅ Accuracy: 99%+ events tracked
- ✅ No data loss: 100% event persistence
- ✅ Duplicate detection: Zero double-counting
- ✅ Revenue reconciliation: ±5% with platform-reported

## 🚀 API Endpoints (Draft)

```python
# Fire view pixel
POST /events/view
{
  "post_id": "uuid",
  "user_id": "uuid",
  "platform": "tiktok"
}
→ { "status": "recorded", "timestamp": "2026-03-12T12:00:00Z" }

# Track click (redirect)
POST /click/{click_token}
{ "destination": "https://amazon.com/...?tracking_id=..." }
Headers: User-Agent, Referer
→ 302 redirect to destination

# Webhook: Purchase confirmed
POST /webhooks/tiktok/purchase
{
  "order_id": "str",
  "product_id": "uuid",
  "revenue": 29.99,
  "user_id": "uuid"
}
→ { "status": "processed", "revenue_credited": 29.99 }

# Get attribution report
GET /v1/attribution/reports/daily
→ {
    "date": "2026-03-12",
    "total_views": 50000,
    "total_clicks": 1000,
    "ctr": 0.02,
    "conversions": 10,
    "conversion_rate": 0.01,
    "revenue": 500,
    "creator_share": 300,
    "platform_commission": 200
  }

# Get post attribution
GET /v1/attribution/posts/{post_id}
→ {
    "views": 5000,
    "clicks": 100,
    "conversions": 1,
    "revenue": 50,
    "ctr": 0.02,
    "conversion_rate": 0.01,
    "top_link": "Amazon Associates"
  }
```

## 📈 Success Metrics

| Metric | Target |
|--------|--------|
| Event Latency | <50ms |
| Tracking Accuracy | 99%+ |
| Data Persistence | 100% |
| Double-count Rate | 0% |
| Revenue Reconciliation | ±5% |

## 🔐 Privacy & Fraud Prevention

- **Privacy:** GDPR-compliant tracking (no PII stored)
- **Fraud Detection:** Anomalous click patterns flagged
- **Click Verification:** User-agent, referrer validation
- **Webhook Verification:** Stripe/TikTok signatures validated

## 📋 Dependencies

- PostgreSQL for event storage
- ClickHouse for analytics
- Kafka for real-time streaming
- Stripe/TikTok/Amazon webhook endpoints

---

**Status:** Design Phase Complete | **Effort:** 4 days | **Priority:** P2

_Milestone 91 Component — Implementation Ready_
