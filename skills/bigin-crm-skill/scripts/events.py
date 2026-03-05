"""
Event/Meeting Management Module
CLI and programmatic interface for Bigin Event operations
"""

import argparse
import json
import sys
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from bigin_crm import BiginCRM
from auth import init_auth_from_config


class EventManager:
    """
    Manager class for event operations
    """
    
    def __init__(self, crm_client: BiginCRM):
        self.crm = crm_client
    
    def create(
        self,
        title: str,
        start_datetime: str,
        duration_minutes: int = 60,
        related_to: Optional[str] = None,
        location: Optional[str] = None,
        description: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new event/meeting
        
        Args:
            title: Event title
            start_datetime: Start datetime (YYYY-MM-DD HH:MM)
            duration_minutes: Meeting duration in minutes
            related_to: Related record in format "module:record_id"
            location: Meeting location or URL
            description: Event description
            attendees: List of attendee emails
            **kwargs: Additional fields
            
        Returns:
            Created event record
        """
        # Parse start datetime
        start_dt = datetime.strptime(start_datetime, "%Y-%m-%d %H:%M")
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        
        data = {
            "Event_Title": title,
            "Start_DateTime": start_dt.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            "End_DateTime": end_dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        }
        
        if location:
            data["Location"] = location
        if description:
            data["Description"] = description
        if related_to:
            module, record_id = related_to.split(":")
            data["What_Id"] = {"id": record_id}
            data["$se_module"] = module
        if attendees:
            data["Participants"] = [{"email": email} for email in attendees]
        
        data.update(kwargs)
        
        return self.crm.create_event(data)
    
    def list(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 200
    ) -> List[Dict[str, Any]]:
        """
        List events with date filters
        
        Args:
            start_date: Filter events starting after this date
            end_date: Filter events ending before this date
            limit: Maximum records
            
        Returns:
            List of events
        """
        result = self.crm.get_events(start_date=start_date, end_date=end_date, limit=limit)
        return result.get("data", [])
    
    def list_upcoming(
        self,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        List upcoming events for next N days
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            List of upcoming events
        """
        today = datetime.now().strftime("%Y-%m-%d")
        future = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        
        return self.list(start_date=today, end_date=future)
    
    def create_meeting_prep(
        self,
        contact_id: str,
        start_datetime: str,
        title: str = "Meeting",
        duration: int = 30
    ) -> Dict[str, Any]:
        """
        Create a meeting with prep notes
        
        Args:
            contact_id: Contact ID
            start_datetime: Meeting start time
            title: Meeting title
            duration: Duration in minutes
            
        Returns:
            Created event record
        """
        # Get contact info for context
        contact = self.crm.get_contact(contact_id)
        contact_data = contact.get("data", [{}])[0]
        contact_name = f"{contact_data.get('First_Name', '')} {contact_data.get('Last_Name', '')}"
        
        description = f"Meeting with {contact_name.strip()}"
        
        return self.create(
            title=title,
            start_datetime=start_datetime,
            duration_minutes=duration,
            related_to=f"Contacts:{contact_id}",
            description=description
        )


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Bigin Event Management")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create an event")
    create_parser.add_argument("--title", required=True, help="Event title")
    create_parser.add_argument("--start", required=True,
                              help="Start datetime (YYYY-MM-DD HH:MM)")
    create_parser.add_argument("--duration", type=int, default=60,
                              help="Duration in minutes")
    create_parser.add_argument("--related-to", help="Related record (module:id)")
    create_parser.add_argument("--location", help="Location or URL")
    create_parser.add_argument("--description", help="Event description")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List events")
    list_parser.add_argument("--start-date", help="Start from date")
    list_parser.add_argument("--end-date", help="End before date")
    list_parser.add_argument("--limit", type=int, default=200, help="Max results")
    
    # Upcoming command
    upcoming_parser = subparsers.add_parser("upcoming", help="List upcoming events")
    upcoming_parser.add_argument("--days", type=int, default=7,
                                help="Days to look ahead")
    
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
        manager = EventManager(crm)
        
        # Execute command
        if args.command == "create":
            result = manager.create(
                title=args.title,
                start_datetime=args.start,
                duration_minutes=args.duration,
                related_to=args.related_to,
                location=args.location,
                description=args.description
            )
            print(json.dumps(result, indent=2))
        
        elif args.command == "list":
            results = manager.list(
                start_date=args.start_date,
                end_date=args.end_date,
                limit=args.limit
            )
            print(json.dumps(results, indent=2))
        
        elif args.command == "upcoming":
            results = manager.list_upcoming(args.days)
            print(json.dumps(results, indent=2))
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
