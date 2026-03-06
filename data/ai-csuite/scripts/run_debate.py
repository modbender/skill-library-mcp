from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
from pathlib import Path

from common import ensure_logs, load_company, profile_for_stage, to_float

PERSONA = {
    "CTO": ("technical correctness and delivery risk", "CPO"),
    "CPO": ("user value and time-to-market", "CTO"),
    "CFO": ("runway protection and ROI", "COO"),
    "CMO": ("market positioning and demand", "CRO"),
    "CRO": ("revenue velocity", "CMO"),
    "COO": ("execution capacity", "CPO"),
    "CSA": ("architecture integrity", "CTO"),
    "CISO": ("security and compliance risk", "CTO"),
    "CV": ("customer evidence", "CRO"),
}

TOPIC_KEYS = {
    "pricing": ["pricing", "discount", "plan", "tier", "price"],
    "hiring": ["hire", "headcount", "team", "recruit"],
    "architecture": ["architecture", "scale", "infra", "microservice", "technical"],
    "security": ["security", "compliance", "gdpr", "soc2", "breach"],
    "growth": ["gtm", "sales", "pipeline", "acquisition", "growth", "marketing"],
}

RECS = {
    "pricing": "Run a 90-day pricing experiment with strict guardrails.",
    "hiring": "Delay permanent hires and use scoped contract support first.",
    "architecture": "Ship with a modular monolith and isolate critical services.",
    "security": "Gate release on baseline controls, logging, and access hardening.",
    "growth": "Focus on one ICP and one repeatable acquisition channel.",
    "general": "Prioritize reversible bets with measurable checkpoints.",
}


def classify_topic(topic: str) -> str:
    text = topic.lower()
    for category, keys in TOPIC_KEYS.items():
        if any(word in text for word in keys):
            return category
    return "general"


def confidence(agent: str, category: str) -> str:
    high = {
        "pricing": {"CFO", "CRO", "CMO"},
        "hiring": {"COO", "CFO", "CEO"},
        "architecture": {"CTO", "CSA"},
        "security": {"CISO", "CTO"},
        "growth": {"CMO", "CRO", "CV"},
        "general": {"CEO", "CoS"},
    }
    return "high" if agent in high.get(category, set()) else "medium"


def round1(agent: str, topic: str, company: dict, category: str) -> tuple[str, str, str]:
    goal = PERSONA.get(agent, ("cross-functional alignment", "CFO"))[0]
    recommendation = RECS[category]
    analysis = (
        f"{agent} evaluates '{topic}' for {company['company_name']} through {goal}. "
        f"The current stage ({company['stage']}) and constraints shape execution options."
    )
    return analysis, recommendation, confidence(agent, category)


def round2(agent: str, agents: list[str], recommendation: str) -> tuple[str, str, str]:
    clash = PERSONA.get(agent, ("", "CFO"))[1]
    peers = [a for a in agents if a != agent and a not in {"CEO", "CoS"}]
    agree = peers[0] if peers else "team"
    challenge = clash if clash in peers else (peers[-1] if peers else "team")
    updated = "Holding position" if challenge == "team" else recommendation
    return agree, challenge, updated


def round3(agent: str, recommendation: str) -> tuple[str, str, str]:
    return (
        "Conceded speed where risk remains reversible.",
        "Will not accept unbounded cost or unmitigated risk.",
        recommendation,
    )


def data_brief(company: dict, category: str) -> tuple[str, str]:
    customer = f"Customer signal priority is {category}; validate with churn and support trend snapshots."
    runway = to_float(company["runway_months"])
    severity = "high" if runway < 6 else "normal"
    finance = f"Runway is {company['runway_months']} months; financial severity is {severity}."
    return customer, finance


def pick_consensus(recommendations: dict[str, str], runway: float) -> str:
    top = Counter(recommendations.values()).most_common(1)[0][0]
    if runway < 6:
        return "Choose the lowest-burn reversible option and defer heavy commitments."
    return top


def ceo_decision(consensus: str, runway: float, category: str) -> tuple[str, str, str, str, str, str]:
    decision = consensus
    if runway < 6 and category in {"hiring", "growth"}:
        decision = "Stabilize runway first, then run a constrained test before expansion."
    rationale = "Decision balances speed, risk, and reversibility against current constraints."
    weighed = "Runway, customer impact, technical feasibility, and execution capacity."
    overrides = "Overrode high-burn paths due to runway risk." if runway < 6 else "No major override."
    trigger = "Revisit if leading indicator misses target for two cycles."
    reversibility = "easily_reversible" if category in {"pricing", "growth", "general"} else "costly_to_reverse"
    return decision, rationale, weighed, overrides, trigger, reversibility


def build_output(topic: str, company: dict, agents: list[str], rounds: int, category: str) -> str:
    runway = to_float(company["runway_months"])
    customer_signal, finance_signal = data_brief(company, category)
    debaters = [a for a in agents if a not in {"CEO", "CoS"}]
    r1: dict[str, tuple[str, str, str]] = {a: round1(a, topic, company, category) for a in debaters}
    r2: dict[str, tuple[str, str, str]] = {a: round2(a, debaters, r1[a][1]) for a in debaters}
    consensus = pick_consensus({a: r1[a][1] for a in debaters}, runway)
    decision, rationale, weighed, overrides, trigger, reversibility = ceo_decision(consensus, runway, category)
    lines = ["**DATA BRIEF (Pre-Round):**", f"- Customer signals: {customer_signal}", f"- Financial context: {finance_signal}", ""]
    for agent in debaters:
        lines += [f"**{agent} (Round 1):**", r1[agent][0], f"Recommendation: {r1[agent][1]}", f"Confidence: {r1[agent][2]}", ""]
    for agent in debaters:
        lines += [f"**{agent} (Round 2):**", f"Agrees with: {r2[agent][0]}", f"Challenges: {r2[agent][1]}", f"Updated position: {r2[agent][2]}", ""]
    if rounds == 3:
        for agent in debaters:
            r3 = round3(agent, r1[agent][1])
            lines += [f"**{agent} (Round 3):**", f"Concessions: {r3[0]}", f"Hard line: {r3[1]}", f"Final recommendation: {r3[2]}", ""]
    lines += [
        "---", "**CEO BRIEF**", "", f"**Topic:** {topic}", f"**Consensus Position:** {consensus}",
        f"**Key Tensions:** Cost discipline vs speed to market across active squads.",
        f"**Recommended Option:** {consensus}", "**Risk Flags:**", f"- {finance_signal}",
        "**Decision Required:** Confirm execution start and owners.", "---", "",
        "---", "**CEO DECISION**", "", f"**DECISION:** {decision}", f"**RATIONALE:** {rationale}",
        f"**WHAT I WEIGHED:** {weighed}", f"**OVERRIDES:** {overrides}", "**NEXT STEPS:**",
        "- CTO: Deliver technical plan and rollback condition.", "- CFO: Track budget and runway variance weekly.",
        "- CPO: Define success metrics and user impact checks.", f"**REVIEW TRIGGER:** {trigger}",
        "**CONFIDENCE:** 7", f"**REVERSIBILITY:** {reversibility}", "---",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    parser.add_argument("--company-file", default="config/company.yaml")
    parser.add_argument("--output")
    args = parser.parse_args()
    company = load_company(args.company_file)
    profile = profile_for_stage(company["stage"])
    category = classify_topic(args.topic)
    body = build_output(args.topic, company, profile["agents"], profile["rounds"], category)
    if args.output:
        out_path = Path(args.output)
    else:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        out_path = ensure_logs(Path.cwd()) / f"debate-{stamp}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(body, encoding="utf-8")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
