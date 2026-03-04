from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

TRACKING_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "gclid",
    "fbclid",
    "mc_cid",
    "mc_eid",
}


def canonicalize(url: str) -> str:
    raw = (url or "").strip()
    if not raw:
        return ""

    # urlparse("example.com") => path='example.com', netloc=''
    # şema yoksa host olarak yorumla.
    if "://" not in raw:
        raw = "https://" + raw

    p = urlparse(raw)
    scheme = p.scheme.lower() if p.scheme else "https"
    netloc = p.netloc.lower()

    if netloc.endswith(":80") and scheme == "http":
        netloc = netloc[:-3]
    if netloc.endswith(":443") and scheme == "https":
        netloc = netloc[:-4]

    path = p.path or "/"
    if path != "/" and path.endswith("/"):
        path = path[:-1]

    q = [
        (k, v)
        for k, v in parse_qsl(p.query, keep_blank_values=True)
        if k.lower() not in TRACKING_PARAMS
    ]
    query = urlencode(sorted(q))

    return urlunparse((scheme, netloc, path, "", query, ""))
