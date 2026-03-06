import argparse
import json
import os
import sys
from datetime import datetime, timedelta

import requests

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.connectors.odoo_client import OdooClient
from src.runtime_env import load_env_file
from src.logic.finance_engine import FinanceEngine
from src.logic.intelligence_engine import IntelligenceEngine
from src.reporters.health import FinancialHealthReporter
from src.reporters.revenue import RevenueReporter
from src.reporters.aging import AgingReporter
from src.reporters.expenses import ExpenseReporter
from src.reporters.executive import ExecutiveReporter
from src.reporters.adhoc import AdHocReporter


def load_settings():
    path = os.path.join(os.path.dirname(__file__), "../../config/settings.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}


def save_settings(settings):
    path = os.path.join(os.path.dirname(__file__), "../../config/settings.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(settings, f, indent=2)


def _print_json(data):
    print(json.dumps(data, indent=2, default=str))


def _resolve_rpc_backend(args) -> str:
    if args.rpc_backend != "auto":
        return args.rpc_backend

    url = os.getenv("ODOO_URL", "").rstrip("/")
    if not url:
        return "xmlrpc"

    try:
        resp = requests.get(f"{url}/web/version", timeout=min(args.timeout, 10), verify=not args.insecure)
        resp.raise_for_status()
        payload = resp.json() if resp.text else {}
        version = str(payload.get("version", ""))
        if version.startswith("19"):
            return "json2"
    except Exception:
        pass

    return "xmlrpc"


def _build_client(args):
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env"))
    load_env_file(env_path)

    context = {}
    if args.lang:
        context["lang"] = args.lang
    if args.tz:
        context["tz"] = args.tz
    if args.company_id:
        context["allowed_company_ids"] = [args.company_id]

    backend = _resolve_rpc_backend(args)

    return OdooClient.from_env(
        timeout=args.timeout,
        retries=args.retries,
        verify_ssl=not args.insecure,
        context=context or None,
        rpc_backend=backend,
    )


def main():
    parser = argparse.ArgumentParser(description="Autonomous CFO CLI (Odoo Native RPC)")

    parser.add_argument("--timeout", type=int, default=30, help="RPC timeout in seconds")
    parser.add_argument("--retries", type=int, default=2, help="Retries for transient RPC failures")
    parser.add_argument("--insecure", action="store_true", help="Disable SSL certificate verification (only for trusted internal environments)")
    parser.add_argument("--lang", type=str, help="Odoo context language (e.g., en_US)")
    parser.add_argument("--tz", type=str, help="Odoo context timezone (e.g., Asia/Dubai)")
    parser.add_argument("--company-id", type=int, help="Restrict RPC context to a specific company id")
    parser.add_argument("--rpc-backend", choices=["auto", "xmlrpc", "json2"], default=os.getenv("ODOO_RPC_BACKEND", "auto"), help="Odoo API backend to use")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Health / doctor command
    doctor_parser = subparsers.add_parser("doctor", help="Validate Odoo connection/auth and inspect capabilities")
    doctor_parser.add_argument("--model", type=str, default="account.move", help="Model to probe")

    # Config command
    config_parser = subparsers.add_parser("config", help="Manage settings")
    config_parser.add_argument("--get", action="store_true", help="View current settings")
    config_parser.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"), help="Set a config value (e.g., anomalies.petty_cash_limit 1000)")

    # Summary command
    summary_parser = subparsers.add_parser("summary", help="Get financial summary")
    summary_parser.add_argument("--days", type=int, default=30, help="Days to look back")

    # Cash Flow command
    subparsers.add_parser("cash_flow", help="Get cash flow status")

    # VAT command
    vat_parser = subparsers.add_parser("vat", help="Get VAT report")
    vat_parser.add_argument("--date-from", type=str, help="Start date (YYYY-MM-DD)")
    vat_parser.add_argument("--date-to", type=str, help="End date (YYYY-MM-DD)")

    # Trends command
    trends_parser = subparsers.add_parser("trends", help="Analyze monthly trends")
    trends_parser.add_argument("--months", type=int, default=6, help="Months to analyze")
    trends_parser.add_argument("--visualize", action="store_true", help="Generate chart")

    # Anomalies command
    anomalies_parser = subparsers.add_parser("anomalies", help="Detect financial anomalies")
    anomalies_parser.add_argument("--ai", action="store_true", help="Use Gemini AI for advanced analysis")

    # Ask command
    ask_parser = subparsers.add_parser("ask", help="Ask a question in natural language")
    ask_parser.add_argument("query", type=str, help="Your question")

    # Power mode: raw rpc call
    rpc_parser = subparsers.add_parser("rpc-call", help="Advanced: execute raw model/method payload")
    rpc_parser.add_argument("--model", required=True, type=str, help="Odoo model (e.g., res.partner)")
    rpc_parser.add_argument("--method", required=True, type=str, help="Model method (e.g., search_read)")
    rpc_parser.add_argument("--payload", type=str, default="{}", help="JSON object payload (JSON-2: named args, XML-RPC: {args:[], kwargs:{}})")

    # === NEW REPORT COMMANDS (v2.0) ===
    
    # Financial Health Report
    health_parser = subparsers.add_parser("health", help="Financial health report (cash, burn rate, runway)")
    health_parser.add_argument("--from", dest="date_from", type=str, help="Start date (YYYY-MM-DD)")
    health_parser.add_argument("--to", dest="date_to", type=str, help="End date (YYYY-MM-DD)")
    health_parser.add_argument("--output", choices=["whatsapp", "pdf", "both"], default="whatsapp", help="Output format")
    
    # Revenue Analytics Report
    revenue_parser = subparsers.add_parser("revenue", help="Revenue analytics (trends, top customers)")
    revenue_parser.add_argument("--from", dest="date_from", type=str, help="Start date (YYYY-MM-DD)")
    revenue_parser.add_argument("--to", dest="date_to", type=str, help="End date (YYYY-MM-DD)")
    revenue_parser.add_argument("--breakdown", choices=["Month", "Week", "Customer", "Category"], default="Month")
    revenue_parser.add_argument("--output", choices=["whatsapp", "pdf", "both"], default="whatsapp")
    
    # AR/AP Aging Report
    aging_parser = subparsers.add_parser("aging", help="AR/AP aging report")
    aging_parser.add_argument("--as-of", dest="as_of_date", type=str, help="As of date (YYYY-MM-DD)")
    aging_parser.add_argument("--buckets", type=str, default="30,60,90", help="Aging buckets (comma-separated)")
    aging_parser.add_argument("--output", choices=["whatsapp", "pdf", "both"], default="whatsapp")
    
    # Expense Breakdown Report
    expenses_parser = subparsers.add_parser("expenses", help="Expense breakdown report")
    expenses_parser.add_argument("--from", dest="date_from", type=str, help="Start date (YYYY-MM-DD)")
    expenses_parser.add_argument("--to", dest="date_to", type=str, help="End date (YYYY-MM-DD)")
    expenses_parser.add_argument("--group-by", choices=["Vendor", "Category", "Month"], default="Category")
    expenses_parser.add_argument("--output", choices=["whatsapp", "pdf", "both"], default="whatsapp")
    
    # Executive Summary Report
    executive_parser = subparsers.add_parser("executive", help="Executive summary (one-page CFO snapshot)")
    executive_parser.add_argument("--from", dest="date_from", type=str, help="Start date (YYYY-MM-DD)")
    executive_parser.add_argument("--to", dest="date_to", type=str, help="End date (YYYY-MM-DD)")
    executive_parser.add_argument("--output", choices=["whatsapp", "pdf", "both"], default="both")
    
    # Ad-hoc Custom Report
    adhoc_parser = subparsers.add_parser("adhoc", help="Custom ad-hoc report builder")
    adhoc_parser.add_argument("--from", dest="date_from", type=str, help="Start date (YYYY-MM-DD)")
    adhoc_parser.add_argument("--to", dest="date_to", type=str, help="End date (YYYY-MM-DD)")
    adhoc_parser.add_argument("--metric-a", type=str, help="First metric (e.g., 'revenue', 'expenses')")
    adhoc_parser.add_argument("--metric-b", type=str, help="Second metric for comparison")
    adhoc_parser.add_argument("--granularity", choices=["Day", "Week", "Month", "Quarter"], default="Month")
    adhoc_parser.add_argument("--output", choices=["whatsapp", "pdf", "both"], default="whatsapp")

    args = parser.parse_args()

    if args.command == "config":
        settings = load_settings()
        if args.get:
            _print_json(settings)
            return
        if args.set:
            key_path, value = args.set
            keys = key_path.split(".")
            d = settings
            for k in keys[:-1]:
                d = d.setdefault(k, {})

            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            else:
                try:
                    value = float(value) if "." in value else int(value)
                except ValueError:
                    pass

            d[keys[-1]] = value
            save_settings(settings)
            _print_json({"status": "updated", "key": key_path, "value": value})
            return

    try:
        client = _build_client(args)
        finance = FinanceEngine(client)
        intelligence = IntelligenceEngine(client)

        if args.command == "doctor":
            version = client.version()
            ok = client.authenticate()
            sample = client.search_read(args.model, domain=[], fields=["id"], limit=1)
            fields = client.get_fields(args.model, attributes=["string", "type"])
            _print_json(
                {
                    "connection": "ok" if ok else "failed",
                    "url": client.url,
                    "db": client.db,
                    "uid": client.uid,
                    "server_version": version,
                    "model_probe": {
                        "model": args.model,
                        "sample_count": len(sample),
                        "fields_count": len(fields),
                    },
                    "context": client.context,
                    "rpc": {
                        "backend": client.rpc_backend,
                        "timeout_seconds": client.timeout,
                        "retries": client.retries,
                        "ssl_verify": client.verify_ssl,
                    },
                    "notes": [
                        "Use Odoo API keys as ODOO_PASSWORD for production integrations.",
                        "Odoo 19 docs mark XML-RPC/JSON-RPC for removal in Odoo 20; plan migration to External JSON-2 API."
                    ],
                }
            )

        elif args.command == "summary":
            result = finance.get_invoice_expense_summary(days=args.days)
            _print_json(result)

        elif args.command == "cash_flow":
            result = finance.get_cash_flow_status()
            _print_json(result)

        elif args.command == "vat":
            date_to = args.date_to or datetime.now().strftime("%Y-%m-%d")
            date_from = args.date_from or (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
            result = intelligence.get_vat_report(date_from, date_to)
            _print_json(result)

        elif args.command == "trends":
            result = intelligence.get_trend_analysis(months=args.months)
            chart_path = None
            if args.visualize:
                from src.tools.visualizer import generate_revenue_vs_expense_chart

                os.makedirs("output", exist_ok=True)
                output_file = f"output/revenue_vs_expense_{datetime.now().strftime('%Y%m%d')}.png"
                chart_path = generate_revenue_vs_expense_chart(result, output_file)

            _print_json({"trends": result, "chart_path": chart_path})

        elif args.command == "anomalies":
            if args.ai:
                result = intelligence.get_ai_anomaly_report()
                _print_json({"ai_report": result})
            else:
                result = intelligence.detect_anomalies()
                _print_json(result)

        elif args.command == "ask":
            result = intelligence.ask(args.query)
            _print_json({"answer": result})

        elif args.command == "rpc-call":
            method = args.method.strip()

            try:
                payload = json.loads(args.payload or "{}")
                if not isinstance(payload, dict):
                    raise ValueError("payload must be a JSON object")
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid payload JSON: {e}") from e

            result = client.call_raw(args.model, method, payload)
            _print_json({
                "model": args.model,
                "method": method,
                "backend": client.rpc_backend,
                "result": result,
            })

        # === NEW REPORT HANDLERS (v2.0) ===
        
        elif args.command == "health":
            reporter = FinancialHealthReporter(finance, intelligence)
            date_from = args.date_from or (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            date_to = args.date_to or datetime.now().strftime("%Y-%m-%d")
            result = reporter.generate(date_from=date_from, date_to=date_to, company_id=args.company_id)
            _print_json({
                "summary": result.summary,
                "charts": result.charts,
                "pdf": result.pdf_path,
                "cards": result.whatsapp_cards,
                "confidence": result.confidence
            })

        elif args.command == "revenue":
            reporter = RevenueReporter(finance, intelligence)
            date_from = args.date_from or (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
            date_to = args.date_to or datetime.now().strftime("%Y-%m-%d")
            result = reporter.generate(
                date_from=date_from, 
                date_to=date_to, 
                breakdown=args.breakdown,
                company_id=args.company_id
            )
            _print_json({
                "summary": result.summary,
                "charts": result.charts,
                "pdf": result.pdf_path,
                "cards": result.whatsapp_cards
            })

        elif args.command == "aging":
            reporter = AgingReporter(finance, intelligence)
            as_of = args.as_of_date or datetime.now().strftime("%Y-%m-%d")
            buckets = [int(b.strip()) for b in args.buckets.split(",")]
            result = reporter.generate(as_of_date=as_of, buckets=buckets, company_id=args.company_id)
            _print_json({
                "summary": result.summary,
                "charts": result.charts,
                "pdf": result.pdf_path,
                "cards": result.whatsapp_cards
            })

        elif args.command == "expenses":
            reporter = ExpenseReporter(finance, intelligence)
            date_from = args.date_from or (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            date_to = args.date_to or datetime.now().strftime("%Y-%m-%d")
            result = reporter.generate(
                date_from=date_from,
                date_to=date_to,
                group_by=args.group_by,
                company_id=args.company_id
            )
            _print_json({
                "summary": result.summary,
                "charts": result.charts,
                "pdf": result.pdf_path,
                "cards": result.whatsapp_cards
            })

        elif args.command == "executive":
            reporter = ExecutiveReporter(finance, intelligence)
            date_from = args.date_from or (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            date_to = args.date_to or datetime.now().strftime("%Y-%m-%d")
            result = reporter.generate(date_from=date_from, date_to=date_to, company_id=args.company_id)
            _print_json({
                "summary": result.summary,
                "kpis": result.data.get("kpis", {}),
                "alerts": result.data.get("alerts", []),
                "recommendations": result.data.get("recommendations", []),
                "charts": result.charts,
                "pdf": result.pdf_path,
                "cards": result.whatsapp_cards
            })

        elif args.command == "adhoc":
            reporter = AdHocReporter(finance, intelligence)
            date_from = args.date_from or (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            date_to = args.date_to or datetime.now().strftime("%Y-%m-%d")
            result = reporter.generate(
                date_from=date_from,
                date_to=date_to,
                metric_a=args.metric_a,
                metric_b=args.metric_b,
                granularity=args.granularity,
                company_id=args.company_id
            )
            _print_json({
                "summary": result.summary,
                "charts": result.charts,
                "cards": result.whatsapp_cards
            })

        else:
            parser.print_help()

    except Exception as e:
        _print_json({"error": str(e), "command": args.command})
        sys.exit(1)


if __name__ == "__main__":
    main()
