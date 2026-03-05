"""
Task Management Module
CLI and programmatic interface for Bigin Task operations
"""

import argparse
import json
import sys
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from bigin_crm import BiginCRM
from auth import init_auth_from_config


class TaskManager:
    """
    Manager class for task operations
    """
    
    def __init__(self, crm_client: BiginCRM):
        self.crm = crm_client
    
    def create(
        self,
        subject: str,
        related_to: Optional[str] = None,
        due_date: Optional[str] = None,
        priority: str = "Normal",
        owner: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new task
        
        Args:
            subject: Task subject
            related_to: Related record in format "module:record_id"
            due_date: Due date (YYYY-MM-DD)
            priority: Task priority (High, Normal, Low)
            owner: Task owner
            description: Task description
            **kwargs: Additional fields
            
        Returns:
            Created task record
        """
        data = {
            "Subject": subject,
            "Priority": priority,
            "Status": "Open"
        }
        
        if due_date:
            data["Due_Date"] = due_date
        if owner:
            data["Owner"] = {"email": owner}
        if description:
            data["Description"] = description
        if related_to:
            # related_to format: "module:record_id" e.g., "Pipelines:12345"
            module, record_id = related_to.split(":")
            data["What_Id"] = {"id": record_id}
            data["$se_module"] = module
        
        data.update(kwargs)
        
        return self.crm.create_task(subject, related_to, due_date, owner, priority)
    
    def update(
        self,
        task_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update an existing task
        
        Args:
            task_id: Task ID to update
            **kwargs: Fields to update
            
        Returns:
            Updated task record
        """
        return self.crm.update_task(task_id, kwargs)
    
    def complete(self, task_id: str) -> Dict[str, Any]:
        """
        Mark task as completed
        
        Args:
            task_id: Task ID
            
        Returns:
            Updated task record
        """
        return self.crm.complete_task(task_id)
    
    def get(self, task_id: str) -> Dict[str, Any]:
        """
        Get task details
        
        Args:
            task_id: Task ID
            
        Returns:
            Task record
        """
        return self.crm.get_task(task_id)
    
    def list(
        self,
        due_before: Optional[str] = None,
        due_after: Optional[str] = None,
        status: str = "Open",
        owner: Optional[str] = None,
        limit: int = 200
    ) -> List[Dict[str, Any]]:
        """
        List tasks with filters
        
        Args:
            due_before: Filter tasks due before date
            due_after: Filter tasks due after date
            status: Task status (Open, Completed)
            owner: Filter by owner
            limit: Maximum records
            
        Returns:
            List of tasks
        """
        result = self.crm.get_tasks(due_before=due_before, status=status, limit=limit)
        tasks = result.get("data", [])
        
        # Additional client-side filtering
        if due_after:
            tasks = [
                t for t in tasks 
                if t.get("data", {}).get("Due_Date", "") >= due_after
            ]
        
        if owner:
            tasks = [
                t for t in tasks
                if t.get("data", {}).get("Owner", {}).get("email") == owner
            ]
        
        return tasks
    
    def list_upcoming(
        self,
        days: int = 7,
        status: str = "Open"
    ) -> List[Dict[str, Any]]:
        """
        List upcoming tasks for next N days
        
        Args:
            days: Number of days to look ahead
            status: Task status
            
        Returns:
            List of upcoming tasks
        """
        today = datetime.now().strftime("%Y-%m-%d")
        future = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        
        return self.list(
            due_before=future,
            due_after=today,
            status=status
        )
    
    def list_overdue(
        self,
        owner: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List overdue tasks
        
        Args:
            owner: Filter by owner
            
        Returns:
            List of overdue tasks
        """
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        return self.list(
            due_before=yesterday,
            status="Open",
            owner=owner
        )
    
    def delete(self, task_id: str) -> Dict[str, Any]:
        """
        Delete a task
        
        Args:
            task_id: Task ID
            
        Returns:
            Deletion result
        """
        return self.crm.delete_task(task_id)
    
    def create_follow_up(
        self,
        related_to: str,
        subject: str = "Follow up",
        days: int = 3,
        priority: str = "Normal"
    ) -> Dict[str, Any]:
        """
        Create a follow-up task
        
        Args:
            related_to: Related record "module:id"
            subject: Task subject
            days: Days from now
            priority: Task priority
            
        Returns:
            Created task record
        """
        due_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        
        return self.create(
            subject=subject,
            related_to=related_to,
            due_date=due_date,
            priority=priority
        )


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Bigin Task Management")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a task")
    create_parser.add_argument("--subject", required=True, help="Task subject")
    create_parser.add_argument("--related-to", help="Related record (module:id)")
    create_parser.add_argument("--due", help="Due date (YYYY-MM-DD)")
    create_parser.add_argument("--priority", default="Normal",
                              choices=["High", "Normal", "Low"],
                              help="Task priority")
    create_parser.add_argument("--owner", help="Task owner")
    create_parser.add_argument("--description", help="Task description")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update a task")
    update_parser.add_argument("--id", required=True, help="Task ID")
    update_parser.add_argument("--subject", help="New subject")
    update_parser.add_argument("--due", help="New due date")
    update_parser.add_argument("--priority", choices=["High", "Normal", "Low"],
                              help="New priority")
    
    # Complete command
    complete_parser = subparsers.add_parser("complete", help="Complete a task")
    complete_parser.add_argument("--id", required=True, help="Task ID")
    
    # Get command
    get_parser = subparsers.add_parser("get", help="Get task details")
    get_parser.add_argument("--id", required=True, help="Task ID")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("--due-before", help="Due before date")
    list_parser.add_argument("--due-after", help="Due after date")
    list_parser.add_argument("--status", default="Open",
                            choices=["Open", "Completed"],
                            help="Task status")
    list_parser.add_argument("--owner", help="Filter by owner")
    list_parser.add_argument("--limit", type=int, default=200, help="Max results")
    
    # Upcoming command
    upcoming_parser = subparsers.add_parser("upcoming", help="List upcoming tasks")
    upcoming_parser.add_argument("--days", type=int, default=7,
                                help="Days to look ahead")
    upcoming_parser.add_argument("--status", default="Open",
                                choices=["Open", "Completed"])
    
    # Overdue command
    overdue_parser = subparsers.add_parser("overdue", help="List overdue tasks")
    overdue_parser.add_argument("--owner", help="Filter by owner")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("--id", required=True, help="Task ID")
    
    # Follow-up command
    followup_parser = subparsers.add_parser("follow-up", help="Create follow-up task")
    followup_parser.add_argument("--related-to", required=True, help="Related record (module:id)")
    followup_parser.add_argument("--subject", default="Follow up", help="Task subject")
    followup_parser.add_argument("--days", type=int, default=3, help="Days from now")
    followup_parser.add_argument("--priority", default="Normal",
                               choices=["High", "Normal", "Low"])
    
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
        manager = TaskManager(crm)
        
        # Execute command
        if args.command == "create":
            result = manager.create(
                subject=args.subject,
                related_to=args.related_to,
                due_date=args.due,
                priority=args.priority,
                owner=args.owner,
                description=args.description
            )
            print(json.dumps(result, indent=2))
        
        elif args.command == "update":
            kwargs = {}
            if args.subject:
                kwargs["Subject"] = args.subject
            if args.due:
                kwargs["Due_Date"] = args.due
            if args.priority:
                kwargs["Priority"] = args.priority
            
            result = manager.update(args.id, **kwargs)
            print(json.dumps(result, indent=2))
        
        elif args.command == "complete":
            result = manager.complete(args.id)
            print(json.dumps(result, indent=2))
        
        elif args.command == "get":
            result = manager.get(args.id)
            print(json.dumps(result, indent=2))
        
        elif args.command == "list":
            results = manager.list(
                due_before=args.due_before,
                due_after=args.due_after,
                status=args.status,
                owner=args.owner,
                limit=args.limit
            )
            print(json.dumps(results, indent=2))
        
        elif args.command == "upcoming":
            results = manager.list_upcoming(args.days, args.status)
            print(json.dumps(results, indent=2))
        
        elif args.command == "overdue":
            results = manager.list_overdue(args.owner)
            print(json.dumps(results, indent=2))
        
        elif args.command == "delete":
            result = manager.delete(args.id)
            print(json.dumps(result, indent=2))
        
        elif args.command == "follow-up":
            result = manager.create_follow_up(
                related_to=args.related_to,
                subject=args.subject,
                days=args.days,
                priority=args.priority
            )
            print(json.dumps(result, indent=2))
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
