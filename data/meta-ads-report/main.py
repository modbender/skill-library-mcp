import os
import re
from datetime import date, timedelta
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount

# Load environment variables
load_dotenv()

class MetaAdsAnalytics:
    """
    Description:
    Retrieves Meta (Facebook/Instagram) Ads performance data for a specific period.
    Calculates Spend, Conversions, and CAC (Cost Per Acquisition).
    If no date is specified, it defaults to 'yesterday'.
    
    Usage:
    - "Show me yesterday's ad performance"
    - "CAC for the last 7 days"
    - "Ad results from 2026-02-01 to 2026-02-10"
    """
    
    name = "meta_ads_analytics"

    def __init__(self):
        self.access_token = os.getenv("META_ACCESS_TOKEN")
        self.ad_account_id = os.getenv("META_AD_ACCOUNT_ID")
        # Default event set to 'offsite_conversion.fb_pixel_custom' as requested
        self.target_event = os.getenv("META_EVENT_NAME", "offsite_conversion.fb_pixel_custom")

    def _parse_dates(self, query: str):
        """Extracts date range from natural language query."""
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # 1. Look for YYYY-MM-DD patterns
        date_pattern = r'\d{4}-\d{2}-\d{2}'
        found_dates = re.findall(date_pattern, query)
        
        if len(found_dates) >= 2:
            return found_dates[0], found_dates[1]
        elif len(found_dates) == 1:
            return found_dates[0], found_dates[0]

        # 2. Keywords (English & Korean support for convenience)
        query_lower = query.lower()
        
        if "today" in query_lower or "오늘" in query:
            return today.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
        
        if "this month" in query_lower or "이번달" in query:
            start = today.replace(day=1)
            return start.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")

        if "last month" in query_lower or "지난달" in query:
            first_day_this_month = today.replace(day=1)
            last_day_last_month = first_day_this_month - timedelta(days=1)
            first_day_last_month = last_day_last_month.replace(day=1)
            return first_day_last_month.strftime("%Y-%m-%d"), last_day_last_month.strftime("%Y-%m-%d")
            
        if any(x in query_lower for x in ["week", "7 days", "일주일", "7일"]):
            start = today - timedelta(days=7)
            return start.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")

        # Default: Yesterday
        return yesterday.strftime("%Y-%m-%d"), yesterday.strftime("%Y-%m-%d")

    def execute(self, query: str = ""):
        if not self.access_token or not self.ad_account_id:
            return "❌ Configuration Error: Please set META_ACCESS_TOKEN and META_AD_ACCOUNT_ID in your .env file."

        try:
            query = query if query else ""
            since, until = self._parse_dates(query)
            
            FacebookAdsApi.init(access_token=self.access_token)
            account = AdAccount(self.ad_account_id)
            
            fields = ['adset_name', 'spend', 'actions']
            params = {
                'time_range': {'since': since, 'until': until},
                'level': 'adset',
                'limit': 50
            }

            insights = account.get_insights(fields=fields, params=params)

            if not insights:
                return f"📅 No ad data found for the period: {since} ~ {until}."

            report = [
                f"📊 **Meta Ads Performance**",
                f"📅 Period: {since} ~ {until}",
                f"🎯 Target Event: `{self.target_event}`",
                ""
            ]
            
            total_spend = 0.0
            total_conv = 0.0

            for item in insights:
                name = item.get('adset_name', 'Unknown Ad Set')
                spend = float(item.get('spend', 0))
                
                conv = 0.0
                actions = item.get('actions', [])
                if actions:
                    for action in actions:
                        # Compare against the target event name
                        if action.get('action_type') == self.target_event:
                            conv = float(action.get('value', 0))
                            break
                
                if spend == 0: continue

                cac = spend / conv if conv > 0 else 0
                
                report.append(
                    f"🔹 **{name}**\n"
                    f"   💸 Cost: {int(spend):,} / 👤 Conv: {int(conv)}\n"
                    f"   📉 CAC: {int(cac):,}"
                )

                total_spend += spend
                total_conv += conv

            total_cac = total_spend / total_conv if total_conv > 0 else 0
                
            report.append(
                f"\n━━━━━━━━━━━━━━\n"
                f"💰 **Total Summary**\n"
                f"Total Cost: {int(total_spend):,} / Total Conv: {int(total_conv)}\n"
                f"Average CAC: **{int(total_cac):,}**"
            )

            return "\n".join(report)

        except Exception as e:
            return f"❌ Meta API Error: {str(e)}"
