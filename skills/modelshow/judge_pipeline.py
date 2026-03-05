#!/usr/bin/env python3
"""
ModelShow2 Atomic Judge Pipeline
=================================
This script takes model responses + a judge's raw text output and ATOMICALLY:
  1. Anonymizes responses (for reference/audit)
  2. De-anonymizes the judge output
  3. Returns ONLY real model names — never placeholder labels

The orchestrator CANNOT receive raw "Response A/B/C" labels because this script
never emits them. De-anonymization is not a step the orchestrator executes;
it is the only thing this script returns.

Usage (two-phase):

Phase 1 — Anonymize (before sending to judge):
  echo '{"action":"anonymize","responses":{"sonnet":"...","grok":"..."}}' | python3 judge_pipeline.py

Phase 2 — De-anonymize (after judge returns):
  echo '{"action":"finalize","judge_output":"...","anonymization_map":{"Response A":"sonnet",...}}' | python3 judge_pipeline.py

The "finalize" action replaces "deanonymize" from the old skill.
It returns deanonymized_judge_output and ranked_models_deanonymized.
No intermediate placeholder state is ever returned to the orchestrator.
"""

import json
import re
import random
import string
import sys
import logging

logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')


def generate_mapping(model_names: list, label_style: str = "alphabetic", shuffle: bool = True):
    if shuffle:
        shuffled = random.sample(model_names, len(model_names))
    else:
        shuffled = list(model_names)

    anon_map = {}      # placeholder → model_name
    reverse_map = {}   # model_name → placeholder

    for i, model in enumerate(shuffled):
        if label_style == "alphabetic":
            label = f"Response {string.ascii_uppercase[i]}"
        elif label_style == "numeric":
            label = f"Candidate {i + 1}"
        else:
            label = f"Response {string.ascii_uppercase[i]}"
        anon_map[label] = model
        reverse_map[model] = label

    return anon_map, reverse_map


def get_blind_responses(responses_by_model: dict, reverse_map: dict) -> dict:
    """Returns placeholder → response_text"""
    return {
        reverse_map[model]: text
        for model, text in responses_by_model.items()
        if model in reverse_map
    }


def deanonymize(judge_output: str, anon_map: dict) -> str:
    """Replace all placeholder labels with real model names (bolded)."""
    result = judge_output
    # Sort descending so longer/later labels replace first (avoids partial overlaps)
    for placeholder in sorted(anon_map.keys(), reverse=True):
        real_model = anon_map[placeholder]
        escaped = re.escape(placeholder)
        pattern = re.compile(rf"(?<!\w){escaped}(?!\w)", re.IGNORECASE)
        result = pattern.sub(f"**{real_model}**", result)
    return result


def extract_rankings(judge_output: str, anon_map: dict) -> list:
    """Extract ranked model list from judge text, returning real model names."""
    ranked = []
    pattern = re.compile(
        r"(?:^|\n)\s*"
        r"(?:###\s*(?:🥇|🥈|🥉|🏆)?\s*)?(?:\d+(?:st|nd|rd|th)?[.:]?\s+)"
        r"(?:Place[:\s]+|Rank[:\s]+)?"
        r"((?:Response|Candidate|Output)\s+[A-Z0-9]+)"
        r".*?(?:Score[:\s]+|—\s*|:\s*)"
        r"(\d+\.?\d*)\s*/\s*10",
        re.MULTILINE | re.IGNORECASE | re.DOTALL
    )

    seen = set()
    for match in pattern.finditer(judge_output):
        raw = match.group(1).strip()
        normalised = next((k for k in anon_map if k.lower() == raw.lower()), raw)
        if normalised in seen:
            continue
        seen.add(normalised)
        score = float(match.group(2))
        model = anon_map.get(normalised)
        if model:
            ranked.append({"placeholder": normalised, "model": model, "score": score})

    ranked.sort(key=lambda x: x["score"], reverse=True)
    for i, item in enumerate(ranked):
        item["rank"] = i + 1
    return ranked


def verify_no_placeholders(text: str) -> list:
    """Return any remaining placeholder-shaped strings (should be empty after deanon)."""
    patterns = [
        r"(?<!\w)Response [A-Z](?!\w)",
        r"(?<!\w)Candidate \d+(?!\w)",
        r"(?<!\w)Output [A-Z](?!\w)",
    ]
    found = []
    for p in patterns:
        found.extend(re.findall(p, text))
    return found


def main():
    data = json.loads(sys.stdin.read())
    action = data.get("action")

    # ── Phase 1: Anonymize ────────────────────────────────────────────────────
    if action == "anonymize":
        responses = data["responses"]
        label_style = data.get("label_style", "alphabetic")
        shuffle = data.get("shuffle", True)

        anon_map, reverse_map = generate_mapping(list(responses.keys()), label_style, shuffle)
        blind_responses = get_blind_responses(responses, reverse_map)

        # Return anonymization data — orchestrator stores anon_map for Phase 2
        print(json.dumps({
            "anonymization_map": anon_map,       # placeholder → model_name
            "reverse_map": reverse_map,           # model_name → placeholder
            "blind_responses_for_judge": blind_responses  # placeholder → response_text
        }))

    # ── Phase 2: Finalize (de-anonymize judge output) ─────────────────────────
    elif action == "finalize":
        judge_output = data.get("judge_output", "")
        anon_map = data.get("anonymization_map", {})

        if not anon_map:
            # Fallback: accept reverse_map key too (model→placeholder) and invert
            rm = data.get("reverse_map", {})
            sample_key = next(iter(rm), "")
            if re.match(r"(?:Response|Candidate|Output)\s+[A-Z0-9]+", sample_key, re.IGNORECASE):
                anon_map = rm  # already placeholder→model
            else:
                anon_map = {v: k for k, v in rm.items()}  # invert model→placeholder

        if not anon_map:
            print(json.dumps({"error": "finalize action requires 'anonymization_map'"}))
            sys.exit(1)

        deanon_output = deanonymize(judge_output, anon_map)
        ranked = extract_rankings(judge_output, anon_map)

        # Verify — warn if any placeholders escaped
        remaining = verify_no_placeholders(deanon_output)
        deanon_ok = len(remaining) == 0

        print(json.dumps({
            "deanonymized_judge_output": deanon_output,
            "ranked_models_deanonymized": ranked,
            "deanonymization_complete": deanon_ok,
            "remaining_placeholders": remaining  # should be [] always
        }))

    # ── Legacy: deanonymize (backward compat with any tooling) ───────────────
    elif action == "deanonymize":
        # Redirect to finalize logic
        data["action"] = "finalize"
        judge_output = data.get("judge_output", "")
        anon_map = data.get("anonymization_map", data.get("reverse_map", {}))

        sample_key = next(iter(anon_map), "")
        if anon_map and not re.match(r"(?:Response|Candidate|Output)\s+[A-Z0-9]+", sample_key, re.IGNORECASE):
            anon_map = {v: k for k, v in anon_map.items()}

        deanon_output = deanonymize(judge_output, anon_map)
        ranked = extract_rankings(judge_output, anon_map)
        remaining = verify_no_placeholders(deanon_output)

        print(json.dumps({
            "deanonymized_judge_output": deanon_output,
            "ranked_models_deanonymized": ranked,
            "deanonymization_complete": len(remaining) == 0,
            "remaining_placeholders": remaining
        }))

    else:
        print(json.dumps({"error": f"Unknown action '{action}'. Use 'anonymize' or 'finalize'."}))
        sys.exit(1)


if __name__ == "__main__":
    main()
