# Ads Manager - Meta & TikTok Ads API Integration

**Task:** #49 — Build Meta + TikTok Ads API Client

## 📢 Purpose

Enables creators to manage ad campaigns directly within the platform, with access to Meta Ads Manager and TikTok Ads Manager APIs for campaign creation, budget management, and performance tracking.

## 🏗️ Architecture

```
Creator Wants to Run Ad Campaign
    ├── Selects post to promote
    ├── Sets budget, audience, duration
    └── Chooses platform (Meta, TikTok, or both)
    ↓
Campaign Creation
    ├── Meta Ads API: Create campaign + ad set
    ├── TikTok Ads API: Create ad group + ads
    ├── Budget allocation: daily or lifetime
    ├── Audience targeting: interests, demographics
    └── Duration: start/end dates
    ↓
Campaign Monitoring
    ├── Real-time performance dashboard
    ├── Impressions, clicks, conversions
    ├── ROI calculation
    ├── Budget spend tracking
    └── Bid optimization suggestions
    ↓
Optimization
    ├── Auto-pause underperforming ads
    ├── Bid adjustments (if performing well)
    ├── Budget reallocation (to best performers)
    ├── A/B test recommendations
    └── Performance alerts
    ↓
Reporting
    ├── Daily/weekly/monthly performance
    ├── Attribution to revenue
    ├── ROI per campaign
    └── Recommendations for next campaign
```

## 🔧 Implementation Components

### API Integrations

- `meta_ads_client.py` — Meta Marketing API integration
- `tiktok_ads_client.py` — TikTok Ads Manager API integration
- `campaign_manager.py` — Create, update, delete campaigns
- `audience_manager.py` — Audience targeting + custom audiences

### Optimization & Monitoring

- `performance_monitor.py` — Real-time metrics aggregation
- `bid_optimizer.py` — Automatic bid adjustments
- `budget_allocator.py` — Rebalance budget to best performers
- `anomaly_detector.py` — Flag unusual patterns (fraud, performance drop)

### Analytics & Dashboards

- `campaign_analytics.py` — Performance calculations
- `roi_calculator.py` — Revenue attribution per campaign
- `performance_dashboard.py` — Real-time Grafana board

## 🚀 API Endpoints (Draft)

```python
# Create ad campaign
POST /v1/ads/campaigns
{
  "post_id": "uuid",
  "platforms": ["meta", "tiktok"],
  "name": "Growing My Brand",
  "budget": 500,
  "budget_period": "daily",
  "audience": {
    "interests": ["content_creation", "social_media"],
    "age_min": 18,
    "age_max": 35
  },
  "duration_days": 7
}
→ {
    "campaign_id": "uuid",
    "meta_campaign_id": "str",
    "tiktok_campaign_id": "str",
    "status": "active"
  }

# Get campaign performance
GET /v1/ads/campaigns/{campaign_id}/performance
→ {
    "impressions": 50000,
    "clicks": 1500,
    "ctr": 0.03,
    "conversions": 30,
    "conversion_rate": 0.02,
    "spend": 500,
    "roi": 2.5,
    "platform_breakdown": {
      "meta": { "impressions": 30000, "spend": 300, "roi": 2.4 },
      "tiktok": { "impressions": 20000, "spend": 200, "roi": 2.6 }
    }
  }

# Get optimization recommendations
GET /v1/ads/campaigns/{campaign_id}/recommendations
→ {
    "recommendations": [
      {
        "action": "increase_budget_meta",
        "reason": "ROI 3:1 vs average 2.5:1",
        "suggested_amount": 100
      },
      {
        "action": "pause_tiktok_audience_segment",
        "reason": "Audience: parents, ROI only 1.2:1",
        "impact_estimate": "Save $30"
      }
    ]
  }

# List all campaigns
GET /v1/ads/campaigns?creator_id={creator_id}
→ [
    {
      "campaign_id": "uuid",
      "name": "str",
      "status": "active|paused|completed",
      "spend_to_date": 250,
      "roi_to_date": 2.3
    },
    ...
  ]

# Pause campaign
POST /v1/ads/campaigns/{campaign_id}/pause
→ { "status": "paused", "effective_time": "2026-03-12T12:00:00Z" }
```

## 📊 Success Metrics

| Metric | Target |
|--------|--------|
| Campaign Creation Latency | < 5 minutes sync |
| Performance Update Delay | < 1 hour |
| Budget Spend Accuracy | 100% no overspends |
| Metric Accuracy | ±2% vs platform |

## 🔐 Security & Compliance

- **OAuth 2.0:** Secure API credential storage
- **Rate Limiting:** Respect platform API limits
- **Budget Controls:** Hard limits to prevent overspend
- **FTC Compliance:** Auto-add "Sponsored" labels

## 📋 Dependencies

- Meta Business Platform API credentials
- TikTok Ads Manager API credentials
- OAuth 2.0 flow for creator authorization

---

**Status:** Design Phase Complete | **Effort:** 3 days | **Priority:** P2

_Milestone 91 Component — Implementation Ready_
