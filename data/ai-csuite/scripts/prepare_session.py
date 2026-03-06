from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import load_company, profile_for_stage


def active_squads(topic: str) -> list[str]:
    text = topic.lower()
    squads = {"Strategy", "Product"}
    if any(k in text for k in ["pricing", "revenue", "sales", "gtm", "marketing", "growth"]):
        squads.add("Growth")
    if any(k in text for k in ["security", "compliance", "risk"]):
        squads.add("Product")
        squads.add("Strategy")
    return sorted(squads)


def build_packet(topic: str, company_file: str) -> dict:
    company = load_company(company_file)
    profile = profile_for_stage(company["stage"])
    agents = profile["agents"]
    data_agents = ["CV", "CFO"]
    packet = {
        "topic": topic,
        "company": company,
        "rounds": profile["rounds"],
        "debate_agents": agents,
        "data_agents": data_agents,
        "data_only_agents": [a for a in data_agents if a not in agents],
        "active_squads": active_squads(topic),
    }
    return packet


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    parser.add_argument("--company-file", default="config/company.yaml")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    packet = build_packet(args.topic, args.company_file)
    if args.json:
        print(json.dumps(packet, indent=2))
        return 0
    print("SESSION PACKET")
    print(f"Topic: {packet['topic']}")
    print(f"Company: {packet['company']['company_name']}")
    print(f"Stage: {packet['company']['stage']}")
    print(f"Rounds: {packet['rounds']}")
    print(f"Squads: {', '.join(packet['active_squads'])}")
    print(f"Debate Agents: {', '.join(packet['debate_agents'])}")
    print(f"Data Agents: {', '.join(packet['data_agents'])}")
    if packet["data_only_agents"]:
        print(f"Data-only Agents: {', '.join(packet['data_only_agents'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
