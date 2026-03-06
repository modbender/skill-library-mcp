"""
Centralized error handling for CFO skill.
Provides structured errors with codes, messages, and context.
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class CFOError(Exception):
    """Base error for CFO skill."""
    message: str
    code: str
    field: Optional[str] = None
    value: Optional[Any] = None
    details: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": self.code,
            "message": self.message,
            "field": self.field,
            "value": str(self.value) if self.value else None,
            "details": self.details,
            "timestamp": datetime.now().isoformat()
        }


class ValidationError(CFOError):
    """Input validation error."""
    def __init__(self, message: str, field: str = None, value: Any = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            field=field,
            value=value
        )


class ConnectionError(CFOError):
    """Odoo connection error."""
    def __init__(self, message: str, details: Dict = None):
        super().__init__(
            message=message,
            code="CONNECTION_ERROR",
            details=details
        )


class DataError(CFOError):
    """Data retrieval/processing error."""
    def __init__(self, message: str, model: str = None, details: Dict = None):
        super().__init__(
            message=message,
            code="DATA_ERROR",
            field=model,
            details=details
        )


class ReportError(CFOError):
    """Report generation error."""
    def __init__(self, message: str, report_type: str = None, details: Dict = None):
        super().__init__(
            message=message,
            code="REPORT_ERROR",
            field=report_type,
            details=details
        )


class CFOErrorHandler:
    """
    Centralized error handler with validation and safe execution.
    
    Usage:
        handler = CFOErrorHandler()
        
        # Validate inputs
        handler.validate_date(date_str, "date_from")
        handler.validate_company_id(company_id)
        
        # Safe execution
        result = handler.safe_execute(func, *args, fallback=None)
    """
    
    def validate_date(self, date_str: str, field_name: str) -> str:
        """Validate date format (YYYY-MM-DD)."""
        if not date_str:
            raise ValidationError(
                f"{field_name} is required",
                field=field_name,
                value=date_str
            )
        
        try:
            parsed = datetime.strptime(date_str, "%Y-%m-%d")
            # Check reasonable range
            if parsed.year < 2000 or parsed.year > 2100:
                raise ValidationError(
                    f"{field_name} must be between 2000 and 2100",
                    field=field_name,
                    value=date_str
                )
            return date_str
        except ValueError:
            raise ValidationError(
                f"{field_name} must be in YYYY-MM-DD format",
                field=field_name,
                value=date_str
            )
    
    def validate_date_range(self, date_from: str, date_to: str) -> bool:
        """Validate date range (from <= to)."""
        try:
            from_dt = datetime.strptime(date_from, "%Y-%m-%d")
            to_dt = datetime.strptime(date_to, "%Y-%m-%d")
            
            if from_dt > to_dt:
                raise ValidationError(
                    "Start date must be before or equal to end date",
                    field="date_range",
                    value=f"{date_from} to {date_to}"
                )
            
            # Check reasonable span (max 5 years)
            days = (to_dt - from_dt).days
            if days > 365 * 5:
                raise ValidationError(
                    "Date range cannot exceed 5 years",
                    field="date_range",
                    value=f"{days} days"
                )
            
            return True
        except ValueError as e:
            raise ValidationError(
                f"Invalid date format: {e}",
                field="date_range"
            )
    
    def validate_company_id(self, company_id: Any) -> int:
        """Validate company ID."""
        if company_id is None:
            raise ValidationError(
                "Company ID is required",
                field="company_id",
                value=company_id
            )
        
        try:
            cid = int(company_id)
            if cid < 1:
                raise ValidationError(
                    "Company ID must be a positive integer",
                    field="company_id",
                    value=company_id
                )
            return cid
        except (TypeError, ValueError):
            raise ValidationError(
                "Company ID must be a valid integer",
                field="company_id",
                value=company_id
            )
    
    def validate_positive_number(self, value: Any, field_name: str) -> float:
        """Validate positive number."""
        try:
            num = float(value)
            if num < 0:
                raise ValidationError(
                    f"{field_name} must be non-negative",
                    field=field_name,
                    value=value
                )
            return num
        except (TypeError, ValueError):
            raise ValidationError(
                f"{field_name} must be a valid number",
                field=field_name,
                value=value
            )
    
    def safe_execute(self, func, *args, fallback=None, **kwargs):
        """
        Execute a function with error handling.
        Returns fallback value on error.
        """
        try:
            return func(*args, **kwargs)
        except CFOError as e:
            logger.error(f"CFO Error: {e.to_dict()}")
            return fallback
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            return fallback
    
    def wrap_report(self, report_func, *args, **kwargs) -> Dict[str, Any]:
        """
        Wrap a report function with error handling.
        Returns a structured response with error info if fails.
        """
        try:
            result = report_func(*args, **kwargs)
            return {
                "success": True,
                "data": result,
                "error": None
            }
        except CFOError as e:
            logger.error(f"Report error: {e.to_dict()}")
            return {
                "success": False,
                "data": None,
                "error": e.to_dict()
            }
        except Exception as e:
            logger.error(f"Unexpected report error: {e}")
            return {
                "success": False,
                "data": None,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            }


def with_error_handler(func):
    """Decorator to add error handling to functions."""
    handler = CFOErrorHandler()
    
    def wrapper(*args, **kwargs):
        return handler.wrap_report(func, *args, **kwargs)
    
    return wrapper
