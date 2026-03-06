"""
Base Reporter - Abstract base class for all financial reports
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime


@dataclass
class ReportResult:
    """Container for report output"""
    report_type: str
    title: str
    period: str
    generated_at: datetime
    data: Dict[str, Any]
    charts: List[str]  # Paths to generated chart images
    pdf_path: Optional[str] = None
    whatsapp_cards: List[str] = None  # List of card image paths
    summary: str = ""  # One-line executive summary
    confidence: str = "high"  # high, medium, low
    methodology: str = ""  # How numbers were calculated
    caveats: List[str] = None  # Any limitations or assumptions
    
    def __post_init__(self):
        if self.whatsapp_cards is None:
            self.whatsapp_cards = []
        if self.caveats is None:
            self.caveats = []


class BaseReporter(ABC):
    """Abstract base class for all report types"""
    
    def __init__(self, finance_engine, intelligence_engine=None):
        self.finance = finance_engine
        self.intelligence = intelligence_engine
        self.client = finance_engine.client
    
    @abstractmethod
    def generate(self, **params) -> ReportResult:
        """Generate the report. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def get_required_params(self) -> List[str]:
        """Return list of required parameter names."""
        pass
    
    def format_currency(self, amount: float, currency: str = "AED") -> str:
        """Format number as currency string"""
        if amount >= 1_000_000:
            return f"{amount/1_000_000:.2f}M {currency}"
        elif amount >= 1_000:
            return f"{amount/1_000:.2f}K {currency}"
        else:
            return f"{amount:.2f} {currency}"
    
    def format_percentage(self, value: float, decimals: int = 1) -> str:
        """Format as percentage string"""
        return f"{value:.{decimals}f}%"
    
    def calculate_change(self, current: float, previous: float) -> Dict[str, Any]:
        """Calculate period-over-period change"""
        if previous == 0:
            return {
                "absolute": current,
                "percentage": 100.0 if current > 0 else 0.0,
                "direction": "up" if current > 0 else "neutral"
            }
        
        change = current - previous
        pct = (change / abs(previous)) * 100
        
        return {
            "absolute": change,
            "percentage": pct,
            "direction": "up" if change > 0 else ("down" if change < 0 else "neutral")
        }
    
    def get_methodology_note(self, model: str, domain: List, fields: List[str]) -> str:
        """Generate methodology note for transparency"""
        return f"Source: Odoo {model} | Filters: {domain} | Fields: {', '.join(fields)}"
    
    def validate_params(self, params: Dict[str, Any]) -> List[str]:
        """
        Validate parameters and return list of issues.
        Empty list means params are valid.
        """
        issues = []
        
        # Check required params
        for param in self.get_required_params():
            if param not in params or params[param] is None:
                issues.append(f"Missing required parameter: {param}")
        
        # Validate date ranges
        if "date_from" in params and "date_to" in params:
            try:
                from datetime import datetime
                start = datetime.strptime(params["date_from"], "%Y-%m-%d")
                end = datetime.strptime(params["date_to"], "%Y-%m-%d")
                if start > end:
                    issues.append("date_from cannot be after date_to")
            except ValueError:
                issues.append("Invalid date format. Use YYYY-MM-DD")
        
        return issues
