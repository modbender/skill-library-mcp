#!/usr/bin/env python3
"""
FIS Lifecycle - Clean version without personal data
"""

import json
import os
import sys
import argparse
from datetime import datetime

class FISLifecycle:
    """Ticket lifecycle management - no external calls, no personal data"""
    
    def __init__(self, hub_path=None):
        self.hub_path = hub_path or os.path.expanduser("~/.openclaw/fis-hub")
        self.tickets_dir = os.path.join(self.hub_path, "tickets")
        self.active_dir = os.path.join(self.tickets_dir, "active")
        self.completed_dir = os.path.join(self.tickets_dir, "completed")
        
        # Ensure directories exist
        for d in [self.active_dir, self.completed_dir]:
            os.makedirs(d, exist_ok=True)
    
    def create_ticket(self, agent, task, role="worker"):
        """Create a new ticket - no external notifications"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ticket_id = f"TASK_{timestamp}_{agent.upper()}"
        
        ticket = {
            "ticket_id": ticket_id,
            "agent_id": agent,
            "role": role,
            "task": task,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        filepath = os.path.join(self.active_dir, f"{ticket_id}.json")
        with open(filepath, 'w') as f:
            json.dump(ticket, f, indent=2)
        
        print(f"✓ Created: {filepath}")
        return ticket_id
    
    def complete_ticket(self, ticket_id):
        """Move ticket to completed"""
        src = os.path.join(self.active_dir, f"{ticket_id}.json")
        dst = os.path.join(self.completed_dir, f"{ticket_id}.json")
        
        if not os.path.exists(src):
            print(f"✗ Not found: {src}")
            return False
        
        # Update status
        with open(src, 'r') as f:
            ticket = json.load(f)
        ticket['status'] = 'completed'
        ticket['updated_at'] = datetime.now().isoformat()
        
        with open(src, 'w') as f:
            json.dump(ticket, f, indent=2)
        
        os.rename(src, dst)
        print(f"✓ Completed: {dst}")
        return True
    
    def list_active(self):
        """List active tickets"""
        tickets = []
        for f in os.listdir(self.active_dir):
            if f.endswith('.json'):
                with open(os.path.join(self.active_dir, f)) as fp:
                    tickets.append(json.load(fp))
        return tickets

def main():
    parser = argparse.ArgumentParser(description='FIS Lifecycle')
    subparsers = parser.add_subparsers(dest='command')
    
    # Create
    create_parser = subparsers.add_parser('create', help='Create ticket')
    create_parser.add_argument('--agent', required=True)
    create_parser.add_argument('--task', required=True)
    create_parser.add_argument('--role', default='worker')
    
    # Complete
    complete_parser = subparsers.add_parser('complete', help='Complete ticket')
    complete_parser.add_argument('--ticket-id', required=True)
    
    # List
    list_parser = subparsers.add_parser('list', help='List active tickets')
    
    args = parser.parse_args()
    
    fis = FISLifecycle()
    
    if args.command == 'create':
        fis.create_ticket(args.agent, args.task, args.role)
    elif args.command == 'complete':
        fis.complete_ticket(args.ticket_id)
    elif args.command == 'list':
        tickets = fis.list_active()
        for t in tickets:
            task = t.get('task', '')
            if isinstance(task, dict):
                task = task.get('description', '')
            print(f"{t['ticket_id']}: {str(task)[:50]}...")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
