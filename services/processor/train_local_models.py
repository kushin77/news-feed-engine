#!/usr/bin/env python
"""
Local ML Model Training Script

Trains TrendForecastingModel and ViralityScoringModel on synthetic data.
Persists models to disk and registers with MLflow.

Usage:
    python train_local_models.py [--output-dir ./models]
"""

import os
import logging
import argparse
from datetime import datetime
import numpy as np
import pandas as pd
import mlflow
import mlflow.xgboost
import mlflow.sklearn
from pathlib import Path

from processor.models import TrendForecastingModel, ViralityScoringModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_synthetic_trend_data(n_samples: int = 500) -> pd.DataFrame:
    """Generate synthetic trend data for training."""
    dates = pd.date_range('2023-01-01', periods=n_samples, freq='D')
    
    # Synthetic trend history
    data = pd.DataFrame({
        'timestamp': dates,
        'trend_name': np.random.choice(['AI', 'Crypto', 'Gaming', 'Sports', 'Music'], n_samples),
        'signal_strength': np.cumsum(np.random.normal(10, 5, n_samples)),
        'engagement_rate': np.random.uniform(0, 1, n_samples),
        'audience_size': np.random.randint(1000, 1000000, n_samples),
        'competitor_count': np.random.randint(0, 100, n_samples),
    })
    
    return data


def create_synthetic_content_data(n_samples: int = 500) -> pd.DataFrame:
    """Generate synthetic content data for virality prediction."""
    data = pd.DataFrame({
        'content_length': np.random.randint(100, 5000, n_samples),
        'creator_followers': np.random.randint(100, 10000000, n_samples),
        'creator_engagement_rate': np.random.uniform(0, 1, n_samples),
        'has_video': np.random.choice([0, 1], n_samples),
        'has_audio': np.random.choice([0, 1], n_samples),
        'has_captions': np.random.choice([0, 1], n_samples),
        'is_trending_topic': np.random.choice([0, 1], n_samples),
        'time_of_day': np.random.randint(0, 24, n_samples),
        'day_of_week': np.random.randint(0, 7, n_samples),
        'content_quality_score': np.random.uniform(0, 1, n_samples),
        'language_id': np.random.choice(['en', 'es', 'fr', 'de', 'zh'], n_samples),
        'is_original': np.random.choice([0, 1], n_samples),
        'content_category': np.random.choice(['tech', 'sports', 'entertainment', 'news', 'other'], n_samples),
        'viral_views': np.random.randint(0, 1000000, n_samples),  # Target: >100k = viral
    })
    
    return data


def train_trend_forecasting_model(output_dir: str) -> str:
    """Train trend forecasting model."""
    logger.info("🚀 Training Trend Forecasting Model...")
    
    with mlflow.start_run(run_name="trend_forecasting_training"):
        model = TrendForecastingModel(model_type='xgboost')
        
        # Generate synthetic data
        data = create_synthetic_trend_data(n_samples=500)
        
        # Log parameters
        mlflow.log_param("model_type", "xgboost")
        mlflow.log_param("training_samples", len(data))
        
        try:
            # Engineer features
            X = model.engineer_features(data)
            mlflow.log_param("feature_count", X.shape[1])
            
            # Create binary targets for 7d and 14d forecasts
            y_7d = np.random.choice([0, 1], size=len(X), p=[0.4, 0.6])
            y_14d = np.random.choice([0, 1], size=len(X), p=[0.35, 0.65])
            
            # Train model
            metrics = model.train(X, y_7d, y_14d)
            
            # Log metrics
            if metrics:
                for metric_name, metric_value in metrics.items():
                    if isinstance(metric_value, (int, float)):
                        mlflow.log_metric(metric_name, float(metric_value))
            
            logger.info(f"✅ Trend model trained")
            
            # Log model artifacts (don't use save_to_mlflow, it would create a nested run)
            if model.model and '7d' in model.model:
                mlflow.xgboost.log_model(model.model['7d'], "trend_model_7d")
                mlflow.xgboost.log_model(model.model['14d'], "trend_model_14d")
            
            return "trend_forecasting_model"
            
        except Exception as e:
            logger.error(f"❌ Error training trend model: {e}")
            mlflow.log_param("error", str(e))
            raise


def train_virality_scoring_model(output_dir: str) -> str:
    """Train virality scoring model."""
    logger.info("🚀 Training Virality Scoring Model...")
    
    with mlflow.start_run(run_name="virality_scoring_training"):
        model = ViralityScoringModel()
        
        # Generate synthetic data
        data = create_synthetic_content_data(n_samples=500)
        
        # Log parameters
        mlflow.log_param("model_type", "ensemble_xgb_lgb")
        mlflow.log_param("xgb_weight", 0.6)
        mlflow.log_param("lgb_weight", 0.4)
        mlflow.log_param("training_samples", len(data))
        
        try:
            # Prepare features and target
            feature_cols = data.columns[data.columns != 'viral_views'].tolist()
            X = data[feature_cols]
            y = (data['viral_views'] > 100000).astype(int)  # Binary: viral > 100k views
            
            # Convert categorical to numeric if needed
            for col in X.columns:
                if X[col].dtype == 'object':
                    X[col] = pd.factorize(X[col])[0]
            
            mlflow.log_param("feature_count", X.shape[1])
            
            # Train model
            metrics = model.train(X, y)
            
            # Log metrics
            if metrics:
                for metric_name, metric_value in metrics.items():
                    if isinstance(metric_value, (int, float)):
                        mlflow.log_metric(metric_name, float(metric_value))
            
            logger.info(f"✅ Virality model trained | Metrics: {metrics}")
            
            # Log model artifacts
            if hasattr(model, 'xgb_model') and model.xgb_model:
                mlflow.sklearn.log_model(model.xgb_model, "virality_model_xgb")
            if hasattr(model, 'lgb_model') and model.lgb_model:
                mlflow.sklearn.log_model(model.lgb_model, "virality_model_lgb")
            
            return "virality_scoring_model"
            
        except Exception as e:
            logger.error(f"❌ Error training virality model: {e}")
            mlflow.log_param("error", str(e))
            raise


def main():
    parser = argparse.ArgumentParser(description="Train ML models locally")
    parser.add_argument("--output-dir", default="./models", help="Output directory for models")
    parser.add_argument("--mlflow-uri", default="sqlite:///mlflow.db", help="MLflow backend URI")
    args = parser.parse_args()
    
    # Create output directory
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    
    # Configure MLflow
    mlflow.set_tracking_uri(args.mlflow_uri)
    mlflow.set_experiment("news-feed-engine-models")
    
    logger.info(f"📊 Starting model training... | Output: {args.output_dir}")
    
    try:
        # Train trend forecasting model
        trend_model_path = train_trend_forecasting_model(args.output_dir)
        logger.info(f"💾 Trend model saved to: {trend_model_path}")
        
        # Train virality scoring model
        virality_model_path = train_virality_scoring_model(args.output_dir)
        logger.info(f"💾 Virality model saved to: {virality_model_path}")
        
        logger.info(f"🎉 All models trained successfully!")
        logger.info(f"📈 MLflow Tracking URI: {args.mlflow_uri}")
        logger.info(f"📊 Experiment: news-feed-engine-models")
        
    except Exception as e:
        logger.error(f"❌ Training failed: {e}")
        raise


if __name__ == "__main__":
    main()
