#!/usr/bin/env python3
"""
GEO Studio orchestrator.
"""

import argparse

def orchestrate(intent, topic):
    paths = {
        "discover": ["geo-prompt-researcher", "geo-competitor-scanner"],
        "build": ["geo-citation-writer", "geo-human-editor", "geo-schema-gen"],
        "fix": ["geo-human-editor", "geo-content-optimizer", "geo-schema-gen"],
        "technical": ["geo-site-audit", "geo-llms-txt", "geo-schema-gen"],
        "report": ["geo-report-builder"],
    }
    
    skills = paths.get(intent, ["geo-studio"])
    return skills

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--intent", choices=["discover", "build", "fix", "technical", "report"])
    parser.add_argument("--topic", required=True)
    args = parser.parse_args()
    
    skills = orchestrate(args.intent, args.topic)
    print(f"Workflow for '{args.topic}':")
    for i, skill in enumerate(skills, 1):
        print(f"{i}. {skill}")

if __name__ == "__main__":
    main()
