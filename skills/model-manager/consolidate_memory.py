import json
import os
from collections import defaultdict

MEMORY_FILE = os.path.expanduser("~/.openclaw/workspace/swarm_memory.json")
INSIGHTS_FILE = os.path.expanduser("~/.openclaw/workspace/swarm_insights.json")

def consolidate():
    if not os.path.exists(MEMORY_FILE):
        print("No memory to consolidate.")
        return

    with open(MEMORY_FILE, 'r') as f:
        runs = json.load(f)

    stats = defaultdict(lambda: {"attempts": 0, "success": 0, "timeouts": 0})

    for run in runs:
        for step in run.get("steps", []):
            model = step["model"]
            status = step["status"]
            
            # Key could be more granular (e.g. "model:task_type")
            key = model
            
            stats[key]["attempts"] += 1
            if status == "success":
                stats[key]["success"] += 1
            elif status == "timeout":
                stats[key]["timeouts"] += 1

    # Generate Insights
    insights = {
        "generated_at": str(os.times()),
        "model_performance": {}
    }

    print("\n🧠 **Hippocampus Consolidation Report**")
    for model, s in stats.items():
        rate = (s["success"] / s["attempts"]) * 100 if s["attempts"] > 0 else 0
        insights["model_performance"][model] = {
            "success_rate": rate,
            "sample_size": s["attempts"]
        }
        print(f"- **{model}**: {rate:.1f}% Success ({s['success']}/{s['attempts']}) - Timeouts: {s['timeouts']}")

        # Evolution Rule: If timeout rate > 50%, suggest config change
        if s["timeouts"] / s["attempts"] > 0.5:
            print(f"  ⚠️  **Insight:** {model} is struggling with timeouts. Recommended: Increase timeout or switch model.")

    with open(INSIGHTS_FILE, 'w') as f:
        json.dump(insights, f, indent=2)
    print(f"\n✨ Insights saved to {INSIGHTS_FILE}")

if __name__ == "__main__":
    consolidate()
