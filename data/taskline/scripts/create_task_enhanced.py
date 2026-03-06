#!/usr/bin/env python3
"""
FULLY ENHANCED task creation with complete project, people, and date intelligence.
Uses all available Taskline APIs for maximum natural language processing.
"""

import json
import re
import requests
import sys
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

def load_config() -> Dict:
    """Load API configuration."""
    try:
        with open('references/config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: config.json not found. Please configure your API settings.")
        sys.exit(1)

def api_request(method: str, endpoint: str, data: Dict = None) -> Dict:
    """Make an API request."""
    config = load_config()
    
    headers = {"X-API-Key": config["apiKey"]}
    if data:
        headers["Content-Type"] = "application/json"
    
    url = f"{config['baseUrl']}/{endpoint.lstrip('/')}"
    
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
    else:
        print(f"API Error {response.status_code}: {response.text}")
        sys.exit(1)

def get_projects() -> List[Dict]:
    """Get all projects."""
    return api_request("GET", "projects")["data"]

def get_people() -> List[Dict]:
    """Get all people."""
    return api_request("GET", "people")["data"]

def find_or_create_project(project_name: str) -> Dict:
    """Find existing project or create new one."""
    projects = get_projects()
    
    # Case-insensitive search
    for project in projects:
        if project["name"].lower() == project_name.lower():
            return project
    
    # Create new project
    print(f"📁 Creating new project: {project_name}")
    return api_request("POST", "projects", {
        "name": project_name,
        "description": f"Auto-created project for {project_name}",
        "isActive": True
    })

def find_or_create_person(name: str) -> Dict:
    """Find existing person or create new one."""
    people = get_people()
    
    # Search by display name or handle (case-insensitive)
    name_lower = name.lower()
    for person in people:
        if (person["displayName"].lower() == name_lower or 
            person["handle"].lower() == name_lower):
            return person
    
    # Create new person
    handle = re.sub(r'[^a-z0-9]', '', name.lower())[:20]  # Clean handle
    print(f"👤 Creating new person: {name}")
    return api_request("POST", "people", {
        "handle": handle,
        "displayName": name,
        "source": "auto"
    })

def parse_enhanced_date(text: str) -> Optional[str]:
    """Enhanced date parsing with comprehensive natural language support."""
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
        if days_ahead <= 0:
            days_ahead += 7
        return (now + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
    
    # Handle "this [day]" or just day names
    days = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 
        'friday': 4, 'saturday': 5, 'sunday': 6
    }
    
    for day_name, day_num in days.items():
        if day_name in text:
            days_ahead = day_num - now.weekday()
            if days_ahead <= 0:  # Already passed this week
                days_ahead += 7
            return (now + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
    
    # Handle "next week" / "in a week"
    if any(phrase in text for phrase in ['next week', 'in a week']):
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
    
    # Handle "end of week" / "EOW"
    if any(phrase in text for phrase in ['end of week', 'eow']):
        days_to_friday = 4 - now.weekday()  # Friday = 4
        if days_to_friday <= 0:
            days_to_friday += 7
        return (now + timedelta(days=days_to_friday)).strftime('%Y-%m-%d')
    
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
        r'(?:for|in|on) the ([\w\s]+?) project(?:\s|$)',
        r'(?:for|in|on) ([\w\s]+?) project(?:\s|$)',
        r'project[:\s]+([\w\s]+?)(?:\s(?:by|due|with|and|$))',
        r'([\w\s]+?) project[:\s]',
    ]
    
    for pattern in project_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            project_name = match.group(1).strip()
            # Skip common words that aren't really projects
            if project_name.lower() in ['this', 'that', 'the', 'a', 'an']:
                continue
                
            # Remove the project reference from text
            cleaned_text = re.sub(pattern, ' ', text, flags=re.IGNORECASE).strip()
            # Clean up extra whitespace
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
            return cleaned_text, project_name
    
    return text, None

def extract_people_assignments(text: str) -> Tuple[str, Optional[str], List[str]]:
    """
    Extract executor and stakeholders from text.
    Returns (remaining_text, executor_name, stakeholder_names)
    """
    executor = None
    stakeholders = []
    
    # Patterns for executors (person who will DO the task)
    executor_patterns = [
        r'ask (\w+(?:\s+\w+)?)\s+to\s+',
        r'have (\w+(?:\s+\w+)?)\s+(?:do|handle|work on|complete|review)\s+',
        r'get (\w+(?:\s+\w+)?)\s+to\s+',
        r'(\w+(?:\s+\w+)?)\s+should\s+(?:do|handle|work on|complete|review)\s+',
        r'(\w+(?:\s+\w+)?)\s+needs? to\s+(?:do|handle|work on|complete|review)\s+',
        r'assign (?:to\s+)?(\w+(?:\s+\w+)?)\s*[:\-]\s*',
        r'executor[:\s]+(\w+(?:\s+\w+)?)',
    ]
    
    for pattern in executor_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            executor = match.group(1).strip()
            # Remove the executor reference from text
            text = re.sub(pattern, '', text, flags=re.IGNORECASE).strip()
            break
    
    # Patterns for stakeholders (people who care about the outcome)
    stakeholder_patterns = [
        r'(?:with|involving|include|cc|notify|keep.*(?:informed|updated))\s+((?:\w+(?:\s+\w+)?(?:\s*,\s*|\s+and\s+))*\w+(?:\s+\w+)?)',
        r'stakeholders?\s*[:\-]\s*((?:\w+(?:\s+\w+)?(?:\s*,\s*|\s+and\s+))*\w+(?:\s+\w+)?)',
        r'(?:loop in|inform)\s+((?:\w+(?:\s+\w+)?(?:\s*,\s*|\s+and\s+))*\w+(?:\s+\w+)?)',
    ]
    
    for pattern in stakeholder_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            stakeholder_text = match.group(1)
            # Parse comma/and separated names
            names = re.split(r'\s*(?:,|and)\s*', stakeholder_text)
            stakeholders.extend([name.strip() for name in names if name.strip() and len(name.strip()) > 1])
            # Remove the stakeholder reference from text
            text = re.sub(pattern, '', text, flags=re.IGNORECASE).strip()
            break
    
    # Clean up text
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text, executor, stakeholders

def parse_enhanced_task(text: str) -> Dict:
    """
    Parse a natural language task request with full intelligence.
    Returns a dict with all task components.
    """
    original_text = text
    
    # Clean up common prefixes
    text = re.sub(r'^(?:add|create|new)\s+task:?\s*', '', text, flags=re.IGNORECASE).strip()
    
    # Extract project first (so we can clean up text for other parsing)
    text, project_name = extract_project_name(text)
    
    # Extract people assignments
    text, executor_name, stakeholder_names = extract_people_assignments(text)
    
    # Extract priority from original text
    priority = parse_priority(original_text)
    
    # Extract due date from original text
    due_date = parse_enhanced_date(original_text)
    
    # Split remaining text for title/description
    if ' - ' in text:
        title, description = text.split(' - ', 1)
    elif ': ' in text and not text.lower().startswith(('http:', 'https:')):
        parts = text.split(': ', 1)
        if len(parts) == 2 and len(parts[0]) < 100:  # Reasonable title length
            title, description = parts
        else:
            title = text
            description = ""
    else:
        title = text
        description = ""
    
    # Clean up and validate
    title = title.strip()
    description = description.strip() if description else ""
    
    # If title is empty or too short, use a meaningful default
    if not title or len(title) < 3:
        if project_name:
            title = f"Task for {project_name} project"
        else:
            title = description[:50] if description else "New task"
    
    return {
        'title': title,
        'description': description,
        'priority': priority,
        'due_date': due_date,
        'project_name': project_name,
        'executor_name': executor_name,
        'stakeholder_names': stakeholder_names
    }

def create_enhanced_task(parsed_task: Dict) -> Dict:
    """Create a task with all enhanced features."""
    payload = {
        "title": parsed_task['title'],
        "status": "not_started"
    }
    
    # Add optional fields
    if parsed_task['description']:
        payload["description"] = parsed_task['description']
    if parsed_task['priority']:
        payload["priority"] = parsed_task['priority']
    if parsed_task['due_date']:
        payload["dueAt"] = parsed_task['due_date']
    
    # Handle project
    if parsed_task['project_name']:
        project = find_or_create_project(parsed_task['project_name'])
        payload["projectId"] = project["id"]
    
    # Handle executor
    if parsed_task['executor_name']:
        executor = find_or_create_person(parsed_task['executor_name'])
        payload["executorPersonId"] = executor["id"]
    
    # Create the task
    task = api_request("POST", "tasks", payload)
    
    # Handle stakeholders (informational for now - may need API extension)
    if parsed_task['stakeholder_names']:
        print(f"👥 Stakeholders identified: {', '.join(parsed_task['stakeholder_names'])}")
        # Note: Stakeholder assignment may require additional API endpoint or task update
        # For now, we'll just log them - you may want to add this to the task description
        # or implement stakeholder assignment via a separate API call
    
    return task

def format_enhanced_task_summary(task: Dict, parsed: Dict) -> str:
    """Format comprehensive task creation summary."""
    lines = [f"✅ Created task: {task['title']}"]
    
    if task.get('description'):
        lines.append(f"   📝 Description: {task['description']}")
    if task.get('priority'):
        priority_emoji = {'urgent': '🔥', 'high': '⬆️', 'medium': '➡️', 'low': '⬇️'}.get(task['priority'], '')
        lines.append(f"   {priority_emoji} Priority: {task['priority']}")
    if task.get('dueAt'):
        lines.append(f"   📅 Due: {task['dueAt']}")
    if task.get('project'):
        lines.append(f"   📁 Project: {task['project']['name']}")
    if task.get('executorPerson') and task['executorPerson']['handle'] != 'me':
        lines.append(f"   👤 Executor: {task['executorPerson']['displayName']}")
    
    return "\n".join(lines)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_task_enhanced.py 'natural language task description'")
        print("\n🧠 Enhanced Examples:")
        print("  'High priority task for Mobile project: fix login bug by Friday'")
        print("  'Ask Sarah to review the FreeMySoul docs by next Monday with John and Mike'") 
        print("  'Create urgent task for Taskline project: add stakeholder management API'")
        print("  'Deploy API updates to Production project tomorrow'")
        print("  'Get Jennifer to handle the Platform project documentation by end of week'")
        print("\n📅 Date Intelligence: today, tomorrow, Friday, next Monday, in 2 weeks, by EOW")
        print("🏗️  Project Intelligence: Auto-detects and creates projects")
        print("👥 People Intelligence: Identifies executors and stakeholders")
        print("🔥 Priority Intelligence: urgent, high, medium, low")
        sys.exit(1)
    
    # Parse the fully enhanced natural language request
    request_text = " ".join(sys.argv[1:])
    parsed_task = parse_enhanced_task(request_text)
    
    print(f"🧠 Parsing: '{request_text}'")
    print(f"📝 Extracted: {json.dumps(parsed_task, indent=2)}")
    print()
    
    # Create the task with full intelligence
    task = create_enhanced_task(parsed_task)
    
    # Display comprehensive result
    print(format_enhanced_task_summary(task, parsed_task))
    print()
    print(f"🔗 Task ID: {task['id']}")