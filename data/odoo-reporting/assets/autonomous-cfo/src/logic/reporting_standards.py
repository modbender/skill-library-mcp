"""
Automatic detection of company reporting standards based on jurisdiction.
Supports IFRS, US GAAP, Ind-AS, and other local standards.
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ReportingStandard:
    """Represents an accounting reporting standard."""
    code: str
    name: str
    jurisdiction: str
    balance_sheet_order: str  # "liquidity" or "persistence"
    currency_placement: str   # "before" or "after"
    negative_format: str      # "brackets" or "minus"
    date_format: str          # "DMY", "MDY", "YMD"
    thousand_separator: str
    decimal_separator: str
    equity_disclosure: str    # "full", "abbreviated"
    cash_flow_method: str     # "indirect", "direct", "both"
    

# Global reporting standards registry
STANDARDS: Dict[str, ReportingStandard] = {
    # IFRS (International)
    "IFRS": ReportingStandard(
        code="IFRS",
        name="International Financial Reporting Standards",
        jurisdiction="International",
        balance_sheet_order="liquidity",
        currency_placement="before",
        negative_format="brackets",
        date_format="DMY",
        thousand_separator=",",
        decimal_separator=".",
        equity_disclosure="full",
        cash_flow_method="indirect",
    ),
    
    # US GAAP
    "US_GAAP": ReportingStandard(
        code="US_GAAP",
        name="United States Generally Accepted Accounting Principles",
        jurisdiction="United States",
        balance_sheet_order="liquidity",
        currency_placement="before",
        negative_format="brackets",
        date_format="MDY",
        thousand_separator=",",
        decimal_separator=".",
        equity_disclosure="full",
        cash_flow_method="both",
    ),
    
    # Ind-AS (India)
    "IND_AS": ReportingStandard(
        code="IND_AS",
        name="Indian Accounting Standards",
        jurisdiction="India",
        balance_sheet_order="persistence",
        currency_placement="before",
        negative_format="brackets",
        date_format="DMY",
        thousand_separator=",",
        decimal_separator=".",
        equity_disclosure="full",
        cash_flow_method="indirect",
    ),
    
    # UK GAAP
    "UK_GAAP": ReportingStandard(
        code="UK_GAAP",
        name="United Kingdom Generally Accepted Accounting Practice",
        jurisdiction="United Kingdom",
        balance_sheet_order="persistence",
        currency_placement="before",
        negative_format="brackets",
        date_format="DMY",
        thousand_separator=",",
        decimal_separator=".",
        equity_disclosure="full",
        cash_flow_method="indirect",
    ),
    
    # UAE (IFRS adopted)
    "UAE_IFRS": ReportingStandard(
        code="UAE_IFRS",
        name="UAE Accounting Standards (IFRS Adopted)",
        jurisdiction="United Arab Emirates",
        balance_sheet_order="liquidity",
        currency_placement="before",
        negative_format="brackets",
        date_format="DMY",
        thousand_separator=",",
        decimal_separator=".",
        equity_disclosure="full",
        cash_flow_method="indirect",
    ),
    
    # Saudi Arabia
    "SOCPA": ReportingStandard(
        code="SOCPA",
        name="Saudi Organization for Certified Public Accountants",
        jurisdiction="Saudi Arabia",
        balance_sheet_order="liquidity",
        currency_placement="before",
        negative_format="brackets",
        date_format="DMY",
        thousand_separator=",",
        decimal_separator=".",
        equity_disclosure="full",
        cash_flow_method="indirect",
    ),
    
    # European Union (IFRS mandated for listed)
    "EU_IFRS": ReportingStandard(
        code="EU_IFRS",
        name="EU IFRS (IAS Regulation)",
        jurisdiction="European Union",
        balance_sheet_order="liquidity",
        currency_placement="after",  # Many EU countries
        negative_format="brackets",
        date_format="DMY",
        thousand_separator=".",      # Many EU countries use .
        decimal_separator=",",       # Many EU countries use ,
        equity_disclosure="full",
        cash_flow_method="indirect",
    ),
    
    # China
    "CAS": ReportingStandard(
        code="CAS",
        name="Chinese Accounting Standards",
        jurisdiction="China",
        balance_sheet_order="liquidity",
        currency_placement="before",
        negative_format="brackets",
        date_format="YMD",
        thousand_separator=",",
        decimal_separator=".",
        equity_disclosure="full",
        cash_flow_method="direct",
    ),
    
    # Japan
    "JGAAP": ReportingStandard(
        code="JGAAP",
        name="Japanese Generally Accepted Accounting Principles",
        jurisdiction="Japan",
        balance_sheet_order="liquidity",
        currency_placement="before",
        negative_format="brackets",
        date_format="YMD",
        thousand_separator=",",
        decimal_separator=".",
        equity_disclosure="full",
        cash_flow_method="indirect",
    ),
    
    # Canada (ASPE/IFRS)
    "ASPE": ReportingStandard(
        code="ASPE",
        name="Accounting Standards for Private Enterprises (Canada)",
        jurisdiction="Canada",
        balance_sheet_order="liquidity",
        currency_placement="before",
        negative_format="brackets",
        date_format="MDY",
        thousand_separator=",",
        decimal_separator=".",
        equity_disclosure="full",
        cash_flow_method="indirect",
    ),
    
    # Australia
    "AASB": ReportingStandard(
        code="AASB",
        name="Australian Accounting Standards Board",
        jurisdiction="Australia",
        balance_sheet_order="liquidity",
        currency_placement="before",
        negative_format="brackets",
        date_format="DMY",
        thousand_separator=",",
        decimal_separator=".",
        equity_disclosure="full",
        cash_flow_method="indirect",
    ),
}

# Country to standard mapping
COUNTRY_STANDARD_MAP: Dict[str, str] = {
    # IFRS jurisdictions
    "AE": "UAE_IFRS",     # UAE
    "SA": "SOCPA",        # Saudi Arabia
    "AU": "AASB",         # Australia
    "NZ": "AASB",         # New Zealand (similar to AASB)
    
    # IFRS default for many
    "GB": "UK_GAAP",      # UK
    "DE": "EU_IFRS",      # Germany
    "FR": "EU_IFRS",      # France
    "NL": "EU_IFRS",      # Netherlands
    "ES": "EU_IFRS",      # Spain
    "IT": "EU_IFRS",      # Italy
    "BE": "EU_IFRS",      # Belgium
    "SE": "EU_IFRS",      # Sweden
    "PL": "EU_IFRS",      # Poland
    
    # Specific standards
    "US": "US_GAAP",      # USA
    "IN": "IND_AS",       # India
    "CN": "CAS",          # China
    "JP": "JGAAP",        # Japan
    "CA": "ASPE",         # Canada
    
    # Default to IFRS
    "DEFAULT": "IFRS",
}


class ReportingStandardDetector:
    """Detects the appropriate reporting standard for a company."""
    
    def __init__(self, client):
        self.client = client
    
    def detect(self, company_id: int) -> ReportingStandard:
        """
        Detect the reporting standard for a company based on:
        1. Company country/jurisdiction
        2. Chart of accounts structure
        3. Fiscal year configuration
        """
        # Get company info
        companies = self.client.read("res.company", [company_id], ["country_id", "name", "currency_id"])
        if not companies:
            return STANDARDS["IFRS"]
        
        company = companies[0]
        country_id = company.get("country_id")
        
        # Detect from country
        if country_id:
            country_code = country_id[1] if isinstance(country_id, (list, tuple)) else country_id
            # Get country code from Odoo (might be name or code)
            countries = self.client.read("res.country", [country_id[0] if isinstance(country_id, (list, tuple)) else country_id], ["code"])
            if countries:
                country_code = countries[0].get("code", "DEFAULT")
                standard_code = COUNTRY_STANDARD_MAP.get(country_code, COUNTRY_STANDARD_MAP["DEFAULT"])
                return STANDARDS[standard_code]
        
        # Default to IFRS
        return STANDARDS["IFRS"]
    
    def get_standard(self, code: str) -> Optional[ReportingStandard]:
        """Get a reporting standard by code."""
        return STANDARDS.get(code)
    
    def list_standards(self) -> List[str]:
        """List all available reporting standards."""
        return list(STANDARDS.keys())


def format_amount(amount: float, standard: ReportingStandard, currency: str = "") -> str:
    """Format an amount according to the reporting standard."""
    # Format number
    abs_amount = abs(amount)
    
    # Thousand separator
    if abs_amount >= 1000:
        formatted = f"{abs_amount:,.2f}"
        if standard.thousand_separator != ",":
            formatted = formatted.replace(",", "TEMP").replace(".", standard.decimal_separator).replace("TEMP", standard.thousand_separator)
    else:
        formatted = f"{abs_amount:.2f}".replace(".", standard.decimal_separator)
    
    # Negative format
    if amount < 0:
        if standard.negative_format == "brackets":
            formatted = f"({formatted})"
        else:
            formatted = f"-{formatted}"
    
    # Currency placement
    if currency:
        if standard.currency_placement == "before":
            formatted = f"{currency} {formatted}"
        else:
            formatted = f"{formatted} {currency}"
    
    return formatted


def format_date(date_str: str, standard: ReportingStandard) -> str:
    """Format a date according to the reporting standard."""
    from datetime import datetime
    
    if not date_str:
        return ""
    
    # Parse ISO date
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return date_str
    
    # Format according to standard
    if standard.date_format == "DMY":
        return dt.strftime("%d/%m/%Y")
    elif standard.date_format == "MDY":
        return dt.strftime("%m/%d/%Y")
    else:  # YMD
        return dt.strftime("%Y/%m/%d")


def get_statement_title(statement_type: str, standard: ReportingStandard) -> str:
    """Get the appropriate title for a financial statement."""
    titles = {
        "balance_sheet": {
            "IFRS": "Statement of Financial Position",
            "US_GAAP": "Balance Sheet",
            "IND_AS": "Balance Sheet",
            "DEFAULT": "Statement of Financial Position",
        },
        "profit_loss": {
            "IFRS": "Statement of Profit or Loss and Other Comprehensive Income",
            "US_GAAP": "Statement of Income",
            "IND_AS": "Statement of Profit and Loss",
            "DEFAULT": "Statement of Profit or Loss",
        },
        "cash_flow": {
            "IFRS": "Statement of Cash Flows",
            "US_GAAP": "Statement of Cash Flows",
            "IND_AS": "Cash Flow Statement",
            "DEFAULT": "Statement of Cash Flows",
        },
        "equity": {
            "IFRS": "Statement of Changes in Equity",
            "US_GAAP": "Statement of Stockholders' Equity",
            "IND_AS": "Statement of Changes in Equity",
            "DEFAULT": "Statement of Changes in Equity",
        },
    }
    
    statement_titles = titles.get(statement_type, {})
    return statement_titles.get(standard.code, statement_titles.get("DEFAULT", statement_type.replace("_", " ").title()))
