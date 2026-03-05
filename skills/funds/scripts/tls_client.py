# Local shim to replace tls_client with curl_cffi.requests
import certifi
from curl_cffi import requests as crequests


class Session:
    def __init__(self, *args, **kwargs):
        # common tls_client kw: client_identifier, random_tls_extension_order, etc.
        self._impersonate = kwargs.get("client_identifier", "chrome")
        self._verify = kwargs.get("verify", certifi.where())
        self._session = crequests.Session(
            impersonate=self._impersonate, verify=self._verify
        )

    def get(self, url, **kwargs):
        kwargs.setdefault("verify", self._verify)
        return self._session.get(url, **kwargs)

    def post(self, url, **kwargs):
        kwargs.setdefault("verify", self._verify)
        return self._session.post(url, **kwargs)

    def put(self, url, **kwargs):
        kwargs.setdefault("verify", self._verify)
        return self._session.put(url, **kwargs)

    def delete(self, url, **kwargs):
        kwargs.setdefault("verify", self._verify)
        return self._session.delete(url, **kwargs)
