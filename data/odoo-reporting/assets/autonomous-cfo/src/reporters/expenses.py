"""
Expense Breakdown Reporter - By vendor, category, anomalies
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from .base import BaseReporter, ReportResult


class ExpenseReporter(BaseReporter):
    """
    Generates expense breakdown including:
    - By vendor
    - By category/account
    - Monthly trends
    - Anomaly detection
    """
    
    def get_required_params(self) -> List[str]:
        return ["date_from", "date_to"]
    
    def generate(self, **params) -> ReportResult:
        date_from = params["date_from"]
        date_to = params["date_to"]
        group_by = params.get("group_by", "Category")
        include_draft = params.get("include_draft", False)
        
        # Gather data
        by_vendor = self._get_expenses_by_vendor(date_from, date_to, include_draft)
        by_category = self._get_expenses_by_category(date_from, date_to, include_draft)
        monthly = self._get_monthly_expenses(date_from, date_to, include_draft)
        totals = self._get_expense_totals(date_from, date_to, include_draft)
        anomalies = self._detect_expense_anomalies(date_from, date_to)
        
        data = {
            "period": f"{date_from} to {date_to}",
            "by_vendor": by_vendor,
            "by_category": by_category,
            "monthly": monthly,
            "totals": totals,
            "anomalies": anomalies,
            "group_by": group_by
        }
        
        # Generate visualizations
        from ..visualizers.chart_factory import ChartFactory
        from ..visualizers.whatsapp_cards import WhatsAppCardGenerator
        from ..visualizers.pdf_report import PDFReportGenerator
        
        chart_factory = ChartFactory()
        card_gen = WhatsAppCardGenerator()
        pdf_gen = PDFReportGenerator()
        
        charts = []
        
        # Expense trend
        if monthly:
            months = [m["month"] for m in monthly]
            expenses = [m["expenses"] for m in monthly]
            charts.append(chart_factory.generate_chart(
                {"x": months, "y": expenses, "y_label": "Expenses"},
                "line",
                "Monthly Expense Trend",
                f"expense_trend_{datetime.now().strftime('%Y%m%d')}.png"
            ))
        
        # Top vendors chart
        if by_vendor:
            labels = [v["vendor"][:20] for v in by_vendor[:8]]
            values = [v["amount"] for v in by_vendor[:8]]
            charts.append(chart_factory.generate_chart(
                {"labels": labels, "values": values},
                "horizontal_bar",
                "Top Vendors by Spend",
                f"top_vendors_{datetime.now().strftime('%Y%m%d')}.png"
            ))
        
        # WhatsApp cards
        cards = []
        
        # Total expenses card
        cards.append(card_gen.generate_kpi_card(
            title="Total Expenses",
            value=self.format_currency(totals.get("total", 0)),
            subtitle=f"{totals.get('bill_count', 0)} bills | Period: {date_from} to {date_to}",
            sparkline_data=[m["expenses"] for m in monthly[-6:]] if monthly else None,
            filename="expenses_total.png"
        ))
        
        # Avg monthly card
        avg_monthly = totals.get("total", 0) / max(len(monthly), 1)
        cards.append(card_gen.generate_kpi_card(
            title="Avg Monthly Spend",
            value=self.format_currency(avg_monthly),
            subtitle=f"Based on {len(monthly)} months",
            filename="expenses_avg.png"
        ))
        
        # Top vendor card
        if by_vendor:
            top = by_vendor[0]
            cards.append(card_gen.generate_kpi_card(
                title="Top Vendor",
                value=top["vendor"][:20],
                subtitle=self.format_currency(top["amount"]),
                filename="expenses_top_vendor.png"
            ))
        
        # Anomalies card
        if anomalies:
            cards.append(card_gen.generate_kpi_card(
                title="Anomalies Detected",
                value=str(len(anomalies)),
                subtitle="Unusual expense patterns",
                filename="expenses_anomalies.png"
            ))
        
        # PDF report
        sections = [
            {
                "title": "Expense Summary",
                "content": {
                    "Total Expenses": totals.get("total", 0),
                    "Bill Count": totals.get("bill_count", 0),
                    "Average Bill": totals.get("avg_bill", 0),
                    "Avg Monthly": avg_monthly
                }
            },
            {
                "title": "Top Vendors",
                "content": {v["vendor"]: self.format_currency(v["amount"]) for v in by_vendor[:10]}
            },
            {
                "title": "By Category",
                "content": {c["category"]: self.format_currency(c["amount"]) for c in by_category[:10]}
            }
        ]
        
        if anomalies:
            sections.append({
                "title": "Anomalies Detected",
                "content": [f"- {a['type']}: {a['details']}" for a in anomalies[:5]]
            })
        
        pdf_path = pdf_gen.generate_report(
            title="Expense Breakdown Report",
            subtitle=f"Period: {date_from} to {date_to}",
            sections=sections,
            metadata={"methodology": "account.move: move_type=in_invoice"},
            filename=f"expenses_{datetime.now().strftime('%Y%m%d')}.pdf"
        )
        
        summary = f"Expenses: {self.format_currency(totals.get('total', 0))} | "
        summary += f"Bills: {totals.get('bill_count', 0)} | "
        summary += f"Avg/Month: {self.format_currency(avg_monthly)}"
        
        return ReportResult(
            report_type="expenses",
            title="Expense Breakdown Report",
            period=f"{date_from} to {date_to}",
            generated_at=datetime.now(),
            data=data,
            charts=charts,
            pdf_path=pdf_path,
            whatsapp_cards=cards,
            summary=summary,
            confidence="high",
            methodology="account.move: move_type=in_invoice, state=posted"
        )
    
    def _get_expenses_by_vendor(self, date_from: str, date_to: str, include_draft: bool) -> List[Dict]:
        """Get expenses aggregated by vendor"""
        domain = [
            ("move_type", "=", "in_invoice"),
            ("invoice_date", ">=", date_from),
            ("invoice_date", "<=", date_to),
            ("partner_id", "!=", False)
        ]
        if not include_draft:
            domain.append(("state", "=", "posted"))
        
        bills = self.client.search_read(
            "account.move",
            domain=domain,
            fields=["partner_id", "amount_total"],
            limit=1000
        )
        
        vendor_totals = defaultdict(float)
        for bill in bills:
            if bill.get("partner_id"):
                vendor = bill["partner_id"][1] if isinstance(bill["partner_id"], list) else str(bill["partner_id"])
                vendor_totals[vendor] += bill["amount_total"]
        
        sorted_vendors = sorted(vendor_totals.items(), key=lambda x: x[1], reverse=True)
        return [{"vendor": v, "amount": a} for v, a in sorted_vendors]
    
    def _get_expenses_by_category(self, date_from: str, date_to: str, include_draft: bool) -> List[Dict]:
        """Get expenses by account category"""
        domain = [
            ("move_type", "=", "in_invoice"),
            ("invoice_date", ">=", date_from),
            ("invoice_date", "<=", date_to)
        ]
        if not include_draft:
            domain.append(("state", "=", "posted"))
        
        # Get journal items for expense invoices
        move_domain = domain.copy()
        moves = self.client.search_read(
            "account.move",
            domain=move_domain,
            fields=["id"],
            limit=1000
        )
        
        move_ids = [m["id"] for m in moves]
        
        if not move_ids:
            return []
        
        # Get lines grouped by account
        lines = self.client.search_read(
            "account.move.line",
            domain=[("move_id", "in", move_ids), ("account_id", "!=", False)],
            fields=["account_id", "debit"],
            limit=5000
        )
        
        category_totals = defaultdict(float)
        for line in lines:
            if line.get("account_id") and line.get("debit"):
                account = line["account_id"][1] if isinstance(line["account_id"], list) else str(line["account_id"])
                category_totals[account] += line["debit"]
        
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        return [{"category": c, "amount": a} for c, a in sorted_categories]
    
    def _get_monthly_expenses(self, date_from: str, date_to: str, include_draft: bool) -> List[Dict]:
        """Get monthly expense breakdown"""
        start = datetime.strptime(date_from, "%Y-%m-%d")
        end = datetime.strptime(date_to, "%Y-%m-%d")
        
        monthly = []
        current = start.replace(day=1)
        
        while current <= end:
            next_month = (current + timedelta(days=32)).replace(day=1)
            month_end = (next_month - timedelta(days=1)).strftime("%Y-%m-%d")
            month_start = current.strftime("%Y-%m-%d")
            
            domain = [
                ("move_type", "=", "in_invoice"),
                ("invoice_date", ">=", month_start),
                ("invoice_date", "<=", month_end)
            ]
            if not include_draft:
                domain.append(("state", "=", "posted"))
            
            bills = self.client.search_read("account.move", domain=domain, fields=["amount_total"])
            expenses = sum(b["amount_total"] for b in bills)
            
            monthly.append({
                "month": current.strftime("%Y-%m"),
                "expenses": expenses,
                "bill_count": len(bills)
            })
            
            current = next_month
        
        return monthly
    
    def _get_expense_totals(self, date_from: str, date_to: str, include_draft: bool) -> Dict:
        """Get expense totals"""
        domain = [
            ("move_type", "=", "in_invoice"),
            ("invoice_date", ">=", date_from),
            ("invoice_date", "<=", date_to)
        ]
        if not include_draft:
            domain.append(("state", "=", "posted"))
        
        bills = self.client.search_read("account.move", domain=domain, fields=["amount_total"])
        total = sum(b["amount_total"] for b in bills)
        count = len(bills)
        
        return {
            "total": total,
            "bill_count": count,
            "avg_bill": total / count if count > 0 else 0
        }
    
    def _detect_expense_anomalies(self, date_from: str, date_to: str) -> List[Dict]:
        """Detect expense anomalies"""
        anomalies = []
        
        # Check for duplicate vendor bills
        domain = [
            ("move_type", "=", "in_invoice"),
            ("state", "!=", "cancel"),
            ("invoice_date", ">=", date_from),
            ("invoice_date", "<=", date_to)
        ]
        bills = self.client.search_read(
            "account.move",
            domain=domain,
            fields=["partner_id", "ref", "amount_total"],
            limit=500
        )
        
        seen = defaultdict(list)
        for bill in bills:
            if bill.get("partner_id") and bill.get("ref"):
                key = (bill["partner_id"][0], bill["ref"])
                seen[key].append(bill)
        
        for key, duplicates in seen.items():
            if len(duplicates) > 1:
                anomalies.append({
                    "type": "Duplicate Bill",
                    "details": f"{duplicates[0]['partner_id'][1]} - Ref: {duplicates[0]['ref']} ({len(duplicates)} occurrences)"
                })
        
        # Check for unusually large bills
        amounts = [b["amount_total"] for b in bills if b.get("amount_total")]
        if amounts:
            avg = sum(amounts) / len(amounts)
            for bill in bills:
                if bill.get("amount_total", 0) > avg * 5:
                    vendor = bill.get("partner_id", ["Unknown"])[1] if bill.get("partner_id") else "Unknown"
                    anomalies.append({
                        "type": "Large Expense",
                        "details": f"{vendor}: {self.format_currency(bill['amount_total'])} (avg: {self.format_currency(avg)})"
                    })
        
        return anomalies[:10]  # Limit to top 10
