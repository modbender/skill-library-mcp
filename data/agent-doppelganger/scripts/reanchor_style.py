import json
import os
import re
import yaml
import statistics

def analyze_style(samples):
    if not samples:
        return None
    
    lengths = [len(s.split()) for s in samples]
    
    # Calculate directness (shorter often = more direct in this context)
    # This is a heuristic: ratio of words to sentences/complexity
    avg_len = statistics.mean(lengths)
    
    # Check for punctuation
    ends_with_punc = [1 if s.strip() and s.strip()[-1] in ".!?" else 0 for s in samples]
    punc_freq = statistics.mean(ends_with_punc)
    
    # Check for casing
    is_lower = [1 if s.islower() else 0 for s in samples if any(c.isalpha() for c in s)]
    lower_freq = statistics.mean(is_lower) if is_lower else 0
    
    # Hedging frequency (simple keyword check)
    hedging_words = ['maybe', 'think', 'possibly', 'probably', 'might', 'could']
    hedging_count = sum(1 for s in samples if any(h in s.lower() for h in hedging_words))
    hedging_freq = hedging_count / len(samples)

    return {
        "sentence_length": {
            "mean": round(avg_len, 2),
            "std": round(statistics.stdev(lengths) if len(lengths) > 1 else 0, 2)
        },
        "punctuation_habits": {
            "end_punc_frequency": round(punc_freq, 2),
            "use_oxford_comma": True # Default to True
        },
        "directness": round(1.0 - (hedging_freq * 2), 2), # Simplified
        "lowercase_preference": round(lower_freq, 2),
        "hedging": round(hedging_freq, 2)
    }

def main():
    # Source samples from our history or a file
    # For now, let's look for a samples file or use a placeholder
    sample_file = os.path.expanduser("~/.openclaw/adg/profile/training_samples.jsonl")
    
    if not os.path.exists(sample_file):
        # Create it with current session data as a seed
        seed_samples = [
            "hi",
            "what now",
            "gemini flash",
            "nba news",
            "give news about kashmir",
            "both"
        ]
        with open(sample_file, 'w') as f:
            for s in seed_samples:
                f.write(json.dumps({"text": s, "timestamp": "2026-02-05T00:00:00Z"}) + "\n")
    
    with open(sample_file, 'r') as f:
        samples = [json.loads(line)['text'] for line in f]
    
    stats = analyze_style(samples)
    
    style_yaml = os.path.expanduser("~/.openclaw/adg/profile/style.yaml")
    with open(style_yaml, 'w') as f:
        yaml.dump(stats, f)
    
    print(f"Re-anchored style based on {len(samples)} samples.")
    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    main()
