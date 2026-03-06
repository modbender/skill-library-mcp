#!/usr/bin/env python3
"""🧠 Detect human mood from messages — simple keyword/pattern matching."""

import json
import re
from pathlib import Path
from datetime import datetime
from config import get_file_path, get_human_name

HUMAN_MOOD_FILE = get_file_path("human_mood.json")

# Mood detection patterns
MOOD_PATTERNS = {
    "excited": {
        "energy": "high",
        "vibe": "positive", 
        "keywords": ["awesome", "amazing", "hell yeah", "let's go", "fuck yeah", "sick", "dope", "lit", "fire", "hyped", "stoked", "pumped"],
        "patterns": [r"\b(!!!|wow|omg|holy shit)\b", r"\b[A-Z]{3,}\b", r"[!]{2,}"]
    },
    "frustrated": {
        "energy": "high",
        "vibe": "negative",
        "keywords": ["fuck", "shit", "damn", "annoying", "broken", "wtf", "ugh", "frustrated", "annoyed", "pissed"],
        "patterns": [r"\bffs\b", r"\bwtf\b", r"\bgod damn", r"piece of shit"]
    },
    "stressed": {
        "energy": "low", 
        "vibe": "negative",
        "keywords": ["stressed", "overwhelmed", "tired", "exhausted", "busy", "swamped", "deadline", "pressure"],
        "patterns": [r"\btoo much\b", r"\bso much\b", r"\bcan't handle\b"]
    },
    "casual": {
        "energy": "neutral",
        "vibe": "neutral", 
        "keywords": ["yeah", "sure", "alright", "cool", "ok", "fine", "whatever", "meh"],
        "patterns": [r"\byep\b", r"\bnah\b", r"\bokay\b"]
    },
    "curious": {
        "energy": "neutral",
        "vibe": "positive",
        "keywords": ["interesting", "how does", "what if", "why", "explain", "tell me", "curious"],
        "patterns": [r"\?", r"\bhow about\b", r"\bwhat about\b", r"\bi wonder\b"]
    },
    "happy": {
        "energy": "neutral",
        "vibe": "positive", 
        "keywords": ["happy", "good", "nice", "great", "perfect", "love it", "thanks", "appreciate"],
        "patterns": [r":\)", r":D", r"<3", r"\bhaha\b", r"\blol\b"]
    },
    "focused": {
        "energy": "high",
        "vibe": "neutral",
        "keywords": ["working", "building", "coding", "debugging", "focusing", "deep work", "in the zone"],
        "patterns": [r"\blet me\b", r"\bgoing to\b", r"\bworking on\b"]
    }
}

def detect_mood(message):
    """Detect mood from a message string."""
    if not message:
        return None
    
    message_lower = message.lower()
    scores = {}
    
    for mood, config in MOOD_PATTERNS.items():
        score = 0
        
        # Keyword matching
        for keyword in config["keywords"]:
            if keyword in message_lower:
                score += 2
        
        # Pattern matching  
        for pattern in config.get("patterns", []):
            matches = len(re.findall(pattern, message_lower))
            score += matches * 1.5
        
        if score > 0:
            scores[mood] = score
    
    if not scores:
        return {
            "mood": "neutral",
            "confidence": 0.3,
            "energy": "neutral", 
            "vibe": "neutral",
            "detected_at": datetime.now().isoformat()
        }
    
    # Get highest scoring mood
    top_mood = max(scores.items(), key=lambda x: x[1])
    mood_name = top_mood[0]
    confidence = min(1.0, top_mood[1] / 10)  # Scale to 0-1
    
    config = MOOD_PATTERNS[mood_name]
    
    return {
        "mood": mood_name,
        "confidence": confidence,
        "energy": config["energy"],
        "vibe": config["vibe"],
        "detected_at": datetime.now().isoformat(),
        "raw_message": message[:100]  # Store snippet for context
    }

def save_human_mood(mood_data):
    """Save detected mood to human_mood.json."""
    try:
        # Load existing data
        try:
            with open(HUMAN_MOOD_FILE) as f:
                data = json.load(f)
        except:
            data = {"version": 1, "current": None, "history": []}
        
        # Update current mood
        data["current"] = mood_data
        
        # Add to history
        data["history"].append(mood_data)
        data["history"] = data["history"][-50:]  # Keep last 50
        
        # Save
        with open(HUMAN_MOOD_FILE, 'w') as f:
            json.dump(data, f, indent=2)
            
    except Exception as e:
        print(f"Failed to save human mood: {e}")

def get_supportive_response(mood_data):
    """Generate a supportive response based on detected mood."""
    if not mood_data:
        return None
    
    mood = mood_data["mood"]
    energy = mood_data["energy"]
    vibe = mood_data["vibe"]
    
    responses = {
        "excited": ["I can feel the energy! 🔥", "Your enthusiasm is contagious!", "That excitement is infectious!"],
        "frustrated": ["That sounds frustrating 😤", "I get why that would be annoying", "Want me to help fix something?"],
        "stressed": ["Take a breath — you got this 💪", "Sounds like a lot on your plate", "Maybe time for a quick break?"],
        "happy": ["Love to see it! 😊", "That happiness comes through!", "Good vibes!"],
        "curious": ["Ooh, I like where your mind is going 🤔", "Always asking the good questions", "Let's explore that!"],
        "focused": ["In the zone! 🎯", "Love the focused energy", "Don't let me interrupt the flow"]
    }
    
    # Mood-specific responses
    if mood in responses:
        return responses[mood][hash(mood_data["detected_at"]) % len(responses[mood])]
    
    # Fallback based on energy/vibe combo
    if energy == "high" and vibe == "positive":
        return "Feeling that high energy! 🚀"
    elif energy == "low" and vibe == "negative": 
        return "Sounds rough — here if you need anything"
    elif vibe == "positive":
        return "Good vibes coming through ✨"
    else:
        return None

def main():
    """CLI interface."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: detect_human_mood.py '<message>'")
        print("       detect_human_mood.py --show")
        return
    
    if sys.argv[1] == "--show":
        try:
            with open(HUMAN_MOOD_FILE) as f:
                data = json.load(f)
                print(json.dumps(data, indent=2))
        except:
            print("No human mood data found")
        return
    
    message = sys.argv[1]
    mood_data = detect_mood(message)
    
    if mood_data:
        save_human_mood(mood_data)
        print(json.dumps(mood_data, indent=2))
        
        # Show supportive response
        response = get_supportive_response(mood_data)
        if response:
            print(f"\nSupportive response: {response}")
    else:
        print("Could not detect mood from message")

if __name__ == "__main__":
    main()