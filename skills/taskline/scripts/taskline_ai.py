#!/usr/bin/env python3
"""
Intelligent Taskline AI Dispatcher
Routes natural language requests to appropriate enhanced scripts.
"""

import json
import re
import subprocess
import sys
from typing import List, Optional

def detect_intent(text: str) -> str:
    """Detect user intent from natural language."""
    text = text.lower().strip()
    
    # Task creation patterns
    creation_patterns = [
        r'(?:add|create|new|make) (?:a )?task',
        r'ask \w+ to',
        r'get \w+ to',
        r'have \w+ (?:do|handle)',
        r'(?:urgent|high|low) priority',
        r'(?:for|in|on) (?:the )?\w+ project',
        r'by (?:tomorrow|friday|monday|tuesday|wednesday|thursday|saturday|sunday|next week)',
    ]
    
    if any(re.search(pattern, text) for pattern in creation_patterns):
        return 'create_task'
    
    # Update task patterns  
    update_patterns = [
        r'mark .* (?:as )?(?:done|complete|finished)',
        r'update .* (?:status|priority)',
        r'set .* to (?:in.progress|waiting|cancelled)',
        r'complete (?:the )?task',
    ]
    
    if any(re.search(pattern, text) for pattern in update_patterns):
        return 'update_task'
    
    # List/query patterns
    query_patterns = [
        r'(?:what|show|list) (?:tasks?|is overdue)',
        r'(?:my|current) (?:tasks?|progress)',
        r'overdue',
        r'in.progress',
        r'completed?',
        r'status',
        r'report',
    ]
    
    if any(re.search(pattern, text) for pattern in query_patterns):
        return 'query_tasks'
    
    # Default to task creation if unclear
    return 'create_task'

def run_enhanced_script(script_name: str, args: List[str]) -> None:
    """Run an enhanced script with arguments."""
    cmd = ['python3', f'scripts/{script_name}'] + args
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Script failed with exit code {e.returncode}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"❌ Script not found: scripts/{script_name}")
        sys.exit(1)

def extract_task_reference(text: str) -> Optional[str]:
    """Extract task ID or description reference from update commands."""
    # Look for explicit task IDs (UUIDs)
    uuid_pattern = r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}'
    match = re.search(uuid_pattern, text, re.IGNORECASE)
    if match:
        return match.group(0)
    
    # Look for task references like "that API task", "the login bug task"
    reference_patterns = [
        r'(?:that|the) ([\w\s]+?) task',
        r'task (?:about|for|on) ([\w\s]+)',
    ]
    
    for pattern in reference_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return None

def process_natural_language(text: str) -> None:
    """Process natural language request and dispatch to appropriate script."""
    intent = detect_intent(text)
    
    print(f"🧠 Intent detected: {intent}")
    print(f"📝 Processing: '{text}'")
    print()
    
    if intent == 'create_task':
        # Use enhanced task creation
        run_enhanced_script('create_task_enhanced.py', [text])
        
    elif intent == 'update_task':
        # Extract task reference and status/priority changes
        task_ref = extract_task_reference(text)
        if task_ref:
            # For now, pass to update script - could enhance further
            run_enhanced_script('update_task.py', [task_ref, text])
        else:
            print("❓ Could not identify which task to update.")
            print("   Try: 'Mark the API task as done' or include the task ID")
    
    elif intent == 'query_tasks':
        # Route to appropriate listing/reporting script
        if any(word in text.lower() for word in ['overdue']):
            run_enhanced_script('reports.py', ['overdue'])
        elif any(word in text.lower() for word in ['report', 'summary']):
            run_enhanced_script('reports.py', ['summary'])  
        else:
            run_enhanced_script('list_tasks.py', [text])
    
    else:
        print(f"❓ Unknown intent: {intent}")
        print("   Try: 'Create task...', 'Show my tasks', or 'Mark task as done'")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("🤖 Taskline AI - Natural Language Task Management")
        print()
        print("Usage: python taskline_ai.py 'natural language request'")
        print()
        print("🧠 Smart Examples:")
        print("  'Add high priority task for Mobile project: fix login by Friday'")
        print("  'Ask Sarah to review the API docs by next Monday'")
        print("  'What tasks are overdue?'")
        print("  'Show my in-progress tasks'") 
        print("  'Mark the authentication task as done'")
        print("  'Create urgent task: deploy hotfix tomorrow'")
        print()
        print("✨ Features:")
        print("  📅 Smart dates: tomorrow, Friday, next week, end of week")
        print("  🏗️  Auto project creation and assignment")
        print("  👥 People detection and executor assignment")
        print("  🔥 Priority intelligence: urgent, high, medium, low")
        print("  🧠 Intent detection: create, update, query")
        sys.exit(1)
    
    # Process the natural language request
    request_text = " ".join(sys.argv[1:])
    process_natural_language(request_text)