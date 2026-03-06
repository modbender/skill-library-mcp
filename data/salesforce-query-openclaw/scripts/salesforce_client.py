#!/usr/bin/env python3
"""
Salesforce Client for GTM Workflows

This module provides authenticated access to Salesforce data including:
- Account lookups with 6Sense intent data
- Campaign member queries (State of Subscription Apps downloads)
- Opportunity pipeline checks
- Contact/Lead retrieval

Usage:
    from salesforce_client import SalesforceClient
    
    sf = SalesforceClient()
    accounts = sf.get_high_intent_accounts(min_score=80, limit=20)

Credentials:
    Credentials are loaded from environment variables. If not set, the client
    will raise a MissingCredentialsError with instructions for the user.
    
    Required environment variables:
    - SALESFORCE_CLIENT_ID
    - SALESFORCE_CLIENT_SECRET
    - SALESFORCE_INSTANCE_URL
    
    Credentials are persisted to macOS Keychain using save_credentials().
    They are loaded automatically if environment variables are not set.
"""

import requests
import os
import re
import subprocess
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

REQUEST_TIMEOUT = 20


class MissingCredentialsError(Exception):
    """Raised when Salesforce credentials are not configured."""
    
    def __init__(self, missing_vars: List[str]):
        self.missing_vars = missing_vars
        message = self._build_message()
        super().__init__(message)
    
    def _build_message(self) -> str:
        return f"""
Salesforce credentials are not configured.

Missing: {', '.join(self.missing_vars)}

To use this skill, please provide the following credentials:
1. SALESFORCE_CLIENT_ID - The Consumer Key from your Salesforce Connected App
2. SALESFORCE_CLIENT_SECRET - The Consumer Secret from your Salesforce Connected App  
3. SALESFORCE_INSTANCE_URL - Your Salesforce instance URL (e.g., https://your-domain.my.salesforce.com)

Credentials are saved in macOS Keychain.
"""


# =============================================================================
# Credential Management Functions
# =============================================================================

# Preferred secure storage (macOS Keychain)
KEYCHAIN_SERVICE = "openclaw.salesforce"


def _keychain_set(account: str, value: str) -> None:
    subprocess.run(
        [
            "security",
            "add-generic-password",
            "-U",
            "-a",
            account,
            "-s",
            KEYCHAIN_SERVICE,
            "-w",
            value,
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def _keychain_get(account: str) -> Optional[str]:
    result = subprocess.run(
        ["security", "find-generic-password", "-a", account, "-s", KEYCHAIN_SERVICE, "-w"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def save_credentials(client_id: str, client_secret: str, instance_url: str) -> str:
    """Save Salesforce credentials to macOS Keychain."""
    _keychain_set("SALESFORCE_CLIENT_ID", client_id)
    _keychain_set("SALESFORCE_CLIENT_SECRET", client_secret)
    _keychain_set("SALESFORCE_INSTANCE_URL", instance_url)

    os.environ['SALESFORCE_CLIENT_ID'] = client_id
    os.environ['SALESFORCE_CLIENT_SECRET'] = client_secret
    os.environ['SALESFORCE_INSTANCE_URL'] = instance_url

    return f"macos-keychain://{KEYCHAIN_SERVICE}"


def get_credentials() -> Dict[str, Optional[str]]:
    """
    Get Salesforce credentials.

    Priority:
    1. Environment variables
    2. macOS Keychain
    """
    client_id = os.getenv('SALESFORCE_CLIENT_ID') or _keychain_get('SALESFORCE_CLIENT_ID')
    client_secret = os.getenv('SALESFORCE_CLIENT_SECRET') or _keychain_get('SALESFORCE_CLIENT_SECRET')
    instance_url = os.getenv('SALESFORCE_INSTANCE_URL') or _keychain_get('SALESFORCE_INSTANCE_URL')

    if client_id:
        os.environ['SALESFORCE_CLIENT_ID'] = client_id
    if client_secret:
        os.environ['SALESFORCE_CLIENT_SECRET'] = client_secret
    if instance_url:
        os.environ['SALESFORCE_INSTANCE_URL'] = instance_url

    return {
        'client_id': client_id,
        'client_secret': client_secret,
        'instance_url': instance_url
    }


def _is_valid_instance_url(instance_url: Optional[str]) -> bool:
    """Allow only HTTPS Salesforce domains."""
    if not instance_url:
        return False
    value = instance_url.strip().rstrip("/")
    # my.salesforce.com, lightning.force.com, and sandbox variants.
    pattern = r"^https://[a-zA-Z0-9.-]+\.(my\.salesforce\.com|lightning\.force\.com|sandbox\.my\.salesforce\.com)$"
    return bool(re.match(pattern, value))


def _soql_escape(value: str) -> str:
    """Escape user-provided text for safe embedding in SOQL string literals."""
    return value.replace("\\", "\\\\").replace("'", "\\'")


def _clamp_int(value: int, min_value: int, max_value: int) -> int:
    return max(min_value, min(max_value, int(value)))


def check_credentials() -> tuple[bool, List[str]]:
    """
    Check if all required credentials are configured.

    Returns:
        Tuple of (all_configured: bool, missing_vars: List[str])
    """
    creds = get_credentials()
    missing = []

    if not creds['client_id']:
        missing.append('SALESFORCE_CLIENT_ID')
    if not creds['client_secret']:
        missing.append('SALESFORCE_CLIENT_SECRET')
    if not creds['instance_url'] or not _is_valid_instance_url(creds['instance_url']):
        missing.append('SALESFORCE_INSTANCE_URL')

    return (len(missing) == 0, missing)


class SalesforceClient:
    """Client for querying Salesforce instance."""
    
    API_VERSION = "v59.0"
    
    def __init__(self):
        """
        Initialize the Salesforce client with credentials.
        
        Credentials are loaded from environment variables or macOS Keychain.
        If credentials are not configured, raises
        MissingCredentialsError with instructions for the user.
        """
        # Check and load credentials
        is_configured, missing = check_credentials()
        
        if not is_configured:
            raise MissingCredentialsError(missing)
        
        creds = get_credentials()
        self.client_id = creds['client_id']
        self.client_secret = creds['client_secret']
        self.instance_url = creds['instance_url']
        self._access_token = None
        self._token_expiry = None
    
    def _get_access_token(self) -> str:
        """Get or refresh the OAuth access token."""
        # Check if we have a valid cached token
        if self._access_token and self._token_expiry and datetime.now() < self._token_expiry:
            return self._access_token
        
        # Request new token
        token_url = f"{self.instance_url}/services/oauth2/token"
        response = requests.post(token_url, data={
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }, timeout=REQUEST_TIMEOUT)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get access token (HTTP {response.status_code})")
        
        data = response.json()
        self._access_token = data["access_token"]
        # Tokens typically last 2 hours, refresh after 1.5 hours
        self._token_expiry = datetime.now() + timedelta(hours=1, minutes=30)
        
        return self._access_token
    
    def query(self, soql: str) -> List[Dict[str, Any]]:
        """Execute a SOQL query and return the records."""
        token = self._get_access_token()
        url = f"{self.instance_url}/services/data/{self.API_VERSION}/query"
        
        response = requests.get(url, 
            headers={"Authorization": f"Bearer {token}"},
            params={"q": soql},
            timeout=REQUEST_TIMEOUT,
        )
        
        if response.status_code != 200:
            raise Exception(f"Query failed (HTTP {response.status_code})")
        
        data = response.json()
        records = data.get("records", [])
        
        # Handle pagination for large result sets
        while data.get("nextRecordsUrl"):
            response = requests.get(
                f"{self.instance_url}{data['nextRecordsUrl']}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=REQUEST_TIMEOUT,
            )
            data = response.json()
            records.extend(data.get("records", []))
        
        return records
    
    def describe_object(self, object_name: str) -> Dict[str, Any]:
        """Get schema information for a Salesforce object."""
        token = self._get_access_token()
        url = f"{self.instance_url}/services/data/{self.API_VERSION}/sobjects/{object_name}/describe"
        
        response = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=REQUEST_TIMEOUT)
        
        if response.status_code != 200:
            raise Exception(f"Describe failed (HTTP {response.status_code})")
        
        return response.json()
    
    # =========================================================================
    # Account Queries
    # =========================================================================
    
    def get_account_by_name(self, name: str, fuzzy: bool = True) -> List[Dict[str, Any]]:
        """Find accounts by company name."""
        safe_name = _soql_escape(name)
        if fuzzy:
            where = f"Name LIKE '%{safe_name}%'"
        else:
            where = f"Name = '{safe_name}'"
        
        return self.query(f"""
            SELECT Id, Name, Website, Domain__c, Industry, 
                   accountIntentScore6sense__c, accountBuyingStage6sense__c,
                   accountProfileFit6sense__c, account6QA6sense__c,
                   Churned__c, OwnerId, Owner.Name
            FROM Account
            WHERE {where}
            LIMIT 20
        """)
    
    def get_account_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Find accounts by website domain."""
        # Clean the domain
        domain = _soql_escape(domain.lower().replace("https://", "").replace("http://", "").replace("www.", "").rstrip("/"))
        
        return self.query(f"""
            SELECT Id, Name, Website, Domain__c, Industry,
                   accountIntentScore6sense__c, accountBuyingStage6sense__c,
                   accountProfileFit6sense__c, account6QA6sense__c,
                   Churned__c, OwnerId, Owner.Name
            FROM Account
            WHERE Domain__c LIKE '%{domain}%' OR Website LIKE '%{domain}%'
            LIMIT 10
        """)
    
    def get_high_intent_accounts(self, min_score: int = 70, limit: int = 50, 
                                  exclude_churned: bool = True,
                                  buying_stages: List[str] = None) -> List[Dict[str, Any]]:
        """Get accounts with high 6Sense intent scores."""
        where_clauses = [f"accountIntentScore6sense__c >= {_clamp_int(min_score, 0, 100)}"]
        
        if exclude_churned:
            where_clauses.append("(Churned__c = false OR Churned__c = null)")
        
        if buying_stages:
            stages_str = "', '".join(_soql_escape(stage) for stage in buying_stages)
            where_clauses.append(f"accountBuyingStage6sense__c IN ('{stages_str}')")
        
        where = " AND ".join(where_clauses)
        
        return self.query(f"""
            SELECT Id, Name, Website, Domain__c, Industry,
                   accountIntentScore6sense__c, accountBuyingStage6sense__c,
                   accountProfileFit6sense__c, accountProfileScore6sense__c,
                   account6QA6sense__c, X6Sense_Segments__c,
                   Churned__c, OwnerId, Owner.Name
            FROM Account
            WHERE {where}
            ORDER BY accountIntentScore6sense__c DESC
            LIMIT {_clamp_int(limit, 1, 500)}
        """)
    
    def get_6qa_accounts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get accounts flagged as 6Sense Qualified Accounts (6QA)."""
        return self.query(f"""
            SELECT Id, Name, Website, Domain__c, Industry,
                   accountIntentScore6sense__c, accountBuyingStage6sense__c,
                   accountProfileFit6sense__c, account6QA6sense__c,
                   account6QAStartDate6sense__c, account6QAAgeInDays6sense__c,
                   Churned__c, OwnerId, Owner.Name
            FROM Account
            WHERE account6QA6sense__c = true AND (Churned__c = false OR Churned__c = null)
            ORDER BY accountIntentScore6sense__c DESC
            LIMIT {_clamp_int(limit, 1, 500)}
        """)
    
    # =========================================================================
    # Campaign & Engagement Queries
    # =========================================================================
    
    def get_sosa_campaigns(self) -> List[Dict[str, Any]]:
        """Get State of Subscription Apps report campaigns."""
        return self.query("""
            SELECT Id, Name, Type, Status, StartDate, NumberOfContacts, NumberOfLeads
            FROM Campaign
            WHERE Name LIKE '%State of%' OR Name LIKE '%SOSA%'
            ORDER BY StartDate DESC
        """)
    
    def get_campaign_members_by_account(self, account_id: str, 
                                         campaign_name_filter: str = None) -> List[Dict[str, Any]]:
        """Get campaign members (contacts/leads) associated with an account."""
        safe_account_id = _soql_escape(account_id)
        where = f"Contact.AccountId = '{safe_account_id}'"
        if campaign_name_filter:
            where += f" AND Campaign.Name LIKE '%{_soql_escape(campaign_name_filter)}%'"
        
        return self.query(f"""
            SELECT Id, ContactId, Contact.Name, Contact.Email, Contact.Title,
                   CampaignId, Campaign.Name, Status, CreatedDate
            FROM CampaignMember
            WHERE {where}
            ORDER BY CreatedDate DESC
            LIMIT 50
        """)
    
    def get_accounts_with_sosa_engagement(self, campaign_name: str = "State of Apps") -> List[Dict[str, Any]]:
        """Get accounts that have contacts who downloaded SOSA reports."""
        return self.query(f"""
            SELECT Contact.Account.Id, Contact.Account.Name, Contact.Account.Website,
                   Contact.Account.Domain__c, Contact.Account.accountIntentScore6sense__c,
                   Contact.Account.accountBuyingStage6sense__c, Contact.Account.Churned__c,
                   COUNT(Id) memberCount
            FROM CampaignMember
            WHERE Campaign.Name LIKE '%{_soql_escape(campaign_name)}%' AND Contact.AccountId != null
            GROUP BY Contact.Account.Id, Contact.Account.Name, Contact.Account.Website,
                     Contact.Account.Domain__c, Contact.Account.accountIntentScore6sense__c,
                     Contact.Account.accountBuyingStage6sense__c, Contact.Account.Churned__c
            ORDER BY COUNT(Id) DESC
            LIMIT 200
        """)
    
    # =========================================================================
    # Opportunity & Pipeline Queries
    # =========================================================================
    
    def get_open_opportunities(self, account_id: str = None) -> List[Dict[str, Any]]:
        """Get open opportunities, optionally filtered by account."""
        where = "IsClosed = false"
        if account_id:
            where += f" AND AccountId = '{_soql_escape(account_id)}'"
        
        return self.query(f"""
            SELECT Id, Name, StageName, Amount, CloseDate, 
                   AccountId, Account.Name, OwnerId, Owner.Name
            FROM Opportunity
            WHERE {where}
            ORDER BY CloseDate ASC
            LIMIT 100
        """)
    
    def get_accounts_with_open_opps(self) -> List[str]:
        """Get list of Account IDs that have open opportunities."""
        results = self.query("""
            SELECT AccountId
            FROM Opportunity
            WHERE IsClosed = false AND AccountId != null
        """)
        return list(set(r["AccountId"] for r in results))
    
    def has_open_opportunity(self, account_id: str) -> bool:
        """Check if an account has any open opportunities."""
        results = self.query(f"""
            SELECT Id FROM Opportunity
            WHERE AccountId = '{_soql_escape(account_id)}' AND IsClosed = false
            LIMIT 1
        """)
        return len(results) > 0
    
    # =========================================================================
    # Contact & Lead Queries
    # =========================================================================
    
    def get_contacts_at_account(self, account_id: str) -> List[Dict[str, Any]]:
        """Get contacts at a specific account."""
        return self.query(f"""
            SELECT Id, Name, Email, Title, Phone, Department
            FROM Contact
            WHERE AccountId = '{_soql_escape(account_id)}'
            ORDER BY CreatedDate DESC
            LIMIT 50
        """)
    
    def get_decision_makers_at_account(self, account_id: str) -> List[Dict[str, Any]]:
        """Get contacts with decision-maker titles at an account."""
        return self.query(f"""
            SELECT Id, Name, Email, Title, Phone
            FROM Contact
            WHERE AccountId = '{_soql_escape(account_id)}'
              AND (Title LIKE '%CEO%' OR Title LIKE '%CTO%' OR Title LIKE '%VP%'
                   OR Title LIKE '%Head%' OR Title LIKE '%Director%' 
                   OR Title LIKE '%Founder%' OR Title LIKE '%Owner%'
                   OR Title LIKE '%Chief%' OR Title LIKE '%President%')
            ORDER BY CreatedDate DESC
            LIMIT 20
        """)
    
    # =========================================================================
    # Activity & History Queries
    # =========================================================================
    
    def get_recent_activities(self, account_id: str, days: int = 90) -> List[Dict[str, Any]]:
        """Get recent activities/tasks for an account."""
        return self.query(f"""
            SELECT Id, Subject, Status, ActivityDate, Description,
                   OwnerId, Owner.Name, WhoId, Who.Name
            FROM Task
            WHERE WhatId = '{_soql_escape(account_id)}' AND ActivityDate >= LAST_N_DAYS:{_clamp_int(days, 1, 3650)}
            ORDER BY ActivityDate DESC
            LIMIT 30
        """)
    
    def was_contacted_recently(self, account_id: str, days: int = 30) -> bool:
        """Check if an account was contacted in the last N days."""
        results = self.query(f"""
            SELECT Id FROM Task
            WHERE WhatId = '{_soql_escape(account_id)}' AND ActivityDate >= LAST_N_DAYS:{_clamp_int(days, 1, 3650)}
            LIMIT 1
        """)
        return len(results) > 0
    
    # =========================================================================
    # User/Owner Queries
    # =========================================================================
    
    def get_sales_users(self) -> List[Dict[str, Any]]:
        """Get active sales users."""
        return self.query("""
            SELECT Id, Name, Email, Username, IsActive
            FROM User
            WHERE IsActive = true AND UserType = 'Standard'
            ORDER BY Name
        """)


# Convenience function for quick queries
def quick_query(soql: str) -> List[Dict[str, Any]]:
    """Execute a quick SOQL query without instantiating a client."""
    return SalesforceClient().query(soql)


if __name__ == "__main__":
    # Test the client
    print("Testing Salesforce Client...")
    print("="*60)
    
    # Check credentials first
    is_configured, missing = check_credentials()
    if not is_configured:
        print(f"\n⚠️  Credentials not configured. Missing: {', '.join(missing)}")
        print("\nTo configure, use save_credentials() or set environment variables.")
        exit(1)
    
    sf = SalesforceClient()
    
    # Test high intent accounts
    print("\nHigh Intent Accounts (score >= 90):")
    accounts = sf.get_high_intent_accounts(min_score=90, limit=5)
    for acc in accounts:
        print(f"  - {acc['Name']}: Intent={acc.get('accountIntentScore6sense__c')}, "
              f"Stage={acc.get('accountBuyingStage6sense__c')}")
    
    # Test SOSA campaigns
    print("\nState of Subscription Apps Campaigns:")
    campaigns = sf.get_sosa_campaigns()
    for c in campaigns[:5]:
        print(f"  - {c['Name']}: {c.get('NumberOfContacts', 0)} contacts, "
              f"{c.get('NumberOfLeads', 0)} leads")
    
    print("\n✅ Salesforce client working!")
