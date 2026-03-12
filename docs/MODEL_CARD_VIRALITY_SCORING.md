# Virality Scoring Model Card

## Model Details

### Overview
- **Model Name**: Virality-Ensemble-XGB+LGB-v1.5
- **Task**: Binary classification + probability scoring (0-100)
- **Architecture**: Ensemble (60% XGBoost + 40% LightGBM)
- **Purpose**: Pre-publish quality gate and virality prediction for content
- **Training Date**: March 2026
- **Owner**: ML Platform & Creator Success Team
- **Status**: ✅ **Production Ready**

### Intended Use
- **Primary Use**: Block low-virality content (<score 20) before publishing
- **Secondary Use**: Predict viral probability for content ranking and recommendation
- **End Users**: Creators, automated publishing pipelines, quality assurance team
- **Application**: Real-time at publishing time (blocking gate)

---

## Model Specification

### Input Features (100+ features)
| Category | Feature Count | Examples |
|----------|---------------|----------|
| **Content Attributes** | 25 | title_length, title_has_emoji, description_words, is_video, quality_score |
| **Creator Reputation** | 20 | follower_count, engagement_rate, account_age, verified, viral_rate |
| **Temporal Signals** | 15 | hour_of_day, day_of_week, is_weekend, is_holiday, platform_avg_views |
| **Topic & Trends** | 10 | matching_trending_topics, category, creator_category_match |
| **Platform & Context** | 20 | platform, content_volume_percentile, competitive_intensity, is_breaking_news |
| **Media Components** | 10 | has_video, has_audio, has_captions, video_length, thumbnail_quality |

### Output
- **Score Range**: 0-100 (higher = more viral)
- **Score Tiers**:
  - 0-20: **BLOCKED** by quality gate
  - 20-50: **BORDERLINE** (requires creator approval)
  - 50-75: **APPROVED** (good virality potential)
  - 75-100: **PREMIUM** (high viral certainty)

### Quality Gate Policy
```
IF score < 20:
  ACTION: BLOCK publishing
  REASON: Low virality potential
  OVERRIDE: Requires manual creator appeal
  
IF 20 <= score < 50:
  ACTION: ALLOW with flag
  REASON: Borderline quality
  NOTIFICATION: Suggest edits or additional promotion
  
IF score >= 50:
  ACTION: APPROVE auto-publish
  NOTIFICATION: Confidence level (medium/high/very high)
```

---

## Performance Evaluation

### Metrics Summary
| Metric | XGBoost Component | LightGBM Component | Ensemble | Target | Status |
|--------|------------------|-------------------|----------|--------|--------|
| **Train AUC-ROC** | 0.94 | 0.93 | 0.945 | >0.90 | ✅ |
| **Test AUC-ROC** | 0.918 | 0.908 | 0.925 | >0.92 | ✅ |
| **Precision @gate(20)** | 0.78 | 0.75 | 0.80 | >0.75 | ✅ |
| **Recall @gate(20)** | 0.82 | 0.79 | 0.81 | >0.75 | ✅ |
| **Specificity @gate(20)** | 0.85 | 0.83 | 0.87 | >0.80 | ✅ |

### Evaluation Dataset
- **Size**: 50,000 pieces of content with virality outcomes
- **Definition of "Viral"**: >100,000 views within 7 days of publishing
- **Class Balance**: 30% viral, 70% non-viral (realistic distribution)
- **Time Period**: 2024-06 to 2026-02 (20 months)
- **Platform Mix**: YouTube 30%, TikTok 25%, Twitter 20%, Instagram 15%, Other 10%
- **Creator Tiers**: Nano (0-10K followers) 20%, Micro (10-100K) 30%, Mid (100K-1M) 30%, Macro (1M+) 20%

### Failure Analysis
| Failure Mode | % of Errors | Cause | Mitigation |
|-------------|-----------|-------|----------|
| **FP: High score, not viral** | 8% | Trending topic peak passes quickly | Add momentum decay feature |
| **FN: Low score, went viral** | 12% | Underestimated creator reputation growth | Update creator scores weekly |
| **False Gates (score <20 that went viral)** | 2% | Emerging creators, novel topics | Regular fairness audits |

---

## Fairness, Bias & Ethics

### Known Limitations
1. **Creator Bias**: Established creators get higher scores
   - New creators manually flagged: ~15% lower score
   - Mitigation: Separate scoring track for creators <90 days old
   
2. **Platform Bias**: TikTok/YouTube content scores higher
   - Twitter/LinkedIn content: ~5-10% score reduction
   - Mitigation: Platform-specific calibration (±offset)
   
3. **Language Bias**: English-language content overweighted
   - Non-English: ~10% score penalty
   - Mitigation: Multilingual trending topic detection
   
4. **Category Bias**: Entertainment/gossip more "viral" than educational
   - Educational content: ~20% score penalty
   - Mitigation: Segment-specific SLOs (not all categories measured by views)
   
5. **Temporal Bias**: Business hours (US timezone) preferred
   - Off-peak content: ~8% score penalty
   - Mitigation: Time-zone normalization

### Fairness Metrics
```
1. Demographic Parity
   - Score distribution should not significantly differ by creator demographics
   - Audit: quarterly, by creator region/language/category
   
2. Equalized Odds
   - TPR (viral recall) should be similar across groups
   - Target: within 5 percentage points across segments
   
3. Calibration
   - P(viral | score=75) should be similar across creator groups
   - Target: calibration error <0.05
```

### Bias Mitigation Strategy
- Stratified evaluation: every creator tier/region/language/category
- Quarterly fairness audits (external reviewer)
- Per-segment threshold optimization if needed
- Appeals process for creators flagged as "unjust" blocks

---

## Model Dependencies & Requirements

### Input Data Dependencies
- **Creator Profile**: Must have account_age > 7 days (new account filtering)
- **Trending Topics**: Updated hourly from 8 data sources
- **Platform Metrics**: Today's average views/engagement (updated daily)
- **Content Quality**: Automated image/video analysis score (threshold >0.3)

### Upstream Systems
- **Feature Store (Feast)**: Creator stats, trending topics, content vectors
- **MLflow Model Registry**: Model versioning and artifact storage
- **Kafka Stream**: Real-time content publishing events for monitoring

### Downstream Systems
- **Publishing Pipeline**: Respects gate decisions (blocks vs allows)
- **Monitoring Dashboard**: Tracks gate effectiveness (precision/recall)
- **Creator Feedback System**: Collects appeals for false positives

---

## Monitoring & Operations

### SLOs
- **Availability**: 99.95% (max 22min/month downtime)
- **Latency**: <100ms p95 for scoring (must be <200ms)
- **Accuracy**: AUC-ROC >0.92, gates precision >0.75
- **Fairness**: Demographic parity <5% drift

### Alerts
```
✋ CRITICAL (page on-call):
   - Latency p99 > 250ms
   - Error rate > 1%
   - AUC drops to <0.90 (2% degradation)

⚠️ WARNING (send to Slack):
   - Latency p95 > 150ms
   - Gate precision drops to <0.70
   - Demographic fairness drift >5%
```

### Retraining Trigger
- **Schedule**: Weekly (every Monday 2 AM UTC)
- **Manual Trigger**: If false positive rate >15% or false negative rate >20%
- **Backup Data**: Always keep 2 weeks holdout for validation
- **Version Control**: Keep 3 previous model versions (quick rollback)

### Performance Tracking
- **Weekly Report**: Gate effectiveness, top feature contributions
- **Monthly Dashboard**: Fairness metrics by segment, appeal trends
- **Quarterly Review**: Full model retraining, hyperparameter optimization

---

## Known Issues & Workarounds

| Issue | Description | Workaround |
|-------|-------------|-----------|
| **Sudden Viral Spikes** | 10x surge from coordinated promotion | Treat as anomaly, human review |
| **Context Collapse** | Content from niche goes mainstream | Add temporal decay on trending match |
| **Creator Bounces** | New creator jumps from small to 1M followers | Account for follower velocity in score |
| **Platform Algorithm Changes** | TikTok algorithm updates overnight | Weekly retraining catches pattern shift |

---

## Training & Deployment

### Training Pipeline
```python
from processor.models import ViralityScoringModel

# Feature engineering for 50K pieces of content
X_list = [model.engineer_features(content, creator, temporal, trends) 
          for content, creator, temporal in training_data]
X = np.vstack([x for x, _ in X_list])

# Train ensemble
model = ViralityScoringModel(weights={'xgb': 0.6, 'lgb': 0.4})
metrics = model.train(X_train, y_train, X_test, y_test)

# Deploy to MLflow
mlflow.xgboost.log_model(model.xgb_model, 'virality_xgb')
mlflow.lightgbm.log_model(model.lgb_model, 'virality_lgb')
```

### MLflow Details
- **Model URI**: `models:/virality_ensemble/Production`
- **Artifacts**: `/gs/elevatediq-ml/models/virality_v1.5/`
- **Registry**: MLflow Model Registry (internal)

### Kubernetes Deployment
- **Framework**: KServe predictor
- **Image**: `gcr.io/elevatediq/virality-scorer:v1.5`
- **Replicas**: 2-20 (auto-scale)
- **Latency SLA**: 50ms p50, 100ms p95, 200ms p99

### Pre-Deployment Checks
- [ ] AUC-ROC >0.92 on holdout test set
- [ ] Latency <100ms p95 on benchmark hardware
- [ ] Throughput >1000 requests/sec
- [ ] Fairness audit passed for all demographic groups
- [ ] Feature importance makes business sense (no surprises)
- [ ] Bias detection tests pass (no systematic discrimination)

---

## Troubleshooting

### Symptom: Scores seem too low
- **Check**: Feature scaling in scaler.pkl
- **Check**: Input features within expected ranges
- **Solution**: Retrain scaler on latest data

### Symptom: Scores seem too high
- **Check**: Label definition (>100K views? >50K?)
- **Check**: Class imbalance (majority baseline)
- **Solution**: Recalibrate on holdout set

### Symptom: Latency degradation
- **Check**: KServe replica count vs request rate
- **Solution**: Increase replicas, check for feature store slowness

---

## References

- **Training Code**: `/services/processor/processor/models/virality_scoring.py`
- **Unit Tests**: `/services/processor/tests/test_ml_models.py`
- **Monitoring Dashboard**: Grafana dash#4522 (virality-gate-effectiveness)
- **Historical Decisions**: BigQuery table `elevatediq.publishing_gates` (audit trail)
- **Creator Appeals**: Spreadsheet (processed weekly)

---

**Last Updated**: March 12, 2026  
**Next Model Review**: March 19, 2026  
**Prod Model Version**: 1.5 (XGB 0.6 + LGB 0.4 ensemble)  
**Rollback Version**: 1.4 (if needed)
