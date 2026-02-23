# Appsmith Dashboard Setup Guide

This directory contains the Appsmith dashboard configuration files for the News Feed Engine admin interface.

## Files Overview

| File | Description |
|------|-------------|
| `dashboard.json` | Main application export with datasources and queries |
| `widgets.json` | Dashboard, Creators, and Content page widgets |
| `widgets-extended.json` | White-Label, Settings, and Video Summaries widgets |

## Quick Setup

### 1. Configure Environment Variables

Set the following in your Appsmith environment configuration:

```javascript
// In Appsmith Settings > Instance Settings > Environment Variables
NEWS_FEED_API_URL=https://news-feed.elevatediq.com  // or your API endpoint
PROMETHEUS_BASE_URL=https://prometheus.your-domain.example   // e.g., https://monitoring.example.com/prometheus
GRAFANA_DASHBOARD_URL=https://grafana.your-domain.example/d/processor-uid/news-feed-processor?orgId=1&kiosk
```bash

### 2. Import Dashboard

1. Open Appsmith and create a new application
2. Go to **Settings > Import**
3. Upload `dashboard.json`
4. The application will create:
   - NewsFeedAPI datasource
   - PrometheusAPI datasource
   - All queries (GetDashboardStats, GetCreators, etc.)
   - Page structure with layouts

### 3. Configure Authentication

The dashboard uses JWT tokens stored in `appsmith.store.adminToken`. Configure authentication:

## Option A: Manual Token Entry

```javascript
// Add a login form that calls your auth endpoint and stores token
storeValue('adminToken', response.token)
storeValue('tenantId', response.tenant_id)
```bash

## Option B: Appsmith SSO Integration

```javascript
// If using Appsmith Enterprise with SSO, token is passed via:
appsmith.user.idToken
```bash

### 4. Add Widgets

For each page, copy the widget configurations from `widgets.json` and `widgets-extended.json`:

#### Dashboard Page

Copy widgets from `widgets.json > Dashboard`:

- `StatsContainer` - 4-column stats display
- `ContentChart` - Area chart for trends
- `RecentContentTable` - Latest content list
- `ProcessingStatus` - Queue progress

#### Creators Page

Copy widgets from `widgets.json > Creators`:

- `CreatorsFilters` - Status and platform filters
- `CreatorsTable` - Main table with CRUD
- `AddCreatorModal` - New creator form
- `EditCreatorModal` - Edit/delete modal

#### Content Page

Copy widgets from `widgets.json > Content`:

- `ContentFilters` - Multi-filter bar
- `ContentTable` - Content list with moderation
- `ContentReviewModal` - Review and status update

#### White-Label Page

Copy widgets from `widgets-extended.json > WhiteLabel`:

- `TenantSelector` - Tenant dropdown
- `BrandingConfig` - Colors, logos, CSS
- `FeatureToggles` - Feature flags
- `ContentFiltersConfig` - Category and keyword filters

#### Settings Page

Copy widgets from `widgets-extended.json > Settings`:

- `GeneralSettings` - Retention, moderation
- `AISettings` - Model, temperature, batch size
- `IntegrationSettings` - Platform toggles

#### Observability Page

Copy widgets from `widgets.json > Observability`:

- `ObsStats` - Live status for Engine/Processor and exporters down count; P95 processing seconds
- `ErrorRateChart` - 6h error-rate time series from recording rule
- `TargetsTable` - Prometheus active targets with health and last scrape details
- `GrafanaPanel` - Optional embedded Grafana dashboard/panel (requires Grafana to allow embedding)

Queries used (auto-created in `dashboard.json`):

- `GetProcessorUp`, `GetEngineUp` — up metrics for service health
- `GetExportersDown` — number of infra exporter targets currently down
- `GetErrorRate` and `GetErrorRateTS` — processor error rate (instant + range)
- `GetProcessingP95` — P95 processing latency
- `GetTargets` — Prometheus active targets listing

Notes:

- Ensure Prometheus and Grafana endpoints are reachable from the Appsmith instance and allow CORS for the Appsmith origin.
- If Grafana requires authentication, prefer signed viewer links, anonymous view, or reverse proxy injecting auth. Set `GRAFANA_DASHBOARD_URL` accordingly.

#### Video Summaries Page

Copy widgets from `widgets-extended.json > VideoSummaries`:

- `VideoFilters` - Status filter
- `VideoSummariesTable` - Summary list
- `VideoSummaryModal` - Video player with summary tabs

## API Endpoints Used

| Query | Method | Endpoint | Description |
|-------|--------|----------|-------------|
| GetDashboardStats | GET | /admin/stats | Dashboard statistics |
| GetCreators | GET | /creators | List creators with pagination |
| CreateCreator | POST | /creators | Add new creator |
| UpdateCreator | PUT | /creators/{id} | Update creator |
| DeleteCreator | DELETE | /creators/{id} | Remove creator |
| GetContent | GET | /content | List content with filters |
| UpdateContentStatus | PATCH | /content/{id}/status | Moderate content |
| GetWhiteLabelConfigs | GET | /admin/whitelabel/configs | List tenant configs |
| CreateWhiteLabelConfig | POST | /admin/whitelabel/configs | Create tenant |
| GetSettings | GET | /admin/config | Get system settings |
| UpdateSettings | PUT | /admin/config | Update settings |
| GetProcessingQueue | GET | /admin/processing/queue | Queue status |
| GetVideoSummaries | GET | /videos | List video summaries |
| RegenerateVideoSummary | POST | /videos/{id}/regenerate | Re-process video |

## Customization

### Adding New Categories

Update the `CategoryFilter` widget options in `widgets.json`:

```javascript
{
  "options": [
    { "label": "All Categories", "value": "" },
    { "label": "Technology", "value": "technology" },
    // Add your categories here
    { "label": "Custom Category", "value": "custom" }
  ]
}
```bash

### Custom Theme

Modify the theme section in `dashboard.json`:

```javascript
"theme": {
  "colors": {
    "primaryColor": "#YOUR_COLOR",
    "backgroundColor": "#F8F9FA"
  },
  "borderRadius": {
    "appBorderRadius": "6px"
  },
  "fontFamily": {
    "appFont": "Inter"
  }
}
```bash

### Adding Custom Queries

1. Add query definition to `dashboard.json > queries`
2. Reference in widget using `{{YourQueryName.data}}`

## Multi-Tenant Setup

The dashboard supports multi-tenant mode:

1. Set `X-Tenant-ID` header in datasource configuration
2. Use `TenantSelector` to switch contexts
3. All queries automatically scope to selected tenant

## Troubleshooting

### Query Errors

Check browser console for detailed error messages. Common issues:

- Invalid JWT token - re-authenticate
- CORS errors - ensure API allows Appsmith origin
- 404 errors - verify API URL configuration
- Prometheus 403/CORS - enable CORS or proxy Prometheus through a gateway with correct headers

### Widget Not Updating

Run queries manually to refresh:

```javascript
GetCreators.run()
```bash

### Date Format Issues

Ensure date columns use correct format:

```javascript
"inputFormat": "YYYY-MM-DDTHH:mm:ss",
"outputFormat": "MMM DD, HH:mm"
```bash

## Support

For issues with:

- **Appsmith platform**: <https://docs.appsmith.com>
- **News Feed Engine API**: Check `/health` endpoint
- **Observability APIs**: Prometheus `/api/v1/query`, `/api/v1/query_range`, `/api/v1/targets`; Grafana share links
- **Dashboard configuration**: Review this README
