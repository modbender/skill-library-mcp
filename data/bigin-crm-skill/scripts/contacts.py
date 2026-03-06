"""
Contact Management Module
CLI and programmatic interface for Bigin Contact operations
"""

import argparse
import json
import sys
import csv
from typing import Optional, Dict, Any, List

from bigin_crm import BiginCRM
from auth import init_auth_from_config


class ContactManager:
    """
    Manager class for contact operations
    """
    
    def __init__(self, crm_client: BiginCRM):
        self.crm = crm_client
    
    def create(
        self,
        first_name: str,
        last_name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        company: Optional[str] = None,
        company_id: Optional[str] = None,
        source: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new contact
        
        Args:
            first_name: Contact first name
            last_name: Contact last name
            email: Email address
            phone: Phone number
            company: Company name (creates link if company_id not provided)
            company_id: Associated company/account ID
            source: Lead source
            **kwargs: Additional fields
            
        Returns:
            Created contact record
        """
        data = {
            "First_Name": first_name,
            "Last_Name": last_name
        }
        
        if email:
            data["Email"] = email
        if phone:
            data["Phone"] = phone
        if company_id:
            data["Account_Name"] = {"id": company_id}
        elif company:
            data["Account_Name"] = company
        if source:
            data["Lead_Source"] = source
        
        data.update(kwargs)
        
        return self.crm.create_contact(data)
    
    def update(
        self,
        contact_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update an existing contact
        
        Args:
            contact_id: Contact ID to update
            **kwargs: Fields to update
            
        Returns:
            Updated contact record
        """
        return self.crm.update_contact(contact_id, kwargs)
    
    def get(
        self,
        contact_id: str,
        include_pipelines: bool = False
    ) -> Dict[str, Any]:
        """
        Get contact details
        
        Args:
            contact_id: Contact ID
            include_pipelines: Include associated pipelines
            
        Returns:
            Contact record
        """
        contact = self.crm.get_contact(contact_id)
        
        if include_pipelines:
            # Search for pipelines related to this contact
            pipelines = self.crm.search_pipelines(f"contact:{contact_id}")
            contact["pipelines"] = pipelines.get("data", [])
        
        return contact
    
    def search(
        self,
        query: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search contacts
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching contacts
        """
        result = self.crm.search_contacts(query)
        return result.get("data", [])[:limit]
    
    def list(
        self,
        criteria: Optional[str] = None,
        limit: int = 200
    ) -> List[Dict[str, Any]]:
        """
        List contacts with optional criteria
        
        Args:
            criteria: Filter criteria
            limit: Maximum records
            
        Returns:
            List of contacts
        """
        result = self.crm.get_contacts(criteria=criteria, limit=limit)
        return result.get("data", [])
    
    def delete(self, contact_id: str) -> Dict[str, Any]:
        """
        Delete a contact
        
        Args:
            contact_id: Contact ID
            
        Returns:
            Deletion result
        """
        return self.crm.delete_contact(contact_id)
    
    def import_from_csv(
        self,
        file_path: str,
        mapping: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Import contacts from CSV file
        
        Args:
            file_path: Path to CSV file
            mapping: Field mapping dictionary (csv_column -> bigin_field)
            
        Returns:
            List of created contact records
        """
        results = []
        
        # Default mapping if not provided
        if mapping is None:
            mapping = {
                "First Name": "First_Name",
                "Last Name": "Last_Name",
                "Email": "Email",
                "Phone": "Phone",
                "Company": "Account_Name",
                "Source": "Lead_Source"
            }
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Map CSV columns to Bigin fields
                data = {}
                for csv_col, bigin_field in mapping.items():
                    if csv_col in row and row[csv_col]:
                        data[bigin_field] = row[csv_col]
                
                if data:
                    try:
                        result = self.crm.create_contact(data)
                        results.append(result)
                    except Exception as e:
                        results.append({"error": str(e), "data": data})
        
        return results
    
    def bulk_import(
        self,
        records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Bulk import contacts from list
        
        Args:
            records: List of contact dictionaries
            
        Returns:
            Bulk import result
        """
        return self.crm.bulk_import_contacts(records)


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Bigin Contact Management")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a contact")
    create_parser.add_argument("--first-name", required=True, help="First name")
    create_parser.add_argument("--last-name", required=True, help="Last name")
    create_parser.add_argument("--email", help="Email address")
    create_parser.add_argument("--phone", help="Phone number")
    create_parser.add_argument("--company", help="Company name")
    create_parser.add_argument("--company-id", help="Company ID")
    create_parser.add_argument("--source", help="Lead source")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update a contact")
    update_parser.add_argument("--id", required=True, help="Contact ID")
    update_parser.add_argument("--phone", help="New phone number")
    update_parser.add_argument("--email", help="New email")
    update_parser.add_argument("--company-id", help="New company ID")
    
    # Get command
    get_parser = subparsers.add_parser("get", help="Get contact details")
    get_parser.add_argument("--id", required=True, help="Contact ID")
    get_parser.add_argument("--include-pipelines", action="store_true", 
                          help="Include associated pipelines")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search contacts")
    search_parser.add_argument("--query", required=True, help="Search query")
    search_parser.add_argument("--limit", type=int, default=100, help="Max results")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List contacts")
    list_parser.add_argument("--criteria", help="Filter criteria")
    list_parser.add_argument("--limit", type=int, default=200, help="Max results")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a contact")
    delete_parser.add_argument("--id", required=True, help="Contact ID")
    
    # Import command
    import_parser = subparsers.add_parser("import", help="Import from CSV")
    import_parser.add_argument("--file", required=True, help="CSV file path")
    import_parser.add_argument("--mapping", help="Field mapping JSON file")
    
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
        manager = ContactManager(crm)
        
        # Execute command
        if args.command == "create":
            result = manager.create(
                first_name=args.first_name,
                last_name=args.last_name,
                email=args.email,
                phone=args.phone,
                company=args.company,
                company_id=args.company_id,
                source=args.source
            )
            print(json.dumps(result, indent=2))
        
        elif args.command == "update":
            kwargs = {}
            if args.phone:
                kwargs["Phone"] = args.phone
            if args.email:
                kwargs["Email"] = args.email
            if args.company_id:
                kwargs["Account_Name"] = {"id": args.company_id}
            
            result = manager.update(args.id, **kwargs)
            print(json.dumps(result, indent=2))
        
        elif args.command == "get":
            result = manager.get(args.id, args.include_pipelines)
            print(json.dumps(result, indent=2))
        
        elif args.command == "search":
            results = manager.search(args.query, args.limit)
            print(json.dumps(results, indent=2))
        
        elif args.command == "list":
            results = manager.list(args.criteria, args.limit)
            print(json.dumps(results, indent=2))
        
        elif args.command == "delete":
            result = manager.delete(args.id)
            print(json.dumps(result, indent=2))
        
        elif args.command == "import":
            mapping = None
            if args.mapping:
                with open(args.mapping, 'r') as f:
                    mapping = json.load(f)
            
            results = manager.import_from_csv(args.file, mapping)
            print(json.dumps(results, indent=2))
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
