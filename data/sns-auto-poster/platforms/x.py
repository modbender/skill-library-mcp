"""X (Twitter) platform - OAuth 1.0a posting."""
import os, hmac, hashlib, base64, time, urllib.parse, uuid, requests
from .base import BasePlatform

class XPlatform(BasePlatform):
    def __init__(self):
        self.consumer_key = os.environ.get("X_CONSUMER_KEY", "")
        self.consumer_secret = os.environ.get("X_CONSUMER_SECRET", "")
        self.access_token = os.environ.get("X_ACCESS_TOKEN", "")
        self.access_token_secret = os.environ.get("X_ACCESS_TOKEN_SECRET", "")

    def _sign(self, method, url, params):
        sorted_params = "&".join(f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(v, safe='')}" for k, v in sorted(params.items()))
        base = f"{method}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(sorted_params, safe='')}"
        key = f"{urllib.parse.quote(self.consumer_secret, safe='')}&{urllib.parse.quote(self.access_token_secret, safe='')}"
        return base64.b64encode(hmac.new(key.encode(), base.encode(), hashlib.sha1).digest()).decode()

    def _auth_header(self, method, url):
        oauth = {
            "oauth_consumer_key": self.consumer_key,
            "oauth_nonce": uuid.uuid4().hex,
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": str(int(time.time())),
            "oauth_token": self.access_token,
            "oauth_version": "1.0",
        }
        oauth["oauth_signature"] = self._sign(method, url, oauth)
        return "OAuth " + ", ".join(f'{urllib.parse.quote(k, safe="")}="{urllib.parse.quote(v, safe="")}"' for k, v in sorted(oauth.items()))

    def _upload_media(self, path):
        url = "https://upload.twitter.com/1.1/media/upload.json"
        r = requests.post(url, headers={"Authorization": self._auth_header("POST", url)}, files={"media": open(path, "rb")})
        if r.status_code in (200, 201, 202):
            return r.json()["media_id_string"]
        return None

    def post(self, text, image_path=None, reply_to=None):
        url = "https://api.twitter.com/2/tweets"
        payload = {"text": text}
        if reply_to:
            payload["reply"] = {"in_reply_to_tweet_id": reply_to}
        if image_path:
            mid = self._upload_media(image_path)
            if mid:
                payload["media"] = {"media_ids": [mid]}
        r = requests.post(url, headers={"Authorization": self._auth_header("POST", url), "Content-Type": "application/json"}, json=payload)
        if r.status_code in (200, 201):
            tid = r.json()["data"]["id"]
            return {"success": True, "id": tid, "url": f"https://x.com/i/status/{tid}"}
        return {"success": False, "error": r.text}
