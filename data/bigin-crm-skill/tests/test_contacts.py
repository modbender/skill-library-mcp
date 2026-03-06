"""
Contact Module Tests
Unit tests for contact operations
"""

import unittest
from unittest.mock import Mock, patch, mock_open
import json
import sys
from io import StringIO

sys.path.insert(0, '../scripts')

from scripts.bigin_crm import BiginCRM
from scripts.contacts import ContactManager


class TestContactManager(unittest.TestCase):
    """Test cases for ContactManager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_crm = Mock(spec=BiginCRM)
        self.manager = ContactManager(self.mock_crm)
    
    def test_create_contact(self):
        """Test creating a contact"""
        mock_response = {
            "data": [{
                "code": "SUCCESS",
                "details": {"id": "987654321"},
                "message": "Contact created"
            }]
        }
        self.mock_crm.create_contact.return_value = mock_response
        
        result = self.manager.create(
            first_name="John",
            last_name="Doe",
            email="john@company.com",
            phone="+1-555-1234",
            company="Acme Inc",
            source="Website"
        )
        
        self.mock_crm.create_contact.assert_called_once()
        call_args = self.mock_crm.create_contact.call_args[0][0]
        self.assertEqual(call_args["First_Name"], "John")
        self.assertEqual(call_args["Last_Name"], "Doe")
        self.assertEqual(call_args["Email"], "john@company.com")
        self.assertEqual(result["data"][0]["code"], "SUCCESS")
    
    def test_update_contact(self):
        """Test updating a contact"""
        mock_response = {
            "data": [{"code": "SUCCESS", "message": "Contact updated"}]
        }
        self.mock_crm.update_contact.return_value = mock_response
        
        result = self.manager.update("987654321", Phone="+1-555-9999")
        
        self.mock_crm.update_contact.assert_called_once_with(
            "987654321", {"Phone": "+1-555-9999"}
        )
        self.assertEqual(result["data"][0]["code"], "SUCCESS")
    
    def test_get_contact_with_pipelines(self):
        """Test getting contact with associated pipelines"""
        mock_contact = {
            "data": [{
                "id": "987654321",
                "First_Name": "John",
                "Last_Name": "Doe"
            }]
        }
        mock_pipelines = {
            "data": [{"id": "1", "Deal_Name": "Test Deal"}]
        }
        
        self.mock_crm.get_contact.return_value = mock_contact
        self.mock_crm.search_pipelines.return_value = mock_pipelines
        
        result = self.manager.get("987654321", include_pipelines=True)
        
        self.mock_crm.get_contact.assert_called_once_with("987654321")
        self.mock_crm.search_pipelines.assert_called_once()
        self.assertIn("pipelines", result)
        self.assertEqual(len(result["pipelines"]), 1)
    
    def test_search_contacts(self):
        """Test searching contacts"""
        mock_response = {
            "data": [
                {"data": {"id": "1", "First_Name": "John", "Last_Name": "Doe"}},
                {"data": {"id": "2", "First_Name": "Jane", "Last_Name": "Doe"}}
            ]
        }
        self.mock_crm.search_contacts.return_value = mock_response
        
        results = self.manager.search("Doe", limit=10)
        
        self.mock_crm.search_contacts.assert_called_once_with("Doe")
        self.assertEqual(len(results), 2)
    
    def test_list_contacts(self):
        """Test listing contacts with criteria"""
        mock_response = {
            "data": [
                {"data": {"id": "1", "First_Name": "John"}},
                {"data": {"id": "2", "First_Name": "Jane"}}
            ]
        }
        self.mock_crm.get_contacts.return_value = mock_response
        
        results = self.manager.list(criteria="(Lead_Source:equals:Website)", limit=50)
        
        self.mock_crm.get_contacts.assert_called_once_with(
            criteria="(Lead_Source:equals:Website)", limit=50
        )
        self.assertEqual(len(results), 2)
    
    def test_delete_contact(self):
        """Test deleting a contact"""
        mock_response = {"code": "SUCCESS", "message": "Contact deleted"}
        self.mock_crm.delete_contact.return_value = mock_response
        
        result = self.manager.delete("987654321")
        
        self.mock_crm.delete_contact.assert_called_once_with("987654321")
        self.assertEqual(result["code"], "SUCCESS")
    
    @patch('builtins.open', mock_open(read_data='First Name,Last Name,Email\nJohn,Doe,john@test.com\nJane,Smith,jane@test.com'))
    def test_import_from_csv(self):
        """Test importing contacts from CSV"""
        mock_response = {
            "data": [{"code": "SUCCESS", "details": {"id": "1"}}]
        }
        self.mock_crm.create_contact.return_value = mock_response
        
        results = self.manager.import_from_csv('test.csv')
        
        self.assertEqual(self.mock_crm.create_contact.call_count, 2)
        self.assertEqual(len(results), 2)
    
    def test_bulk_import(self):
        """Test bulk importing contacts"""
        mock_response = {
            "data": [{"code": "SUCCESS", "message": "Bulk import completed"}]
        }
        self.mock_crm.bulk_import_contacts.return_value = mock_response
        
        records = [
            {"First_Name": "John", "Last_Name": "Doe", "Email": "john@test.com"},
            {"First_Name": "Jane", "Last_Name": "Smith", "Email": "jane@test.com"}
        ]
        
        result = self.manager.bulk_import(records)
        
        self.mock_crm.bulk_import_contacts.assert_called_once_with(records)
        self.assertEqual(result["data"][0]["code"], "SUCCESS")


class TestBiginCRMContacts(unittest.TestCase):
    """Test cases for BiginCRM contact methods"""
    
    @patch('bigin_crm.requests')
    def setUp(self, mock_requests):
        """Set up test fixtures"""
        self.crm = BiginCRM("test_token", "com")
        self.mock_requests = mock_requests
    
    @patch('bigin_crm.requests.post')
    def test_create_contact_api(self, mock_post):
        """Test create_contact API call"""
        mock_response = Mock()
        mock_response.json.return_value = {"data": [{"id": "123"}]}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = self.crm.create_contact({
            "First_Name": "John",
            "Last_Name": "Doe",
            "Email": "john@test.com"
        })
        
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[0][0], "https://www.zohoapis.com/bigin/v2/Contacts")
    
    @patch('bigin_crm.requests.get')
    def test_search_contacts_api(self, mock_get):
        """Test search_contacts API call"""
        mock_response = Mock()
        mock_response.json.return_value = {"data": []}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = self.crm.search_contacts("test query")
        
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn("word=test+query", call_args[0][0])


if __name__ == "__main__":
    unittest.main()
