"""
Pipeline Module Tests
Unit tests for pipeline operations
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from datetime import datetime

import sys
sys.path.insert(0, '../scripts')

from scripts.bigin_crm import BiginCRM
from scripts.pipelines import PipelineManager


class TestPipelineManager(unittest.TestCase):
    """Test cases for PipelineManager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_crm = Mock(spec=BiginCRM)
        self.manager = PipelineManager(self.mock_crm)
    
    def test_create_pipeline(self):
        """Test creating a pipeline"""
        # Mock response
        mock_response = {
            "data": [{
                "code": "SUCCESS",
                "details": {"id": "123456789"},
                "message": "Pipeline created successfully"
            }]
        }
        self.mock_crm.create_pipeline.return_value = mock_response
        
        # Test creation
        result = self.manager.create(
            contact_id="12345",
            company_id="67890",
            stage="Prospecting",
            amount=50000,
            closing_date="2026-03-15",
            owner="sales@company.com",
            name="Acme Deal"
        )
        
        # Verify
        self.mock_crm.create_pipeline.assert_called_once()
        call_args = self.mock_crm.create_pipeline.call_args[0][0]
        self.assertEqual(call_args["Stage"], "Prospecting")
        self.assertEqual(call_args["Amount"], 50000)
        self.assertEqual(call_args["Deal_Name"], "Acme Deal")
        self.assertEqual(result["data"][0]["code"], "SUCCESS")
    
    def test_update_pipeline(self):
        """Test updating a pipeline"""
        mock_response = {
            "data": [{
                "code": "SUCCESS",
                "message": "Pipeline updated"
            }]
        }
        self.mock_crm.update_pipeline.return_value = mock_response
        
        result = self.manager.update(
            pipeline_id="123456789",
            stage="Negotiation",
            amount=75000,
            probability=70
        )
        
        self.mock_crm.update_pipeline.assert_called_once_with(
            "123456789",
            {"Stage": "Negotiation", "Amount": 75000, "Probability": 70}
        )
        self.assertEqual(result["data"][0]["code"], "SUCCESS")
    
    def test_advance_pipeline_with_stage(self):
        """Test advancing pipeline to specific stage"""
        mock_response = {
            "data": [{
                "code": "SUCCESS",
                "message": "Stage updated"
            }]
        }
        self.mock_crm.advance_pipeline.return_value = mock_response
        
        result = self.manager.advance("123456789", "Negotiation")
        
        self.mock_crm.advance_pipeline.assert_called_once_with("123456789", "Negotiation")
        self.assertEqual(result["data"][0]["code"], "SUCCESS")
    
    def test_win_pipeline(self):
        """Test marking pipeline as won"""
        mock_response = {
            "data": [{
                "code": "SUCCESS",
                "message": "Pipeline won"
            }]
        }
        self.mock_crm.win_pipeline.return_value = mock_response
        
        result = self.manager.win("123456789")
        
        self.mock_crm.win_pipeline.assert_called_once_with("123456789")
        self.assertEqual(result["data"][0]["code"], "SUCCESS")
    
    def test_lose_pipeline(self):
        """Test marking pipeline as lost"""
        mock_response = {
            "data": [{
                "code": "SUCCESS",
                "message": "Pipeline lost"
            }]
        }
        self.mock_crm.lose_pipeline.return_value = mock_response
        
        result = self.manager.lose("123456789", "Budget constraints")
        
        self.mock_crm.lose_pipeline.assert_called_once_with("123456789", "Budget constraints")
        self.assertEqual(result["data"][0]["code"], "SUCCESS")
    
    def test_list_pipelines(self):
        """Test listing pipelines with filters"""
        mock_response = {
            "data": [
                {"data": {"id": "1", "Stage": "Prospecting", "Amount": 10000}},
                {"data": {"id": "2", "Stage": "Prospecting", "Amount": 20000}}
            ]
        }
        self.mock_crm.get_pipelines.return_value = mock_response
        
        results = self.manager.list(stage="Prospecting", owner="me", limit=50)
        
        self.mock_crm.get_pipelines.assert_called_once_with(
            stage="Prospecting", owner="me", limit=50
        )
        self.assertEqual(len(results), 2)
    
    def test_search_pipelines(self):
        """Test searching pipelines"""
        mock_response = {
            "data": [
                {"data": {"id": "1", "Deal_Name": "Acme Project"}}
            ]
        }
        self.mock_crm.search_pipelines.return_value = mock_response
        
        results = self.manager.search("Acme")
        
        self.mock_crm.search_pipelines.assert_called_once_with("Acme")
        self.assertEqual(len(results), 1)
    
    def test_bulk_update(self):
        """Test bulk updating pipelines"""
        mock_list_response = {
            "data": [
                {"data": {"id": "1", "Stage": "Negotiation"}},
                {"data": {"id": "2", "Stage": "Negotiation"}}
            ]
        }
        mock_update_response = {
            "data": [{"code": "SUCCESS", "message": "Updated"}]
        }
        
        self.mock_crm.get_pipelines.return_value = mock_list_response
        self.mock_crm.advance_pipeline.return_value = mock_update_response
        
        results = self.manager.bulk_update("Negotiation", "Closed Won")
        
        self.assertEqual(len(results), 2)
        self.assertEqual(self.mock_crm.advance_pipeline.call_count, 2)


class TestBiginCRMPipelines(unittest.TestCase):
    """Test cases for BiginCRM pipeline methods"""
    
    @patch('bigin_crm.requests')
    def setUp(self, mock_requests):
        """Set up test fixtures"""
        self.crm = BiginCRM("test_token", "com")
        self.mock_requests = mock_requests
    
    @patch('bigin_crm.requests.post')
    def test_create_pipeline_api(self, mock_post):
        """Test create_pipeline API call"""
        mock_response = Mock()
        mock_response.json.return_value = {"data": [{"id": "123"}]}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = self.crm.create_pipeline({"Stage": "Prospecting", "Amount": 1000})
        
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[0][0], "https://www.zohoapis.com/bigin/v2/Pipelines")
        self.assertEqual(result["data"][0]["id"], "123")
    
    @patch('bigin_crm.requests.get')
    def test_get_pipelines_with_filters(self, mock_get):
        """Test get_pipelines with filters"""
        mock_response = Mock()
        mock_response.json.return_value = {"data": []}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = self.crm.get_pipelines(stage="Prospecting", owner="test@company.com")
        
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn("criteria", call_args[1]["params"])


if __name__ == "__main__":
    unittest.main()
