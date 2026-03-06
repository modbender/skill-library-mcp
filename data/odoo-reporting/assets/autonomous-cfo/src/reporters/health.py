"""
Financial Health Reporter - Cash flow, liquidity, burn rate analysis
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from .base import BaseReporter, ReportResult


class FinancialHealthReporter(BaseReporter):
    """
    Generates comprehensive financial health report including:
    - Cash position and liquidity
    - Burn rate and runway
    - Working capital analysis
    - Financial ratios
    """
    
    def get_required_params(self) -> List[str]:
        return ["date_from", "date_to"]
    
    def generate(self, **params) -> ReportResult:
        """Generate financial health report"""
        
        # Validate params
        issues = self.validate_params(params)
        if issues:
            raise ValueError(f"Invalid params: {', '.join(issues)}")
        
        date_from = params["date_from"]
        date_to = params["date_to"]
        include_forecast = params.get("include_forecast", True)
        company_id = params.get("company_id")
        
        # Gather data
        cash_position = self._get_cash_position(company_id)
        burn_rate = self._calculate_burn_rate(date_from, date_to, company_id)
        working_capital = self._calculate_working_capital(company_id)
        ratios = self._calculate_ratios(cash_position, working_capital)
        
        # Build report data
        data = {
            "period": f"{date_from} to {date_to}",
            "cash_position": cash_position,
            "burn_rate": burn_rate,
            "working_capital": working_capital,
            "ratios": ratios,
        }
        
        # Generate outputs
        from ..visualizers.chart_factory import ChartFactory
        from ..visualizers.whatsapp_cards import WhatsAppCardGenerator
        from ..visualizers.pdf_report import PDFReportGenerator
        
        chart_factory = ChartFactory()
        card_gen = WhatsAppCardGenerator()
        pdf_gen = PDFReportGenerator()
        
        # Generate charts
        charts = []
        
        # Cash position chart
        if cash_position.get("journals"):
            chart_data = {
                "labels": [j["name"][:20] for j in cash_position["journals"][:8]],
                "values": [j.get("balance", 0) for j in cash_position["journals"][:8]]
            }
            charts.append(chart_factory.generate_chart(
                {"labels": chart_data["labels"], "values": chart_data["values"]},
                "horizontal_bar",
                "Cash by Account",
                f"cash_position_{datetime.now().strftime('%Y%m%d')}.png"
            ))
        
        # Burn rate trend
        if burn_rate.get("monthly_burn"):
            months = [b["month"] for b in burn_rate["monthly_burn"]]
            burns = [b["burn"] for b in burn_rate["monthly_burn"]]
            charts.append(chart_factory.generate_chart(
                {"x": months, "y": burns},
                "line",
                "Monthly Burn Rate",
                f"burn_rate_{datetime.now().strftime('%Y%m%d')}.png"
            ))
        
        # Generate WhatsApp cards
        cards = []
        
        # Total liquidity card
        cards.append(card_gen.generate_kpi_card(
            title="Total Liquidity",
            value=self.format_currency(cash_position.get("total_liquidity", 0)),
            change={"percentage": ratios.get("liquidity_change_pct", 0), "direction": "up" if ratios.get("liquidity_change_pct", 0) > 0 else "down"},
            subtitle="Cash + Bank Balances",
            filename="health_liquidity.png"
        ))
        
        # Burn rate card
        cards.append(card_gen.generate_kpi_card(
            title="Monthly Burn Rate",
            value=self.format_currency(burn_rate.get("avg_monthly_burn", 0)),
            subtitle=f"Based on last {burn_rate.get('months_analyzed', 0)} months",
            filename="health_burn.png"
        ))
        
        # Runway card
        runway = burn_rate.get("runway_months", 0)
        cards.append(card_gen.generate_kpi_card(
            title="Cash Runway",
            value=f"{runway:.1f} months",
            change={"percentage": 0, "direction": "neutral"},
            subtitle="At current burn rate",
            filename="health_runway.png"
        ))
        
        # Generate PDF
        sections = [
            {
                "title": "Cash Position",
                "content": {
                    "Total Liquidity": cash_position.get("total_liquidity", 0),
                    "Bank Accounts": cash_position.get("bank_count", 0),
                    "Cash Accounts": cash_position.get("cash_count", 0),
                }
            },
            {
                "title": "Burn Rate Analysis",
                "content": {
                    "Average Monthly Burn": burn_rate.get("avg_monthly_burn", 0),
                    "Months Analyzed": burn_rate.get("months_analyzed", 0),
                    "Cash Runway (months)": burn_rate.get("runway_months", 0),
                }
            },
            {
                "title": "Working Capital",
                "content": {
                    "Current Assets": working_capital.get("current_assets", 0),
                    "Current Liabilities": working_capital.get("current_liabilities", 0),
                    "Net Working Capital": working_capital.get("net_working_capital", 0),
                }
            },
            {
                "title": "Key Ratios",
                "content": {
                    "Current Ratio": f"{ratios.get('current_ratio', 0):.2f}",
                    "Quick Ratio": f"{ratios.get('quick_ratio', 0):.2f}",
                }
            }
        ]
        
        pdf_path = pdf_gen.generate_report(
            title="Financial Health Report",
            subtitle=f"Period: {date_from} to {date_to}",
            sections=sections,
            metadata={
                "methodology": "Data sourced from Odoo account.journal, account.move, and account.account models."
            },
            filename=f"financial_health_{datetime.now().strftime('%Y%m%d')}.pdf"
        )
        
        # Build summary
        summary = f"Liquidity: {self.format_currency(cash_position.get('total_liquidity', 0))} | "
        summary += f"Burn: {self.format_currency(burn_rate.get('avg_monthly_burn', 0))}/mo | "
        summary += f"Runway: {runway:.1f} months"
        
        return ReportResult(
            report_type="financial_health",
            title="Financial Health Report",
            period=f"{date_from} to {date_to}",
            generated_at=datetime.now(),
            data=data,
            charts=charts,
            pdf_path=pdf_path,
            whatsapp_cards=cards,
            summary=summary,
            confidence="high",
            methodology="Odoo RPC queries: account.journal (balances), account.move (cash flow), account.account (working capital)",
            caveats=[
                "Burn rate calculated from posted transactions only",
                "Runway assumes constant burn rate (may vary seasonally)"
            ]
        )
    
    def _get_cash_position(self, company_id: Optional[int] = None) -> Dict[str, Any]:
        """Get current cash and bank balances"""
        domain = [("type", "in", ["bank", "cash"])]
        if company_id:
            domain.append(("company_id", "=", company_id))
        
        journals = self.client.search_read(
            "account.journal",
            domain=domain,
            fields=["name", "code", "type", "current_statement_balance"]
        )
        
        total = 0
        bank_count = 0
        cash_count = 0
        
        for j in journals:
            balance = j.get("current_statement_balance", 0) or 0
            total += balance
            if j["type"] == "bank":
                bank_count += 1
            else:
                cash_count += 1
        
        return {
            "total_liquidity": total,
            "bank_count": bank_count,
            "cash_count": cash_count,
            "journals": journals
        }
    
    def _calculate_burn_rate(self, date_from: str, date_to: str, company_id: Optional[int] = None) -> Dict[str, Any]:
        """Calculate monthly burn rate from expenses minus revenue"""
        from datetime import datetime
        
        # Get monthly breakdown
        start = datetime.strptime(date_from, "%Y-%m-%d")
        end = datetime.strptime(date_to, "%Y-%m-%d")
        
        monthly_data = []
        total_expenses = 0
        total_revenue = 0
        
        # Iterate through months in period
        current = start.replace(day=1)
        while current <= end:
            next_month = (current + timedelta(days=32)).replace(day=1)
            month_end = next_month - timedelta(days=1)
            
            month_start_str = current.strftime("%Y-%m-%d")
            month_end_str = month_end.strftime("%Y-%m-%d")
            
            # Get revenue for month
            rev_domain = [
                ("move_type", "=", "out_invoice"),
                ("state", "=", "posted"),
                ("invoice_date", ">=", month_start_str),
                ("invoice_date", "<=", month_end_str)
            ]
            revenues = self.client.search_read("account.move", domain=rev_domain, fields=["amount_total"])
            month_revenue = sum(r["amount_total"] for r in revenues)
            
            # Get expenses for month
            exp_domain = [
                ("move_type", "=", "in_invoice"),
                ("state", "=", "posted"),
                ("invoice_date", ">=", month_start_str),
                ("invoice_date", "<=", month_end_str)
            ]
            expenses = self.client.search_read("account.move", domain=exp_domain, fields=["amount_total"])
            month_expense = sum(e["amount_total"] for e in expenses)
            
            burn = month_expense - month_revenue
            monthly_data.append({
                "month": current.strftime("%Y-%m"),
                "revenue": month_revenue,
                "expenses": month_expense,
                "burn": burn
            })
            
            total_revenue += month_revenue
            total_expenses += month_expense
            
            current = next_month
        
        # Calculate averages
        months_count = len(monthly_data)
        avg_burn = (total_expenses - total_revenue) / months_count if months_count > 0 else 0
        
        # Get current liquidity for runway
        cash_pos = self._get_cash_position(company_id)
        runway = cash_pos["total_liquidity"] / avg_burn if avg_burn > 0 else float('inf')
        
        return {
            "monthly_burn": monthly_data,
            "avg_monthly_burn": avg_burn,
            "months_analyzed": months_count,
            "total_revenue": total_revenue,
            "total_expenses": total_expenses,
            "runway_months": runway
        }
    
    def _calculate_working_capital(self, company_id: Optional[int] = None) -> Dict[str, Any]:
        """Calculate working capital components"""
        domain = []
        if company_id:
            domain.append(("company_id", "=", company_id))
        
        # Get current assets (receivable, cash, inventory)
        asset_domain = domain + [
            ("account_type", "in", ["asset_receivable", "asset_cash", "asset_current"])
        ]
        assets = self.client.search_read(
            "account.account",
            domain=asset_domain,
            fields=["code", "name", "account_type", "current_balance"]
        )
        
        current_assets = sum(a.get("current_balance", 0) or 0 for a in assets)
        
        # Get current liabilities (payable)
        liability_domain = domain + [
            ("account_type", "in", ["liability_payable", "liability_current"])
        ]
        liabilities = self.client.search_read(
            "account.account",
            domain=liability_domain,
            fields=["code", "name", "account_type", "current_balance"]
        )
        
        current_liabilities = sum(l.get("current_balance", 0) or 0 for l in liabilities)
        
        return {
            "current_assets": current_assets,
            "current_liabilities": current_liabilities,
            "net_working_capital": current_assets - current_liabilities
        }
    
    def _calculate_ratios(self, cash_position: Dict, working_capital: Dict) -> Dict[str, Any]:
        """Calculate key financial ratios"""
        current_assets = working_capital.get("current_assets", 0)
        current_liabilities = working_capital.get("current_liabilities", 1)  # Avoid div by 0
        
        current_ratio = current_assets / current_liabilities if current_liabilities > 0 else 0
        
        # Quick ratio excludes inventory (we'll approximate with cash + receivables)
        quick_assets = cash_position.get("total_liquidity", 0)
        # Add receivables approximation
        quick_ratio = quick_assets / current_liabilities if current_liabilities > 0 else 0
        
        return {
            "current_ratio": current_ratio,
            "quick_ratio": quick_ratio,
            "liquidity_change_pct": 0  # Would need historical comparison
        }
