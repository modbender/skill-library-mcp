#!/usr/bin/env python3
"""
Convert raw Dribbble references into structured style cards.
Each style card captures the visual DNA of a design for prompt generation.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


# Default style analysis prompts for AI agents
ANALYSIS_PROMPT = """Analyze this design and extract a style card with these fields:

- palette: List of 3-6 dominant hex colors
- composition: Layout type (e.g., centered, asymmetric, grid, split, diagonal, layered)
- typography: Font characteristics (e.g., bold sans-serif, thin serif, handwritten, monospace)
- mood: 2-3 emotional descriptors (e.g., bold and energetic, calm and minimal, playful and warm)
- textures: Surface qualities (e.g., glass morphism, grain, matte, metallic, paper)
- lighting: Light description (e.g., soft diffused, harsh directional, neon glow, golden hour)
- depth: Spatial quality (e.g., flat, layered with shadows, 3D perspective, isometric)
- contrast: High/medium/low
- style_tags: Design style categories (e.g., brutalist, minimalist, retro, futuristic, organic)

Return as JSON."""


def build_style_cards(references: list[dict], existing_cards: list[dict] | None = None) -> list[dict]:
    """
    Build style cards from references.
    
    In automated mode (no AI), creates skeleton cards from available metadata.
    The AI agent should enhance these with visual analysis when images are available.
    """
    existing_urls = set()
    if existing_cards:
        existing_urls = {c.get("source_url", "") for c in existing_cards}

    cards = list(existing_cards) if existing_cards else []

    for ref in references:
        if ref["url"] in existing_urls:
            continue

        card = {
            "id": f"sc_{len(cards) + 1:04d}",
            "title": ref.get("title", "Untitled"),
            "source_url": ref["url"],
            "image_url": ref.get("image_url", ""),
            "palette": [],
            "composition": "unknown",
            "typography": "unknown",
            "mood": [],
            "textures": [],
            "lighting": "unknown",
            "depth": "unknown",
            "contrast": "medium",
            "style_tags": _extract_tags(ref),
            "description": ref.get("description", ""),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "analyzed": False,
        }
        cards.append(card)

    return cards


def _extract_tags(ref: dict) -> list[str]:
    """Extract basic style tags from title and description."""
    text = f"{ref.get('title', '')} {ref.get('description', '')}".lower()
    
    tag_keywords = {
        "minimal": ["minimal", "minimalist", "clean", "simple"],
        "bold": ["bold", "strong", "heavy", "thick"],
        "retro": ["retro", "vintage", "80s", "90s", "nostalgic"],
        "futuristic": ["futuristic", "future", "sci-fi", "cyber", "neon"],
        "organic": ["organic", "natural", "nature", "botanical"],
        "geometric": ["geometric", "geometry", "shapes", "angular"],
        "gradient": ["gradient", "gradients", "color transition"],
        "3d": ["3d", "three-dimensional", "isometric", "render"],
        "flat": ["flat", "flat design", "2d"],
        "brutalist": ["brutalist", "brutal", "raw"],
        "glassmorphism": ["glass", "glassmorphism", "frosted", "blur"],
        "dark-mode": ["dark", "dark mode", "dark theme", "night"],
        "illustration": ["illustration", "illustrated", "drawing", "artwork"],
        "typography": ["typography", "type", "lettering", "font"],
        "ui-design": ["ui", "ux", "interface", "app", "dashboard", "website"],
        "branding": ["brand", "branding", "logo", "identity"],
        "motion": ["motion", "animation", "animated", "kinetic"],
        "photography": ["photo", "photography", "photograph"],
    }

    found_tags = []
    for tag, keywords in tag_keywords.items():
        if any(kw in text for kw in keywords):
            found_tags.append(tag)

    return found_tags if found_tags else ["untagged"]


def enhance_card_prompt(card: dict) -> str:
    """Generate a prompt for an AI agent to analyze the design image and fill in the style card."""
    return f"""{ANALYSIS_PROMPT}

Design title: {card['title']}
Design URL: {card['source_url']}
Image URL: {card['image_url']}
Current tags: {', '.join(card['style_tags'])}

Update the style card fields based on your visual analysis."""


def select_cards(cards: list[dict], goal: str, count: int = 3) -> list[dict]:
    """Select the most relevant style cards for a given prompt goal."""
    goal_lower = goal.lower()
    
    scored = []
    for card in cards:
        score = 0
        card_text = f"{card.get('title', '')} {' '.join(card.get('style_tags', []))} {' '.join(card.get('mood', []))} {card.get('description', '')}".lower()
        
        # Score based on keyword overlap
        goal_words = set(re.findall(r'\w+', goal_lower))
        card_words = set(re.findall(r'\w+', card_text))
        overlap = goal_words & card_words
        score += len(overlap) * 2
        
        # Bonus for analyzed cards
        if card.get("analyzed"):
            score += 1
        
        # Bonus for cards with complete data
        if card.get("palette"):
            score += 1
        if card.get("mood"):
            score += 1
            
        scored.append((score, card))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    return [card for _, card in scored[:count]]


def main():
    parser = argparse.ArgumentParser(description="Build and manage style cards from visual references")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Build command
    build_parser = subparsers.add_parser("build", help="Build style cards from references")
    build_parser.add_argument("--input", "-i", default="data/references.json", help="Input references JSON")
    build_parser.add_argument("--output", "-o", default="data/style_cards.json", help="Output style cards JSON")
    build_parser.add_argument("--append", action="store_true", help="Append to existing cards")

    # Select command
    select_parser = subparsers.add_parser("select", help="Select relevant cards for a goal")
    select_parser.add_argument("--cards", "-c", default="data/style_cards.json", help="Style cards JSON")
    select_parser.add_argument("--goal", "-g", required=True, help="Prompt goal description")
    select_parser.add_argument("--count", "-n", type=int, default=3, help="Number of cards to select")

    # Prompt command
    prompt_parser = subparsers.add_parser("prompt", help="Generate analysis prompt for a card")
    prompt_parser.add_argument("--cards", "-c", default="data/style_cards.json", help="Style cards JSON")
    prompt_parser.add_argument("--id", required=True, help="Style card ID to analyze")

    # Stats command
    subparsers.add_parser("stats", help="Show style card statistics")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "build":
        input_path = Path(args.input)
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if not input_path.exists():
            print(f"Error: {input_path} not found. Run scrape_dribbble.py first.", file=sys.stderr)
            sys.exit(1)

        with open(input_path, "r", encoding="utf-8") as f:
            references = json.load(f)

        existing = None
        if args.append and output_path.exists():
            with open(output_path, "r", encoding="utf-8") as f:
                existing = json.load(f)

        cards = build_style_cards(references, existing)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(cards, f, indent=2, ensure_ascii=False)

        analyzed = sum(1 for c in cards if c.get("analyzed"))
        print(f"Built {len(cards)} style cards ({analyzed} analyzed)")
        print(f"Saved to {output_path}")

    elif args.command == "select":
        cards_path = Path(args.cards)
        if not cards_path.exists():
            print(f"Error: {cards_path} not found.", file=sys.stderr)
            sys.exit(1)

        with open(cards_path, "r", encoding="utf-8") as f:
            cards = json.load(f)

        selected = select_cards(cards, args.goal, args.count)
        print(f"Selected {len(selected)} cards for: {args.goal}\n")
        for card in selected:
            print(f"  [{card['id']}] {card['title']}")
            print(f"    Tags: {', '.join(card.get('style_tags', []))}")
            print(f"    URL: {card['source_url']}")
            print()

    elif args.command == "prompt":
        cards_path = Path(args.cards)
        if not cards_path.exists():
            print(f"Error: {cards_path} not found.", file=sys.stderr)
            sys.exit(1)

        with open(cards_path, "r", encoding="utf-8") as f:
            cards = json.load(f)

        card = next((c for c in cards if c["id"] == args.id), None)
        if not card:
            print(f"Error: Card {args.id} not found.", file=sys.stderr)
            sys.exit(1)

        print(enhance_card_prompt(card))

    elif args.command == "stats":
        cards_path = Path("data/style_cards.json")
        if not cards_path.exists():
            print("No style cards found. Run 'build' first.")
            return

        with open(cards_path, "r", encoding="utf-8") as f:
            cards = json.load(f)

        analyzed = sum(1 for c in cards if c.get("analyzed"))
        all_tags = {}
        for card in cards:
            for tag in card.get("style_tags", []):
                all_tags[tag] = all_tags.get(tag, 0) + 1

        print(f"Total cards: {len(cards)}")
        print(f"Analyzed: {analyzed}")
        print(f"Pending analysis: {len(cards) - analyzed}")
        print(f"\nTop tags:")
        for tag, count in sorted(all_tags.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {tag}: {count}")


if __name__ == "__main__":
    main()
