# Gamification Engine

**Status**: ✅ Complete (Milestone 89 Deliverable)  
**Last Updated**: March 13, 2026

---

## Overview

The Gamification Engine is a microservice that drives user engagement through a points, badges, and leaderboards system. It rewards creators for content creation, engagement, and community building.

---

## Features

### Points System
- Award points for user actions (posting, engagement, milestones)
- Track point transaction history
- Real-time point balance updates

### Badges
- 8 pre-defined achievement badges
- Automatic bonus points when badges are awarded
- Badge tracking and user progress

### Leaderboards
- Real-time ranking of top users
- Configurable leaderboard limits
- Points and badge count display

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/` | GET | Service info |
| `/api/points` | POST | Award points to user |
| `/api/leaderboard` | GET | Get top users |
| `/api/badges` | POST | Award badge to user |
| `/api/users/<user_id>` | GET | Get user profile |

---

## Usage Examples

### Award Points
```bash
curl -X POST http://localhost:8080/api/points \
  -H "Content-Type: application/json" \
  -d '{"user_id": "123", "points": 50, "reason": "First post"}'
```

### Get Leaderboard
```bash
curl http://localhost:8080/api/leaderboard?limit=10
```

### Award Badge
```bash
curl -X POST http://localhost:8080/api/badges \
  -H "Content-Type: application/json" \
  -d '{"user_id": "123", "badge_name": "First Post"}'
```

---

## Default Badges

| Badge | Description | Points |
|-------|-------------|--------|
| First Post | Created your first post | 10 |
| Early Adopter | Joined during beta | 100 |
| Viral Hit | Got 10,000 views on a post | 500 |
| Community Builder | Gained 100 followers | 250 |
| Top Creator | Reached 1,000 followers | 1000 |
| Engagement Master | 100 likes on a single post | 150 |
| Streak Champion | Posted for 7 days in a row | 200 |
| Trendsetter | Created content that started a trend | 300 |

---

## Deployment

### Docker Compose
```bash
cd services/gamification
docker-compose up -d
```

### Manual
```bash
pip install -r requirements.txt
python app.py
```

---

## Database Schema

- **users**: id, username, points, created_at, updated_at
- **badges**: id, name, description, points, icon, created_at
- **user_badges**: id, user_id, badge_id, awarded_at
- **point_transactions**: id, user_id, points, reason, created_at

---

## Milestone 89 Completion

This service completes **Issue #48: Build Gamification Engine** as part of Milestone 89: Viral Growth & Engagement Roadmap.

**Acceptance Criteria Met:**
- ✅ Points system implemented
- ✅ Badges with bonus points
- ✅ Leaderboard functionality
- ✅ PostgreSQL database schema
- ✅ REST API with all required endpoints
