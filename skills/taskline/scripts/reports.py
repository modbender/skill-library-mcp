#!/usr/bin/env python3
"""
Generate reports and analytics from Taskline API.
"""

import json
import requests
import sys
from typing import Dict, List
from datetime import datetime, timedelta

def load_config() -> Dict:
    """Load API configuration."""
    try:
        with open('references/config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: config.json not found. Please configure your API settings.")
        sys.exit(1)

def get_summary() -> Dict:
    """Get task summary report."""
    config = load_config()
    headers = {"X-API-Key": config["apiKey"]}
    
    response = requests.get(f"{config['baseUrl']}/reports/summary", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching summary: {response.status_code}")
        return {}

def get_overdue() -> List[Dict]:
    """Get overdue tasks."""
    config = load_config()
    headers = {"X-API-Key": config["apiKey"]}
    
    response = requests.get(f"{config['baseUrl']}/reports/overdue", headers=headers)
    
    if response.status_code == 200:
        return response.json()["data"]
    else:
        print(f"Error fetching overdue tasks: {response.status_code}")
        return []

def get_by_project() -> Dict:
    """Get tasks grouped by project."""
    config = load_config()
    headers = {"X-API-Key": config["apiKey"]}
    
    response = requests.get(f"{config['baseUrl']}/reports/by-project", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching project report: {response.status_code}")
        return {}

def get_completed_over_time(group_by: str = "day") -> Dict:
    """Get completed tasks over time."""
    config = load_config()
    headers = {"X-API-Key": config["apiKey"]}
    
    params = {"groupBy": group_by}
    response = requests.get(f"{config['baseUrl']}/reports/completed", 
                          params=params, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching completion report: {response.status_code}")
        return {}

def format_summary_report(summary: Dict) -> str:
    """Format task summary for display."""
    total = summary.get('total', 0)
    if total == 0:
        return "📋 No tasks found"
    
    # Calculate percentages
    not_started = summary.get('not_started', 0)
    in_progress = summary.get('in_progress', 0) 
    waiting = summary.get('waiting', 0)
    completed = summary.get('completed', 0)
    cancelled = summary.get('cancelled', 0)
    
    # Active tasks (not completed or cancelled)
    active = not_started + in_progress + waiting
    
    lines = [
        f"📊 Task Summary",
        f"═══════════════",
        f"Total Tasks: {total}",
        f"Active: {active} | Completed: {completed}",
        "",
        f"⚪ Not Started: {not_started:>3} ({not_started/total*100:4.1f}%)",
        f"🔵 In Progress: {in_progress:>3} ({in_progress/total*100:4.1f}%)",
        f"🟡 Waiting:     {waiting:>3} ({waiting/total*100:4.1f}%)",
        f"✅ Completed:   {completed:>3} ({completed/total*100:4.1f}%)"
    ]
    
    if cancelled > 0:
        lines.append(f"❌ Cancelled:   {cancelled:>3} ({cancelled/total*100:4.1f}%)")
    
    # Completion rate
    if total > 0:
        completion_rate = completed / total * 100
        lines.extend([
            "",
            f"📈 Completion Rate: {completion_rate:.1f}%"
        ])
    
    return "\n".join(lines)

def format_overdue_report(overdue_tasks: List[Dict]) -> str:
    """Format overdue tasks report."""
    if not overdue_tasks:
        return "🎉 No overdue tasks!"
    
    lines = [
        f"⚠️  Overdue Tasks ({len(overdue_tasks)})",
        f"════════════════════════"
    ]
    
    for task in overdue_tasks:
        due_date = datetime.fromisoformat(task['dueAt'].replace('Z', '+00:00'))
        days_overdue = (datetime.now(due_date.tzinfo) - due_date).days
        
        priority_str = ""
        if task.get('priority'):
            priority_indicators = {
                'urgent': '🔥', 'high': '🔺',
                'medium': '🔸', 'low': '🔹'
            }
            indicator = priority_indicators.get(task['priority'].lower(), '')
            priority_str = f" {indicator}" if indicator else f" [{task['priority']}]"
        
        lines.append(f"• {task['title']}{priority_str}")
        lines.append(f"  Due: {due_date.strftime('%b %d')} ({days_overdue} day{'s' if days_overdue != 1 else ''} ago)")
        
        if task.get('description'):
            lines.append(f"  {task['description']}")
        
        lines.append("")
    
    return "\n".join(lines)

def format_project_report(project_data: Dict) -> str:
    """Format project breakdown report."""
    projects = project_data.get('projects', [])
    unassigned = project_data.get('unassigned', {})
    
    if not projects and not unassigned.get('taskCounts', {}).get('total', 0):
        return "📋 No projects or tasks found"
    
    lines = [
        f"📁 Tasks by Project",
        f"═══════════════════"
    ]
    
    # Show projects
    for project in projects:
        counts = project['taskCounts']
        total = counts['total']
        active = counts['not_started'] + counts['in_progress'] + counts['waiting']
        
        lines.extend([
            f"",
            f"📂 {project['name']} ({total} task{'s' if total != 1 else ''})",
            f"   Active: {active} | Completed: {counts['completed']}"
        ])
        
        if total > 0:
            if counts['not_started'] > 0:
                lines.append(f"   ⚪ Not Started: {counts['not_started']}")
            if counts['in_progress'] > 0:
                lines.append(f"   🔵 In Progress: {counts['in_progress']}")
            if counts['waiting'] > 0:
                lines.append(f"   🟡 Waiting: {counts['waiting']}")
    
    # Show unassigned tasks
    if unassigned.get('taskCounts', {}).get('total', 0) > 0:
        counts = unassigned['taskCounts']
        total = counts['total']
        active = counts['not_started'] + counts['in_progress'] + counts['waiting']
        
        lines.extend([
            f"",
            f"📝 Unassigned Tasks ({total} task{'s' if total != 1 else ''})",
            f"   Active: {active} | Completed: {counts['completed']}"
        ])
    
    return "\n".join(lines)

def format_completion_report(completion_data: Dict) -> str:
    """Format completion trend report."""
    periods = completion_data.get('periods', [])
    total = completion_data.get('total', 0)
    group_by = completion_data.get('groupBy', 'day')
    
    if not periods:
        return f"📈 No completed tasks in the last {'30 days' if group_by == 'day' else '12 weeks' if group_by == 'week' else '12 months'}"
    
    time_desc = {
        'day': 'Daily Completion Trend (Last 30 Days)',
        'week': 'Weekly Completion Trend (Last 12 Weeks)', 
        'month': 'Monthly Completion Trend (Last 12 Months)'
    }
    
    lines = [
        f"📈 {time_desc[group_by]}",
        f"{'═' * len(time_desc[group_by]) + 2}",
        f"Total Completed: {total}"
    ]
    
    if periods:
        lines.append("")
        
        # Show recent periods with activity
        recent_periods = sorted(periods, key=lambda x: x['period'], reverse=True)[:10]
        
        for period in recent_periods:
            if period['count'] > 0:
                date_str = period['period']
                if group_by == 'day':
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    formatted_date = date_obj.strftime('%b %d')
                elif group_by == 'week':
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    formatted_date = f"Week of {date_obj.strftime('%b %d')}"
                else:  # month
                    formatted_date = datetime.strptime(date_str, '%Y-%m').strftime('%b %Y')
                
                bar_length = min(20, period['count'])
                bar = '█' * bar_length
                
                lines.append(f"{formatted_date:>12}: {period['count']:>2} {bar}")
    
    return "\n".join(lines)

if __name__ == "__main__":
    report_type = sys.argv[1] if len(sys.argv) > 1 else "summary"
    
    if report_type in ['summary', 'overview']:
        summary = get_summary()
        print(format_summary_report(summary))
    
    elif report_type == 'overdue':
        overdue = get_overdue()
        print(format_overdue_report(overdue))
    
    elif report_type in ['project', 'projects']:
        projects = get_by_project()
        print(format_project_report(projects))
    
    elif report_type in ['completion', 'completed', 'trends']:
        group_by = sys.argv[2] if len(sys.argv) > 2 else "day"
        completed = get_completed_over_time(group_by)
        print(format_completion_report(completed))
    
    else:
        print("Available reports:")
        print("  summary    - Task status overview")
        print("  overdue    - Tasks past their due date")  
        print("  projects   - Tasks grouped by project")
        print("  completion - Completion trends over time")
        print("")
        print("Examples:")
        print("  python reports.py summary")
        print("  python reports.py overdue")
        print("  python reports.py completion week")