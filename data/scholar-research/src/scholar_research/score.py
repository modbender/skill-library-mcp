#!/usr/bin/env python3
"""
Scholar Research - Scoring Module
Calculates credibility scores for academic papers
"""

import json
import requests
from typing import Dict, List, Optional
from datetime import datetime

# Default weights
DEFAULT_WEIGHTS = {
    "citation_count": 15,
    "publication_recency": 10,
    "author_reputation": 12,
    "journal_impact": 12,
    "peer_review_status": 10,
    "open_access": 8,
    "retraction_status": 10,
    "author_network": 8,
    "funder_acknowledgment": 5,
    "reproducibility": 5
}

DEFAULT_BONUS = {
    "author_trust_max": 20,
    "journal_reputation_max": 20
}


class CredibilityScorer:
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.weights = self.config.get("scoring", {}).get("paper_quality", DEFAULT_WEIGHTS)
        self.bonus_max = self.config.get("scoring", {}).get("bonus", DEFAULT_BONUS)
        
    def calculate_score(self, paper: Dict) -> Dict:
        """Calculate credibility score for a paper"""
        
        # Normalize each factor (0-100 scale)
        scores = {}
        
        # 1. Citation count (0-100 based on citations)
        # More realistic: 100 citations = max score
        citations = paper.get("citations", 0)
        
        # Handle various data types
        if isinstance(citations, (list, tuple)):
            citations = citations[0] if citations else 0
        if isinstance(citations, str):
            try:
                citations = int(citations.split()[0]) if citations.split() else 0
            except:
                citations = 0
        if isinstance(citations, dict):
            citations = citations.get("is-referenced-by-count", 0)
        
        try:
            citations = int(citations) if citations else 0
        except (ValueError, TypeError):
            citations = 0
            
        # 100 citations = 100 score, scale down
        scores["citation_count"] = min(100, citations * 2)  # 50 citations = max
        
        # 2. Publication recency (0-100, newer = higher)
        pub_date = paper.get("published", "")
        
        # Handle various data types
        if isinstance(pub_date, (list, tuple)):
            pub_date = str(pub_date[0]) if pub_date else ""
        elif isinstance(pub_date, dict):
            pub_date = str(pub_date.get("date-parts", [[""]])[0][0]) if pub_date.get("date-parts") else ""
            
        scores["publication_recency"] = self._calculate_recency(pub_date)
        
        # 3. Author reputation - default to 40 (unknown)
        scores["author_reputation"] = 40
        
        # 4. Journal impact - default to 40 (unknown)
        scores["journal_impact"] = paper.get("journal_impact_score", 40)
        
        # 5. Peer review status - check if published in journal
        journal = paper.get("journal", "")
        peer_reviewed = bool(journal and "arxiv" not in str(paper.get("source", "")).lower())
        scores["peer_review_status"] = 100 if peer_reviewed else 50
        
        # 6. Open access - from paper data
        scores["open_access"] = 100 if paper.get("open_access", False) else 40
        
        # 7. Retraction status - assume not retracted
        scores["retraction_status"] = 100
        
        # 8. Author network - default 40
        scores["author_network"] = 40
        
        # 9. Funder acknowledgment - unknown
        scores["funder_acknowledgment"] = 40
        
        # 10. Reproducibility - unknown
        scores["reproducibility"] = 40
        
        # Calculate weighted score
        weighted_score = 0
        total_weight = 0
        
        for factor, weight in self.weights.items():
            if factor in scores:
                weighted_score += scores[factor] * weight
                total_weight += weight
        
        # Normalize to 0-100 (weighted average)
        if total_weight > 0:
            paper_score = weighted_score / total_weight
        else:
            paper_score = 50
        
        # Add bonus scores (capped)
        author_bonus = min(20, paper.get("author_bonus", 0))
        journal_bonus = min(20, paper.get("journal_bonus", 0))
        
        final_score = paper_score + author_bonus + journal_bonus
        final_score = min(100, final_score)  # Cap at 100
        
        return {
            "score": round(final_score, 1),
            "breakdown": {k: round(v, 1) for k, v in scores.items()},
            "bonuses": {
                "author_trust": author_bonus,
                "journal_reputation": journal_bonus
            }
        }
    
    def _calculate_recency(self, pub_date: str) -> float:
        """Calculate recency score based on publication date"""
        try:
            if isinstance(pub_date, list):
                # Handle date-parts format [2024, 1, 15]
                pub_date = "-".join(map(str, pub_date[:3]))
            
            pub_dt = datetime.strptime(str(pub_date)[:10], "%Y-%m-%d")
            years_ago = (datetime.now() - pub_dt).days / 365
            
            # Score: 100 if <1 year, decreases with age
            if years_ago < 1:
                return 100
            elif years_ago < 2:
                return 90
            elif years_ago < 3:
                return 75
            elif years_ago < 5:
                return 60
            elif years_ago < 10:
                return 40
            else:
                return 20
        except:
            return 50  # Default for unknown dates
    
    def score_papers(self, papers: List[Dict]) -> List[Dict]:
        """Score all papers and return sorted list"""
        scored_papers = []
        
        for paper in papers:
            score_data = self.calculate_score(paper)
            paper["credibility_score"] = score_data["score"]
            paper["score_breakdown"] = score_data["breakdown"]
            paper["score_bonuses"] = score_data["bonuses"]
            scored_papers.append(paper)
        
        # Sort by score (highest first)
        scored_papers.sort(key=lambda x: x.get("credibility_score", 0), reverse=True)
        
        return scored_papers
    
    def get_distribution(self, papers: List[Dict]) -> Dict:
        """Get distribution of scores"""
        ranges = {
            "90-100": 0,
            "70-89": 0,
            "50-69": 0,
            "30-49": 0,
            "0-29": 0
        }
        
        for paper in papers:
            score = paper.get("credibility_score", 0)
            if score >= 90:
                ranges["90-100"] += 1
            elif score >= 70:
                ranges["70-89"] += 1
            elif score >= 50:
                ranges["50-69"] += 1
            elif score >= 30:
                ranges["30-49"] += 1
            else:
                ranges["0-29"] += 1
        
        return ranges
    
    def get_statistics(self, papers: List[Dict]) -> Dict:
        """Get statistics about scored papers"""
        scores = [p.get("credibility_score", 0) for p in papers]
        
        if not scores:
            return {}
        
        return {
            "count": len(scores),
            "average": round(sum(scores) / len(scores), 1),
            "min": min(scores),
            "max": max(scores),
            "median": sorted(scores)[len(scores) // 2]
        }


class AuthorAnalyzer:
    """Analyze author credibility"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
    
    def get_author_info(self, author_name: str) -> Dict:
        """Get author info from OpenAlex"""
        try:
            url = f"https://api.openalex.org/authors?search={author_name}&per_page=1"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get("results"):
                author = data["results"][0]
                return {
                    "h_index": author.get("h_index", 0),
                    "cited_by_count": author.get("cited_by_count", 0),
                    "works_count": author.get("works_count", 0),
                    "institution": author.get("last_known_institution", {}).get("display_name", ""),
                    "openalex_id": author.get("id", "")
                }
        except Exception as e:
            print(f"Author lookup error: {e}")
        
        return {}


class JournalAnalyzer:
    """Analyze journal credibility"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
    
    def get_journal_info(self, journal_name: str) -> Dict:
        """Get journal info from CrossRef"""
        try:
            url = f"https://api.crossref.org/journals/{journal_name}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if "message" in data:
                journal = data["message"]
                return {
                    "impact_factor": journal.get("impact-factor", {}).get("2023", 0),
                    "publisher": journal.get("publisher", ""),
                    "issn": journal.get("ISSN", [""])[0],
                    "title": journal.get("title", "")
                }
        except Exception as e:
            print(f"Journal lookup error: {e}")
        
        return {}


if __name__ == "__main__":
    # Test
    scorer = CredibilityScorer()
    
    test_papers = [
        {
            "title": "Test Paper 1",
            "citations": 500,
            "published": "2024-01-15",
            "peer_reviewed": True,
            "open_access": True,
            "journal_impact_score": 80
        },
        {
            "title": "Test Paper 2", 
            "citations": 10,
            "published": "2020-01-15",
            "peer_reviewed": True,
            "open_access": False,
            "journal_impact_score": 40
        }
    ]
    
    scored = scorer.score_papers(test_papers)
    for p in scored:
        print(f"{p['title']}: {p['credibility_score']}")
