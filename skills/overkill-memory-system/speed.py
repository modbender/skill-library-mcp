"""
Speed Optimizations for Overkill Memory System

Provides ultra-low latency search through:
1. Ultra-Hot Tier: In-memory cache for last 10 queries
2. Pre-compiled Queries: Skip emotional detection for common patterns
3. Lazy Loading: Defer heavy imports until needed
4. Confidence Early Exit: Skip unnecessary ranking
5. Query Normalization: Standardize queries for better cache hits
6. Result Truncation: Limit results to max 5
"""

from typing import List, Dict, Any, Optional
from collections import OrderedDict
import importlib

# ============================================================================
# LAZY IMPORT HELPER
# ============================================================================

def _lazy_import(module_name: str):
    """
    Lazily import a module only when needed.
    
    Args:
        module_name: Name of the module to import
    
    Returns:
        The imported module
    """
    return importlib.import_module(module_name)


# ============================================================================
# PRE-COMPILED QUERIES
# ============================================================================

# Pre-parsed common queries - these skip emotional detection
COMMON_QUERIES = {
    "user preference": {
        "keywords": ["preference", "prefer", "like", "dislike", "favorite"],
        "weights": {"context": 0.8, "content": 0.2},
        "skip_emotional": True
    },
    "fix error": {
        "keywords": ["fix", "error", "bug", "issue", "problem", "broken", "crash", "fail"],
        "weights": {"context": 0.3, "content": 0.7},
        "skip_emotional": True
    },
    "project": {
        "keywords": ["project", "code", "implement", "feature", "function"],
        "weights": {"context": 0.4, "content": 0.6},
        "skip_emotional": True
    },
    "remember": {
        "keywords": ["remember", "recall", "remind", "stored", "saved"],
        "weights": {"context": 0.9, "content": 0.1},
        "skip_emotional": True
    },
    "recent": {
        "keywords": ["recent", "latest", "last", "new", "recently", "yesterday", "today"],
        "weights": {"context": 0.2, "content": 0.8},
        "skip_emotional": True
    }
}


def get_compiled_query(query: str) -> Optional[Dict[str, Any]]:
    """
    Check if query matches a pre-compiled pattern.
    
    Args:
        query: Normalized search query
    
    Returns:
        Compiled query config if matches, None otherwise
    """
    normalized = normalize_query(query)
    
    for pattern, config in COMMON_QUERIES.items():
        # Check if any keyword is in the query
        for keyword in config["keywords"]:
            if keyword in normalized:
                return {
                    "pattern": pattern,
                    "weights": config["weights"],
                    "skip_emotional": config["skip_emotional"]
                }
    
    return None


# ============================================================================
# RESULT TRUNCATION
# ============================================================================

MAX_RESULTS = 5


def truncate_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Truncate results to MAX_RESULTS.
    
    Args:
        results: List of search results
    
    Returns:
        Truncated list (max MAX_RESULTS items)
    """
    return results[:MAX_RESULTS]


# ============================================================================
# QUERY NORMALIZATION
# ============================================================================

def normalize_query(query: str) -> str:
    """
    Normalize query for better cache hits.
    
    Normalization steps:
    - Convert to lowercase
    - Strip whitespace
    
    Args:
        query: Raw user query
    
    Returns:
        Normalized query string
    """
    return query.lower().strip()


# ============================================================================
# ULTRA-HOT TIER (In-Memory Cache)
# ============================================================================

class UltraHotCache:
    """
    In-memory LRU cache for the most recent queries.
    Stores last 10 queries for sub-millisecond access.
    """
    
    def __init__(self, max_size: int = 10):
        self.max_size = max_size
        self._cache: OrderedDict = OrderedDict()
    
    def get(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached result for query.
        
        Args:
            query: Search query (will be normalized)
        
        Returns:
            Cached results if exists, None otherwise
        """
        normalized = normalize_query(query)
        if normalized in self._cache:
            # Move to end (most recently used)
            self._cache.move_to_end(normalized)
            return self._cache[normalized]
        return None
    
    def set(self, query: str, results: List[Dict[str, Any]]) -> None:
        """
        Cache results for query.
        
        Args:
            query: Search query (will be normalized)
            results: Results to cache
        """
        normalized = normalize_query(query)
        
        # If key exists, update and move to end
        if normalized in self._cache:
            self._cache.move_to_end(normalized)
        
        # Add new entry
        self._cache[normalized] = results
        
        # Evict oldest if over max size
        while len(self._cache) > self.max_size:
            self._cache.popitem(last=False)
    
    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()
    
    def __len__(self) -> int:
        return len(self._cache)
    
    def __contains__(self, query: str) -> bool:
        return normalize_query(query) in self._cache


# Global ultra-hot cache instance
_ultra_hot_cache = UltraHotCache(max_size=10)


def get_ultra_hot(query: str) -> Optional[List[Dict[str, Any]]]:
    """
    Get cached result from ultra-hot tier.
    
    Args:
        query: Search query
    
    Returns:
        Cached results if exists, None otherwise
    """
    return _ultra_hot_cache.get(query)


def set_ultra_hot(query: str, results: List[Dict[str, Any]]) -> None:
    """
    Cache result in ultra-hot tier.
    
    Args:
        query: Search query
        results: Results to cache
    """
    _ultra_hot_cache.set(query, results)


def clear_ultra_hot() -> None:
    """Clear the ultra-hot cache."""
    _ultra_hot_cache.clear()


# ============================================================================
# CONFIDENCE EARLY EXIT
# ============================================================================

def rank_with_confidence(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Apply confidence-based early exit to ranking.
    
    Rules:
    - If top result confidence > 0.95, return only 1 result
    - If gap > 0.5 between top 2 results, return only 1 result
    - Otherwise, return up to 5 results
    
    Args:
        results: List of ranked results (should have 'score' or 'confidence')
    
    Returns:
        Filtered list based on confidence rules
    """
    if not results:
        return results
    
    # Extract scores - handle different result formats
    scores = []
    for r in results:
        if "score" in r:
            scores.append(r["score"])
        elif "confidence" in r:
            scores.append(r["confidence"])
        elif "relevance" in r:
            scores.append(r["relevance"])
        else:
            # No score available, return all
            return truncate_results(results)
    
    if not scores:
        return results
    
    top_score = scores[0]
    
    # Rule 1: Top result has very high confidence (>0.95)
    if top_score > 0.95:
        return [results[0]]
    
    # Rule 2: Gap between top 2 results is large (>0.5)
    if len(scores) >= 2:
        gap = scores[0] - scores[1]
        if gap > 0.5:
            return [results[0]]
    
    # Default: Return top 5
    return truncate_results(results)


# ============================================================================
# WEIGHTED RANKING (For Pre-compiled Queries)
# ============================================================================

def apply_compiled_weights(
    results: List[Dict[str, Any]], 
    weights: Dict[str, float]
) -> List[Dict[str, Any]]:
    """
    Apply pre-defined weights to result ranking.
    
    Args:
        results: Raw search results
        weights: Weight dict with keys like 'context', 'content'
    
    Returns:
        Reweighted results
    """
    if not results or not weights:
        return results
    
    # Re-score based on weights
    for r in results:
        base_score = r.get("score", r.get("confidence", 0.5))
        
        # Boost based on matching metadata
        boost = 0.0
        if "context" in weights and r.get("type") == "context":
            boost += weights.get("context", 0) * 0.1
        if "content" in weights and r.get("type") == "content":
            boost += weights.get("content", 0) * 0.1
        
        r["_weighted_score"] = base_score + boost
    
    # Sort by weighted score
    return sorted(results, key=lambda x: x.get("_weighted_score", 0), reverse=True)


# ============================================================================
# INTEGRATION HELPERS
# ============================================================================

def apply_speed_optimizations(
    query: str,
    results: List[Dict[str, Any]],
    skip_ultra_hot: bool = False,
    compiled: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Apply all speed optimizations to search results.
    
    Pipeline:
    1. Apply compiled weights (if pre-compiled query matched)
    2. Apply confidence early exit (ranking)
    3. Truncate to MAX_RESULTS
    4. Cache in ultra-hot (if not skipped)
    
    Args:
        query: Original search query
        results: Raw results from search
        skip_ultra_hot: If True, skip caching (for cache hits)
        compiled: Pre-compiled query config if matched
    
    Returns:
        Optimized results
    """
    # Apply pre-compiled weights if available
    if compiled and "weights" in compiled:
        results = apply_compiled_weights(results, compiled["weights"])
    
    # Apply confidence-based early exit
    results = rank_with_confidence(results)
    
    # Truncate to max results
    results = truncate_results(results)
    
    # Cache in ultra-hot (unless this was a cache hit)
    if not skip_ultra_hot and results:
        set_ultra_hot(query, results)
    
    return results


# ============================================================================
# UPDATED SEARCH FLOW (for documentation)
# ============================================================================

def search_flow(query: str) -> str:
    """
    Document the updated search flow.
    
    Flow:
    query → ULTRA-HOT → CACHE → COMPILED? → YES→use weights
                                        → NO →emotional detection
    
    Returns:
        Description of the search flow
    """
    return """
Updated Search Flow:
1. query → ULTRA-HOT (check in-memory cache for exact match)
2. ULTRA-HOT → CACHE HIT? → YES: return cached results
3. CACHE → COMPILED? → Check if query matches pre-compiled patterns
4. COMPILED = YES → Use pre-defined weights, skip emotional detection
5. COMPILED = NO → Run emotional detection (tone, urgency)
6. Return optimized results with confidence early exit
"""
