#!/usr/bin/env python3
"""
last30days Research + Gemini Synthesis
Wraps last30days research with Gemini for briefings and prompts.
"""
import json
import os
import subprocess
import sys
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

# Paths
SKILL_DIR = Path(__file__).parent.parent
LAST30_SCRIPT = SKILL_DIR / "scripts" / "last30days.py"
OUTPUT_DIR = Path(os.environ.get("LAST30DAYS_OUTPUT_DIR", "/home/openclaw/.openclaw/workspace/total-recall/last30days"))
BRIEFINGS_DIR = OUTPUT_DIR / "briefings"
PROMPTS_DIR = OUTPUT_DIR / "prompts"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

def run_research(topic: str, quick: bool = True) -> dict:
    """Run last30days research and return JSON."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    BRIEFINGS_DIR.mkdir(parents=True, exist_ok=True)
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        "python3", str(LAST30_SCRIPT),
        topic,
        "--emit=json",
        "--store"  # Save to SQLite
    ]
    if quick:
        cmd.append("--quick")
    
    print(f"🔍 Researching: {topic}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=SKILL_DIR)
    
    if result.returncode != 0:
        print(f"❌ Research failed: {result.stderr}")
        return {}
    
    # Parse JSON from output
    try:
        # Find JSON in output
        output = result.stdout
        start = output.find('{')
        if start == -1:
            print("❌ No JSON found in output")
            return {}
        data = json.loads(output[start:])
        return data
    except json.JSONDecodeError as e:
        print(f"❌ JSON parse error: {e}")
        return {}


def synthesize_briefing(data: dict, topic: str) -> str:
    """Use Gemini to synthesize research into expert briefing."""
    if not GEMINI_API_KEY:
        return "❌ No GEMINI_API_KEY set"
    
    # Extract key findings
    x_posts = data.get("x", [])[:10]
    youtube = data.get("youtube", [])[:5]
    web = data.get("web", [])[:10]
    
    findings = []
    for p in x_posts:
        findings.append(f"- @{p.get('author_handle')}: {p.get('text', '')[:200]}")
    for w in web:
        findings.append(f"- {w.get('title')}: {w.get('snippet', '')[:150]}")
    
    findings_text = "\n".join(findings) if findings else "No findings found."
    
    prompt = f"""You are an expert researcher. Based on this research data about "{topic}", create:

1. **Expert Briefing** (3-5 paragraphs): Key insights, trends, and what's being discussed
2. **3 Copy-Paste Prompts**: Ready-to-use prompts for AI tools (ChatGPT, Claude, etc.)
3. **Top 3 Recommendations**: Actionable takeaways

Research findings:
{findings_text}

Date range: {data.get('range', {}).get('from', 'N/A')} to {data.get('range', {}).get('to', 'N/A')}

Format your response clearly with headers."""

    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2048
        }
    })
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        req = urllib.request.Request(url, data=body.encode(), headers={"Content-Type": "application/json"})
        resp = json.load(urllib.request.urlopen(req))
        return resp["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"❌ Synthesis failed: {e}"


def save_outputs(topic: str, research_data: dict, briefing: str):
    """Save research and briefing to files."""
    slug = topic.lower().replace(" ", "-")[:50]
    date = datetime.now().strftime("%Y%m%d")
    
    # Save research JSON
    research_file = OUTPUT_DIR / f"{slug}-{date}.json"
    with open(research_file, "w") as f:
        json.dump(research_data, f, indent=2)
    
    # Save briefing
    briefing_file = BRIEFINGS_DIR / f"{slug}-{date}.md"
    with open(briefing_file, "w") as f:
        f.write(f"# Research: {topic}\n")
        f.write(f"Date: {datetime.now().isoformat()}\n\n")
        f.write(briefing)
    
    print(f"✅ Saved:")
    print(f"   Research: {research_file}")
    print(f"   Briefing: {briefing_file}")
    
    return briefing_file


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 last30days-synthesize.py <topic>")
        sys.exit(1)
    
    topic = " ".join(sys.argv[1:])
    
    # Research
    data = run_research(topic)
    if not data:
        print("❌ No research data")
        sys.exit(1)
    
    # Synthesize
    print("🧠 Synthesizing with Gemini...")
    briefing = synthesize_briefing(data, topic)
    
    # Save
    briefing_file = save_outputs(topic, data, briefing)
    
    print(f"\n📋 Briefing:\n{briefing[:500]}...")
