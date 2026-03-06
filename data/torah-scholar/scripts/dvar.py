#!/usr/bin/env python3
"""
Dvar Torah Generator - AI-assisted Torah insights
Pulls sources from Sefaria and structures a dvar Torah.
"""

import json
import sys
import os

# Import sefaria module from same directory
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from sefaria import get_text, get_links, get_parsha, search, format_text, strip_html

def get_parsha_info():
    """Get this week's parsha details."""
    parsha = get_parsha()
    if "error" in parsha:
        return None
    return parsha

def get_parsha_opening(ref: str, verses: int = 5) -> dict:
    """Get the opening verses of a parsha."""
    # Extract book and starting chapter:verse from ref like "Exodus 27:20-30:10"
    parts = ref.split("-")[0]  # Get "Exodus 27:20"
    
    # Get the text
    result = get_text(parts)
    return result

def get_key_commentaries(ref: str) -> list:
    """Get key commentaries on a verse."""
    links = get_links(ref)
    if isinstance(links, dict) and "error" in links:
        return []
    
    # Filter for main commentaries
    key_commentators = ["Rashi", "Ramban", "Sforno", "Or HaChaim", "Ibn Ezra", "Kli Yakar"]
    commentaries = []
    
    for link in links:
        ref_text = link.get("ref", "")
        for commentator in key_commentators:
            if commentator in ref_text:
                commentaries.append({
                    "commentator": commentator,
                    "ref": ref_text,
                    "he": link.get("he", ""),
                    "text": link.get("text", "")
                })
                break
    
    return commentaries[:5]  # Limit to 5 commentaries

def find_related_sources(query: str, limit: int = 3) -> list:
    """Find related sources on a theme."""
    results = search(query, limit=limit)
    
    if "error" in results:
        return []
    
    hits = results.get("hits", {}).get("hits", [])
    sources = []
    
    for hit in hits[:limit]:
        ref_id = hit.get("_id", "")
        ref = ref_id.split(" (")[0] if " (" in ref_id else ref_id
        highlight = hit.get("highlight", {})
        snippets = highlight.get("naive_lemmatizer", [])
        
        sources.append({
            "ref": ref,
            "snippet": snippets[0] if snippets else ""
        })
    
    return sources

def generate_dvar_structure(parsha_name: str = None, ref: str = None, theme: str = None) -> str:
    """
    Generate a structured dvar Torah outline with sources.
    
    Args:
        parsha_name: Name of parsha (e.g., "Tetzaveh")
        ref: Specific verse reference to focus on
        theme: Optional theme to explore
    
    Returns:
        Markdown-formatted dvar Torah structure with sources
    """
    output = []
    
    # Get parsha info if not provided
    if not parsha_name and not ref:
        parsha_info = get_parsha_info()
        if parsha_info:
            parsha_name = parsha_info.get("parsha")
            ref = parsha_info.get("ref")
            hebrew_name = parsha_info.get("hebrew", "")
        else:
            return "Error: Could not get parsha information"
    else:
        hebrew_name = ""
    
    output.append(f"# Dvar Torah: Parashat {parsha_name}")
    if hebrew_name:
        output.append(f"## פרשת {hebrew_name}")
    output.append("")
    
    # Get opening verses
    if ref:
        output.append("## Opening Verses")
        output.append(f"**Source:** {ref}")
        output.append("")
        
        # Get the actual text
        opening_ref = ref.split("-")[0]  # Get first part
        text_data = get_text(opening_ref)
        
        if "error" not in text_data:
            he_text = text_data.get("he", [])
            en_text = text_data.get("text", [])
            
            # Show first 3 verses
            for i in range(min(3, len(he_text) if isinstance(he_text, list) else 1)):
                if isinstance(he_text, list) and i < len(he_text):
                    clean_he = strip_html(str(he_text[i]))
                    output.append(f"**{i+1}.** {clean_he}")
                if isinstance(en_text, list) and i < len(en_text):
                    clean_en = strip_html(str(en_text[i]))
                    output.append(f"   *{clean_en}*")
                output.append("")
    
    # Get commentaries on the opening verse
    if ref:
        opening_verse = ref.split("-")[0]
        output.append("## Classical Commentaries")
        output.append("")
        
        commentaries = get_key_commentaries(opening_verse)
        if commentaries:
            for comm in commentaries:
                output.append(f"### {comm['commentator']}")
                output.append(f"**{comm['ref']}**")
                if comm.get("text"):
                    clean_text = strip_html(str(comm["text"]))[:300]
                    output.append(f"> {clean_text}...")
                elif comm.get("he"):
                    clean_he = strip_html(str(comm["he"]))[:200]
                    output.append(f"> {clean_he}...")
                output.append("")
        else:
            output.append("*No commentaries found for this reference*")
            output.append("")
    
    # Find thematic connections if theme provided
    if theme:
        output.append(f"## Related Sources: {theme}")
        output.append("")
        
        related = find_related_sources(theme)
        if related:
            for source in related:
                output.append(f"- **{source['ref']}**")
                if source.get("snippet"):
                    clean_snippet = source["snippet"].replace("<b>", "**").replace("</b>", "**")
                    output.append(f"  > {clean_snippet}")
                output.append("")
    
    # Add structure suggestions
    output.append("## Suggested Structure")
    output.append("")
    output.append("1. **Hook**: Start with a question or observation from the opening verses")
    output.append("2. **Problem**: What difficulty or tension exists in the text?")
    output.append("3. **Sources**: Bring the commentaries above to explore answers")
    output.append("4. **Resolution**: Synthesize insights from the sources")
    output.append("5. **Application**: Connect to modern life or personal growth")
    output.append("")
    
    # Add key themes to explore
    output.append("## Key Themes to Explore")
    output.append("")
    if parsha_name:
        # Search for themes related to this parsha
        themes = find_related_sources(parsha_name, limit=5)
        if themes:
            for t in themes:
                output.append(f"- {t['ref']}")
    
    output.append("")
    output.append("---")
    output.append("*Sources powered by Sefaria. Customize and expand with your own insights.*")
    
    return "\n".join(output)


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        # Default: generate for this week's parsha
        print(generate_dvar_structure())
        return
    
    command = sys.argv[1]
    
    if command == "parsha":
        # Generate for this week's parsha
        print(generate_dvar_structure())
    
    elif command == "ref" and len(sys.argv) >= 3:
        # Generate for specific reference
        ref = " ".join(sys.argv[2:])
        print(generate_dvar_structure(ref=ref))
    
    elif command == "theme" and len(sys.argv) >= 3:
        # Generate with specific theme
        theme = " ".join(sys.argv[2:])
        print(generate_dvar_structure(theme=theme))
    
    elif command == "help" or command == "-h":
        print("""
Dvar Torah Generator

Usage:
    dvar.py                     Generate for this week's parsha
    dvar.py parsha              Generate for this week's parsha
    dvar.py ref <reference>     Generate for specific verse/section
    dvar.py theme <theme>       Generate with specific theme focus

Examples:
    dvar.py
    dvar.py ref "Genesis 12:1"
    dvar.py theme "faith and trust"
""")
    
    else:
        # Treat as parsha name or ref
        ref = " ".join(sys.argv[1:])
        print(generate_dvar_structure(ref=ref))


if __name__ == "__main__":
    main()
