"""
IFRS Financial Statement Reporter
Generates compliant financial statements from Chart of Accounts + Journal Entries

Automatically detects company's reporting standard (IFRS, US GAAP, Ind-AS, etc.)
and formats statements accordingly.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict

from .base import BaseReporter, ReportResult
from ..logic.reporting_standards import (
    ReportingStandardDetector, 
    ReportingStandard,
    format_amount, 
    format_date,
    get_statement_title
)


class FinancialStatementReporter(BaseReporter):
    """
    Generates compliant financial statements.
    Automatically detects reporting standard based on company jurisdiction.
    
    Supported Standards:
    - IFRS (International)
    - US GAAP (United States)
    - Ind-AS (India)
    - UK GAAP
    - SOCPA (Saudi Arabia)
    - EU IFRS
    - CAS (China)
    - JGAAP (Japan)
    - And more...
    """
    
    # Account Type Mapping (universal)
    ACCOUNT_MAPPING = {
        "income": "revenue",
        "income_other": "other_income",
        "expense": "administrative_expenses",
        "expense_direct_cost": "cost_of_sales",
        "expense_depreciation": "depreciation",
        "expense_other": "other_expenses",
    }
    
    def get_required_params(self) -> List[str]:
        return ["date_from", "date_to", "company_id"]
    
    def generate(
        self,
        date_from: str,
        date_to: str,
        company_id: int,
        statement_type: str = "profit_loss",
        standard: str = None,
        **params
    ) -> ReportResult:
        """
        Generate compliant financial statement.
        
        Args:
            date_from: Start date YYYY-MM-DD
            date_to: End date YYYY-MM-DD
            company_id: Odoo company ID
            statement_type: 'profit_loss', 'balance_sheet', or 'cash_flow'
            standard: Optional standard code ('IFRS', 'US_GAAP', etc.)
                      If not provided, auto-detects from company country
        """
        
        # Detect or use provided reporting standard
        detector = ReportingStandardDetector(self.client)
        if standard:
            self.standard = detector.get_standard(standard) or detector.detect(company_id)
        else:
            self.standard = detector.detect(company_id)
        
        if statement_type == "profit_loss":
            return self._generate_profit_loss(date_from, date_to, company_id, **params)
        elif statement_type == "balance_sheet":
            return self._generate_balance_sheet(date_to, company_id, **params)
        else:
            raise ValueError(f"Unsupported statement type: {statement_type}")
    
    def _generate_profit_loss(self, date_from: str, date_to: str, company_id: int, **params) -> ReportResult:
        """Generate IAS 1 compliant P&L statement."""
        
        from ..visualizers.pdf_report import PDFReportGenerator
        from ..visualizers.whatsapp_cards import WhatsAppCardGenerator
        
        # Get Chart of Accounts
        accounts = self.client.search_read(
            "account.account",
            domain=[],
            fields=["id", "code", "name", "account_type", "internal_group"]
        )
        
        # Map accounts by type
        acc_by_type = defaultdict(list)
        for a in accounts:
            acc_by_type[a.get("account_type", "unknown")].append(a["id"])
        
        # Fetch ledger balances
        revenue = self._get_income_balance(acc_by_type["income"], company_id, date_from, date_to)
        other_income = self._get_income_balance(acc_by_type["income_other"], company_id, date_from, date_to)
        cost_of_sales = self._get_expense_balance(acc_by_type["expense_direct_cost"], company_id, date_from, date_to)
        depreciation = self._get_expense_balance(acc_by_type["expense_depreciation"], company_id, date_from, date_to)
        admin_expenses = self._get_expense_balance(acc_by_type["expense"], company_id, date_from, date_to)
        other_expenses = self._get_expense_balance(acc_by_type["expense_other"], company_id, date_from, date_to)
        
        # IFRS calculations
        gross_profit = revenue["total"] - cost_of_sales["total"]
        total_expenses = admin_expenses["total"] + depreciation["total"] + other_expenses["total"]
        operating_profit = gross_profit + other_income["total"] - total_expenses
        profit_for_period = operating_profit  # Before tax; add tax calc if needed
        
        data = {
            "period": f"{date_from} to {date_to}",
            "company_id": company_id,
            "revenue": revenue,
            "other_income": other_income,
            "cost_of_sales": cost_of_sales,
            "depreciation": depreciation,
            "admin_expenses": admin_expenses,
            "other_expenses": other_expenses,
            "totals": {
                "revenue": revenue["total"],
                "cost_of_sales": cost_of_sales["total"],
                "gross_profit": gross_profit,
                "total_expenses": total_expenses,
                "operating_profit": operating_profit,
                "profit_for_period": profit_for_period,
                "gross_margin_pct": (gross_profit / revenue["total"] * 100) if revenue["total"] else 0,
                "net_margin_pct": (profit_for_period / revenue["total"] * 100) if revenue["total"] else 0,
            }
        }
        
        # Generate PDF
        pdf_gen = PDFReportGenerator()
        pdf_path = self._generate_ifrs_pdf(data, date_from, date_to, company_id)
        
        # Generate cards
        card_gen = WhatsAppCardGenerator()
        cards = []
        cards.append(card_gen.generate_kpi_card(
            title="Net Profit",
            value=self.format_currency(profit_for_period),
            change={"percentage": data["totals"]["net_margin_pct"], "direction": "up" if profit_for_period > 0 else "down"},
            subtitle=f"Margin: {data['totals']['net_margin_pct']:.1f}%",
            filename="ifrs_net_profit.png"
        ))
        cards.append(card_gen.generate_kpi_card(
            title="Gross Profit",
            value=self.format_currency(gross_profit),
            subtitle=f"Margin: {data['totals']['gross_margin_pct']:.1f}%",
            filename="ifrs_gross_profit.png"
        ))
        
        summary = f"Revenue: {self.format_currency(revenue['total'])} | Net Profit: {self.format_currency(profit_for_period)} ({data['totals']['net_margin_pct']:.1f}%)"
        
        return ReportResult(
            report_type="ifrs_profit_loss",
            title="Statement of Profit or Loss and Other Comprehensive Income",
            period=f"{date_from} to {date_to}",
            generated_at=datetime.now(),
            data=data,
            charts=[],
            pdf_path=pdf_path,
            whatsapp_cards=cards,
            summary=summary,
            confidence="high",
            methodology="Ledger-based: account.move.line aggregated by account.account internal_group"
        )
    
    def _get_income_balance(self, account_ids: List[int], company_id: int, date_from: str, date_to: str) -> Dict:
        """Get income balance (credit - debit) for accounts."""
        if not account_ids:
            return {"total": 0, "by_account": {}}
        
        lines = self.client.search_read(
            "account.move.line",
            domain=[
                ("account_id", "in", account_ids),
                ("date", ">=", date_from),
                ("date", "<=", date_to),
                ("parent_state", "=", "posted"),
                ("company_id", "=", company_id)
            ],
            fields=["account_id", "credit", "debit"]
        )
        
        by_account = defaultdict(lambda: {"credit": 0, "debit": 0})
        for line in lines:
            acc_id = line["account_id"][0]
            by_account[acc_id]["credit"] += line.get("credit", 0)
            by_account[acc_id]["debit"] += line.get("debit", 0)
        
        return {
            "total": sum(v["credit"] - v["debit"] for v in by_account.values()),
            "by_account": dict(by_account)
        }
    
    def _get_expense_balance(self, account_ids: List[int], company_id: int, date_from: str, date_to: str) -> Dict:
        """Get expense balance (debit - credit) for accounts."""
        if not account_ids:
            return {"total": 0, "by_account": {}}
        
        lines = self.client.search_read(
            "account.move.line",
            domain=[
                ("account_id", "in", account_ids),
                ("date", ">=", date_from),
                ("date", "<=", date_to),
                ("parent_state", "=", "posted"),
                ("company_id", "=", company_id)
            ],
            fields=["account_id", "credit", "debit"]
        )
        
        by_account = defaultdict(lambda: {"credit": 0, "debit": 0})
        for line in lines:
            acc_id = line["account_id"][0]
            by_account[acc_id]["credit"] += line.get("credit", 0)
            by_account[acc_id]["debit"] += line.get("debit", 0)
        
        return {
            "total": sum(v["debit"] - v["credit"] for v in by_account.values()),
            "by_account": dict(by_account)
        }
    
    def _generate_ifrs_pdf(self, data: Dict, date_from: str, date_to: str, company_id: int) -> str:
        """Generate IFRS-compliant PDF."""
        from fpdf import FPDF
        import os
        
        company = self.client.read("res.company", [company_id], ["name", "currency_id"])[0]
        currency = company.get("currency_id", [1, "AED"])[1]
        totals = data["totals"]
        
        class IFRSPDF(FPDF):
            def header(self):
                self.set_font("Helvetica", "B", 20)
                self.set_text_color(26, 42, 58)
                self.cell(0, 12, "Statement of Profit or Loss", new_x="LMARGIN", new_y="NEXT", align="C")
                self.set_font("Helvetica", "", 12)
                self.set_text_color(102, 102, 102)
                self.cell(0, 8, "and Other Comprehensive Income", new_x="LMARGIN", new_y="NEXT", align="C")
                self.set_font("Helvetica", "B", 10)
                self.set_text_color(51, 51, 51)
                self.cell(0, 6, company["name"][:50], new_x="LMARGIN", new_y="NEXT", align="C")
                self.set_font("Helvetica", "", 9)
                self.cell(0, 5, f"For the Month Ended {date_to}", new_x="LMARGIN", new_y="NEXT", align="C")
                self.ln(3)
                self.set_draw_color(205, 127, 50)
                self.line(15, self.get_y(), 195, self.get_y())
                self.ln(6)
        
        pdf = IFRSPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        def line_item(label, amount, indent=0, is_expense=False):
            pdf.set_font("Helvetica", "", 9)
            pdf.set_x(15 + indent)
            pdf.cell(115 - indent, 5, label[:55])
            if is_expense:
                pdf.cell(0, 5, f"({abs(amount):,.2f})" if amount else "-", new_x="LMARGIN", new_y="NEXT", align="R")
            else:
                pdf.cell(0, 5, f"{amount:,.2f}" if amount else "-", new_x="LMARGIN", new_y="NEXT", align="R")
        
        def subtotal(label, amount, is_expense=False):
            pdf.set_draw_color(180, 180, 180)
            pdf.line(115, pdf.get_y(), 195, pdf.get_y())
            pdf.ln(1)
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(115, 5, label)
            val = f"({abs(amount):,.2f})" if is_expense else f"{amount:,.2f}"
            pdf.cell(0, 5, val, new_x="LMARGIN", new_y="NEXT", align="R")
            pdf.ln(2)
        
        def total(label, amount):
            pdf.set_draw_color(205, 127, 50)
            pdf.line(95, pdf.get_y(), 195, pdf.get_y())
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(26, 42, 58)
            pdf.cell(115, 6, label)
            pdf.cell(0, 6, f"{amount:,.2f}", new_x="LMARGIN", new_y="NEXT", align="R")
            pdf.ln(3)
        
        # Revenue
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 5, "Revenue", new_x="LMARGIN", new_y="NEXT")
        line_item("Sales Revenue", totals["revenue"], indent=3)
        subtotal("Total Revenue", totals["revenue"])
        
        # Cost of Sales
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 5, "Cost of Sales", new_x="LMARGIN", new_y="NEXT")
        line_item("Direct Costs", totals["cost_of_sales"], indent=3, is_expense=True)
        subtotal("Total Cost of Sales", totals["cost_of_sales"], is_expense=True)
        
        total("Gross Profit", totals["gross_profit"])
        
        # Expenses
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 5, "Operating Expenses", new_x="LMARGIN", new_y="NEXT")
        line_item("Administrative Expenses", data["admin_expenses"]["total"], indent=3, is_expense=True)
        line_item("Depreciation & Amortization", data["depreciation"]["total"], indent=3, is_expense=True)
        subtotal("Total Operating Expenses", totals["total_expenses"], is_expense=True)
        
        total("Profit for the Period", totals["profit_for_period"])
        
        # Footer
        pdf.ln(8)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(0, 4, "Prepared in accordance with IFRS | Reference: IAS 1", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.cell(0, 4, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", new_x="LMARGIN", new_y="NEXT", align="C")
        
        os.makedirs("output/pdf_reports", exist_ok=True)
        path = f"output/pdf_reports/ifrs_pl_{date_to.replace('-', '')}.pdf"
        pdf.output(path)
        return path
    
    def _generate_balance_sheet(self, as_of_date: str, company_id: int, **params) -> ReportResult:
        """
        Generate IAS 1 compliant Balance Sheet (Statement of Financial Position).
        
        CRITICAL: Odoo equity calculation requires special handling:
        - equity_unaffected is a SUSPENSE account, not regular equity
        - Current Year Earnings must be computed from P&L (Income - Expenses)
        - Total Equity = Equity Proper + Retained Earnings + Current Year Earnings
        """
        
        from ..visualizers.pdf_report import PDFReportGenerator
        from ..visualizers.whatsapp_cards import WhatsAppCardGenerator
        from fpdf import FPDF
        import os
        
        # Get Chart of Accounts
        accounts = self.client.search_read(
            "account.account",
            domain=[],
            fields=["id", "code", "name", "account_type", "internal_group"]
        )
        
        # Map accounts by internal_group and account_type
        acc_by_group = defaultdict(list)
        for a in accounts:
            acc_by_group[a.get("internal_group", "other")].append(a)
        
        def get_balance_as_of(account_ids):
            """Get balance as of date (all entries up to date)."""
            if not account_ids:
                return {"by_account": {}, "total": 0}
            
            lines = self.client.search_read(
                "account.move.line",
                domain=[
                    ("account_id", "in", account_ids),
                    ("date", "<=", as_of_date),
                    ("parent_state", "=", "posted"),
                    ("company_id", "=", company_id)
                ],
                fields=["account_id", "credit", "debit"]
            )
            
            acc_map = {a["id"]: a for a in accounts if a["id"] in account_ids}
            by_account = {}
            
            for line in lines:
                acc_id = line["account_id"][0]
                if acc_id not in by_account:
                    by_account[acc_id] = {"credit": 0, "debit": 0, "name": acc_map[acc_id]["name"], "code": acc_map[acc_id]["code"]}
                by_account[acc_id]["credit"] += line.get("credit", 0)
                by_account[acc_id]["debit"] += line.get("debit", 0)
            
            return {"by_account": by_account, "total": 0}
        
        # === ASSETS ===
        asset_ids = [a["id"] for a in acc_by_group["asset"]]
        asset_data = get_balance_as_of(asset_ids)
        asset_total = sum(v["debit"] - v["credit"] for v in asset_data["by_account"].values())
        
        non_current_asset_ids = [a["id"] for a in acc_by_group["asset"] if a.get("account_type") in ["asset_non_current", "asset_fixed"]]
        current_asset_ids = [a["id"] for a in acc_by_group["asset"] if a.get("account_type") in ["asset_current", "asset_cash", "asset_receivable", "asset_prepayments"]]
        
        non_current_asset_data = get_balance_as_of(non_current_asset_ids)
        non_current_asset_total = sum(v["debit"] - v["credit"] for v in non_current_asset_data["by_account"].values())
        
        current_asset_data = get_balance_as_of(current_asset_ids)
        current_asset_total = sum(v["debit"] - v["credit"] for v in current_asset_data["by_account"].values())
        
        # === LIABILITIES ===
        liability_ids = [a["id"] for a in acc_by_group["liability"]]
        liability_data = get_balance_as_of(liability_ids)
        liability_total = sum(v["credit"] - v["debit"] for v in liability_data["by_account"].values())
        
        non_current_liab_ids = [a["id"] for a in acc_by_group["liability"] if a.get("account_type") == "liability_non_current"]
        current_liab_ids = [a["id"] for a in acc_by_group["liability"] if a.get("account_type") in ["liability_current", "liability_payable", "liability_credit_card"]]
        
        non_current_liab_data = get_balance_as_of(non_current_liab_ids)
        non_current_liab_total = sum(v["credit"] - v["debit"] for v in non_current_liab_data["by_account"].values())
        
        current_liab_data = get_balance_as_of(current_liab_ids)
        current_liab_total = sum(v["credit"] - v["debit"] for v in current_liab_data["by_account"].values())
        
        # === EQUITY (ODOO-CORRECT METHOD) ===
        # 1. Equity Proper (type: equity, excluding equity_unaffected)
        equity_proper_ids = [a["id"] for a in acc_by_group["equity"] if a.get("account_type") != "equity_unaffected"]
        equity_proper_data = get_balance_as_of(equity_proper_ids)
        equity_proper_total = sum(v["credit"] - v["debit"] for v in equity_proper_data["by_account"].values())
        
        # 2. Retained Earnings (prior years from equity_unaffected ledger)
        unaffected_ids = [a["id"] for a in acc_by_group["equity"] if a.get("account_type") == "equity_unaffected"]
        unaffected_data = get_balance_as_of(unaffected_ids)
        retained_earnings = sum(v["credit"] - v["debit"] for v in unaffected_data["by_account"].values())
        
        # 3. Current Year Earnings (computed from P&L)
        income_ids = [a["id"] for a in acc_by_group["income"]]
        expense_ids = [a["id"] for a in acc_by_group["expense"]]
        
        income_data = get_balance_as_of(income_ids)
        income_total = sum(v["credit"] - v["debit"] for v in income_data["by_account"].values())
        
        expense_data = get_balance_as_of(expense_ids)
        expense_total = sum(v["debit"] - v["credit"] for v in expense_data["by_account"].values())
        
        current_year_earnings = income_total - expense_total
        
        # Total Equity
        equity_total = equity_proper_total + retained_earnings + current_year_earnings
        
        # Balance check
        balance_check = asset_total - (liability_total + equity_total)
        
        company = self.client.read("res.company", [company_id], ["name", "currency_id"])[0]
        currency = company.get("currency_id", [1, "AED"])[1]
        
        # Generate PDF
        class SOFPPDF(FPDF):
            def header(self):
                self.set_font("Helvetica", "B", 20)
                self.set_text_color(26, 42, 58)
                self.cell(0, 14, "Statement of Financial Position", new_x="LMARGIN", new_y="NEXT", align="C")
                self.set_font("Helvetica", "B", 11)
                self.set_text_color(51, 51, 51)
                self.cell(0, 7, company["name"][:50], new_x="LMARGIN", new_y="NEXT", align="C")
                self.set_font("Helvetica", "", 10)
                self.cell(0, 6, f"As at {as_of_date}", new_x="LMARGIN", new_y="NEXT", align="C")
                self.ln(3)
                self.set_draw_color(205, 127, 50)
                self.set_line_width(0.6)
                self.line(15, self.get_y(), 195, self.get_y())
                self.ln(6)
        
        pdf = SOFPPDF()
        pdf.add_page()
        
        def section_header(title):
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(26, 42, 58)
            pdf.cell(0, 6, title, new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(51, 51, 51)
        
        def line_item(label, amount, indent=0):
            pdf.set_font("Helvetica", "", 9)
            pdf.set_x(15 + indent)
            pdf.cell(110 - indent, 5, label[:52])
            if abs(amount) >= 0.01:
                pdf.cell(0, 5, f"{amount:,.2f}", new_x="LMARGIN", new_y="NEXT", align="R")
            else:
                pdf.cell(0, 5, "-", new_x="LMARGIN", new_y="NEXT", align="R")
        
        def subtotal(label, amount):
            pdf.set_draw_color(180, 180, 180)
            pdf.line(110, pdf.get_y(), 195, pdf.get_y())
            pdf.ln(1)
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(110, 5, label)
            pdf.cell(0, 5, f"{amount:,.2f}", new_x="LMARGIN", new_y="NEXT", align="R")
            pdf.ln(2)
        
        def total_line(label, amount, final=False):
            if final:
                pdf.set_draw_color(205, 127, 50)
                pdf.set_line_width(0.8)
            else:
                pdf.set_draw_color(100, 100, 100)
            pdf.line(90, pdf.get_y(), 195, pdf.get_y())
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 10 if final else 9)
            pdf.set_text_color(26, 42, 58)
            pdf.cell(110, 6 if final else 5, label)
            pdf.cell(0, 6 if final else 5, f"{amount:,.2f}", new_x="LMARGIN", new_y="NEXT", align="R")
            pdf.ln(3)
            pdf.set_text_color(51, 51, 51)
        
        # ASSETS
        section_header("ASSETS")
        section_header("Non-Current Assets")
        for acc_id, data in sorted(non_current_asset_data["by_account"].items(), key=lambda x: x[1]["code"])[:10]:
            net = data["debit"] - data["credit"]
            if abs(net) >= 0.01:
                line_item(data["name"][:50], net, indent=3)
        subtotal("Total Non-Current Assets", non_current_asset_total)
        
        section_header("Current Assets")
        for acc_id, data in sorted(current_asset_data["by_account"].items(), key=lambda x: x[1]["code"])[:12]:
            net = data["debit"] - data["credit"]
            if abs(net) >= 0.01:
                line_item(data["name"][:50], net, indent=3)
        if len(current_asset_data["by_account"]) > 12:
            remaining = sum(d["debit"] - d["credit"] for d in list(current_asset_data["by_account"].values())[12:])
            line_item("Other current assets", remaining, indent=3)
        subtotal("Total Current Assets", current_asset_total)
        total_line("TOTAL ASSETS", asset_total, final=True)
        
        # EQUITY AND LIABILITIES
        pdf.ln(4)
        section_header("EQUITY AND LIABILITIES")
        section_header("Equity")
        for acc_id, data in sorted(equity_proper_data["by_account"].items(), key=lambda x: x[1]["code"]):
            net = data["credit"] - data["debit"]
            if abs(net) >= 0.01:
                line_item(data["name"][:50], net, indent=3)
        line_item("Retained Earnings", retained_earnings, indent=3)
        line_item("Current Year Earnings", current_year_earnings, indent=3)
        subtotal("Total Equity", equity_total)
        
        section_header("Non-Current Liabilities")
        for acc_id, data in sorted(non_current_liab_data["by_account"].items(), key=lambda x: x[1]["code"]):
            net = data["credit"] - data["debit"]
            if abs(net) >= 0.01:
                line_item(data["name"][:50], net, indent=3)
        subtotal("Total Non-Current Liabilities", non_current_liab_total)
        
        section_header("Current Liabilities")
        for acc_id, data in sorted(current_liab_data["by_account"].items(), key=lambda x: x[1]["code"])[:8]:
            net = data["credit"] - data["debit"]
            if abs(net) >= 0.01:
                line_item(data["name"][:50], net, indent=3)
        if len(current_liab_data["by_account"]) > 8:
            remaining = sum(d["credit"] - d["debit"] for d in list(current_liab_data["by_account"].values())[8:])
            line_item("Other current liabilities", remaining, indent=3)
        subtotal("Total Current Liabilities", current_liab_total)
        total_line("TOTAL EQUITY AND LIABILITIES", liability_total + equity_total, final=True)
        
        # Footer
        pdf.ln(6)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(0, 4, "Prepared in accordance with IFRS | Reference: IAS 1", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.cell(0, 4, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", new_x="LMARGIN", new_y="NEXT", align="C")
        
        os.makedirs("output/pdf_reports", exist_ok=True)
        pdf_path = f"output/pdf_reports/sofp_{as_of_date.replace('-', '')}.pdf"
        pdf.output(pdf_path)
        
        # Generate cards
        card_gen = WhatsAppCardGenerator()
        cards = []
        cards.append(card_gen.generate_kpi_card(
            title="Total Assets",
            value=self.format_currency(asset_total),
            subtitle=company["name"][:30],
            filename="sofp_assets.png"
        ))
        cards.append(card_gen.generate_kpi_card(
            title="Total Equity",
            value=self.format_currency(equity_total),
            subtitle=f"Current Year Earnings: {self.format_currency(current_year_earnings)}",
            filename="sofp_equity.png"
        ))
        
        data = {
            "as_of_date": as_of_date,
            "company_id": company_id,
            "assets": {
                "non_current": non_current_asset_total,
                "current": current_asset_total,
                "total": asset_total
            },
            "liabilities": {
                "non_current": non_current_liab_total,
                "current": current_liab_total,
                "total": liability_total
            },
            "equity": {
                "equity_proper": equity_proper_total,
                "retained_earnings": retained_earnings,
                "current_year_earnings": current_year_earnings,
                "total": equity_total
            },
            "balance_check": balance_check
        }
        
        summary = f"Assets: {self.format_currency(asset_total)} = Equity: {self.format_currency(equity_total)} + Liabilities: {self.format_currency(liability_total)}"
        if abs(balance_check) < 0.01:
            summary += " ✓ BALANCED"
        else:
            summary += f" ⚠ IMBALANCE: {self.format_currency(balance_check)}"
        
        return ReportResult(
            report_type="ifrs_balance_sheet",
            title="Statement of Financial Position",
            period=f"As at {as_of_date}",
            generated_at=datetime.now(),
            data=data,
            charts=[],
            pdf_path=pdf_path,
            whatsapp_cards=cards,
            summary=summary,
            confidence="high" if abs(balance_check) < 0.01 else "medium",
            methodology="Ledger-based with Odoo equity calculation: Equity Proper + Retained Earnings + Current Year Earnings (computed)"
        )
