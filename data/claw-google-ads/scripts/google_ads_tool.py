import sys
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description='Google Ads Management Tool (Stub)')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # List command
    list_parser = subparsers.add_parser('list', help='List campaigns')
    
    # Update status command
    status_parser = subparsers.add_parser('update-status', help='Update campaign status')
    status_parser.add_argument('--id', required=True, help='Campaign ID')
    status_parser.add_argument('--status', required=True, choices=['ENABLED', 'PAUSED'], help='New status')

    # Update budget command
    budget_parser = subparsers.add_parser('update-budget', help='Update campaign budget')
    budget_parser.add_argument('--id', required=True, help='Campaign ID')
    budget_parser.add_argument('--amount', required=True, type=float, help='New budget amount')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException

    try:
        # Load credentials from default location (~/.google-ads.yaml)
        client = GoogleAdsClient.load_from_storage()
        googleads_service = client.get_service("GoogleAdsService")
        # Find customer ID by checking reachable customers or use a default if provided
        # For now, we assume the user might have one or we'll try to list accessible ones
        customer_service = client.get_service("CustomerService")
        accessible_customers = customer_service.list_accessible_customers()
        
        # Taking the first customer for demonstration or extracting from config
        if not accessible_customers.resource_names:
            print("No accessible customers found.")
            return

        resource_name = accessible_customers.resource_names[0]
        customer_id = resource_name.split('/')[-1]
        print(f"Using Customer ID: {customer_id}")

        if args.command == 'list':
            query = """
                SELECT
                  campaign.id,
                  campaign.name,
                  campaign.status,
                  metrics.impressions,
                  metrics.clicks,
                  metrics.cost_micros
                FROM campaign
                WHERE segments.date DURING LAST_7_DAYS
            """
            search_request = client.get_type("SearchGoogleAdsRequest")
            search_request.customer_id = customer_id
            search_request.query = query
            
            results = googleads_service.search(request=search_request)
            print("-" * 50)
            print(f"{'ID':<15} {'Name':<20} {'Status':<10} {'Clicks':<8}")
            print("-" * 50)
            for row in results:
                print(f"{row.campaign.id:<15} {row.campaign.name:<20} {row.campaign.status.name:<10} {row.metrics.clicks:<8}")
            print("-" * 50)

    except GoogleAdsException as ex:
        print(f"Request with ID '{ex.request_id}' failed with status '{ex.error.code().name}' and includes the following errors:")
        for error in ex.failure.errors:
            print(f"\tError with message '{error.message}'.")
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    print(f"\t\tOn field: {field_path_element.field_name}")
        sys.exit(1)
    except Exception as e:
        import traceback
        print(f"An unexpected error occurred: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
