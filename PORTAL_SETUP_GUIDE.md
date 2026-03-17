# 🚀 News Feed Engine - Complete Portal Setup Guide

**Status**: Portal Ready for Development  
**Last Updated**: March 17, 2026

---

## ✅ Services Running

### Frontend Portal
- **Status**: ✅ **RUNNING**
- **URL**: http://localhost:5173
- **Framework**: React 18 with Vite
- **Port**: 5173
- **Commands**:
  ```bash
  cd services/frontend
  npm run dev
  ```

### Backend Services
- **News Feed Engine (Go)**: Port 8082 (requires PostgreSQL)
- **Processor (Python)**: Processing ML pipeline
- **MLflow Server**: Model registry and experiment tracking

### Development Infrastructure
- **MLflow**: http://localhost:5000
- **Prometheus**: Metrics/monitoring
- **Grafana**: Dashboard visualization

---

## 🎯 Quick Start (Development Mode)

### 1️⃣ Start Frontend Portal
```bash
cd services/frontend
npm run dev
```
✅ Access: http://localhost:5173

### 2️⃣ Start MLflow Server (for ML pipeline)
```bash
cd services/processor
mlflow ui --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlruns
```
✅ Access: http://localhost:5000

### 3️⃣ Optional: Start Go Backend (requires PostgreSQL)
```bash
cd services/news-feed-engine

# Set environment for development
export ENVIRONMENT=development
export DATABASE_URL="postgres://user:password@localhost:5432/news_feed"
export SKIP_KAFKA_INIT=true

# Run
./bin/news-feed-engine.exe
```
✅ Access: http://localhost:8082

---

## 📊 Portal Features Available

### Without Backend Database
- ✅ Frontend UI components
- ✅ React state management (Zustand)
- ✅ TypeScript type safety  
- ✅ Tailwind CSS styling
- ✅ Responsive design
- ✅ Client-side validation
- ✅ Local data mocking

### With MLflow
- ✅ ML model tracking
- ✅ Experiment management
- ✅ Model versioning
- ✅ Metrics visualization

### Full Stack (with PostgreSQL + Go Backend)
- ✅ Real data persistence
- ✅ REST API endpoints
- ✅ Database queries
- ✅ Kafka event streaming
- ✅ Multi-platform integrations

---

## 🛠️ Available Commands

### Frontend
```bash
cd services/frontend

npm run dev          # Start development server (port 5173)
npm run build        # Production build
npm run lint         # ESLint check
npm run lint:fix     # Fix linting issues
npm run type-check   # TypeScript validation
npm run test         # Run tests with Vitest
npm run faang-check  # Full FAANG quality check (lint + type + coverage)
```

### Backend (Go)
```bash
cd services/news-feed-engine

make build           # Build all (Go + Python)
make build-go        # Build Go service
make test            # Run all tests
make test-go         # Go tests only
make lint            # Lint check
```

### Processor (Python ML Pipeline)
```bash
cd services/processor

pytest tests/                    # Run all tests
python train_local_models.py    # Train ML models locally
mlflow server --backend-store-uri sqlite:///mlflow.db  # Start MLflow UI
```

---

## 🔍 Testing Portal Connectivity

### Check Frontend
```bash
curl http://localhost:5173
```

### Check Backend Health
```bash
curl http://localhost:8082/health
```

### Check MLflow
```bash
curl http://localhost:5000/api/2.0/mlflow/experiments/list
```

---

## 📝 Portal Pages Structure

```
/                          # Home page
/feed                      # News feed
/analytics                 # Analytics dashboard
/settings                  # User settings
/integrations              # Platform integrations
/ai-insights               # AI predictions & trends
/content-library           # Media library
/publishing                # Publishing controls
```

---

## 🚨 Common Issues & Solutions

### Issue: Frontend won't start
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Issue: Port already in use
```bash
# Find process using port
lsof -i :5173

# Kill process
kill -9 <PID>
```

### Issue: Backend database connection fails
```bash
# Set development mode to skip database
export ENVIRONMENT=development
export SKIP_KAFKA_INIT=true
./bin/news-feed-engine.exe
```

### Issue: MLflow models not showing
```bash
# Check MLflow backend
cd services/processor
mlflow server --backend-store-uri sqlite:///mlflow.db
# Access: http://localhost:5000
```

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│             News Feed Engine Portal                      │
└─────────────────────────────────────────────────────────┘
         │                │                    │
    Frontend          MLflow            Backend API
   (Vite/React)      (Model Reg)      (Go/PostgreSQL)
  localhost:5173   localhost:5000    localhost:8082
         │                │                    │
         └────────────────┴────────────────────┘
                     Network Layer
                (HTTP/REST/WebSocket)
                     │
         ┌───────────┴──────────┐
         │                      │
    State Store          Database
    (Zustand)          (PostgreSQL)
```

---

## ✨ Next Steps

### Phase 1: Frontend Validation
- [ ] Portal loads on http://localhost:5173
- [ ] UI components render correctly
- [ ] Navigation works
- [ ] Responsive design validated

### Phase 2: Backend Integration
- [ ] Set up PostgreSQL locally
- [ ] Configure database credentials
- [ ] Start Go service on port 8082
- [ ] Test API endpoints

### Phase 3: ML Pipeline
- [ ] Run MLflow server
- [ ] View trained models
- [ ] Test model inference
- [ ] Integrate predictions into UI

### Phase 4: End-to-End Testing
- [ ] Frontend ↔ API ↔ Database flow
- [ ] User authentication
- [ ] Content publishing
- [ ] Analytics tracking

---

## 📞 Support

For issues or questions:
1. Check logs in `/var/log/` (if running in containers)
2. Review error messages in terminal output
3. Consult architecture docs in `docs/` folder
4. Check GitHub issues: https://github.com/kushin77/news-feed-engine/issues

---

## 🎉 You're Ready!

**Next Action**: Open http://localhost:5173 in your browser and start exploring the portal!

```bash
# Quick start command (all in one)
cd services/frontend && npm run dev &
cd services/processor && mlflow ui &
```

Enjoy building! 🚀
