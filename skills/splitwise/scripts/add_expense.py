import sys
import os
import json
import urllib.request
import argparse

# SECURITY MANIFEST:
#   Environment variables accessed: SPLITWISE_API_KEY (only)
#   External endpoints called: https://secure.splitwise.com/ (only)
#   Local files read: none
#   Local files written: none

def main():
    parser = argparse.ArgumentParser(description="Add an expense to Splitwise")
    parser.add_argument("--cost", required=True, help="Total cost")
    parser.add_argument("--desc", required=True, help="Description")
    parser.add_argument("--payer_id", required=True, help="User ID of the payer")
    parser.add_argument("--other_id", required=True, help="User ID of the other person")
    parser.add_argument("--group_id", help="Optional group ID")
    parser.add_argument("--via", help="Custom 'via' suffix (e.g., 'whisker')")
    
    args = parser.parse_args()
    
    token = os.environ.get("SPLITWISE_API_KEY")
    if not token:
        print("ERROR: SPLITWISE_API_KEY environment variable not set.")
        sys.exit(1)
        
    url = "https://secure.splitwise.com/api/v3.0/create_expense"
    
    # Simple 50/50 split logic
    cost_float = float(args.cost)
    share = cost_float / 2
    
    # Append (via ...) to the description if provided
    description = args.desc
    if args.via:
        description = f"{description} (via {args.via})"
    
    data = {
        "cost": args.cost,
        "description": description,
        "currency_code": "USD",
        "users__0__user_id": args.payer_id,
        "users__0__paid_share": args.cost,
        "users__0__owed_share": str(share),
        "users__1__user_id": args.other_id,
        "users__1__paid_share": "0",
        "users__1__owed_share": str(share)
    }
    
    if args.group_id:
        data["group_id"] = args.group_id

    encoded_data = urllib.parse.urlencode(data).encode("utf-8")
    
    req = urllib.request.Request(url, data=encoded_data, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("User-Agent", "OpenClawAgent/1.0")
    
    try:
        with urllib.request.urlopen(req) as res:
            response_data = json.load(res)
            print(json.dumps(response_data, indent=2))
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
