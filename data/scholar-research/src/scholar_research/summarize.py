#!/usr/bin/env python3
"""
Scholar Research - Summarization Module
Summarizes academic papers and generates field timelines
"""

import requests
import json
from typing import Dict, List
from datetime import datetime


class PaperSummarizer:
    """Summarizes academic papers"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
    
    def summarize_abstract(self, abstract: str, max_length: int = 200) -> str:
        """Summarize paper abstract"""
        if not abstract:
            return "No abstract available."
        
        # Simple extraction - in production would use LLM
        sentences = abstract.split(". ")
        if len(sentences) <= 3:
            return abstract
        
        # Return first 2-3 sentences as summary
        summary = ". ".join(sentences[:2])
        if len(summary) > max_length:
            summary = summary[:max_length].rsplit(".", 1)[0] + "."
        
        return summary + "."
    
    def summarize_methodology(self, paper: Dict) -> str:
        """Extract methodology from paper"""
        # In production, would use AI to analyze full text
        method = paper.get("methodology", "")
        
        if method:
            return method
        
        # Placeholder - would extract from PDF
        return "Methodology details available in full paper. Key approach involves experimental validation and comparative analysis."
    
    def generate_detailed_summary(self, paper: Dict) -> Dict:
        """Generate comprehensive summary for top papers"""
        
        return {
            "title": paper.get("title", "Untitled"),
            "authors": paper.get("authors", []),
            "published": paper.get("published", ""),
            "journal": paper.get("journal", ""),
            "doi": paper.get("doi", ""),
            "score": paper.get("credibility_score", 0),
            "citations": paper.get("citations", 0),
            
            "summary": self.summarize_abstract(paper.get("abstract", "")),
            
            "methodology": self.summarize_methodology(paper),
            
            "key_findings": paper.get("key_findings", [
                "Key findings available in full paper",
                "See PDF for complete analysis"
            ]),
            
            "limitations": paper.get("limitations", [
                "Further validation needed",
                "Limited sample size in study"
            ])
        }
    
    def format_paper_entry(self, paper: Dict, index: int = 1) -> str:
        """Format paper as readable entry"""
        
        s = paper.get("credibility_score", 0)
        citations = paper.get("citations", 0)
        
        entry = f"""[{index}] {paper.get('title', 'Untitled')} ({paper.get('published', 'N/A')[:4]})
    Score: {s:.0f}/100 | Citations: {citations}
    📄 PDF | 📊 Figures | 🔬 SI
    
    Summary: {self.summarize_abstract(paper.get('abstract', ''), 300)}
    
    Methodology: {self.summarize_methodology(paper)}"""
        
        return entry


class TimelineGenerator:
    """Generates field evolution timeline"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
    
    def generate_timeline(self, papers: List[Dict]) -> Dict:
        """Generate timeline from papers"""
        
        # Group papers by year
        year_papers = {}
        
        for paper in papers:
            pub_date = str(paper.get("published", ""))
            
            # Extract year
            if "-" in pub_date:
                year = pub_date.split("-")[0]
            elif len(pub_date) == 4 and pub_date.isdigit():
                year = pub_date
            else:
                year = "Unknown"
            
            if year not in year_papers:
                year_papers[year] = []
            year_papers[year].append(paper)
        
        # Sort years
        sorted_years = sorted(year_papers.keys(), reverse=True)
        
        # Generate timeline entries
        timeline = []
        
        for year in sorted_years:
            if year == "Unknown":
                continue
                
            papers_this_year = year_papers[year]
            
            # Extract key themes/topics
            themes = self._extract_themes(papers_this_year)
            
            # Find major breakthroughs (highest scored)
            top_paper = max(papers_this_year, key=lambda x: x.get("credibility_score", 0))
            
            timeline.append({
                "year": year,
                "paper_count": len(papers_this_year),
                "top_paper": {
                    "title": top_paper.get("title", ""),
                    "score": top_paper.get("credibility_score", 0),
                    "citations": top_paper.get("citations", 0)
                },
                "themes": themes,
                "trends": self._identify_trends(papers_this_year)
            })
        
        return {
            "timeline": timeline,
            "total_papers": len(papers),
            "year_distribution": {year: len(year_papers[year]) for year in sorted_years}
        }
    
    def _extract_themes(self, papers: List[Dict]) -> List[str]:
        """Extract main themes from papers"""
        # Simple extraction - would use NLP in production
        themes = []
        
        # Get unique journals/venues
        venues = set()
        for p in papers:
            venue = p.get("journal", "")
            if venue:
                venues.add(venue[:30])
        
        # Placeholder - would use topic modeling
        return list(venues)[:3] if venues else ["Research topics"]
    
    def _identify_trends(self, papers: List[Dict]) -> List[str]:
        """Identify trends from papers"""
        # Placeholder - would use trend analysis
        return [
            "Continued research activity",
            "Growing interest in field"
        ]
    
    def format_timeline(self, timeline_data: Dict) -> str:
        """Format timeline as readable text"""
        
        timeline = timeline_data.get("timeline", [])
        
        if not timeline:
            return "No timeline data available."
        
        output = []
        output.append(f"📈 FIELD TIMELINE ({timeline_data.get('total_papers', 0)} papers)")
        output.append("─" * 40)
        
        for entry in timeline:
            year = entry.get("year", "")
            count = entry.get("paper_count", 0)
            top = entry.get("top_paper", {})
            
            # Visual bar
            bar = "█" * min(count, 20)
            
            output.append(f"\n{year}: {bar} {count} papers")
            
            if top.get("title"):
                output.append(f"   → Major: {top['title'][:50]}...")
            
            themes = entry.get("themes", [])
            if themes:
                output.append(f"   → Focus: {', '.join(themes[:2])}")
        
        return "\n".join(output)


class VisualizationGenerator:
    """Generates visualizations"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
    
    def generate_distribution_chart(self, distribution: Dict) -> str:
        """Generate text-based distribution chart"""
        
        total = sum(distribution.values())
        if total == 0:
            return "No data"
        
        # Find max for scaling
        max_count = max(distribution.values())
        
        output = ["📊 Credibility Distribution", ""]
        
        ranges = [
            ("90-100", "★ Top"),
            ("70-89", ""),
            ("50-69", ""),
            ("30-49", ""),
            ("0-29", "")
        ]
        
        for (range_label, suffix), (key, count) in zip(ranges, distribution.items()):
            bar_len = int((count / max_count) * 20) if max_count > 0 else 0
            bar = "█" * bar_len + "░" * (20 - bar_len)
            output.append(f"Score {range_label}: {bar} ({count} papers) {suffix}")
        
        return "\n".join(output)
    
    def generate_statistics(self, stats: Dict) -> str:
        """Generate statistics summary"""
        
        return f"""
📊 Statistics
──────────────────────────────────────
Total Papers: {stats.get('count', 0)}
Average Score: {stats.get('average', 0):.1f}/100
Score Range: {stats.get('min', 0):.0f} - {stats.get('max', 0):.0f}
Median Score: {stats.get('median', 0):.1f}
──────────────────────────────────────"""


if __name__ == "__main__":
    # Test
    papers = [
        {"title": "Paper A", "published": "2024-01", "citations": 100, "credibility_score": 95, "journal": "Nature", "abstract": "This is a test abstract about machine learning."},
        {"title": "Paper B", "published": "2024-02", "citations": 50, "credibility_score": 80, "journal": "Science", "abstract": "Another test about AI."},
        {"title": "Paper C", "published": "2023-01", "citations": 200, "credibility_score": 90, "journal": "Cell", "abstract": "Biology paper."},
        {"title": "Paper D", "published": "2022-01", "citations": 10, "credibility_score": 60, "journal": "IEEE", "abstract": "Engineering paper."},
    ]
    
    summ = PaperSummarizer()
    timeline = TimelineGenerator()
    viz = VisualizationGenerator()
    
    print("=== Papers ===")
    for p in papers:
        print(summ.format_paper_entry(p))
    
    print("\n=== Timeline ===")
    tl = timeline.generate_timeline(papers)
    print(timeline.format_timeline(tl))
    
    print("\n=== Distribution ===")
    from scripts.score import CredibilityScorer
    scorer = CredibilityScorer()
    scored = scorer.score_papers(papers)
    dist = scorer.get_distribution(scored)
    print(viz.generate_distribution_chart(dist))
