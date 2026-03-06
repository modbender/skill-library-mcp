"""
Revenue Analytics Reporter - MoM trends, top customers, category breakdown
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from .base import BaseReporter, ReportResult


class RevenueReporter(BaseReporter):
    """
    Generates revenue analytics including:
    - Month-over-month trends
    - Top customers by revenue
    - Revenue by product/category
    - Growth analysis
    """
    
    def get_required_params(self) -> List[str]:
        return ["date_from", "date_to"]
    
    def generate(self, **params) -> ReportResult:
        date_from = params["date_from"]
        date_to = params["date_to"]
        breakdown = params.get("breakdown", "Month")
        top_n = params.get("top_n", 10)
        
        # Gather data
        monthly_trends = self._get_monthly_revenue(date_from, date_to)
        top_customers = self._get_top_customers(date_from, date_to, top_n)
        totals = self._get_totals(date_from, date_to)
        
        data = {
            "period": f"{date_from} to {date_to}",
            "monthly_trends": monthly_trends,
            "top_customers": top_customers,
            "totals": totals,
            "breakdown": breakdown
        }
        
        # Generate visualizations
        from ..visualizers.chart_factory import ChartFactory
        from ..visualizers.whatsapp_cards import WhatsAppCardGenerator
        from ..visualizers.pdf_report import PDFReportGenerator
        
        chart_factory = ChartFactory()
        card_gen = WhatsAppCardGenerator()
        pdf_gen = PDFReportGenerator()
        
        charts = []
        
        # Revenue trend line
        if monthly_trends:
            months = [m["month"] for m in monthly_trends]
            revenues = [m["revenue"] for m in monthly_trends]
            charts.append(chart_factory.generate_chart(
                {"x": months, "y": revenues, "y_label": "Revenue"},
                "line",
                "Monthly Revenue Trend",
                f"revenue_trend_{datetime.now().strftime('%Y%m%d')}.png"
            ))
        
        # Top customers bar chart
        if top_customers:
            labels = [c["name"][:25] for c in top_customers[:8]]
            values = [c["revenue"] for c in top_customers[:8]]
            charts.append(chart_factory.generate_chart(
                {"labels": labels, "values": values},
                "horizontal_bar",
                "Top Customers by Revenue",
                f"top_customers_{datetime.now().strftime('%Y%m%d')}.png"
            ))
        
        # WhatsApp cards
        cards = []
        
        # Total revenue card
        cards.append(card_gen.generate_kpi_card(
            title="Total Revenue",
            value=self.format_currency(totals.get("total_revenue", 0)),
            subtitle=f"Period: {date_from} to {date_to}",
            sparkline_data=[m["revenue"] for m in monthly_trends[-6:]] if monthly_trends else None,
            filename="revenue_total.png"
        ))
        
        # Growth card
        growth_pct = totals.get("growth_pct", 0)
        cards.append(card_gen.generate_kpi_card(
            title="Period Growth",
            value=f"{growth_pct:+.1f}%",
            change={"percentage": abs(growth_pct), "direction": "up" if growth_pct > 0 else "down"},
            subtitle="vs previous period",
            filename="revenue_growth.png"
        ))
        
        # Top customer card
        if top_customers:
            top = top_customers[0]
            cards.append(card_gen.generate_kpi_card(
                title="Top Customer",
                value=top["name"][:20],
                subtitle=self.format_currency(top["revenue"]),
                filename="revenue_top_customer.png"
            ))
        
        # PDF report
        sections = [
            {
                "title": "Revenue Summary",
                "content": {
                    "Total Revenue": totals.get("total_revenue", 0),
                    "Invoice Count": totals.get("invoice_count", 0),
                    "Average Invoice": totals.get("avg_invoice", 0),
                    "Growth vs Prior Period": f"{growth_pct:+.1f}%"
                }
            },
            {
                "title": "Top Customers",
                "content": {c["name"]: self.format_currency(c["revenue"]) for c in top_customers[:10]}
            }
        ]
        
        pdf_path = pdf_gen.generate_report(
            title="Revenue Analytics Report",
            subtitle=f"Period: {date_from} to {date_to}",
            sections=sections,
            metadata={"methodology": "Odoo account.move (out_invoice, posted)"},
            filename=f"revenue_{datetime.now().strftime('%Y%m%d')}.pdf"
        )
        
        summary = f"Revenue: {self.format_currency(totals.get('total_revenue', 0))} | "
        summary += f"Growth: {growth_pct:+.1f}% | "
        summary += f"Invoices: {totals.get('invoice_count', 0)}"
        
        return ReportResult(
            report_type="revenue",
            title="Revenue Analytics Report",
            period=f"{date_from} to {date_to}",
            generated_at=datetime.now(),
            data=data,
            charts=charts,
            pdf_path=pdf_path,
            whatsapp_cards=cards,
            summary=summary,
            confidence="high",
            methodology="account.move: move_type=out_invoice, state=posted"
        )
    
    def _get_monthly_revenue(self, date_from: str, date_to: str) -> List[Dict]:
        """Get monthly revenue breakdown"""
        start = datetime.strptime(date_from, "%Y-%m-%d")
        end = datetime.strptime(date_to, "%Y-%m-%d")
        
        monthly = []
        current = start.replace(day=1)
        
        while current <= end:
            next_month = (current + timedelta(days=32)).replace(day=1)
            month_end = (next_month - timedelta(days=1)).strftime("%Y-%m-%d")
            month_start = current.strftime("%Y-%m-%d")
            
            domain = [
                ("move_type", "=", "out_invoice"),
                ("state", "=", "posted"),
                ("invoice_date", ">=", month_start),
                ("invoice_date", "<=", month_end)
            ]
            invoices = self.client.search_read("account.move", domain=domain, fields=["amount_total"])
            revenue = sum(i["amount_total"] for i in invoices)
            
            monthly.append({
                "month": current.strftime("%Y-%m"),
                "revenue": revenue,
                "invoice_count": len(invoices)
            })
            
            current = next_month
        
        return monthly
    
    def _get_top_customers(self, date_from: str, date_to: str, limit: int) -> List[Dict]:
        """Get top customers by revenue"""
        domain = [
            ("move_type", "=", "out_invoice"),
            ("state", "=", "posted"),
            ("invoice_date", ">=", date_from),
            ("invoice_date", "<=", date_to),
            ("partner_id", "!=", False)
        ]
        
        invoices = self.client.search_read(
            "account.move",
            domain=domain,
            fields=["partner_id", "amount_total"],
            limit=500
        )
        
        # Aggregate by customer
        from collections import defaultdict
        customer_totals = defaultdict(float)
        
        for inv in invoices:
            if inv.get("partner_id"):
                partner_name = inv["partner_id"][1] if isinstance(inv["partner_id"], list) else str(inv["partner_id"])
                customer_totals[partner_name] += inv["amount_total"]
        
        # Sort and limit
        sorted_customers = sorted(customer_totals.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        return [{"name": name, "revenue": rev} for name, rev in sorted_customers]
    
    def _get_totals(self, date_from: str, date_to: str) -> Dict[str, Any]:
        """Get revenue totals and growth"""
        domain = [
            ("move_type", "=", "out_invoice"),
            ("state", "=", "posted"),
            ("invoice_date", ">=", date_from),
            ("invoice_date", "<=", date_to)
        ]
        
        invoices = self.client.search_read("account.move", domain=domain, fields=["amount_total"])
        total = sum(i["amount_total"] for i in invoices)
        count = len(invoices)
        avg = total / count if count > 0 else 0
        
        # Calculate growth vs prior period
        period_days = (datetime.strptime(date_to, "%Y-%m-%d") - datetime.strptime(date_from, "%Y-%m-%d")).days
        prior_start = (datetime.strptime(date_from, "%Y-%m-%d") - timedelta(days=period_days)).strftime("%Y-%m-%d")
        prior_end = (datetime.strptime(date_from, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
        
        prior_domain = [
            ("move_type", "=", "out_invoice"),
            ("state", "=", "posted"),
            ("invoice_date", ">=", prior_start),
            ("invoice_date", "<=", prior_end)
        ]
        prior_invoices = self.client.search_read("account.move", domain=prior_domain, fields=["amount_total"])
        prior_total = sum(i["amount_total"] for i in prior_invoices)
        
        growth = ((total - prior_total) / prior_total * 100) if prior_total > 0 else 0
        
        return {
            "total_revenue": total,
            "invoice_count": count,
            "avg_invoice": avg,
            "prior_period_revenue": prior_total,
            "growth_pct": growth
        }
