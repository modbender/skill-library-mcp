"""
Bigin CRM Python Module
Main client for interacting with Bigin CRM REST API v2
"""

import requests
import json
import sys
from datetime import datetime
from typing import Optional, Dict, List, Any

# Debug logging flag - set to True for troubleshooting
DEBUG = False

def log_debug(msg, data=None):
    """Log debug information to stderr"""
    if DEBUG:
        print(f"[DEBUG] {msg}", file=sys.stderr)
        if data:
            print(f"[DEBUG] {json.dumps(data, indent=2) if isinstance(data, (dict, list)) else data}", file=sys.stderr)


class BiginCRM:
    """
    Bigin CRM API Client
    
    Initialize with OAuth token and optional data center.
    Default data center is 'com' (United States).
    """
    
    def __init__(self, auth_token: str, dc: str = 'com'):
        """
        Initialize Bigin CRM client
        
        Args:
            auth_token: OAuth2 access token
            dc: Data center - com, eu, in, au, jp, uk, ca, etc.
        """
        self.base_url = f"https://www.zohoapis.{dc}/bigin/v2"
        self.headers = {
            "Authorization": f"Zoho-oauthtoken {auth_token}",
            "Content-Type": "application/json"
        }
    
    # ==================== PIPELINES (CORE) ====================
    
    def create_pipeline(self, data: Dict[str, Any]) -> Dict:
        """
        Create a pipeline entry (equivalent to Deal in CRM)
        
        Args:
            data: Pipeline data dictionary
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/Pipelines"
        payload = {"data": [data]}
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_pipelines(
        self,
        stage: Optional[str] = None,
        owner: Optional[str] = None,
        limit: int = 200,
        fields: Optional[str] = "All"
    ) -> Dict:
        """
        Get pipeline records with optional filters
        
        Args:
            stage: Filter by pipeline stage
            owner: Filter by owner email
            limit: Maximum records to return (default 200)
            fields: Comma-separated field names or "All" (default: All)
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/Pipelines"
        params = {"per_page": limit, "fields": fields}
        
        # Build criteria string
        criteria = []
        if stage:
            criteria.append(f"(Stage:equals:{stage})")
        if owner:
            criteria.append(f"(Owner:equals:{owner})")
        
        if criteria:
            params["criteria"] = " and ".join(criteria)
        
        log_debug(f"API Request URL: {url}")
        log_debug(f"API Request Headers: {self.headers}")
        log_debug(f"API Request Params: {params}")
        
        response = requests.get(url, headers=self.headers, params=params)
        
        log_debug(f"API Response Status: {response.status_code}")
        log_debug(f"API Response URL: {response.url}")
        try:
            log_debug(f"API Response Body: {response.text[:500]}")
        except:
            log_debug(f"API Response Body: {response.text}")
        
        response.raise_for_status()
        return response.json()
    
    def get_pipeline(self, pipeline_id: str) -> Dict:
        """
        Get a single pipeline record by ID
        
        Args:
            pipeline_id: Pipeline record ID
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/Pipelines/{pipeline_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def update_pipeline(self, pipeline_id: str, data: Dict[str, Any]) -> Dict:
        """
        Update a pipeline record (e.g., change stage)
        
        Args:
            pipeline_id: Pipeline record ID
            data: Updated pipeline data
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/Pipelines/{pipeline_id}"
        payload = {"data": [data]}
        response = requests.put(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()
    
    def delete_pipeline(self, pipeline_id: str) -> Dict:
        """
        Delete a pipeline record
        
        Args:
            pipeline_id: Pipeline record ID
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/Pipelines/{pipeline_id}"
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def advance_pipeline(self, pipeline_id: str, new_stage: Optional[str] = None) -> Dict:
        """
        Move pipeline to next stage or specified stage
        
        Args:
            pipeline_id: Pipeline record ID
            new_stage: Optional specific stage to move to
            
        Returns:
            API response as dictionary
        """
        update_data = {}
        if new_stage:
            update_data["Stage"] = new_stage
        # Could also implement logic to determine next stage automatically
        return self.update_pipeline(pipeline_id, update_data)
    
    def win_pipeline(self, pipeline_id: str) -> Dict:
        """
        Mark pipeline as won (Closed Won)
        
        Args:
            pipeline_id: Pipeline record ID
            
        Returns:
            API response as dictionary
        """
        return self.update_pipeline(pipeline_id, {"Stage": "Closed Won"})
    
    def lose_pipeline(self, pipeline_id: str, reason: Optional[str] = None) -> Dict:
        """
        Mark pipeline as lost (Closed Lost)
        
        Args:
            pipeline_id: Pipeline record ID
            reason: Optional loss reason
            
        Returns:
            API response as dictionary
        """
        data = {"Stage": "Closed Lost"}
        if reason:
            data["Loss_Reason"] = reason
        return self.update_pipeline(pipeline_id, data)
    
    def search_pipelines(self, query: str) -> Dict:
        """
        Search pipelines by keyword
        
        Args:
            query: Search query string
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/Pipelines/search"
        params = {"word": query}
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        # Handle 204 No Content (empty search results)
        if response.status_code == 204:
            return {"data": []}
        return response.json()
    
    # ==================== CONTACTS ====================
    
    def create_contact(self, data: Dict[str, Any]) -> Dict:
        """
        Create a contact
        
        Args:
            data: Contact data dictionary
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/Contacts"
        payload = {"data": [data]}
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_contacts(
        self, 
        criteria: Optional[str] = None, 
        limit: int = 200
    ) -> Dict:
        """
        Get contacts with optional criteria
        
        Args:
            criteria: Filter criteria string
            limit: Maximum records to return
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/Contacts"
        params = {"per_page": limit}
        if criteria:
            params["criteria"] = criteria
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_contact(self, contact_id: str) -> Dict:
        """
        Get a single contact by ID
        
        Args:
            contact_id: Contact record ID
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/Contacts/{contact_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def update_contact(self, contact_id: str, data: Dict[str, Any]) -> Dict:
        """
        Update a contact
        
        Args:
            contact_id: Contact record ID
            data: Updated contact data
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/Contacts/{contact_id}"
        payload = {"data": [data]}
        response = requests.put(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()
    
    def delete_contact(self, contact_id: str) -> Dict:
        """
        Delete a contact
        
        Args:
            contact_id: Contact record ID
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/Contacts/{contact_id}"
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def search_contacts(self, query: str) -> Dict:
        """
        Search contacts by keyword
        
        Args:
            query: Search query string
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/Contacts/search"
        params = {"word": query}
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        # Handle 204 No Content (empty search results)
        if response.status_code == 204:
            return {"data": []}
        return response.json()
    
    # ==================== COMPANIES (ACCOUNTS) ====================
    
    def create_company(self, data: Dict[str, Any]) -> Dict:
        """
        Create a company (uses Accounts API)
        
        Args:
            data: Company data dictionary
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/Accounts"
        payload = {"data": [data]}
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_companies(
        self, 
        criteria: Optional[str] = None, 
        limit: int = 200
    ) -> Dict:
        """
        Get companies
        
        Args:
            criteria: Filter criteria string
            limit: Maximum records to return
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/Accounts"
        params = {"per_page": limit}
        if criteria:
            params["criteria"] = criteria
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_company(self, company_id: str) -> Dict:
        """
        Get a single company by ID
        
        Args:
            company_id: Company record ID
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/Accounts/{company_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def update_company(self, company_id: str, data: Dict[str, Any]) -> Dict:
        """
        Update a company
        
        Args:
            company_id: Company record ID
            data: Updated company data
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/Accounts/{company_id}"
        payload = {"data": [data]}
        response = requests.put(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()
    
    def delete_company(self, company_id: str) -> Dict:
        """
        Delete a company
        
        Args:
            company_id: Company record ID
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/Accounts/{company_id}"
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def search_companies(self, query: str) -> Dict:
        """
        Search companies by keyword
        
        Args:
            query: Search query string
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/Accounts/search"
        params = {"word": query}
        log_debug(f"search_companies URL: {url}")
        log_debug(f"search_companies headers: {self.headers}")
        log_debug(f"search_companies params: {params}")
        response = requests.get(url, headers=self.headers, params=params)
        log_debug(f"search_companies status: {response.status_code}")
        log_debug(f"search_companies response text: {response.text[:500]}")
        response.raise_for_status()
        # Handle 204 No Content (empty search results)
        if response.status_code == 204:
            return {"data": []}
        return response.json()
    
    # ==================== TASKS ====================
    
    def create_task(
        self, 
        subject: str, 
        related_to: Optional[str] = None, 
        due_date: Optional[str] = None, 
        owner: Optional[str] = None,
        priority: Optional[str] = None
    ) -> Dict:
        """
        Create a follow-up task
        
        Args:
            subject: Task subject
            related_to: Related record in format "module:record_id"
            due_date: Due date in YYYY-MM-DD format
            owner: Owner email or name
            priority: Task priority (High, Normal, Low)
            
        Returns:
            API response as dictionary
        """
        data = {"Subject": subject}
        
        if due_date:
            data["Due_Date"] = due_date
        if owner:
            data["Owner"] = {"name": owner}
        if priority:
            data["Priority"] = priority
        if related_to:
            # related_to format: "module:record_id" e.g., "Pipelines:12345"
            module, record_id = related_to.split(":")
            data["What_Id"] = {"id": record_id}
        
        url = f"{self.base_url}/Tasks"
        payload = {"data": [data]}
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_tasks(
        self, 
        due_before: Optional[str] = None, 
        status: str = "Open", 
        limit: int = 200
    ) -> Dict:
        """
        Get tasks with filters
        
        Args:
            due_before: Filter tasks due before this date
            status: Task status (Open, Completed)
            limit: Maximum records to return
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/Tasks"
        params = {"per_page": limit}
        
        criteria = [f"(Status:equals:{status})"]
        if due_before:
            criteria.append(f"(Due_Date:less_than:{due_before})")
        
        params["criteria"] = " and ".join(criteria)
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_task(self, task_id: str) -> Dict:
        """
        Get a single task by ID
        
        Args:
            task_id: Task record ID
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/Tasks/{task_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def update_task(self, task_id: str, data: Dict[str, Any]) -> Dict:
        """
        Update a task
        
        Args:
            task_id: Task record ID
            data: Updated task data
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/Tasks/{task_id}"
        payload = {"data": [data]}
        response = requests.put(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()
    
    def complete_task(self, task_id: str) -> Dict:
        """
        Mark a task as completed
        
        Args:
            task_id: Task record ID
            
        Returns:
            API response as dictionary
        """
        return self.update_task(task_id, {"Status": "Completed"})
    
    def delete_task(self, task_id: str) -> Dict:
        """
        Delete a task
        
        Args:
            task_id: Task record ID
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/Tasks/{task_id}"
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    # ==================== EVENTS ====================
    
    def create_event(self, data: Dict[str, Any]) -> Dict:
        """
        Create an event/meeting
        
        Args:
            data: Event data dictionary
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/Events"
        payload = {"data": [data]}
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_events(
        self, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None,
        limit: int = 200
    ) -> Dict:
        """
        Get events with optional date filters
        
        Args:
            start_date: Start date filter
            end_date: End date filter
            limit: Maximum records to return
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/Events"
        params = {"per_page": limit}
        
        criteria = []
        if start_date:
            criteria.append(f"(Start_DateTime:greater_than:{start_date})")
        if end_date:
            criteria.append(f"(End_DateTime:less_than:{end_date})")
        
        if criteria:
            params["criteria"] = " and ".join(criteria)
            
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    # ==================== CALLS ====================
    
    def create_call(self, data: Dict[str, Any]) -> Dict:
        """
        Log a call
        
        Args:
            data: Call data dictionary
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/Calls"
        payload = {"data": [data]}
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_calls(
        self, 
        related_to: Optional[str] = None,
        limit: int = 200
    ) -> Dict:
        """
        Get logged calls
        
        Args:
            related_to: Filter by related record
            limit: Maximum records to return
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/Calls"
        params = {"per_page": limit}
        
        if related_to:
            params["criteria"] = f"(What_Id:equals:{related_to})"
            
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    # ==================== BULK OPERATIONS ====================
    
    def bulk_import_contacts(self, records: List[Dict[str, Any]]) -> Dict:
        """
        Bulk import contacts
        
        Args:
            records: List of contact data dictionaries
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/Contacts"
        # Bigin API supports up to 100 records per bulk request
        payload = {"data": records[:100]}
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()
    
    # ==================== REPORTING ====================
    
    def get_pipeline_report(
        self, 
        by_stage: bool = True, 
        by_owner: bool = True
    ) -> Dict[str, Any]:
        """
        Generate pipeline summary report
        
        Args:
            by_stage: Group by stage
            by_owner: Group by owner
            
        Returns:
            Aggregated report dictionary
        """
        pipelines = self.get_pipelines(limit=200)
        
        report = {
            "total_count": 0,
            "by_stage": {},
            "by_owner": {},
            "total_value": 0,
            "generated_at": datetime.now().isoformat()
        }
        
        data = pipelines.get("data", [])
        if not data:
            return report
        
        for record in data:
            info = record.get("data", {})
            report["total_count"] += 1
            
            # Aggregate by stage
            if by_stage:
                stage = info.get("Stage", "Unknown")
                if stage not in report["by_stage"]:
                    report["by_stage"][stage] = {"count": 0, "value": 0}
                report["by_stage"][stage]["count"] += 1
                amount = info.get("Amount", 0) or 0
                report["by_stage"][stage]["value"] += amount
            
            # Aggregate by owner
            if by_owner:
                owner = info.get("Owner", {}).get("name", "Unknown")
                if owner not in report["by_owner"]:
                    report["by_owner"][owner] = {"count": 0, "value": 0}
                report["by_owner"][owner]["count"] += 1
                amount = info.get("Amount", 0) or 0
                report["by_owner"][owner]["value"] += amount
            
            # Total value
            amount = info.get("Amount", 0) or 0
            report["total_value"] += amount
        
        return report
    
    def get_forecast(self, month: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate weighted pipeline forecast
        
        Args:
            month: Target month in YYYY-MM format
            
        Returns:
            Forecast dictionary with weighted values
        """
        pipelines = self.get_pipelines(limit=200)
        
        forecast = {
            "month": month or datetime.now().strftime("%Y-%m"),
            "total_pipeline_value": 0,
            "weighted_forecast": 0,
            "by_stage": {},
            "generated_at": datetime.now().isoformat()
        }
        
        # Stage probability mapping (customize based on your pipeline)
        stage_probabilities = {
            "Prospecting": 10,
            "Qualification": 25,
            "Needs Analysis": 40,
            "Value Proposition": 50,
            "Id. Decision Makers": 60,
            "Proposal/Price Quote": 70,
            "Negotiation/Review": 80,
            "Closed Won": 100,
            "Closed Lost": 0
        }
        
        data = pipelines.get("data", [])
        for record in data:
            info = record.get("data", {})
            stage = info.get("Stage", "Unknown")
            amount = info.get("Amount", 0) or 0
            probability = info.get("Probability", stage_probabilities.get(stage, 50))
            
            forecast["total_pipeline_value"] += amount
            forecast["weighted_forecast"] += amount * (probability / 100)
            
            if stage not in forecast["by_stage"]:
                forecast["by_stage"][stage] = {
                    "count": 0,
                    "value": 0,
                    "weighted_value": 0,
                    "probability": probability
                }
            
            forecast["by_stage"][stage]["count"] += 1
            forecast["by_stage"][stage]["value"] += amount
            forecast["by_stage"][stage]["weighted_value"] += amount * (probability / 100)
        
        return forecast
