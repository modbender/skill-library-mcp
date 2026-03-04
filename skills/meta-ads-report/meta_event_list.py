import os
from datetime import date, timedelta
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount

load_dotenv()

class MetaEventListSkill:
    """
    Description:
    Fetches and lists ALL raw event names (action_types) that occurred yesterday.
    Use this to find the correct event name for your META_EVENT_NAME configuration.
    
    Usage:
    - "List all ad events"
    - "Show me available meta events"
    """
    
    name = "list_meta_events"

    def __init__(self):
        self.access_token = os.getenv("META_ACCESS_TOKEN")
        self.ad_account_id = os.getenv("META_AD_ACCOUNT_ID")

    def execute(self, query: str = ""):
        if not self.access_token or not self.ad_account_id:
            return "❌ Configuration Error: Please set META_ACCESS_TOKEN and META_AD_ACCOUNT_ID."

        try:
            FacebookAdsApi.init(access_token=self.access_token)
            account = AdAccount(self.ad_account_id)
            
            # Check data for yesterday to see recent active events
            yesterday = date.today() - timedelta(days=1)
            date_str = yesterday.strftime('%Y-%m-%d')
            
            fields = ['actions']
            params = {
                'time_range': {'since': date_str, 'until': date_str},
                'level': 'account', # Account level to see all events
            }

            insights = account.get_insights(fields=fields, params=params)

            if not insights:
                return f"⚠️ No events found for yesterday ({date_str}). Please check if your ads are active."

            data = insights[0]
            actions = data.get('actions', [])
            
            if not actions:
                return f"⚠️ Ads ran yesterday, but no conversion actions were recorded."

            # Generate list
            result_lines = [f"📋 **Available Events (from {date_str})**", "Copy the 'Action Type' below to your .env file.\n"]
            
            for action in actions:
                a_type = action.get('action_type')
                a_val = action.get('value')
                result_lines.append(f"🔹 **Type:** `{a_type}`\n   Count: {a_val}")

            return "\n".join(result_lines)

        except Exception as e:
            return f"❌ Error fetching events: {str(e)}"
