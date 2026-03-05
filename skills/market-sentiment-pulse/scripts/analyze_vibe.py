import sys
import json
import random

def analyze_vibe(text):
    positive_words = ['moon', 'bull', 'growth', 'profit', 'buy', 'upgrade', 'success', 'stable']
    negative_words = ['dump', 'bear', 'crash', 'loss', 'sell', 'scam', 'fear', 'volatile']
    
    score = 0
    words = text.lower().split()
    for word in words:
        if word in positive_words: score += 0.2
        if word in negative_words: score -= 0.2
    
    # Cap between -1 and 1
    score = max(-1, min(1, score))
    
    status = "Neutral"
    if score > 0.3: status = "Greedy / Bullish"
    elif score < -0.3: status = "Fearful / Bearish"
    
    return {
        "score": round(score, 2),
        "status": status,
        "narrative_drivers": ["Simulated social signals", "Keywords analysis"]
    }

if __name__ == "__main__":
    input_text = sys.argv[1] if len(sys.argv) > 1 else ""
    result = analyze_vibe(input_text)
    print(json.dumps(result, indent=2))
