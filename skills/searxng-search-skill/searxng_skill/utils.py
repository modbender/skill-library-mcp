"""
Utility functions for SearXNG skill
"""

from typing import Dict, Any, Optional, List
from urllib.parse import quote_plus, urljoin, urlparse
import json


def build_search_url(base_url: str, endpoint: str = "/search") -> str:
    """
    Build complete search URL
    
    Args:
        base_url: Base URL of SearXNG instance
        endpoint: API endpoint
        
    Returns:
        Complete URL
    """
    return urljoin(base_url.rstrip('/'), endpoint)


def sanitize_query(query: str) -> str:
    """
    Sanitize search query
    
    Args:
        query: Raw search query
        
    Returns:
        Sanitized query
    """
    return query.strip()


def validate_url(url: str) -> bool:
    """
    Validate URL format
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def format_results(
    raw_results: Dict[str, Any],
    max_results: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Format and filter search results
    
    Args:
        raw_results: Raw results from SearXNG
        max_results: Maximum number of results to return
        
    Returns:
        Formatted results list
    """
    results = raw_results.get("results", [])
    
    if max_results:
        results = results[:max_results]
    
    return results


def merge_search_results(
    results_list: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Merge multiple search result sets
    
    Args:
        results_list: List of result dictionaries
        
    Returns:
        Merged results
    """
    merged = {
        "results": [],
        "suggestions": [],
        "answers": [],
        "corrections": []
    }
    
    for results in results_list:
        merged["results"].extend(results.get("results", []))
        merged["suggestions"].extend(results.get("suggestions", []))
        merged["answers"].extend(results.get("answers", []))
        merged["corrections"].extend(results.get("corrections", []))
    
    # Remove duplicates
    merged["suggestions"] = list(set(merged["suggestions"]))
    merged["answers"] = list(set(merged["answers"]))
    
    return merged


def deduplicate_results(
    results: List[Dict[str, Any]],
    key: str = "url"
) -> List[Dict[str, Any]]:
    """
    Remove duplicate results based on key
    
    Args:
        results: List of search results
        key: Key to use for deduplication
        
    Returns:
        Deduplicated results
    """
    seen = set()
    deduped = []
    
    for result in results:
        value = result.get(key)
        if value and value not in seen:
            seen.add(value)
            deduped.append(result)
    
    return deduped


def export_results_json(
    results: Dict[str, Any],
    filepath: str
) -> None:
    """
    Export results to JSON file
    
    Args:
        results: Search results
        filepath: Output file path
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


def export_results_csv(
    results: List[Dict[str, Any]],
    filepath: str
) -> None:
    """
    Export results to CSV file
    
    Args:
        results: Search results
        filepath: Output file path
    """
    import csv
    
    if not results:
        return
    
    keys = results[0].keys()
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)