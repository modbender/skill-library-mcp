"""
Tests for Odoo CFO Skill
Run: ./venv/bin/python -m pytest tests/ -v
"""
import os
import sys
import json
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.logic.reporting_standards import (
    ReportingStandardDetector, 
    STANDARDS, 
    format_amount,
    format_date,
    get_statement_title
)
from src.logic.error_handler import CFOErrorHandler, CFOError, ValidationError
from src.visualizers.excel_export import ExcelExporter
from src.logic.forecasting import CashFlowForecaster


class TestReportingStandards:
    """Test automatic standard detection."""
    
    def test_standards_registry(self):
        """All expected standards exist."""
        expected = ["IFRS", "US_GAAP", "IND_AS", "UK_GAAP", "SOCPA", "EU_IFRS", "CAS", "JGAAP", "ASPE", "AASB"]
        for code in expected:
            assert code in STANDARDS, f"Missing standard: {code}"
    
    def test_format_amount_positive(self):
        """Format positive amounts."""
        standard = STANDARDS["IFRS"]
        result = format_amount(1234.56, standard, "AED")
        assert "AED" in result
        assert "1,234.56" in result or "1234.56" in result
    
    def test_format_amount_negative(self):
        """Format negative amounts with brackets (IFRS)."""
        standard = STANDARDS["IFRS"]
        result = format_amount(-1234.56, standard, "AED")
        assert "(" in result or "-" in result
    
    def test_format_date_dmy(self):
        """Format date in DMY format."""
        standard = STANDARDS["IFRS"]  # DMY
        result = format_date("2026-01-31", standard)
        assert "31" in result and "01" in result and "2026" in result
    
    def test_format_date_mdy(self):
        """Format date in MDY format (US)."""
        standard = STANDARDS["US_GAAP"]  # MDY
        result = format_date("2026-01-31", standard)
        assert "01" in result and "31" in result and "2026" in result
    
    def test_statement_titles(self):
        """Get correct statement titles per standard."""
        ifrs_title = get_statement_title("balance_sheet", STANDARDS["IFRS"])
        us_title = get_statement_title("balance_sheet", STANDARDS["US_GAAP"])
        
        assert "Financial Position" in ifrs_title
        assert "Balance Sheet" in us_title


class TestErrorHandler:
    """Test error handling."""
    
    def test_validation_error(self):
        """Validation errors have proper structure."""
        error = ValidationError("Invalid date", field="date_from", value="invalid")
        assert error.message == "Invalid date"
        assert error.field == "date_from"
        assert error.code == "VALIDATION_ERROR"
    
    def test_error_handler_date_validation(self):
        """Date validation works."""
        handler = CFOErrorHandler()
        
        # Valid date
        handler.validate_date("2026-01-31", "date_from")  # Should not raise
        
        # Invalid date
        with pytest.raises(ValidationError):
            handler.validate_date("invalid", "date_from")
    
    def test_error_handler_company_id(self):
        """Company ID validation works."""
        handler = CFOErrorHandler()
        
        # Valid
        handler.validate_company_id(1)  # Should not raise
        
        # Invalid
        with pytest.raises(ValidationError):
            handler.validate_company_id(-1)
        
        with pytest.raises(ValidationError):
            handler.validate_company_id("invalid")
    
    def test_error_handler_date_range(self):
        """Date range validation works."""
        handler = CFOErrorHandler()
        
        # Valid range
        handler.validate_date_range("2026-01-01", "2026-01-31")  # Should not raise
        
        # Invalid range (from > to)
        with pytest.raises(ValidationError):
            handler.validate_date_range("2026-01-31", "2026-01-01")


class TestExcelExporter:
    """Test Excel export functionality."""
    
    def test_export_balance_sheet(self):
        """Export balance sheet to Excel."""
        exporter = ExcelExporter()
        
        data = {
            "as_of_date": "2026-01-31",
            "company_name": "Test Company",
            "assets": {
                "non_current": {"Property": 100000, "Equipment": 50000},
                "current": {"Cash": 25000, "Receivables": 15000}
            },
            "liabilities": {
                "non_current": {"Loans": 80000},
                "current": {"Payables": 10000}
            },
            "equity": {
                "total": 100000
            }
        }
        
        output = exporter.export_balance_sheet(data)
        assert output is not None
        assert len(output) > 1000  # Should have content
    
    def test_export_profit_loss(self):
        """Export P&L to Excel."""
        exporter = ExcelExporter()
        
        data = {
            "period": "2026-01-01 to 2026-01-31",
            "company_name": "Test Company",
            "revenue": {"Sales": 100000},
            "expenses": {"Costs": 60000, "Admin": 10000},
            "totals": {
                "gross_profit": 40000,
                "net_profit": 30000
            }
        }
        
        output = exporter.export_profit_loss(data)
        assert output is not None
        assert len(output) > 1000


class TestForecasting:
    """Test AI forecasting."""
    
    def test_cash_flow_forecast(self):
        """Generate cash flow forecast."""
        forecaster = CashFlowForecaster()
        
        historical = [
            {"date": "2026-01-01", "cash_in": 10000, "cash_out": 8000},
            {"date": "2026-01-02", "cash_in": 12000, "cash_out": 9000},
            {"date": "2026-01-03", "cash_in": 11000, "cash_out": 8500},
            {"date": "2026-01-04", "cash_in": 13000, "cash_out": 9500},
            {"date": "2026-01-05", "cash_in": 10500, "cash_out": 8200},
        ]
        
        forecast = forecaster.forecast(historical, days_ahead=7)
        
        assert "predictions" in forecast
        assert len(forecast["predictions"]) == 7
        assert "confidence" in forecast
        assert "trend" in forecast
    
    def test_forecast_with_insufficient_data(self):
        """Handle insufficient data gracefully."""
        forecaster = CashFlowForecaster()
        
        # Only 1 data point
        historical = [{"date": "2026-01-01", "cash_in": 10000, "cash_out": 8000}]
        
        forecast = forecaster.forecast(historical, days_ahead=7)
        
        assert "error" in forecast or "predictions" in forecast


class TestIntegration:
    """Integration tests (require Odoo connection)."""
    
    @pytest.fixture
    def client(self):
        """Get Odoo client (skip if no connection)."""
        try:
            from src.connectors.odoo_client import OdooClient
            from src.runtime_env import load_env_file
            load_env_file(".env")
            client = OdooClient.from_env(rpc_backend="json2")
            client.authenticate()
            return client
        except Exception as e:
            pytest.skip(f"No Odoo connection: {e}")
    
    def test_connection(self, client):
        """Test Odoo connection."""
        version = client.get_server_version()
        assert version is not None
        assert len(version) > 0
    
    def test_standard_detection(self, client):
        """Test standard detection from company."""
        from src.reporters.financial_statements import FinancialStatementReporter
        
        reporter = FinancialStatementReporter(client)
        standard = reporter._detect_standard(1)  # Assuming company ID 1
        
        assert standard is not None
        assert standard.code in STANDARDS


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
