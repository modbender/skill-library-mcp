from typing import Optional

from .core.client import TwitterAPIClient
from .api.tweet import TweetAPI
from .api.user import UserAPI
from .api.profile import ProfileAPI
from .api.relationship import RelationshipAPI
from .api.subscription import SubscriptionAPI
from .api.direct_message import DirectMessageAPI
from .api.timeline_service import TimelineService

class Twitter:
    """
    Main Twitter API client that combines all API modules.
    """
    
    def __init__(self, auth_token: str, ct0: Optional[str] = None):
        """
        Initialize the Twitter API client.
        
        Args:
            auth_token (str): Authentication token
            ct0 (Optional[str], optional): CSRF token. Defaults to None.
        """
        self.auth_token = auth_token
        self.ct0 = ct0
        self.client = TwitterAPIClient(auth_token, ct0)
        
        # Initialize API modules
        self.tweet = TweetAPI(self.client)
        self.user = UserAPI(self.client)
        self.profile = ProfileAPI(auth_token, ct0)
        self.relationship = RelationshipAPI(self.client)
        self.subscription = SubscriptionAPI(self.client)
        self.direct_message = DirectMessageAPI(self.client)
        
        # Initialize service modules
        self.timeline = TimelineService(self.tweet)
    
    async def fetch_csrf_token(self) -> Optional[str]:
        """
        Fetch a new CSRF token.
        
        Returns:
            Optional[str]: New CSRF token
        """
        return await self.client.fetch_csrf_token() 