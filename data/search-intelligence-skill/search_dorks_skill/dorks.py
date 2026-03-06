"""
Dork generator: creates optimized search-engine dork queries from
parsed intents. Handles operator translation across engine families,
intelligent template filling, and multi-dork composition.
"""

from __future__ import annotations
import re
from typing import Any
from .models import SearchIntent, DorkQuery, IntentCategory
from .config import DORK_TEMPLATES, OPERATOR_SUPPORT, OPERATOR_ALIASES


class DorkGenerator:
    """Generate optimized dork queries from a SearchIntent."""

    def generate(self, intent: SearchIntent) -> list[DorkQuery]:
        """Generate a list of dork queries appropriate for the intent."""
        category = intent.category.value
        subcategory = intent.subcategory or "general"

        # Get templates for this category + subcategory
        templates = self._get_templates(category, subcategory)
        if not templates and subcategory != "general":
            templates = self._get_templates(category, "general")
        if not templates:
            templates = self._get_templates("general", "general")

        # Fill templates with entity values
        dorks = []
        fill_values = self._build_fill_values(intent)

        for template in templates:
            filled = self._fill_template(template, fill_values)
            if filled and filled.strip():
                operators = self._detect_operators(filled)
                purpose = self._describe_dork(template, fill_values)
                dorks.append(DorkQuery(
                    query=filled,
                    engine_hint="google",  # default; translated later
                    category_hint=category,
                    operators_used=operators,
                    purpose=purpose,
                ))

        # If no templates matched at all, create basic keyword queries
        if not dorks:
            dorks = self._fallback_dorks(intent)

        # Add keyword-enhanced variants
        dorks.extend(self._keyword_enhanced_dorks(intent, fill_values))

        return dorks

    def generate_custom(
        self,
        keyword: str,
        domain: str = "",
        filetype: str = "",
        intitle: str = "",
        inurl: str = "",
        exclude: list[str] | None = None,
        exact_match: bool = False,
        extra_operators: dict[str, str] | None = None,
    ) -> DorkQuery:
        """Build a custom dork query from explicit parameters."""
        parts = []

        if domain:
            parts.append(f"site:{domain}")
        if filetype:
            parts.append(f"filetype:{filetype}")
        if intitle:
            parts.append(f'intitle:"{intitle}"')
        if inurl:
            parts.append(f'inurl:"{inurl}"')
        if exclude:
            for ex in exclude:
                parts.append(f"-{ex}")
        if extra_operators:
            for op, val in extra_operators.items():
                parts.append(f"{op}:{val}")

        if exact_match:
            parts.append(f'"{keyword}"')
        else:
            parts.append(keyword)

        query = " ".join(parts)
        return DorkQuery(
            query=query,
            engine_hint="google",
            operators_used=self._detect_operators(query),
            purpose=f"Custom dork for: {keyword}",
        )

    def translate(self, dork: DorkQuery, target_engine: str) -> DorkQuery:
        """Translate a dork query's operators to work on a different engine."""
        if target_engine not in OPERATOR_SUPPORT:
            # Engine doesn't have special operator syntax; strip operators
            return DorkQuery(
                query=self._strip_operators(dork.query),
                engine_hint=target_engine,
                category_hint=dork.category_hint,
                operators_used=[],
                purpose=dork.purpose + f" (translated for {target_engine})",
            )

        translated = dork.query
        target_ops = OPERATOR_SUPPORT[target_engine]

        # Translate known operators
        for canonical_op, aliases in OPERATOR_ALIASES.items():
            if target_engine in aliases:
                target_op = aliases[target_engine]
                # Replace canonical_op: with target_op:
                translated = re.sub(
                    rf'\b{re.escape(canonical_op)}:',
                    f'{target_op}:',
                    translated,
                )

        # Remove operators not supported by target engine
        supported_ops = set(target_ops.keys())
        all_operators = set()
        for ops in OPERATOR_SUPPORT.values():
            all_operators.update(ops.keys())

        for op in all_operators - supported_ops:
            # Remove unsupported operators like cache:, related:, etc.
            translated = re.sub(
                rf'\b{re.escape(op)}:\S+',
                '',
                translated,
            )

        # Handle OR syntax differences
        if target_engine == "yandex":
            translated = translated.replace(" OR ", " | ")
        elif "or" in target_ops:
            translated = translated.replace(" | ", " OR ")

        translated = re.sub(r'\s+', ' ', translated).strip()

        return DorkQuery(
            query=translated,
            engine_hint=target_engine,
            category_hint=dork.category_hint,
            operators_used=self._detect_operators(translated),
            purpose=dork.purpose,
        )

    def _get_templates(self, category: str, subcategory: str) -> list[str]:
        cat_templates = DORK_TEMPLATES.get(category, {})
        return cat_templates.get(subcategory, [])

    def _build_fill_values(self, intent: SearchIntent) -> dict[str, str]:
        """Build the template fill dictionary from intent entities + keywords."""
        values: dict[str, str] = {}

        # Direct entity mappings
        for key in ["domain", "email", "email_domain", "name", "username",
                     "phone", "ip", "cve", "filetype", "year",
                     "company", "author"]:
            if key in intent.entities:
                values[key] = intent.entities[key]

        # Keyword as fallback for common template variables
        keyword = " ".join(intent.keywords) if intent.keywords else ""
        values.setdefault("keyword", keyword)
        values.setdefault("name", keyword)
        values.setdefault("company", keyword)
        values.setdefault("author", keyword)

        # Domain-derived values
        if "domain" in values:
            values.setdefault("email_domain", values["domain"])

        return values

    def _fill_template(self, template: str, values: dict[str, str]) -> str:
        """Fill a dork template with values. Skip if required values missing."""
        # Find all placeholders
        placeholders = re.findall(r'\{(\w+)\}', template)

        for ph in placeholders:
            if ph not in values or not values[ph]:
                # Required placeholder missing — skip this template
                return ""

        try:
            return template.format(**values)
        except (KeyError, IndexError):
            return ""

    def _detect_operators(self, query: str) -> list[str]:
        """Detect which search operators are used in a query."""
        operators = []
        op_patterns = [
            "site:", "filetype:", "intitle:", "allintitle:", "inurl:",
            "allinurl:", "intext:", "allintext:", "inanchor:",
            "cache:", "related:", "info:", "define:", "link:",
            "before:", "after:", "mime:", "title:", "host:",
            "domain:", "lang:", "inbody:", "contains:", "ip:",
            "feed:", "loc:", "prefer:", "ext:",
        ]
        for op in op_patterns:
            if op in query.lower():
                operators.append(op.rstrip(":"))

        if '"' in query:
            operators.append("exact_match")
        if " OR " in query or " | " in query:
            operators.append("or")
        if query.startswith("-") or " -" in query:
            operators.append("exclude")
        if "AROUND(" in query:
            operators.append("around")
        if ".." in query:
            operators.append("numrange")

        return operators

    def _describe_dork(self, template: str, values: dict[str, str]) -> str:
        """Generate a human-readable description of what a dork does."""
        descriptions = {
            "site:": "targeting specific domain",
            "filetype:": "searching for specific file types",
            "intitle:": "matching page titles",
            "inurl:": "matching URL patterns",
            "intext:": "searching page content",
            '"': "exact phrase matching",
        }
        parts = []
        for op, desc in descriptions.items():
            if op in template:
                parts.append(desc)

        domain = values.get("domain", "")
        keyword = values.get("keyword", "")

        if domain and keyword:
            return f"Search {domain} — {', '.join(parts) if parts else 'general search'} for '{keyword}'"
        elif domain:
            return f"Search {domain} — {', '.join(parts) if parts else 'general scan'}"
        elif keyword:
            return f"Search for '{keyword}' — {', '.join(parts) if parts else 'general search'}"
        return "General search"

    def _strip_operators(self, query: str) -> str:
        """Remove all search operators, leaving just keywords."""
        # Remove operator:value patterns
        stripped = re.sub(r'\b\w+:\S+', '', query)
        # Remove OR, AND, AROUND
        stripped = re.sub(r'\b(OR|AND|AROUND\(\d+\))\b', '', stripped)
        # Clean up quotes (keep the content)
        stripped = stripped.replace('"', '')
        # Clean whitespace
        stripped = re.sub(r'\s+', ' ', stripped).strip()
        return stripped

    def _fallback_dorks(self, intent: SearchIntent) -> list[DorkQuery]:
        """Generate basic dork queries when no templates match."""
        keyword = " ".join(intent.keywords) if intent.keywords else ""
        if not keyword:
            return []

        dorks = [
            DorkQuery(
                query=f'"{keyword}"',
                engine_hint="google",
                category_hint=intent.category.value,
                operators_used=["exact_match"],
                purpose=f"Exact search for '{keyword}'",
            ),
            DorkQuery(
                query=keyword,
                engine_hint="google",
                category_hint=intent.category.value,
                operators_used=[],
                purpose=f"Broad search for '{keyword}'",
            ),
        ]

        domain = intent.entities.get("domain")
        if domain:
            dorks.append(DorkQuery(
                query=f'site:{domain} "{keyword}"',
                engine_hint="google",
                category_hint=intent.category.value,
                operators_used=["site", "exact_match"],
                purpose=f"Search {domain} for '{keyword}'",
            ))

        return dorks

    def _keyword_enhanced_dorks(
        self, intent: SearchIntent, fill_values: dict[str, str]
    ) -> list[DorkQuery]:
        """Create additional dorks by combining keywords with discovered entities."""
        extras = []
        keyword = fill_values.get("keyword", "")
        domain = fill_values.get("domain", "")

        if not keyword or len(intent.keywords) < 2:
            return extras

        # If we have a domain and multiple keywords, search for each keyword on the domain
        if domain and len(intent.keywords) >= 2:
            for kw in intent.keywords[:3]:
                extras.append(DorkQuery(
                    query=f'site:{domain} "{kw}"',
                    engine_hint="google",
                    category_hint=intent.category.value,
                    operators_used=["site", "exact_match"],
                    purpose=f"Search {domain} for '{kw}'",
                ))

        return extras