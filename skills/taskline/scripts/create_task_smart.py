#!/usr/bin/env python3
"""
Smart task creation with progressive enhancement.
Falls back gracefully when advanced APIs aren't available.
"""

import json
import re
import requests
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

def load_config() -> Dict:
    """Load API configuration."""
    try:
        with open('references/config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: config.json not found. Please configure your API settings.")
        sys.exit(1)

def api_request(method: str, endpoint: str, data: Dict = None, fallback_on_404: bool = True) -> Optional[Dict]:
    """Make an API request with fallback handling."""
    config = load_config()
    
    headers = {"X-API-Key": config["apiKey"]}
    if data:
        headers["Content-Type"] = "application/json"
    
    url = f"{config['baseUrl']}/{endpoint.lstrip('/')}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PATCH":
            response = requests.patch(url, json=data, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        if response.status_code in [200, 201]:
            return response.json()
        elif response.status_code == 404 and fallback_on_404:
            return None  # API not available yet
        else:
            print(f"API Error {response.status_code}: {response.text}")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        if fallback_on_404:
            return None
        print(f"Request failed: {e}")
        sys.exit(1)

def get_projects() -> List[Dict]:
    """Get all projects (with fallback)."""
    result = api_request("GET", "projects")
    if result is None:
        print("ℹ️  Projects API not yet available - using project report fallback")
        # Fallback to by-project report
        report = api_request("GET", "reports/by-project", fallback_on_404=False)
        return report.get("projects", [])
    return result.get("data", [])

def get_people() -> List[Dict]:
    """Get all people (with fallback)."""
    result = api_request("GET", "people")
    if result is None:
        print("ℹ️  People API not yet available - using basic assignment")
        return []
    return result.get("data", [])

def find_or_create_project(project_name: str) -> Optional[str]:
    """Find existing project or create new one. Returns project ID or None."""
    projects = get_projects()
    
    # Case-insensitive search
    for project in projects:
        if project["name"].lower() == project_name.lower():
            return project["id"]
    
    # Try to create new project
    new_project = api_request("POST", "projects", {
        "name": project_name,
        "description": f"Auto-created project for {project_name}",
        "isActive": True
    })
    
    if new_project:
        print(f"📁 Created new project: {project_name}")
        return new_project["id"]
    else:
        print(f"⚠️  Cannot create project '{project_name}' - API not available yet")
        return None

def parse_enhanced_date(text: str) -> Optional[str]:
    """Enhanced date parsing with natural language support."""
    text = text.lower().strip()
    now = datetime.now()
    
    # Handle "today"
    if 'today' in text:
        return now.strftime('%Y-%m-%d')
    
    # Handle "tomorrow"
    if 'tomorrow' in text:
        return (now + timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Handle "next [day]" (next Monday, next Friday, etc.)
    next_day_match = re.search(r'next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', text)
    if next_day_match:
        target_day = next_day_match.group(1)
        days = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        target_weekday = days[target_day]
        days_ahead = target_weekday - now.weekday()
        if days_ahead <= 0:  # Target is this week or past
            days_ahead += 7  # Go to next week
        return (now + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
    
    # Handle day names (this week or next)
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
    
    # Handle "next week"
    if 'next week' in text:
        return (now + timedelta(days=7)).strftime('%Y-%m-%d')
    
    # Handle "in X days/weeks"
    in_match = re.search(r'in (\d+) (day|week)s?', text)
    if in_match:
        amount = int(in_match.group(1))
        unit = in_match.group(2)
        if unit == 'day':
            return (now + timedelta(days=amount)).strftime('%Y-%m-%d')
        elif unit == 'week':
            return (now + timedelta(weeks=amount)).strftime('%Y-%m-%d')
    
    # Handle "by [day]" (by Friday = this Friday or next Friday)
    by_match = re.search(r'by\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', text)
    if by_match:
        target_day = by_match.group(1)
        target_weekday = days[target_day]
        days_ahead = target_weekday - now.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return (now + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
    
    return None

def parse_priority(text: str) -> Optional[str]:
    """Extract priority from natural language."""
    text = text.lower()
    if any(word in text for word in ['urgent', 'critical', 'asap', 'emergency']):
        return 'urgent'
    elif any(word in text for word in ['high', 'important']):
        return 'high'
    elif any(word in text for word in ['medium', 'normal']):
        return 'medium'
    elif any(word in text for word in ['low']):
        return 'low'
    return None

def extract_project_name(text: str) -> Tuple[str, Optional[str]]:
    """Extract project name from text and return (remaining_text, project_name)."""
    project_patterns = [
        r'for the ([\w\s]+?) project',
        r'in the ([\w\s]+?) project', 
        r'on the ([\w\s]+?) project',
        r'for ([\w\s]+?) project',
        r'in ([\w\s]+?) project',
        r'on ([\w\s]+?) project',
        r'project[:\s]+([\w\s]+?)(?:\s(?:by|due|with|$))',
    ]
    
    for pattern in project_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            project_name = match.group(1).strip()
            # Remove the project reference from text
            cleaned_text = re.sub(pattern, '', text, flags=re.IGNORECASE).strip()
            # Clean up extra whitespace
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
            return cleaned_text, project_name
    
    return text, None

def extract_people_mentions(text: str) -> Tuple[str, List[str]]:
    """Extract people mentions from text (for future stakeholder support)."""
    people = []
    
    # Patterns for people mentions
    people_patterns = [
        r'ask (\w+(?:\s+\w+)?)\s+to',
        r'have (\w+(?:\s+\w+)?)\s+(?:do|handle|work|review)',
        r'(\w+(?:\s+\w+)?)\s+should\s+(?:do|handle|work|review)',
        r'get (\w+(?:\s+\w+)?)\s+to',
        r'(\w+(?:\s+\w+)?)\s+needs to',
        r'assign to (\w+(?:\s+\w+)?)',
        r'(?:with|involving|include|cc|notify)\s+(\w+(?:\s+\w+)?)',
    ]
    
    for pattern in people_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            person_name = match.group(1).strip()
            people.append(person_name)
            # Remove the people reference from text for cleaner title
            text = re.sub(pattern, '', text, flags=re.IGNORECASE).strip()
            break  # Only extract first mention for now
    
    # Clean up text
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text, people

def parse_smart_task(text: str) -> Dict:
    """
    Parse a natural language task request with progressive enhancement.
    """
    original_text = text
    
    # Clean up common prefixes
    text = re.sub(r'^(add task:?|create task:?|new task:?)\s*', '', text, flags=re.IGNORECASE).strip()
    
    # Extract project
    text, project_name = extract_project_name(text)
    
    # Extract people (for future use)
    text, people_mentions = extract_people_mentions(text)
    
    # Extract priority
    priority = parse_priority(original_text)
    
    # Extract due date
    due_date = parse_enhanced_date(original_text)
    
    # Split remaining text for title/description
    if ' - ' in text:
        title, description = text.split(' - ', 1)
    elif ': ' in text and not text.lower().startswith(('http:', 'https:')):
        parts = text.split(': ', 1)
        if len(parts) == 2:
            title, description = parts
        else:
            title = text
            description = ""
    else:
        title = text
        description = ""
    
    # Clean up
    title = title.strip()
    description = description.strip() if description else ""
    
    return {
        'title': title,
        'description': description,
        'priority': priority,
        'due_date': due_date,
        'project_name': project_name,
        'people_mentions': people_mentions
    }

def create_smart_task(parsed_task: Dict) -> Dict:
    """Create a task with progressive enhancement."""
    payload = {
        "title": parsed_task['title'],
        "status": "not_started"
    }
    
    if parsed_task['description']:
        payload["description"] = parsed_task['description']
    if parsed_task['priority']:
        payload["priority"] = parsed_task['priority']
    if parsed_task['due_date']:
        payload["dueAt"] = parsed_task['due_date']
    
    # Handle project (if available)
    if parsed_task['project_name']:
        project_id = find_or_create_project(parsed_task['project_name'])
        if project_id:
            payload["projectId"] = project_id
    
    # Create the task
    task = api_request("POST", "tasks", payload, fallback_on_404=False)
    
    # Handle people mentions (informational for now)
    if parsed_task['people_mentions']:
        print(f"👥 People mentioned: {', '.join(parsed_task['people_mentions'])}")
        print("   (Full people management will be available when People API is deployed)")
    
    return task

def format_smart_task_summary(task: Dict, parsed: Dict) -> str:
    """Format task creation summary."""
    lines = [f"✅ Created task: {task['title']}"]
    
    if task.get('description'):
        lines.append(f"   Description: {task['description']}")
    if task.get('priority'):
        lines.append(f"   Priority: {task['priority']}")
    if task.get('dueAt'):
        lines.append(f"   Due: {task['dueAt']}")
    if task.get('project'):
        lines.append(f"   Project: {task['project']['name']}")
    
    return "\n".join(lines)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_task_smart.py 'task description'")
        print("\nExamples:")
        print("  'High priority task for Mobile project: fix login bug by Friday'")
        print("  'Ask Sarah to review the FreeMySoul docs by next Monday'") 
        print("  'Deploy the Projects API tomorrow'")
        print("  'Create urgent task: fix server issues in Production project'")
        sys.exit(1)
    
    # Parse the smart natural language request
    request_text = " ".join(sys.argv[1:])
    parsed_task = parse_smart_task(request_text)
    
    print(f"🧠 Parsing: '{request_text}'")
    print(f"📝 Extracted: {parsed_task}")
    print()
    
    # Create the task
    task = create_smart_task(parsed_task)
    
    # Display result
    print(format_smart_task_summary(task, parsed_task))