#!/usr/bin/env python3
"""
Test script for ASCII Art Generator skill.
"""

import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from basic_shapes import create_box, create_circle, create_tree, create_heart, create_progress_bar
from text_banners import create_banner, create_header, create_centered_text, create_quote
from conceptual_diagrams import create_flowchart, create_mind_map, create_process_diagram, create_timeline

def test_all_functions():
    """Test all major functions of the skill."""
    
    print("=" * -60)
    print("Testing ASCII Art Generator Skill")
    print("=" * -60)
    
    print("\n1. Testing Basic Shapes:")
    print("-" * 40)
    
    print("Box (rounded):")
    print(create_box(15, 6, 'rounded'))
    
    print("\nCircle (filled):")
    print(create_circle(4, True))
    
    print("\nTree:")
    print(create_tree(8))
    
    print("\nHeart:")
    print(create_heart(3))
    
    print("\nProgress Bar:")
    print(create_progress_bar(75, 25, 'gradient'))
    
    print("\n2. Testing Text Banners:")
    print("-" * 40)
    
    print("Fancy Banner:")
    print(create_banner("Welcome", 'fancy', 25))
    
    print("\nHeader Level 1:")
    print(create_header("Main Title", 1, 'center'))
    
    print("\nCentered Text with Border:")
    print(create_centered_text("Test Message", 30, True))
    
    print("\nQuote:")
    print(create_quote("The only limit is your imagination.", "Anonymous", 40))
    
    print("\n3. Testing Conceptual Diagrams:")
    print("-" * 40)
    
    print("Flowchart:")
    steps = ["Start", "Input", "Process", "Output", "End"]
    print(create_flowchart(steps))
    
    print("\nSimple Mind Map:")
    branches = [
        ("Research", []),
        ("Design", []),
        ("Develop", [])
    ]
    print(create_mind_map("Project", branches))
    
    print("\nProcess Diagram:")
    stages = ["Collect", "Analyze", "Visualize", "Share"]
    feedback = [(3, 1, "Refine")]
    print(create_process_diagram("Data Pipeline", stages, feedback))
    
    print("\nTimeline:")
    events = ["Kickoff", "Alpha", "Beta", "Launch"]
    dates = ["2026-01-01", "2026-02-01", "2026-03-01", "2026-04-01"]
    print(create_timeline(events, dates))
    
    print("\n" + "=" * -60)
    print("All tests completed successfully!")
    print("=" * -60)

if __name__ == "__main__":
    test_all_functions()