#!/usr/bin/env python3
"""
O*NET Occupation Lookup & AI Exposure Analysis

Searches the bundled O*NET datasets to find occupations, their tasks,
work activities, and abilities, then estimates AI exposure.

Usage:
    python onet_lookup.py --search "Software Developer"
    python onet_lookup.py --soc "15-1252.00" --detail
    python onet_lookup.py --search "Customer Service" --exposure
"""

import argparse
import pandas as pd
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "data")

# Work activities considered highly AI-exposed
HIGH_AI_ACTIVITIES = {
    "Getting Information",
    "Processing Information",
    "Analyzing Data or Information",
    "Documenting/Recording Information",
    "Interacting With Computers",
    "Communicating with Persons Outside Organization",
    "Communicating with Supervisors, Peers, or Subordinates",
    "Organizing, Planning, and Prioritizing Work",
    "Updating and Using Relevant Knowledge",
    "Evaluating Information to Determine Compliance with Standards",
    "Interpreting the Meaning of Information for Others",
    "Estimating the Quantifiable Characteristics of Products, Events, or Information",
    "Scheduling Work and Activities",
    "Performing Administrative Activities",
}

# Work activities with low AI exposure (physical/manual)
LOW_AI_ACTIVITIES = {
    "Performing General Physical Activities",
    "Handling and Moving Objects",
    "Controlling Machines and Processes",
    "Operating Vehicles, Mechanized Devices, or Equipment",
    "Repairing and Maintaining Mechanical Equipment",
    "Repairing and Maintaining Electronic Equipment",
    "Inspecting Equipment, Structures, or Materials",
}

# Cognitive abilities (higher AI exposure)
COGNITIVE_ABILITIES = {
    "Oral Comprehension", "Written Comprehension", "Oral Expression",
    "Written Expression", "Fluency of Ideas", "Originality",
    "Problem Sensitivity", "Deductive Reasoning", "Inductive Reasoning",
    "Information Ordering", "Category Flexibility", "Mathematical Reasoning",
    "Number Facility", "Memorization", "Speed of Closure", "Flexibility of Closure",
    "Perceptual Speed", "Selective Attention", "Time Sharing",
}

# Physical abilities (lower AI exposure)
PHYSICAL_ABILITIES = {
    "Static Strength", "Explosive Strength", "Dynamic Strength",
    "Trunk Strength", "Stamina", "Extent Flexibility", "Dynamic Flexibility",
    "Gross Body Coordination", "Gross Body Equilibrium", "Manual Dexterity",
    "Finger Dexterity", "Arm-Hand Steadiness", "Control Precision",
    "Multilimb Coordination", "Response Orientation", "Rate Control",
    "Reaction Time", "Wrist-Finger Speed", "Speed of Limb Movement",
}


def load_data():
    """Load all O*NET datasets."""
    data = {}
    files = {
        "occupations": "Occupation_Data.txt",
        "tasks": "Task_Statements.txt",
        "task_ratings": "Task_Ratings.txt",
        "activities": "Work_Activities.txt",
        "abilities": "Abilities.txt",
    }
    for key, fname in files.items():
        path = os.path.join(DATA_DIR, fname)
        if os.path.exists(path):
            data[key] = pd.read_csv(path, sep='\t')
        else:
            print(f"Warning: {fname} not found at {path}", file=sys.stderr)
            data[key] = pd.DataFrame()
    return data


def search_occupations(data, query):
    """Search occupations by title or description."""
    occ = data["occupations"]
    mask = (
        occ["Title"].str.contains(query, case=False, na=False)
        | occ["Description"].str.contains(query, case=False, na=False)
    )
    return occ[mask]


def get_occupation_detail(data, soc_code):
    """Get detailed info for a specific O*NET-SOC code."""
    occ = data["occupations"]
    match = occ[occ["O*NET-SOC Code"] == soc_code]
    if match.empty:
        return None

    result = {
        "soc_code": soc_code,
        "title": match.iloc[0]["Title"],
        "description": match.iloc[0]["Description"],
    }

    # Tasks
    tasks = data["tasks"]
    occ_tasks = tasks[tasks["O*NET-SOC Code"] == soc_code]
    result["tasks"] = occ_tasks[["Task ID", "Task", "Task Type"]].to_dict("records")

    # Work Activities (importance scores)
    activities = data["activities"]
    occ_act = activities[activities["O*NET-SOC Code"] == soc_code]
    result["work_activities"] = occ_act[["Element Name", "Data Value"]].to_dict("records")

    # Abilities (importance scores)
    abilities = data["abilities"]
    occ_abil = abilities[abilities["O*NET-SOC Code"] == soc_code]
    result["abilities"] = occ_abil[["Element Name", "Data Value"]].to_dict("records")

    return result


def estimate_ai_exposure(data, soc_code):
    """Estimate AI exposure for an occupation based on work activities and abilities."""
    activities = data["activities"]
    abilities = data["abilities"]

    # Work activity-based exposure
    occ_act = activities[activities["O*NET-SOC Code"] == soc_code]

    if occ_act.empty:
        return None

    high_exp_score = 0
    low_exp_score = 0
    total_score = 0

    for _, row in occ_act.iterrows():
        name = row["Element Name"]
        importance = row["Data Value"]
        total_score += importance
        if name in HIGH_AI_ACTIVITIES:
            high_exp_score += importance
        elif name in LOW_AI_ACTIVITIES:
            low_exp_score += importance

    activity_exposure = high_exp_score / total_score if total_score > 0 else 0

    # Ability-based exposure
    occ_abil = abilities[abilities["O*NET-SOC Code"] == soc_code]

    cognitive_score = 0
    physical_score = 0

    for _, row in occ_abil.iterrows():
        name = row["Element Name"]
        importance = row["Data Value"]
        if name in COGNITIVE_ABILITIES:
            cognitive_score += importance
        elif name in PHYSICAL_ABILITIES:
            physical_score += importance

    total_abil = cognitive_score + physical_score
    ability_exposure = cognitive_score / total_abil if total_abil > 0 else 0

    # Combined score (weighted: 60% activity, 40% ability)
    combined = 0.6 * activity_exposure + 0.4 * ability_exposure

    return {
        "soc_code": soc_code,
        "activity_exposure": round(activity_exposure, 3),
        "ability_exposure": round(ability_exposure, 3),
        "combined_exposure": round(combined, 3),
        "exposure_level": (
            "Very High" if combined > 0.7
            else "High" if combined > 0.55
            else "Moderate" if combined > 0.4
            else "Low" if combined > 0.25
            else "Very Low"
        ),
        "high_exposure_activities": [
            row["Element Name"]
            for _, row in occ_act.iterrows()
            if row["Element Name"] in HIGH_AI_ACTIVITIES and row["Data Value"] >= 3.5
        ],
    }


def main():
    parser = argparse.ArgumentParser(description="O*NET Occupation Lookup & AI Exposure Analysis")
    parser.add_argument("--search", type=str, help="Search occupations by keyword")
    parser.add_argument("--soc", type=str, help="Look up a specific O*NET-SOC code")
    parser.add_argument("--detail", action="store_true", help="Show detailed tasks, activities, abilities")
    parser.add_argument("--exposure", action="store_true", help="Estimate AI exposure score")
    parser.add_argument("--limit", type=int, default=10, help="Max results for search")

    args = parser.parse_args()

    if not args.search and not args.soc:
        parser.print_help()
        sys.exit(1)

    print("Loading O*NET datasets...", file=sys.stderr)
    data = load_data()

    if args.search:
        results = search_occupations(data, args.search)
        print(f"\nFound {len(results)} occupations matching '{args.search}':\n")
        for _, row in results.head(args.limit).iterrows():
            print(f"  {row['O*NET-SOC Code']:16s} {row['Title']}")
            if args.exposure:
                exp = estimate_ai_exposure(data, row["O*NET-SOC Code"])
                if exp:
                    print(f"{'':18s} AI Exposure: {exp['combined_exposure']:.1%} ({exp['exposure_level']})")
            print()

    if args.soc:
        if args.detail:
            detail = get_occupation_detail(data, args.soc)
            if detail:
                print(f"\n{'='*60}")
                print(f"  {detail['title']} ({detail['soc_code']})")
                print(f"{'='*60}")
                print(f"\nDescription: {detail['description']}\n")

                print(f"Tasks ({len(detail['tasks'])} total):")
                for t in detail["tasks"][:10]:
                    print(f"  [{t['Task Type']}] {t['Task']}")
                if len(detail["tasks"]) > 10:
                    print(f"  ... and {len(detail['tasks']) - 10} more")

                print(f"\nTop Work Activities (by importance):")
                sorted_acts = sorted(detail["work_activities"], key=lambda x: x["Data Value"], reverse=True)
                for a in sorted_acts[:10]:
                    marker = " [AI-EXPOSED]" if a["Element Name"] in HIGH_AI_ACTIVITIES else ""
                    print(f"  {a['Data Value']:.2f}  {a['Element Name']}{marker}")

                print(f"\nTop Abilities (by importance):")
                sorted_abil = sorted(detail["abilities"], key=lambda x: x["Data Value"], reverse=True)
                for a in sorted_abil[:10]:
                    atype = "[COGNITIVE]" if a["Element Name"] in COGNITIVE_ABILITIES else "[PHYSICAL]" if a["Element Name"] in PHYSICAL_ABILITIES else "[OTHER]"
                    print(f"  {a['Data Value']:.2f}  {a['Element Name']} {atype}")
            else:
                print(f"No occupation found with SOC code: {args.soc}")

        if args.exposure:
            exp = estimate_ai_exposure(data, args.soc)
            if exp:
                print(f"\n{'='*60}")
                print(f"  AI EXPOSURE ESTIMATE: {args.soc}")
                print(f"{'='*60}")
                print(f"  Activity-based exposure:  {exp['activity_exposure']:.1%}")
                print(f"  Ability-based exposure:   {exp['ability_exposure']:.1%}")
                print(f"  Combined exposure:        {exp['combined_exposure']:.1%}")
                print(f"  Exposure level:           {exp['exposure_level']}")
                if exp["high_exposure_activities"]:
                    print(f"\n  Key AI-exposed activities (importance ≥ 3.5):")
                    for act in exp["high_exposure_activities"]:
                        print(f"    • {act}")


if __name__ == "__main__":
    main()
