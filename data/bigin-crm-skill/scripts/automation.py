"""
Pipeline Automation Module
CLI and programmatic interface for Bigin CRM automation workflows
"""

import argparse
import json
import sys
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from bigin_crm import BiginCRM
from auth import init_auth_from_config


class AutomationManager:
    """
    Manager class for automation workflows
    """
    
    def __init__(self, crm_client: BiginCRM):
        self.crm = crm_client
    
    def auto_assign_unassigned(
        self,
        owners: List[str],
        round_robin: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Auto-assign unassigned pipelines to owners
        
        Args:
            owners: List of owner emails
            round_robin: Use round-robin assignment
            
        Returns:
            List of assignment results
        """
        # Get unassigned pipelines
        unassigned = self.crm.get_pipelines(
            criteria="(Owner:equals:None)",
            limit=200
        )
        
        results = []
        owner_index = 0
        
        for record in unassigned.get("data", []):
            pipeline_id = record.get("data", {}).get("id")
            if not pipeline_id:
                continue
            
            # Select owner
            if round_robin:
                owner = owners[owner_index % len(owners)]
                owner_index += 1
            else:
                # Random assignment
                import random
                owner = random.choice(owners)
            
            try:
                result = self.crm.update_pipeline(
                    pipeline_id,
                    {"Owner": {"email": owner}}
                )
                results.append({
                    "pipeline_id": pipeline_id,
                    "assigned_to": owner,
                    "status": "success",
                    "result": result
                })
            except Exception as e:
                results.append({
                    "pipeline_id": pipeline_id,
                    "assigned_to": owner,
                    "status": "error",
                    "error": str(e)
                })
        
        return results
    
    def create_follow_up_tasks(
        self,
        stale_days: int = 7,
        task_subject: str = "Follow up on stale pipeline"
    ) -> List[Dict[str, Any]]:
        """
        Create follow-up tasks for stale pipelines
        
        Args:
            stale_days: Days since last activity
            task_subject: Task subject template
            
        Returns:
            List of created tasks
        """
        # Get open pipelines
        pipelines = self.crm.get_pipelines(limit=200)
        
        results = []
        cutoff_date = (datetime.now() - timedelta(days=stale_days)).strftime("%Y-%m-%d")
        
        for record in pipelines.get("data", []):
            data = record.get("data", {})
            pipeline_id = data.get("id")
            stage = data.get("Stage", "")
            
            # Skip closed pipelines
            if stage in ["Closed Won", "Closed Lost"]:
                continue
            
            # Check last activity date (if available)
            last_activity = data.get("Last_Activity_Time", "")
            
            # If no activity or stale, create task
            if not last_activity or last_activity < cutoff_date:
                try:
                    task = self.crm.create_task(
                        subject=f"{task_subject} - {data.get('Deal_Name', 'Unknown')}",
                        related_to=f"Pipelines:{pipeline_id}",
                        due_date=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
                        priority="High"
                    )
                    results.append({
                        "pipeline_id": pipeline_id,
                        "task": task,
                        "status": "created"
                    })
                except Exception as e:
                    results.append({
                        "pipeline_id": pipeline_id,
                        "status": "error",
                        "error": str(e)
                    })
        
        return results
    
    def advance_stale_pipelines(
        self,
        criteria: str = "proposal-sent-and-7-days",
        target_stage: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Auto-advance pipelines based on criteria
        
        Args:
            criteria: Criteria for advancement
            target_stage: Optional specific target stage
            
        Returns:
            List of advancement results
        """
        results = []
        
        if criteria == "proposal-sent-and-7-days":
            # Get pipelines in "Proposal/Price Quote" stage for >7 days
            pipelines = self.crm.get_pipelines(
                stage="Proposal/Price Quote",
                limit=200
            )
            
            cutoff_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            
            for record in pipelines.get("data", []):
                data = record.get("data", {})
                pipeline_id = data.get("id")
                modified_time = data.get("Modified_Time", "")
                
                if modified_time and modified_time < cutoff_date:
                    try:
                        new_stage = target_stage or "Negotiation/Review"
                        result = self.crm.advance_pipeline(pipeline_id, new_stage)
                        results.append({
                            "pipeline_id": pipeline_id,
                            "from_stage": "Proposal/Price Quote",
                            "to_stage": new_stage,
                            "status": "advanced",
                            "result": result
                        })
                    except Exception as e:
                        results.append({
                            "pipeline_id": pipeline_id,
                            "status": "error",
                            "error": str(e)
                        })
        
        elif criteria == "probability-gt-80":
            # Get pipelines with >80% probability
            pipelines = self.crm.get_pipelines(limit=200)
            
            for record in pipelines.get("data", []):
                data = record.get("data", {})
                probability = data.get("Probability", 0)
                stage = data.get("Stage", "")
                pipeline_id = data.get("id")
                
                if probability > 80 and stage not in ["Closed Won", "Closed Lost"]:
                    try:
                        new_stage = target_stage or "Negotiation/Review"
                        result = self.crm.advance_pipeline(pipeline_id, new_stage)
                        results.append({
                            "pipeline_id": pipeline_id,
                            "probability": probability,
                            "to_stage": new_stage,
                            "status": "advanced",
                            "result": result
                        })
                    except Exception as e:
                        results.append({
                            "pipeline_id": pipeline_id,
                            "status": "error",
                            "error": str(e)
                        })
        
        return results
    
    def identify_stuck_pipelines(
        self,
        days_in_stage: int = 14
    ) -> List[Dict[str, Any]]:
        """
        Identify pipelines stuck in same stage
        
        Args:
            days_in_stage: Days threshold for being "stuck"
            
        Returns:
            List of stuck pipelines with suggestions
        """
        pipelines = self.crm.get_pipelines(limit=200)
        
        stuck_pipelines = []
        cutoff_date = (datetime.now() - timedelta(days=days_in_stage)).strftime("%Y-%m-%d")
        
        for record in pipelines.get("data", []):
            data = record.get("data", {})
            stage = data.get("Stage", "")
            
            # Skip closed pipelines
            if stage in ["Closed Won", "Closed Lost"]:
                continue
            
            modified_time = data.get("Modified_Time", "")
            if modified_time and modified_time < cutoff_date:
                # Generate suggestion based on stage
                suggestion = self._get_stage_suggestion(stage)
                
                stuck_pipelines.append({
                    "pipeline_id": data.get("id"),
                    "deal_name": data.get("Deal_Name"),
                    "stage": stage,
                    "amount": data.get("Amount"),
                    "owner": data.get("Owner", {}).get("email"),
                    "last_modified": modified_time,
                    "days_in_stage": days_in_stage,
                    "suggestion": suggestion
                })
        
        return stuck_pipelines
    
    def _get_stage_suggestion(self, stage: str) -> str:
        """Get suggestion for stuck pipeline based on stage"""
        suggestions = {
            "Prospecting": "Send initial outreach email or make discovery call",
            "Qualification": "Schedule qualification call to understand requirements",
            "Needs Analysis": "Send questionnaire or schedule deep-dive meeting",
            "Value Proposition": "Prepare and send customized proposal",
            "Id. Decision Makers": "Request meeting with all stakeholders",
            "Proposal/Price Quote": "Follow up on proposal acceptance",
            "Negotiation/Review": "Address objections and finalize terms"
        }
        return suggestions.get(stage, "Review and follow up")


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Bigin Pipeline Automation")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Assign command
    assign_parser = subparsers.add_parser("assign", help="Auto-assign pipelines")
    assign_parser.add_argument("--unassigned", action="store_true",
                              help="Assign unassigned pipelines")
    assign_parser.add_argument("--round-robin", action="store_true",
                              help="Use round-robin assignment")
    assign_parser.add_argument("--owners", nargs="+", required=True,
                              help="List of owner emails")
    
    # Follow-up command
    followup_parser = subparsers.add_parser("follow-up",
                                           help="Create follow-up tasks")
    followup_parser.add_argument("--stale-days", type=int, default=7,
                                help="Days since last activity")
    followup_parser.add_argument("--create-tasks", action="store_true",
                                help="Create tasks for stale pipelines")
    
    # Advance command
    advance_parser = subparsers.add_parser("advance",
                                          help="Auto-advance pipelines")
    advance_parser.add_argument("--criteria", default="proposal-sent-and-7-days",
                             help="Advancement criteria")
    advance_parser.add_argument("--target-stage", help="Target stage")
    
    # Stuck pipelines command
    stuck_parser = subparsers.add_parser("stuck",
                                        help="Identify stuck pipelines")
    stuck_parser.add_argument("--days", type=int, default=14,
                             help="Days threshold for stuck pipelines")
    
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
        manager = AutomationManager(crm)
        
        # Execute command
        if args.command == "assign":
            if not args.unassigned:
                print("Error: --unassigned flag required")
                sys.exit(1)
            
            results = manager.auto_assign_unassigned(
                owners=args.owners,
                round_robin=args.round_robin
            )
            print(json.dumps(results, indent=2))
        
        elif args.command == "follow-up":
            if not args.create_tasks:
                # Just identify stale pipelines
                pipelines = crm.get_pipelines(limit=200)
                stale = []
                cutoff = (datetime.now() - timedelta(days=args.stale_days)).strftime("%Y-%m-%d")
                
                for record in pipelines.get("data", []):
                    data = record.get("data", {})
                    if data.get("Stage") not in ["Closed Won", "Closed Lost"]:
                        last_activity = data.get("Last_Activity_Time", "")
                        if not last_activity or last_activity < cutoff:
                            stale.append({
                                "id": data.get("id"),
                                "name": data.get("Deal_Name"),
                                "stage": data.get("Stage")
                            })
                
                print(json.dumps(stale, indent=2))
            else:
                results = manager.create_follow_up_tasks(args.stale_days)
                print(json.dumps(results, indent=2))
        
        elif args.command == "advance":
            results = manager.advance_stale_pipelines(
                criteria=args.criteria,
                target_stage=args.target_stage
            )
            print(json.dumps(results, indent=2))
        
        elif args.command == "stuck":
            results = manager.identify_stuck_pipelines(args.days)
            print(json.dumps(results, indent=2))
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
