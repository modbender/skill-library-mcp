"""
HiEnergy API Skill - Open Claw Skill for querying advertisers, affiliate programs, and deals.
"""

import os
import re
import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import requests


class HiEnergySkillError(Exception):
    """Raised when the HiEnergy skill encounters a recoverable API/runtime error."""


@dataclass(frozen=True)
class CommissionInsight:
    """Normalized view of a commission field for ranking and user explanation."""
    model: str
    display: str
    percent_value: Optional[float]
    flat_amount_usd: Optional[float]


class HiEnergySkill:
    """
    A skill for interacting with the HiEnergy API to answer questions about
    advertisers, affiliate programs, deals, transactions, and contacts.
    """
    
    BASE_URL = "https://app.hienergy.ai"
    MAX_SEARCH_TERMS = 3  # Maximum number of keywords to extract from questions
    MAX_DISPLAY_ITEMS = 20  # Show a fuller top list in chat responses
    MAX_PAGE_SIZE = 500  # API-documented max
    DEFAULT_CHAT_LIMIT = 20  # safe interactive default; increase only when needed
    REQUEST_TIMEOUT_SECONDS = 30
    ALLOWED_HTTP_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the HiEnergy API skill.
        
        Args:
            api_key: The API key for HiEnergy API. If not provided, will try to read
                    from HIENERGY_API_KEY environment variable.
        """
        self.api_key = (
            api_key
            or os.environ.get('HIENERGY_API_KEY')
            or os.environ.get('HI_ENERGY_API_KEY')
        )
        if not self.api_key:
            raise ValueError(
                "API key is required. Provide it as a parameter or set HIENERGY_API_KEY "
                "(or HI_ENERGY_API_KEY) environment variable. "
                "Get your key at https://app.hienergy.ai/api_documentation/api_key "
                "(login: https://app.hienergy.ai/sign_in)."
            )
        
        self.headers = {
            'X-Api-Key': self.api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'openclaw-hi-energy-affiliate-copilot/1.0'
        }
    
    def _clamp_page_size(self, value: int) -> int:
        """Clamp page size to API-safe bounds."""
        if value is None:
            return 20
        return max(1, min(int(value), self.MAX_PAGE_SIZE))

    def _make_request(self, endpoint: str, method: str = 'GET',
                      params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict:
        """
        Make a request to the HiEnergy API.
        
        Args:
            endpoint: The API endpoint to call
            method: HTTP method (GET, POST, etc.)
            params: Query parameters
            data: Request body data
            
        Returns:
            Response data as dictionary
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        clean_endpoint = endpoint.lstrip('/')
        upper_method = method.upper()

        if upper_method not in self.ALLOWED_HTTP_METHODS:
            raise HiEnergySkillError(f"Unsupported HTTP method: {method}")

        if clean_endpoint.startswith(('http://', 'https://')) or '..' in clean_endpoint:
            raise HiEnergySkillError("Invalid endpoint path")

        url = f"{self.BASE_URL}/api/v1/{clean_endpoint}"
        
        try:
            response = requests.request(
                method=upper_method,
                url=url,
                headers=self.headers,
                params=params,
                json=data,
                timeout=self.REQUEST_TIMEOUT_SECONDS
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else 'unknown'
            body_preview = ''
            if e.response is not None:
                body_preview = (e.response.text or '')[:300]
            if status == 429:
                retry_after = None
                if e.response is not None:
                    retry_after = e.response.headers.get('Retry-After')
                hint = f" Please retry in {retry_after} seconds." if retry_after else " Please retry in a few seconds."
                raise HiEnergySkillError(f"Rate limited by HiEnergy API (HTTP 429).{hint}")
            raise HiEnergySkillError(f"API request failed (HTTP {status}): {body_preview}")
        except requests.exceptions.RequestException as e:
            raise HiEnergySkillError(f"API request failed: {str(e)}")
    
    def _normalize_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten JSON:API-style objects while preserving top-level keys."""
        if not isinstance(item, dict):
            return {}

        attrs = item.get('attributes')
        if isinstance(attrs, dict):
            merged = dict(attrs)
            if 'id' not in merged and item.get('id') is not None:
                merged['id'] = item.get('id')
            if item.get('type') is not None:
                merged['type'] = item.get('type')
            return merged

        return item

    def _extract_list_data(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract list payloads across flat, JSON:API, and root-key wrapped formats."""
        if not isinstance(response, dict):
            return []
            
        # Check for root keys that wrap the data (e.g., 'transactions', 'advertisers')
        # This handles cases like {"transactions": {"data": [...]}}
        for key in ['transactions', 'advertisers', 'deals', 'contacts', 'agencies', 'tags', 'status_changes']:
            if key in response and isinstance(response[key], dict) and 'data' in response[key]:
                return self._extract_list_data(response[key])

        data = response.get('data', [])
        if isinstance(data, list):
            return [self._normalize_item(item) for item in data]
        if isinstance(data, dict):
            return [self._normalize_item(data)]
        return []

    def _extract_single_data(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Extract single payloads across flat and JSON:API response formats."""
        items = self._extract_list_data(response)
        return items[0] if items else {}

    def get_advertisers_by_domain(self, domain_or_url: str, limit: int = DEFAULT_CHAT_LIMIT) -> List[Dict]:
        """
        Search advertisers by domain or URL.

        Args:
            domain_or_url: Domain or URL (e.g., amazon.com or https://amazon.com)
            limit: Maximum number of results to return

        Returns:
            List of advertiser dictionaries
        """
        params: Dict[str, Any] = {
            'domain': domain_or_url,
            'limit': self._clamp_page_size(limit)
        }

        results: List[Dict[str, Any]] = []

        # Primary endpoint from docs.
        try:
            response = self._make_request('advertisers/search_by_domain', params=params)
            results = self._extract_list_data(response)
        except Exception:
            results = []

        # Some backends accept `url` instead of `domain`.
        if not results:
            try:
                url_params: Dict[str, Any] = {
                    'url': domain_or_url,
                    'limit': self._clamp_page_size(limit)
                }
                url_response = self._make_request('advertisers/search_by_domain', params=url_params)
                results = self._extract_list_data(url_response)
            except Exception:
                results = []

        # Fallback: use advertisers index filters when domain endpoint is unstable.
        if not results:
            try:
                idx_response = self._make_request('advertisers', params={
                    'domain': domain_or_url,
                    'limit': self._clamp_page_size(limit)
                })
                results = self._extract_list_data(idx_response)
            except Exception:
                results = []

        if not results:
            try:
                idx_response = self._make_request('advertisers', params={
                    'name': domain_or_url,
                    'limit': self._clamp_page_size(limit)
                })
                results = self._extract_list_data(idx_response)
            except Exception:
                results = []

        return results

    def get_advertisers(self, search: Optional[str] = None,
                       limit: int = DEFAULT_CHAT_LIMIT, offset: int = 0) -> List[Dict]:
        """
        Get advertisers from the HiEnergy API.

        Args:
            search: Optional name/search term to filter advertisers
            limit: Maximum number of results to return
            offset: Offset for pagination

        Returns:
            List of advertiser dictionaries
        """
        base_params = {
            'limit': self._clamp_page_size(limit),
            'offset': offset
        }

        def dedupe(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            seen_ids = set()
            merged: List[Dict[str, Any]] = []
            for item in items:
                item_id = str(item.get('id')) if item.get('id') is not None else json.dumps(item, sort_keys=True)
                if item_id in seen_ids:
                    continue
                seen_ids.add(item_id)
                merged.append(item)
            return merged

        # Prefer domain endpoint for domain/URL-like queries.
        if search and ('.' in search or search.startswith('http://') or search.startswith('https://')):
            domain_results = self.get_advertisers_by_domain(search, limit=limit)
            if domain_results:
                return domain_results

        # No search term: preserve strict behavior and error surfacing.
        if not search:
            response = self._make_request('advertisers', params=dict(base_params))
            return self._extract_list_data(response)

        # Primary + fallback param strategies for advertiser search.
        strategies: List[Dict[str, Any]] = [
            {**base_params, 'name': search},
            {**base_params, 'domain': search},
            {**base_params, 'url': search},
        ]

        results: List[Dict[str, Any]] = []
        last_error: Optional[Exception] = None
        for params in strategies:
            try:
                response = self._make_request('advertisers', params=params)
                items = self._extract_list_data(response)
                if items:
                    results = dedupe(items)
                    break
            except Exception as e:
                last_error = e
                continue

        if not results and last_error is not None:
            raise last_error

        # Multi-word fallback: retry per token across name/domain/url and merge.
        if search and not results and ' ' in search.strip():
            token_collected: List[Dict[str, Any]] = []
            for token in [t.strip() for t in search.split() if t.strip()]:
                token_strategies = [
                    {**base_params, 'name': token},
                    {**base_params, 'domain': token},
                    {**base_params, 'url': token},
                ]
                for token_params in token_strategies:
                    try:
                        token_response = self._make_request('advertisers', params=token_params)
                        token_collected.extend(self._extract_list_data(token_response))
                    except Exception:
                        continue
            results = dedupe(token_collected)

        return results
    
    def get_affiliate_programs(self, advertiser_id: Optional[str] = None,
                              search: Optional[str] = None,
                              limit: int = DEFAULT_CHAT_LIMIT, offset: int = 0) -> List[Dict]:
        """
        Get affiliate program matches via advertiser endpoints.

        Note: HiEnergy does not expose a dedicated /affiliate_programs endpoint.
        Program discovery is performed via:
        - /advertisers/search_by_domain (for domain/url-like queries)
        - /advertisers index search (for name/text queries)

        Args:
            advertiser_id: Optional advertiser ID to filter results
            search: Optional search term or domain/url
            limit: Maximum number of results to return
            offset: Offset for pagination

        Returns:
            List of advertiser/program dictionaries
        """
        try:
            programs = self.get_advertisers(search=search, limit=limit, offset=offset)
        except Exception:
            programs = []

        if search:
            merged = {str(p.get('id')): p for p in programs if p.get('id') is not None}

            # Expand ambiguous cannabis intent (e.g., "weed") to likely network vocabulary.
            cannabis_aliases = {'weed', 'marijuana', 'cannabis', 'thc'}
            if search.lower().strip() in cannabis_aliases:
                for variant in ['cbd', 'hemp', 'cannabis', 'thc']:
                    try:
                        extra = self.get_advertisers(search=variant, limit=limit, offset=offset)
                        for p in extra:
                            pid = str(p.get('id'))
                            if pid and pid not in merged:
                                merged[pid] = p
                    except Exception:
                        continue

            # Improve matching for spaced brand names (e.g., "all birds" -> "allbirds").
            if ' ' in search.strip():
                compact_variants = [
                    ''.join(search.split()),
                    '-'.join(search.split()),
                ]
                for variant in compact_variants:
                    if not variant:
                        continue
                    try:
                        extra = self.get_advertisers(search=variant, limit=limit, offset=offset)
                        for p in extra:
                            pid = str(p.get('id'))
                            if pid and pid not in merged:
                                merged[pid] = p
                    except Exception:
                        continue

            if merged:
                programs = list(merged.values())

        # Re-rank by closeness to query string to surface strongest brand match first.
        if search:
            q = search.lower().strip()
            q_compact = ''.join(q.split())
            topical = [p for p in programs if self._is_topical_match(p, q)]
            if topical:
                programs = topical

            def score(item: Dict[str, Any]) -> int:
                name = str(item.get('name', '')).lower()
                name_compact = ''.join(name.split())
                s = 0
                if q == name:
                    s += 100
                if re.search(rf"\\b{re.escape(q)}\\b", name):
                    s += 50
                if q_compact and q_compact == name_compact:
                    s += 80
                if q_compact and q_compact in name_compact:
                    s += 40
                return s

            programs = sorted(programs, key=score, reverse=True)

        if advertiser_id:
            advertiser_id_str = str(advertiser_id)
            programs = [
                p for p in programs
                if str(p.get('id')) == advertiser_id_str or str(p.get('advertiser_id')) == advertiser_id_str
            ]

        return programs
    
    def _commission_raw_value(self, program: Dict[str, Any]) -> Optional[Any]:
        """Pick the first available commission-like field from a program payload."""
        for key in ('commission_rate', 'avg_commission_rate', 'commission_amount'):
            value = program.get(key)
            if value not in (None, ''):
                return value
        return None

    def _commission_insight(self, program: Dict[str, Any]) -> CommissionInsight:
        """Normalize commission text so results are easier to compare and explain."""
        raw = self._commission_raw_value(program)
        if raw is None:
            return CommissionInsight(
                model='unknown',
                display='Unknown',
                percent_value=None,
                flat_amount_usd=None,
            )

        if isinstance(raw, (int, float)):
            numeric = float(raw)
            return CommissionInsight(
                model='percent',
                display=f"{numeric:g}%",
                percent_value=numeric,
                flat_amount_usd=None,
            )

        text = str(raw).strip()
        lower_text = text.lower()

        # Range support like "8-12%" or "$10 - $25".
        range_matches = re.findall(r'\d+(?:\.\d+)?', lower_text)
        if len(range_matches) >= 2 and ('-' in lower_text or 'to' in lower_text):
            low = float(range_matches[0])
            high = float(range_matches[1])
            midpoint = round((low + high) / 2, 2)
            if '%' in lower_text:
                return CommissionInsight(
                    model='percent-range',
                    display=f"{low:g}-{high:g}% (avg {midpoint:g}%)",
                    percent_value=midpoint,
                    flat_amount_usd=None,
                )
            if '$' in lower_text or 'usd' in lower_text:
                return CommissionInsight(
                    model='flat-range',
                    display=f"${low:g}-${high:g} (avg ${midpoint:g})",
                    percent_value=None,
                    flat_amount_usd=midpoint,
                )

        numeric_match = re.search(r'\d+(?:\.\d+)?', lower_text.replace(',', ''))
        if numeric_match:
            numeric = float(numeric_match.group(0))
            if '%' in lower_text or 'revshare' in lower_text or 'revenue share' in lower_text:
                return CommissionInsight(
                    model='percent',
                    display=f"{numeric:g}%",
                    percent_value=numeric,
                    flat_amount_usd=None,
                )
            if '$' in lower_text or 'usd' in lower_text or any(k in lower_text for k in ('cpa', 'flat', 'per sale')):
                return CommissionInsight(
                    model='flat',
                    display=f"${numeric:g}",
                    percent_value=None,
                    flat_amount_usd=numeric,
                )

            # Unknown unit: keep useful display and treat as percent for historical compatibility.
            return CommissionInsight(
                model='numeric-unknown-unit',
                display=f"{numeric:g}",
                percent_value=numeric,
                flat_amount_usd=None,
            )

        return CommissionInsight(
            model='text-unparsed',
            display=text,
            percent_value=None,
            flat_amount_usd=None,
        )

    def _parse_commission_value(self, program: Dict[str, Any]) -> float:
        """Backwards-compatible commission value used by older filtering paths."""
        insight = self._commission_insight(program)
        if insight.percent_value is not None:
            return insight.percent_value
        return 0.0

    def _canonical_topic_terms(self, query: str) -> set:
        """Map common vertical terms to canonical keyword sets."""
        q = (query or '').lower().strip()
        if q in {'weed', 'marijuana', 'cannabis', 'thc'}:
            return {
                'weed', 'marijuana', 'cannabis', 'thc', 'cbd', 'hemp',
                'delta-8', 'delta 8', 'canna', 'kush', 'dispensary'
            }
        return {q} if q else set()

    def _text_has_term(self, text: str, term: str) -> bool:
        """Word-boundary match for prose, with compact fallback for terms like delta-8."""
        if not text or not term:
            return False
        escaped = re.escape(term)
        if re.search(rf"\b{escaped}\b", text):
            return True

        # Only use compact matching for punctuated terms (e.g. delta-8 -> delta8).
        if re.search(r'[^a-z0-9]', term):
            compact_text = re.sub(r'[^a-z0-9]+', '', text)
            compact_term = re.sub(r'[^a-z0-9]+', '', term)
            return bool(compact_term and compact_term in compact_text)
        return False

    def _is_topical_match(self, program: Dict[str, Any], query: str) -> bool:
        """Check if a program actually matches the requested topic."""
        terms = self._canonical_topic_terms(query)
        if not terms:
            return True

        prose_haystack = ' '.join([
            str(program.get('name', '')),
            str(program.get('description', '')),
            str(program.get('program_details', '')),
        ]).lower()

        id_haystack = ' '.join([
            str(program.get('domain', '')),
            str(program.get('url', '')),
            str(program.get('slug', '')),
        ]).lower()

        for term in terms:
            if self._text_has_term(prose_haystack, term):
                return True
            if term.replace(' ', '').replace('-', '') in re.sub(r'[^a-z0-9]+', '', id_haystack):
                return True
        return False

    def research_affiliate_programs(self,
                                    search: Optional[str] = None,
                                    advertiser_id: Optional[str] = None,
                                    min_commission: Optional[float] = None,
                                    network_slug: Optional[str] = None,
                                    status: Optional[str] = None,
                                    country: Optional[str] = None,
                                    limit: int = DEFAULT_CHAT_LIMIT,
                                    top_n: int = 10) -> Dict[str, Any]:
        """
        Research affiliate programs with ranking and summary stats.

        Returns a dict with:
        - summary: aggregate counts + average commission
        - programs: filtered + ranked program list
        """
        programs = self.get_affiliate_programs(
            advertiser_id=advertiser_id,
            search=search,
            limit=limit,
        )

        filtered: List[Dict[str, Any]] = []
        for program in programs:
            commission = self._commission_insight(program)

            # min_commission is interpreted as minimum percent threshold.
            if min_commission is not None:
                if commission.percent_value is None or commission.percent_value < float(min_commission):
                    continue

            if network_slug:
                network_value = str(
                    program.get('network_slug')
                    or (program.get('network') or {}).get('slug')
                    or ''
                ).lower()
                if network_slug.lower() not in network_value:
                    continue

            if status:
                status_value = str(program.get('status') or program.get('program_status') or '').lower()
                if status.lower() != status_value:
                    continue

            if country:
                country_value = ' '.join([
                    str(program.get('country', '')),
                    str(program.get('country_code', '')),
                    ' '.join(program.get('countries', []) if isinstance(program.get('countries'), list) else []),
                ]).lower()
                if country.lower() not in country_value:
                    continue

            enriched = dict(program)
            enriched['_commission_value'] = commission.percent_value or 0.0
            enriched['_commission_display'] = commission.display
            enriched['_commission_model'] = commission.model
            enriched['_commission_percent'] = commission.percent_value
            enriched['_commission_flat_usd'] = commission.flat_amount_usd
            filtered.append(enriched)

        ranked = sorted(
            filtered,
            key=lambda p: (
                p.get('_commission_percent') is not None,
                p.get('_commission_percent', 0.0),
                p.get('_commission_flat_usd', 0.0),
                p.get('transactions_count', 0) or 0,
            ),
            reverse=True,
        )

        top_programs = ranked[:max(1, int(top_n))]
        percent_values = [p.get('_commission_percent') for p in ranked if p.get('_commission_percent') is not None]
        avg_commission = (sum(percent_values) / len(percent_values)) if percent_values else 0.0

        return {
            'summary': {
                'query': search,
                'total_programs_scanned': len(programs),
                'total_programs_matched': len(ranked),
                'average_commission': round(avg_commission, 2),
                'average_commission_basis': 'percent-only (flat-fee programs excluded)',
                'filters': {
                    'advertiser_id': advertiser_id,
                    'min_commission': min_commission,
                    'network_slug': network_slug,
                    'status': status,
                    'country': country,
                },
            },
            'programs': top_programs,
        }

    def find_deals(self, search: Optional[str] = None,
                   category: Optional[str] = None,
                   advertiser_id: Optional[str] = None,
                   vertical_id: Optional[int] = None,
                   country: Optional[str] = None,
                   exclusive: Optional[bool] = None,
                   active: Optional[bool] = None,
                   status: Optional[str] = None,
                   network_id: Optional[str] = None,
                   min_commission: Optional[float] = None,
                   limit: int = DEFAULT_CHAT_LIMIT, offset: int = 0,
                   cursor: Optional[str] = None,
                   page: Optional[int] = None,
                   per_page: Optional[int] = None,
                   network_slug: Optional[str] = None,
                   start_date: Optional[str] = None,
                   end_date: Optional[str] = None,
                   effective_after: Optional[str] = None,
                   effective_before: Optional[str] = None,
                   sort_by: Optional[str] = None,
                   sort_order: Optional[str] = None) -> List[Dict]:
        """
        Find deals from the HiEnergy API.

        Args:
            search: Optional text search (maps to /api/v1/deals?search=...)
            category: Optional local alias for category-like filtering (best-effort)
            advertiser_id: Optional advertiser ID/slug to filter deals
            vertical_id: Optional vertical tag ID filter
            country: Optional ISO2 country filter (e.g. US, CA)
            exclusive: Optional exclusive-only filter (true/false)
            active: Optional active-only filter (true/false)
            status: Optional status filter (active/inactive)
            network_id: Optional network ID/slug filter
            min_commission: Optional minimum commission rate
            limit: Maximum number of results to return
            offset: Offset for pagination (legacy)
            cursor: Cursor pagination token
            page: Offset pagination page number
            per_page: Offset pagination page size
            network_slug: Optional legacy network slug filter
            start_date: Optional start date filter (YYYY-MM-DD)
            end_date: Optional end date filter (YYYY-MM-DD)
            effective_after: Optional effective date lower bound (YYYY-MM-DD)
            effective_before: Optional effective date upper bound (YYYY-MM-DD)
            sort_by: Optional sort field
            sort_order: Optional sort direction (asc/desc)

        Returns:
            List of deal dictionaries
        """
        params: Dict[str, Any] = {
            'limit': self._clamp_page_size(limit),
            'offset': offset
        }
        if search:
            # HiEnergy deals endpoint supports text queries via `search`
            # e.g. /api/v1/deals?search=summer+sale
            params['search'] = search
        if category:
            params['category'] = category
        if advertiser_id:
            params['advertiser_id'] = advertiser_id
        if vertical_id is not None:
            params['vertical_id'] = int(vertical_id)
        if country:
            params['country'] = country
        if exclusive is not None:
            params['exclusive'] = bool(exclusive)
        if active is not None:
            params['active'] = bool(active)
        if status:
            params['status'] = status
        if network_id:
            params['network_id'] = network_id
        if min_commission is not None:
            params['min_commission'] = min_commission
        if cursor:
            params['cursor'] = cursor
        if page is not None:
            params['page'] = page
        if per_page is not None:
            params['per_page'] = self._clamp_page_size(per_page)
        if network_slug:
            params['network_slug'] = network_slug
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        if effective_after:
            params['effective_after'] = effective_after
        if effective_before:
            params['effective_before'] = effective_before
        if sort_by:
            params['sort_by'] = sort_by
        if sort_order:
            params['sort_order'] = sort_order

        response = self._make_request('deals', params=params)
        results = self._extract_list_data(response)

        # Fallback 1: some backends may still expect `name` instead of `search`.
        if search and not results:
            fallback_params = dict(params)
            fallback_params.pop('search', None)
            fallback_params['name'] = search
            fallback_response = self._make_request('deals', params=fallback_params)
            results = self._extract_list_data(fallback_response)

        # Fallback 2: multi-word token search with de-dup if exact phrase misses.
        if search and not results and ' ' in search.strip():
            merged: List[Dict[str, Any]] = []
            seen_ids = set()
            for token in [t.strip() for t in search.split() if t.strip()]:
                token_params = dict(params)
                token_params['search'] = token
                token_response = self._make_request('deals', params=token_params)
                token_results = self._extract_list_data(token_response)
                if not token_results:
                    token_params.pop('search', None)
                    token_params['name'] = token
                    token_response = self._make_request('deals', params=token_params)
                    token_results = self._extract_list_data(token_response)

                for item in token_results:
                    item_id = str(item.get('id'))
                    if item_id not in seen_ids:
                        seen_ids.add(item_id)
                        merged.append(item)
            results = merged

        return results
    
    def get_transactions(self, search: Optional[str] = None,
                         advertiser_id: Optional[str] = None,
                         network_id: Optional[str] = None,
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None,
                         currency: Optional[str] = None,
                         sort_by: Optional[str] = None,
                         sort_order: Optional[str] = None,
                         limit: int = DEFAULT_CHAT_LIMIT,
                         offset: int = 0,
                         cursor: Optional[str] = None,
                         page: Optional[int] = None,
                         per_page: Optional[int] = None,
                         advertiser_slug: Optional[str] = None,
                         network_slug: Optional[str] = None,
                         status: Optional[str] = None,
                         contact_id: Optional[str] = None) -> List[Dict]:
        """
        Get transactions from the HiEnergy API.

        Args:
            search: Optional broad search text (client-assisted)
            advertiser_id: Filter by advertiser id/slug
            network_id: Filter by network id/slug
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            currency: Currency code filter (USD/EUR/...)
            sort_by: Sort field (transaction_date|commission_amount|sale_amount)
            sort_order: Sort direction (asc|desc)
            limit: Maximum number of results to return
            offset: Offset for pagination (legacy)
            cursor: Cursor pagination token
            page: Offset pagination page number
            per_page: Offset pagination page size
            advertiser_slug: Legacy alias for advertiser_id
            network_slug: Legacy alias for network_id
            status: Optional status filter (best-effort; if supported)
            contact_id: Optional contact filter (best-effort; if supported)

        Returns:
            List of transaction dictionaries
        """
        params: Dict[str, Any] = {
            'limit': self._clamp_page_size(limit),
            'offset': offset
        }

        if advertiser_id:
            params['advertiser_id'] = advertiser_id
        if advertiser_slug:
            params['advertiser_slug'] = advertiser_slug
        if network_id:
            params['network_id'] = network_id
        if network_slug:
            params['network_slug'] = network_slug
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        if currency:
            params['currency'] = currency
        if sort_by:
            params['sort_by'] = sort_by
        if sort_order:
            params['sort_order'] = sort_order
        if cursor:
            params['cursor'] = cursor
        if page is not None:
            params['page'] = page
        if per_page is not None:
            params['per_page'] = self._clamp_page_size(per_page)
        if status:
            params['status'] = status
        if contact_id:
            params['contact_id'] = contact_id

        # If search is provided, try server-side targeted filters first.
        if search and not any([advertiser_id, advertiser_slug, network_id, network_slug]):
            candidate_filters = [
                {'advertiser_id': search},
                {'advertiser_slug': search},
                {'network_id': search},
                {'network_slug': search},
            ]

            for candidate in candidate_filters:
                try_params = dict(params)
                try_params.update(candidate)
                try:
                    response = self._make_request('transactions', params=try_params)
                    items = self._extract_list_data(response)
                    if items:
                        return items
                except Exception:
                    # Some candidate filters may not be accepted by backend for a given value.
                    continue

        response = self._make_request('transactions', params=params)
        results = self._extract_list_data(response)

        # Client-side fallback for broad text search when API has no generic text param.
        if search:
            query = search.lower().strip()
            if query:
                filtered: List[Dict[str, Any]] = []
                for tx in results:
                    advertiser = tx.get('advertiser') if isinstance(tx.get('advertiser'), dict) else {}
                    network = tx.get('network') if isinstance(tx.get('network'), dict) else {}
                    haystack = ' '.join([
                        str(tx.get('id', '')),
                        str(tx.get('transaction_id', '')),
                        str(tx.get('order_id', '')),
                        str(tx.get('status', '')),
                        str(tx.get('currency', '')),
                        str(tx.get('advertiser_id', '')),
                        str(tx.get('advertiser_slug', '')),
                        str(advertiser.get('id', '')),
                        str(advertiser.get('name', '')),
                        str(advertiser.get('slug', '')),
                        str(network.get('id', '')),
                        str(network.get('name', '')),
                        str(network.get('slug', '')),
                    ]).lower()
                    if query in haystack:
                        filtered.append(tx)
                results = filtered

        return results

    def get_contacts(self, search: Optional[str] = None,
                     email: Optional[str] = None,
                     phone: Optional[str] = None,
                     domain: Optional[str] = None,
                     advertiser_id: Optional[str] = None,
                     advertiser_name: Optional[str] = None,
                     limit: int = DEFAULT_CHAT_LIMIT, 
                     offset: int = 0,
                     cursor: Optional[str] = None,
                     page: Optional[int] = None,
                     per_page: Optional[int] = None) -> List[Dict]:
        """
        Get contacts from the HiEnergy API.

        Args:
            search: Free-form query (q)
            email: Exact email match
            phone: Optional phone filter (client-side or if API supports it)
            domain: Filter by advertiser domain
            advertiser_id: Filter by advertiser ID or slug
            advertiser_name: Filter by advertiser name
            limit: Maximum number of results to return
            offset: Offset for pagination (legacy)
            cursor: Cursor pagination token
            page: Offset pagination page number
            per_page: Offset pagination page size

        Returns:
            List of contact dictionaries
        """
        params: Dict[str, Any] = {
            'limit': self._clamp_page_size(limit),
            'offset': offset
        }
        
        if search:
            params['q'] = search
        if email:
            params['email'] = email
        if phone:
            params['phone'] = phone
        if domain:
            params['domain'] = domain
        if advertiser_id:
            params['advertiser_id'] = advertiser_id
        if advertiser_name:
            params['advertiser_name'] = advertiser_name
        if cursor:
            params['cursor'] = cursor
        if page is not None:
            params['page'] = page
        if per_page is not None:
            params['per_page'] = self._clamp_page_size(per_page)

        response = self._make_request('contacts', params=params)
        return self._extract_list_data(response)

    def get_agencies(self, search: Optional[str] = None,
                     agency_id: Optional[str] = None,
                     limit: int = DEFAULT_CHAT_LIMIT,
                     page: Optional[int] = None,
                     per_page: Optional[int] = None) -> List[Dict]:
        """
        Get agencies from the HiEnergy API.
        
        Args:
            search: Optional name search
            agency_id: Optional ID filter
            limit: Max results
            page: Page number
            per_page: Results per page
            
        Returns:
            List of agency dictionaries
        """
        params: Dict[str, Any] = {}
        if search:
            params['q'] = search # Assuming 'q' or 'name' - starting with 'q' as common pattern
        if agency_id:
            params['agency_id'] = agency_id # or id if it's a direct resource, but usually index filters by id
            
        if page is not None:
            params['page'] = page
        
        final_limit = self._clamp_page_size(per_page if per_page is not None else limit)
        params['per_page'] = final_limit

        # Note: If endpoint is /agencies, we use that.
        # If it doesn't exist, this might fail, but we'll implement it as requested.
        try:
            response = self._make_request('agencies', params=params)
            return self._extract_list_data(response)
        except Exception:
            # Fallback if specific search fails, return empty
            return []

    def search_tags(self, search: Optional[str] = None,
                    page: Optional[int] = None,
                    per_page: Optional[int] = None) -> List[Dict]:
        """
        Search for tags/categories.
        
        Args:
            search: Search term (q)
            page: Page number
            per_page: Results per page
            
        Returns:
            List of tag dictionaries
        """
        params: Dict[str, Any] = {}
        if search:
            params['search'] = search # Docs say 'search' (or 'q')
            
        if page is not None:
            params['page'] = page
            
        if per_page is not None:
            params['per_page'] = self._clamp_page_size(per_page)

        response = self._make_request('tags', params=params)
        return self._extract_list_data(response)

    def get_tag_advertisers(self, tag_id: str,
                            network_id: Optional[str] = None,
                            status: Optional[str] = None,
                            sort: Optional[str] = None,
                            page: Optional[int] = None,
                            per_page: Optional[int] = None) -> List[Dict]:
        """
        Get advertisers for a specific tag.
        
        Args:
            tag_id: Tag ID or slug
            network_id: Filter by network
            status: Filter by status
            sort: Sort field (global_total_sales, etc.)
            page: Page number
            per_page: Results per page
            
        Returns:
            List of advertiser dictionaries (nested in data)
        """
        params: Dict[str, Any] = {}
        if network_id:
            params['network_id'] = network_id
        if status:
            params['status'] = status
        if sort:
            params['sort'] = sort
        if page is not None:
            params['page'] = page
        if per_page is not None:
            params['per_page'] = self._clamp_page_size(per_page)

        response = self._make_request(f'tags/{tag_id}/advertisers', params=params)
        return self._extract_list_data(response)

    def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new contact (Admin only).
        
        Args:
            contact_data: Dictionary containing contact fields.
                         Required: advertiser_id, email.
                         Optional: name, given_name, family_name, phone, job_title, source, status.
            
        Returns:
            Created contact dictionary
        """
        response = self._make_request('contacts', method='POST', data={'contact': contact_data})
        return self._extract_single_data(response)

    def find_contact_on_web(self, advertiser_name: str, advertiser_id: str) -> Optional[Dict[str, Any]]:
        """
        [Placeholder] Search the web for an affiliate contact.
        Actual implementation logic resides in the agent's multi-step plan:
        1. Agent calls web_search to find people on LinkedIn.
        2. Agent calls create_contact to push them to API.
        This method serves as an intent marker.
        """
        return None

    def replace_contact(self, contact_id: str, advertiser_id: str) -> Dict[str, Any]:
        """
        Reassign a contact to another advertiser.
        
        Args:
            contact_id: The ID of the contact to move
            advertiser_id: The target advertiser ID/slug
            
        Returns:
            Updated contact dictionary
        """
        data = {'advertiser_id': advertiser_id}
        response = self._make_request(f'contacts/{contact_id}/replace', method='POST', data=data)
        return self._extract_single_data(response)

    def get_publisher(self, publisher_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific publisher.
        
        Args:
            publisher_id: The ID or slug of the publisher
            
        Returns:
            Publisher details dictionary
        """
        response = self._make_request(f'publishers/{publisher_id}')
        return self._extract_single_data(response)

    def update_publisher(self, publisher_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a publisher's attributes (Admin/Publisher auth).
        
        Args:
            publisher_id: The ID or slug of the publisher
            data: Dictionary of fields to update (name, domain, network keys, etc.)
            
        Returns:
            Updated publisher dictionary
        """
        response = self._make_request(f'publishers/{publisher_id}', method='PATCH', data=data)
        return self._extract_single_data(response)

    def get_status_changes(self, 
                           q: Optional[str] = None,
                           from_status: Optional[str] = None,
                           to_status: Optional[str] = None,
                           advertiser_id: Optional[str] = None,
                           limit: int = DEFAULT_CHAT_LIMIT,
                           page: Optional[int] = None,
                           per_page: Optional[int] = None) -> List[Dict]:
        """
        Get status changes for advertisers.
        
        Args:
            q: Free-text search (Searchkick)
            from_status: Filter by previous status
            to_status: Filter by new status
            advertiser_id: Filter by advertiser ID or slug
            limit: Alias for per_page
            page: Page number
            per_page: Results per page
            
        Returns:
            List of status change dictionaries
        """
        params: Dict[str, Any] = {}
        if q:
            params['q'] = q
        if from_status:
            params['from_status'] = from_status
        if to_status:
            params['to_status'] = to_status
        if advertiser_id:
            params['advertiser_id'] = advertiser_id
        
        # Pagination
        if page is not None:
            params['page'] = page
        
        # Handle limit/per_page priority
        final_limit = self._clamp_page_size(per_page if per_page is not None else limit)
        params['per_page'] = final_limit

        response = self._make_request('status_changes', params=params)
        return self._extract_list_data(response)


    def get_advertiser_details(self, advertiser_id: str) -> Dict:
        """
        Get detailed information about a specific advertiser.
        
        Args:
            advertiser_id: The ID of the advertiser
            
        Returns:
            Advertiser details dictionary
        """
        response = self._make_request(f'advertisers/{advertiser_id}')
        return self._extract_single_data(response)
    
    def get_program_details(self, program_id: str) -> Dict:
        """
        Get detailed information about a specific affiliate program.
        
        Args:
            program_id: The ID of the affiliate program
            
        Returns:
            Program details dictionary
        """
        response = self._make_request(f'affiliate_programs/{program_id}')
        return self._extract_single_data(response)
    
    def get_deal_details(self, deal_id: str) -> Dict:
        """
        Get detailed information about a specific deal.
        
        Args:
            deal_id: The ID of the deal
            
        Returns:
            Deal details dictionary
        """
        response = self._make_request(f'deals/{deal_id}')
        return self._extract_single_data(response)
    
    def get_transaction_details(self, transaction_id: str) -> Dict:
        """
        Get detailed information about a specific transaction.

        Args:
            transaction_id: The ID of the transaction

        Returns:
            Transaction details dictionary
        """
        response = self._make_request(f'transactions/{transaction_id}')
        return self._extract_single_data(response)

    def get_contact_details(self, contact_id: str) -> Dict:
        """
        Get detailed information about a specific contact.

        Args:
            contact_id: The ID of the contact

        Returns:
            Contact details dictionary
        """
        response = self._make_request(f'contacts/{contact_id}')
        return self._extract_single_data(response)

    def _looks_like_domain_or_url(self, text: str) -> bool:
        t = (text or '').strip().lower()
        return '.' in t or t.startswith('http://') or t.startswith('https://')

    def _is_detail_request(self, question_lower: str) -> bool:
        detail_terms = ['more detail', 'details', 'detail', 'profile', 'show endpoint', 'full info', 'deep dive']
        return any(term in question_lower for term in detail_terms)

    def _is_yes_reply(self, question_lower: str) -> bool:
        yes_tokens = {'yes', 'y', 'yeah', 'yep', 'sure', 'ok', 'okay', 'please do'}
        cleaned = question_lower.strip()
        return cleaned in yes_tokens

    def _infer_intent(self, question_lower: str, context: Optional[Dict] = None) -> str:
        """Infer intent from question text, with conversational context fallback."""
        if any(term in question_lower for term in ['advertiser', 'company', 'brand', 'merchant']):
            return 'advertisers'
        if any(term in question_lower for term in ['program', 'affiliate program', 'partnership']):
            return 'programs'
        if any(term in question_lower for term in ['deal', 'offer', 'discount', 'promotion', 'coupon']):
            return 'deals'
        if any(term in question_lower for term in ['transaction', 'payment', 'sale', 'order', 'invoice']):
            return 'transactions'
        if any(term in question_lower for term in ['contact', 'customer', 'lead', 'client', 'prospect']):
            return 'contacts'
        if any(term in question_lower for term in ['status change', 'approval', 'rejection', 'applied']):
            return 'status_changes'
        if any(term in question_lower for term in ['publisher', 'network key', 'credential']):
            return 'publishers'
        if any(term in question_lower for term in ['agency', 'agencies']):
            return 'agencies'
        if any(term in question_lower for term in ['tag', 'category', 'categories']):
            return 'tags'

        # Conversational follow-up fallback (e.g., "what about macys?")
        if isinstance(context, dict):
            last_intent = str(context.get('last_intent', '')).strip().lower()
            if last_intent in {'advertisers', 'programs', 'deals', 'transactions', 'contacts', 'status_changes', 'publishers', 'agencies', 'tags'}:
                return last_intent

        return 'general'

    def answer_question(self, question: str, context: Optional[Dict] = None) -> str:
        """Answer a natural-language question using intent routing + API calls."""
        question_lower = question.lower()

        # Follow-up flow: user replied "yes" to detail offer from advertiser index results.
        if context and self._is_yes_reply(question_lower):
            last_adv_id = context.get('last_advertiser_id') if isinstance(context, dict) else None
            if last_adv_id:
                details = self.get_advertiser_details(str(last_adv_id))
                return self._format_advertiser_details_answer(details)

        search_term = self._extract_search_term(question)
        intent = self._infer_intent(question_lower, context=context)
        preface = f"Looking for {search_term or 'matches'} in {intent}..."

        if intent == 'advertisers' or self._looks_like_domain_or_url(search_term):
            advertisers = self.get_advertisers(search=search_term)
            if advertisers:
                if self._is_detail_request(question_lower):
                    first = advertisers[0]
                    adv_id = first.get('id')
                    if adv_id:
                        details = self.get_advertiser_details(str(adv_id))
                        return f"{preface}\n{self._format_advertiser_details_answer(details)}"
                return f"{preface}\n{self._format_advertisers_answer(advertisers, question)}"
            return f"{preface}\nI couldn't find any advertisers matching your query.\n{self._search_tips()}"

        if intent == 'programs':
            if 'research' in question_lower or 'best' in question_lower or 'top' in question_lower:
                report = self.research_affiliate_programs(search=search_term, top_n=5)
                if report.get('programs'):
                    return f"{preface}\n{self._format_program_research_answer(report)}"
                return f"{preface}\nI couldn't find any affiliate programs matching your query.\n{self._search_tips()}"

            programs = self.get_affiliate_programs(search=search_term)
            if programs:
                answer = self._format_programs_answer(programs, question)
                if len(programs) > 1:
                    answer += "\nThere are multiple matches. Do you want a specific publisher or network?"
                return f"{preface}\n{answer}"
            return f"{preface}\nI couldn't find any affiliate programs matching your query.\n{self._search_tips()}"

        if intent == 'deals':
            deals = self.find_deals(search=search_term)
            if deals:
                return f"{preface}\n{self._format_deals_answer(deals, question)}"
            return f"{preface}\nI couldn't find any deals matching your query.\n{self._search_tips()}"

        if intent == 'transactions':
            transactions = self.get_transactions(search=search_term)
            if transactions:
                return f"{preface}\n{self._format_transactions_answer(transactions, question)}"
            return f"{preface}\nI couldn't find any transactions matching your query.\n{self._search_tips()}"

        if intent == 'contacts':
            contacts = self.get_contacts(search=search_term)
            if contacts:
                return f"{preface}\n{self._format_contacts_answer(contacts, question)}"
            return (f"{preface}\nI couldn't find any contacts matching your query.\n"
                    "Tip: You can ask me to 'find contact on web for [Advertiser]' to search LinkedIn and add them.")

        if intent == 'status_changes':
            changes = self.get_status_changes(q=search_term)
            if changes:
                return f"{preface}\n{self._format_status_changes_answer(changes, question)}"
            return f"{preface}\nI couldn't find any status changes matching your query.\n{self._search_tips()}"
            
        if intent == 'agencies':
            agencies = self.get_agencies(search=search_term)
            if agencies:
                return f"{preface}\n{self._format_agencies_answer(agencies, question)}"
            return f"{preface}\nI couldn't find any agencies matching your query.\n{self._search_tips()}"

        if intent == 'tags':
            # Check if user wants advertisers for a tag (e.g. "advertisers in electronics tag")
            if 'advertiser' in question_lower:
                # Naive assumption: search term IS the tag slug/id
                advertisers = self.get_tag_advertisers(tag_id=search_term)
                if advertisers:
                    return f"{preface}\n{self._format_advertisers_answer(advertisers, question)}"
                return f"{preface}\nI couldn't find any advertisers for tag '{search_term}'.\n{self._search_tips()}"
            
            tags = self.search_tags(search=search_term)
            if tags:
                return f"{preface}\n{self._format_tags_answer(tags, question)}"
            return f"{preface}\nI couldn't find any tags matching your query.\n{self._search_tips()}"

        if intent == 'publishers':
             # Note: publishers endpoint usually requires an ID. For natural language, we might need a specific ID strategy.
             # This is a placeholder for basic publisher queries if we have a known ID or self-lookup.
             # For now, let's just hint that they need an ID or it's an admin feature.
             return f"{preface}\nPublisher lookup requires a specific ID. Try 'show publisher <id>'.\n{self._search_tips()}"


        # General search across all
        return f"{preface}\n{self._general_search(question)}"    
    def _extract_search_term(self, question: str) -> str:
        """Extract the main search term from a question."""
        # Remove common question words
        stop_words = ['what', 'are', 'the', 'is', 'about', 'tell', 'me', 'show',
                      'find', 'get', 'list', 'any', 'which', 'who', 'how',
                      'search', 'for', 'advertiser', 'advertisers', 'affiliate',
                      'program', 'programs']
        words = question.lower().split()
        filtered_words = [w.strip('?.,!') for w in words if w.lower() not in stop_words]
        # Return first few keywords to keep search focused
        return ' '.join(filtered_words[:self.MAX_SEARCH_TERMS]) if filtered_words else question
    
    def _extract_advertiser_id(self, item: Dict[str, Any]) -> Optional[str]:
        """Best-effort advertiser id extraction from mixed response shapes."""
        if not isinstance(item, dict):
            return None

        advertiser_obj = item.get('advertiser') if isinstance(item.get('advertiser'), dict) else {}

        candidates = [
            item.get('advertiser_id'),
            advertiser_obj.get('id'),
            item.get('id'),
        ]

        for candidate in candidates:
            if candidate is None:
                continue
            text = str(candidate).strip()
            if text:
                return text
        return None

    def _advertiser_link(self, advertiser_id: Optional[str]) -> str:
        """Build the canonical advertiser details link."""
        if not advertiser_id:
            return 'N/A'
        return f"https://app.hienergy.ai/a/{advertiser_id}"

    def _search_tips(self) -> str:
        """Return concise examples of what users can search for."""
        return (
            "Tips: Ask for advertisers by brand/domain, programs by vertical, deals by category, "
            "transactions by date range, or contacts by name/email. For commissions, ask for "
            "min % and I'll separate percent vs flat-fee payouts."
        )

    def _format_structured_answer(self, summary: str, top_results: List[str], next_filter: str) -> str:
        """Standard response shape for readability in chat."""
        lines = [f"Summary: {summary}", "Top Results:"]
        if top_results:
            lines.extend([f"- {row}" for row in top_results[:self.MAX_DISPLAY_ITEMS]])
        else:
            lines.append("- None")
        lines.append(f"Next Filter: {next_filter}")
        lines.append(self._search_tips())
        return "\n".join(lines)

    def _format_advertisers_answer(self, advertisers: List[Dict], question: str) -> str:
        """Format advertisers data into an answer (including publisher context)."""
        if len(advertisers) == 1:
            adv = advertisers[0]
            publisher = adv.get('publisher_name') or adv.get('agency_name') or adv.get('publisher_id') or 'Unknown'
            network = adv.get('network_name') or 'Unknown'
            adv_id = self._extract_advertiser_id(adv)
            link = self._advertiser_link(adv_id)
            return (
                f"Found advertiser: {adv.get('name', 'Unknown')} "
                f"(publisher: {publisher}, network: {network}) - "
                f"{adv.get('description', 'No description available')}\n"
                f"More info: {link}\n"
                f"Want a deeper summary from the advertiser profile? Reply 'yes'.\n"
                f"{self._search_tips()}"
            )
        else:
            rows = []
            for adv in advertisers[:self.MAX_DISPLAY_ITEMS]:
                publisher = adv.get('publisher_name') or adv.get('agency_name') or adv.get('publisher_id') or 'Unknown'
                link = self._advertiser_link(self._extract_advertiser_id(adv))
                rows.append(f"{adv.get('name', 'Unknown')} [publisher: {publisher}] ({link})")
            return (
                f"Found {len(advertisers)} advertisers: {', '.join(rows)}\n"
                f"Want a deeper summary for the top match from the advertiser profile? Reply 'yes'.\n"
                f"{self._search_tips()}"
            )

    def _format_advertiser_details_answer(self, advertiser: Dict[str, Any]) -> str:
        """Format advertiser show-endpoint details."""
        if not advertiser:
            return "I couldn't load advertiser details."

        name = advertiser.get('name', 'Unknown')
        advertiser_id = advertiser.get('id', 'Unknown')
        domain = advertiser.get('domain', 'N/A')
        url = advertiser.get('url', 'N/A')
        status = advertiser.get('status') or advertiser.get('program_status') or 'N/A'
        publisher = advertiser.get('publisher_name') or advertiser.get('agency_name') or advertiser.get('publisher_id') or 'Unknown'
        network = advertiser.get('network_name') or 'Unknown'
        commission = advertiser.get('commission_rate') or advertiser.get('avg_commission_rate') or 'N/A'

        return (
            f"Advertiser details: {name} (id: {advertiser_id})\n"
            f"- Domain: {domain}\n"
            f"- URL: {url}\n"
            f"- Status: {status}\n"
            f"- Publisher: {publisher}\n"
            f"- Network: {network}\n"
            f"- Commission: {commission}\n"
            f"- More info: {self._advertiser_link(str(advertiser_id))}\n"
            f"{self._search_tips()}"
        )
    
    def _format_programs_answer(self, programs: List[Dict], question: str) -> str:
        """Format affiliate program matches (backed by advertiser endpoints)."""
        rows = []
        for prog in programs:
            link = self._advertiser_link(self._extract_advertiser_id(prog))
            network = prog.get('network_name') or 'Unknown'
            publisher = prog.get('publisher_name') or prog.get('agency_name') or prog.get('publisher_id') or 'Unknown'
            rows.append(f"{prog.get('name', 'Unknown')} [network: {network}, publisher: {publisher}] ({link})")
        summary = f"Found {len(programs)} affiliate programs."
        return self._format_structured_answer(
            summary=summary,
            top_results=rows,
            next_filter="Add publisher name or network to narrow the list."
        )
    
    def _format_deals_answer(self, deals: List[Dict], question: str) -> str:
        """Format deals data into an answer."""
        rows = []
        for deal in deals[:self.MAX_DISPLAY_ITEMS]:
            link = self._advertiser_link(self._extract_advertiser_id(deal))
            rows.append(f"{deal.get('title', 'Unknown')} ({link})")
        return self._format_structured_answer(
            summary=f"Found {len(deals)} deals.",
            top_results=rows,
            next_filter="Filter by category, advertiser_id, or min_commission."
        )

    def _format_program_research_answer(self, report: Dict[str, Any]) -> str:
        """Format affiliate program research report."""
        summary = report.get('summary', {})
        programs = report.get('programs', [])
        if not programs:
            return "No affiliate programs matched your research filters."

        rows = []
        for p in programs[:self.MAX_DISPLAY_ITEMS]:
            name = p.get('name', 'Unknown')
            commission = p.get('_commission_display') or p.get('commission_rate') or p.get('_commission_value', 'N/A')
            commission_model = p.get('_commission_model', 'unknown')
            link = self._advertiser_link(self._extract_advertiser_id(p))
            rows.append(f"{name} (commission: {commission}, type: {commission_model}) | advertiser: {link}")

        basis = summary.get('average_commission_basis', '')
        basis_suffix = f"; {basis}" if basis else ''
        return self._format_structured_answer(
            summary=(
                f"Program research: {summary.get('total_programs_matched', 0)} matches "
                f"(avg commission {summary.get('average_commission', 0)}%{basis_suffix})."
            ),
            top_results=rows,
            next_filter="Try min commission %, country, status, or network_slug to narrow it down."
        )

    def _format_transactions_answer(self, transactions: List[Dict], question: str) -> str:
        """Format transactions data into an answer."""
        tx_rows = []
        for tx in transactions[:self.MAX_DISPLAY_ITEMS]:
            link = self._advertiser_link(self._extract_advertiser_id(tx))
            amount = tx.get('amount', tx.get('sale_amount', 'N/A'))
            status = tx.get('status', 'unknown')
            tx_rows.append(f"{str(tx.get('id', 'Unknown'))} - amount: {amount}, status: {status} ({link})")
        return self._format_structured_answer(
            summary=f"Found {len(transactions)} transactions.",
            top_results=tx_rows,
            next_filter="Filter by date range, advertiser_id, network_slug, or status."
        )

    def _format_contacts_answer(self, contacts: List[Dict], question: str) -> str:
        """Format contacts data into an answer."""
        rows = []
        for c in contacts[:self.MAX_DISPLAY_ITEMS]:
            name = c.get('name') or c.get('full_name') or 'Unknown'
            email = c.get('email', 'N/A')
            rows.append(f"{name} - Email: {email}")
        return self._format_structured_answer(
            summary=f"Found {len(contacts)} contacts.",
            top_results=rows,
            next_filter="Filter by name, email, or phone."
        )

    def _format_status_changes_answer(self, changes: List[Dict], question: str) -> str:
        """Format status changes data into an answer."""
        rows = []
        for c in changes[:self.MAX_DISPLAY_ITEMS]:
            adv_name = c.get('advertiser_name', 'Unknown')
            from_status = c.get('from_status', 'N/A')
            to_status = c.get('to_status', 'N/A')
            date = c.get('created_at', 'N/A')[:10]  # simple YYYY-MM-DD
            rows.append(f"{adv_name}: {from_status} -> {to_status} on {date}")
        
        return self._format_structured_answer(
            summary=f"Found {len(changes)} status changes.",
            top_results=rows,
            next_filter="Filter by advertiser, from_status, or to_status."
        )

    def _format_agencies_answer(self, agencies: List[Dict], question: str) -> str:
        """Format agencies data into an answer."""
        rows = []
        for agency in agencies[:self.MAX_DISPLAY_ITEMS]:
            name = agency.get('name', 'Unknown')
            agency_id = agency.get('id', 'Unknown')
            rows.append(f"{name} (ID: {agency_id})")
        
        return self._format_structured_answer(
            summary=f"Found {len(agencies)} agencies.",
            top_results=rows,
            next_filter="Use agency_id to filter other resources."
        )

    def _format_tags_answer(self, tags: List[Dict], question: str) -> str:
        """Format tags data into an answer."""
        rows = []
        for tag in tags[:self.MAX_DISPLAY_ITEMS]:
            name = tag.get('name', 'Unknown')
            tag_id = tag.get('id', 'Unknown')
            count = tag.get('taggings_count', 'N/A')
            rows.append(f"{name} (ID: {tag_id}, count: {count})")
        
        return self._format_structured_answer(
            summary=f"Found {len(tags)} tags.",
            top_results=rows,
            next_filter="Use 'advertisers in <tag>' to see advertisers."
        )

    def _general_search(self, question: str) -> str:
        """Perform a general search when question type is unclear."""
        search_term = self._extract_search_term(question)
        
        # Try all endpoints
        advertisers = self.get_advertisers(search=search_term, limit=3)
        programs = self.get_affiliate_programs(search=search_term, limit=3)
        deals = self.find_deals(search=search_term, limit=3)
        transactions = self.get_transactions(search=search_term, limit=3)
        contacts = self.get_contacts(search=search_term, limit=3)
        tags = self.search_tags(search=search_term, per_page=3)
        
        results = []
        if advertisers:
            results.append(f"Advertisers: {', '.join([a.get('name', 'Unknown') for a in advertisers])}")
        if programs:
            results.append(f"Programs: {', '.join([p.get('name', 'Unknown') for p in programs])}")
        if deals:
            results.append(f"Deals: {', '.join([d.get('title', 'Unknown') for d in deals])}")
        if transactions:
            results.append(f"Transactions: {', '.join([str(t.get('id', 'Unknown')) for t in transactions])}")
        if contacts:
            results.append(
                f"Contacts: {', '.join([(c.get('name') or c.get('full_name') or 'Unknown') for c in contacts])}"
            )
        if tags:
            results.append(f"Tags: {', '.join([t.get('name', 'Unknown') for t in tags])}")
        
        if results:
            return "Found the following:\n" + "\n".join(results) + "\n" + self._search_tips()
        else:
            return "I couldn't find any results for your question.\n" + self._search_tips()


def main():
    """Example usage of the HiEnergy skill."""
    import sys
    
    # Check if API key is provided
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        api_key = os.environ.get('HIENERGY_API_KEY')
    
    if not api_key:
        print("Usage: python hienergy_skill.py <api_key>")
        print("Or set HIENERGY_API_KEY environment variable")
        sys.exit(1)
    
    # Create skill instance
    skill = HiEnergySkill(api_key=api_key)
    
    # Example queries
    print("=" * 60)
    print("HiEnergy API Skill - Example Usage")
    print("=" * 60)
    
    try:
        # Get advertisers
        print("\n1. Getting advertisers:")
        advertisers = skill.get_advertisers(limit=5)
        print(f"   Found {len(advertisers)} advertisers")
        
        # Get affiliate programs
        print("\n2. Getting affiliate programs:")
        programs = skill.get_affiliate_programs(limit=5)
        print(f"   Found {len(programs)} programs")
        
        # Find deals
        print("\n3. Finding deals:")
        deals = skill.find_deals(limit=5)
        print(f"   Found {len(deals)} deals")
        
        # Get transactions
        print("\n4. Getting transactions:")
        transactions = skill.get_transactions(limit=5)
        print(f"   Found {len(transactions)} transactions")

        # Get contacts
        print("\n5. Getting contacts:")
        contacts = skill.get_contacts(limit=5)
        print(f"   Found {len(contacts)} contacts")

        # Answer a question
        print("\n6. Answering questions:")
        question = "What transactions were recently created?"
        answer = skill.answer_question(question)
        print(f"   Q: {question}")
        print(f"   A: {answer}")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nNote: This is a mock implementation. The actual API endpoints may differ.")
        print("Please refer to https://app.hienergy.ai/api_documentation for details.")


if __name__ == '__main__':
    main()
