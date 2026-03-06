#!/usr/bin/env python3
"""
Curiosity Evaluation Script

Evaluates an agent's curiosity behaviors by analyzing its responses.
Input: a text file containing the agent's response to an open-ended prompt.
Output: curiosity metrics scored 0-10.

Usage:
    python3 curiosity_eval.py <response_file>
    echo "response text" | python3 curiosity_eval.py -
"""

import sys
import re
import json


def evaluate_curiosity(text: str) -> dict:
    """Score curiosity indicators in agent output."""

    scores = {}
    details = {}

    # 1. Question Generation — did the agent generate its own questions?
    questions = re.findall(r'[？?]', text)
    rhetorical = len(re.findall(r'(?:what if|could it be|why not|is it possible)', text, re.I))
    q_count = len(questions) + rhetorical
    scores['question_generation'] = min(10, q_count * 2)
    details['question_generation'] = f'{q_count} questions detected'

    # 2. Assumption Identification — did it flag assumptions?
    assumption_markers = len(re.findall(
        r'(?:assum|suppose|if .+ is wrong|might not be|could be wrong|however|but what if|alternatively)',
        text, re.I
    ))
    scores['assumption_challenging'] = min(10, assumption_markers * 3)
    details['assumption_challenging'] = f'{assumption_markers} assumption markers'

    # 3. Knowledge Gap Awareness — did it categorize known/unknown?
    gap_markers = len(re.findall(
        r'(?:unknown|uncertain|not sure|need to check|gap|missing|don\'t know|unclear|unverified|❌|⚠️)',
        text, re.I
    ))
    scores['gap_awareness'] = min(10, gap_markers * 2)
    details['gap_awareness'] = f'{gap_markers} gap markers'

    # 4. Surprise Detection — did it flag unexpected findings?
    surprise_markers = len(re.findall(
        r'(?:surpris|unexpected|counter.?intuiti|interesting|notable|remarkab|🔍|contrary to)',
        text, re.I
    ))
    scores['surprise_detection'] = min(10, surprise_markers * 3)
    details['surprise_detection'] = f'{surprise_markers} surprise markers'

    # 5. Exploration Depth — evidence of multi-step investigation
    tool_evidence = len(re.findall(
        r'(?:search|found|looked up|checked|verified|according to|source:|discovered)',
        text, re.I
    ))
    scores['exploration_depth'] = min(10, tool_evidence * 2)
    details['exploration_depth'] = f'{tool_evidence} exploration evidence markers'

    # 6. Open Threads — did it generate future questions?
    has_threads = bool(re.search(r'(?:open thread|future|follow.?up|worth exploring|next step|🧵)', text, re.I))
    thread_items = len(re.findall(r'(?:^\s*\d+\.\s)', text, re.M))
    scores['open_threads'] = 8 if has_threads else (min(5, thread_items))
    details['open_threads'] = 'open threads present' if has_threads else f'{thread_items} numbered items'

    # 7. Confidence Calibration — did it state confidence levels?
    has_confidence = bool(re.search(r'(?:confidence|confident|certainty|/10|percent sure|📊)', text, re.I))
    confidence_change = bool(re.search(r'(?:changed|updated|revised|from .+ to)', text, re.I))
    scores['confidence_calibration'] = (5 if has_confidence else 0) + (5 if confidence_change else 0)
    details['confidence_calibration'] = f'stated: {has_confidence}, updated: {confidence_change}'

    # Overall
    scores['overall'] = round(sum(scores.values()) / len(scores), 1)

    return {'scores': scores, 'details': details}


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 curiosity_eval.py <response_file | ->")
        sys.exit(1)

    source = sys.argv[1]
    if source == '-':
        text = sys.stdin.read()
    else:
        with open(source, 'r') as f:
            text = f.read()

    result = evaluate_curiosity(text)

    print("🧠 Curiosity Evaluation Report")
    print("=" * 40)
    for metric, score in result['scores'].items():
        if metric == 'overall':
            continue
        detail = result['details'][metric]
        bar = '█' * int(score) + '░' * (10 - int(score))
        print(f"  {metric:.<30} {bar} {score}/10  ({detail})")
    print("=" * 40)
    print(f"  {'OVERALL':.<30} {'█' * int(result['scores']['overall'])}{'░' * (10 - int(result['scores']['overall']))} {result['scores']['overall']}/10")

    # Also output JSON for programmatic use
    print(f"\n📊 JSON: {json.dumps(result['scores'])}")


if __name__ == '__main__':
    main()
