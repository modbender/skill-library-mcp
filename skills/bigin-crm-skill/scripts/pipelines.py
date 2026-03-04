"""
Pipeline Management Module
CLI and programmatic interface for Bigin Pipeline operations
"""

import argparse
import json
import sys
from typing import Optional, Dict, Any, List
from datetime import datetime

from bigin_crm import BiginCRM
from auth import init_auth_from_config, BiginOAuth


class PipelineManager:
    """
    Manager class for pipeline operations
    """
    
    # Valid stages for Sales Pipeline Standard (from Bigin API)
    VALID_STAGES = [
        "Qualification",
        "Needs Analysis",
        "Proposal/Price Quote",
        "Negotiation/Review",
        "Closed Won",
        "Closed Lost"
    ]
    
    # Default sub-pipeline value (required by Bigin API)
    DEFAULT_SUB_PIPELINE = "Sales Pipeline Standard"
    
    def __init__(self, crm_client: BiginCRM):
        self.crm = crm_client
    
    def _validate_stage(self, stage: str) -> None:
        """
        Validate that the stage is valid for the pipeline.
        
        Args:
            stage: Stage name to validate
            
        Raises:
            ValueError: If stage is not in VALID_STAGES
        """
        if stage not in self.VALID_STAGES:
            raise ValueError(
                f"Invalid stage '{stage}'. Valid stages are: {', '.join(self.VALID_STAGES)}"
            )
    
    def create(
        self,
        contact_id: Optional[str] = None,
        company_id: Optional[str] = None,
        stage: str = "Qualification",
        amount: float = 0.0,
        closing_date: Optional[str] = None,
        owner: Optional[str] = None,
        name: Optional[str] = None,
        sub_pipeline: str = "Sales Pipeline Standard",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new pipeline entry
        
        Args:
            contact_id: Associated contact ID
            company_id: Associated company/account ID
            stage: Pipeline stage (default: Qualification)
            amount: Deal amount
            closing_date: Expected closing date (YYYY-MM-DD)
            owner: Owner email
            name: Pipeline/deal name
            sub_pipeline: Sub-pipeline name (default: Sales Pipeline Standard)
            **kwargs: Additional fields
            
        Returns:
            Created pipeline record
            
        Raises:
            ValueError: If stage is invalid
        """
        # Validate stage early to provide clear error message
        self._validate_stage(stage)
        
        data = {
            "Stage": stage,
            "Amount": amount,
            "Sub_Pipeline": sub_pipeline
        }
        
        if name:
            data["Deal_Name"] = name
        if contact_id:
            data["Contact_Name"] = {"id": contact_id}
        if company_id:
            data["Account_Name"] = {"id": company_id}
        if closing_date:
            data["Closing_Date"] = closing_date
        if owner:
            data["Owner"] = {"email": owner}
        
        # Add any additional fields
        data.update(kwargs)
        
        return self.crm.create_pipeline(data)
    
    def update(
        self,
        pipeline_id: str,
        stage: Optional[str] = None,
        amount: Optional[float] = None,
        probability: Optional[int] = None,
        closing_date: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update an existing pipeline
        
        Args:
            pipeline_id: Pipeline ID to update
            stage: New stage
            amount: New amount
            probability: Win probability (0-100)
            closing_date: New closing date
            **kwargs: Additional fields to update
            
        Returns:
            Updated pipeline record
        """
        data = {}
        
        if stage:
            data["Stage"] = stage
        if amount is not None:
            data["Amount"] = amount
        if probability is not None:
            data["Probability"] = probability
        if closing_date:
            data["Closing_Date"] = closing_date
        
        data.update(kwargs)
        
        return self.crm.update_pipeline(pipeline_id, data)
    
    def advance(
        self,
        pipeline_id: str,
        new_stage: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Advance pipeline to next stage
        
        Args:
            pipeline_id: Pipeline ID
            new_stage: Optional specific stage to move to
            
        Returns:
            Updated pipeline record
            
        Raises:
            ValueError: If new_stage is provided but invalid
        """
        if new_stage:
            self._validate_stage(new_stage)
            return self.crm.advance_pipeline(pipeline_id, new_stage)
        
        # Get current pipeline to determine next stage
        current = self.crm.get_pipeline(pipeline_id)
        current_stage = current.get("data", [{}])[0].get("Stage", "Qualification")
        
        # Define stage progression (matches Bigin Sales Pipeline Standard)
        stage_flow = [
            "Qualification",
            "Needs Analysis",
            "Proposal/Price Quote",
            "Negotiation/Review",
            "Closed Won"
        ]
        
        if current_stage in stage_flow:
            current_index = stage_flow.index(current_stage)
            if current_index < len(stage_flow) - 1:
                next_stage = stage_flow[current_index + 1]
                return self.crm.advance_pipeline(pipeline_id, next_stage)
        
        return self.crm.advance_pipeline(pipeline_id)
    
    def win(self, pipeline_id: str) -> Dict[str, Any]:
        """
        Mark pipeline as won
        
        Args:
            pipeline_id: Pipeline ID
            
        Returns:
            Updated pipeline record
        """
        return self.crm.win_pipeline(pipeline_id)
    
    def lose(self, pipeline_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Mark pipeline as lost
        
        Args:
            pipeline_id: Pipeline ID
            reason: Loss reason
            
        Returns:
            Updated pipeline record
        """
        return self.crm.lose_pipeline(pipeline_id, reason)
    
    def list(
        self,
        stage: Optional[str] = None,
        owner: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        List pipelines with filters
        
        Args:
            stage: Filter by stage
            owner: Filter by owner
            limit: Maximum records
            
        Returns:
            List of pipeline records
        """
        result = self.crm.get_pipelines(stage=stage, owner=owner, limit=limit)
        return result.get("data", [])
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search pipelines
        
        Args:
            query: Search query
            
        Returns:
            List of matching pipelines
        """
        result = self.crm.search_pipelines(query)
        return result.get("data", [])
    
    def get(self, pipeline_id: str, include_history: bool = False) -> Dict[str, Any]:
        """
        Get pipeline details
        
        Args:
            pipeline_id: Pipeline ID
            include_history: Include activity history
            
        Returns:
            Pipeline record
        """
        pipeline = self.crm.get_pipeline(pipeline_id)
        
        if include_history:
            # Fetch related tasks, events, calls
            # This would require additional API calls
            pass
        
        return pipeline
    
    def bulk_update(
        self,
        from_stage: str,
        to_stage: str,
        criteria: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Bulk update pipelines from one stage to another
        
        Args:
            from_stage: Current stage to filter
            to_stage: Target stage
            criteria: Additional criteria
            
        Returns:
            List of update results
        """
        pipelines = self.list(stage=from_stage, limit=200)
        results = []
        
        for record in pipelines:
            pipeline_id = record.get("data", {}).get("id")
            if pipeline_id:
                # Apply additional criteria if specified
                if criteria and not self._matches_criteria(record, criteria):
                    continue
                
                result = self.crm.advance_pipeline(pipeline_id, to_stage)
                results.append(result)
        
        return results
    
    def _matches_criteria(self, record: Dict, criteria: str) -> bool:
        """
        Check if record matches criteria string
        
        Args:
            record: Pipeline record
            criteria: Criteria string (e.g., "probability-gt-80")
            
        Returns:
            True if matches
        """
        # Simple criteria parsing
        data = record.get("data", {})
        
        if criteria == "probability-gt-80":
            prob = data.get("Probability", 0)
            return prob > 80
        
        # Add more criteria handlers as needed
        return True


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Bigin Pipeline Management")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Valid stages for help text
    valid_stages = "Qualification, Needs Analysis, Proposal/Price Quote, Negotiation/Review, Closed Won, Closed Lost"
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a pipeline")
    create_parser.add_argument("--contact-id", help="Associated contact ID")
    create_parser.add_argument("--company-id", help="Associated company ID")
    create_parser.add_argument("--stage", default="Qualification",
                               help=f"Pipeline stage (default: Qualification). Valid: {valid_stages}")
    create_parser.add_argument("--amount", type=float, default=0.0, help="Deal amount")
    create_parser.add_argument("--closing-date", help="Expected closing date (YYYY-MM-DD)")
    create_parser.add_argument("--owner", help="Owner email")
    create_parser.add_argument("--name", help="Pipeline name")
    create_parser.add_argument("--sub-pipeline", default="Sales Pipeline Standard",
                               help="Sub-pipeline name (default: Sales Pipeline Standard)")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update a pipeline")
    update_parser.add_argument("--id", required=True, help="Pipeline ID")
    update_parser.add_argument("--stage", help="New stage")
    update_parser.add_argument("--amount", type=float, help="New amount")
    update_parser.add_argument("--probability", type=int, help="Win probability (0-100)")
    update_parser.add_argument("--closing-date", help="New closing date")
    
    # Advance command
    advance_parser = subparsers.add_parser("advance", help="Advance pipeline stage")
    advance_parser.add_argument("--id", required=True, help="Pipeline ID")
    advance_parser.add_argument("--stage", help="Specific stage to move to")
    
    # Win/Lose commands
    win_parser = subparsers.add_parser("win", help="Mark pipeline as won")
    win_parser.add_argument("--id", required=True, help="Pipeline ID")
    
    lose_parser = subparsers.add_parser("lose", help="Mark pipeline as lost")
    lose_parser.add_argument("--id", required=True, help="Pipeline ID")
    lose_parser.add_argument("--reason", help="Loss reason")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List pipelines")
    list_parser.add_argument("--stage", help="Filter by stage")
    list_parser.add_argument("--owner", help="Filter by owner")
    list_parser.add_argument("--limit", type=int, default=50, help="Maximum records")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search pipelines")
    search_parser.add_argument("--query", required=True, help="Search query")
    search_parser.add_argument("--stage", help="Filter by stage")
    
    # Get command
    get_parser = subparsers.add_parser("get", help="Get pipeline details")
    get_parser.add_argument("--id", required=True, help="Pipeline ID")
    get_parser.add_argument("--include-history", action="store_true", help="Include history")
    
    # Bulk update command
    bulk_parser = subparsers.add_parser("bulk-update", help="Bulk update pipelines")
    bulk_parser.add_argument("--stage", required=True, help="Current stage")
    bulk_parser.add_argument("--new-stage", required=True, help="Target stage")
    bulk_parser.add_argument("--criteria", help="Additional criteria")
    
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
        manager = PipelineManager(crm)
        
        # Execute command
        if args.command == "create":
            result = manager.create(
                contact_id=args.contact_id,
                company_id=args.company_id,
                stage=args.stage,
                amount=args.amount,
                closing_date=args.closing_date,
                owner=args.owner,
                name=args.name,
                sub_pipeline=args.sub_pipeline
            )
            print(json.dumps(result, indent=2))
        
        elif args.command == "update":
            result = manager.update(
                pipeline_id=args.id,
                stage=args.stage,
                amount=args.amount,
                probability=args.probability,
                closing_date=args.closing_date
            )
            print(json.dumps(result, indent=2))
        
        elif args.command == "advance":
            result = manager.advance(args.id, args.stage)
            print(json.dumps(result, indent=2))
        
        elif args.command == "win":
            result = manager.win(args.id)
            print(json.dumps(result, indent=2))
        
        elif args.command == "lose":
            result = manager.lose(args.id, args.reason)
            print(json.dumps(result, indent=2))
        
        elif args.command == "list":
            results = manager.list(
                stage=args.stage,
                owner=args.owner,
                limit=args.limit
            )
            print(json.dumps(results, indent=2))
        
        elif args.command == "search":
            results = manager.search(args.query)
            if args.stage:
                results = [r for r in results if r.get("data", {}).get("Stage") == args.stage]
            print(json.dumps(results, indent=2))
        
        elif args.command == "get":
            result = manager.get(args.id, args.include_history)
            print(json.dumps(result, indent=2))
        
        elif args.command == "bulk-update":
            results = manager.bulk_update(args.stage, args.new_stage, args.criteria)
            print(json.dumps(results, indent=2))
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
