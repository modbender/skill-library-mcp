"""Multi-layer cascade fetcher: OAuth -> Tor -> Stealth HTTP -> Browser -> PullPush.

Tries each layer in order, falling through on failure.
Caches which layers are working to skip known-broken ones for 1 hour.
"""

import sys
import time
from typing import Any, Dict, List, Optional

from . import reddit_auth
from . import tor_client
from . import stealth_http
from . import browser_stealth
from . import pullpush_client

LAYER_CACHE_TTL = 3600
_layer_failures: Dict[str, float] = {}


def _is_healthy(name: str) -> bool:
    failed_at = _layer_failures.get(name)
    if failed_at is None:
        return True
    return (time.time() - failed_at) > LAYER_CACHE_TTL


def _mark_failed(name: str) -> None:
    _layer_failures[name] = time.time()


def _mark_ok(name: str) -> None:
    _layer_failures.pop(name, None)


def _log(msg: str) -> None:
    print(f"[cascade] {msg}", file=sys.stderr)


def _try_layer(name: str, module: Any, fn_name: str, *args: Any, **kw: Any) -> Optional[Any]:
    if not _is_healthy(name):
        return None
    fn = getattr(module, fn_name, None)
    if fn is None:
        return None
    try:
        result = fn(*args, **kw)
        _mark_ok(name)
        _log(f"{name}/{fn_name} OK")
        return result
    except Exception as e:
        _mark_failed(name)
        _log(f"{name}/{fn_name} failed: {e}")
        return None


def _build_layer_chain(fn_name: str) -> List[tuple]:
    chain = []
    if reddit_auth.is_configured():
        oauth_fn = _OAUTH_MAP.get(fn_name, fn_name)
        chain.append(("oauth", reddit_auth, oauth_fn))
    if tor_client.is_available():
        chain.append(("tor", tor_client, fn_name))
    chain.append(("stealth_http", stealth_http, fn_name))
    if browser_stealth.is_available():
        chain.append(("browser", browser_stealth, fn_name))
    pp_fn = _PULLPUSH_MAP.get(fn_name)
    if pp_fn:
        chain.append(("pullpush", pullpush_client, pp_fn))
    return chain


def _cascade(fn_name: str, *args: Any, **kw: Any) -> Any:
    chain = _build_layer_chain(fn_name)
    for name, module, mapped_fn in chain:
        result = _try_layer(name, module, mapped_fn, *args, **kw)
        if result is not None:
            return result
    raise RuntimeError(f"All layers failed for {fn_name}({args})")


_OAUTH_MAP = {
    "fetch_about": "fetch_about",
    "fetch_posts": "fetch_posts",
    "fetch_comments_raw": "fetch_comments",
    "search_posts": "search",
    "fetch_user_posts": "fetch_user",
}

_PULLPUSH_MAP = {
    "fetch_posts": "fetch_posts",
    "search_posts": "search_posts",
    "fetch_user_posts": "fetch_user_posts",
}


def fetch_about(subreddit: str) -> Dict[str, Any]:
    return _cascade("fetch_about", subreddit)


def fetch_posts(subreddit: str, sort: str = "hot", timeframe: str = "week", limit: int = 25) -> List[Dict]:
    return _cascade("fetch_posts", subreddit, sort, timeframe, limit)


def fetch_comments_raw(post_url: str, depth: int = 8, limit: int = 200) -> Any:
    return _cascade("fetch_comments_raw", post_url, depth, limit)


def search_posts(subreddit: str, query: str, sort: str = "relevance", timeframe: str = "all", limit: int = 25) -> List[Dict]:
    return _cascade("search_posts", subreddit, query, sort, timeframe, limit)


def fetch_user_posts(username: str, limit: int = 25) -> List[Dict]:
    return _cascade("fetch_user_posts", username, limit)


def health_check() -> Dict[str, Any]:
    return {
        "oauth": {"configured": reddit_auth.is_configured(), "healthy": _is_healthy("oauth")},
        "tor": {"available": tor_client.is_available(), "healthy": _is_healthy("tor")},
        "stealth_http": {"healthy": _is_healthy("stealth_http")},
        "browser": {"available": browser_stealth.is_available(), "healthy": _is_healthy("browser")},
        "pullpush": {"available": True, "healthy": _is_healthy("pullpush")},
    }
