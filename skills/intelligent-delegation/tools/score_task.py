#!/usr/bin/env python3
"""
Task Scoring Tool — Evaluate tasks on 7 axes to determine delegation strategy.

Based on "Intelligent AI Delegation" paper (arXiv 2602.11865).

Usage:
    python3 score_task.py --interactive
    python3 score_task.py --json '{"description": "...", "complexity": 3, ...}'
    
Outputs: recommended agent type, autonomy level, monitoring frequency, human approval needed
"""

import argparse
import json
import sys

AXES = {
    "complexity": "How many steps / how much reasoning? (1=trivial, 5=very complex)",
    "criticality": "How bad if it fails? (1=no impact, 5=severe consequences)",
    "cost": "Expected compute cost? (1=cheap, 5=expensive)",
    "reversibility": "Can effects be undone? (1=fully reversible, 5=irreversible)",
    "verifiability": "How easy to check output? (1=auto-verifiable, 5=human judgment)",
    "contextuality": "Sensitive context needed? (1=none, 5=highly sensitive)",
    "subjectivity": "Objective or preference-based? (1=objective, 5=subjective)",
}

AGENT_TIERS = {
    "tier1_cheap": {"cost": 1, "capability": 2, "examples": "Scout, DeepSeek, small models"},
    "tier2_balanced": {"cost": 2, "capability": 3, "examples": "Gemini Flash, GPT-4o-mini"},
    "tier3_capable": {"cost": 3, "capability": 4, "examples": "Sonnet, Gemini Pro"},
    "tier4_main": {"cost": 5, "capability": 5, "examples": "Main orchestrator agent"},
}


def score_to_autonomy(scores):
    risk = (scores["criticality"] + (6 - scores["reversibility"]) + scores["subjectivity"]) / 3
    if risk >= 4:
        return "atomic"
    elif risk >= 2.5:
        return "bounded"
    return "open-ended"


def score_to_monitoring(scores):
    urgency = (scores["criticality"] + scores["complexity"]) / 2
    if urgency >= 4:
        return "continuous"
    elif urgency >= 2.5:
        return "periodic"
    return "on-completion"


def needs_human_approval(scores):
    if scores["reversibility"] >= 4 and scores["criticality"] >= 3:
        return True, "Irreversible action with significant consequences"
    if scores["contextuality"] >= 4:
        return True, "Involves sensitive/private data"
    if scores["criticality"] >= 5:
        return True, "Critical task — failure would be severe"
    return False, None


def select_agent_tier(scores, description=""):
    desc = description.lower()
    
    # Keyword-based routing
    if any(kw in desc for kw in ["build", "code", "script", "debug", "api"]):
        return "tier3_capable", "Code task requires capable agent"
    if any(kw in desc for kw in ["research", "search", "summarize"]):
        if scores["complexity"] <= 3:
            return "tier2_balanced", "Research task within balanced tier"
        return "tier4_main", "Complex research needs main agent"
    if any(kw in desc for kw in ["write", "draft", "content"]):
        return "tier3_capable", "Content creation needs capable agent"
    
    # Score-based routing
    if scores["complexity"] <= 2 and scores["criticality"] <= 2:
        return "tier1_cheap", "Simple, low-stakes task"
    if scores["complexity"] >= 4 or scores["criticality"] >= 4:
        return "tier3_capable", "Complex/critical task"
    
    return "tier2_balanced", "Standard task"


def calculate_recommendation(scores, description=""):
    tier, reason = select_agent_tier(scores, description)
    autonomy = score_to_autonomy(scores)
    monitoring = score_to_monitoring(scores)
    human_req, human_reason = needs_human_approval(scores)
    
    risk = (
        scores["criticality"] * 0.3 +
        (6 - scores["reversibility"]) * 0.25 +
        scores["complexity"] * 0.2 +
        scores["contextuality"] * 0.15 +
        scores["subjectivity"] * 0.1
    )
    
    return {
        "agent_tier": tier,
        "agent_examples": AGENT_TIERS[tier]["examples"],
        "agent_reason": reason,
        "autonomy": autonomy,
        "monitoring": monitoring,
        "human_approval_required": human_req,
        "human_approval_reason": human_reason,
        "risk_level": "HIGH" if risk >= 4 else "MEDIUM" if risk >= 2.5 else "LOW",
        "risk_score": round(risk, 2),
        "scores": scores,
    }


def interactive_scoring():
    print("=" * 60)
    print("TASK SCORING — Answer each question (1-5)")
    print("=" * 60)
    
    description = input("\nTask description: ").strip()
    
    scores = {}
    for axis, question in AXES.items():
        while True:
            try:
                val = int(input(f"\n{axis.upper()}: {question}\n  Score (1-5): "))
                if 1 <= val <= 5:
                    scores[axis] = val
                    break
            except ValueError:
                pass
            print("  Please enter 1-5")
    
    rec = calculate_recommendation(scores, description)
    
    print("\n" + "=" * 60)
    print("RECOMMENDATION")
    print("=" * 60)
    print(f"""
Task: {description}
Risk Level: {rec['risk_level']} (score: {rec['risk_score']}/5)

Delegation:
  Agent Tier: {rec['agent_tier']} ({rec['agent_examples']})
  Reason: {rec['agent_reason']}
  Autonomy: {rec['autonomy']}
  Monitoring: {rec['monitoring']}
  Human Approval: {'YES — ' + rec['human_approval_reason'] if rec['human_approval_required'] else 'No'}
""")
    return rec


def json_scoring(json_str):
    data = json.loads(json_str)
    description = data.pop("description", "")
    
    for axis in AXES:
        if axis not in data:
            print(f"Missing: {axis}", file=sys.stderr)
            sys.exit(2)
        if not 1 <= data[axis] <= 5:
            print(f"Invalid {axis}: must be 1-5", file=sys.stderr)
            sys.exit(2)
    
    rec = calculate_recommendation(data, description)
    print(json.dumps(rec, indent=2))
    return rec


def main():
    parser = argparse.ArgumentParser(description="Score a task for delegation")
    parser.add_argument("--interactive", "-i", action="store_true")
    parser.add_argument("--json", "-j", help="JSON with scores")
    args = parser.parse_args()
    
    if args.interactive:
        interactive_scoring()
    elif args.json:
        json_scoring(args.json)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
