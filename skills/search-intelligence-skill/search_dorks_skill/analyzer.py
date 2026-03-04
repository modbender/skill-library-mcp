"""
Result analyzer: scores, deduplicates, ranks results, and generates
refined query suggestions. The intelligence layer over raw search results.
"""

from __future__ import annotations
import re
import hashlib
from urllib.parse import urlparse
from .models import SearchResult, SearchIntent
from .config import CREDIBILITY_BOOSTS, CREDIBILITY_PENALTIES


class ResultAnalyzer:
    """Score, deduplicate, rank, and analyze search results."""

    def analyze(
        self,
        results: list[SearchResult],
        intent: SearchIntent,
    ) -> list[SearchResult]:
        """Full analysis pipeline: deduplicate → score → sort."""
        results = self.deduplicate(results)
        results = self.score_all(results, intent)
        results.sort(key=lambda r: r.relevance, reverse=True)
        return results

    def deduplicate(self, results: list[SearchResult]) -> list[SearchResult]:
        """Remove duplicate results based on URL normalization."""
        seen_urls: dict[str, SearchResult] = {}
        seen_content: set[str] = set()

        for r in results:
            norm_url = self._normalize_url(r.url)
            content_hash = self._content_hash(r.title, r.snippet)

            if norm_url in seen_urls:
                # Merge engine info into existing result
                existing = seen_urls[norm_url]
                for eng in r.engines:
                    if eng not in existing.engines:
                        existing.engines.append(eng)
                existing.positions.extend(r.positions)
                existing.score = max(existing.score, r.score)
                continue

            if content_hash in seen_content:
                continue

            seen_urls[norm_url] = r
            seen_content.add(content_hash)

        return list(seen_urls.values())

    def score_all(
        self,
        results: list[SearchResult],
        intent: SearchIntent,
    ) -> list[SearchResult]:
        """Compute relevance scores for all results."""
        for r in results:
            r.relevance = self._compute_relevance(r, intent)
        return results

    def _compute_relevance(self, result: SearchResult, intent: SearchIntent) -> float:
        """Multi-signal relevance scoring."""
        score = 0.0

        # 1. Base SearXNG score (normalized)
        score += min(result.score / 10.0, 1.0) * 2.0

        # 2. Keyword match scoring
        kw_score = self._keyword_relevance(result, intent)
        score += kw_score * 3.0

        # 3. Multi-engine agreement bonus
        engine_count = len(result.engines)
        score += min(engine_count * 0.5, 2.0)

        # 4. Position scoring (lower position = better)
        if result.positions:
            avg_pos = sum(result.positions) / len(result.positions)
            score += max(0, (20 - avg_pos) / 20) * 1.5

        # 5. Credibility scoring
        score += self._credibility_score(result)

        # 6. Content quality scoring
        score += self._content_quality_score(result)

        # 7. Intent-specific boosts
        score += self._intent_specific_score(result, intent)

        # Normalize to 0-10 range
        return min(max(score, 0.0), 10.0)

    def _keyword_relevance(self, result: SearchResult, intent: SearchIntent) -> float:
        """Score how well result matches intent keywords."""
        if not intent.keywords:
            return 0.5

        text = f"{result.title} {result.snippet}".lower()
        matches = 0
        total = len(intent.keywords)

        for kw in intent.keywords:
            kw_lower = kw.lower()
            if kw_lower in text:
                matches += 1
                # Title match is worth more
                if kw_lower in result.title.lower():
                    matches += 0.5

        return matches / max(total, 1)

    def _credibility_score(self, result: SearchResult) -> float:
        """Score based on source credibility."""
        url = result.url.lower()
        parsed = urlparse(url)
        domain = parsed.netloc

        boost = 0.0
        for pattern, value in CREDIBILITY_BOOSTS.items():
            if pattern in domain or domain.endswith(pattern):
                boost = max(boost, value - 1.0)  # Convert multiplier to additive

        # Check for penalty signals in snippet
        text = f"{result.title} {result.snippet}".lower()
        penalty = 0.0
        for pattern, value in CREDIBILITY_PENALTIES.items():
            if pattern in text:
                penalty = max(penalty, 1.0 - value)

        return boost - penalty

    def _content_quality_score(self, result: SearchResult) -> float:
        """Score based on snippet quality indicators."""
        score = 0.0
        snippet = result.snippet

        # Longer snippets usually mean more content
        if len(snippet) > 200:
            score += 0.3
        elif len(snippet) > 100:
            score += 0.2
        elif len(snippet) < 30:
            score -= 0.3

        # Has title
        if result.title and len(result.title) > 10:
            score += 0.2

        # URL quality
        url = result.url
        if url.startswith("https://"):
            score += 0.1
        if len(url) < 150:  # Not an excessively long URL
            score += 0.1

        return score

    def _intent_specific_score(self, result: SearchResult, intent: SearchIntent) -> float:
        """Bonus scores based on intent category."""
        url = result.url.lower()
        text = f"{result.title} {result.snippet}".lower()
        category = intent.category.value
        score = 0.0

        if category == "academic":
            academic_domains = ["arxiv.org", "scholar.google", "pubmed", "doi.org",
                              "researchgate.net", "academia.edu", ".edu"]
            if any(d in url for d in academic_domains):
                score += 1.0
            if any(w in text for w in ["abstract", "doi", "et al", "journal", "proceedings"]):
                score += 0.5

        elif category == "code":
            code_domains = ["github.com", "gitlab.com", "stackoverflow.com",
                          "npmjs.com", "pypi.org", "docs."]
            if any(d in url for d in code_domains):
                score += 1.0

        elif category == "security":
            sec_domains = ["exploit-db.com", "cve.mitre.org", "nvd.nist.gov",
                         "hackerone.com", "portswigger.net"]
            if any(d in url for d in sec_domains):
                score += 1.0
            if any(w in text for w in ["cve-", "vulnerability", "exploit", "advisory"]):
                score += 0.5

        elif category == "osint":
            # Prefer results with contact info or personal data indicators
            if any(w in text for w in ["email", "phone", "linkedin", "profile", "bio"]):
                score += 0.5

        elif category == "news":
            news_domains = ["reuters.com", "apnews.com", "bbc.com", "cnn.com",
                          "nytimes.com", "theguardian.com"]
            if any(d in url for d in news_domains):
                score += 1.0

        elif category == "seo":
            # Check for SEO-relevant content
            if any(w in text for w in ["sitemap", "robots", "canonical", "indexed", "crawl"]):
                score += 0.5

        return score

    def generate_refinements(
        self,
        results: list[SearchResult],
        intent: SearchIntent,
    ) -> list[str]:
        """Analyze result gaps and suggest refined queries."""
        suggestions = []
        keyword = " ".join(intent.keywords) if intent.keywords else ""

        if not results:
            # No results — suggest broader queries
            if keyword:
                suggestions.append(keyword)  # Try without operators
                if len(keyword.split()) > 3:
                    # Shorten query
                    words = keyword.split()
                    suggestions.append(" ".join(words[:3]))
                suggestions.append(f'"{keyword}"')
            return suggestions

        if len(results) < 5:
            # Few results — suggest alternatives
            if intent.entities.get("domain"):
                # Try without site restriction
                suggestions.append(f'"{keyword}"')
                suggestions.append(f'{keyword} {intent.entities["domain"]}')
            if keyword:
                # Try synonym/related terms
                suggestions.append(f'"{keyword}" OR similar OR related')

        # Suggest time-restricted variants if not already used
        if not intent.time_range and keyword:
            suggestions.append(f'{keyword} (recent or {intent.time_range or "2024"})')

        # Suggest filetype variants
        if intent.category.value in ("academic", "files") and keyword:
            for ft in ["pdf", "doc", "csv"]:
                suggestions.append(f'{keyword} filetype:{ft}')

        # Extract potential new keywords from top results
        if results:
            new_terms = self._extract_new_terms(results[:5], intent)
            for term in new_terms[:3]:
                if keyword:
                    suggestions.append(f'{keyword} "{term}"')
                else:
                    suggestions.append(f'"{term}"')

        return suggestions[:10]  # Cap at 10 suggestions

    def summarize(self, results: list[SearchResult], intent: SearchIntent) -> str:
        """Generate a brief text summary of the results."""
        if not results:
            return "No results found. Consider broadening your search or using different keywords."

        n = len(results)
        top = results[:3]
        engines = set()
        for r in results:
            engines.update(r.engines)

        domains = set()
        for r in results[:10]:
            parsed = urlparse(r.url)
            domains.add(parsed.netloc)

        summary_parts = [
            f"Found {n} results across {len(engines)} engines.",
            f"Top sources: {', '.join(list(domains)[:5])}.",
        ]

        if top:
            summary_parts.append(f"Best match: \"{top[0].title}\" ({top[0].url})")

        avg_relevance = sum(r.relevance for r in results) / n if n else 0
        if avg_relevance > 7:
            summary_parts.append("High-quality results — strong keyword matches.")
        elif avg_relevance > 4:
            summary_parts.append("Moderate quality — consider refining your query.")
        else:
            summary_parts.append("Low relevance scores — try different keywords or operators.")

        return " ".join(summary_parts)

    def _extract_new_terms(
        self, results: list[SearchResult], intent: SearchIntent
    ) -> list[str]:
        """Extract potentially useful new search terms from results."""
        existing = set(kw.lower() for kw in intent.keywords)
        all_text = " ".join(f"{r.title} {r.snippet}" for r in results)

        # Find capitalized phrases (potential entities/terms)
        candidates = re.findall(r'\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\b', all_text)

        # Filter: not in original keywords, not too short/long, appears multiple times
        term_counts: dict[str, int] = {}
        for term in candidates:
            if term.lower() not in existing and 3 < len(term) < 40:
                term_counts[term] = term_counts.get(term, 0) + 1

        # Return terms that appear more than once
        frequent = sorted(term_counts.items(), key=lambda x: x[1], reverse=True)
        return [term for term, count in frequent if count > 1]

    @staticmethod
    def _normalize_url(url: str) -> str:
        parsed = urlparse(url)
        # Normalize: lowercase host, remove trailing slash, remove fragments
        normalized = f"{parsed.scheme}://{parsed.netloc.lower()}{parsed.path.rstrip('/')}"
        if parsed.query:
            normalized += f"?{parsed.query}"
        return normalized

    @staticmethod
    def _content_hash(title: str, snippet: str) -> str:
        content = f"{title.lower().strip()}|{snippet.lower().strip()[:200]}"
        return hashlib.md5(content.encode()).hexdigest()