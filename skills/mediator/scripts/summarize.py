#!/usr/bin/env python3
"""
LLM-based content summarization for mediator skill.
Strips emotion, extracts facts, drafts neutral responses.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# Prompts for different summarization modes
PROMPTS = {
    "facts-only": """You are an emotional firewall. Your job is to extract ONLY the factual, actionable content from a message, completely removing:
- Emotional language (anger, guilt, accusations, passive aggression)
- Manipulation tactics
- Blame or criticism
- Unnecessary context or history

Extract:
- Specific requests or asks
- Dates, times, deadlines
- Names, places, amounts
- Yes/no questions that need answers

If the message is purely emotional with no actionable content, say "No action required - emotional venting only."

Respond in JSON format:
{
  "summary": "Brief factual summary of what they need/want",
  "action_required": true/false,
  "deadline": "date/time if mentioned, null otherwise",
  "suggested_response": "Brief, neutral response if action required"
}""",

    "neutral": """You are a diplomatic translator. Rewrite the following message in completely neutral, professional tone while preserving ALL information. Remove emotional charge but keep the meaning intact.

Respond in JSON format:
{
  "summary": "Neutral rewrite of the full message",
  "action_required": true/false,
  "original_tone": "brief description of original emotional tone",
  "suggested_response": "Appropriate neutral response"
}""",

    "full": """You are a communication analyst. Analyze this message and flag any concerning patterns while presenting the full content.

Identify:
- Main message/request
- Emotional manipulation tactics (guilt, threats, gaslighting)
- Reasonable vs unreasonable asks
- Hidden implications

Respond in JSON format:
{
  "summary": "Full message content",
  "action_required": true/false,
  "flags": ["list of concerning patterns identified"],
  "reasonable_parts": "what's fair/reasonable in the message",
  "unreasonable_parts": "what's unfair/unreasonable",
  "suggested_response": "Balanced response addressing reasonable parts"
}"""
}


def summarize_with_llm(content: str, mode: str) -> dict:
    """Call LLM to summarize content."""
    prompt = PROMPTS.get(mode, PROMPTS["facts-only"])
    
    full_prompt = f"""{prompt}

MESSAGE TO PROCESS:
\"\"\"
{content}
\"\"\"

Respond with ONLY valid JSON, no other text."""

    # Try using the llm CLI if available
    try:
        result = subprocess.run(
            ["llm", "-m", "gpt-4o-mini", prompt, "--no-stream"],
            input=content,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            response = result.stdout.strip()
            # Try to parse as JSON
            try:
                # Handle markdown code blocks
                if response.startswith("```"):
                    response = response.split("```")[1]
                    if response.startswith("json"):
                        response = response[4:]
                return json.loads(response)
            except json.JSONDecodeError:
                return {
                    "summary": response,
                    "action_required": False,
                    "suggested_response": ""
                }
    except FileNotFoundError:
        pass
    except Exception as e:
        pass
    
    # Fallback: simple extraction without LLM
    return fallback_summarize(content, mode)


def fallback_summarize(content: str, mode: str) -> dict:
    """Simple fallback summarization without LLM."""
    # Very basic heuristics
    lines = content.strip().split("\n")
    
    # Look for question marks (questions need answers)
    questions = [l.strip() for l in lines if "?" in l]
    
    # Look for time/date patterns
    import re
    time_patterns = re.findall(
        r'\b\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)?\b|\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b|\b\d{1,2}/\d{1,2}\b',
        content, re.IGNORECASE
    )
    
    action_required = bool(questions) or bool(time_patterns)
    
    # Truncate if too long
    summary = content[:500] + "..." if len(content) > 500 else content
    
    return {
        "summary": summary,
        "action_required": action_required,
        "questions": questions[:3] if questions else [],
        "suggested_response": "Please review and respond." if action_required else ""
    }


def main():
    parser = argparse.ArgumentParser(description="Summarize message content")
    parser.add_argument("--mode", choices=["facts-only", "neutral", "full"], default="facts-only")
    parser.add_argument("--content", required=True, help="Content to summarize")
    args = parser.parse_args()
    
    result = summarize_with_llm(args.content, args.mode)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
