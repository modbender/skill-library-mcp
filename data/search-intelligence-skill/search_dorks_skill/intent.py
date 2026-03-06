"""
Intent parser: analyzes natural-language search queries to determine
category, subcategory, entities, constraints, and optimal search depth.
Uses keyword scoring, regex entity extraction, and heuristic rules.
No external NLP dependencies required.
"""

from __future__ import annotations
import re
from typing import Any
from .models import SearchIntent, IntentCategory, Depth
from .config import INTENT_SIGNALS


# ─── Entity extraction patterns ──────────────────────────────────────────────

ENTITY_PATTERNS: dict[str, re.Pattern] = {
    "domain": re.compile(
        r'\b(?:site:|on\s+|for\s+|of\s+)?'
        r'((?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)'
        r'+[a-zA-Z]{2,})\b'
    ),
    "email": re.compile(
        r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'
    ),
    "ip_address": re.compile(
        r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b'
    ),
    "phone": re.compile(
        r'(\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})'
    ),
    "cve": re.compile(
        r'\b(CVE-\d{4}-\d{4,})\b', re.IGNORECASE
    ),
    "username": re.compile(
        r'(?:@|user(?:name)?[:\s]+)([a-zA-Z0-9_.-]{3,30})\b'
    ),
    "filetype": re.compile(
        r'\b(?:filetype|file\s*type|format)[:\s]+(\w+)\b', re.IGNORECASE
    ),
    "year": re.compile(
        r'\b(20[12]\d)\b'
    ),
    "quoted_name": re.compile(
        r'"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)"'
    ),
}

# Subcategory detection patterns
SUBCATEGORY_PATTERNS: dict[str, dict[str, list[str]]] = {
    "security": {
        "exposed_files": ["env file", ".env", "exposed file", "config file", "backup file", "log file"],
        "directory_listing": ["directory listing", "index of", "open directory"],
        "admin_panels": ["admin panel", "admin page", "login page", "dashboard", "wp-admin", "phpmyadmin"],
        "sensitive_data": ["password", "credential", "private key", "api key", "secret key", "aws key"],
        "exposed_apis": ["api", "swagger", "graphql", "endpoint", "api-docs"],
        "subdomains": ["subdomain", "sub domain"],
        "git_exposed": [".git", "git exposed", "git repository", "svn", ".svn"],
        "technology_stack": ["technology", "tech stack", "powered by", "framework", "cms"],
    },
    "seo": {
        "indexation": ["indexed", "indexation", "index", "crawl"],
        "backlinks": ["backlink", "backlinks", "link", "referring domain"],
        "competitors": ["competitor", "alternative", "similar site", "related"],
        "content_audit": ["content", "keyword", "page"],
        "technical_seo": ["sitemap", "robots.txt", "canonical", "noindex", "hreflang", "schema"],
    },
    "osint": {
        "person": ["person", "who is", "find person", "investigate person"],
        "email": ["email", "mail"],
        "username": ["username", "user", "handle", "account"],
        "domain_recon": ["domain", "site", "website", "whois", "dns"],
        "company": ["company", "organization", "business", "startup", "corporation"],
        "phone": ["phone", "telephone", "number", "call"],
        "ip_address": ["ip", "ip address", "server"],
    },
    "academic": {
        "papers": ["paper", "research", "study", "journal", "article", "publication"],
        "datasets": ["dataset", "data", "csv", "benchmark"],
        "authors": ["author", "researcher", "professor", "scientist"],
    },
    "code": {
        "repositories": ["repo", "repository", "project", "source code"],
        "packages": ["package", "library", "module", "dependency", "npm", "pip"],
        "documentation": ["documentation", "docs", "api reference", "readme"],
        "issues_bugs": ["bug", "issue", "error", "fix", "solution", "workaround"],
    },
    "files": {
        "documents": ["document", "pdf", "doc", "report", "whitepaper", "ebook"],
        "data": ["data", "csv", "json", "xml", "sql", "spreadsheet"],
        "media": ["image", "video", "audio", "music", "photo"],
        "archives": ["archive", "zip", "rar", "compressed"],
        "config": ["config", "configuration", "yaml", "toml", "ini"],
    },
}


class IntentParser:
    """Analyze a natural-language query and return a structured SearchIntent."""

    def parse(self, query: str, depth: Depth | str = Depth.STANDARD) -> SearchIntent:
        if isinstance(depth, str):
            depth = Depth(depth)

        entities = self._extract_entities(query)
        category = self._classify(query, entities)
        subcategory = self._detect_subcategory(query, category)
        keywords = self._extract_keywords(query, entities)
        constraints = self._extract_constraints(query)
        time_range = self._detect_time_range(query)
        confidence = self._compute_confidence(query, category)

        return SearchIntent(
            category=IntentCategory(category),
            subcategory=subcategory,
            entities=entities,
            keywords=keywords,
            constraints=constraints,
            time_range=time_range,
            depth=depth,
            confidence=confidence,
        )

    def _extract_entities(self, query: str) -> dict[str, Any]:
        entities: dict[str, Any] = {}

        # Extract email first (before domain, since email contains domain)
        email_match = ENTITY_PATTERNS["email"].search(query)
        if email_match:
            email = email_match.group(1)
            entities["email"] = email
            entities["email_domain"] = email.split("@")[1]

        # Extract domain (skip if it's part of a matched email)
        for m in ENTITY_PATTERNS["domain"].finditer(query):
            domain = m.group(1).lower()
            # Skip common non-domain patterns and email domains already captured
            if domain in ("e.g", "i.e", "etc.com"):
                continue
            if "email" in entities and domain == entities.get("email_domain"):
                continue
            # Skip if it's a generic word that matches domain pattern
            if len(domain.split(".")) >= 2 and len(domain) > 4:
                entities["domain"] = domain
                break

        # IP address
        ip_match = ENTITY_PATTERNS["ip_address"].search(query)
        if ip_match:
            entities["ip"] = ip_match.group(1)

        # Phone
        phone_match = ENTITY_PATTERNS["phone"].search(query)
        if phone_match:
            entities["phone"] = phone_match.group(1)

        # CVE
        cve_match = ENTITY_PATTERNS["cve"].search(query)
        if cve_match:
            entities["cve"] = cve_match.group(1).upper()

        # Username
        user_match = ENTITY_PATTERNS["username"].search(query)
        if user_match:
            entities["username"] = user_match.group(1)

        # Filetype
        ft_match = ENTITY_PATTERNS["filetype"].search(query)
        if ft_match:
            entities["filetype"] = ft_match.group(1).lower()

        # Year
        year_match = ENTITY_PATTERNS["year"].search(query)
        if year_match:
            entities["year"] = year_match.group(1)

        # Quoted name (likely a person)
        name_match = ENTITY_PATTERNS["quoted_name"].search(query)
        if name_match:
            entities["name"] = name_match.group(1)
        else:
            # Heuristic: look for capitalized name patterns without quotes
            name_pat = re.findall(r'\b([A-Z][a-z]{2,}\s+[A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,})?)\b', query)
            if name_pat:
                entities["name"] = name_pat[0]

        return entities

    def _classify(self, query: str, entities: dict[str, Any]) -> str:
        """Score query against each intent category and return best match."""
        query_lower = query.lower()
        scores: dict[str, float] = {}

        for category, info in INTENT_SIGNALS.items():
            score = 0.0
            keywords = info.get("_keywords", [])
            for kw in keywords:
                if kw in query_lower:
                    score += info.get("keywords", 1.0)
                    # Exact word boundary match gets extra credit
                    if re.search(r'\b' + re.escape(kw) + r'\b', query_lower):
                        score += 0.5
            scores[category] = score

        # Entity-based boosts
        if "email" in entities:
            scores["osint"] = scores.get("osint", 0) + 3.0
        if "ip" in entities:
            scores["osint"] = scores.get("osint", 0) + 2.0
            scores["security"] = scores.get("security", 0) + 2.0
        if "cve" in entities:
            scores["security"] = scores.get("security", 0) + 5.0
        if "phone" in entities:
            scores["osint"] = scores.get("osint", 0) + 3.0
        if "name" in entities and not entities.get("domain"):
            scores["osint"] = scores.get("osint", 0) + 2.0
        if "domain" in entities:
            # Domain + security keywords → security
            if scores.get("security", 0) > 0:
                scores["security"] += 2.0
            # Domain + seo keywords → seo
            if scores.get("seo", 0) > 0:
                scores["seo"] += 2.0

        if not scores or max(scores.values()) == 0:
            return "general"

        return max(scores, key=scores.get)

    def _detect_subcategory(self, query: str, category: str) -> str:
        query_lower = query.lower()
        patterns = SUBCATEGORY_PATTERNS.get(category, {})

        best_sub = "general"
        best_score = 0

        for sub, triggers in patterns.items():
            score = sum(1 for t in triggers if t in query_lower)
            if score > best_score:
                best_score = score
                best_sub = sub

        return best_sub

    def _extract_keywords(self, query: str, entities: dict) -> list[str]:
        """Extract meaningful search keywords from the query."""
        # Remove entity values from query to get remaining keywords
        cleaned = query
        for val in entities.values():
            if isinstance(val, str):
                cleaned = cleaned.replace(val, "")

        # Remove common stop/instruction words
        stop_words = {
            "find", "search", "look", "get", "show", "list", "give",
            "me", "the", "a", "an", "for", "on", "in", "of", "to",
            "all", "any", "with", "about", "from", "that", "this",
            "what", "where", "how", "who", "which", "please", "can",
            "you", "i", "want", "need", "do", "does", "is", "are",
            "was", "were", "be", "been", "being", "have", "has",
            "had", "will", "would", "could", "should", "may", "might",
            "using", "use", "and", "or", "not", "but", "if", "then",
        }

        words = re.findall(r'\b[a-zA-Z]{2,}\b', cleaned.lower())
        keywords = [w for w in words if w not in stop_words]

        # Preserve quoted phrases from original query
        quoted = re.findall(r'"([^"]+)"', query)
        keywords = quoted + keywords

        # Deduplicate while preserving order
        seen = set()
        unique = []
        for k in keywords:
            if k.lower() not in seen:
                seen.add(k.lower())
                unique.append(k)

        return unique

    def _extract_constraints(self, query: str) -> dict[str, Any]:
        constraints = {}
        query_lower = query.lower()

        # Language constraints
        lang_map = {
            "in english": "en", "in spanish": "es", "in french": "fr",
            "in german": "de", "in chinese": "zh", "in japanese": "ja",
            "in russian": "ru", "in portuguese": "pt", "in arabic": "ar",
        }
        for phrase, code in lang_map.items():
            if phrase in query_lower:
                constraints["language"] = code
                break

        # Result count hints
        if any(w in query_lower for w in ["all", "everything", "exhaustive", "comprehensive"]):
            constraints["exhaustive"] = True
        if any(w in query_lower for w in ["top", "best", "first"]):
            num_match = re.search(r'(?:top|best|first)\s+(\d+)', query_lower)
            constraints["limit"] = int(num_match.group(1)) if num_match else 10

        # Exclusion hints
        exclude_match = re.findall(r'(?:exclude|without|not|except)\s+(\S+)', query_lower)
        if exclude_match:
            constraints["exclude"] = exclude_match

        return constraints

    def _detect_time_range(self, query: str) -> str:
        query_lower = query.lower()
        if any(w in query_lower for w in ["today", "past 24 hours", "last 24 hours"]):
            return "day"
        if any(w in query_lower for w in ["this week", "past week", "last week"]):
            return "week"
        if any(w in query_lower for w in ["this month", "past month", "last month"]):
            return "month"
        if any(w in query_lower for w in ["this year", "past year", "last year"]):
            return "year"
        if any(w in query_lower for w in ["recent", "latest", "newest", "current"]):
            return "month"
        return ""

    def _compute_confidence(self, query: str, category: str) -> float:
        """Estimate how confident we are in the classification."""
        if category == "general":
            return 0.3

        query_lower = query.lower()
        keywords = INTENT_SIGNALS.get(category, {}).get("_keywords", [])
        matches = sum(1 for kw in keywords if kw in query_lower)

        if matches >= 3:
            return 0.95
        elif matches == 2:
            return 0.80
        elif matches == 1:
            return 0.60
        return 0.40