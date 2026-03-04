"""
Company Management Module
CLI and programmatic interface for Bigin Company (Account) operations
"""

import argparse
import json
import sys
from typing import Optional, Dict, Any, List

from bigin_crm import BiginCRM
from auth import init_auth_from_config


class CompanyManager:
    """
    Manager class for company/account operations
    """
    
    def __init__(self, crm_client: BiginCRM):
        self.crm = crm_client
    
    def create(
        self,
        name: str,
        industry: Optional[str] = None,
        website: Optional[str] = None,
        employees: Optional[int] = None,
        address: Optional[str] = None,
        phone: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new company
        
        Args:
            name: Company name
            industry: Industry type
            website: Company website
            employees: Number of employees
            address: Company address
            phone: Company phone
            **kwargs: Additional fields
            
        Returns:
            Created company record
        """
        data = {
            "Account_Name": name
        }
        
        if industry:
            data["Industry"] = industry
        if website:
            data["Website"] = website
        if employees:
            data["Employees"] = employees
        if address:
            data["Billing_Street"] = address
        if phone:
            data["Phone"] = phone
        
        data.update(kwargs)
        
        return self.crm.create_company(data)
    
    def update(
        self,
        company_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update an existing company
        
        Args:
            company_id: Company ID to update
            **kwargs: Fields to update
            
        Returns:
            Updated company record
        """
        return self.crm.update_company(company_id, kwargs)
    
    def get(
        self,
        company_id: str,
        include_contacts: bool = False,
        include_pipelines: bool = False
    ) -> Dict[str, Any]:
        """
        Get company details
        
        Args:
            company_id: Company ID
            include_contacts: Include associated contacts
            include_pipelines: Include associated pipelines
            
        Returns:
            Company record with optional related data
        """
        company = self.crm.get_company(company_id)
        
        if include_contacts:
            # Search for contacts related to this company
            contacts = self.crm.get_contacts(
                criteria=f"(Account_Name:equals:{company_id})"
            )
            company["contacts"] = contacts.get("data", [])
        
        if include_pipelines:
            # Search for pipelines related to this company
            pipelines = self.crm.search_pipelines(f"company:{company_id}")
            company["pipelines"] = pipelines.get("data", [])
        
        return company
    
    def search(
        self,
        query: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search companies
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching companies
        """
        result = self.crm.search_companies(query)
        return result.get("data", [])[:limit]
    
    def list(
        self,
        criteria: Optional[str] = None,
        limit: int = 200
    ) -> List[Dict[str, Any]]:
        """
        List companies with optional criteria
        
        Args:
            criteria: Filter criteria
            limit: Maximum records
            
        Returns:
            List of companies
        """
        result = self.crm.get_companies(criteria=criteria, limit=limit)
        return result.get("data", [])
    
    def delete(self, company_id: str) -> Dict[str, Any]:
        """
        Delete a company
        
        Args:
            company_id: Company ID
            
        Returns:
            Deletion result
        """
        return self.crm.delete_company(company_id)
    
    def find_or_create(
        self,
        name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Find company by name or create if not exists
        
        Args:
            name: Company name to search/create
            **kwargs: Additional fields for creation
            
        Returns:
            Company record (existing or new)
        """
        # Search for existing company
        search_results = self.search(name, limit=10)
        
        for result in search_results:
            company_name = result.get("data", {}).get("Account_Name", "").lower()
            if company_name == name.lower():
                return result
        
        # Not found, create new
        return self.create(name, **kwargs)


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Bigin Company Management")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a company")
    create_parser.add_argument("--name", required=True, help="Company name")
    create_parser.add_argument("--industry", help="Industry type")
    create_parser.add_argument("--website", help="Company website")
    create_parser.add_argument("--employees", type=int, help="Number of employees")
    create_parser.add_argument("--address", help="Company address")
    create_parser.add_argument("--phone", help="Company phone")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update a company")
    update_parser.add_argument("--id", required=True, help="Company ID")
    update_parser.add_argument("--phone", help="New phone number")
    update_parser.add_argument("--website", help="New website")
    update_parser.add_argument("--industry", help="New industry")
    
    # Get command
    get_parser = subparsers.add_parser("get", help="Get company details")
    get_parser.add_argument("--id", required=True, help="Company ID")
    get_parser.add_argument("--include-contacts", action="store_true",
                          help="Include associated contacts")
    get_parser.add_argument("--include-pipelines", action="store_true",
                          help="Include associated pipelines")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search companies")
    search_parser.add_argument("--query", required=True, help="Search query")
    search_parser.add_argument("--limit", type=int, default=100, help="Max results")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List companies")
    list_parser.add_argument("--criteria", help="Filter criteria")
    list_parser.add_argument("--limit", type=int, default=200, help="Max results")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a company")
    delete_parser.add_argument("--id", required=True, help="Company ID")
    
    # Find or create command
    find_create_parser = subparsers.add_parser("find-or-create",
                                               help="Find or create company")
    find_create_parser.add_argument("--name", required=True, help="Company name")
    find_create_parser.add_argument("--industry", help="Industry type")
    find_create_parser.add_argument("--website", help="Company website")
    
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
        manager = CompanyManager(crm)
        
        # Execute command
        if args.command == "create":
            result = manager.create(
                name=args.name,
                industry=args.industry,
                website=args.website,
                employees=args.employees,
                address=args.address,
                phone=args.phone
            )
            print(json.dumps(result, indent=2))
        
        elif args.command == "update":
            kwargs = {}
            if args.phone:
                kwargs["Phone"] = args.phone
            if args.website:
                kwargs["Website"] = args.website
            if args.industry:
                kwargs["Industry"] = args.industry
            
            result = manager.update(args.id, **kwargs)
            print(json.dumps(result, indent=2))
        
        elif args.command == "get":
            result = manager.get(
                args.id,
                args.include_contacts,
                args.include_pipelines
            )
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
        
        elif args.command == "find-or-create":
            result = manager.find_or_create(
                name=args.name,
                industry=args.industry,
                website=args.website
            )
            print(json.dumps(result, indent=2))
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
