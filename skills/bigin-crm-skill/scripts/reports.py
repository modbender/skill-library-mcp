"""
Reporting & Analytics Module
CLI and programmatic interface for Bigin CRM reports
"""

import argparse
import json
import sys
import csv
from typing import Optional, Dict, Any, List
from datetime import datetime

from bigin_crm import BiginCRM
from auth import init_auth_from_config


class ReportManager:
    """
    Manager class for generating reports
    """
    
    def __init__(self, crm_client: BiginCRM):
        self.crm = crm_client
    
    def pipeline_report(
        self,
        by_stage: bool = True,
        by_owner: bool = True
    ) -> Dict[str, Any]:
        """
        Generate pipeline summary report
        
        Args:
            by_stage: Group by stage
            by_owner: Group by owner
            
        Returns:
            Pipeline report data
        """
        return self.crm.get_pipeline_report(by_stage=by_stage, by_owner=by_owner)
    
    def forecast(
        self,
        month: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate weighted pipeline forecast
        
        Args:
            month: Target month (YYYY-MM)
            
        Returns:
            Forecast data
        """
        return self.crm.get_forecast(month=month)
    
    def performance_report(
        self,
        owner: Optional[str] = None,
        month: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate sales performance report
        
        Args:
            owner: Filter by owner
            month: Target month (YYYY-MM)
            
        Returns:
            Performance report data
        """
        # Get all pipelines
        pipelines = self.crm.get_pipelines(limit=200)
        
        report = {
            "period": month or datetime.now().strftime("%Y-%m"),
            "owner": owner or "All",
            "total_deals": 0,
            "won_deals": 0,
            "lost_deals": 0,
            "open_deals": 0,
            "total_value": 0,
            "won_value": 0,
            "win_rate": 0,
            "average_deal_size": 0,
            "generated_at": datetime.now().isoformat()
        }
        
        for record in pipelines.get("data", []):
            data = record.get("data", {})
            
            # Filter by owner if specified
            if owner:
                record_owner = data.get("Owner", {}).get("email", "")
                if record_owner != owner:
                    continue
            
            report["total_deals"] += 1
            amount = data.get("Amount", 0) or 0
            report["total_value"] += amount
            
            stage = data.get("Stage", "")
            if stage == "Closed Won":
                report["won_deals"] += 1
                report["won_value"] += amount
            elif stage == "Closed Lost":
                report["lost_deals"] += 1
            else:
                report["open_deals"] += 1
        
        # Calculate metrics
        if report["total_deals"] > 0:
            report["win_rate"] = (report["won_deals"] / report["total_deals"]) * 100
            report["average_deal_size"] = report["total_value"] / report["total_deals"]
        
        return report
    
    def activity_report(
        self,
        user: str = "me",
        week: Optional[str] = None,
        include_calls: bool = True,
        include_tasks: bool = True,
        include_events: bool = True
    ) -> Dict[str, Any]:
        """
        Generate activity report
        
        Args:
            user: User identifier
            week: Week identifier (YYYY-WW)
            include_calls: Include call data
            include_tasks: Include task data
            include_events: Include event data
            
        Returns:
            Activity report data
        """
        report = {
            "user": user,
            "week": week or datetime.now().strftime("%Y-%W"),
            "generated_at": datetime.now().isoformat(),
            "activities": {
                "calls": 0,
                "tasks_completed": 0,
                "tasks_created": 0,
                "meetings": 0
            },
            "details": {}
        }
        
        if include_calls:
            calls = self.crm.get_calls(limit=200)
            report["activities"]["calls"] = len(calls.get("data", []))
            report["details"]["calls"] = calls.get("data", [])
        
        if include_tasks:
            tasks_open = self.crm.get_tasks(status="Open", limit=200)
            tasks_completed = self.crm.get_tasks(status="Completed", limit=200)
            report["activities"]["tasks_created"] = len(tasks_open.get("data", []))
            report["activities"]["tasks_completed"] = len(tasks_completed.get("data", []))
            report["details"]["tasks"] = {
                "open": tasks_open.get("data", []),
                "completed": tasks_completed.get("data", [])
            }
        
        if include_events:
            events = self.crm.get_events(limit=200)
            report["activities"]["meetings"] = len(events.get("data", []))
            report["details"]["events"] = events.get("data", [])
        
        return report
    
    def export_to_csv(
        self,
        report_data: Dict[str, Any],
        output_path: str
    ) -> None:
        """
        Export report data to CSV
        
        Args:
            report_data: Report dictionary
            output_path: Output CSV file path
        """
        # Flatten data for CSV export
        if "by_stage" in report_data:
            # Pipeline report
            with open(output_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Stage", "Count", "Value"])
                for stage, data in report_data.get("by_stage", {}).items():
                    writer.writerow([stage, data.get("count", 0), data.get("value", 0)])
        
        elif "total_deals" in report_data:
            # Performance report
            with open(output_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Metric", "Value"])
                writer.writerow(["Total Deals", report_data.get("total_deals", 0)])
                writer.writerow(["Won Deals", report_data.get("won_deals", 0)])
                writer.writerow(["Lost Deals", report_data.get("lost_deals", 0)])
                writer.writerow(["Open Deals", report_data.get("open_deals", 0)])
                writer.writerow(["Total Value", report_data.get("total_value", 0)])
                writer.writerow(["Win Rate %", report_data.get("win_rate", 0)])


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Bigin Reporting & Analytics")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Pipeline report command
    pipeline_parser = subparsers.add_parser("pipeline", help="Pipeline report")
    pipeline_parser.add_argument("--by-stage", action="store_true", default=True,
                               help="Group by stage")
    pipeline_parser.add_argument("--by-owner", action="store_true", default=True,
                               help="Group by owner")
    pipeline_parser.add_argument("--output", help="Output CSV file")
    
    # Forecast command
    forecast_parser = subparsers.add_parser("forecast", help="Sales forecast")
    forecast_parser.add_argument("--month", help="Target month (YYYY-MM)")
    forecast_parser.add_argument("--output", help="Output CSV file")
    
    # Performance command
    perf_parser = subparsers.add_parser("performance", help="Performance report")
    perf_parser.add_argument("--owner", help="Filter by owner")
    perf_parser.add_argument("--month", help="Target month (YYYY-MM)")
    perf_parser.add_argument("--output", help="Output CSV file")
    
    # Activity report command
    activity_parser = subparsers.add_parser("activity", help="Activity report")
    activity_parser.add_argument("--user", default="me", help="User identifier")
    activity_parser.add_argument("--week", help="Week (YYYY-WW)")
    activity_parser.add_argument("--include-calls", action="store_true",
                                help="Include calls")
    activity_parser.add_argument("--include-tasks", action="store_true",
                                help="Include tasks")
    activity_parser.add_argument("--include-events", action="store_true",
                                help="Include events")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        # Initialize auth and CRM client
        auth = init_auth_from_config()
        access_token = auth.get_access_token()
        dc = auth.dc
        
        crm = BiginCRM(access_token, dc)
        manager = ReportManager(crm)
        
        # Execute command
        if args.command == "pipeline":
            report = manager.pipeline_report(args.by_stage, args.by_owner)
            if args.output:
                manager.export_to_csv(report, args.output)
                print(f"Report exported to {args.output}")
            else:
                print(json.dumps(report, indent=2))
        
        elif args.command == "forecast":
            report = manager.forecast(args.month)
            if args.output:
                manager.export_to_csv(report, args.output)
                print(f"Report exported to {args.output}")
            else:
                print(json.dumps(report, indent=2))
        
        elif args.command == "performance":
            report = manager.performance_report(args.owner, args.month)
            if args.output:
                manager.export_to_csv(report, args.output)
                print(f"Report exported to {args.output}")
            else:
                print(json.dumps(report, indent=2))
        
        elif args.command == "activity":
            report = manager.activity_report(
                args.user,
                args.week,
                args.include_calls,
                args.include_tasks,
                args.include_events
            )
            print(json.dumps(report, indent=2))
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
