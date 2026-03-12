# Milestone 88: ML Infrastructure Deployment Runbook

**Status**: Approved for Production Deployment  
**Version**: 1.0  
**Created**: March 12, 2026  
**Owner**: ML Platform Team

---

## Pre-Deployment Checklist

### Requirements Validation (DO THIS FIRST)
- [ ] **Kubernetes Cluster**: 1.27+ with GPU node pool
  - GPU Nodes: Minimum 2x T4 (or equivalent)
  - CPU Nodes: Minimum 20 CPU cores dedicated
  - Memory: Minimum 64GB total
  
- [ ] **Storage**: 
  - S3/GCS bucket for artifacts: 500GB minimum
  - PostgreSQL database: 50GB disk, single-node acceptable (upgrade pre-production)
  - Redis: 50G available for online features
  
- [ ] **Network**:
  - Ingress controller deployed (Nginx or Traefik)
  - DNS records configured (feast-api.internal, qdrant.internal, mlflow.internal)
  - Network policies enforced (namespace isolation)
  
- [ ] **Monitoring Stack**:
  - Prometheus + Grafana deployed
  - Alert manager configured
  - Log aggregation (ELK or Stackdriver)

### Access & Permissions
- [ ] Docker registry push access (GCR/DockerHub)
- [ ] Kubernetes cluster kubeconfig
- [ ] Service account with cluster-admin role (temporary, for setup)
- [ ] PostgreSQL admin password (secure, stored in Key Vault)
- [ ] Redis password (strong, random)
- [ ] Qdrant API key (strong, random)

### Data Preparation
- [ ] 2 years of trend history data (parquet format)
- [ ] 50K+ training samples for virality model
- [ ] Feature definitions validated (feature_definitions.py)
- [ ] Training data splits: 80% train, 10% val, 10% test

---

## Step 1: Provision Infrastructure (Day 1)

### 1.1 Deploy PostgreSQL
```bash
# Option A: Kubernetes StatefulSet (quick, not HA)
kubectl apply -f infrastructure/ml-stack/k8s/postgres-statefulset.yaml

# Option B: GCP Cloud SQL (recommended for production)
gcloud sql instances create ml-store-db \
  --tier=db-custom-2-8192 \
  --database-version=POSTGRES_15 \
  --region=us-central1

gcloud sql databases create mlflow --instance=ml-store-db
```

### 1.2 Deploy Redis
```bash
# Redis for Feast online store
kubectl apply -f infrastructure/ml-stack/k8s/redis-deployment.yaml

# Verify healthy
kubectl exec -it $(kubectl get po -l app=redis -o jsonpath='{.items[0].metadata.name}') -- redis-cli ping
# Expected output: PONG
```

### 1.3 Deploy Qdrant Vector DB
```bash
# Create namespace
kubectl create namespace ml-stack

# Deploy Qdrant
kubectl apply -f infrastructure/ml-stack/k8s/qdrant-deployment.yaml

# Verify
kubectl port-forward -n ml-stack svc/qdrant 6333:6333 &
curl -s http://localhost:6333/health | jq .status
# Expected: "ok"
```

### 1.4 Deploy MLflow Tracking Server
```bash
# Build MLflow image if needed
docker build -t mlflow:v2.1 infrastructure/ml-stack/mlflow/

# Deploy
kubectl apply -f infrastructure/ml-stack/k8s/mlflow-deployment.yaml

# Verify UI access
kubectl port-forward -n ml-stack svc/mlflow 5000:5000 &
curl -s http://localhost:5000 # Should return HTML
```

### 1.5 Deploy Feast Feature Store
```bash
# Build Feast API image
docker build -t feast-api:v0.36 infrastructure/ml-stack/feast/

# Deploy
kubectl apply -f infrastructure/ml-stack/k8s/feast-deployment.yaml

# Verify health
kubectl port-forward -n ml-stack svc/feast-api 6566:6566 &
curl -s http://localhost:6566/health | jq .status
# Expected: "healthy"
```

**Verification Command** (run after all deployments):
```bash
$ kubectl get po -n ml-stack
NAME                      READY   STATUS    RESTARTS   AGE
feast-api-xxxx            1/1     Running   0          5m
mlflow-xxxx               1/1     Running   0          5m
postgres-0                1/1     Running   0          10m
qdrant-0                  1/1     Running   0          8m
redis-0                   1/1     Running   0          7m
```

---

## Step 2: Initialize Feature Store (Day 2)

### 2.1 Register Feature Definitions
```bash
# SSH into Feast API pod
kubectl exec -it -n ml-stack $(kubectl get po -l app=feast-api -o jsonpath='{.items[0].metadata.name}') -- bash

# Inside pod:
cd /feast/repo
feast apply

# Output should list all 5 feature views:
# - user_features
# - content_features  
# - engagement_features
# - trend_features
# - creator_features
```

### 2.2 Upload Historical Data
```bash
# Prepare data in parquet format matching feature schemas
cd infrastructure/ml-stack/feast/data/
python scripts/prepare_features.py  # Converts CSV → Parquet

# Upload to offline store (BigQuery)
python scripts/upload_features_to_bq.py

# Verify data was uploaded
kubectl run -it --rm feast-client --image=feast-api:v0.36 -- python -c "
from feast import FeatureStore
fs = FeatureStore(repo_path='/feast/repo')
features = fs.get_historical_features(
    entity_df=pd.DataFrame({'user_id': ['user_1']}),
    features=['user_features:age_bracket']
)
print(features.to_df())
"
```

---

## Step 3: Train & Registry ML Models (Day 3-4)

### 3.1 Train Trend Forecasting Model
```bash
# Training script creates the model and registers in MLflow
cd services/processor
python processor/models/train_trend_forecasting.py \
  --data-path gs://elevatediq-ml/training_data/trends_24m.parquet \
  --model-output-dir ./models/trend_forecast \
  --mlflow-uri http://mlflow-service:5000

# Output:
# ✅  Model trained: train_auc_7d=0.92, test_auc_7d=0.89
# ✅  Registered in MLflow: models:/trend_forecast_7d/1
```

### 3.2 Train Virality Scoring Model
```bash
python processor/models/train_virality_scoring.py \
  --data-path gs://elevatediq-ml/training_data/virality_50k.parquet \
  --model-output-dir ./models/virality_scoring \
  --mlflow-uri http://mlflow-service:5000

# Output:
# ✅  Model trained: ensemble_auc=0.925
# ✅  Registered in MLflow:  models:/virality_ensemble/1
# ✅  Gate performance: precision=0.80, recall=0.81
```

### 3.3 Verify Models Registered
```bash
# Check MLflow registry
curl -s http://mlflow-service:5000/api/2.0/registered-models | jq .

# Expected output includes:
# - Models: trend_forecast_7d, trend_forecast_14d, virality_ensemble
# - Versions: 1 (stage: None)
# - Latest: stage Production (will be promoted after validation)
```

---

## Step 4: Deploy Models to KServe (Day 5)

### 4.1 Create KServe InferenceService for Trend Model
```bash
kubectl apply -f - <<EOF
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: trend-forecast-predictor
  namespace: ml-stack
spec:
  predictor:
    model:
      modelFormat:
        name: xgboost
      storageUri: gs://elevatediq-ml/models/trend_forecast/v1
      resources:
        limits:
          memory: 2Gi
          cpu: "1"
        requests:
          memory: 1Gi
          cpu: "500m"
  transformer:
    containers:
    - name: kserve-transformer
      image: feature-transformer:v1
      env:
      - name: FEAST_SERVER
        value: "feast-api-service:6566"
  canaryTrafficPercent: 5
EOF

# Verify deployment
kubectl get inferenceservice -n ml-stack trend-forecast-predictor
```

### 4.2 Create KServe InferenceService for Virality Model
```bash
kubectl apply -f infrastructure/ml-stack/k8s/virality-kserve.yaml

# Verify
kubectl get inferenceservice -n ml-stack virality-ensemble
```

### 4.3 Load Test Models
```bash
# Start port-forward
kubectl port-forward -n ml-stack svc/trend-forecast-predictor 8080:80 &
kubectl port-forward -n ml-stack svc/virality-ensemble 8081:80 &

# Load test with 100 QPS for 60 seconds
ghz --insecure \
  -d '{"signal_strength": [10, 20, 30, 40, 50]}' \
  -m '{}' \
  -n 6000 \
  -c 100 \
  -D "$(cat model_request.json)" \
  localhost:8080

# Expected results:
# Average latency: <150ms
# 99th percentile: <300ms
# Error rate: <0.1%
```

---

## Step 5: Setup Monitoring (Day 5)

### 5.1 Deploy Monitoring Dashboards
```bash
# Prometheus scrape config for ML stack
kubectl apply -f infrastructure/ml-stack/k8s/prometheus-scrape-config.yaml

# Import Grafana dashboards
curl -X POST http://grafana-service:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @infrastructure/ml-stack/grafana/dashboard-trend-forecast.json

curl -X POST http://grafana-service:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @infrastructure/ml-stack/grafana/dashboard-virality-gate.json
```

### 5.2 Configure Alerts
```bash
# Alert rules for model performance degradation
kubectl apply -f infrastructure/ml-stack/k8s/prometheus-alert-rules.yaml

# Expected alerts:
# - trend_forecast_model_auc_low: AUC < 0.83
# - virality_gate_precision_low: precision < 0.70
# - kserve_latency_high: p99 > 300ms
# - model_serving_unavailable: 0 replicas ready
```

### 5.3 Setup Logging
```bash
# Structured logging for model servingand prediction debugging
kubectl apply -f infrastructure/ml-stack/k8s/logging-config.yaml

# Verify logs are being collected
kubectl logs -n ml-stack -l app=trend-forecast-predictor --tail=50
```

---

## Step 6: Integration Testing (Day 6)

### 6.1 End-to-End Pipeline Test
```bash
# Test complete flow: features → model → prediction
python tests/test_e2e_ml_pipeline.py \
  --feast-uri http://feast-api-service:6566 \
  --trend-model-uri http://trend-forecast-predictor/v1/models/trend-forecast:predict \
  --virality-model-uri http://virality-ensemble/v1/models/virality:predict

# Expected output:
# ✅ Feast feature retrieval: 45ms
# ✅ Trend forecasting: 67ms
# ✅ Virality scoring: 82ms
# ✅ Total latency: 194ms
```

### 6.2 Model Validation
```bash
# Run test suite
pytest tests/test_ml_models.py -v --tb=short

# Expected output:
# test_trend_forecasting_model.py::test_feature_engineering_output_shape PASSED
# test_trend_forecasting_model.py::test_model_training_convergence PASSED
# test_virality_scoring_model.py::test_predict_score_range PASSED
# test_virality_scoring_model.py::test_quality_gate_blocking_low_scores PASSED
# ============== 12 passed in 2.3s ==============
```

### 6.3 Canary Validation
```bash
# Monitor canary (5% traffic) for 1 hour
kubectl logs -n ml-stack -l app=trend-forecast-predictor -f | grep ERROR

# Metrics to check:
# - Error rate: <0.1%
# - Latency p95: <300ms
# - Model predictions make sense (sanity checks)

# After validation, promote to 100%
kubectl patch inferenceservice trend-forecast-predictor \
  -n ml-stack \
  -p '{"spec": {"canaryTrafficPercent": 0}}'
```

---

## Post-Deployment

### Handoff Checklist
- [ ] OpsUpdate run books with team passwords
- [ ] Grafana dashboards configured + alerts working
- [ ] On-call schedule established
- [ ] Escalation procedures defined
- [ ] Rollback procedures tested
- [ ] Team training completed (30min hands-on workshop)

### Day 1 Operations
- Monitor all pods: `kubectl get po -n ml-stack -w`
- Check alert manager: http://alertmanager:9093
- Verify dashboards populate with live data
- Run hourly sanity checks (trends, virality scores making sense)

### Retraining Trigger
Models retrain automatically every Monday @ 2 AM UTC. Manual retraining:
```bash
# Trigger model retraining
python processor/models/retrain_all.py \
  --force \
  --data-from=2024-01-01
```

---

## Rollback Procedures

### Emergency Rollback (Complete System Failure)
```bash
# Kill all ML stack services
kubectl delete ns ml-stack

# Revert to previous version
git checkout HEAD~1
kubectl apply -f infrastructure/ml-stack/k8s/

# Estimated recovery time: 10-15 minutes
```

### Model Rollback (Bad Model Version)
```bash
# If trend_forecast_predictor has degraded performance:
kubectl set image deployment/trend-forecast-predictor \
  kserve-container=gcr.io/elevatediq/trend-forecast:v1.0

# The "v1.0" loads the previous model from MLflow
# Verify: http://trend-forecast-predictor/metrics (check model version)
```

---

## Troubleshooting Quick Reference

| Symptom | Cause | Fix |
|---------|-------|-----|
| Pod CrashLoopBackOff | Out of memory | `kubectl edit deployment POD_NAME`, increase memory limits |
| Model serving timeout | Feature store slow | `kubectl logs -n ml-stack feast-api`, check databases |
| High error rate | Input validation | Check logs: `kubectl logs POD_NAME`, verify feature ranges |
| Latency spike | Canary traffic | Check if routing to slow replica, fix with `canaryTrafficPercent: 0` |

---

## Support Contacts
- **Platform Team**: #ml-platform Slack
- **On-Call**: escalations@elevatediq.com
- **Incidents**: #incidents Slack channel
- **Docs**: https://wiki.internal/ml-infrastructure

---

**Deployment Owner**: [Your Name]  
**Deployment Date**: March XX, 2026  
**Estimated Duration**: 6 business days  
**Risk Level**: Medium (careful testing required, can rollback quickly)
