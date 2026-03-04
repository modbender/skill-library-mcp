#!/usr/bin/env python3
"""
Account Matcher - Match Top Apps database entries to Salesforce accounts

This module helps bridge the gap between the Top Apps database (Appfigures data)
and Salesforce CRM records by matching on developer names, domains, and app names.

Matching Strategy (in order of reliability):
1. Domain match (highest confidence)
2. Developer name match with multiple search variants
3. App name match (lowest confidence)

Name Normalization:
- Strips legal suffixes: LLC, Inc., Corp., Ltd., etc.
- Strips generic app-related words: App, Apps, Studio, Games, Mobile, etc.
- Generates multiple search variants from longest to shortest

False Positive Prevention:
- Requires word boundary matching (not just substring containment)
- Uses similarity scoring to rank and filter results
- Minimum similarity threshold of 0.4 for acceptance

Usage:
    from account_matcher import AccountMatcher
    
    matcher = AccountMatcher()
    matches = matcher.match_app_to_salesforce({
        "developer_name": "Tezza App LLC",
        "developer_website": "shoptezza.com"
    })
"""

import re
from typing import Optional, List, Dict, Any, Tuple
from salesforce_client import SalesforceClient


class AccountMatcher:
    """Match Top Apps entries to Salesforce accounts."""
    
    # Legal entity suffixes to strip
    LEGAL_SUFFIXES = [
        'inc', 'incorporated', 'llc', 'llp', 'ltd', 'limited', 'corp', 'corporation',
        'co', 'company', 'gmbh', 'ag', 'sa', 'srl', 'bv', 'pty', 'plc', 'lp',
        'holding', 'holdings', 'group', 'international', 'intl'
    ]
    
    # Generic words commonly found in app developer names that should be stripped
    # for matching purposes (searched progressively)
    GENERIC_WORDS = [
        'app', 'apps', 'application', 'applications',
        'mobile', 'studio', 'studios', 'games', 'gaming',
        'software', 'technologies', 'technology', 'tech',
        'digital', 'interactive', 'entertainment', 'media',
        'labs', 'lab', 'works', 'solutions', 'services',
        'ventures', 'enterprises', 'worldwide', 'global'
    ]
    
    # Minimum similarity score to accept a match (prevents false positives)
    MIN_SIMILARITY_THRESHOLD = 0.4
    
    def __init__(self, sf_client: SalesforceClient = None):
        """Initialize with an optional Salesforce client."""
        self.sf = sf_client or SalesforceClient()
        self._sf_accounts_cache = None
    
    def _normalize_name(self, name: str, strip_generic: bool = False) -> str:
        """
        Normalize a company name for matching.
        
        Args:
            name: The company name to normalize
            strip_generic: If True, also strip generic words like "App", "Studio", etc.
        """
        if not name:
            return ""
        
        name = name.lower()
        
        # Remove legal suffixes
        for suffix in self.LEGAL_SUFFIXES:
            # Match suffix at end of string, with optional punctuation
            pattern = rf'\s*,?\s*{suffix}\.?\s*$'
            name = re.sub(pattern, '', name, flags=re.IGNORECASE)
        
        # Optionally remove generic words
        if strip_generic:
            for word in self.GENERIC_WORDS:
                # Remove as whole word only (not partial matches)
                pattern = rf'\b{word}\b'
                name = re.sub(pattern, '', name, flags=re.IGNORECASE)
        
        # Clean up punctuation and whitespace
        name = re.sub(r'[^\w\s]', '', name)  # Remove punctuation
        name = re.sub(r'\s+', ' ', name).strip()  # Normalize whitespace
        
        return name
    
    def _generate_search_variants(self, name: str) -> List[str]:
        """
        Generate multiple search variants from a company name.
        
        For "Tezza App LLC", generates:
        - "Tezza App LLC" (original)
        - "Tezza App" (without legal suffix)
        - "Tezza" (without generic words)
        
        Returns variants in order from most specific to least specific.
        """
        if not name:
            return []
        
        variants = []
        seen = set()
        
        # Variant 1: Original name (cleaned)
        original = name.strip()
        if original and original.lower() not in seen:
            variants.append(original)
            seen.add(original.lower())
        
        # Variant 2: Without legal suffixes
        no_legal = self._normalize_name(name, strip_generic=False)
        if no_legal and no_legal not in seen:
            variants.append(no_legal)
            seen.add(no_legal)
        
        # Variant 3: Without legal suffixes AND generic words
        no_generic = self._normalize_name(name, strip_generic=True)
        if no_generic and no_generic not in seen:
            variants.append(no_generic)
            seen.add(no_generic)
        
        # Variant 4: First word only (if multi-word and > 3 chars)
        words = no_generic.split()
        if len(words) > 1 and len(words[0]) > 3:
            first_word = words[0]
            if first_word not in seen:
                variants.append(first_word)
                seen.add(first_word)
        
        return variants
    
    def _normalize_domain(self, domain: str) -> str:
        """Normalize a domain for matching."""
        if not domain:
            return ""
        domain = domain.lower()
        domain = re.sub(r'^https?://', '', domain)
        domain = re.sub(r'^www\.', '', domain)
        domain = domain.split('/')[0]  # Remove path
        return domain
    
    def _extract_domain_from_url(self, url: str) -> str:
        """Extract the base domain from a URL."""
        if not url:
            return ""
        domain = self._normalize_domain(url)
        # Get the main domain (e.g., "calm.com" from "app.calm.com")
        parts = domain.split('.')
        if len(parts) >= 2:
            return '.'.join(parts[-2:])
        return domain
    
    def _search_accounts_by_name(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search Salesforce accounts by name with LIKE query.
        Returns accounts where the name contains the search term.
        """
        if not search_term or len(search_term) < 2:
            return []
        
        # Escape single quotes for SOQL
        safe_term = search_term.replace("'", "\\'")
        
        return self.sf.query(f"""
            SELECT Id, Name, Website, Domain__c, Industry, 
                   accountIntentScore6sense__c, accountBuyingStage6sense__c,
                   accountProfileFit6sense__c, account6QA6sense__c,
                   Churned__c, OwnerId, Owner.Name, Type
            FROM Account
            WHERE Name LIKE '%{safe_term}%'
            LIMIT 20
        """)
    
    def _is_word_boundary_match(self, search_term: str, account_name: str) -> bool:
        """
        Check if the search term matches at word boundaries in the account name.
        
        This prevents false positives like "nfl" matching "Inflow".
        
        Examples:
            - "nfl" in "NFL" → True (exact match)
            - "nfl" in "NFL Enterprises" → True (word boundary)
            - "nfl" in "Inflow" → False (substring, not word boundary)
            - "tezza" in "Tezza" → True (exact match)
        """
        if not search_term or not account_name:
            return False
        
        search_lower = search_term.lower()
        account_lower = account_name.lower()
        
        # Exact match
        if search_lower == account_lower:
            return True
        
        # Check if search term appears as a complete word (word boundary match)
        # Use word boundary regex: \b matches start/end of word
        pattern = rf'\b{re.escape(search_lower)}\b'
        if re.search(pattern, account_lower):
            return True
        
        # Check if account name starts with the search term followed by space/punctuation
        if account_lower.startswith(search_lower) and (
            len(account_lower) == len(search_lower) or 
            not account_lower[len(search_lower)].isalnum()
        ):
            return True
        
        return False
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate similarity between two normalized names.
        Returns a score between 0 and 1.
        
        Uses multiple strategies:
        1. Exact match after normalization → 1.0
        2. Word boundary containment → based on length ratio
        3. Word overlap (Jaccard similarity)
        """
        if not name1 or not name2:
            return 0.0
        
        n1 = self._normalize_name(name1, strip_generic=True).lower()
        n2 = self._normalize_name(name2, strip_generic=True).lower()
        
        if not n1 or not n2:
            return 0.0
        
        # Exact match after normalization
        if n1 == n2:
            return 1.0
        
        # Check word boundary match (not just substring)
        # This prevents "nfl" matching "inflow"
        if self._is_word_boundary_match(n1, n2):
            shorter = min(len(n1), len(n2))
            longer = max(len(n1), len(n2))
            return shorter / longer
        
        if self._is_word_boundary_match(n2, n1):
            shorter = min(len(n1), len(n2))
            longer = max(len(n1), len(n2))
            return shorter / longer
        
        # Check word overlap (Jaccard similarity)
        words1 = set(n1.split())
        words2 = set(n2.split())
        if words1 and words2:
            overlap = len(words1 & words2)
            total = len(words1 | words2)
            if overlap > 0:
                return overlap / total
        
        # No good match
        return 0.0
    
    def match_app_to_salesforce(self, app: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Match a Top Apps entry to Salesforce accounts.
        
        Args:
            app: Dictionary with keys like 'developer_name', 'developer_website', 'name'
        
        Returns:
            List of matching Salesforce accounts with match confidence
        """
        matches = []
        developer_name = app.get("developer_name", "")
        developer_website = app.get("developer_website", "")
        app_name = app.get("name", "")
        
        # Try matching by domain first (most reliable)
        if developer_website:
            domain = self._extract_domain_from_url(developer_website)
            if domain:
                domain_matches = self.sf.get_account_by_domain(domain)
                for acc in domain_matches:
                    acc["_match_type"] = "domain"
                    acc["_match_confidence"] = "high"
                    acc["_match_score"] = 1.0
                    matches.append(acc)
        
        # Try matching by developer name with multiple variants
        if developer_name and not matches:
            variants = self._generate_search_variants(developer_name)
            
            for variant in variants:
                if len(variant) < 3:
                    continue
                    
                name_matches = self._search_accounts_by_name(variant)
                
                for acc in name_matches:
                    # Calculate similarity score
                    similarity = self._calculate_name_similarity(developer_name, acc.get("Name", ""))
                    
                    # Only accept matches above threshold (prevents false positives like NFL→Inflow)
                    if similarity >= self.MIN_SIMILARITY_THRESHOLD:
                        # Check if we already have this account
                        if not any(m["Id"] == acc["Id"] for m in matches):
                            acc["_match_type"] = "developer_name"
                            acc["_match_confidence"] = "high" if similarity >= 0.8 else "medium" if similarity >= 0.5 else "low"
                            acc["_match_score"] = similarity
                            acc["_match_variant"] = variant
                            matches.append(acc)
                
                # If we found good matches, stop trying more variants
                if any(m.get("_match_score", 0) >= 0.5 for m in matches):
                    break
        
        # Try matching by app name as last resort
        if app_name and not matches:
            # Extract core app name (before colon or dash)
            core_app_name = re.split(r'[:\-–—]', app_name)[0].strip()
            
            if core_app_name and len(core_app_name) >= 3:
                app_matches = self._search_accounts_by_name(core_app_name)
                
                for acc in app_matches:
                    similarity = self._calculate_name_similarity(core_app_name, acc.get("Name", ""))
                    
                    # Higher threshold for app name matches (more prone to false positives)
                    if similarity >= 0.5:
                        if not any(m["Id"] == acc["Id"] for m in matches):
                            acc["_match_type"] = "app_name"
                            acc["_match_confidence"] = "medium" if similarity >= 0.8 else "low"
                            acc["_match_score"] = similarity
                            matches.append(acc)
        
        # Sort by match score (highest first)
        matches.sort(key=lambda x: x.get("_match_score", 0), reverse=True)
        
        # Deduplicate by Account ID (keep highest scoring)
        seen_ids = set()
        unique_matches = []
        for m in matches:
            if m["Id"] not in seen_ids:
                seen_ids.add(m["Id"])
                unique_matches.append(m)
        
        return unique_matches
    
    def bulk_match_apps(self, apps: List[Dict[str, Any]], 
                        progress_callback=None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Match multiple apps to Salesforce accounts.
        
        Args:
            apps: List of app dictionaries
            progress_callback: Optional function called with (current, total)
        
        Returns:
            Dictionary mapping app bundle_id to list of Salesforce matches
        """
        results = {}
        total = len(apps)
        
        for i, app in enumerate(apps):
            bundle_id = app.get("bundle_id", app.get("name", f"app_{i}"))
            matches = self.match_app_to_salesforce(app)
            results[bundle_id] = matches
            
            if progress_callback:
                progress_callback(i + 1, total)
        
        return results
    
    def enrich_app_with_salesforce(self, app: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich a Top Apps entry with Salesforce data.
        
        Returns the app dict with additional Salesforce fields added.
        """
        enriched = app.copy()
        matches = self.match_app_to_salesforce(app)
        
        if matches:
            best_match = matches[0]  # Take the first (best) match
            enriched["sf_account_id"] = best_match.get("Id")
            enriched["sf_account_name"] = best_match.get("Name")
            enriched["sf_match_type"] = best_match.get("_match_type")
            enriched["sf_match_confidence"] = best_match.get("_match_confidence")
            enriched["sf_match_score"] = best_match.get("_match_score")
            enriched["sf_intent_score"] = best_match.get("accountIntentScore6sense__c")
            enriched["sf_buying_stage"] = best_match.get("accountBuyingStage6sense__c")
            enriched["sf_profile_fit"] = best_match.get("accountProfileFit6sense__c")
            enriched["sf_is_6qa"] = best_match.get("account6QA6sense__c")
            enriched["sf_churned"] = best_match.get("Churned__c")
            enriched["sf_owner"] = best_match.get("Owner", {}).get("Name") if best_match.get("Owner") else None
        else:
            enriched["sf_account_id"] = None
            enriched["sf_match_type"] = "no_match"
        
        return enriched


if __name__ == "__main__":
    # Test the matcher
    matcher = AccountMatcher()
    
    # Test with some sample apps including the problematic ones
    test_apps = [
        {"developer_name": "Tezza App LLC", "developer_website": "", "name": "Tezza: Aesthetic Photo Editor"},
        {"developer_name": "NFL Enterprises LLC", "developer_website": "", "name": "NFL"},
        {"developer_name": "Calm, Inc.", "developer_website": "calm.com", "name": "Calm"},
        {"developer_name": "Headspace Inc.", "developer_website": "headspace.com", "name": "Headspace"},
        {"developer_name": "Twelve APP", "developer_website": "", "name": "Yubo: Chat Meet & Make Friends"},
        {"developer_name": "BPMobile", "developer_website": "", "name": "iScanner: PDF Document Scanner"},
    ]
    
    print("Testing Improved Account Matcher...")
    print("="*70)
    
    for app in test_apps:
        print(f"\nMatching: {app['developer_name']}")
        print(f"  App name: {app['name']}")
        
        # Show search variants
        variants = matcher._generate_search_variants(app['developer_name'])
        print(f"  Search variants: {variants}")
        
        matches = matcher.match_app_to_salesforce(app)
        if matches:
            for m in matches[:2]:
                print(f"  ✓ {m['Name']} (via {m['_match_type']}, score: {m.get('_match_score', 0):.2f})")
                print(f"    Intent: {m.get('accountIntentScore6sense__c')}, Stage: {m.get('accountBuyingStage6sense__c')}")
        else:
            print("  ✗ No matches found")
