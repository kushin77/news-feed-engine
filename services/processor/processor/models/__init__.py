"""Models package for ML prediction tasks."""

from .trend_forecasting import TrendForecastingModel
from .virality_scoring import ViralityScoringModel

__all__ = [
    'TrendForecastingModel',
    'ViralityScoringModel',
]
