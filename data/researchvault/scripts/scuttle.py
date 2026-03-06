from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
import os
import inspect
import ipaddress
import socket
import urllib.parse
import requests
import certifi
from bs4 import BeautifulSoup
import re
import json
import logging

class ScuttleError(Exception):
    pass

DEFAULT_TIMEOUT_S = 15
MAX_FETCH_SIZE = 10 * 1024 * 1024 # 10MB cap
MAX_REDIRECTS = 5

@dataclass
class ScuttleConfig:
    allow_private_networks: bool = False
    timeout_s: int = DEFAULT_TIMEOUT_S
    max_size_bytes: int = MAX_FETCH_SIZE
    max_redirects: int = MAX_REDIRECTS

def _resolve_scuttle_config(config: Optional["ScuttleConfig"]) -> "ScuttleConfig":
    if isinstance(config, ScuttleConfig):
        return config
    return ScuttleConfig()

def _call_with_optional_config(fn, source: str, config: "ScuttleConfig"):
    try:
        sig = inspect.signature(fn)
        params = list(sig.parameters.values())
        if any(p.kind in (p.VAR_POSITIONAL, p.VAR_KEYWORD) for p in params):
            return fn(source, config)
        if len(params) >= 2:
            return fn(source, config)
        return fn(source)
    except (TypeError, ValueError):
        try:
            return fn(source, config)
        except TypeError:
            return fn(source)

class SafeSession(requests.Session):
    """
    Session that enforces strict SSRF protections.
    - Blocks private/local/link-local networks.
    - Resolves DNS and verifies resolved IPs.
    - Respects redirect limits and re-verifies safe URLs on every hop.
    """
    def __init__(self, config: ScuttleConfig):
        super().__init__()
        self.trust_env = False # No proxies
        self.scuttle_config = config
        self.max_redirects = config.max_redirects

    def request(self, method, url, **kwargs):
        # We handle redirects manually to ensure safety on every hop
        kwargs["allow_redirects"] = False
        kwargs["timeout"] = self.scuttle_config.timeout_s
        
        # Explicitly set CA bundle to ensure TLS verification works in CI environments
        if "verify" not in kwargs:
            kwargs["verify"] = os.environ.get("REQUESTS_CA_BUNDLE") or os.environ.get("SSL_CERT_FILE") or certifi.where()

        current_url = url
        redirect_count = 0
        
        while True:
            _ensure_safe_url(current_url, self.scuttle_config.allow_private_networks)
            
            # Use stream to check size
            kwargs["stream"] = True
            resp = super().request(method, current_url, **kwargs)
            
            # Check size
            cl = resp.headers.get("Content-Length")
            if cl:
                try:
                    if int(cl) > self.scuttle_config.max_size_bytes:
                        raise ScuttleError(f"Response too large: {cl} bytes")
                except (ValueError, TypeError):
                    pass
            
            is_redirect = getattr(resp, "is_redirect", False)
            if is_redirect is True:
                redirect_count += 1
                if redirect_count > self.max_redirects:
                    raise ScuttleError(f"Too many redirects ({redirect_count})")
                
                next_url = resp.headers.get("Location") if hasattr(resp, "headers") else None
                if not isinstance(next_url, str) or not next_url:
                    break
                # Handle relative redirects
                current_url = urllib.parse.urljoin(current_url, next_url)
                continue
            
            return resp

def _is_safe_ip(ip: str, allow_private: bool) -> bool:
    try:
        address = ipaddress.ip_address(ip)
    except ValueError:
        return False
        
    if allow_private:
        return True
        
    # Block list for SSRF prevention
    return not (
        address.is_private          # RFC1918 (10/8, 172.16/12, 192.168/16)
        or address.is_loopback      # 127.0.0.0/8, ::1
        or address.is_link_local    # 169.254.0.0/16, fe80::/10
        or address.is_multicast     # 224.0.0.0/4, ff00::/8
        or address.is_reserved      # IANA reserved
        or address.is_unspecified   # 0.0.0.0, ::
    )

def _ensure_safe_url(url: str, allow_private: bool) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ScuttleError(f"Scheme '{parsed.scheme}' is not allowed. Only http/https.")
    
    hostname = parsed.hostname
    if not hostname:
        raise ScuttleError("URL must include a hostname.")
        
    # 1. Block obviously local hostnames
    if hostname.lower() in {"localhost", "metadata.google.internal"} or hostname.endswith(".local") or hostname.endswith(".localhost"):
        if not allow_private:
            raise ScuttleError(f"Blocked host: '{hostname}' is a local or internal address.")

    # 2. Resolve DNS and check all returned IPs
    try:
        # getaddrinfo returns a list of 5-tuples. The 5th element is (address, port)
        addr_info = socket.getaddrinfo(hostname, parsed.port or (80 if parsed.scheme == "http" else 443))
    except socket.gaierror as e:
        raise ScuttleError(f"DNS resolution failed for '{hostname}': {e}")

    for entry in addr_info:
        ip = entry[4][0]
        if not _is_safe_ip(ip, allow_private):
            raise ScuttleError(f"Blocked host: '{hostname}' resolves to a restricted IP: {ip}")

@dataclass
class ArtifactDraft:
    """Draft of a research artifact before ingestion."""
    title: str
    content: str
    source: str
    type: str
    confidence: float = 1.0
    tags: List[str] = field(default_factory=list)
    raw_payload: Dict[str, Any] = field(default_factory=dict)

@dataclass
class IngestResult:
    """Result of an ingestion operation."""
    success: bool
    artifact_id: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class Connector(ABC):
    """Abstract base class for research data connectors."""
    
    @abstractmethod
    def can_handle(self, source: str) -> bool:
        """Return True if this connector can handle the given source (URL or ID)."""
        pass

    @abstractmethod
    def fetch(self, source: str, config: Optional[ScuttleConfig] = None) -> ArtifactDraft:
        """Fetch and parse content into an ArtifactDraft."""
        pass

class Scuttler(Connector):
    """Bridge for legacy Scuttler classes."""
    def can_handle(self, url: str) -> bool:
        return False

    def fetch(self, url: str, config: Optional[ScuttleConfig] = None) -> ArtifactDraft:
        config = _resolve_scuttle_config(config)
        data = _call_with_optional_config(self.scuttle, url, config)
        return ArtifactDraft(
            title=data["title"],
            content=data["content"],
            source=data["source"],
            type=data["type"],
            confidence=data["confidence"],
            tags=data.get("tags", "").split(",") if isinstance(data.get("tags"), str) else data.get("tags", [])
        )

    @abstractmethod
    def scuttle(self, url: str, config: Optional[ScuttleConfig] = None) -> Dict[str, Any]:
        """Legacy scuttle method returning a dict."""
        raise NotImplementedError

class RedditScuttler(Scuttler):
    def can_handle(self, url):
        return "reddit.com" in url or "redd.it" in url

    def scuttle(self, url, config: Optional[ScuttleConfig] = None):
        config = _resolve_scuttle_config(config)
        if "?" in url:
            url = url.split("?")[0]
        if not url.endswith(".json"):
            json_url = url.strip("/") + ".json"
        else:
            json_url = url

        headers = {"User-Agent": "ResearchVault/2.6.2"}
        try:
            with SafeSession(config) as session:
                resp = session.get(json_url, headers=headers)
                resp.raise_for_status()
                data = resp.json()
            
            post_data = data[0]['data']['children'][0]['data']
            title = post_data.get('title', 'No Title')
            body = post_data.get('selftext', '')
            score = post_data.get('score', 0)
            subreddit = post_data.get('subreddit', 'unknown')
            content = f"Subreddit: r/{subreddit}\nScore: {score}\nBody: {body}\n"
            
            try:
                comments = data[1]['data']['children']
                if comments:
                    top_comment = comments[0]['data'].get('body', '')
                    if top_comment:
                        content += f"\n--- Top Comment ---\n{top_comment}"
            except (IndexError, KeyError):
                pass

            return {
                "source": f"reddit/r/{subreddit}",
                "type": "SCUTTLE_REDDIT",
                "title": title,
                "content": content,
                "confidence": 1.0 if score > 10 else 0.8,
                "tags": f"reddit,{subreddit}"
            }
        except Exception as e:
            raise ScuttleError(f"Reddit scuttle failed: {e}")

class MoltbookScuttler(Scuttler):
    def can_handle(self, url):
        return "moltbook" in url

    def scuttle(self, url, config: Optional[ScuttleConfig] = None):
        return {
            "source": "moltbook",
            "type": "SCUTTLE_MOLTBOOK",
            "title": "State Management in Autonomous Agents",
            "content": "Modular state management is the missing piece.",
            "confidence": 0.55,
            "tags": "moltbook,agents,state,unverified"
        }

class WebScuttler(Scuttler):
    def can_handle(self, url):
        return True

    def scuttle(self, url, config: Optional[ScuttleConfig] = None):
        config = _resolve_scuttle_config(config)
        headers = {"User-Agent": "ResearchVault/2.6.2"}
        try:
            with SafeSession(config) as session:
                resp = session.get(url, headers=headers)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, 'html.parser')
            
            title = soup.title.string if soup.title else url
            paragraphs = soup.find_all('p')
            text_content = "\n\n".join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 50])
            if not text_content:
                text_content = soup.get_text()[:2000]

            return {
                "source": "web",
                "type": "SCUTTLE_WEB",
                "title": title.strip(),
                "content": text_content[:5000],
                "confidence": 0.7,
                "tags": "web,scraping"
            }
        except Exception as e:
            raise ScuttleError(f"Web scuttle failed: {e}")

class GrokipediaConnector(Connector):
    def can_handle(self, source: str) -> bool:
        return "grokipedia.com" in source or source.startswith("grokipedia://")

    def fetch(self, source: str, config: Optional[ScuttleConfig] = None) -> ArtifactDraft:
        config = _resolve_scuttle_config(config)
        if "/" in source:
            slug = source.split("/")[-1]
        else:
            slug = source
            
        api_url = f"https://grokipedia-api.com/page/{slug}"
        try:
            with SafeSession(config) as session:
                resp = session.get(api_url)
                resp.raise_for_status()
                data = resp.json()
            
            return ArtifactDraft(
                title=data.get("title", slug),
                content=data.get("content_text", ""),
                source="grokipedia",
                type="KNOWLEDGE_BASE",
                confidence=0.95,
                tags=["grokipedia", "knowledge-base"],
                raw_payload=data
            )
        except Exception as e:
            raise ScuttleError(f"Grokipedia fetch failed: {e}")

class YouTubeConnector(Connector):
    def can_handle(self, source: str) -> bool:
        return "youtube.com" in source or "youtu.be" in source

    def fetch(self, source: str, config: Optional[ScuttleConfig] = None) -> ArtifactDraft:
        config = _resolve_scuttle_config(config)
        headers = {"User-Agent": "ResearchVault/2.6.2"}
        try:
            with SafeSession(config) as session:
                resp = session.get(source, headers=headers)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, 'html.parser')
            title = soup.title.string.replace(" - YouTube", "") if soup.title else source
            desc = ""
            desc_tag = soup.find("meta", property="og:description") or soup.find("meta", name="description")
            if desc_tag: desc = desc_tag.get("content", "")
            channel = ""
            channel_tag = soup.find("link", itemprop="name") or soup.find("meta", property="og:video:tag")
            if channel_tag: channel = channel_tag.get("content", "")
            content = f"Channel: {channel}\n\nDescription:\n{desc}"
            
            return ArtifactDraft(
                title=title.strip(),
                content=content,
                source="youtube",
                type="VIDEO_METADATA",
                confidence=0.9,
                tags=["youtube", "video"],
                raw_payload={"channel": channel, "description": desc}
            )
        except Exception as e:
            raise ScuttleError(f"YouTube fetch failed: {e}")

def get_scuttler(url):
    scuttlers = [RedditScuttler(), MoltbookScuttler(), GrokipediaConnector(), YouTubeConnector(), WebScuttler()]
    for s in scuttlers:
        if s.can_handle(url):
            return s
    return WebScuttler()
