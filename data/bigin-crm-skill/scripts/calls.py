"""
Call Logging Module
CLI and programmatic interface for Bigin Call operations
"""

import argparse
import json
import sys
from typing import Optional, Dict, Any, List
from datetime import datetime

from bigin_crm import BiginCRM
from auth import init_auth_from_config


class CallManager:
    """
    Manager class for call logging operations
    """
    
    def __init__(self, crm_client: BiginCRM):
        self.crm = crm_client
    
    def create(
        self,
        subject: str,
        related_to: Optional[str] = None,
        call_type: str = "Outbound",
        duration_minutes: int = 0,
        outcome: Optional[str] = None,
        description: Optional[str] = None,
        owner: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Log a call
        
        Args:
            subject: Call subject/topic
            related_to: Related record in format "module:record_id"
            call_type: Call type (Outbound, Inbound)
            duration_minutes: Call duration
            outcome: Call outcome/result
            description: Call notes
            owner: Call owner
            **kwargs: Additional fields
            
        Returns:
            Created call record
        """
        data = {
            "Subject": subject,
            "Call_Type": call_type,
            "Call_Duration": f"{duration_minutes}:00"
        }
        
        if outcome:
            data["Call_Result"] = outcome
        if description:
            data["Description"] = description
        if owner:
            data["Owner"] = {"email": owner}
        if related_to:
            module, record_id = related_to.split(":")
            data["What_Id"] = {"id": record_id}
            data["$se_module"] = module
        
        data.update(kwargs)
        
        return self.crm.create_call(data)
    
    def list(
        self,
        related_to: Optional[str] = None,
        call_type: Optional[str] = None,
        limit: int = 200
    ) -> List[Dict[str, Any]]:
        """
        List logged calls
        
        Args:
            related_to: Filter by related record
            call_type: Filter by call type
            limit: Maximum records
            
        Returns:
            List of call records
        """
        result = self.crm.get_calls(related_to=related_to, limit=limit)
        calls = result.get("data", [])
        
        if call_type:
            calls = [
                c for c in calls
                if c.get("data", {}).get("Call_Type") == call_type
            ]
        
        return calls
    
    def log_outbound(
        self,
        contact_id: str,
        subject: str,
        duration: int = 0,
        outcome: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log an outbound call to a contact
        
        Args:
            contact_id: Contact ID
            subject: Call subject
            duration: Call duration in minutes
            outcome: Call outcome
            
        Returns:
            Created call record
        """
        return self.create(
            subject=subject,
            related_to=f"Contacts:{contact_id}",
            call_type="Outbound",
            duration_minutes=duration,
            outcome=outcome
        )
    
    def log_inbound(
        self,
        contact_id: str,
        subject: str,
        duration: int = 0,
        outcome: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log an inbound call from a contact
        
        Args:
            contact_id: Contact ID
            subject: Call subject
            duration: Call duration in minutes
            outcome: Call outcome
            
        Returns:
            Created call record
        """
        return self.create(
            subject=subject,
            related_to=f"Contacts:{contact_id}",
            call_type="Inbound",
            duration_minutes=duration,
            outcome=outcome
        )


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Bigin Call Logging")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Log a call")
    create_parser.add_argument("--subject", required=True, help="Call subject")
    create_parser.add_argument("--related-to", help="Related record (module:id)")
    create_parser.add_argument("--type", default="Outbound",
                              choices=["Outbound", "Inbound"],
                              help="Call type")
    create_parser.add_argument("--duration", type=int, default=0,
                              help="Duration in minutes")
    create_parser.add_argument("--outcome", help="Call outcome/result")
    create_parser.add_argument("--description", help="Call notes")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List logged calls")
    list_parser.add_argument("--related-to", help="Filter by related record")
    list_parser.add_argument("--type", choices=["Outbound", "Inbound"],
                            help="Filter by type")
    list_parser.add_argument("--limit", type=int, default=200, help="Max results")
    
    # Outbound command
    outbound_parser = subparsers.add_parser("outbound", help="Log outbound call")
    outbound_parser.add_argument("--contact-id", required=True, help="Contact ID")
    outbound_parser.add_argument("--subject", required=True, help="Call subject")
    outbound_parser.add_argument("--duration", type=int, default=0,
                                help="Duration in minutes")
    outbound_parser.add_argument("--outcome", help="Call outcome")
    
    # Inbound command
    inbound_parser = subparsers.add_parser("inbound", help="Log inbound call")
    inbound_parser.add_argument("--contact-id", required=True, help="Contact ID")
    inbound_parser.add_argument("--subject", required=True, help="Call subject")
    inbound_parser.add_argument("--duration", type=int, default=0,
                               help="Duration in minutes")
    inbound_parser.add_argument("--outcome", help="Call outcome")
    
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
        manager = CallManager(crm)
        
        # Execute command
        if args.command == "create":
            result = manager.create(
                subject=args.subject,
                related_to=args.related_to,
                call_type=args.type,
                duration_minutes=args.duration,
                outcome=args.outcome,
                description=args.description
            )
            print(json.dumps(result, indent=2))
        
        elif args.command == "list":
            results = manager.list(
                related_to=args.related_to,
                call_type=args.type,
                limit=args.limit
            )
            print(json.dumps(results, indent=2))
        
        elif args.command == "outbound":
            result = manager.log_outbound(
                contact_id=args.contact_id,
                subject=args.subject,
                duration=args.duration,
                outcome=args.outcome
            )
            print(json.dumps(result, indent=2))
        
        elif args.command == "inbound":
            result = manager.log_inbound(
                contact_id=args.contact_id,
                subject=args.subject,
                duration=args.duration,
                outcome=args.outcome
            )
            print(json.dumps(result, indent=2))
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
