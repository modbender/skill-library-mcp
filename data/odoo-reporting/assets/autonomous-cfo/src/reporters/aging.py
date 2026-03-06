"""
AR/AP Aging Reporter - Who owes you, who you owe, overdue buckets
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from .base import BaseReporter, ReportResult


class AgingReporter(BaseReporter):
    """
    Generates AR/AP aging report including:
    - Accounts receivable aging (0-30, 31-60, 61-90, 90+)
    - Accounts payable aging
    - Overdue analysis
    - Collection priority
    """
    
    def get_required_params(self) -> List[str]:
        return ["as_of_date"]
    
    def generate(self, **params) -> ReportResult:
        as_of = params.get("as_of_date", datetime.now().strftime("%Y-%m-%d"))
        buckets = params.get("buckets", [30, 60, 90])
        
        # Gather data
        ar_aging = self._get_ar_aging(as_of, buckets)
        ap_aging = self._get_ap_aging(as_of, buckets)
        summary = self._get_aging_summary(ar_aging, ap_aging)
        
        data = {
            "as_of_date": as_of,
            "buckets": buckets,
            "ar_aging": ar_aging,
            "ap_aging": ap_aging,
            "summary": summary
        }
        
        # Generate visualizations
        from ..visualizers.chart_factory import ChartFactory
        from ..visualizers.whatsapp_cards import WhatsAppCardGenerator
        from ..visualizers.pdf_report import PDFReportGenerator
        
        chart_factory = ChartFactory()
        card_gen = WhatsAppCardGenerator()
        pdf_gen = PDFReportGenerator()
        
        charts = []
        
        # AR by bucket chart
        if summary.get("ar_by_bucket"):
            labels = list(summary["ar_by_bucket"].keys())
            values = list(summary["ar_by_bucket"].values())
            charts.append(chart_factory.generate_chart(
                {"x": labels, "y": values},
                "bar",
                "AR Aging Buckets",
                f"ar_aging_{datetime.now().strftime('%Y%m%d')}.png"
            ))
        
        # WhatsApp cards
        cards = []
        
        # Total AR card
        cards.append(card_gen.generate_kpi_card(
            title="Total Receivables",
            value=self.format_currency(summary.get("total_ar", 0)),
            subtitle=f"As of {as_of}",
            filename="aging_ar.png"
        ))
        
        # Overdue AR card
        cards.append(card_gen.generate_kpi_card(
            title="Overdue Receivables",
            value=self.format_currency(summary.get("ar_overdue", 0)),
            change={"percentage": (summary.get("ar_overdue", 0) / max(summary.get("total_ar", 1), 1)) * 100, "direction": "down"},
            subtitle=f"{summary.get('overdue_ar_count', 0)} invoices",
            filename="aging_overdue.png"
        ))
        
        # Total AP card
        cards.append(card_gen.generate_kpi_card(
            title="Total Payables",
            value=self.format_currency(summary.get("total_ap", 0)),
            subtitle=f"As of {as_of}",
            filename="aging_ap.png"
        ))
        
        # PDF report
        sections = [
            {
                "title": "Summary",
                "content": {
                    "Total Receivables": summary.get("total_ar", 0),
                    "Total Payables": summary.get("total_ap", 0),
                    "Net Position": summary.get("total_ar", 0) - summary.get("total_ap", 0),
                    "Overdue AR": summary.get("ar_overdue", 0),
                }
            },
            {
                "title": "AR Aging Buckets",
                "content": summary.get("ar_by_bucket", {})
            },
            {
                "title": "AP Aging Buckets", 
                "content": summary.get("ap_by_bucket", {})
            },
            {
                "title": "Top Overdue Customers",
                "content": self._format_top_overdue(ar_aging)
            }
        ]
        
        pdf_path = pdf_gen.generate_report(
            title="AR/AP Aging Report",
            subtitle=f"As of {as_of}",
            sections=sections,
            metadata={"methodology": "account.move: out_invoice/in_invoice, payment_state, invoice_date_due"},
            filename=f"aging_{datetime.now().strftime('%Y%m%d')}.pdf"
        )
        
        summary_text = f"AR: {self.format_currency(summary.get('total_ar', 0))} | "
        summary_text += f"AP: {self.format_currency(summary.get('total_ap', 0))} | "
        summary_text += f"Overdue: {self.format_currency(summary.get('ar_overdue', 0))}"
        
        return ReportResult(
            report_type="aging",
            title="AR/AP Aging Report",
            period=f"As of {as_of}",
            generated_at=datetime.now(),
            data=data,
            charts=charts,
            pdf_path=pdf_path,
            whatsapp_cards=cards,
            summary=summary_text,
            confidence="high",
            methodology="account.move: move_type, state=posted, payment_state, invoice_date_due"
        )
    
    def _get_ar_aging(self, as_of: str, buckets: List[int]) -> List[Dict]:
        """Get AR aging by customer"""
        domain = [
            ("move_type", "=", "out_invoice"),
            ("state", "=", "posted"),
            ("payment_state", "in", ["not_paid", "partial"]),
            ("amount_residual", ">", 0)
        ]
        
        invoices = self.client.search_read(
            "account.move",
            domain=domain,
            fields=["partner_id", "amount_residual", "invoice_date_due", "name"],
            limit=1000
        )
        
        as_of_date = datetime.strptime(as_of, "%Y-%m-%d")
        aged = []
        
        for inv in invoices:
            if not inv.get("invoice_date_due") or not inv.get("partner_id"):
                continue
            
            due_date = datetime.strptime(inv["invoice_date_due"], "%Y-%m-%d")
            days_overdue = (as_of_date - due_date).days
            
            # Determine bucket
            bucket = "Current"
            if days_overdue > buckets[-1]:
                bucket = f"{buckets[-1]}+ days"
            else:
                for i, b in enumerate(buckets):
                    if days_overdue <= 0:
                        bucket = "Current"
                        break
                    prev = buckets[i-1] if i > 0 else 0
                    if prev < days_overdue <= b:
                        bucket = f"{prev}-{b} days"
                        break
            
            aged.append({
                "customer": inv["partner_id"][1] if isinstance(inv["partner_id"], list) else str(inv["partner_id"]),
                "invoice": inv.get("name", ""),
                "amount": inv["amount_residual"],
                "due_date": inv["invoice_date_due"],
                "days_overdue": max(days_overdue, 0),
                "bucket": bucket
            })
        
        return aged
    
    def _get_ap_aging(self, as_of: str, buckets: List[int]) -> List[Dict]:
        """Get AP aging by vendor"""
        domain = [
            ("move_type", "=", "in_invoice"),
            ("state", "=", "posted"),
            ("payment_state", "in", ["not_paid", "partial"]),
            ("amount_residual", ">", 0)
        ]
        
        bills = self.client.search_read(
            "account.move",
            domain=domain,
            fields=["partner_id", "amount_residual", "invoice_date_due", "name"],
            limit=1000
        )
        
        as_of_date = datetime.strptime(as_of, "%Y-%m-%d")
        aged = []
        
        for bill in bills:
            if not bill.get("invoice_date_due") or not bill.get("partner_id"):
                continue
            
            due_date = datetime.strptime(bill["invoice_date_due"], "%Y-%m-%d")
            days_overdue = (as_of_date - due_date).days
            
            bucket = "Current"
            if days_overdue > 0:
                if days_overdue > buckets[-1]:
                    bucket = f"{buckets[-1]}+ days"
                else:
                    for i, b in enumerate(buckets):
                        prev = buckets[i-1] if i > 0 else 0
                        if prev < days_overdue <= b:
                            bucket = f"{prev}-{b} days"
                            break
            
            aged.append({
                "vendor": bill["partner_id"][1] if isinstance(bill["partner_id"], list) else str(bill["partner_id"]),
                "bill": bill.get("name", ""),
                "amount": bill["amount_residual"],
                "due_date": bill["invoice_date_due"],
                "days_overdue": max(days_overdue, 0),
                "bucket": bucket
            })
        
        return aged
    
    def _get_aging_summary(self, ar_aging: List, ap_aging: List) -> Dict:
        """Summarize aging data"""
        ar_by_bucket = defaultdict(float)
        ap_by_bucket = defaultdict(float)
        
        for item in ar_aging:
            ar_by_bucket[item["bucket"]] += item["amount"]
        
        for item in ap_aging:
            ap_by_bucket[item["bucket"]] += item["amount"]
        
        total_ar = sum(item["amount"] for item in ar_aging)
        total_ap = sum(item["amount"] for item in ap_aging)
        
        ar_overdue = sum(item["amount"] for item in ar_aging if item["days_overdue"] > 0)
        overdue_count = sum(1 for item in ar_aging if item["days_overdue"] > 0)
        
        return {
            "total_ar": total_ar,
            "total_ap": total_ap,
            "ar_overdue": ar_overdue,
            "overdue_ar_count": overdue_count,
            "ar_by_bucket": dict(ar_by_bucket),
            "ap_by_bucket": dict(ap_by_bucket)
        }
    
    def _format_top_overdue(self, ar_aging: List) -> Dict:
        """Get top overdue customers"""
        customer_totals = defaultdict(float)
        for item in ar_aging:
            if item["days_overdue"] > 0:
                customer_totals[item["customer"]] += item["amount"]
        
        sorted_customers = sorted(customer_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        return {name: self.format_currency(amt) for name, amt in sorted_customers}
