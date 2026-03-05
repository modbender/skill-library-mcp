"""
Automation Module Tests
Unit tests for automation workflows
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import sys

sys.path.insert(0, '../scripts')

from scripts.bigin_crm import BiginCRM
from scripts.automation import AutomationManager


class TestAutomationManager(unittest.TestCase):
    """Test cases for AutomationManager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_crm = Mock(spec=BiginCRM)
        self.manager = AutomationManager(self.mock_crm)
    
    def test_auto_assign_unassigned(self):
        """Test auto-assigning unassigned pipelines"""
        # Mock unassigned pipelines
        mock_pipelines = {
            "data": [
                {"data": {"id": "1", "Deal_Name": "Deal 1"}},
                {"data": {"id": "2", "Deal_Name": "Deal 2"}},
                {"data": {"id": "3", "Deal_Name": "Deal 3"}}
            ]
        }
        mock_update_response = {
            "data": [{"code": "SUCCESS", "message": "Updated"}]
        }
        
        self.mock_crm.get_pipelines.return_value = mock_pipelines
        self.mock_crm.update_pipeline.return_value = mock_update_response
        
        owners = ["sales1@company.com", "sales2@company.com"]
        results = self.manager.auto_assign_unassigned(owners, round_robin=True)
        
        self.assertEqual(len(results), 3)
        self.assertEqual(self.mock_crm.update_pipeline.call_count, 3)
        
        # Check round-robin assignment
        first_call = self.mock_crm.update_pipeline.call_args_list[0]
        self.assertEqual(first_call[0][1]["Owner"]["email"], "sales1@company.com")
    
    def test_create_follow_up_tasks(self):
        """Test creating follow-up tasks for stale pipelines"""
        # Mock open pipelines
        mock_pipelines = {
            "data": [
                {
                    "data": {
                        "id": "1",
                        "Deal_Name": "Stale Deal",
                        "Stage": "Prospecting",
                        "Last_Activity_Time": "2026-01-01"
                    }
                },
                {
                    "data": {
                        "id": "2",
                        "Deal_Name": "Active Deal",
                        "Stage": "Negotiation",
                        "Last_Activity_Time": datetime.now().strftime("%Y-%m-%d")
                    }
                }
            ]
        }
        mock_task_response = {
            "data": [{"code": "SUCCESS", "details": {"id": "task123"}}]
        }
        
        self.mock_crm.get_pipelines.return_value = mock_pipelines
        self.mock_crm.create_task.return_value = mock_task_response
        
        results = self.manager.create_follow_up_tasks(stale_days=7)
        
        # Should only create task for stale pipeline
        self.assertEqual(len(results), 1)
        self.mock_crm.create_task.assert_called_once()
    
    def test_advance_stale_pipelines_proposal(self):
        """Test advancing stale proposal pipelines"""
        # Mock pipelines in proposal stage
        mock_pipelines = {
            "data": [
                {
                    "data": {
                        "id": "1",
                        "Deal_Name": "Old Proposal",
                        "Stage": "Proposal/Price Quote",
                        "Modified_Time": "2026-01-01"
                    }
                }
            ]
        }
        mock_advance_response = {
            "data": [{"code": "SUCCESS", "message": "Advanced"}]
        }
        
        self.mock_crm.get_pipelines.return_value = mock_pipelines
        self.mock_crm.advance_pipeline.return_value = mock_advance_response
        
        results = self.manager.advance_stale_pipelines(
            criteria="proposal-sent-and-7-days",
            target_stage="Negotiation/Review"
        )
        
        self.assertEqual(len(results), 1)
        self.mock_crm.advance_pipeline.assert_called_once_with("1", "Negotiation/Review")
    
    def test_advance_high_probability(self):
        """Test advancing high probability pipelines"""
        # Mock pipelines with high probability
        mock_pipelines = {
            "data": [
                {
                    "data": {
                        "id": "1",
                        "Deal_Name": "Likely Win",
                        "Stage": "Negotiation/Review",
                        "Probability": 85
                    }
                },
                {
                    "data": {
                        "id": "2",
                        "Deal_Name": "Uncertain",
                        "Stage": "Negotiation/Review",
                        "Probability": 60
                    }
                }
            ]
        }
        mock_advance_response = {
            "data": [{"code": "SUCCESS", "message": "Advanced"}]
        }
        
        self.mock_crm.get_pipelines.return_value = mock_pipelines
        self.mock_crm.advance_pipeline.return_value = mock_advance_response
        
        results = self.manager.advance_stale_pipelines(
            criteria="probability-gt-80"
        )
        
        # Should only advance the one with >80% probability
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["probability"], 85)
    
    def test_identify_stuck_pipelines(self):
        """Test identifying stuck pipelines"""
        # Mock pipelines
        old_date = (datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d")
        mock_pipelines = {
            "data": [
                {
                    "data": {
                        "id": "1",
                        "Deal_Name": "Stuck Deal",
                        "Stage": "Prospecting",
                        "Amount": 50000,
                        "Modified_Time": old_date,
                        "Owner": {"email": "sales@company.com"}
                    }
                },
                {
                    "data": {
                        "id": "2",
                        "Deal_Name": "Won Deal",
                        "Stage": "Closed Won",
                        "Modified_Time": old_date
                    }
                }
            ]
        }
        
        self.mock_crm.get_pipelines.return_value = mock_pipelines
        
        results = self.manager.identify_stuck_pipelines(days_in_stage=14)
        
        # Should only return non-closed pipelines
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["pipeline_id"], "1")
        self.assertEqual(results[0]["stage"], "Prospecting")
        self.assertIn("suggestion", results[0])
    
    def test_get_stage_suggestion(self):
        """Test getting suggestions for different stages"""
        suggestions = {
            "Prospecting": "Send initial outreach email",
            "Qualification": "Schedule qualification call",
            "Needs Analysis": "Conduct needs assessment",
            "Proposal/Price Quote": "Follow up on proposal acceptance",
            "Unknown Stage": "Review and follow up"
        }
        
        for stage, expected_phrase in suggestions.items():
            suggestion = self.manager._get_stage_suggestion(stage)
            self.assertIn(expected_phrase, suggestion)


class TestAutomationIntegration(unittest.TestCase):
    """Integration-style tests for automation workflows"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_crm = Mock(spec=BiginCRM)
        self.manager = AutomationManager(self.mock_crm)
    
    def test_full_automation_workflow(self):
        """Test a complete automation workflow"""
        # 1. Identify unassigned pipelines
        unassigned = {
            "data": [
                {"data": {"id": "1", "Deal_Name": "Unassigned 1"}},
                {"data": {"id": "2", "Deal_Name": "Unassigned 2"}}
            ]
        }
        self.mock_crm.get_pipelines.return_value = unassigned
        self.mock_crm.update_pipeline.return_value = {"code": "SUCCESS"}
        
        # Assign them
        assign_results = self.manager.auto_assign_unassigned(
            ["sales1@company.com", "sales2@company.com"],
            round_robin=True
        )
        
        # 2. Create follow-up tasks for stale ones
        stale_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        stale_pipelines = {
            "data": [
                {
                    "data": {
                        "id": "1",
                        "Deal_Name": "Stale Deal",
                        "Stage": "Prospecting",
                        "Last_Activity_Time": stale_date
                    }
                }
            ]
        }
        self.mock_crm.get_pipelines.return_value = stale_pipelines
        self.mock_crm.create_task.return_value = {"code": "SUCCESS"}
        
        task_results = self.manager.create_follow_up_tasks(stale_days=7)
        
        # Verify workflow completed
        self.assertEqual(len(assign_results), 2)
        self.assertEqual(len(task_results), 1)


if __name__ == "__main__":
    unittest.main()
