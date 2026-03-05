#!/usr/bin/env python3
"""
List and filter tasks from Taskline API.
"""

import json
import requests
import sys
from typing import Dict, List, Optional
from datetime import datetime, timedelta

def load_config() -> Dict:
    """Load API configuration."""
    try:
        with open('references/config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: config.json not found. Please configure your API settings.")
        sys.exit(1)

def get_tasks(status: str = None, limit: int = 100) -> List[Dict]:
    """Fetch tasks from the API."""
    config = load_config()
    
    params = {"limit": limit}
    if status:
        params["status"] = status
    
    headers = {"X-API-Key": config["apiKey"]}
    
    response = requests.get(f"{config['baseUrl']}/tasks", params=params, headers=headers)
    
    if response.status_code == 200:
        return response.json()["data"]
    else:
        print(f"Error fetching tasks: {response.status_code}")
        print(response.text)
        sys.exit(1)

def get_overdue_tasks() -> List[Dict]:
    """Fetch overdue tasks."""
    config = load_config()
    headers = {"X-API-Key": config["apiKey"]}
    
    response = requests.get(f"{config['baseUrl']}/reports/overdue", headers=headers)
    
    if response.status_code == 200:
        return response.json()["data"]
    else:
        print(f"Error fetching overdue tasks: {response.status_code}")
        return []

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

def format_task(task: Dict, show_details: bool = True) -> str:
    """Format a single task for display."""
    # Status emoji
    status_emoji = {
        'not_started': '⚪',
        'in_progress': '🔵', 
        'waiting': '🟡',
        'completed': '✅',
        'cancelled': '❌'
    }
    
    emoji = status_emoji.get(task['status'], '⚪')
    title = task['title']
    
    # Priority indicator
    priority_indicators = {
        'urgent': '🔥',
        'high': '🔺',
        'medium': '🔸',
        'low': '🔹'
    }
    
    priority_str = ""
    if task.get('priority'):
        indicator = priority_indicators.get(task['priority'].lower(), '')
        priority_str = f" {indicator}" if indicator else f" [{task['priority']}]"
    
    # Due date
    due_str = ""
    if task.get('dueAt'):
        due_date = datetime.fromisoformat(task['dueAt'].replace('Z', '+00:00'))
        now = datetime.now(due_date.tzinfo)
        
        if due_date.date() == now.date():
            due_str = " (due today)"
        elif due_date < now:
            days_overdue = (now - due_date).days
            due_str = f" (overdue by {days_overdue} day{'s' if days_overdue != 1 else ''})"
        else:
            due_str = f" (due {due_date.strftime('%b %d')})"
    
    line = f"{emoji} {title}{priority_str}{due_str}"
    
    if show_details and task.get('description'):
        line += f"\n   {task['description']}"
    
    return line

def format_summary(summary: Dict) -> str:
    """Format task summary for display."""
    total = summary.get('total', 0)
    if total == 0:
        return "📋 No tasks found"
    
    lines = [
        f"📋 Task Summary ({total} total):",
        f"   ⚪ Not started: {summary.get('not_started', 0)}",
        f"   🔵 In progress: {summary.get('in_progress', 0)}",
        f"   🟡 Waiting: {summary.get('waiting', 0)}",  
        f"   ✅ Completed: {summary.get('completed', 0)}"
    ]
    
    if summary.get('cancelled', 0) > 0:
        lines.append(f"   ❌ Cancelled: {summary['cancelled']}")
    
    return "\n".join(lines)

def parse_filter_request(text: str) -> str:
    """Parse natural language filter requests."""
    text = text.lower()
    
    # Status filters
    if any(phrase in text for phrase in ['not started', 'new', 'todo']):
        return 'not_started'
    elif any(phrase in text for phrase in ['in progress', 'working', 'active', 'current']):
        return 'in_progress'
    elif any(phrase in text for phrase in ['waiting', 'blocked', 'paused']):
        return 'waiting'
    elif any(phrase in text for phrase in ['completed', 'done', 'finished']):
        return 'completed'
    elif any(phrase in text for phrase in ['cancelled', 'canceled']):
        return 'cancelled'
    
    return None

if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) > 1:
        request_text = " ".join(sys.argv[1:]).lower()
        
        if 'summary' in request_text or 'overview' in request_text:
            summary = get_summary()
            print(format_summary(summary))
            sys.exit(0)
        elif 'overdue' in request_text:
            tasks = get_overdue_tasks()
            if not tasks:
                print("📋 No overdue tasks! 🎉")
            else:
                print(f"⚠️  {len(tasks)} overdue task{'s' if len(tasks) != 1 else ''}:")
                for task in tasks:
                    print(format_task(task))
            sys.exit(0)
        else:
            # Try to parse status filter
            status_filter = parse_filter_request(request_text)
            if status_filter:
                tasks = get_tasks(status=status_filter)
                status_names = {
                    'not_started': 'Not Started',
                    'in_progress': 'In Progress',
                    'waiting': 'Waiting',
                    'completed': 'Completed',
                    'cancelled': 'Cancelled'
                }
                
                if not tasks:
                    print(f"📋 No {status_names[status_filter].lower()} tasks")
                else:
                    print(f"📋 {status_names[status_filter]} tasks ({len(tasks)}):")
                    for task in tasks:
                        print(format_task(task))
                sys.exit(0)
    
    # Default: show all tasks
    tasks = get_tasks()
    if not tasks:
        print("📋 No tasks found")
        print("\nTip: Create a task by saying 'Add task: [description]'")
    else:
        print(f"📋 All tasks ({len(tasks)}):")
        for task in tasks:
            print(format_task(task))