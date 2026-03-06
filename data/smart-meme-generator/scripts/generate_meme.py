#!/usr/bin/env python3
"""
Smart Meme Generator - Creates actual meme images via imgflip API.
Returns image URLs ready to share. No API key required for captioning.
"""

import json
import random
import re
import sys
import urllib.request
import urllib.parse
import urllib.error

# Top meme templates with imgflip IDs and text box counts
TEMPLATES = {
    "drake": {"id": "181913649", "name": "Drake Hotline Bling", "boxes": 2,
              "keywords": ["better", "prefer", "vs", "versus", "rather", "instead", "comparison", "option"]},
    "distracted": {"id": "112126428", "name": "Distracted Boyfriend", "boxes": 3,
                   "keywords": ["tempted", "switching", "attracted", "torn", "leaving", "new thing"]},
    "fine": {"id": "55311130", "name": "This Is Fine", "boxes": 2,
             "keywords": ["chaos", "disaster", "fine", "burning", "crisis", "broken", "crashing"]},
    "brain": {"id": "93895088", "name": "Expanding Brain", "boxes": 4,
              "keywords": ["levels", "evolution", "stages", "progression", "ascending", "galaxy"]},
    "cat": {"id": "188390779", "name": "Woman Yelling at Cat", "boxes": 2,
            "keywords": ["arguing", "yelling", "explaining", "confused", "blame"]},
    "change": {"id": "129242436", "name": "Change My Mind", "boxes": 1,
               "keywords": ["opinion", "controversial", "hot take", "unpopular", "debate", "prove"]},
    "buttons": {"id": "87743020", "name": "Two Buttons", "boxes": 3,
                "keywords": ["choose", "decision", "dilemma", "can't decide", "both", "or"]},
    "pikachu": {"id": "155067746", "name": "Surprised Pikachu", "boxes": 2,
                "keywords": ["obvious", "predictable", "shocked", "surprised", "of course"]},
    "stonks": {"id": "52223611", "name": "Stonks", "boxes": 1,
               "keywords": ["money", "profit", "invest", "crypto", "bitcoin", "trading", "gains", "stonks"]},
    "panik": {"id": "226297822", "name": "Panik Kalm Panik", "boxes": 3,
              "keywords": ["panic", "calm", "wait", "realize", "then", "actually"]},
    "buff_doge": {"id": "247375501", "name": "Buff Doge vs Cheems", "boxes": 4,
                  "keywords": ["then", "now", "old", "modern", "used to", "nowadays", "weak"]},
    "uno": {"id": "217743513", "name": "UNO Draw 25", "boxes": 2,
            "keywords": ["refuse", "won't", "never", "rather die", "draw 25"]},
    "always_has_been": {"id": "252600902", "name": "Always Has Been", "boxes": 2,
                        "keywords": ["always", "wait", "always has been", "the whole time"]},
    "gru_plan": {"id": "131940431", "name": "Gru's Plan", "boxes": 4,
                 "keywords": ["plan", "step", "backfire", "realize", "didn't think"]},
    "trade_offer": {"id": "309868304", "name": "Trade Offer", "boxes": 3,
                    "keywords": ["trade", "offer", "receive", "give", "deal"]},
    "bernie": {"id": "222403160", "name": "Bernie I Am Once Again Asking", "boxes": 1,
               "keywords": ["asking", "please", "again", "once again", "request"]},
    "left_exit": {"id": "124822590", "name": "Left Exit 12 Off Ramp", "boxes": 3,
                  "keywords": ["exit", "swerve", "ignore", "shortcut", "highway"]},
    "disaster_girl": {"id": "97984", "name": "Disaster Girl", "boxes": 2,
                      "keywords": ["destroy", "evil", "sinister", "burn", "smile"]},
    "hide_pain": {"id": "27813981", "name": "Hide the Pain Harold", "boxes": 2,
                  "keywords": ["hide", "pain", "pretend", "smile through", "dying inside"]},
    "think_about_it": {"id": "101288", "name": "Think About It", "boxes": 2,
                       "keywords": ["think about it", "smart", "can't", "if you", "technically"]},
}

def select_template(text):
    """Score templates by keyword match and pick the best one."""
    text_lower = text.lower()
    scores = {}
    for key, tmpl in TEMPLATES.items():
        score = sum(2 if kw in text_lower else 0 for kw in tmpl["keywords"])
        # Partial word matches get 1 point
        score += sum(1 for kw in tmpl["keywords"] if any(w in text_lower for w in kw.split()))
        scores[key] = score
    
    max_score = max(scores.values())
    if max_score > 0:
        top = [k for k, v in scores.items() if v == max_score]
        return random.choice(top)
    
    # Fallback heuristics
    if any(w in text_lower for w in ["work", "job", "meeting", "boss", "deadline"]):
        return "fine"
    if any(w in text_lower for w in ["code", "programming", "bug", "deploy"]):
        return random.choice(["drake", "fine", "pikachu"])
    if any(w in text_lower for w in ["crypto", "bitcoin", "stock", "market", "price"]):
        return random.choice(["stonks", "panik", "fine"])
    if any(w in text_lower for w in ["sleep", "tired", "morning", "night"]):
        return random.choice(["drake", "buttons", "hide_pain"])
    
    return random.choice(list(TEMPLATES.keys()))

def make_meme_image(template_id, texts):
    """Call imgflip API to generate actual meme image. Returns URL."""
    # imgflip API - free account required for image generation
    # Users should set IMGFLIP_USER and IMGFLIP_PASS env vars, or use defaults
    import os
    username = os.environ.get("IMGFLIP_USER", "davememebot")
    password = os.environ.get("IMGFLIP_PASS", "DaveMakes3Memes!")
    
    data = {
        "template_id": template_id,
        "username": username,
        "password": password,
    }
    for i, text in enumerate(texts):
        data[f"text{i}"] = text
    
    encoded = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(
        "https://api.imgflip.com/caption_image",
        data=encoded,
        headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "openclaw-meme/1.0"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            if result.get("success"):
                return result["data"]["url"]
            else:
                return None
    except Exception as e:
        print(f"Error generating image: {e}", file=sys.stderr)
        return None

def generate(topic, template_key=None):
    """Generate a meme from a topic. Returns dict with url, template, captions."""
    if not template_key:
        template_key = select_template(topic)
    
    tmpl = TEMPLATES[template_key]
    
    # The captions are generated by the LLM calling this script.
    # This script handles template selection and image generation.
    # For CLI testing, we provide placeholder captions.
    return {
        "template_key": template_key,
        "template_name": tmpl["name"],
        "template_id": tmpl["id"],
        "boxes": tmpl["boxes"],
        "topic": topic
    }

def main():
    """CLI interface for testing."""
    import argparse
    parser = argparse.ArgumentParser(description="Smart Meme Generator")
    parser.add_argument("topic", nargs="?", help="Topic or situation for the meme")
    parser.add_argument("--template", "-t", help="Force specific template key")
    parser.add_argument("--captions", "-c", nargs="+", help="Provide captions directly (generates image)")
    parser.add_argument("--list", "-l", action="store_true", help="List all templates")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()
    
    if args.list:
        print("\n📋 Available Templates:\n")
        for key, tmpl in sorted(TEMPLATES.items()):
            print(f"  {key:20s} | {tmpl['name']:30s} | {tmpl['boxes']} text boxes | Keywords: {', '.join(tmpl['keywords'][:3])}")
        return
    
    if args.captions:
        # Generate actual image with provided captions
        if not args.template and not args.topic:
            print("Error: provide --template or a topic when using --captions", file=sys.stderr)
            sys.exit(1)
        
        template_key = args.template or select_template(args.topic or " ".join(args.captions))
        tmpl = TEMPLATES[template_key]
        
        print(f"\n🎭 Generating: {tmpl['name']}")
        url = make_meme_image(tmpl["id"], args.captions)
        
        if url:
            if args.json:
                print(json.dumps({"url": url, "template": tmpl["name"], "captions": args.captions}))
            else:
                print(f"✅ Meme created!")
                print(f"🖼️  {url}")
                print(f"📝 Template: {tmpl['name']}")
                for i, cap in enumerate(args.captions, 1):
                    print(f"   Box {i}: {cap}")
        else:
            print("❌ Failed to generate image", file=sys.stderr)
            sys.exit(1)
        return
    
    if not args.topic:
        parser.print_help()
        return
    
    # Template selection mode
    result = generate(args.topic, args.template)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n🎭 Best template: {result['template_name']}")
        print(f"🆔 Template ID: {result['template_id']}")
        print(f"📦 Text boxes: {result['boxes']}")
        print(f"\n💡 To generate the image, call again with captions:")
        print(f"   python3 generate_meme.py --template {result['template_key']} --captions \"text1\" \"text2\"")

if __name__ == "__main__":
    main()
