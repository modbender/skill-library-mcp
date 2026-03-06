from urllib.parse import urlparse, parse_qs, unquote, urljoin

SEARCH_DOMAINS = {
    "duckduckgo.com",
    "www.bing.com",
    "search.yahoo.com",
    "search.brave.com",
}


def _extract_real_link(href: str):
    if not href:
        return None
    if href.startswith("http"):
        return href
    if href.startswith("//"):
        return "https:" + href
    # duckduckgo redirect links: /l/?uddg=...
    if "uddg=" in href:
        parsed = urlparse(href)
        qs = parse_qs(parsed.query)
        if "uddg" in qs and qs["uddg"]:
            return unquote(qs["uddg"][0])
    return None


def extract(url: str, html: str, tree):
    links = []
    titles = []

    for a in tree.css("a[href]")[:200]:
        href = (a.attributes.get("href") or "").strip()
        real = _extract_real_link(href)
        if not real:
            if href.startswith("/"):
                real = urljoin(url, href)
            else:
                continue
        if not real.startswith("http"):
            continue

        host = (urlparse(real).hostname or "").lower()
        if any(host.endswith(d) for d in SEARCH_DOMAINS):
            continue

        text = a.text(strip=True)
        if text:
            titles.append(text)
        links.append(real)

    # dedup
    dedup = []
    seen = set()
    for l in links:
        if l not in seen:
            seen.add(l)
            dedup.append(l)

    title_node = tree.css_first("title")
    page_title = title_node.text(strip=True) if title_node else None

    return {
        "title": page_title,
        "text": "\n".join(titles[:30]),
        "links": dedup[:120],
    }
