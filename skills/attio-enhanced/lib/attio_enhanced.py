"""
Enhanced Attio Skill Module
Provides advanced functionality for interacting with Attio API including
batch operations, error handling, data validation, and enrichment.
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

import aiohttp
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


class AttioEnhancedClient:
    """
    Enhanced Attio client with batch operations, error handling, and data validation
    """
    
    def __init__(self, api_key: str = None, workspace_id: str = None):
        """
        Initialize the enhanced Attio client
        
        Args:
            api_key: Attio API key
            workspace_id: Attio workspace ID
        """
        self.api_key = api_key or os.getenv('ATTIO_API_KEY')
        self.workspace_id = workspace_id or os.getenv('ATTIO_WORKSPACE_ID')
        # Attio API base - objects don't use /workspaces/{id} prefix
        # Use /v2/objects/{slug}/records directly
        self.base_url = "https://api.attio.com/v2"
        self.workspace_id = workspace_id or os.getenv('ATTIO_WORKSPACE_ID')
        
        if not self.api_key:
            raise ValueError("Attio API key is required")
        if not self.workspace_id:
            raise ValueError("Attio workspace ID is required")
            
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # Async session for batch operations
        self.async_session = None
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.async_session = aiohttp.ClientSession(
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.async_session:
            await self.async_session.close()
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.exceptions.RequestException, ConnectionError))
    )
    def _make_request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """
        Make a request to the Attio API with retry logic
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request data
            
        Returns:
            Response JSON data
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, json=data)
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                self.logger.warning(f"Rate limited. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
                raise requests.exceptions.RequestException("Rate limited")
            
            # Capture error response before raising
            if response.status_code >= 400:
                error_text = response.text
                self.logger.error(f"Error response: {error_text}")
                
                # Create enhanced HTTPError with error body
                error = requests.exceptions.HTTPError(
                    f"{response.status_code} {response.reason} | {error_text}",
                    response=response
                )
                error.error_body = error_text
                raise error
            
            # Handle success
            response.raise_for_status()
            
            return response.json() if response.content else {}
        
        except requests.exceptions.HTTPError as e:
            # Re-raise if already processed above
            if hasattr(e, 'error_body'):
                raise
            
            self.logger.error(f"HTTP error occurred: {e}")
            if response.status_code >= 500:
                # Retry server errors
                raise
            else:
                # Don't retry client errors
                raise e
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error occurred: {e}")
            raise
    
    async def _make_async_request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """
        Make an async request to the Attio API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request data
            
        Returns:
            Response JSON data
        """
        if not self.async_session:
            raise RuntimeError("Async session not initialized. Use as async context manager.")
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.async_session.request(method, url, json=data) as response:
                
                # Handle rate limiting
                if response.status == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    self.logger.warning(f"Rate limited. Waiting {retry_after} seconds...")
                    await asyncio.sleep(retry_after)
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=429
                    )
                
                response_text = await response.text()
                
                # Capture error response before raising
                if response.status >= 400:
                    self.logger.error(f"Error response: {response_text}")
                    
                    # Create custom error with full details in the message
                    error = aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=f"{response.reason} | {response_text}"
                    )
                    # Store error text as attribute for easier checking
                    error.error_body = response_text
                    raise error
                
                # Handle success
                response.raise_for_status()
                
                return json.loads(response_text) if response_text else {}
        
        except aiohttp.ClientResponseError as e:
            # Re-raise if already processed above
            if hasattr(e, 'error_body'):
                raise
            
            self.logger.error(f"HTTP error occurred: {e}")
            if e.status >= 500:
                # Retry server errors
                raise
            else:
                # Don't retry client errors
                raise e
        except aiohttp.ClientError as e:
            self.logger.error(f"Request error occurred: {e}")
            raise
    
    def validate_crm_data(self, record_type: str, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Validate CRM data based on common requirements
        
        Args:
            record_type: Type of record (person, organization, deal, etc.)
            data: Record data to validate
            
        Returns:
            Dictionary with validation results (field -> list of errors)
        """
        errors = {}
        
        # Common validations
        if not isinstance(data, dict):
            errors['_general'] = ['Data must be a dictionary']
            return errors
        
        # Person validations
        if record_type.lower() == 'person':
            if 'email' in data:
                email = data['email']
                if email and not self._is_valid_email(email):
                    errors['email'] = ['Invalid email format']
            
            if 'first_name' in data and data['first_name']:
                first_name = data['first_name']
                if len(first_name.strip()) == 0:
                    errors['first_name'] = ['First name cannot be empty']
            
            if 'last_name' in data and data['last_name']:
                last_name = data['last_name']
                if len(last_name.strip()) == 0:
                    errors['last_name'] = ['Last name cannot be empty']
        
        # Organization validations
        elif record_type.lower() == 'organization':
            if 'name' in data:
                name = data['name']
                if not name or len(name.strip()) == 0:
                    errors['name'] = ['Organization name cannot be empty']
        
        # Deal validations
        elif record_type.lower() == 'deal':
            if 'amount' in data:
                amount = data['amount']
                if amount is not None and not isinstance(amount, (int, float)):
                    errors['amount'] = ['Amount must be a number']
            
            if 'status' in data:
                status = data['status']
                if status and not isinstance(status, str):
                    errors['status'] = ['Status must be a string']
        
        return errors
    
    def _is_valid_email(self, email: str) -> bool:
        """Simple email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    async def batch_create_records(self, record_type: str, records: List[Dict[str, Any]], 
                                  chunk_size: int = 50) -> Dict[str, Any]:
        """
        Create multiple records in batches with error handling
        
        Args:
            record_type: Type of record to create
            records: List of records to create
            chunk_size: Number of records per batch
            
        Returns:
            Results with success and failure counts
        """
        if not self.async_session:
            raise RuntimeError("Async session not initialized. Use as async context manager.")
        
        total_records = len(records)
        successful = 0
        failed = []
        failed_details = []
        
        # Split records into chunks
        for i in range(0, len(records), chunk_size):
            chunk = records[i:i + chunk_size]
            
            # Validate each record in the chunk
            validated_chunk = []
            for idx, record in enumerate(chunk):
                validation_errors = self.validate_crm_data(record_type, record)
                if validation_errors:
                    failed.append(i + idx)
                    failed_details.append({
                        'index': i + idx,
                        'record': record,
                        'errors': validation_errors
                    })
                else:
                    validated_chunk.append(record)
            
            if validated_chunk:
                try:
                    # Attempt to create the validated records
                    result = await self._create_batch_chunk(record_type, validated_chunk)
                    
                    # Count successful creations
                    if 'results' in result:
                        successful += len(result['results'])
                    else:
                        # If no specific results count, assume all succeeded
                        successful += len(validated_chunk)
                        
                except Exception as e:
                    # If the entire batch fails, mark all as failed
                    for j, record in enumerate(validated_chunk):
                        failed.append(i + j)
                        failed_details.append({
                            'index': i + j,
                            'record': record,
                            'error': str(e)
                        })
        
        return {
            'total_records': total_records,
            'successful': successful,
            'failed': len(failed),
            'failed_indices': failed,
            'failed_details': failed_details
        }
    
    async def _create_batch_chunk(self, record_type: str, chunk: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a single chunk of records
        
        Args:
            record_type: Type of record (e.g., 'deals', 'people', 'companies')
            chunk: List of records to create
            
        Returns:
            API response
        """
        # Attio API uses plural for objects: deals not deal, people not person
        # Endpoint: /v2/objects/{plural-slug}/records
        # Payload: { "data": { "values": { ... } }
        
        # Handle singular→plural mapping
        plural_map = {
            'deal': 'deals',
            'person': 'people', 
            'company': 'companies',
            'organization': 'companies'
        }
        # Transform field names for people
        if record_type.lower() == 'person':
            # Attio people use 'name' not first_name/last_name
            for record in chunk:
                if 'first_name' in record or 'last_name' in record:
                    first = record.pop('first_name', '')
                    last = record.pop('last_name', '')
                    full = f"{first} {last}".strip()
                    if full:
                        record['name'] = [full]
        
        plural_type = plural_map.get(record_type.lower(), record_type.lower())
        
        # Build payload in Attio format
        entries = []
        for record in chunk:
            values = {}
            for key, value in record.items():
                if isinstance(value, list):
                    values[key] = value
                elif isinstance(value, dict):
                    values[key] = value
                else:
                    values[key] = [{"value": value}]
            entry = {"values": values}
            entries.append(entry)
        
        # Attio format
        if len(chunk) == 1:
            record = chunk[0]
            values = {}
            for key, value in record.items():
                if isinstance(value, list):
                    values[key] = value
                elif isinstance(value, dict):
                    values[key] = value
                else:
                    values[key] = [{"value": value}]
            payload = {"data": {"values": values}}
        else:
            entries = []
            for record in chunk:
                values = {}
                for key, value in record.items():
                    if isinstance(value, list):
                        values[key] = value
                    elif isinstance(value, dict):
                        values[key] = value
                    else:
                        values[key] = [{"value": value}]
                entries.append({"values": values})
            payload = {"data": entries}
        
        endpoint = f"/objects/{plural_type}/records"
        return await self._make_async_request('POST', endpoint, payload)
    
    def enrich_contact_data(self, contact_data: Dict[str, Any], 
                           enrichment_sources: List[str] = None) -> Dict[str, Any]:
        """
        Enrich contact data from external sources
        
        Args:
            contact_data: Original contact data
            enrichment_sources: List of sources to use for enrichment
            
        Returns:
            Enriched contact data
        """
        if enrichment_sources is None:
            enrichment_sources = ['linkedin', 'twitter', 'company_data']
        
        enriched_data = contact_data.copy()
        
        # Example enrichment logic (would connect to actual APIs in real implementation)
        if 'email' in contact_data and contact_data['email']:
            email = contact_data['email']
            # Placeholder for actual email-based enrichment
            enriched_data['email_domain'] = email.split('@')[-1]
        
        if 'company' in contact_data and contact_data['company']:
            company = contact_data['company']
            # Placeholder for actual company enrichment
            enriched_data['company_size'] = 'unknown'  # Would come from company DB
            enriched_data['industry'] = 'unknown'     # Would come from industry DB
        
        if 'linkedin_url' in contact_data:
            # Placeholder for LinkedIn data enrichment
            enriched_data['linkedin_verified'] = True
        
        # Add timestamp of enrichment
        enriched_data['enrichment_timestamp'] = datetime.now().isoformat()
        
        return enriched_data
    
    def manage_attio_tasks(self, task_type: str, operation: str, 
                          params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Manage Attio-related tasks with enhanced tracking
        
        Args:
            task_type: Type of task (import, export, sync, etc.)
            operation: Operation to perform (start, complete, fail, track)
            params: Additional parameters for the task
            
        Returns:
            Task management result
        """
        if not params:
            params = {}
        
        task_id = params.get('task_id', f"{task_type}_{int(time.time())}")
        status = 'created'
        
        # Log task creation
        self.logger.info(f"Managing task: {task_id}, type: {task_type}, op: {operation}")
        
        # Process based on operation
        if operation == 'start':
            status = 'running'
            # Store task metadata
            task_metadata = {
                'task_id': task_id,
                'task_type': task_type,
                'status': status,
                'started_at': datetime.now().isoformat(),
                'params': params
            }
            # In a real implementation, store this in a database
            return task_metadata
        
        elif operation == 'complete':
            status = 'completed'
            completion_data = {
                'task_id': task_id,
                'task_type': task_type,
                'status': status,
                'completed_at': datetime.now().isoformat(),
                'params': params,
                'result': params.get('result', {})
            }
            return completion_data
        
        elif operation == 'fail':
            status = 'failed'
            failure_data = {
                'task_id': task_id,
                'task_type': task_type,
                'status': status,
                'failed_at': datetime.now().isoformat(),
                'params': params,
                'error': params.get('error', 'Unknown error')
            }
            return failure_data
        
        elif operation == 'track':
            # Return current status of task
            return {
                'task_id': task_id,
                'task_type': task_type,
                'status': status,
                'updated_at': datetime.now().isoformat()
            }
        
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    def handle_rate_limits(self, func, *args, **kwargs):
        """
        Wrapper to handle rate limits for any function
        
        Args:
            func: Function to wrap
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Function result
        """
        max_retries = kwargs.pop('max_retries', 5)
        base_delay = kwargs.pop('base_delay', 1)
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Rate limited
                    if attempt < max_retries - 1:  # Not the last attempt
                        delay = base_delay * (2 ** attempt)  # Exponential backoff
                        self.logger.warning(f"Rate limited. Waiting {delay}s before retry {attempt + 1}/{max_retries}")
                        time.sleep(delay)
                        continue
                    else:
                        raise
                else:
                    raise
            except Exception as e:
                raise


# Convenience functions for common operations

async def batch_import_contacts(contacts: List[Dict[str, Any]], 
                               api_key: str = None, 
                               workspace_id: str = None) -> Dict[str, Any]:
    """
    Convenience function to batch import contacts with all enhancements
    
    Args:
        contacts: List of contact dictionaries
        api_key: Attio API key
        workspace_id: Attio workspace ID
        
    Returns:
        Import results
    """
    async with AttioEnhancedClient(api_key, workspace_id) as client:
        # Enrich contacts if needed
        enriched_contacts = [
            client.enrich_contact_data(contact) for contact in contacts
        ]
        
        # Perform batch import
        results = await client.batch_create_records('person', enriched_contacts)
        
        # Track the import task
        task_result = client.manage_attio_tasks(
            task_type='contact_import',
            operation='complete',
            params={
                'result': results,
                'contact_count': len(contacts)
            }
        )
        
        return {
            'import_results': results,
            'task_tracking': task_result
        }


def validate_and_clean_crm_data(records: List[Dict[str, Any]], 
                               record_type: str) -> Dict[str, Any]:
    """
    Validate and clean CRM data before import
    
    Args:
        records: List of records to validate
        record_type: Type of record (person, organization, etc.)
        
    Returns:
        Validation results with cleaned data
    """
    client = AttioEnhancedClient()
    
    valid_records = []
    invalid_records = []
    
    for i, record in enumerate(records):
        errors = client.validate_crm_data(record_type, record)
        if errors:
            invalid_records.append({
                'index': i,
                'record': record,
                'errors': errors
            })
        else:
            valid_records.append(record)
    
    return {
        'valid_records': valid_records,
        'invalid_records': invalid_records,
        'valid_count': len(valid_records),
        'invalid_count': len(invalid_records)
    }