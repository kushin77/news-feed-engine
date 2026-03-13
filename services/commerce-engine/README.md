# Commerce Engine - Social Commerce Integration

**Epic:** #64 — Social Commerce Integration — Direct Sales on Every Post (2-3x Monetization)

## 🛒 Purpose

Enables direct e-commerce on social media posts through platform-native shopping (TikTok Shop, Instagram Shopping, YouTube Shopping) with complete attribution and revenue tracking.

## 🏗️ Architecture

```
Creator Product Catalog
    ├── Uploaded inventory
    ├── Product metadata (title, price, image)
    └── Stock levels
    ↓
Platform Sync Engines
    ├── TikTok Shop (daily sync)
    ├── Instagram Shopping (feed generation)
    ├── YouTube Shopping (shelf cards)
    └── Amazon Associates (affiliate links)
    ↓
Post Creation
    ├── Creator tags products to post
    ├── Platform-optimized product cards appear
    ├── Affiliate deeplinks generated
    └── UTM parameters encoded
    ↓
Click Tracking
    ├── Redirect server captures clicks
    ├── User ID + post ID + product ID logged
    ├── Platform identified
    └── Timestamp recorded
    ↓
Purchase Attribution
    ├── Platform webhook: purchase confirmed
    ├── Join: click event + purchase event
    ├── Calculate: revenue per post, per product, per platform
    └── Update creator earnings
    ↓
Earnings Dashboard
    ├── Real-time earnings by platform
    ├── Top performing products
    ├── Conversion rates by placement
    └── Payout calculation
```

## 🔧 Implementation Components

### Platform Integration Services

- `tiktok_shop/` — Daily product catalog sync via TikTok API
- `instagram_shopping/` — Meta-formatted product feed generation
- `youtube_shopping/` — Product shelf cards + video tagging
- `affiliate_management/` — DeepLink generation + URL shortening
- `click_tracker/` — Fast redirect server (<50ms latency)
- `purchase_matcher.py` — Join clicks with platform webhooks
- `revenue_calculator.py` — Per-post/product earnings

### Affiliate Integrations

- Amazon Associates (5-10% commission)
- ShareASale (300+ merchants)
- Impact (performance tracking)
- Refersion (shopify integrations)

### Analytics & Dashboards

- Grafana board (real-time earnings)
- Performance by platform
- Top products
- Conversion funnels

## 📊 Acceptance Criteria

- ✅ TikTok Shop: Daily sync, live purchases on all posts
- ✅ Instagram Shopping: Product feed validated by Meta, shoppable carousel
- ✅ YouTube Shopping: Shelf cards appear on all videos
- ✅ Affiliate tracking: Zero lost click attribution (UTM parameters)
- ✅ Revenue reconciliation: ±5% vs platform-reported sales
- ✅ Product recommendations: Recommended products achieve ≥2% CTR
- ✅ Dashboard updates: Earnings updated within 24 hours of purchase
- ✅ Zero false attribution: Same click never double-counted

## 🚀 API Endpoints (Draft)

```python
# Sync product to TikTok Shop
POST /v1/commerce/products/sync/tiktok
{
  "product_id": "uuid",
  "title": "str",
  "price": 29.99,
  "image_url": "s3://...",
  "inventory": 100
}
→ { "tiktok_product_id": "str", "status": "synced" }

# Generate shoppable post
POST /v1/commerce/posts/{post_id}/shopping
{
  "products": ["product_id_1", "product_id_2"],
  "platforms": ["tiktok", "instagram", "youtube"]
}
→ { "shopping_enabled": true, "product_cards": [...]" }

# Get affiliate link for product
GET /v1/commerce/products/{product_id}/affiliate-link
→ { "link": "https://short.url/abc123", "commission_rate": 0.08 }

# Track click
POST /v1/commerce/clicks
{
  "post_id": "uuid",
  "product_id": "uuid",
  "platform": "tiktok",
  "user_id": "uuid"
}
→ { "click_id": "uuid", "timestamp": "2026-03-12T12:00:00Z" }

# Record purchase
POST /v1/commerce/purchases
{
  "click_id": "uuid",
  "order_value": 29.99,
  "platform": "tiktok"
}
→ { "revenue_credited": 29.99, "creator_share": 11.97 }

# Get earnings dashboard
GET /v1/commerce/dashboard/{creator_id}
→ {
    "total_revenue": 1250,
    "platform_breakdown": {
      "tiktok_shop": 800,
      "instagram": 300,
      "amazon": 150
    },
    "top_products": [...]
  }
```

## 📈 Revenue Model

Per 1M views (assuming 2% CTR):
- 20k clicks
- 1% conversion rate = 200 sales
- $50 average order value = $10k revenue
- Platform retains 40-60% = $4-6k per million views
- Creator retains 40% = $4k per million views

At 1B views/month: $4-6M monthly platform revenue

## 📊 Success Metrics

| Metric | Target |
|--------|--------|
| Daily Sync Accuracy | 100% |
| Live Shopping On Posts | 100% new posts |
| Click Attribution | 100% tracked |
| Revenue Reconciliation | ±5% |
| Product CTR | ≥2% |
| Dashboard Update Lag | <24h |
| Double-count Rate | 0% |

## 🔐 Safety & Compliance

- **No Double-Counting:** Deduplicate clicks across platforms
- **Revenue Reconciliation:** Platform APIs vs internal tracking ±5%
- **Affiliate Compliance:** Proper disclosure (FTC/AANA)
- **Fraud Detection:** Anomalous click patterns flagged
- **User Privacy:** GDPR-compliant tracking

## 📋 Dependencies

- #27 (Publishing) — for post integration
- #31 (Revenue tracking) — for billing
- #50 (Server-side attribution) — for click tracking

---

**Status:** Design Phase Complete | **Effort:** 4 days | **Priority:** P1

_Milestone 91 Component — Implementation Ready_
