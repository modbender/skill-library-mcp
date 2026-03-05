"""Search indexing and retrieval engine."""

import re
from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class SearchIndex:
    """In-memory search index with multiple search strategies."""
    
    def __init__(self):
        """Initialize search index."""
        self.docs: List[Dict[str, Any]] = []
        self.doc_index: Dict[int, Dict[str, Any]] = {}
        self._build_search_cache()
    
    def _build_search_cache(self) -> None:
        """Build cached search structures."""
        self.keywords_cache = {}
        for i, doc in enumerate(self.docs):
            # Extract keywords from title and tags
            text = f"{doc['title']} {' '.join(doc.get('tags', []))}".lower()
            words = re.findall(r'\b\w+\b', text)
            for word in words:
                if word not in self.keywords_cache:
                    self.keywords_cache[word] = []
                if i not in self.keywords_cache[word]:
                    self.keywords_cache[word].append(i)
    
    def build(self, docs: List[Dict[str, Any]]) -> None:
        """
        Build index from documents.
        
        Args:
            docs: List of document dicts with {url, title, content, tags, full_content}
        """
        self.docs = docs
        for i, doc in enumerate(docs):
            self.doc_index[i] = doc
        self._build_search_cache()
        logger.info(f"Built search index with {len(docs)} documents")
    
    def _keyword_search(self, query: str, limit: int = 10) -> List[Tuple[int, float]]:
        """
        Keyword-based search using simple term matching.
        
        Returns:
            List of (doc_index, relevance_score) tuples
        """
        query_words = re.findall(r'\b\w+\b', query.lower())
        if not query_words:
            return []
        
        scores = {}
        for i, doc in enumerate(self.docs):
            score = 0
            title_lower = doc['title'].lower()
            content_lower = doc['full_content'].lower()
            
            for word in query_words:
                # Title match (higher weight)
                if word in title_lower:
                    score += 10
                
                # Content match
                if word in content_lower:
                    # Count occurrences
                    count = content_lower.count(word)
                    score += min(count, 5)  # Cap at 5 to avoid skewing
                
                # Tag match (high weight)
                if word in [t.lower() for t in doc.get('tags', [])]:
                    score += 8
            
            if score > 0:
                scores[i] = score
        
        # Sort by score descending
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked[:limit]
    
    def _regex_search(self, pattern: str, limit: int = 10) -> List[Tuple[int, float]]:
        """
        Regex-based search for advanced queries.
        
        Returns:
            List of (doc_index, relevance_score) tuples
        """
        try:
            regex = re.compile(pattern, re.IGNORECASE)
        except re.error as e:
            logger.warning(f"Invalid regex pattern: {e}")
            return []
        
        scores = {}
        for i, doc in enumerate(self.docs):
            matches_title = len(regex.findall(doc['title']))
            matches_content = len(regex.findall(doc['full_content']))
            
            if matches_title or matches_content:
                score = matches_title * 10 + matches_content
                scores[i] = score
        
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked[:limit]
    
    def _hybrid_search(self, query: str, limit: int = 10) -> List[Tuple[int, float]]:
        """
        Hybrid search: keyword first, then by relevance.
        
        Returns:
            List of (doc_index, relevance_score) tuples
        """
        # Start with keyword search
        results = self._keyword_search(query, limit * 2)
        
        # Boost by proximity of query terms in content
        for i, (doc_idx, score) in enumerate(results):
            doc = self.docs[doc_idx]
            content = doc['full_content'].lower()
            query_lower = query.lower()
            
            # Check for phrase match
            if query_lower in content:
                results[i] = (doc_idx, score * 1.5)
        
        # Re-sort
        results = sorted(results, key=lambda x: x[1], reverse=True)
        return results[:limit]
    
    def search(self, query: str, method: str = "keyword", limit: int = 10,
               regex: bool = False) -> List[Dict[str, Any]]:
        """
        Search the index.
        
        Args:
            query: Search query string
            method: "keyword", "regex", or "hybrid"
            limit: Maximum results to return
            regex: If True, treat query as regex pattern
        
        Returns:
            List of result dicts sorted by relevance
        """
        if not query.strip():
            return []
        
        if regex:
            ranked = self._regex_search(query, limit)
        elif method == "hybrid":
            ranked = self._hybrid_search(query, limit)
        else:
            ranked = self._keyword_search(query, limit)
        
        results = []
        for doc_idx, score in ranked:
            doc = self.docs[doc_idx].copy()
            doc['relevance_score'] = round(score, 2)
            doc['rank'] = len(results) + 1
            results.append(doc)
        
        return results
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize index for caching."""
        return {
            "docs": self.docs,
            "count": len(self.docs),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchIndex":
        """Deserialize index from cache."""
        index = cls()
        index.build(data.get("docs", []))
        return index
