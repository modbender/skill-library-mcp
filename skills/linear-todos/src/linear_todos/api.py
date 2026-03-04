"""Linear API client for GraphQL operations."""

import json
from typing import Any, Optional, Dict, List

import requests


class LinearError(Exception):
    """Base exception for Linear API errors."""
    pass


class LinearAPIError(LinearError):
    """Exception raised when the Linear API returns an error."""
    
    def __init__(self, message: str, errors: Optional[List[Dict]] = None):
        super().__init__(message)
        self.errors = errors or []


class LinearAPI:
    """Client for the Linear GraphQL API."""
    
    API_URL = "https://api.linear.app/graphql"
    
    def __init__(self, api_key: Optional[str] = None, config=None):
        """Initialize the Linear API client.
        
        Args:
            api_key: Linear API key. If not provided, will use config.
            config: Config instance. If not provided, a new one will be created.
            
        Raises:
            LinearError: If no API key is available
        """
        if config is None:
            from linear_todos.config import Config
            config = Config()
        
        self.api_key = api_key or config.api_key
        self.config = config
        
        if not self.api_key:
            raise LinearError("No Linear API key found. Run 'linear-todo-setup' or set LINEAR_API_KEY.")
    
    def _make_request(self, query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a GraphQL request to the Linear API.
        
        Args:
            query: GraphQL query string
            variables: Optional variables for the query
            
        Returns:
            JSON response as dictionary
            
        Raises:
            LinearAPIError: If the API returns errors
            requests.RequestException: If the HTTP request fails
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": self.api_key,
        }
        
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        response = requests.post(
            self.API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        
        if "errors" in data:
            raise LinearAPIError(
                f"GraphQL error: {data['errors'][0].get('message', 'Unknown error')}",
                errors=data["errors"]
            )
        
        return data
    
    def get_viewer(self) -> Dict[str, Any]:
        """Get the current user's information.
        
        Returns:
            User info dictionary with id, name, email
        """
        query = """
        {
            viewer {
                id
                name
                email
            }
        }
        """
        response = self._make_request(query)
        return response["data"]["viewer"]
    
    def get_teams(self) -> List[Dict[str, Any]]:
        """Get all teams in the workspace.
        
        Returns:
            List of team dictionaries with id, name, key
        """
        query = """
        {
            teams {
                nodes {
                    id
                    name
                    key
                }
            }
        }
        """
        response = self._make_request(query)
        return response["data"]["teams"]["nodes"]
    
    def get_team_states(self, team_id: str) -> List[Dict[str, Any]]:
        """Get workflow states for a team.
        
        Args:
            team_id: The team ID
            
        Returns:
            List of state dictionaries with id, name, type
        """
        query = """
        query GetTeamStates($teamId: String!) {
            team(id: $teamId) {
                states {
                    nodes {
                        id
                        name
                        type
                    }
                }
            }
        }
        """
        response = self._make_request(query, {"teamId": team_id})
        return response["data"]["team"]["states"]["nodes"]
    
    def get_team_issues(self, team_id: str, include_completed: bool = False,
                        first: int = 100) -> List[Dict[str, Any]]:
        """Get issues for a team.
        
        Args:
            team_id: The team ID
            include_completed: If True, include completed and canceled issues
            first: Maximum number of issues to fetch
            
        Returns:
            List of issue dictionaries
        """
        query = """
        query GetTeamIssues($teamId: String!, $first: Int) {
            team(id: $teamId) {
                issues(first: $first) {
                    nodes {
                        id
                        identifier
                        title
                        description
                        priority
                        dueDate
                        archivedAt
                        state {
                            id
                            name
                            type
                        }
                        assignee {
                            id
                            name
                        }
                    }
                }
            }
        }
        """
        variables = {"teamId": team_id, "first": first}
        response = self._make_request(query, variables)
        issues = response["data"]["team"]["issues"]["nodes"]
        
        # Filter client-side to avoid GraphQL injection
        if not include_completed:
            issues = [
                issue for issue in issues
                if issue.get("state", {}).get("type") not in ("completed", "canceled")
            ]
        
        return issues
    
    def get_issue(self, issue_id: str) -> Dict[str, Any]:
        """Get a single issue by ID.
        
        Args:
            issue_id: Issue identifier (e.g., "TODO-123")
            
        Returns:
            Issue dictionary
        """
        query = """
        query GetIssue($issueId: String!) {
            issue(id: $issueId) {
                id
                identifier
                title
                description
                state {
                    id
                    name
                    type
                }
                assignee {
                    id
                    name
                }
                team {
                    id
                    name
                }
                priority
                dueDate
                url
                labels {
                    nodes {
                        name
                    }
                }
            }
        }
        """
        response = self._make_request(query, {"issueId": issue_id})
        return response["data"]["issue"]
    
    def create_issue(self, team_id: str, title: str, 
                     description: Optional[str] = None,
                     state_id: Optional[str] = None,
                     priority: Optional[int] = None,
                     due_date: Optional[str] = None,
                     assignee_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new issue.
        
        Args:
            team_id: Team ID (required)
            title: Issue title (required)
            description: Issue description
            state_id: Initial state ID
            priority: Priority (0=none, 1=urgent, 2=high, 3=normal, 4=low)
            due_date: Due date in ISO format
            assignee_id: Assignee user ID
            
        Returns:
            Created issue dictionary with success flag
        """
        query = """
        mutation CreateIssue($input: IssueCreateInput!) {
            issueCreate(input: $input) {
                success
                issue {
                    id
                    identifier
                    title
                    url
                    dueDate
                    state {
                        name
                    }
                }
            }
        }
        """
        
        # Build input variables safely
        variables = {
            "input": {
                "teamId": team_id,
                "title": title
            }
        }
        
        if description:
            variables["input"]["description"] = description
        if state_id:
            variables["input"]["stateId"] = state_id
        if priority is not None:
            variables["input"]["priority"] = priority
        if due_date:
            variables["input"]["dueDate"] = due_date
        if assignee_id:
            variables["input"]["assigneeId"] = assignee_id
        
        response = self._make_request(query, variables)
        return response["data"]["issueCreate"]
    
    def update_issue(self, issue_id: str,
                     title: Optional[str] = None,
                     description: Optional[str] = None,
                     state_id: Optional[str] = None,
                     priority: Optional[int] = None,
                     due_date: Optional[str] = None,
                     assignee_id: Optional[str] = None) -> Dict[str, Any]:
        """Update an existing issue.
        
        Args:
            issue_id: Issue identifier (e.g., "TODO-123")
            title: New title
            description: New description
            state_id: New state ID
            priority: New priority
            due_date: New due date
            assignee_id: New assignee
            
        Returns:
            Updated issue dictionary with success flag
        """
        query = """
        mutation UpdateIssue($id: String!, $input: IssueUpdateInput!) {
            issueUpdate(id: $id, input: $input) {
                success
                issue {
                    id
                    identifier
                    title
                    dueDate
                    state {
                        id
                        name
                    }
                }
            }
        }
        """
        
        # Build input variables safely
        variables = {"input": {}}
        
        if title is not None:
            variables["input"]["title"] = title
        if description is not None:
            variables["input"]["description"] = description
        if state_id is not None:
            variables["input"]["stateId"] = state_id
        if priority is not None:
            variables["input"]["priority"] = priority
        if due_date is not None:
            variables["input"]["dueDate"] = due_date
        if assignee_id is not None:
            variables["input"]["assigneeId"] = assignee_id
        
        if not variables["input"]:
            raise LinearError("No update fields provided")
        
        variables["id"] = issue_id
        
        response = self._make_request(query, variables)
        return response["data"]["issueUpdate"]
    
    @staticmethod
    def priority_to_label(priority: int) -> str:
        """Convert priority number to human-readable label.
        
        Args:
            priority: Priority number (0-4)
            
        Returns:
            Human-readable priority label
        """
        labels = {
            0: "None",
            1: "Urgent",
            2: "High",
            3: "Normal",
            4: "Low",
        }
        return labels.get(priority, "None")
    
    @staticmethod
    def priority_to_number(priority: str) -> Optional[int]:
        """Convert priority string to number.
        
        Args:
            priority: Priority string (urgent, high, normal, low, none)
            
        Returns:
            Priority number or None if invalid
        """
        mapping = {
            "urgent": 1,
            "high": 2,
            "normal": 3,
            "low": 4,
            "none": 0,
            "1": 1,
            "2": 2,
            "3": 3,
            "4": 4,
            "0": 0,
        }
        return mapping.get(priority.lower())
    
    @staticmethod
    def priority_icon(priority: int) -> str:
        """Get an icon for a priority level.
        
        Args:
            priority: Priority number
            
        Returns:
            Icon emoji
        """
        icons = {
            0: "📋",
            1: "🔥",
            2: "⚡",
            3: "📌",
            4: "💤",
        }
        return icons.get(priority, "📋")
