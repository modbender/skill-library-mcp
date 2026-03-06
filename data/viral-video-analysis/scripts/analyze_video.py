#!/usr/bin/env python3
"""
Viral Video Analysis - Analyze videos and generate creator feedback
Usage: 
  python analyze_video.py <video_url>              # Single video analysis
  python analyze_video.py --batch <excel_path>    # Batch analysis
"""

import sys
import json
import requests
import argparse

import os

BASE_URL = "https://mavi-backend.memories.ai/serve/api/v2"
API_KEY = os.environ.get("MEMORIES_API_KEY", "")
if not API_KEY:
    print("Warning: MEMORIES_API_KEY not set. Get your key at https://api-tools.memories.ai")
HEADERS = {"Authorization": API_KEY}

# Thresholds
WORD_COUNT_GOOD = 100
WORD_COUNT_BAD = 150


def detect_platform(url: str) -> str:
    """Detect platform from URL."""
    url = url.lower()
    if "tiktok" in url:
        return "tiktok"
    if "instagram" in url:
        return "instagram"
    if "twitter" in url or "x.com" in url:
        return "twitter"
    if "facebook" in url:
        return None  # Not supported
    return "youtube"


def get_transcript(video_url: str, platform: str = None) -> dict:
    """Get audio transcript from Memories.ai API."""
    if platform is None:
        platform = detect_platform(video_url)
    
    if not platform:
        return {"error": "Platform not supported (Facebook)"}
    
    try:
        resp = requests.post(
            f"{BASE_URL}/{platform}/video/transcript",
            headers=HEADERS,
            json={"video_url": video_url, "channel": "rapid"},
            timeout=60
        )
        data = resp.json()
        if data.get("success"):
            transcripts = data.get("data", {}).get("transcripts", [])
            if transcripts:
                text = transcripts[0].get("text", "")
                return {
                    "text": text,
                    "word_count": len(text.split()),
                    "platform": platform
                }
        return {"error": data.get("msg", "Unknown error")}
    except Exception as e:
        return {"error": str(e)}


def analyze_video(url: str) -> dict:
    """Analyze a single video and return metrics + feedback."""
    platform = detect_platform(url)
    result = get_transcript(url, platform)
    
    if "error" in result:
        return {"url": url, "error": result["error"]}
    
    word_count = result["word_count"]
    
    # Determine status
    if word_count < WORD_COUNT_GOOD:
        status = "GOOD"
        status_emoji = "✅"
    elif word_count < WORD_COUNT_BAD:
        status = "OK"
        status_emoji = "⚠️"
    else:
        status = "BAD"
        status_emoji = "❌"
    
    # Generate issues
    issues = []
    feedback = []
    
    if word_count >= WORD_COUNT_BAD:
        issues.append("Too many words (>150)")
        feedback.append(f"Word count: {word_count} words. Top performers use <100. Replace verbal explanations with visual demonstrations.")
    elif word_count >= WORD_COUNT_GOOD:
        issues.append("Word count slightly high (100-150)")
        feedback.append(f"Word count: {word_count} words. Consider reducing to <100 for better performance.")
    
    # Always add this reminder
    feedback.append("Remember: Ads reach people who don't follow you. You have 3 seconds to grab attention!")
    
    return {
        "url": url,
        "platform": platform,
        "word_count": word_count,
        "status": status,
        "status_emoji": status_emoji,
        "issues": issues,
        "feedback": feedback,
        "transcript_preview": result["text"][:300] + "..." if len(result["text"]) > 300 else result["text"]
    }


def print_analysis(analysis: dict):
    """Print formatted analysis."""
    if "error" in analysis:
        print(f"❌ Error: {analysis['error']}")
        return
    
    print(f"\n{'='*60}")
    print(f"📹 VIDEO ANALYSIS")
    print(f"{'='*60}")
    print(f"URL: {analysis['url']}")
    print(f"Platform: {analysis['platform']}")
    print(f"\n📊 METRICS:")
    print(f"   Word Count: {analysis['word_count']} {analysis['status_emoji']} ({analysis['status']})")
    print(f"   Target: <100 words")
    
    if analysis['issues']:
        print(f"\n⚠️ ISSUES:")
        for issue in analysis['issues']:
            print(f"   • {issue}")
    
    print(f"\n💬 FEEDBACK FOR CREATOR:")
    for fb in analysis['feedback']:
        print(f"   • {fb}")
    
    print(f"\n📝 TRANSCRIPT PREVIEW:")
    print(f"   \"{analysis['transcript_preview']}\"")
    print(f"\n{'='*60}")


def generate_feedback_template(analysis: dict) -> str:
    """Generate copy-paste feedback for creator."""
    if "error" in analysis:
        return f"Could not analyze: {analysis['error']}"
    
    template = f"""
Hi [Creator],

Thanks for your video! Here's feedback to help boost performance:

**Word Count Analysis:**
Your video: {analysis['word_count']} words
Target: <100 words
Status: {analysis['status']}

**Recommendations:**
"""
    for fb in analysis['feedback']:
        template += f"• {fb}\n"
    
    template += """
**Reference Videos (what "good" looks like):**
• instagram.com/reel/Cy1zs4gLGFG (46 words, 15s for 3 outfits)
• instagram.com/reel/DEybxPbNeOl (56 words, quick visual showcase)

Best,
[Team]
"""
    return template


def main():
    parser = argparse.ArgumentParser(description='Analyze video performance')
    parser.add_argument('url', nargs='?', help='Video URL to analyze')
    parser.add_argument('--batch', help='Excel file for batch analysis')
    parser.add_argument('--feedback', action='store_true', help='Generate feedback template')
    
    args = parser.parse_args()
    
    if args.batch:
        import pandas as pd
        df = pd.read_excel(args.batch)
        df.columns = [c.lower().replace('sum of ', '').replace(' ', '_') for c in df.columns]
        
        url_col = 'video_url' if 'video_url' in df.columns else 'row_labels'
        
        print(f"Analyzing {len(df)} videos...")
        for i, row in df.head(10).iterrows():  # Sample first 10
            url = row[url_col]
            analysis = analyze_video(url)
            print_analysis(analysis)
        
    elif args.url:
        analysis = analyze_video(args.url)
        print_analysis(analysis)
        
        if args.feedback:
            print("\n📋 FEEDBACK TEMPLATE (copy-paste):")
            print(generate_feedback_template(analysis))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
