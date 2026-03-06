"""
Parameter Checker - Detects missing params and generates questions
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta


@dataclass
class MissingParam:
    """Represents a missing parameter that needs user input"""
    name: str
    question: str
    options: Optional[List[str]] = None  # For multiple choice
    default: Optional[str] = None
    required: bool = True


class ParamChecker:
    """Validates report parameters and identifies missing info"""
    
    def __init__(self):
        self.date_patterns = {
            "today": datetime.now().strftime("%Y-%m-%d"),
            "yesterday": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "this week": self._get_week_range(),
            "last week": self._get_last_week_range(),
            "this month": self._get_month_range(),
            "last month": self._get_last_month_range(),
            "this quarter": self._get_quarter_range(),
            "last quarter": self._get_last_quarter_range(),
            "this year": self._get_year_range(),
            "last year": self._get_last_year_range(),
        }
    
    def check_report_params(self, report_type: str, params: Dict[str, Any]) -> List[MissingParam]:
        """
        Check if required params are present for a report type.
        Returns list of missing params with questions.
        """
        missing = []
        
        # Common required params
        if "date_from" not in params or "date_to" not in params:
            missing.append(MissingParam(
                name="date_range",
                question="What period should the report cover?",
                options=[
                    "Today",
                    "This week",
                    "This month",
                    "Last month",
                    "This quarter",
                    "This year",
                    "Custom range"
                ]
            ))
        
        # Report-specific checks
        if report_type == "aging":
            if "as_of_date" not in params:
                missing.append(MissingParam(
                    name="as_of_date",
                    question="As of what date? (e.g., 'today', '2024-01-31')",
                    default="today"
                ))
            if "buckets" not in params:
                missing.append(MissingParam(
                    name="buckets",
                    question="What aging buckets to use?",
                    options=["30/60/90", "7/15/30/60/90", "Custom"],
                    default="30/60/90"
                ))
        
        elif report_type == "revenue":
            if "breakdown" not in params:
                missing.append(MissingParam(
                    name="breakdown",
                    question="Breakdown by?",
                    options=["Month", "Week", "Customer", "Product category", "None (totals only)"],
                    default="Month"
                ))
            if "top_n" not in params:
                missing.append(MissingParam(
                    name="top_n",
                    question="Show top N customers/products?",
                    default="10",
                    required=False
                ))
        
        elif report_type == "expenses":
            if "group_by" not in params:
                missing.append(MissingParam(
                    name="group_by",
                    question="Group expenses by?",
                    options=["Vendor", "Category", "Month", "Account"],
                    default="Category"
                ))
            if "include_draft" not in params:
                missing.append(MissingParam(
                    name="include_draft",
                    question="Include draft bills?",
                    options=["No (posted only)", "Yes (include drafts)"],
                    default="No (posted only)"
                ))
        
        elif report_type == "health":
            if "include_forecast" not in params:
                missing.append(MissingParam(
                    name="include_forecast",
                    question="Include cash flow forecast?",
                    options=["Yes", "No"],
                    default="Yes"
                ))
        
        elif report_type == "adhoc":
            # Ad-hoc needs metric specification
            if "metric_a" not in params:
                missing.append(MissingParam(
                    name="metric_a",
                    question="What's the first metric? (e.g., 'revenue', 'expenses', 'cash in')"
                ))
            if "metric_b" not in params:
                missing.append(MissingParam(
                    name="metric_b",
                    question="What's the second metric to compare?",
                    required=False
                ))
            if "granularity" not in params:
                missing.append(MissingParam(
                    name="granularity",
                    question="Group by?",
                    options=["Day", "Week", "Month", "Quarter"],
                    default="Month"
                ))
        
        # Output format check
        if "output_format" not in params:
            missing.append(MissingParam(
                name="output_format",
                question="Output format?",
                options=["WhatsApp cards", "PDF report", "Both"],
                default="WhatsApp cards"
            ))
        
        return missing
    
    def parse_date_range(self, user_input: str) -> tuple:
        """Parse user's date range input into from/to dates"""
        user_input = user_input.lower().strip()
        
        if user_input in self.date_patterns:
            result = self.date_patterns[user_input]
            if isinstance(result, tuple):
                return result
            # Single date (today, yesterday)
            return (result, result)
        
        # Try to parse as custom range "Jan 1-31" or "2024-01-01 to 2024-01-31"
        # ... additional parsing logic
        
        return None, None
    
    def _get_week_range(self):
        today = datetime.now()
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        return (start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
    
    def _get_last_week_range(self):
        today = datetime.now()
        start = today - timedelta(days=today.weekday() + 7)
        end = start + timedelta(days=6)
        return (start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
    
    def _get_month_range(self):
        today = datetime.now()
        start = today.replace(day=1)
        next_month = (start + timedelta(days=32)).replace(day=1)
        end = next_month - timedelta(days=1)
        return (start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
    
    def _get_last_month_range(self):
        today = datetime.now()
        first_of_this_month = today.replace(day=1)
        end = first_of_this_month - timedelta(days=1)
        start = end.replace(day=1)
        return (start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
    
    def _get_quarter_range(self):
        today = datetime.now()
        quarter = (today.month - 1) // 3
        start_month = quarter * 3 + 1
        start = today.replace(month=start_month, day=1)
        end_month = start_month + 2
        end = start.replace(month=end_month, day=1) + timedelta(days=31)
        end = end.replace(day=1) - timedelta(days=1)
        return (start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
    
    def _get_last_quarter_range(self):
        today = datetime.now()
        quarter = (today.month - 1) // 3
        start_month = quarter * 3 + 1 - 3
        if start_month <= 0:
            start_month += 12
            year = today.year - 1
        else:
            year = today.year
        start = today.replace(year=year, month=start_month, day=1)
        end_month = start_month + 2
        end = start.replace(month=end_month, day=1) + timedelta(days=31)
        end = end.replace(day=1) - timedelta(days=1)
        return (start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
    
    def _get_year_range(self):
        today = datetime.now()
        start = today.replace(month=1, day=1)
        end = today.replace(month=12, day=31)
        return (start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
    
    def _get_last_year_range(self):
        today = datetime.now()
        start = today.replace(year=today.year - 1, month=1, day=1)
        end = today.replace(year=today.year - 1, month=12, day=31)
        return (start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
