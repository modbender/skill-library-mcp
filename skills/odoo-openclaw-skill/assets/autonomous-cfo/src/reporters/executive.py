"""
Executive Summary Reporter - One-page CFO snapshot
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from .base import BaseReporter, ReportResult
from .health import FinancialHealthReporter
from .revenue import RevenueReporter
from .aging import AgingReporter
from .expenses import ExpenseReporter


class ExecutiveReporter(BaseReporter):
    """
    Generates executive summary combining:
    - Key financial metrics
    - Health indicators
    - Top risks/opportunities
    - Action items
    """
    
    def get_required_params(self) -> List[str]:
        return ["date_from", "date_to"]
    
    def generate(self, **params) -> ReportResult:
        date_from = params["date_from"]
        date_to = params["date_to"]
        
        # Gather data from other reporters
        health_reporter = FinancialHealthReporter(self.finance, self.intelligence)
        revenue_reporter = RevenueReporter(self.finance, self.intelligence)
        aging_reporter = AgingReporter(self.finance, self.intelligence)
        expense_reporter = ExpenseReporter(self.finance, self.intelligence)
        
        # Get summaries
        health_data = health_reporter._get_cash_position(params.get("company_id"))
        burn_data = health_reporter._calculate_burn_rate(date_from, date_to, params.get("company_id"))
        revenue_totals = revenue_reporter._get_totals(date_from, date_to)
        expense_totals = expense_reporter._get_expense_totals(date_from, date_to, False)
        
        # AR/AP summary
        as_of = params.get("as_of_date", date_to)
        ar_aging = aging_reporter._get_ar_aging(as_of, [30, 60, 90])
        ap_aging = aging_reporter._get_ap_aging(as_of, [30, 60, 90])
        aging_summary = aging_reporter._get_aging_summary(ar_aging, ap_aging)
        
        # Calculate KPIs
        net_income = revenue_totals.get("total_revenue", 0) - expense_totals.get("total", 0)
        margin = (net_income / max(revenue_totals.get("total_revenue", 1), 1)) * 100
        
        # Build executive data
        data = {
            "period": f"{date_from} to {date_to}",
            "kpis": {
                "revenue": revenue_totals.get("total_revenue", 0),
                "expenses": expense_totals.get("total", 0),
                "net_income": net_income,
                "margin_pct": margin,
                "total_ar": aging_summary.get("total_ar", 0),
                "total_ap": aging_summary.get("total_ap", 0),
                "cash_position": health_data.get("total_liquidity", 0),
                "runway_months": burn_data.get("runway_months", 0)
            },
            "alerts": self._generate_alerts(data={
                "margin": margin,
                "runway": burn_data.get("runway_months", 0),
                "ar_overdue": aging_summary.get("ar_overdue", 0),
                "ar_overdue_pct": (aging_summary.get("ar_overdue", 0) / max(aging_summary.get("total_ar", 1), 1)) * 100
            }),
            "recommendations": self._generate_recommendations(data={
                "margin": margin,
                "runway": burn_data.get("runway_months", 0),
                "ar_overdue_pct": (aging_summary.get("ar_overdue", 0) / max(aging_summary.get("total_ar", 1), 1)) * 100,
                "growth_pct": revenue_totals.get("growth_pct", 0)
            })
        }
        
        # Generate visualizations
        from ..visualizers.chart_factory import ChartFactory
        from ..visualizers.whatsapp_cards import WhatsAppCardGenerator
        from ..visualizers.pdf_report import PDFReportGenerator
        
        chart_factory = ChartFactory()
        card_gen = WhatsAppCardGenerator()
        pdf_gen = PDFReportGenerator()
        
        charts = []
        
        # KPI comparison chart
        kpis = data["kpis"]
        charts.append(chart_factory.generate_chart(
            {
                "labels": ["Revenue", "Expenses", "Net Income", "AR", "AP"],
                "values": [
                    kpis["revenue"],
                    kpis["expenses"],
                    max(kpis["net_income"], 0),  # Don't show negative
                    kpis["total_ar"],
                    kpis["total_ap"]
                ]
            },
            "bar",
            "Financial Overview",
            f"executive_overview_{datetime.now().strftime('%Y%m%d')}.png"
        ))
        
        # WhatsApp cards
        cards = []
        
        # Net Income card
        cards.append(card_gen.generate_kpi_card(
            title="Net Income",
            value=self.format_currency(kpis["net_income"]),
            change={"percentage": margin, "direction": "up" if kpis["net_income"] > 0 else "down"},
            subtitle=f"Margin: {margin:.1f}%",
            filename="exec_net_income.png"
        ))
        
        # Revenue card
        cards.append(card_gen.generate_kpi_card(
            title="Revenue",
            value=self.format_currency(kpis["revenue"]),
            change={"percentage": revenue_totals.get("growth_pct", 0), "direction": "up" if revenue_totals.get("growth_pct", 0) > 0 else "down"},
            subtitle=f"{revenue_totals.get('invoice_count', 0)} invoices",
            filename="exec_revenue.png"
        ))
        
        # Cash position card
        cards.append(card_gen.generate_kpi_card(
            title="Cash Position",
            value=self.format_currency(kpis["cash_position"]),
            subtitle=f"Runway: {kpis['runway_months']:.1f} months",
            filename="exec_cash.png"
        ))
        
        # AR/AP comparison card
        cards.append(card_gen.generate_comparison_card(
            title="Receivables vs Payables",
            items=[
                {"label": "Total AR", "value": self.format_currency(kpis["total_ar"]), "color": "#cd7f32"},
                {"label": "Total AP", "value": self.format_currency(kpis["total_ap"]), "color": "#c45c5c"},
                {"label": "Overdue AR", "value": self.format_currency(aging_summary.get("ar_overdue", 0)), "color": "#c45c5c"},
                {"label": "Net Position", "value": self.format_currency(kpis["total_ar"] - kpis["total_ap"]), "color": "#2e7d32" if kpis["total_ar"] > kpis["total_ap"] else "#c45c5c"}
            ],
            filename="exec_ar_ap.png"
        ))
        
        # PDF report
        sections = [
            {
                "title": "Executive Summary",
                "content": {
                    "Period": f"{date_from} to {date_to}",
                    "Report Date": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
            },
            {
                "title": "Key Performance Indicators",
                "content": {
                    "Revenue": self.format_currency(kpis["revenue"]),
                    "Expenses": self.format_currency(kpis["expenses"]),
                    "Net Income": self.format_currency(kpis["net_income"]),
                    "Profit Margin": f"{margin:.1f}%",
                    "Cash Position": self.format_currency(kpis["cash_position"]),
                    "Cash Runway": f"{kpis['runway_months']:.1f} months",
                    "Total Receivables": self.format_currency(kpis["total_ar"]),
                    "Total Payables": self.format_currency(kpis["total_ap"])
                }
            }
        ]
        
        if data["alerts"]:
            sections.append({
                "title": "Alerts",
                "content": data["alerts"]
            })
        
        if data["recommendations"]:
            sections.append({
                "title": "Recommendations",
                "content": data["recommendations"]
            })
        
        pdf_path = pdf_gen.generate_report(
            title="Executive Summary Report",
            subtitle=f"Period: {date_from} to {date_to}",
            sections=sections,
            metadata={"methodology": "Aggregated from Odoo financial modules"},
            filename=f"executive_{datetime.now().strftime('%Y%m%d')}.pdf"
        )
        
        summary = f"Revenue: {self.format_currency(kpis['revenue'])} | "
        summary += f"Net: {self.format_currency(kpis['net_income'])} ({margin:.1f}%) | "
        summary += f"Cash: {self.format_currency(kpis['cash_position'])}"
        
        return ReportResult(
            report_type="executive",
            title="Executive Summary Report",
            period=f"{date_from} to {date_to}",
            generated_at=datetime.now(),
            data=data,
            charts=charts,
            pdf_path=pdf_path,
            whatsapp_cards=cards,
            summary=summary,
            confidence="high",
            methodology="Aggregated from account.move, account.journal, account.account"
        )
    
    def _generate_alerts(self, data: Dict) -> List[str]:
        """Generate alerts based on KPIs"""
        alerts = []
        
        if data.get("margin", 0) < 10:
            alerts.append(f"Low profit margin ({data['margin']:.1f}%). Review cost structure.")
        
        if data.get("runway", 0) < 3:
            alerts.append(f"Critical: Cash runway under 3 months ({data['runway']:.1f} months).")
        elif data.get("runway", 0) < 6:
            alerts.append(f"Warning: Cash runway under 6 months ({data['runway']:.1f} months).")
        
        if data.get("ar_overdue_pct", 0) > 30:
            alerts.append(f"High overdue AR ({data['ar_overdue_pct']:.1f}%). Escalate collections.")
        
        return alerts
    
    def _generate_recommendations(self, data: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recs = []
        
        if data.get("margin", 0) < 15:
            recs.append("Review top expense categories for cost optimization opportunities.")
        
        if data.get("ar_overdue_pct", 0) > 20:
            recs.append("Implement stricter payment terms and follow-up procedures.")
        
        if data.get("growth_pct", 0) < 0:
            recs.append("Revenue declining. Analyze customer churn and market conditions.")
        elif data.get("growth_pct", 0) > 20:
            recs.append("Strong growth. Ensure cash reserves support expansion.")
        
        if data.get("runway", 0) < 12:
            recs.append("Build cash reserves. Consider credit line for working capital.")
        
        return recs
