#!/usr/bin/env python3
"""
Create a task in Taskline via API with natural language parsing.
"""

import json
import re
import requests
import sys
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

def load_config() -> Dict:
    """Load API configuration."""
    try:
        with open('references/config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: config.json not found. Please configure your API settings.")
        sys.exit(1)

def parse_priority(text: str) -> Optional[str]:
    """Extract priority from natural language."""
    text = text.lower()
    if any(word in text for word in ['urgent', 'critical', 'asap']):
        return 'urgent'
    elif any(word in text for word in ['high', 'important']):
        return 'high'
    elif any(word in text for word in ['medium', 'normal']):
        return 'medium'
    elif any(word in text for word in ['low']):
        return 'low'
    return None

def parse_due_date(text: str) -> Optional[str]:
    """Parse relative dates from natural language."""
    text = text.lower()
    now = datetime.now()
    
    # Tomorrow
    if 'tomorrow' in text:
        return (now + timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Day names (assuming current week, or next week if past)
    days = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 
        'friday': 4, 'saturday': 5, 'sunday': 6
    }
    
    for day_name, day_num in days.items():
        if day_name in text:
            days_ahead = day_num - now.weekday()
            if days_ahead <= 0:  # Target day already passed this week
                days_ahead += 7
            return (now + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
    
    # Next week
    if 'next week' in text:
        return (now + timedelta(days=7)).strftime('%Y-%m-%d')
    
    # In X days
    match = re.search(r'in (\d+) days?', text)
    if match:
        days = int(match.group(1))
        return (now + timedelta(days=days)).strftime('%Y-%m-%d')
    
    return None

def parse_task_request(text: str) -> Tuple[str, str, Optional[str], Optional[str]]:
    """
    Parse natural language task request.
    Returns: (title, description, priority, due_date)
    """
    
    # Clean up common prefixes
    text = re.sub(r'^(add task:?|create task:?|new task:?)\s*', '', text, flags=re.IGNORECASE)
    
    # Extract priority
    priority = parse_priority(text)
    
    # Extract due date
    due_date = parse_due_date(text)
    
    # Split on common separators for title/description
    if ' - ' in text:
        title, description = text.split(' - ', 1)
    elif ': ' in text and not text.lower().startswith(('http:', 'https:')):
        title, description = text.split(': ', 1)
    else:
        title = text
        description = ""
    
    # Clean up title and description
    title = title.strip()
    description = description.strip() if description else ""
    
    return title, description, priority, due_date

def create_task(title: str, description: str = "", priority: str = None, due_date: str = None) -> Dict:
    """Create a task via the Taskline API."""
    config = load_config()
    
    payload = {
        "title": title,
        "status": "not_started"
    }
    
    if description:
        payload["description"] = description
    if priority:
        payload["priority"] = priority
    if due_date:
        payload["dueAt"] = due_date
    
    headers = {
        "X-API-Key": config["apiKey"],
        "Content-Type": "application/json"
    }
    
    response = requests.post(f"{config['baseUrl']}/tasks", json=payload, headers=headers)
    
    if response.status_code == 201:
        return response.json()
    else:
        print(f"Error creating task: {response.status_code}")
        print(response.text)
        sys.exit(1)

def format_task_summary(task: Dict) -> str:
    """Format task for display."""
    lines = [
        f"✅ Created task: {task['title']}",
        f"   Status: {task['status']}"
    ]
    
    if task.get('description'):
        lines.append(f"   Description: {task['description']}")
    if task.get('priority'):
        lines.append(f"   Priority: {task['priority']}")
    if task.get('dueAt'):
        lines.append(f"   Due: {task['dueAt']}")
    
    return "\n".join(lines)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_task.py 'task description'")
        print("Examples:")
        print("  python create_task.py 'Fix the authentication bug'")
        print("  python create_task.py 'High priority: Review marketing proposal due Friday'")
        sys.exit(1)
    
    # Parse the natural language request
    request_text = " ".join(sys.argv[1:])
    title, description, priority, due_date = parse_task_request(request_text)
    
    # Create the task
    task = create_task(title, description, priority, due_date)
    
    # Display result
    print(format_task_summary(task))