import argparse
import json
import requests
import sys

# Constants - Update these if needed
BASE_URL = "https://services.leadconnectorhq.com"
VERSION = "2021-07-28" # Default V2 API version

def get_headers(api_key):
    return {
        "Authorization": f"Bearer {api_key}",
        "Version": VERSION,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

def handle_response(response):
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        try:
            print(f"Details: {response.json()}")
        except:
            print(f"Raw Response: {response.text}")
        sys.exit(1)

def manage_contacts(args, headers):
    url = f"{BASE_URL}/contacts"
    
    if args.action == "lookup":
        if not args.email and not args.phone:
            print("Error: lookup requires --email or --phone")
            sys.exit(1)
            
        params = {}
        if args.email: params['query'] = args.email
        elif args.phone: params['query'] = args.phone
        
        # Use search endpoint for lookup
        resp = requests.get(f"{url}/search", headers=headers, params=params)
        data = handle_response(resp)
        print(json.dumps(data, indent=2))

    elif args.action == "create":
        payload = {
            "firstName": args.first_name,
            "lastName": args.last_name,
            "email": args.email,
            "phone": args.phone
        }
        # Remove None values
        payload = {k: v for k, v in payload.items() if v}
        
        resp = requests.post(url, headers=headers, json=payload)
        data = handle_response(resp)
        print(json.dumps(data, indent=2))

    elif args.action == "update":
        if not args.contact_id:
             print("Error: update requires --contact-id")
             sys.exit(1)
        
        payload = {
            "firstName": args.first_name,
            "lastName": args.last_name,
            "email": args.email,
            "phone": args.phone
        }
        payload = {k: v for k, v in payload.items() if v}

        resp = requests.put(f"{url}/{args.contact_id}", headers=headers, json=payload)
        data = handle_response(resp)
        print(json.dumps(data, indent=2))

def manage_opportunities(args, headers):
    url = f"{BASE_URL}/opportunities"

    if args.action == "list":
         if not args.pipeline_id:
             print("Error: list opportunities requires --pipeline-id")
             sys.exit(1)
         
         params = {"pipelineId": args.pipeline_id}
         resp = requests.get(f"{url}/search", headers=headers, params=params)
         data = handle_response(resp)
         print(json.dumps(data, indent=2))

    elif args.action == "create":
        if not args.pipeline_id or not args.stage_id or not args.contact_id or not args.title:
             print("Error: create opportunity requires --pipeline-id, --stage-id, --contact-id, and --title")
             sys.exit(1)
        
        payload = {
            "pipelineId": args.pipeline_id,
            "locationId": "YOUR_LOCATION_ID_IF_NEEDED", # Usually inferred from token context in V2
            "name": args.title,
            "pipelineStageId": args.stage_id,
            "status": "open",
            "contactId": args.contact_id
        }
        
        resp = requests.post(url, headers=headers, json=payload)
        data = handle_response(resp)
        print(json.dumps(data, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Omnium Hub CRM Client")
    parser.add_argument("--api-key", required=True, help="Omnium Hub API Key (Bearer Token)")
    
    subparsers = parser.add_subparsers(dest="resource", required=True)

    # Contacts Subcommand
    contacts_parser = subparsers.add_parser("contacts", help="Manage Contacts")
    contacts_parser.add_argument("--action", choices=["lookup", "create", "update"], required=True)
    contacts_parser.add_argument("--email", help="Contact Email")
    contacts_parser.add_argument("--phone", help="Contact Phone")
    contacts_parser.add_argument("--first-name", help="First Name")
    contacts_parser.add_argument("--last-name", help="Last Name")
    contacts_parser.add_argument("--contact-id", help="Contact ID (for update)")

    # Opportunities Subcommand
    opp_parser = subparsers.add_parser("opportunities", help="Manage Opportunities")
    opp_parser.add_argument("--action", choices=["list", "create"], required=True)
    opp_parser.add_argument("--pipeline-id", help="Pipeline ID")
    opp_parser.add_argument("--stage-id", help="Stage ID")
    opp_parser.add_argument("--contact-id", help="Contact ID")
    opp_parser.add_argument("--title", help="Opportunity Title")

    # Default to contacts if resource is not specified in older style calls (compatibility)
    # But argparse handles this with subparsers.
    
    args = parser.parse_args()
    headers = get_headers(args.api_key)

    if args.resource == "contacts":
        manage_contacts(args, headers)
    elif args.resource == "opportunities":
        manage_opportunities(args, headers)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
