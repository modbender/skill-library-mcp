from __future__ import annotations

import unittest
from unittest.mock import MagicMock

from free_search.providers import (
    AuthError,
    BraveProvider,
    DuckDuckGoInstantProvider,
    DuckDuckGoProvider,
    ParseError,
    SearchApiProvider,
    SerperProvider,
    TavilyProvider,
)


class TestProviders(unittest.TestCase):
    def test_brave_missing_api_key(self) -> None:
        provider = BraveProvider(config={})
        with self.assertRaises(AuthError):
            provider.search("milan", max_results=3)

    def test_brave_parses_json_results(self) -> None:
        session = MagicMock()
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "web": {
                "results": [
                    {"title": "A", "url": "https://a", "description": "desc a"},
                    {"title": "", "url": "https://b", "description": "skip"},
                ]
            }
        }
        session.get.return_value = response

        provider = BraveProvider(config={"api_key": "token"}, session=session)
        rows = provider.search("milan", max_results=5)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].title, "A")
        self.assertEqual(rows[0].url, "https://a")

    def test_brave_retries_with_prefix_case_swap_after_auth_failure(self) -> None:
        session = MagicMock()
        bad = MagicMock()
        bad.status_code = 401
        bad.json.return_value = {"message": "invalid token"}
        ok = MagicMock()
        ok.status_code = 200
        ok.json.return_value = {
            "web": {
                "results": [
                    {"title": "X", "url": "https://x", "description": "desc x"},
                ]
            }
        }
        session.get.side_effect = [bad, ok]

        provider = BraveProvider(config={"api_key": "BSAabc123"}, session=session)
        rows = provider.search("milan", max_results=3)

        self.assertEqual(len(rows), 1)
        self.assertEqual(session.get.call_count, 2)
        first_headers = session.get.call_args_list[0].kwargs["headers"]
        second_headers = session.get.call_args_list[1].kwargs["headers"]
        self.assertEqual(first_headers["X-Subscription-Token"], "BSAabc123")
        self.assertEqual(second_headers["X-Subscription-Token"], "BSaabc123")

    def test_tavily_parses_results(self) -> None:
        session = MagicMock()
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "results": [
                {"title": "T1", "url": "https://t1", "content": "ct1"},
            ]
        }
        session.post.return_value = response

        provider = TavilyProvider(config={"api_key": "token"}, session=session)
        rows = provider.search("milan", max_results=2)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].source, "tavily")

    def test_serper_non_json_raises_parse_error(self) -> None:
        session = MagicMock()
        response = MagicMock()
        response.status_code = 200
        response.json.side_effect = ValueError("invalid json")
        session.post.return_value = response

        provider = SerperProvider(config={"api_key": "token"}, session=session)
        with self.assertRaises(ParseError):
            provider.search("milan", max_results=5)

    def test_serper_parses_organic_results(self) -> None:
        session = MagicMock()
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "organic": [
                {"title": "S1", "link": "https://s1", "snippet": "snippet"},
            ]
        }
        session.post.return_value = response

        provider = SerperProvider(config={"api_key": "token"}, session=session)
        rows = provider.search("milan", max_results=2)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].url, "https://s1")

    def test_duckduckgo_html_parse(self) -> None:
        session = MagicMock()
        response = MagicMock()
        response.status_code = 200
        response.text = """
        <html><body>
          <div class=\"result\">
            <a class=\"result__a\" href=\"https://x\">X title</a>
            <a class=\"result__snippet\">X snippet</a>
          </div>
        </body></html>
        """
        session.get.return_value = response

        provider = DuckDuckGoProvider(config={}, session=session)
        rows = provider.search("milan", max_results=2)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].title, "X title")

    def test_duckduckgo_html_parse_modern_layout_and_unwrap_redirect(self) -> None:
        session = MagicMock()
        response = MagicMock()
        response.status_code = 200
        response.text = """
        <html><body>
          <li data-layout="organic">
            <h2>
              <a data-testid="result-title-a" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com%2Fpost">
                Modern title
              </a>
            </h2>
            <div data-result="snippet">Modern snippet</div>
          </li>
        </body></html>
        """
        session.get.return_value = response

        provider = DuckDuckGoProvider(config={}, session=session)
        rows = provider.search("milan", max_results=2)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].title, "Modern title")
        self.assertEqual(rows[0].url, "https://example.com/post")
        self.assertEqual(rows[0].snippet, "Modern snippet")

    def test_duckduckgo_instant_parses_nested_topics_and_dedupes(self) -> None:
        session = MagicMock()
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "AbstractText": "Milan - City in Italy",
            "AbstractURL": "https://example.com/milan",
            "RelatedTopics": [
                {
                    "Topics": [
                        {"Text": "Milan Cathedral - Landmark", "FirstURL": "https://example.com/duomo"},
                        {"Text": "Milan Cathedral - Landmark", "FirstURL": "https://example.com/duomo"},
                    ]
                }
            ],
        }
        session.get.return_value = response

        provider = DuckDuckGoInstantProvider(config={}, session=session)
        rows = provider.search("milan", max_results=5)

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0].url, "https://example.com/milan")
        self.assertEqual(rows[1].url, "https://example.com/duomo")

    def test_searchapi_parses_organic_results(self) -> None:
        session = MagicMock()
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "organic_results": [
                {"title": "R1", "link": "https://r1", "snippet": "snip"},
            ]
        }
        session.get.return_value = response

        provider = SearchApiProvider(config={"api_key": "token"}, session=session)
        rows = provider.search("milan", max_results=3)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].title, "R1")


if __name__ == "__main__":
    unittest.main()
