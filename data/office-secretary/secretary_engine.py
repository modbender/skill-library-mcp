import os, sys, msal, requests, json, stat
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Configuration
BASE_DIR = os.path.dirname(__file__)
load_dotenv(os.path.join(BASE_DIR, '.env'))
CACHE_PATH = os.path.join(BASE_DIR, 'token_cache.bin')

# FIX: Removed 'Tasks.ReadWrite' to adhere to least-privilege requirements.
# These scopes now perfectly match the documented features in SKILL.md.
REQUIRED_SCOPES = [
    'User.Read',
    'Mail.ReadWrite',
    'Calendars.ReadWrite',
    'Files.ReadWrite',
    'ChatMessage.Send'
]

class UnifiedSecretary:
    def __init__(self):
        self.client_id = os.getenv('SECRETARY_CLIENT_ID')
        self.tenant_id = os.getenv('SECRETARY_TENANT_ID')
        self.base_url = "https://graph.microsoft.com/v1.0"
        
        if not self.client_id or not self.tenant_id:
            raise ValueError("SECURITY ERROR: Missing SECRETARY_CLIENT_ID or SECRETARY_TENANT_ID in .env")

        self.cache = msal.SerializableTokenCache()
        self._load_cache()

    def _load_cache(self):
        """Safely loads the token cache and enforces file permissions."""
        if os.path.exists(CACHE_PATH):
            if os.name != 'nt': # Unix-like permission hardening
                os.chmod(CACHE_PATH, stat.S_IRUSR | stat.S_IWUSR)
            with open(CACHE_PATH, "r") as f:
                self.cache.deserialize(f.read())

    def _save_cache(self):
        """Saves cache and ensures it is only readable by the owner."""
        with open(CACHE_PATH, "w") as f:
            f.write(self.cache.serialize())
        if os.name != 'nt':
            os.chmod(CACHE_PATH, stat.S_IRUSR | stat.S_IWUSR)

    def get_token(self):
        authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        app = msal.PublicClientApplication(self.client_id, authority=authority, token_cache=self.cache)
        
        accounts = app.get_accounts()
        result = app.acquire_token_silent(REQUIRED_SCOPES, account=accounts[0]) if accounts else None
        
        if not result:
            result = app.acquire_token_interactive(REQUIRED_SCOPES)
            self._save_cache()
        return result.get('access_token')

    def call(self, method, endpoint, data=None):
        headers = {'Authorization': f'Bearer {self.get_token()}', 'Content-Type': 'application/json'}
        return requests.request(method, f"{self.base_url}/{endpoint}", headers=headers, json=data)

    def find_meeting(self, email):
        payload = {
            "schedules": [email],
            "startTime": {"dateTime": datetime.utcnow().isoformat() + "Z", "timeZone": "UTC"},
            "endTime": {"dateTime": (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z", "timeZone": "UTC"},
            "availabilityViewInterval": 60
        }
        return self.call("POST", "me/calendar/getSchedule", payload).json()

    def post_teams(self, team_id, channel_id, msg):
        return self.call("POST", f"teams/{team_id}/channels/{channel_id}/messages", {"body": {"content": msg}})

    def triage_mail(self):
        messages = self.call("GET", "me/messages?$filter=importance eq 'high'&$top=5").json()
        for m in messages.get('value', []):
            self.call("PATCH", f"me/messages/{m['id']}", {"categories": ["Urgent"]})
        return f"Triaged {len(messages.get('value', []))} items."

    def cleanup_drive(self):
        t = (datetime.utcnow() - timedelta(days=90)).isoformat() + "Z"
        items = self.call("GET", f"me/drive/root/children?$filter=lastModifiedDateTime lt {t}").json()
        return [i['name'] for i in items.get('value', [])]

if __name__ == "__main__":
    sec = UnifiedSecretary()
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "mail": print(sec.triage_mail())
        elif cmd == "drive": print(sec.cleanup_drive())
        elif cmd == "calendar": print(sec.find_meeting(sys.argv[2]))
        elif cmd == "teams": print(sec.post_teams(sys.argv[2], sys.argv[3], sys.argv[4]))