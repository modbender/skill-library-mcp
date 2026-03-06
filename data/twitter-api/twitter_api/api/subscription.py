from typing import Dict, Any, Optional

from ..core.client import TwitterAPIClient
from ..utils.constants import Endpoints
from ..utils.helpers import create_form_data

class SubscriptionAPI:
    """
    API for subscription-related operations.
    """
    
    def __init__(self, client: TwitterAPIClient):
        """
        Initialize the Subscription API.
        
        Args:
            client (TwitterAPIClient): Twitter API client
        """
        self.client = client
    
    async def verify_subscription(self) -> Optional[Dict[str, Any]]:
        """
        Verify subscription status.
        
        Returns:
            Optional[Dict[str, Any]]: Response from the API
        """
        params = {
            'variables': '{}'
        }
        return await self.client.get(Endpoints.VERIFY_SUBSCRIPTION, params=params)
    
    async def create_subscription(self, 
                                    payment_method_id: str, 
                                    subscription_type: str = "premium") -> Optional[Dict[str, Any]]:
        """
        Create a new subscription.
        
        Args:
            payment_method_id (str): Payment method ID
            subscription_type (str, optional): Subscription type. Defaults to "premium".
            
        Returns:
            Optional[Dict[str, Any]]: Response from the API
        """
        data = {
            "payment_method_id": payment_method_id,
            "subscription_type": subscription_type
        }
        
        form_data = create_form_data(data)
        return await self.client.post(Endpoints.CREATE_SUBSCRIPTION, data=form_data)


async def _demo_verify_subscription(auth_token: str, ct0: str) -> None:
    """Load primary creds and call verify_subscription."""
    client = TwitterAPIClient(auth_token, ct0=ct0)
    sub_api = SubscriptionAPI(client)
    data = await sub_api.verify_subscription()
    if data is None:
        print("No data (auth failed or API error)")
        return
    import json
    print(json.dumps(data, indent=2, default=str))


if __name__ == "__main__":
    import asyncio
    import os
    cwd = os.path.abspath(os.getcwd())
    for path in [os.path.join(cwd, ".env"), os.path.join(cwd, "social_ops", ".env")]:
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip())
            break
    auth = os.environ.get("GANCLAW_X_PRIMARY_AUTH_TOKEN") or os.environ.get("PICLAW_TWITTER_AUTH_TOKEN") or ""
    ct0 = os.environ.get("GANCLAW_X_PRIMARY_CT0") or os.environ.get("PICLAW_TWITTER_CT0") or ""
    if not auth or not ct0:
        print("Set GANCLAW_X_PRIMARY_AUTH_TOKEN and GANCLAW_X_PRIMARY_CT0 (e.g. in .env)")
        raise SystemExit(1)
    asyncio.run(_demo_verify_subscription(auth, ct0))