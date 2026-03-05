"""
AI-powered financial forecasting.
Uses statistical methods and AI for cash flow and revenue predictions.
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
import statistics

logger = logging.getLogger(__name__)


@dataclass
class ForecastResult:
    """Result of a forecast calculation."""
    predictions: List[Dict[str, Any]]
    confidence: float  # 0-1
    trend: str  # "up", "down", "stable"
    summary: str
    methodology: str


class CashFlowForecaster:
    """
    Forecast future cash flow based on historical data.
    
    Uses:
    - Moving averages for baseline
    - Trend analysis for direction
    - Seasonality detection (if enough data)
    - AI for narrative generation (optional)
    
    Usage:
        forecaster = CashFlowForecaster()
        forecast = forecaster.forecast(historical_data, days_ahead=30)
    """
    
    def __init__(self, use_ai: bool = True):
        self.use_ai = use_ai
    
    def forecast(
        self, 
        historical: List[Dict[str, Any]], 
        days_ahead: int = 30,
        current_balance: float = None
    ) -> Dict[str, Any]:
        """
        Generate cash flow forecast.
        
        Args:
            historical: List of daily cash flow data
                [{"date": "2026-01-01", "cash_in": 10000, "cash_out": 8000}, ...]
            days_ahead: Number of days to forecast
            current_balance: Current cash balance (optional)
        
        Returns:
            Forecast with predictions, confidence, and narrative
        """
        if len(historical) < 3:
            return {
                "error": "Insufficient data for forecasting",
                "min_required": 3,
                "provided": len(historical),
                "fallback": "Use at least 3 days of historical data"
            }
        
        # Extract time series
        cash_in_series = [d.get("cash_in", 0) for d in historical]
        cash_out_series = [d.get("cash_out", 0) for d in historical]
        net_series = [i - o for i, o in zip(cash_in_series, cash_out_series)]
        
        # Calculate statistics
        avg_in = statistics.mean(cash_in_series)
        avg_out = statistics.mean(cash_out_series)
        avg_net = statistics.mean(net_series)
        
        std_net = statistics.stdev(net_series) if len(net_series) > 1 else 0
        
        # Detect trend
        trend = self._detect_trend(net_series)
        
        # Calculate confidence based on volatility
        volatility = std_net / abs(avg_net) if avg_net != 0 else 1
        confidence = max(0.3, min(0.95, 1 - volatility * 0.5))
        
        # Generate predictions
        last_date = datetime.strptime(historical[-1]["date"], "%Y-%m-%d")
        predictions = []
        
        running_balance = current_balance or 0
        cumulative_net = 0
        
        for day in range(1, days_ahead + 1):
            pred_date = (last_date + timedelta(days=day)).strftime("%Y-%m-%d")
            
            # Apply trend adjustment
            trend_factor = 1 + (0.02 * day if trend == "up" else -0.02 * day if trend == "down" else 0)
            
            pred_in = avg_in * trend_factor
            pred_out = avg_out * trend_factor
            pred_net = pred_in - pred_out
            
            cumulative_net += pred_net
            pred_balance = running_balance + cumulative_net
            
            # Confidence decreases with time
            day_confidence = confidence * (1 - day * 0.01)
            
            predictions.append({
                "date": pred_date,
                "day": day,
                "cash_in": round(pred_in, 2),
                "cash_out": round(pred_out, 2),
                "net": round(pred_net, 2),
                "cumulative_net": round(cumulative_net, 2),
                "balance": round(pred_balance, 2) if current_balance else None,
                "confidence": round(day_confidence, 2)
            })
        
        # Generate summary
        total_pred_net = sum(p["net"] for p in predictions)
        end_balance = running_balance + cumulative_net
        
        summary = self._generate_summary(
            trend=trend,
            avg_net=avg_net,
            total_pred_net=total_pred_net,
            confidence=confidence,
            days=days_ahead,
            end_balance=end_balance
        )
        
        # Risk assessment
        risk = self._assess_risk(predictions, current_balance)
        
        return {
            "predictions": predictions,
            "confidence": round(confidence, 2),
            "trend": trend,
            "summary": summary,
            "statistics": {
                "avg_daily_in": round(avg_in, 2),
                "avg_daily_out": round(avg_out, 2),
                "avg_daily_net": round(avg_net, 2),
                "volatility": round(volatility, 3)
            },
            "projected": {
                "total_net": round(total_pred_net, 2),
                "end_balance": round(end_balance, 2) if current_balance else None
            },
            "risk": risk,
            "methodology": "Moving average with trend adjustment"
        }
    
    def _detect_trend(self, series: List[float]) -> str:
        """Detect trend direction using linear regression slope."""
        if len(series) < 3:
            return "stable"
        
        n = len(series)
        x = list(range(n))
        y = series
        
        # Simple linear regression
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        
        numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y))
        denominator = sum((xi - x_mean) ** 2 for xi in x)
        
        if denominator == 0:
            return "stable"
        
        slope = numerator / denominator
        
        # Normalize slope relative to mean
        slope_normalized = slope / abs(y_mean) if y_mean != 0 else 0
        
        if slope_normalized > 0.05:
            return "up"
        elif slope_normalized < -0.05:
            return "down"
        else:
            return "stable"
    
    def _generate_summary(
        self, 
        trend: str, 
        avg_net: float, 
        total_pred_net: float,
        confidence: float,
        days: int,
        end_balance: float
    ) -> str:
        """Generate narrative summary."""
        trend_desc = {
            "up": "improving",
            "down": "declining",
            "stable": "stable"
        }
        
        conf_level = "high" if confidence > 0.7 else "moderate" if confidence > 0.5 else "low"
        
        summary = f"Cash flow trend is {trend_desc[trend]}. "
        summary += f"Average daily net cash: {avg_net:,.2f}. "
        summary += f"Projected {days}-day net change: {total_pred_net:,.2f}. "
        
        if end_balance is not None:
            summary += f"Projected ending balance: {end_balance:,.2f}. "
        
        summary += f"Confidence: {conf_level} ({confidence:.0%})."
        
        return summary
    
    def _assess_risk(self, predictions: List[Dict], current_balance: float) -> Dict[str, Any]:
        """Assess cash flow risk."""
        risks = []
        
        if current_balance is not None:
            # Check for negative balance risk
            min_balance = min(p.get("balance", 0) for p in predictions)
            if min_balance < 0:
                risks.append({
                    "type": "negative_balance",
                    "severity": "high",
                    "description": f"Projected to go negative: {min_balance:,.2f}",
                    "mitigation": "Arrange additional funding or reduce outflows"
                })
            elif min_balance < current_balance * 0.1:
                risks.append({
                    "type": "low_balance",
                    "severity": "medium",
                    "description": f"Balance may drop to {min_balance:,.2f}",
                    "mitigation": "Monitor closely and prepare contingency"
                })
        
        # Check trend
        net_values = [p["net"] for p in predictions]
        if all(n < 0 for n in net_values[:7]):
            risks.append({
                "type": "negative_trend",
                "severity": "medium",
                "description": "Consistently negative cash flow projected",
                "mitigation": "Review expenses and accelerate collections"
            })
        
        return {
            "level": "high" if any(r["severity"] == "high" for r in risks) else
                     "medium" if risks else "low",
            "items": risks
        }


class RevenueForecaster:
    """Forecast future revenue based on historical data."""
    
    def forecast(
        self,
        historical: List[Dict[str, Any]],
        periods_ahead: int = 3,
        period_type: str = "month"
    ) -> Dict[str, Any]:
        """
        Forecast revenue.
        
        Args:
            historical: List of period revenue data
                [{"period": "2026-01", "revenue": 100000}, ...]
            periods_ahead: Number of periods to forecast
            period_type: "month" or "quarter"
        
        Returns:
            Revenue forecast with predictions
        """
        if len(historical) < 3:
            return {
                "error": "Insufficient data",
                "min_required": 3,
                "provided": len(historical)
            }
        
        revenues = [d.get("revenue", 0) for d in historical]
        avg_revenue = statistics.mean(revenues)
        
        # Detect trend
        trend = self._detect_trend(revenues)
        
        # Seasonality (simple month-over-month growth)
        if len(revenues) >= 12:
            # Year-over-year comparison
            yoy_growth = (revenues[-1] - revenues[-12]) / revenues[-12] if revenues[-12] else 0
        else:
            # Sequential growth
            yoy_growth = (revenues[-1] - revenues[-2]) / revenues[-2] if revenues[-2] else 0
        
        # Generate predictions
        predictions = []
        last_period = historical[-1]["period"]
        
        for i in range(1, periods_ahead + 1):
            if period_type == "month":
                # Parse YYYY-MM
                year, month = map(int, last_period.split("-"))
                month += i
                while month > 12:
                    month -= 12
                    year += 1
                pred_period = f"{year:04d}-{month:02d}"
            else:
                # Quarter
                pred_period = f"Q{i} (projected)"
            
            # Apply growth rate
            growth_factor = 1 + (yoy_growth * i * 0.1)  # Diminishing growth
            pred_revenue = avg_revenue * growth_factor if trend == "up" else avg_revenue
            
            predictions.append({
                "period": pred_period,
                "revenue": round(pred_revenue, 2),
                "growth_rate": round(yoy_growth * 100, 2)
            })
        
        return {
            "predictions": predictions,
            "trend": trend,
            "statistics": {
                "avg_revenue": round(avg_revenue, 2),
                "growth_rate": round(yoy_growth * 100, 2)
            },
            "methodology": "Moving average with growth trend"
        }
    
    def _detect_trend(self, series: List[float]) -> str:
        """Detect trend direction."""
        if len(series) < 3:
            return "stable"
        
        recent = series[-3:]
        older = series[:-3] if len(series) > 3 else series
        
        recent_avg = statistics.mean(recent)
        older_avg = statistics.mean(older)
        
        change = (recent_avg - older_avg) / older_avg if older_avg else 0
        
        if change > 0.05:
            return "up"
        elif change < -0.05:
            return "down"
        return "stable"


class BudgetForecaster:
    """Forecast budget variance."""
    
    def forecast_variance(
        self,
        actuals: Dict[str, float],
        budget: Dict[str, float],
        months_remaining: int
    ) -> Dict[str, Any]:
        """
        Forecast year-end budget variance.
        
        Args:
            actuals: Actual YTD figures by category
            budget: Annual budget by category
            months_remaining: Months left in fiscal year
        
        Returns:
            Projected variance analysis
        """
        projections = {}
        total_projected_variance = 0
        
        for category, budget_amount in budget.items():
            actual_ytd = actuals.get(category, 0)
            
            # Burn rate
            months_elapsed = 12 - months_remaining
            if months_elapsed > 0:
                monthly_rate = actual_ytd / months_elapsed
                projected_total = actual_ytd + (monthly_rate * months_remaining)
            else:
                projected_total = budget_amount
            
            variance = projected_total - budget_amount
            variance_pct = (variance / budget_amount * 100) if budget_amount else 0
            
            projections[category] = {
                "budget": budget_amount,
                "actual_ytd": actual_ytd,
                "projected_total": round(projected_total, 2),
                "variance": round(variance, 2),
                "variance_pct": round(variance_pct, 2),
                "status": "over" if variance > 0 else "under" if variance < 0 else "on_track"
            }
            
            total_projected_variance += variance
        
        return {
            "projections": projections,
            "total_projected_variance": round(total_projected_variance, 2),
            "months_remaining": months_remaining,
            "summary": f"Projected year-end variance: {total_projected_variance:,.2f}"
        }
