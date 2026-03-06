#!/usr/bin/env python3
"""
Fetch issues from Sentry API.

Usage:
    python3 sentry_issues.py --org <org> --project <project> [options]

Examples:
    # List recent unresolved issues
    python3 sentry_issues.py --org myorg --project myproject
    
    # Get specific issue with stack trace
    python3 sentry_issues.py --org myorg --project myproject --issue 12345 --details
    
    # Filter by query
    python3 sentry_issues.py --org myorg --project myproject --query "is:unresolved level:error"
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse

SENTRY_API_BASE = "https://sentry.io/api/0"


def get_auth_token(token_arg):
    """Get auth token from argument or environment."""
    if token_arg:
        return token_arg
    token = os.environ.get("SENTRY_AUTH_TOKEN")
    if not token:
        print("Error: No auth token provided. Set SENTRY_AUTH_TOKEN or use --token", file=sys.stderr)
        sys.exit(1)
    return token


def make_request(url, token):
    """Make authenticated request to Sentry API."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        print(f"HTTP Error {e.code}: {e.reason}", file=sys.stderr)
        if error_body:
            print(f"Response: {error_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def list_issues(org, project, token, query=None, limit=25, sort="date"):
    """List issues for a project."""
    params = {
        "limit": limit,
        "sort": sort,
    }
    if query:
        params["query"] = query
    
    query_string = urllib.parse.urlencode(params)
    url = f"{SENTRY_API_BASE}/projects/{org}/{project}/issues/?{query_string}"
    
    issues = make_request(url, token)
    return issues


def get_issue_details(org, issue_id, token):
    """Get detailed information about a specific issue."""
    # Get issue info
    issue_url = f"{SENTRY_API_BASE}/issues/{issue_id}/"
    issue = make_request(issue_url, token)
    
    # Get latest event for stack trace
    events_url = f"{SENTRY_API_BASE}/issues/{issue_id}/events/latest/"
    try:
        latest_event = make_request(events_url, token)
        issue["latestEvent"] = latest_event
    except SystemExit:
        # Event might not exist, continue without it
        issue["latestEvent"] = None
    
    return issue


def format_issue_summary(issue):
    """Format issue for display."""
    return {
        "id": issue.get("id"),
        "title": issue.get("title"),
        "culprit": issue.get("culprit"),
        "level": issue.get("level"),
        "status": issue.get("status"),
        "count": issue.get("count"),
        "userCount": issue.get("userCount"),
        "firstSeen": issue.get("firstSeen"),
        "lastSeen": issue.get("lastSeen"),
        "permalink": issue.get("permalink"),
    }


def format_issue_details(issue):
    """Format detailed issue with stack trace."""
    result = format_issue_summary(issue)
    
    # Add metadata
    result["metadata"] = issue.get("metadata", {})
    result["tags"] = issue.get("tags", [])
    
    # Extract stack trace from latest event
    latest_event = issue.get("latestEvent")
    if latest_event:
        result["eventId"] = latest_event.get("eventID")
        result["context"] = latest_event.get("context", {})
        result["tags"] = latest_event.get("tags", [])
        
        # Get exception/stack trace
        entries = latest_event.get("entries", [])
        for entry in entries:
            if entry.get("type") == "exception":
                exceptions = entry.get("data", {}).get("values", [])
                result["exceptions"] = []
                for exc in exceptions:
                    exc_data = {
                        "type": exc.get("type"),
                        "value": exc.get("value"),
                        "stacktrace": [],
                    }
                    stacktrace = exc.get("stacktrace", {})
                    frames = stacktrace.get("frames", [])
                    for frame in frames[-10:]:  # Last 10 frames
                        exc_data["stacktrace"].append({
                            "filename": frame.get("filename"),
                            "function": frame.get("function"),
                            "lineNo": frame.get("lineNo"),
                            "context": frame.get("context", []),
                        })
                    result["exceptions"].append(exc_data)
            elif entry.get("type") == "breadcrumbs":
                crumbs = entry.get("data", {}).get("values", [])
                result["breadcrumbs"] = crumbs[-5:]  # Last 5 breadcrumbs
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Fetch issues from Sentry")
    parser.add_argument("--org", required=True, help="Sentry organization slug")
    parser.add_argument("--project", required=True, help="Project slug")
    parser.add_argument("--token", help="Auth token (or set SENTRY_AUTH_TOKEN)")
    parser.add_argument("--issue", help="Specific issue ID to fetch")
    parser.add_argument("--details", action="store_true", help="Include stack trace and event details")
    parser.add_argument("--query", help="Filter query (e.g., 'is:unresolved level:error')")
    parser.add_argument("--limit", type=int, default=25, help="Max issues to return")
    parser.add_argument("--sort", choices=["date", "new", "priority", "freq", "user"], 
                       default="date", help="Sort order")
    
    args = parser.parse_args()
    token = get_auth_token(args.token)
    
    if args.issue:
        # Fetch specific issue
        issue = get_issue_details(args.org, args.issue, token)
        if args.details:
            result = format_issue_details(issue)
        else:
            result = format_issue_summary(issue)
        print(json.dumps(result, indent=2))
    else:
        # List issues
        issues = list_issues(
            args.org, 
            args.project, 
            token, 
            query=args.query,
            limit=args.limit,
            sort=args.sort
        )
        if args.details:
            result = [format_issue_details(i) for i in issues]
        else:
            result = [format_issue_summary(i) for i in issues]
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
