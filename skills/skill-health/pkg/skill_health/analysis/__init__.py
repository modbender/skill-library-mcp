"""Analysis by time window: hourly, daily, weekly, monthly, cross-temporal alerts."""

from skill_health.analysis.cross_alerts import build_cross_alerts
from skill_health.analysis.daily import (
    build_daily_report,
    infer_target_date_from_bundle,
)
from skill_health.analysis.hourly import build_hourly_report, infer_now_from_bundle
from skill_health.analysis.monthly import (
    build_monthly_report,
    infer_month_end_date_from_bundle,
)
from skill_health.analysis.weekly import (
    build_weekly_report,
    infer_week_end_date_from_bundle,
)

__all__ = [
    "build_cross_alerts",
    "build_hourly_report",
    "build_daily_report",
    "build_weekly_report",
    "build_monthly_report",
    "infer_now_from_bundle",
    "infer_target_date_from_bundle",
    "infer_week_end_date_from_bundle",
    "infer_month_end_date_from_bundle",
]
