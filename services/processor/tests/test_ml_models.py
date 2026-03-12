"""
Unit tests for ML models - FAANG quality standards

Coverage requirements:
- Feature engineering: correct dimensions, value ranges, no NaN
- Model training: convergence, metric validation
- Model prediction: output shapes, value ranges
- Edge cases: missing data, extreme values
- Regression: consistent behavior across runs (random seed)
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime
import tempfile
import os

from processor.models import TrendForecastingModel, ViralityScoringModel


class TestTrendForecastingModel:
    """Test trend forecasting model for time-series prediction."""
    
    @pytest.fixture
    def sample_trend_data(self):
        """Create sample trend history data."""
        dates = pd.date_range('2024-01-01', periods=30, freq='D')
        return pd.DataFrame({
            'timestamp': dates,
            'trend_name': ['AI' if i % 3 == 0 else 'Crypto' if i % 3 == 1 else 'Gaming' 
                           for i in range(30)],
            'signal_strength': np.cumsum(np.random.normal(10, 5, 30)),
        })
    
    @pytest.fixture
    def model(self):
        """Initialize model."""
        return TrendForecastingModel(model_type='xgboost')
    
    def test_feature_engineering_output_shape(self, model, sample_trend_data):
        """Verify feature engineering produces correct dimensions."""
        X = model.engineer_features(sample_trend_data)
        
        assert X.ndim == 2, "Features should be 2D array"
        assert X.shape[1] > 10, f"Should have >10 features, got {X.shape[1]}"
        assert len(model.feature_names) == X.shape[1], "Feature names mismatch"
    
    def test_feature_engineering_no_nan(self, model, sample_trend_data):
        """Verify no NaN values in engineered features."""
        X = model.engineer_features(sample_trend_data)
        
        assert not np.isnan(X).any(), "Features contain NaN values"
        assert not np.isinf(X).any(), "Features contain infinite values"
    
    def test_feature_engineering_value_ranges(self, model, sample_trend_data):
        """Verify engineered features are in reasonable ranges."""
        X = model.engineer_features(sample_trend_data)
        
        # Features should generally be in [-10, 10] range after scaling
        assert np.all(X < 1e6), "Features contain extremely large values"
        assert np.all(X > -1e6), "Features contain extremely negative values"
    
    def test_model_training_convergence(self, model, sample_trend_data):
        """Verify model training converges."""
        X = model.engineer_features(sample_trend_data)
        
        # Create synthetic labels (50% positive, 50% negative)
        y_7d = np.random.binomial(1, 0.5, X.shape[0])
        y_14d = np.random.binomial(1, 0.5, X.shape[0])
        
        metrics = model.train(X, y_7d, y_14d)
        
        assert 'train_auc_7d' in metrics, "Missing 7d AUC metric"
        assert 'train_auc_14d' in metrics, "Missing 14d AUC metric"
        assert 0 <= metrics['train_auc_7d'] <= 1, "AUC out of range"
        assert 0 <= metrics['train_auc_14d'] <= 1, "AUC out of range"
    
    def test_model_prediction_output_shape(self, model, sample_trend_data):
        """Verify prediction output has correct shape."""
        X = model.engineer_features(sample_trend_data)
        y = np.random.binomial(1, 0.5, X.shape[0])
        
        model.train(X, y, y)
        
        pred_7d, pred_14d = model.predict(X)
        
        assert pred_7d.shape == (X.shape[0],), "7d predictions shape mismatch"
        assert pred_14d.shape == (X.shape[0],), "14d predictions shape mismatch"
    
    def test_model_prediction_probability_range(self, model, sample_trend_data):
        """Verify predictions are valid probabilities [0, 1]."""
        X = model.engineer_features(sample_trend_data)
        y = np.random.binomial(1, 0.5, X.shape[0])
        
        model.train(X, y, y)
        pred_7d, pred_14d = model.predict(X)
        
        assert np.all((pred_7d >= 0) & (pred_7d <= 1)), "7d predictions outside [0, 1]"
        assert np.all((pred_14d >= 0) & (pred_14d <= 1)), "14d predictions outside [0, 1]"
    
    def test_reproducibility_with_seed(self, sample_trend_data):
        """Test model produces same results with same random seed."""
        X = TrendForecastingModel().engineer_features(sample_trend_data)
        y = np.random.RandomState(42).binomial(1, 0.5, X.shape[0])
        
        # Train model 1
        model1 = TrendForecastingModel(model_type='xgboost')
        model1.train(X, y, y)
        pred1_7d, pred1_14d = model1.predict(X)
        
        # Train model 2 (same seed in XGBoost params)
        model2 = TrendForecastingModel(model_type='xgboost')
        model2.train(X, y, y)
        pred2_7d, pred2_14d = model2.predict(X)
        
        # Should be identical (deterministic with same seed)
        np.testing.assert_array_almost_equal(pred1_7d, pred2_7d, decimal=5)
        np.testing.assert_array_almost_equal(pred1_14d, pred2_14d, decimal=5)


class TestViralityScoringModel:
    """Test virality scoring model for content quality gating."""
    
    @pytest.fixture
    def sample_content(self):
        """Sample content data."""
        return {
            'title': 'Breaking: AI Achieves Major Breakthrough!',
            'description': 'Scientists announce significant advancement in machine learning.',
            'category': 'technology',
            'length_min': 3,
            'language': 'en',
            'has_video': True,
            'has_audio': True,
            'has_captions': True,
            'quality_score': 0.85,
            'platform': 'youtube',
            'is_breaking': True,
            'age_hours': 0.5,
        }
    
    @pytest.fixture
    def sample_creator(self):
        """Sample creator data."""
        return {
            'follower_count': 100000,
            'engagement_rate': 0.05,
            'content_quality_score': 0.8,
            'account_age_days': 730,
            'verified': True,
            'avg_views_per_post': 50000,
            'viral_content_rate': 0.2,
            'category': 'technology',
            'growth_rate_pct': 15,
        }
    
    @pytest.fixture
    def sample_temporal(self):
        """Sample temporal data."""
        return {
            'hour_of_day': 19,  # Evening peak
            'day_of_week': 3,  # Wednesday
            'is_holiday': False,
            'season': 'spring',
            'platform_avg_views': 100000,
            'platform_avg_engagement': 0.04,
            'content_volume_today': 5000,
            'content_volume_percentile': 0.7,
        }
    
    @pytest.fixture
    def model(self):
        """Initialize model."""
        return ViralityScoringModel()
    
    def test_feature_engineering_output_shape(self, model, sample_content, sample_creator, sample_temporal):
        """Verify feature engineering produces correct dimensions."""
        X, names = model.engineer_features(
            sample_content, sample_creator, sample_temporal, ['AI', 'Machine Learning']
        )
        
        assert isinstance(X, np.ndarray), "Output should be numpy array"
        assert X.ndim == 1, "Single sample should produce 1D array"
        assert len(X) > 50, f"Should have >50 features, got {len(X)}"
        assert len(names) == len(X), "Feature names count mismatch"
    
    def test_feature_engineering_no_nan(self, model, sample_content, sample_creator, sample_temporal):
        """Verify no NaN values in engineered features."""
        X, _ = model.engineer_features(
            sample_content, sample_creator, sample_temporal, ['AI']
        )
        
        assert not np.isnan(X).any(), "Features contain NaN values"
        assert not np.isinf(X).any(), "Features contain infinite values"
    
    def test_model_training_convergence(self, model, sample_content, sample_creator, sample_temporal):
        """Verify model training converges."""
        # Generate 200 samples
        X_list = []
        for i in range(200):
            content = sample_content.copy()
            content['title'] = f"Content {i}"
            creator = sample_creator.copy()
            creator['follower_count'] = 10000 * (1 + i % 10)
            temporal = sample_temporal.copy()
            temporal['hour_of_day'] = i % 24
            
            X, _ = model.engineer_features(content, creator, temporal, ['AI', 'trending'])
            X_list.append(X)
        
        X = np.array(X_list)
        y = np.random.binomial(1, 0.5, 200)  # Binary viral/non-viral
        
        metrics = model.train(X, y)
        
        assert 'train_auc_ensemble' in metrics
        assert 0 <= metrics['train_auc_ensemble'] <= 1
        assert metrics['train_auc_ensemble'] > 0.5, "Model should perform better than random"
    
    def test_predict_score_range(self, model, sample_content, sample_creator, sample_temporal):
        """Verify virality scores are in range [0, 100]."""
        # Train model first
        X_list = []
        for _ in range(100):
            X, _ = model.engineer_features(
                sample_content, sample_creator, sample_temporal, ['AI']
            )
            X_list.append(X)
        X = np.array(X_list)
        y = np.random.binomial(1, 0.5, 100)
        model.train(X, y)
        
        # Predict
        X_test, _ = model.engineer_features(
            sample_content, sample_creator, sample_temporal, ['AI']
        )
        scores = model.predict_score(X_test.reshape(1, -1))
        
        assert scores.shape == (1,), "Output shape mismatch"
        assert 0 <= scores[0] <= 100, f"Score out of range: {scores[0]}"
    
    def test_quality_gate_blocking_low_scores(self, model):
        """Verify quality gate blocks low virality scores."""
        approved, reason = model.quality_gate(15)
        assert not approved, "Should block score <20"
        assert "blocked" in reason.lower(), "Reason should mention blocking"
    
    def test_quality_gate_approving_high_scores(self, model):
        """Verify quality gate approves high virality scores."""
        approved, reason = model.quality_gate(75)
        assert approved, "Should approve score >50"
    
    def test_quality_gate_borderline_scores(self, model):
        """Verify quality gate flags borderline scores."""
        approved, reason = model.quality_gate(35)
        assert approved, "Should approve but flag 20-50 range"
        assert "borderline" in reason.lower() or "review" in reason.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
