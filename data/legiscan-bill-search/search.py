import requests
import json
import os
import sys
import argparse

def get_active_bills(api_key, state, queries):
    found_bills = {}

    for q in queries:
        # Ensure query is properly quoted if it contains spaces
        query_param = f'"{q}"' if ' ' in q and not q.startswith('"') else q
        url = f"https://api.legiscan.com/?key={api_key}&op=getSearch&state={state}&query={query_param}"
        try:
            response = requests.get(url).json()
            if response.get('status') == 'OK':
                search_results = response.get('searchresult', {})
                for key, bill in search_results.items():
                    if key == 'summary':
                        continue
                    if isinstance(bill, dict) and bill.get('bill_id'):
                        bill_id = bill['bill_id']
                        if bill_id not in found_bills:
                            found_bills[bill_id] = bill
            else:
                print(f"API Error for query '{q}': {response.get('error', 'Unknown error')}", file=sys.stderr)
        except Exception as e:
            print(f"Error searching {q}: {e}", file=sys.stderr)

    return found_bills

def get_bill_details(api_key, bill_id):
    url = f"https://api.legiscan.com/?key={api_key}&op=getBill&id={bill_id}"
    try:
        res = requests.get(url).json()
        if res.get('status') == 'OK':
            return res.get('bill')
    except Exception as e:
        print(f"Error fetching bill {bill_id}: {e}", file=sys.stderr)
    return None

def summarize_bills(api_key, state, queries, include_passed=False):
    bills = get_active_bills(api_key, state, queries)
    summaries = []

    for bill_id in bills:
        details = get_bill_details(api_key, bill_id)
        if not details:
            continue

        # LegiScan status: 1=Intro, 2=Engrossed, 3=Enrolled, 4=Passed, 5=Veto, 6=Conflict
        status = details.get('status', 0)

        # Filter out dead or completed bills unless requested
        if not include_passed:
            if status >= 4 or status == 0:
                continue

        number = details.get('bill_number')
        title = details.get('title')
        description = details.get('description', '')
        url = details.get('url')
        last_action = details.get('status_date', 'Unknown date')

        summary = f"**Bill {number} ({state})**: {title}\n"
        summary += f"*Last Action*: {last_action}\n"
        summary += f"*Description*: {description[:300]}...\n"
        summary += f"*Link*: {url}\n"
        summaries.append(summary)

    if not summaries:
        return f"No active bills found for keywords: {', '.join(queries)} in {state}."

    return "\n---\n".join(summaries)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search LegiScan for state bills by keywords.")
    parser.add_argument("--state", default=os.environ.get("LEGISCAN_STATE", "TX"), help="State abbreviation (e.g., TN, TX, CA)")
    parser.add_argument("--keywords", help="Comma-separated keywords (overrides defaults)")
    parser.add_argument("--all", action="store_true", help="Include passed/completed bills")

    args = parser.parse_args()

    api_key = os.environ.get("LEGISCAN_API_KEY")
    if not api_key:
        print("Error: LEGISCAN_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    if args.keywords:
        keywords = [k.strip() for k in args.keywords.split(",")]
    else:
        # Default keywords if none provided
        keywords = ["crypto", "bitcoin", "blockchain"]

    report = summarize_bills(api_key, args.state.upper(), keywords, include_passed=args.all)
    print(report)