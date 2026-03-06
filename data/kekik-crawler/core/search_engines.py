from urllib.parse import quote_plus


def build_search_urls(query: str):
    q = quote_plus(query)
    return {
        "duckduckgo": f"https://duckduckgo.com/html/?q={q}",
        "bing": f"https://www.bing.com/search?q={q}",
        "yahoo": f"https://search.yahoo.com/search?p={q}",
        "brave_web": f"https://search.brave.com/search?q={q}",
    }


def build_multi_query_urls(queries):
    urls = []
    for q in queries:
        urls.extend(build_search_urls(q).values())
    seen = set()
    out = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out
