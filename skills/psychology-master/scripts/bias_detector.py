#!/usr/bin/env python3
"""
Bias Detector Tool

Analyzes marketing copy for psychological manipulation, dark patterns, and ethical concerns.
Provides recommendations for ethical alternatives.

Usage:
    python bias_detector.py --copy "Your marketing copy here"
    python bias_detector.py --file marketing_copy.txt
    python bias_detector.py --copy "Limited time offer!" --strict
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
MAX_INPUT_FILE_BYTES = 200_000


@dataclass
class Result:
    """Standard result structure for skill scripts."""
    success: bool
    data: dict
    errors: List[str]
    warnings: List[str]


# Patterns to detect (regex patterns and keywords)
MANIPULATION_PATTERNS = {
    "fake_urgency": {
        "patterns": [
            r"(?i)\bonly\s+\d+\s+left\b",
            r"(?i)\blimited\s+time\b",
            r"(?i)\bact\s+now\b",
            r"(?i)\bhurry\b",
            r"(?i)\bexpires?\s+(soon|today|tonight)\b",
            r"(?i)\blast\s+chance\b",
            r"(?i)\bdon'?t\s+miss\b",
            r"(?i)\bending\s+soon\b",
            r"(?i)\bwhile\s+supplies\s+last\b"
        ],
        "severity": "medium",
        "description": "Creates artificial urgency that may not be genuine",
        "ethical_alternative": "Use real deadlines and genuine scarcity. If urgency is artificial, remove it.",
        "questions": ["Is this scarcity/deadline real?", "Would removing it significantly change the message?"]
    },
    "fear_based": {
        "patterns": [
            r"(?i)\bdon'?t\s+be\s+left\s+behind\b",
            r"(?i)\bmissing\s+out\b",
            r"(?i)\bfomo\b",
            r"(?i)\byou'?ll\s+regret\b",
            r"(?i)\bfailing\s+to\b",
            r"(?i)\brisk\s+losing\b",
            r"(?i)\bwithout\s+this\s+you\b",
            r"(?i)\bcan'?t\s+afford\s+to\s+miss\b"
        ],
        "severity": "medium",
        "description": "Uses fear to motivate action rather than genuine value",
        "ethical_alternative": "Focus on positive outcomes and genuine benefits instead of fear.",
        "questions": ["Does this exploit anxiety?", "Would a calm person find this manipulative?"]
    },
    "confirmshaming": {
        "patterns": [
            r"(?i)no\s*,?\s*I\s+(don'?t\s+want|prefer|like)\s+to\s+(stay|remain|be)\s+(poor|broke|unsuccessful|unhappy|stupid|ignorant)",
            r"(?i)I\s+don'?t\s+(want|need|care\s+about)\s+(success|money|health|happiness|improvement)",
            r"(?i)no\s+thanks\s*,?\s*I('?m|\s+am)\s+(fine|happy)\s+(being|staying)\s+(broke|poor|unsuccessful)",
            r"(?i)I('?ll|\s+will)\s+pass\s+on\s+(success|improvement|growth)"
        ],
        "severity": "high",
        "description": "Guilt-trips users for declining an offer",
        "ethical_alternative": "Use neutral decline options like 'No thanks' or 'Maybe later'",
        "questions": ["Does declining make the user feel bad about themselves?"]
    },
    "false_authority": {
        "patterns": [
            r"(?i)\bexperts?\s+(say|agree|recommend)\b",
            r"(?i)\bscientists?\s+(say|prove|confirm)\b",
            r"(?i)\bstudies?\s+show\b",
            r"(?i)\bresearch\s+(proves?|shows?)\b",
            r"(?i)\bclinically\s+proven\b",
            r"(?i)\bdoctors?\s+(recommend|approve)\b"
        ],
        "severity": "medium",
        "description": "Claims authority without specific citation",
        "ethical_alternative": "Cite specific studies, researchers, or sources that can be verified.",
        "questions": ["Can this claim be verified?", "Is the source credible and named?"]
    },
    "social_pressure": {
        "patterns": [
            r"(?i)\beveryone('?s|\s+is)\s+(using|buying|doing)\b",
            r"(?i)\b\d+\s*(million|k|thousand|hundred)\s+(people|users|customers)\b",
            r"(?i)\bjoin\s+the\s+\d+\b",
            r"(?i)\bdon'?t\s+be\s+the\s+only\s+one\b",
            r"(?i)\ball\s+your\s+(friends|competitors)\b"
        ],
        "severity": "low",
        "description": "Uses social pressure to influence decision",
        "ethical_alternative": "Social proof is ethical when accurate. Ensure numbers are real and current.",
        "questions": ["Are these numbers accurate?", "Is this creating unhealthy FOMO?"]
    },
    "hidden_costs": {
        "patterns": [
            r"(?i)\bstarting\s+(at|from)\s+\$",
            r"(?i)\bas\s+low\s+as\b",
            r"(?i)\bfrom\s+only\s+\$",
            r"(?i)\bplus\s+(shipping|handling|fees)\b",
            r"(?i)\badditional\s+(fees|charges)\s+may\s+apply\b",
            r"(?i)\bexcluding\b.*\b(tax|fees|shipping)\b"
        ],
        "severity": "medium",
        "description": "May indicate costs that aren't immediately clear",
        "ethical_alternative": "Show full pricing upfront. Be transparent about all costs.",
        "questions": ["Is the full cost clear?", "Are there surprise fees later?"]
    },
    "exaggerated_claims": {
        "patterns": [
            r"(?i)\bguaranteed\s+(results?|success)\b",
            r"(?i)\b100%\s+(effective|guaranteed|success)\b",
            r"(?i)\bnever\s+fail\b",
            r"(?i)\balways\s+works?\b",
            r"(?i)\binstant\s+(results?|success|transformation)\b",
            r"(?i)\bmiracle\b",
            r"(?i)\blife-?changing\b",
            r"(?i)\brevolutionary\b"
        ],
        "severity": "medium",
        "description": "Makes claims that may be impossible to substantiate",
        "ethical_alternative": "Use specific, verifiable claims. Qualify broad statements.",
        "questions": ["Can this be proven?", "Is there an asterisk or fine print?"]
    },
    "manipulation_language": {
        "patterns": [
            r"(?i)\bsecret\s+(method|technique|formula)\b",
            r"(?i)\bthey\s+don'?t\s+want\s+you\s+to\s+know\b",
            r"(?i)\bhidden\s+(truth|secret)\b",
            r"(?i)\bunlock\s+the\s+secret\b",
            r"(?i)\bweird\s+trick\b"
        ],
        "severity": "high",
        "description": "Uses conspiracy-style language to create intrigue",
        "ethical_alternative": "Be direct about what you offer. Avoid manufactured mystery.",
        "questions": ["Is this creating false intrigue?", "Is there actually a secret?"]
    }
}

# Positive patterns (ethical persuasion)
POSITIVE_PATTERNS = {
    "clear_value": [
        r"(?i)\byou('?ll)?\s+(get|receive|learn|discover)\b",
        r"(?i)\bhelps?\s+you\b",
        r"(?i)\bsave\s+(time|money|effort)\b",
        r"(?i)\bimprove\s+your\b"
    ],
    "transparency": [
        r"(?i)\bno\s+hidden\s+(fees|costs)\b",
        r"(?i)\bfull\s+refund\b",
        r"(?i)\bcancel\s+anytime\b",
        r"(?i)\bno\s+obligation\b",
        r"(?i)\brisk-?free\b"
    ],
    "specific_proof": [
        r"(?i)\bcase\s+study\b",
        r"(?i)\baccording\s+to\s+\[?\w+",
        r"(?i)\bsource:\s*\w+",
        r"(?i)\bverified\s+by\b"
    ],
    "respect_autonomy": [
        r"(?i)\byour\s+choice\b",
        r"(?i)\bif\s+it('?s|\s+is)\s+right\s+for\s+you\b",
        r"(?i)\bdecide\s+for\s+yourself\b",
        r"(?i)\bno\s+pressure\b"
    ]
}


def resolve_input_file(file_arg: str) -> Path:
    raw = Path((file_arg or "").strip())
    if not raw:
        raise ValueError("Input file path is empty")
    resolved = raw.resolve() if raw.is_absolute() else (SKILL_ROOT / raw).resolve()
    try:
        resolved.relative_to(SKILL_ROOT)
    except ValueError as exc:
        raise ValueError("Input file must stay inside the skill directory.") from exc
    if not resolved.is_file():
        raise ValueError(f"Input file not found: {file_arg}")
    try:
        if resolved.stat().st_size > MAX_INPUT_FILE_BYTES:
            raise ValueError(f"Input file exceeds {MAX_INPUT_FILE_BYTES} bytes.")
    except OSError as exc:
        raise ValueError(f"Unable to stat input file: {file_arg}") from exc
    return resolved


def read_input_file(file_arg: str) -> str:
    resolved = resolve_input_file(file_arg)
    try:
        return resolved.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise ValueError(f"Unable to read input file: {file_arg}") from exc


def analyze_copy(text: str, strict: bool = False) -> Result:
    """Analyze marketing copy for manipulation patterns."""
    errors = []
    warnings = []
    
    if not text or not text.strip():
        errors.append("No text provided for analysis")
        return Result(success=False, data={}, errors=errors, warnings=warnings)
    
    findings = []
    positive_findings = []
    total_score = 100  # Start with perfect score
    
    # Check for manipulation patterns
    for pattern_name, pattern_info in MANIPULATION_PATTERNS.items():
        matches = []
        for regex in pattern_info["patterns"]:
            found = re.findall(regex, text)
            matches.extend(found)
        
        if matches:
            severity_deduction = {"high": 20, "medium": 10, "low": 5}
            deduction = severity_deduction.get(pattern_info["severity"], 10)
            if strict:
                deduction *= 1.5
            total_score -= min(deduction * len(set(matches)), deduction * 3)
            
            findings.append({
                "pattern": pattern_name,
                "severity": pattern_info["severity"],
                "matches": list(set(matches))[:5],  # Limit to 5 examples
                "description": pattern_info["description"],
                "ethical_alternative": pattern_info["ethical_alternative"],
                "questions_to_ask": pattern_info["questions"]
            })
    
    # Check for positive patterns
    for pattern_name, patterns in POSITIVE_PATTERNS.items():
        matches = []
        for regex in patterns:
            found = re.findall(regex, text)
            matches.extend(found)
        
        if matches:
            total_score += min(5 * len(set(matches)), 15)  # Bonus for good practices
            positive_findings.append({
                "pattern": pattern_name,
                "matches": list(set(matches))[:3]
            })
    
    # Ensure score is within bounds
    total_score = max(0, min(100, total_score))
    
    # Generate verdict
    if total_score >= 80:
        verdict = "PASS"
        verdict_detail = "Copy appears ethical with minor or no concerns"
    elif total_score >= 60:
        verdict = "REVIEW"
        verdict_detail = "Copy has some concerning patterns that should be reviewed"
    else:
        verdict = "FAIL"
        verdict_detail = "Copy contains multiple manipulation patterns and needs revision"
    
    # Generate recommendations
    recommendations = []
    if findings:
        recommendations.append("Review flagged patterns and consider ethical alternatives")
        
        # Pattern-specific recommendations
        pattern_names = [f["pattern"] for f in findings]
        if "confirmshaming" in pattern_names:
            recommendations.append("PRIORITY: Replace confirmshaming decline options with neutral alternatives")
        if "fake_urgency" in pattern_names:
            recommendations.append("Verify all urgency claims are genuine; remove artificial scarcity")
        if "exaggerated_claims" in pattern_names:
            recommendations.append("Qualify or remove absolute claims; add specific evidence")
        if "hidden_costs" in pattern_names:
            recommendations.append("Ensure all costs are transparent and visible upfront")
    
    if not positive_findings:
        recommendations.append("Add positive elements: clear value statements, transparency signals")
    
    analysis = {
        "verdict": verdict,
        "verdict_detail": verdict_detail,
        "score": total_score,
        "text_analyzed": text[:200] + "..." if len(text) > 200 else text,
        "manipulation_patterns_found": findings,
        "positive_patterns_found": positive_findings,
        "recommendations": recommendations,
        "summary": {
            "total_issues": len(findings),
            "high_severity": len([f for f in findings if f["severity"] == "high"]),
            "medium_severity": len([f for f in findings if f["severity"] == "medium"]),
            "low_severity": len([f for f in findings if f["severity"] == "low"]),
            "positive_elements": len(positive_findings)
        }
    }
    
    return Result(
        success=True,
        data=analysis,
        errors=errors,
        warnings=warnings
    )


def main():
    parser = argparse.ArgumentParser(description="Analyze marketing copy for manipulation patterns")
    parser.add_argument("--copy", type=str, help="Marketing copy to analyze")
    parser.add_argument("--file", type=str, help="File containing marketing copy")
    parser.add_argument("--strict", action="store_true", help="Use stricter analysis")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    # Get text to analyze
    if args.file:
        try:
            text = read_input_file(args.file)
        except ValueError as e:
            if args.json:
                print(json.dumps(asdict(Result(success=False, data={}, errors=[str(e)], warnings=[])), indent=2))
            else:
                print(f"Error reading file: {e}")
            sys.exit(1)
    elif args.copy:
        text = args.copy
    else:
        print("Error: Provide either --copy or --file")
        sys.exit(1)
    
    result = analyze_copy(text, args.strict)
    
    if args.json:
        print(json.dumps(asdict(result), indent=2))
    else:
        if not result.success:
            print("ANALYSIS FAILED")
            for error in result.errors:
                print(f"  ERROR: {error}")
            sys.exit(1)
        
        data = result.data
        
        print("=" * 60)
        print("MARKETING COPY BIAS ANALYSIS")
        print("=" * 60)
        
        # Verdict with color-coding hint
        verdict_emoji = {"PASS": "✅", "REVIEW": "⚠️", "FAIL": "❌"}
        print(f"\n{verdict_emoji.get(data['verdict'], '•')} VERDICT: {data['verdict']}")
        print(f"   {data['verdict_detail']}")
        print(f"   Score: {data['score']}/100")
        
        print(f"\n📝 TEXT ANALYZED:")
        print(f"   \"{data['text_analyzed']}\"")
        
        # Summary
        summary = data["summary"]
        print(f"\n📊 SUMMARY")
        print(f"   Issues Found: {summary['total_issues']}")
        if summary["total_issues"] > 0:
            print(f"   - High Severity: {summary['high_severity']}")
            print(f"   - Medium Severity: {summary['medium_severity']}")
            print(f"   - Low Severity: {summary['low_severity']}")
        print(f"   Positive Elements: {summary['positive_elements']}")
        
        # Manipulation patterns
        if data["manipulation_patterns_found"]:
            print(f"\n⚠️ MANIPULATION PATTERNS DETECTED")
            for finding in data["manipulation_patterns_found"]:
                severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                print(f"\n   {severity_emoji.get(finding['severity'], '•')} {finding['pattern'].upper()} [{finding['severity']}]")
                print(f"      Description: {finding['description']}")
                print(f"      Found: {', '.join(finding['matches'][:3])}")
                print(f"      Ethical Alternative: {finding['ethical_alternative']}")
        
        # Positive patterns
        if data["positive_patterns_found"]:
            print(f"\n✅ POSITIVE PATTERNS FOUND")
            for finding in data["positive_patterns_found"]:
                print(f"   • {finding['pattern']}: {', '.join(finding['matches'][:2])}")
        
        # Recommendations
        if data["recommendations"]:
            print(f"\n💡 RECOMMENDATIONS")
            for rec in data["recommendations"]:
                print(f"   • {rec}")
        
        print("\n" + "=" * 60)
    
    # Exit code based on verdict
    exit_codes = {"PASS": 0, "REVIEW": 0, "FAIL": 10}
    sys.exit(exit_codes.get(result.data.get("verdict", "FAIL"), 1))


if __name__ == "__main__":
    main()
