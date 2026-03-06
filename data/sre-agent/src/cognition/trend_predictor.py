"""
Trend prediction using Holt-Winters and Prophet.

Predicts metric values 1-6 hours ahead to enable early warning.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import structlog
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from src.config.settings import get_settings
from src.models.metrics import MetricSeries

logger = structlog.get_logger()


class TrendPrediction:
    """Prediction result for a metric."""

    def __init__(
        self,
        metric_name: str,
        labels: Dict[str, str],
        predictions: List[Tuple[datetime, float]],
        confidence_intervals: Optional[List[Tuple[float, float]]] = None,
        algorithm: str = "holt_winters",
    ):
        self.metric_name = metric_name
        self.labels = labels
        self.predictions = predictions
        self.confidence_intervals = confidence_intervals
        self.algorithm = algorithm
        self.created_at = datetime.utcnow()

    @property
    def prediction_horizon_hours(self) -> float:
        """Get total prediction horizon in hours."""
        if not self.predictions:
            return 0
        first_ts = self.predictions[0][0]
        last_ts = self.predictions[-1][0]
        return (last_ts - first_ts).total_seconds() / 3600

    def get_value_at(self, target_time: datetime) -> Optional[float]:
        """Get predicted value at a specific time."""
        for ts, val in self.predictions:
            if abs((ts - target_time).total_seconds()) < 300:  # Within 5 minutes
                return val
        return None

    def will_breach_threshold(
        self, threshold: float, direction: str = "above"
    ) -> Tuple[bool, Optional[datetime], Optional[float]]:
        """
        Check if prediction will breach a threshold.

        Args:
            threshold: The threshold value
            direction: "above" or "below"

        Returns:
            Tuple of (will_breach, breach_time, predicted_value_at_breach)
        """
        for ts, val in self.predictions:
            if direction == "above" and val > threshold:
                return True, ts, val
            elif direction == "below" and val < threshold:
                return True, ts, val
        return False, None, None


class TrendPredictor:
    """
    Predicts future metric values using time series forecasting.

    Features:
    - Holt-Winters exponential smoothing
    - Prophet (optional, for more complex patterns)
    - Threshold breach prediction
    - Confidence intervals
    """

    def __init__(
        self,
        horizons_hours: Optional[List[int]] = None,
        algorithms: Optional[List[str]] = None,
    ):
        settings = get_settings()
        self.horizons_hours = horizons_hours or settings.prediction.horizons_hours
        self.algorithms = algorithms or settings.prediction.algorithms

        # Cache for predictions
        self._prediction_cache: Dict[str, TrendPrediction] = {}
        self._cache_ttl_minutes = 5

    def predict(
        self,
        series: MetricSeries,
        horizon_hours: Optional[int] = None,
    ) -> Optional[TrendPrediction]:
        """
        Generate predictions for a metric series.

        Args:
            series: Historical metric data
            horizon_hours: Prediction horizon (defaults to max configured)

        Returns:
            TrendPrediction or None if insufficient data
        """
        if not series.data_points or len(series.data_points) < 24:
            logger.debug(
                "Insufficient data for prediction",
                metric=series.name,
                points=len(series.data_points) if series.data_points else 0,
            )
            return None

        horizon = horizon_hours or max(self.horizons_hours)

        # Check cache
        cache_key = self._make_cache_key(series.name, series.labels, horizon)
        cached = self._prediction_cache.get(cache_key)
        if cached and self._is_cache_valid(cached):
            return cached

        # Generate prediction
        prediction = None
        if "holt_winters" in self.algorithms:
            prediction = self._predict_holt_winters(series, horizon)
        elif "prophet" in self.algorithms:
            prediction = self._predict_prophet(series, horizon)

        if prediction:
            self._prediction_cache[cache_key] = prediction

        return prediction

    def _predict_holt_winters(
        self,
        series: MetricSeries,
        horizon_hours: int,
    ) -> Optional[TrendPrediction]:
        """Generate prediction using Holt-Winters exponential smoothing."""
        try:
            values = np.array(series.values)

            # Handle any NaN or inf values
            values = np.nan_to_num(values, nan=np.nanmean(values))

            # Determine seasonality
            # For minute-level data, hourly seasonality = 60 periods
            seasonal_periods = min(60, len(values) // 3)

            if seasonal_periods < 2:
                seasonal_periods = None

            # Fit model
            model = ExponentialSmoothing(
                values,
                seasonal_periods=seasonal_periods,
                trend="add" if len(values) > 100 else None,
                seasonal="add" if seasonal_periods else None,
                damped_trend=True if len(values) > 100 else False,
            )

            fitted = model.fit(optimized=True)

            # Generate predictions
            # Assuming 1-minute resolution data
            n_periods = horizon_hours * 60
            forecast = fitted.forecast(n_periods)

            # Create prediction timestamps
            last_ts = series.latest_timestamp or datetime.utcnow()
            predictions = [
                (last_ts + timedelta(minutes=i + 1), float(val))
                for i, val in enumerate(forecast)
            ]

            # Calculate simple confidence intervals (using fitted model's residuals)
            residual_std = float(np.std(fitted.resid))
            confidence_intervals = [
                (val - 1.96 * residual_std, val + 1.96 * residual_std)
                for _, val in predictions
            ]

            logger.debug(
                "Generated Holt-Winters prediction",
                metric=series.name,
                horizon_hours=horizon_hours,
                n_points=len(predictions),
            )

            return TrendPrediction(
                metric_name=series.name,
                labels=series.labels,
                predictions=predictions,
                confidence_intervals=confidence_intervals,
                algorithm="holt_winters",
            )

        except Exception as e:
            logger.warning(
                "Holt-Winters prediction failed",
                metric=series.name,
                error=str(e),
            )
            return None

    def _predict_prophet(
        self,
        series: MetricSeries,
        horizon_hours: int,
    ) -> Optional[TrendPrediction]:
        """Generate prediction using Prophet."""
        try:
            from prophet import Prophet
            import pandas as pd

            # Prepare data for Prophet
            df = pd.DataFrame({
                "ds": series.timestamps,
                "y": series.values,
            })

            # Fit model
            model = Prophet(
                changepoint_prior_scale=0.05,
                seasonality_mode="additive",
            )
            model.fit(df)

            # Create future dataframe
            future = model.make_future_dataframe(
                periods=horizon_hours * 60,
                freq="T",  # Minute frequency
            )

            # Generate forecast
            forecast = model.predict(future)

            # Extract predictions (future only)
            last_ts = series.latest_timestamp
            future_forecast = forecast[forecast["ds"] > last_ts]

            predictions = [
                (row["ds"].to_pydatetime(), float(row["yhat"]))
                for _, row in future_forecast.iterrows()
            ]

            confidence_intervals = [
                (float(row["yhat_lower"]), float(row["yhat_upper"]))
                for _, row in future_forecast.iterrows()
            ]

            logger.debug(
                "Generated Prophet prediction",
                metric=series.name,
                horizon_hours=horizon_hours,
                n_points=len(predictions),
            )

            return TrendPrediction(
                metric_name=series.name,
                labels=series.labels,
                predictions=predictions,
                confidence_intervals=confidence_intervals,
                algorithm="prophet",
            )

        except ImportError:
            logger.warning("Prophet not installed, skipping Prophet prediction")
            return None
        except Exception as e:
            logger.warning(
                "Prophet prediction failed",
                metric=series.name,
                error=str(e),
            )
            return None

    def predict_threshold_breach(
        self,
        series: MetricSeries,
        upper_threshold: Optional[float] = None,
        lower_threshold: Optional[float] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Predict if and when a threshold will be breached.

        Args:
            series: Metric series
            upper_threshold: Upper bound
            lower_threshold: Lower bound

        Returns:
            Breach prediction details or None
        """
        prediction = self.predict(series)
        if not prediction:
            return None

        result: Dict[str, Any] = {
            "metric_name": series.name,
            "labels": series.labels,
            "breaches": [],
        }

        if upper_threshold is not None:
            will_breach, breach_time, breach_value = prediction.will_breach_threshold(
                upper_threshold, "above"
            )
            if will_breach:
                result["breaches"].append({
                    "threshold": upper_threshold,
                    "direction": "above",
                    "predicted_time": breach_time.isoformat() if breach_time else None,
                    "predicted_value": breach_value,
                    "eta_hours": (
                        (breach_time - datetime.utcnow()).total_seconds() / 3600
                        if breach_time
                        else None
                    ),
                })

        if lower_threshold is not None:
            will_breach, breach_time, breach_value = prediction.will_breach_threshold(
                lower_threshold, "below"
            )
            if will_breach:
                result["breaches"].append({
                    "threshold": lower_threshold,
                    "direction": "below",
                    "predicted_time": breach_time.isoformat() if breach_time else None,
                    "predicted_value": breach_value,
                    "eta_hours": (
                        (breach_time - datetime.utcnow()).total_seconds() / 3600
                        if breach_time
                        else None
                    ),
                })

        return result if result["breaches"] else None

    def _make_cache_key(
        self, metric_name: str, labels: Dict[str, str], horizon: int
    ) -> str:
        """Create cache key."""
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{metric_name}{{{label_str}}}:{horizon}h"

    def _is_cache_valid(self, prediction: TrendPrediction) -> bool:
        """Check if cached prediction is still valid."""
        age = datetime.utcnow() - prediction.created_at
        return age.total_seconds() < self._cache_ttl_minutes * 60

    def clear_cache(self) -> None:
        """Clear prediction cache."""
        self._prediction_cache.clear()
