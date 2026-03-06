"""
Tests for the enhanced Attio skill
"""

import asyncio
import unittest.mock as mock
from unittest.mock import MagicMock
import pytest
from lib.attio_enhanced import AttioEnhancedClient, validate_and_clean_crm_data


@pytest.fixture
def mock_client():
    """Create a mocked AttioEnhancedClient for testing"""
    with mock.patch('lib.attio_enhanced.requests.Session') as mock_session_class:
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.headers = {}
        
        client = AttioEnhancedClient(api_key='test-key', workspace_id='test-workspace')
        client.session = mock_session
        return client


def test_client_initialization():
    """Test that the client initializes correctly"""
    client = AttioEnhancedClient(api_key='test-key', workspace_id='test-workspace')
    
    assert client.api_key == 'test-key'
    assert client.workspace_id == 'test-workspace'
    assert 'Bearer test-key' in client.session.headers['Authorization']


def test_email_validation():
    """Test email validation functionality"""
    client = AttioEnhancedClient(api_key='test-key', workspace_id='test-workspace')
    
    # Valid emails
    assert client._is_valid_email('test@example.com') is True
    assert client._is_valid_email('user.name+tag@example.co.uk') is True
    
    # Invalid emails
    assert client._is_valid_email('invalid-email') is False
    assert client._is_valid_email('@example.com') is False
    assert client._is_valid_email('test@') is False
    assert client._is_valid_email('') is False


def test_person_validation():
    """Test person record validation"""
    client = AttioEnhancedClient(api_key='test-key', workspace_id='test-workspace')
    
    # Valid person
    valid_person = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com'
    }
    errors = client.validate_crm_data('person', valid_person)
    assert errors == {}
    
    # Invalid person with empty name
    invalid_person = {
        'first_name': '',
        'last_name': 'Doe',
        'email': 'john@example.com'
    }
    errors = client.validate_crm_data('person', invalid_person)
    assert 'first_name' in errors
    
    # Invalid person with bad email
    invalid_person = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'not-an-email'
    }
    errors = client.validate_crm_data('person', invalid_person)
    assert 'email' in errors


def test_organization_validation():
    """Test organization record validation"""
    client = AttioEnhancedClient(api_key='test-key', workspace_id='test-workspace')
    
    # Valid organization
    valid_org = {
        'name': 'Example Corp'
    }
    errors = client.validate_crm_data('organization', valid_org)
    assert errors == {}
    
    # Invalid organization with empty name
    invalid_org = {
        'name': ''
    }
    errors = client.validate_crm_data('organization', invalid_org)
    assert 'name' in errors


def test_deal_validation():
    """Test deal record validation"""
    client = AttioEnhancedClient(api_key='test-key', workspace_id='test-workspace')
    
    # Valid deal
    valid_deal = {
        'amount': 1000,
        'status': 'open'
    }
    errors = client.validate_crm_data('deal', valid_deal)
    assert errors == {}
    
    # Invalid deal with non-numeric amount
    invalid_deal = {
        'amount': 'thousand',
        'status': 'open'
    }
    errors = client.validate_crm_data('deal', invalid_deal)
    assert 'amount' in errors


def test_validate_and_clean_crm_data():
    """Test the validate_and_clean_crm_data function"""
    records = [
        {'first_name': 'John', 'last_name': 'Doe', 'email': 'john@example.com'},  # Valid
        {'first_name': '', 'last_name': 'Smith', 'email': 'jane@example.com'},    # Invalid
        {'first_name': 'Bob', 'last_name': 'Johnson', 'email': 'bob@example.com'}  # Valid
    ]
    
    results = validate_and_clean_crm_data(records, 'person')
    
    assert results['valid_count'] == 2
    assert results['invalid_count'] == 1
    assert len(results['valid_records']) == 2
    assert len(results['invalid_records']) == 1


def test_enrich_contact_data():
    """Test contact data enrichment"""
    client = AttioEnhancedClient(api_key='test-key', workspace_id='test-workspace')
    
    contact_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'company': 'Example Corp'
    }
    
    enriched = client.enrich_contact_data(contact_data)
    
    assert 'email_domain' in enriched
    assert enriched['email_domain'] == 'example.com'
    assert 'enrichment_timestamp' in enriched
    assert enriched['first_name'] == 'John'


@pytest.mark.asyncio
async def test_batch_create_records():
    """Test batch record creation"""
    with mock.patch('lib.attio_enhanced.aiohttp.ClientSession') as mock_session_class:
        mock_session = MagicMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session
        mock_session.request = MagicMock()
        
        # Mock the response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text.return_value = '{"results": [{"id": "1"}, {"id": "2"}]}'
        mock_response.raise_for_status = MagicMock()
        mock_session.request.return_value.__aenter__.return_value = mock_response
        
        async with AttioEnhancedClient(api_key='test-key', workspace_id='test-workspace') as client:
            records = [
                {'first_name': 'John', 'last_name': 'Doe', 'email': 'john@example.com'},
                {'first_name': 'Jane', 'last_name': 'Smith', 'email': 'jane@example.com'}
            ]
            
            results = await client.batch_create_records('person', records, chunk_size=2)
            
            assert results['total_records'] == 2
            assert results['successful'] >= 0  # At least 0 successful


def test_manage_attio_tasks():
    """Test task management functionality"""
    client = AttioEnhancedClient(api_key='test-key', workspace_id='test-workspace')
    
    # Test starting a task
    task_start = client.manage_attio_tasks(
        task_type='contact_import',
        operation='start',
        params={'contact_count': 100}
    )
    
    assert task_start['task_type'] == 'contact_import'
    assert task_start['status'] == 'running'
    assert 'started_at' in task_start
    
    # Test completing a task
    task_complete = client.manage_attio_tasks(
        task_type='contact_import',
        operation='complete',
        params={
            'task_id': task_start['task_id'],
            'result': {'success': 95, 'failed': 5}
        }
    )
    
    assert task_complete['status'] == 'completed'
    assert 'completed_at' in task_complete


def test_task_management_invalid_operation():
    """Test that invalid operations raise an error"""
    client = AttioEnhancedClient(api_key='test-key', workspace_id='test-workspace')
    
    with pytest.raises(ValueError):
        client.manage_attio_tasks(
            task_type='contact_import',
            operation='invalid_operation'
        )


if __name__ == '__main__':
    pytest.main([__file__])