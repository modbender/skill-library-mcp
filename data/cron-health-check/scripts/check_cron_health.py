#!/usr/bin/env python3
"""
Cron Health Check - Monitor OpenClaw cron job health and report issues.

Analyzes cron run logs to identify:
- Jobs with consecutive failures
- Delivery failures
- Timeout patterns
- Recent errors
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional


class CronHealthChecker:
    def __init__(self, openclaw_home: Path):
        self.openclaw_home = openclaw_home
        self.cron_dir = openclaw_home / "cron"
        self.jobs_file = self.cron_dir / "jobs.json"
        self.runs_dir = self.cron_dir / "runs"
        
    def load_jobs(self) -> List[Dict[str, Any]]:
        """Load cron jobs configuration."""
        try:
            with open(self.jobs_file, "r") as f:
                data = json.load(f)
                return data.get("jobs", [])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading jobs.json: {e}", file=sys.stderr)
            return []
    
    def load_run_history(self, job_id: str, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Load run history for a specific job."""
        run_file = self.runs_dir / f"{job_id}.jsonl"
        if not run_file.exists():
            return []
        
        cutoff_time = datetime.now().timestamp() * 1000 - (hours_back * 3600 * 1000)
        runs = []
        
        try:
            with open(run_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        run = json.loads(line)
                        if run.get("ts", 0) >= cutoff_time:
                            runs.append(run)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"Error reading run file {run_file}: {e}", file=sys.stderr)
        
        return runs
    
    def analyze_job_health(self, job: Dict[str, Any], hours_back: int = 24) -> Dict[str, Any]:
        """Analyze health of a single job."""
        job_id = job.get("id")
        job_name = job.get("name", "Unknown")
        state = job.get("state", {})
        
        runs = self.load_run_history(job_id, hours_back)
        
        # Analyze recent runs
        recent_errors = []
        timeout_count = 0
        delivery_failure_count = 0
        consecutive_errors = state.get("consecutiveErrors", 0)
        last_status = state.get("lastStatus", "unknown")
        last_error = state.get("lastError")
        
        for run in runs[-20:]:  # Last 20 runs
            if run.get("status") == "error":
                error = run.get("error", "")
                recent_errors.append({
                    "timestamp": run.get("ts"),
                    "error": error,
                    "duration": run.get("durationMs", 0)
                })
                if "timeout" in error.lower():
                    timeout_count += 1
                if "delivery failed" in error.lower():
                    delivery_failure_count += 1
        
        # Determine health status
        health_status = "healthy"
        issues = []
        
        if consecutive_errors >= 3:
            health_status = "critical"
            issues.append(f"{consecutive_errors} consecutive errors")
        elif consecutive_errors >= 1:
            health_status = "warning"
            issues.append(f"{consecutive_errors} consecutive error(s)")
        
        if timeout_count >= 3:
            health_status = "critical" if health_status == "healthy" else health_status
            issues.append(f"{timeout_count} timeout(s) in recent runs")
        elif timeout_count >= 1:
            health_status = "warning" if health_status == "healthy" else health_status
            issues.append(f"{timeout_count} timeout(s)")
        
        if delivery_failure_count >= 3 and not job.get("delivery", {}).get("bestEffort"):
            health_status = "warning" if health_status == "healthy" else health_status
            issues.append(f"{delivery_failure_count} delivery failure(s) - consider adding --best-effort-deliver")
        
        if last_status == "error" and last_error:
            if "403" in last_error or "limit exceeded" in last_error.lower():
                issues.append("OpenRouter API limit exceeded - check https://openrouter.ai/settings/keys")
        
        return {
            "job_id": job_id,
            "job_name": job_name,
            "enabled": job.get("enabled", True),
            "health_status": health_status,
            "issues": issues,
            "consecutive_errors": consecutive_errors,
            "last_status": last_status,
            "last_error": last_error,
            "recent_error_count": len(recent_errors),
            "timeout_count": timeout_count,
            "delivery_failure_count": delivery_failure_count,
            "recent_errors": recent_errors[-5:] if recent_errors else []  # Last 5 errors
        }
    
    def check_all_jobs(self, hours_back: int = 24) -> Dict[str, Any]:
        """Check health of all cron jobs."""
        jobs = self.load_jobs()
        results = {
            "timestamp": datetime.now().isoformat(),
            "hours_analyzed": hours_back,
            "total_jobs": len(jobs),
            "healthy_jobs": 0,
            "warning_jobs": 0,
            "critical_jobs": 0,
            "disabled_jobs": 0,
            "job_details": []
        }
        
        for job in jobs:
            if not job.get("enabled", True):
                results["disabled_jobs"] += 1
                continue
            
            health = self.analyze_job_health(job, hours_back)
            results["job_details"].append(health)
            
            if health["health_status"] == "critical":
                results["critical_jobs"] += 1
            elif health["health_status"] == "warning":
                results["warning_jobs"] += 1
            else:
                results["healthy_jobs"] += 1
        
        return results


def main():
    parser = argparse.ArgumentParser(description="Check OpenClaw cron job health.")
    parser.add_argument("--hours", type=int, default=24, help="Hours of history to analyze (default: 24)")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--openclaw-home", type=str, help="OpenClaw home directory (default: ~/.openclaw)")
    args = parser.parse_args()
    
    openclaw_home = Path(args.openclaw_home) if args.openclaw_home else Path.home() / ".openclaw"
    
    checker = CronHealthChecker(openclaw_home)
    results = checker.check_all_jobs(hours_back=args.hours)
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("=" * 70)
        print("CRON JOB HEALTH CHECK")
        print("=" * 70)
        print(f"\nAnalyzed last {args.hours} hours")
        print(f"Total jobs: {results['total_jobs']}")
        print(f"  ✓ Healthy: {results['healthy_jobs']}")
        print(f"  ⚠ Warning: {results['warning_jobs']}")
        print(f"  ✗ Critical: {results['critical_jobs']}")
        print(f"  ⊘ Disabled: {results['disabled_jobs']}\n")
        
        if results['critical_jobs'] > 0 or results['warning_jobs'] > 0:
            print("ISSUES FOUND:\n")
            for job in results['job_details']:
                if job['health_status'] in ['critical', 'warning']:
                    status_icon = "✗" if job['health_status'] == 'critical' else "⚠"
                    print(f"{status_icon} {job['job_name']} ({job['health_status']})")
                    if job['issues']:
                        for issue in job['issues']:
                            print(f"   - {issue}")
                    if job['last_error']:
                        print(f"   Last error: {job['last_error']}")
                    print()
        else:
            print("✓ All enabled jobs are healthy!\n")
        
        print("=" * 70)
        
        # Exit with error code if critical issues found
        if results['critical_jobs'] > 0:
            sys.exit(2)
        elif results['warning_jobs'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)


if __name__ == "__main__":
    main()
