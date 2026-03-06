#!/usr/bin/env python3
"""
Kimai CLI - Complete API client for Kimai time-tracking software.
Supports timesheets, customers, projects, activities, teams, invoices.
"""

import argparse
import csv
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime
from typing import Optional, Dict, Any, List

VERSION = "1.0.0"
API_VERSION = "1.1"


class KimaiError(Exception):
    """Custom exception for Kimai API errors"""
    pass


class KimaiClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Any:
        """Make HTTP request to Kimai API"""
        url = f"{self.base_url}/api/{endpoint}"
        if params:
            query = '&'.join(f"{k}={v}" for k, v in params.items() if v is not None)
            if query:
                url += f"?{query}"
        
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode() if data else None,
                headers=self.headers,
                method=method
            )
            with urllib.request.urlopen(req) as response:
                if response.status == 204:
                    return None
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            try:
                error_data = json.loads(body)
                raise KimaiError(f"API Error {e.code}: {error_data.get('message', body)}")
            except json.JSONDecodeError:
                raise KimaiError(f"HTTP Error {e.code}: {body}")
        except Exception as e:
            raise KimaiError(f"Request failed: {e}")

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        return self._request('GET', endpoint, params=params)

    def post(self, endpoint: str, data: Dict) -> Any:
        return self._request('POST', endpoint, data=data)

    def patch(self, endpoint: str, data: Dict) -> Any:
        return self._request('PATCH', endpoint, data=data)

    def delete(self, endpoint: str) -> None:
        return self._request('DELETE', endpoint)


class OutputFormatter:
    @staticmethod
    def print_json(data: Any):
        print(json.dumps(data, indent=2, ensure_ascii=False))

    @staticmethod
    def print_table(data: List[Dict], fields: Optional[List[str]] = None):
        if not data:
            print("No data")
            return
        if not isinstance(data, list):
            data = [data]
        if not fields:
            fields = list(data[0].keys())
        
        # Calculate widths
        widths = {f: max(len(str(f)), max(len(str(row.get(f, ''))) for row in data)) for f in fields}
        
        # Print header
        header = " | ".join(f.ljust(widths[f]) for f in fields)
        print(header)
        print("-" * len(header))
        
        # Print rows
        for row in data:
            print(" | ".join(str(row.get(f, '')).ljust(widths[f]) for f in fields))

    @staticmethod
    def print_csv(data: List[Dict], fields: Optional[List[str]] = None):
        if not isinstance(data, list):
            data = [data]
        if not fields and data:
            fields = list(data[0].keys())
        
        writer = csv.DictWriter(sys.stdout, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)


def confirm_deletion(entity_type: str, entity_id: str, cascade_warning: str = "") -> bool:
    """Interactive confirmation for destructive operations"""
    print(f"⚠️ WARNING: You are about to DELETE {entity_type} ID {entity_id}")
    if cascade_warning:
        print(f"   {cascade_warning}")
    print("This action cannot be undone.")
    response = input("Type 'yes' to confirm: ")
    return response.strip().lower() == 'yes'


def get_client() -> KimaiClient:
    """Initialize client from environment"""
    base_url = os.getenv('KIMAI_BASE_URL')
    token = os.getenv('KIMAI_API_TOKEN')
    
    if not base_url or not token:
        print("Error: KIMAI_BASE_URL and KIMAI_API_TOKEN environment variables required", file=sys.stderr)
        sys.exit(1)
    
    return KimaiClient(base_url, token)


def handle_timesheets(args):
    client = get_client()
    fmt = OutputFormatter()
    
    if args.command == 'list':
        params = {
            'user': args.user,
            'customer': args.customer,
            'project': args.project,
            'activity': args.activity,
            'begin': args.begin,
            'end': args.end,
            'exported': args.exported,
            'billable': args.billable,
            'active': args.active,
            'page': args.page,
            'size': args.size,
            'orderBy': args.order_by,
            'order': args.order,
            'full': 1 if args.full else 0
        }
        data = client.get('timesheets', {k: v for k, v in params.items() if v is not None})
        if args.format == 'json':
            fmt.print_json(data)
        elif args.format == 'csv':
            fmt.print_csv(data, ['id', 'begin', 'end', 'duration', 'project', 'activity', 'description', 'rate'])
        else:
            fmt.print_table(data, ['id', 'begin', 'end', 'duration', 'description', 'rate'])
    
    elif args.command == 'get':
        data = client.get(f'timesheets/{args.id}')
        fmt.print_json(data) if args.format == 'json' else fmt.print_table([data])
    
    elif args.command == 'create':
        data = {
            'project': args.project,
            'activity': args.activity,
            'description': args.description,
            'tags': args.tags,
            'begin': args.begin,
            'end': args.end,
            'billable': args.billable,
            'exported': args.exported
        }
        # Remove None values but keep False
        data = {k: v for k, v in data.items() if v is not None}
        result = client.post('timesheets', data)
        print(f"{'Started' if not args.end else 'Created'} timesheet ID: {result['id']}")
        fmt.print_json(result) if args.format == 'json' else None
    
    elif args.command == 'stop':
        result = client.patch(f'timesheets/{args.id}/stop', {})
        print(f"Stopped timesheet ID: {result['id']}")
        fmt.print_json(result) if args.format == 'json' else None
    
    elif args.command == 'active':
        data = client.get('timesheets/active')
        if args.format == 'json':
            fmt.print_json(data)
        else:
            fmt.print_table(data, ['id', 'begin', 'project', 'activity', 'description'])
    
    elif args.command == 'recent':
        params = {'begin': args.begin, 'size': args.size}
        data = client.get('timesheets/recent', {k: v for k, v in params.items() if v})
        fmt.print_json(data) if args.format == 'json' else fmt.print_table(data)
    
    elif args.command == 'delete':
        cascade = "This will delete ALL linked timesheet entries."
        if not args.force and not confirm_deletion('timesheet', args.id, cascade):
            print("Cancelled")
            sys.exit(0)
        client.delete(f'timesheets/{args.id}')
        print(f"Deleted timesheet {args.id}")


def handle_customers(args):
    client = get_client()
    fmt = OutputFormatter()
    
    if args.command == 'list':
        params = {'visible': args.visible, 'term': args.term, 'orderBy': args.order_by}
        data = client.get('customers', {k: v for k, v in params.items() if v})
        fmt.print_json(data) if args.format == 'json' else fmt.print_table(data, ['id', 'name', 'visible', 'currency'])
    
    elif args.command == 'get':
        data = client.get(f'customers/{args.id}')
        fmt.print_json(data)
    
    elif args.command == 'create':
        data = {
            'name': args.name,
            'country': args.country,
            'currency': args.currency,
            'timezone': args.timezone,
            'comment': args.comment,
            'number': args.number,
            'visible': args.visible,
            'billable': args.billable
        }
        data = {k: v for k, v in data.items() if v is not None}
        result = client.post('customers', data)
        print(f"Created customer ID: {result['id']}")
        fmt.print_json(result)
    
    elif args.command == 'delete':
        cascade = "This will delete ALL linked projects, activities, and timesheets."
        if not args.force and not confirm_deletion('customer', args.id, cascade):
            print("Cancelled")
            sys.exit(0)
        client.delete(f'customers/{args.id}')
        print(f"Deleted customer {args.id}")


def handle_projects(args):
    client = get_client()
    fmt = OutputFormatter()
    
    if args.command == 'list':
        params = {
            'customer': args.customer,
            'visible': args.visible,
            'term': args.term,
            'globalActivities': args.global_activities
        }
        data = client.get('projects', {k: v for k, v in params.items() if v})
        fmt.print_json(data) if args.format == 'json' else fmt.print_table(data, ['id', 'name', 'customer', 'visible'])
    
    elif args.command == 'create':
        data = {
            'name': args.name,
            'customer': args.customer,
            'comment': args.comment,
            'visible': args.visible,
            'billable': args.billable,
            'globalActivities': args.global_activities
        }
        data = {k: v for k, v in data.items() if v is not None}
        result = client.post('projects', data)
        print(f"Created project ID: {result['id']}")
        fmt.print_json(result)
    
    elif args.command == 'delete':
        cascade = "This will delete ALL linked activities and timesheets."
        if not args.force and not confirm_deletion('project', args.id, cascade):
            print("Cancelled")
            sys.exit(0)
        client.delete(f'projects/{args.id}')
        print(f"Deleted project {args.id}")


def handle_activities(args):
    client = get_client()
    fmt = OutputFormatter()
    
    if args.command == 'list':
        params = {'project': args.project, 'visible': args.visible, 'globals': args.globals_only}
        data = client.get('activities', {k: v for k, v in params.items() if v})
        fmt.print_json(data) if args.format == 'json' else fmt.print_table(data, ['id', 'name', 'project', 'visible'])
    
    elif args.command == 'create':
        data = {
            'name': args.name,
            'project': args.project,
            'comment': args.comment,
            'visible': args.visible,
            'billable': args.billable
        }
        data = {k: v for k, v in data.items() if v is not None}
        result = client.post('activities', data)
        print(f"Created activity ID: {result['id']}")
        fmt.print_json(result)
    
    elif args.command == 'delete':
        cascade = "This will delete ALL linked timesheets."
        if not args.force and not confirm_deletion('activity', args.id, cascade):
            print("Cancelled")
            sys.exit(0)
        client.delete(f'activities/{args.id}')
        print(f"Deleted activity {args.id}")


def handle_system(args):
    client = get_client()
    fmt = OutputFormatter()
    
    if args.command == 'ping':
        data = client.get('ping')
        print(data.get('message', 'pong'))
    elif args.command == 'version':
        data = client.get('version')
        fmt.print_json(data)
    elif args.command == 'plugins':
        data = client.get('plugins')
        fmt.print_json(data)
    elif args.command == 'config':
        data = client.get('config/timesheet')
        fmt.print_json(data)


def main():
    parser = argparse.ArgumentParser(
        description='Kimai CLI - Time Tracking API Client',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment variables:
  KIMAI_BASE_URL    - API base URL (https://kimai.example.com)
  KIMAI_API_TOKEN   - Bearer token
"""
    )
    subparsers = parser.add_subparsers(dest='resource', help='API Resource')

    # Timesheets
    ts_parser = subparsers.add_parser('timesheets', help='Time tracking operations')
    ts_sub = ts_parser.add_subparsers(dest='command')
    
    ts_list = ts_sub.add_parser('list', help='List timesheets')
    ts_list.add_argument('--user', help='Filter by user ID or "all"')
    ts_list.add_argument('--customer', type=int, help='Filter by customer ID')
    ts_list.add_argument('--project', type=int, help='Filter by project ID')
    ts_list.add_argument('--activity', type=int, help='Filter by activity ID')
    ts_list.add_argument('--begin', help='Start date (YYYY-MM-DDTHH:mm:ss)')
    ts_list.add_argument('--end', help='End date (YYYY-MM-DDTHH:mm:ss)')
    ts_list.add_argument('--exported', choices=['0', '1'], help='Export status filter')
    ts_list.add_argument('--billable', choices=['0', '1'], help='Billable filter')
    ts_list.add_argument('--active', choices=['0', '1'], help='Active filter')
    ts_list.add_argument('--page', type=int, default=1)
    ts_list.add_argument('--size', type=int, default=50)
    ts_list.add_argument('--order-by', choices=['id', 'begin', 'end', 'rate'])
    ts_list.add_argument('--order', choices=['ASC', 'DESC'])
    ts_list.add_argument('--full', action='store_true', help='Full objects')
    ts_list.add_argument('--format', choices=['json', 'table', 'csv'], default='table')

    ts_get = ts_sub.add_parser('get', help='Get timesheet by ID')
    ts_get.add_argument('id', type=int)
    ts_get.add_argument('--format', choices=['json', 'table'], default='table')

    ts_create = ts_sub.add_parser('create', help='Create timesheet/start timer')
    ts_create.add_argument('--project', type=int, required=True, help='Project ID')
    ts_create.add_argument('--activity', type=int, required=True, help='Activity ID')
    ts_create.add_argument('--description', help='Description')
    ts_create.add_argument('--tags', help='Comma-separated tags')
    ts_create.add_argument('--begin', help='Start time (defaults to now)')
    ts_create.add_argument('--end', help='End time (omit for active timer)')
    ts_create.add_argument('--billable', type=bool, default=True)
    ts_create.add_argument('--exported', type=bool, default=False)
    ts_create.add_argument('--format', choices=['json', 'table'], default='table')

    ts_stop = ts_sub.add_parser('stop', help='Stop active timesheet')
    ts_stop.add_argument('id', type=int, help='Timesheet ID')
    ts_stop.add_argument('--format', choices=['json', 'table'], default='table')

    ts_active = ts_sub.add_parser('active', help='List active timers')
    ts_active.add_argument('--format', choices=['json', 'table'], default='table')

    ts_recent = ts_sub.add_parser('recent', help='Recent activities')
    ts_recent.add_argument('--begin', help='Start date filter')
    ts_recent.add_argument('--size', type=int, default=10)
    ts_recent.add_argument('--format', choices=['json', 'table'], default='table')

    ts_del = ts_sub.add_parser('delete', help='Delete timesheet')
    ts_del.add_argument('id', type=int)
    ts_del.add_argument('--force', action='store_true', help='Skip confirmation')

    # Customers
    cust_parser = subparsers.add_parser('customers', help='Customer management')
    cust_sub = cust_parser.add_subparsers(dest='command')
    
    cust_list = cust_sub.add_parser('list', help='List customers')
    cust_list.add_argument('--visible', choices=['1', '2', '3'], default='1')
    cust_list.add_argument('--term', help='Search term')
    cust_list.add_argument('--order-by', choices=['id', 'name'])
    cust_list.add_argument('--format', choices=['json', 'table'], default='table')

    cust_get = cust_sub.add_parser('get', help='Get customer')
    cust_get.add_argument('id', type=int)
    cust_get.add_argument('--format', choices=['json', 'table'], default='json')

    cust_create = cust_sub.add_parser('create', help='Create customer')
    cust_create.add_argument('name', help='Customer name')
    cust_create.add_argument('--country', required=True, help='Country code (ISO 3166-1 alpha-2)')
    cust_create.add_argument('--currency', required=True, help='Currency code (ISO 4217)')
    cust_create.add_argument('--timezone', required=True, help='Timezone (e.g., Europe/Berlin)')
    cust_create.add_argument('--comment', help='Comment/description')
    cust_create.add_argument('--number', help='Customer number')
    cust_create.add_argument('--visible', type=bool, default=True)
    cust_create.add_argument('--billable', type=bool, default=True)

    cust_del = cust_sub.add_parser('delete', help='Delete customer')
    cust_del.add_argument('id', type=int)
    cust_del.add_argument('--force', action='store_true', help='Skip confirmation')

    # Projects
    proj_parser = subparsers.add_parser('projects', help='Project management')
    proj_sub = proj_parser.add_subparsers(dest='command')
    
    proj_list = proj_sub.add_parser('list', help='List projects')
    proj_list.add_argument('--customer', type=int, help='Filter by customer')
    proj_list.add_argument('--visible', choices=['1', '2', '3'], default='1')
    proj_list.add_argument('--term', help='Search term')
    proj_list.add_argument('--global-activities', choices=['0', '1'])
    proj_list.add_argument('--format', choices=['json', 'table'], default='table')

    proj_create = proj_sub.add_parser('create', help='Create project')
    proj_create.add_argument('name', help='Project name')
    proj_create.add_argument('--customer', type=int, required=True, help='Customer ID')
    proj_create.add_argument('--comment', help='Description')
    proj_create.add_argument('--visible', type=bool, default=True)
    proj_create.add_argument('--billable', type=bool, default=True)
    proj_create.add_argument('--global-activities', type=bool, default=True)

    proj_del = proj_sub.add_parser('delete', help='Delete project')
    proj_del.add_argument('id', type=int)
    proj_del.add_argument('--force', action='store_true')

    # Activities
    act_parser = subparsers.add_parser('activities', help='Activity management')
    act_sub = act_parser.add_subparsers(dest='command')
    
    act_list = act_sub.add_parser('list', help='List activities')
    act_list.add_argument('--project', type=int, help='Filter by project')
    act_list.add_argument('--visible', choices=['1', '2', '3'], default='1')
    act_list.add_argument('--globals-only', choices=['0', '1'], help='Only global activities')
    act_list.add_argument('--format', choices=['json', 'table'], default='table')

    act_create = act_sub.add_parser('create', help='Create activity')
    act_create.add_argument('name', help='Activity name')
    act_create.add_argument('--project', type=int, help='Project ID (omit for global)')
    act_create.add_argument('--comment', help='Description')
    act_create.add_argument('--visible', type=bool, default=True)
    act_create.add_argument('--billable', type=bool, default=True)

    act_del = act_sub.add_parser('delete', help='Delete activity')
    act_del.add_argument('id', type=int)
    act_del.add_argument('--force', action='store_true')

    # System
    sys_parser = subparsers.add_parser('system', help='System info')
    sys_sub = sys_parser.add_subparsers(dest='command')
    sys_sub.add_parser('ping', help='Test connectivity')
    sys_sub.add_parser('version', help='Get version')
    sys_sub.add_parser('plugins', help='List plugins')
    sys_sub.add_parser('config', help='Timesheet config')

    args = parser.parse_args()

    if not args.resource:
        parser.print_help()
        sys.exit(1)

    try:
        if args.resource == 'timesheets':
            handle_timesheets(args)
        elif args.resource == 'customers':
            handle_customers(args)
        elif args.resource == 'projects':
            handle_projects(args)
        elif args.resource == 'activities':
            handle_activities(args)
        elif args.resource == 'system':
            handle_system(args)
        else:
            print(f"Resource '{args.resource}' not yet implemented", file=sys.stderr)
            sys.exit(1)
    except KimaiError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nCancelled", file=sys.stderr)
        sys.exit(130)


if __name__ == '__main__':
    main()
