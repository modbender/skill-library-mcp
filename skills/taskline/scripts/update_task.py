#!/usr/bin/env python3
"""
Update task status in Taskline API with natural language parsing.
"""

import json
import re
import requests
import sys
from typing import Dict, List, Optional, Tuple

def load_config() -> Dict:
    """Load API configuration."""
    try:
        with open('references/config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: config.json not found. Please configure your API settings.")
        sys.exit(1)

def get_all_tasks() -> List[Dict]:
    """Fetch all tasks for reference matching."""
    config = load_config()
    headers = {"X-API-Key": config["apiKey"]}
    
    response = requests.get(f"{config['baseUrl']}/tasks", headers=headers)
    
    if response.status_code == 200:
        return response.json()["data"]
    else:
        print(f"Error fetching tasks: {response.status_code}")
        return []

def parse_status_update(text: str) -> Optional[str]:
    """Parse status from natural language."""
    text = text.lower()
    
    # Completed status
    if any(phrase in text for phrase in ['mark as done', 'mark done', 'complete', 'completed', 'finish', 'finished']):
        return 'completed'
    
    # In progress status  
    if any(phrase in text for phrase in ['start', 'begin', 'working on', 'in progress']):
        return 'in_progress'
    
    # Waiting status
    if any(phrase in text for phrase in ['wait', 'waiting', 'block', 'blocked', 'pause', 'paused']):
        return 'waiting'
    
    # Cancelled status
    if any(phrase in text for phrase in ['cancel', 'cancelled', 'abandon']):
        return 'cancelled'
    
    # Reset to not started
    if any(phrase in text for phrase in ['reset', 'restart', 'not started']):
        return 'not_started'
    
    return None

def find_matching_tasks(reference: str, tasks: List[Dict]) -> List[Dict]:
    """Find tasks matching a natural language reference."""
    reference = reference.lower().strip()
    
    # Remove common prefixes
    reference = re.sub(r'^(the |that |this )', '', reference)
    
    matches = []
    
    for task in tasks:
        title_lower = task['title'].lower()
        
        # Exact title match
        if reference == title_lower:
            return [task]
        
        # Partial title match
        if reference in title_lower or title_lower in reference:
            matches.append(task)
        
        # Word overlap scoring
        ref_words = set(reference.split())
        title_words = set(title_lower.split())
        
        if len(ref_words) > 0:
            overlap = len(ref_words.intersection(title_words))
            if overlap >= min(2, len(ref_words)):  # At least 2 words or all words
                if task not in matches:
                    matches.append(task)
    
    return matches

def update_task_status(task_id: str, status: str) -> Dict:
    """Update a task's status via the API."""
    config = load_config()
    
    payload = {"status": status}
    headers = {
        "X-API-Key": config["apiKey"],
        "Content-Type": "application/json"
    }
    
    response = requests.patch(f"{config['baseUrl']}/tasks/{task_id}", json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error updating task: {response.status_code}")
        print(response.text)
        sys.exit(1)

def parse_update_request(text: str) -> Tuple[str, Optional[str]]:
    """
    Parse natural language update request.
    Returns: (task_reference, new_status)
    """
    
    # Extract the new status
    new_status = parse_status_update(text)
    
    # Extract task reference
    text_lower = text.lower()
    
    # Common patterns for task references
    patterns = [
        r'mark (.*?) as (done|complete|finished)',
        r'complete (.*?)(?:$|\s+(task|item))',
        r'set (.*?) to (\w+)',
        r'start (?:working on )?(.*?)(?:$|\s+(task|item))',
        r'(.*?) (?:is |should be )?(?:done|complete|finished)',
    ]
    
    task_reference = ""
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            task_reference = match.group(1).strip()
            break
    
    if not task_reference:
        # Fallback: try to extract task reference after common action words
        action_words = ['mark', 'set', 'complete', 'finish', 'start', 'begin']
        for word in action_words:
            if word in text_lower:
                parts = text_lower.split(word, 1)
                if len(parts) > 1:
                    task_reference = parts[1].strip()
                    # Clean up common trailing words
                    task_reference = re.sub(r'\s+(as |to |done|complete|finished).*$', '', task_reference)
                    break
    
    return task_reference, new_status

def format_status_name(status: str) -> str:
    """Format status for display."""
    status_names = {
        'not_started': 'Not Started',
        'in_progress': 'In Progress', 
        'waiting': 'Waiting',
        'completed': 'Completed',
        'cancelled': 'Cancelled'
    }
    return status_names.get(status, status)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python update_task.py 'update description'")
        print("Examples:")
        print("  python update_task.py 'Mark the API task as done'")
        print("  python update_task.py 'Complete the Bertha integration'")
        print("  python update_task.py 'Start working on the frontend updates'")
        sys.exit(1)
    
    # Parse the update request
    request_text = " ".join(sys.argv[1:])
    task_reference, new_status = parse_update_request(request_text)
    
    if not new_status:
        print("Error: Could not determine what status to set.")
        print("Try phrases like: 'mark as done', 'complete', 'start working on', 'set to waiting'")
        sys.exit(1)
    
    if not task_reference:
        print("Error: Could not determine which task to update.")
        print("Try being more specific about the task title or description.")
        sys.exit(1)
    
    # Find matching tasks
    all_tasks = get_all_tasks()
    matching_tasks = find_matching_tasks(task_reference, all_tasks)
    
    if not matching_tasks:
        print(f"Error: No tasks found matching '{task_reference}'")
        print("\nAvailable tasks:")
        for task in all_tasks[:5]:  # Show first 5 tasks
            print(f"  - {task['title']}")
        if len(all_tasks) > 5:
            print(f"  ... and {len(all_tasks) - 5} more")
        sys.exit(1)
    
    if len(matching_tasks) > 1:
        print(f"Multiple tasks match '{task_reference}':")
        for i, task in enumerate(matching_tasks, 1):
            print(f"  {i}. {task['title']} (status: {task['status']})")
        print("\nPlease be more specific.")
        sys.exit(1)
    
    # Update the task
    task = matching_tasks[0]
    updated_task = update_task_status(task['id'], new_status)
    
    # Display result
    status_emoji = {
        'not_started': '⚪',
        'in_progress': '🔵',
        'waiting': '🟡', 
        'completed': '✅',
        'cancelled': '❌'
    }
    
    emoji = status_emoji.get(new_status, '⚪')
    old_status_name = format_status_name(task['status'])
    new_status_name = format_status_name(new_status)
    
    print(f"{emoji} Updated '{task['title']}'")
    print(f"   Status: {old_status_name} → {new_status_name}")