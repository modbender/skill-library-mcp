from core.search_engines import build_multi_query_urls


def test_multi_query_urls_unique():
    urls = build_multi_query_urls(["keyiflerolsun", "keyiflerolsun"])
    assert len(urls) == len(set(urls))
    assert any("duckduckgo" in u for u in urls)
    assert any("bing.com" in u for u in urls)
