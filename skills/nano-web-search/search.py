#!/usr/bin/env python3
"""NanoGPT Web Search API wrapper."""

import os
import json
import requests
from typing import Optional, List, Dict, Any


class NanoWebSearch:
    """NanoGPT Web Search API client."""
    
    API_URL = "https://nano-gpt.com/api/web"
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the search client.
        
        Args:
            api_key: NanoGPT API key. If not provided, reads from NANOGPT_API_KEY env var.
        
        Raises:
            ValueError: If no API key is provided or found in environment.
        """
        self.api_key = api_key or os.environ.get("NANOGPT_API_KEY")
        if not self.api_key:
            raise ValueError(
                "No API key provided. Set NANOGPT_API_KEY environment variable "
                "or pass api_key parameter. Get your key at https://nano-gpt.com"
            )
    
    def search(
        self,
        query: str,
        provider: str = "linkup",
        depth: str = "standard",
        output_type: str = "searchResults",
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        max_results: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Perform a web search.
        
        Args:
            query: Search query
            provider: Search provider (linkup, tavily, exa, kagi, perplexity, valyu, brave)
            depth: Search depth (standard or deep)
            output_type: Output format (searchResults, sourcedAnswer, structured)
            from_date: Start date filter (YYYY-MM-DD)
            to_date: End date filter (YYYY-MM-DD)
            include_domains: Domains to search exclusively
            exclude_domains: Domains to exclude
            max_results: Maximum number of results
            **kwargs: Additional provider-specific options
            
        Returns:
            Search results as dict with 'data' and 'metadata' keys
        """
        payload = {
            "query": query,
            "provider": provider,
            "depth": depth,
            "outputType": output_type,
        }
        
        if from_date:
            payload["fromDate"] = from_date
        if to_date:
            payload["toDate"] = to_date
        if include_domains:
            payload["includeDomains"] = include_domains
        if exclude_domains:
            payload["excludeDomains"] = exclude_domains
        if max_results:
            payload["maxResults"] = max_results
        
        # Add any additional provider-specific options
        payload.update(kwargs)
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
        }
        
        response = requests.post(self.API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def search_results(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Search and return just the results list.
        
        Args:
            query: Search query
            **kwargs: Additional search options
            
        Returns:
            List of search result items
        """
        result = self.search(query, output_type="searchResults", **kwargs)
        return result.get("data", [])
    
    def sourced_answer(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search and return a sourced answer.
        
        Args:
            query: Search query
            **kwargs: Additional search options
            
        Returns:
            Dict with 'answer' and 'sources' keys
        """
        result = self.search(query, output_type="sourcedAnswer", **kwargs)
        return result.get("data", {})
    
    def structured_search(
        self,
        query: str,
        schema: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Search and return structured data matching a schema.
        
        Args:
            query: Search query
            schema: JSON schema for the output
            **kwargs: Additional search options
            
        Returns:
            Structured data matching the schema
        """
        result = self.search(
            query,
            output_type="structured",
            structuredOutputSchema=json.dumps(schema),
            **kwargs
        )
        return result.get("data", {})


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python search.py <query> [--provider PROVIDER] [--depth DEPTH]")
        print("\nSet NANOGPT_API_KEY environment variable before using.")
        sys.exit(1)
    
    # Simple CLI
    search = NanoWebSearch()
    
    # Parse args
    query_parts = []
    kwargs = {}
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg.startswith("--"):
            key = arg[2:].replace("-", "_")
            if i + 1 < len(sys.argv):
                kwargs[key] = sys.argv[i + 1]
                i += 2
                continue
        query_parts.append(arg)
        i += 1
    
    query = " ".join(query_parts)
    
    # Perform search
    try:
        result = search.search(query, **kwargs)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
