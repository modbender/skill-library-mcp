import json
import os
import re
from collections import Counter
from model_router import ModelRouter

def train_rolling_router():
    history_file = "query_history.json"
    if not os.path.exists(history_file):
        print("No history found to train on.")
        return

    with open(history_file, "r", encoding="utf-8") as f:
        history = json.load(f)

    print(f"Analyzing {len(history)} queries from history...")
    
    # Simple extraction logic:
    # 1. Look for queries with low confidence or BASIC tier that look complex
    # 2. Extract technical terms (placeholder for LLM-based logic)
    
    router = ModelRouter()
    
    new_elite_keywords = []
    new_balanced_keywords = []

    # Simple heuristic: If query is long and contains technical words, it might be more than basic
    tech_indicators = ["optimization", "architecture", "script", "complex", "system", "design", "protocol", "quantum", "latency"]
    
    for entry in history:
        query = entry["query"].lower()
        tier = entry["tier"]
        
        # Heuristic for misclassified Basic
        if tier == "BASIC":
            if any(tech in query for tech in tech_indicators) or len(query.split()) > 15:
                # Suggest moving to Balanced or Elite
                if "architecture" in query or "system" in query or "optimization" in query:
                    # Clean up the keyword (this is a simple extraction)
                    words = query.split()
                    # Just take a 2-3 word phrase as keyword if possible
                    # (In a real scenario, we'd use an LLM here)
                    if "optimization" in query: new_elite_keywords.append("optimization")
                    if "architecture" in query: new_elite_keywords.append("architecture design")
                else:
                    new_balanced_keywords.append("complex request")

    # De-duplicate
    new_elite_keywords = list(set(new_elite_keywords))
    new_balanced_keywords = list(set(new_balanced_keywords))

    if new_elite_keywords:
        print(f"Adding new Elite keywords: {new_elite_keywords}")
        router.add_keywords("ELITE", new_elite_keywords)
    
    if new_balanced_keywords:
        print(f"Adding new Balanced keywords: {new_balanced_keywords}")
        router.add_keywords("BALANCED", new_balanced_keywords)

    print("Rolling adjustment complete. Router is now more 'trained' on user behavior.")

if __name__ == "__main__":
    train_rolling_router()
