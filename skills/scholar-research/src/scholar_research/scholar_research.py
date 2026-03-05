#!/usr/bin/env python3
"""
Scholar Research - Main Entry Point
Search, analyze, and summarize academic papers
"""

import json
import sys
import os
from typing import Dict, List

# Add scripts to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from search import ScholarSearch
from score import CredibilityScorer
from summarize import PaperSummarizer, TimelineGenerator, VisualizationGenerator
from figure_extract import FigureExtractor, PDFDownloader


class ScholarResearch:
    """Main class for scholar research skill"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")
        
        # Load config
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                self.config = json.load(f)
        else:
            self.config = {}
        
        # Initialize modules
        self.searcher = ScholarSearch(self.config)
        self.scorer = CredibilityScorer(self.config)
        self.summarizer = PaperSummarizer(self.config)
        self.timeline_gen = TimelineGenerator(self.config)
        self.viz_gen = VisualizationGenerator(self.config)
        self.figure_extractor = FigureExtractor(self.config)
        self.pdf_downloader = PDFDownloader(self.config)
    
    def search(self, query: str, fields: List[str] = None, max_results: int = 50) -> List[Dict]:
        """Search for papers"""
        
        print(f"🔍 Searching for: {query}")
        
        # Search all sources
        papers = self.searcher.search_all(query)
        
        print(f"   Found {len(papers)} papers")
        
        # Score papers
        scored_papers = self.scorer.score_papers(papers)
        
        return scored_papers
    
    def present_results(self, papers: List[Dict], top_n: int = 5, extract_figures: bool = False) -> str:
        """Present search results"""
        
        output = []
        
        # Get display settings
        display = self.config.get("display", {})
        if top_n is None:
            top_n = display.get("top_papers_count", 5)
        
        if extract_figures is None:
            extract_figures = display.get("extract_figures_for_top", 0) > 0
        
        # Statistics
        stats = self.scorer.get_statistics(papers)
        output.append(self.viz_gen.generate_statistics(stats))
        
        # Distribution
        if display.get("show_distribution_chart", True):
            dist = self.scorer.get_distribution(papers)
            output.append("\n" + self.viz_gen.generate_distribution_chart(dist))
        
        # Top papers
        output.append(f"\n{'='*50}")
        output.append(f"⭐ TOP PAPERS ({top_n})")
        output.append("="*50)
        
        for i, paper in enumerate(papers[:top_n], 1):
            entry = self.summarizer.format_paper_entry(paper, i)
            output.append("\n" + entry)
            
            # Extract figures for top papers if requested
            if extract_figures and paper.get("pdf_url"):
                output.append("\n   [Extracting figures...]")
        
        # Timeline
        if display.get("show_timeline", True):
            timeline_data = self.timeline_gen.generate_timeline(papers[top_n:])
            output.append("\n\n" + "="*50)
            output.append(f"📈 FIELD TIMELINE ({len(papers) - top_n} papers)")
            output.append("="*50)
            output.append(self.timeline_gen.format_timeline(timeline_data))
        
        return "\n".join(output)
    
    def run(self, query: str, **kwargs) -> str:
        """Run full research workflow"""
        
        # Search
        papers = self.search(query)
        
        # Present
        return self.present_results(papers, **kwargs)


def main():
    """CLI entry point"""
    
    if len(sys.argv) < 2:
        print("Usage: python scholar_research.py <query> [--top N] [--extract-figures]")
        sys.exit(1)
    
    query = sys.argv[1]
    
    # Parse args
    top_n = 5
    extract_figures = False
    
    for arg in sys.argv[2:]:
        if arg.startswith("--top="):
            top_n = int(arg.split("=")[1])
        elif arg == "--extract-figures":
            extract_figures = True
    
    # Run
    scholar = ScholarResearch()
    result = scholar.run(query, top_n=top_n, extract_figures=extract_figures)
    
    print(result)


if __name__ == "__main__":
    main()
