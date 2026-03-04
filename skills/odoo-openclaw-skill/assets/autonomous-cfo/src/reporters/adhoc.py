"""
Ad-hoc Custom Report Generator
"""
from typing import Dict, Any, List
from datetime import datetime
from collections import defaultdict

from .base import BaseReporter, ReportResult


class AdHocReporter(BaseReporter):
    """Custom ad-hoc report builder"""
    
    def get_required_params(self) -> List[str]:
        return ["date_from", "date_to", "metric_a"]
    
    def generate(self, **params) -> ReportResult:
        from ..visualizers.chart_factory import ChartFactory
        from ..visualizers.whatsapp_cards import WhatsAppCardGenerator
        from ..visualizers.pdf_report import PDFReportGenerator
        
        date_from = params["date_from"]
        date_to = params["date_to"]
        metric_a = params["metric_a"]
        metric_b = params.get("metric_b")
        
        data_a = self._get_metric(metric_a, date_from, date_to)
        data_b = self._get_metric(metric_b, date_from, date_to) if metric_b else None
        
        chart_factory = ChartFactory()
        card_gen = WhatsAppCardGenerator()
        
        cards = []
        total_a = sum(d["value"] for d in data_a)
        cards.append(card_gen.generate_kpi_card(
            title=metric_a.title(),
            value=self.format_currency(total_a),
            subtitle=f"{date_from} to {date_to}",
            filename="adhoc_a.png"
        ))
        
        if data_b:
            total_b = sum(d["value"] for d in data_b)
            cards.append(card_gen.generate_kpi_card(
                title=metric_b.title(),
                value=self.format_currency(total_b),
                subtitle=f"vs {metric_a}",
                filename="adhoc_b.png"
            ))
        
        return ReportResult(
            report_type="adhoc",
            title=f"Ad-hoc: {metric_a}" + (f" vs {metric_b}" if metric_b else ""),
            period=f"{date_from} to {date_to}",
            generated_at=datetime.now(),
            data={"a": data_a, "b": data_b},
            charts=[],
            whatsapp_cards=cards,
            summary=f"{metric_a}: {self.format_currency(total_a)}",
            confidence="high",
            methodology="Custom query"
        )
    
    def _get_metric(self, metric: str, date_from: str, date_to: str) -> List[Dict]:
        metric = metric.lower()
        domain = [("invoice_date", ">=", date_from), ("invoice_date", "<=", date_to), ("state", "=", "posted")]
        
        if "revenue" in metric or "sales" in metric:
            domain.append(("move_type", "=", "out_invoice"))
        elif "expense" in metric:
            domain.append(("move_type", "=", "in_invoice"))
        else:
            domain.append(("move_type", "=", "out_invoice"))
        
        records = self.client.search_read("account.move", domain=domain, fields=["invoice_date", "amount_total"])
        
        grouped = defaultdict(float)
        for r in records:
            if r.get("invoice_date"):
                grouped[r["invoice_date"][:7]] += r.get("amount_total", 0)
        
        return [{"period": k, "value": v} for k, v in sorted(grouped.items())]
