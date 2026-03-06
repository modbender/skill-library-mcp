#!/usr/bin/env python3
"""
Conversion Audit Tool

Analyzes conversion funnels and provides psychology-based optimization recommendations.
Uses behavioral economics, persuasion science, and UX psychology principles.

Usage:
    python conversion_audit.py --funnel signup --segment new_users
    python conversion_audit.py --funnel checkout --segment returning --stage decision
"""

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict


@dataclass
class Result:
    """Standard result structure for skill scripts."""
    success: bool
    data: dict
    errors: List[str]
    warnings: List[str]


# Funnel stage psychological frameworks
FUNNEL_STAGES = {
    "awareness": {
        "user_mindset": "Curious, skeptical, distracted",
        "primary_need": "Relevance, credibility",
        "key_metrics": ["Impressions", "CTR", "Bounce rate"],
        "psychological_levers": [
            {"lever": "Attention capture", "mechanism": "Pattern interrupt, novelty", "ethical": True},
            {"lever": "Relevance signaling", "mechanism": "Immediate value proposition", "ethical": True},
            {"lever": "Curiosity gap", "mechanism": "Information gap creates pull", "ethical": True}
        ],
        "common_failures": [
            "Unclear value proposition",
            "Generic messaging",
            "Mismatch with audience expectations"
        ]
    },
    "interest": {
        "user_mindset": "Engaged, evaluating, comparing",
        "primary_need": "Understanding, value clarity",
        "key_metrics": ["Time on page", "Scroll depth", "Pages per session"],
        "psychological_levers": [
            {"lever": "Social proof", "mechanism": "Others' behavior reduces uncertainty", "ethical": True},
            {"lever": "Authority", "mechanism": "Expert endorsement builds trust", "ethical": True},
            {"lever": "Specificity", "mechanism": "Concrete details more believable", "ethical": True}
        ],
        "common_failures": [
            "Information overload",
            "Unclear differentiation",
            "No proof points"
        ]
    },
    "consideration": {
        "user_mindset": "Comparing options, anxious about decision",
        "primary_need": "Trust, differentiation, risk reduction",
        "key_metrics": ["Return visits", "Comparison page views", "Content downloads"],
        "psychological_levers": [
            {"lever": "Loss aversion framing", "mechanism": "What they lose by not acting", "ethical": True},
            {"lever": "Comparison facilitation", "mechanism": "Make your option clearly superior", "ethical": True},
            {"lever": "Testimonials", "mechanism": "Reduce perceived risk via others' success", "ethical": True}
        ],
        "common_failures": [
            "No clear differentiation",
            "Unaddressed objections",
            "Friction in evaluation process"
        ]
    },
    "decision": {
        "user_mindset": "Ready to act, seeking confirmation",
        "primary_need": "Risk reduction, confidence, simplicity",
        "key_metrics": ["Cart additions", "Form starts", "CTA clicks"],
        "psychological_levers": [
            {"lever": "Friction removal", "mechanism": "Reduce steps and cognitive load", "ethical": True},
            {"lever": "Risk reversal", "mechanism": "Guarantees, free trials", "ethical": True},
            {"lever": "Urgency (real)", "mechanism": "Genuine scarcity or time limits", "ethical": True}
        ],
        "common_failures": [
            "Complex checkout process",
            "Hidden costs",
            "No guarantee or risk reversal"
        ]
    },
    "conversion": {
        "user_mindset": "Committed, vulnerable to regret",
        "primary_need": "Confirmation, reassurance, simplicity",
        "key_metrics": ["Completion rate", "Drop-off points", "Error rates"],
        "psychological_levers": [
            {"lever": "Progress indicators", "mechanism": "Sunk cost and completion drive", "ethical": True},
            {"lever": "Trust signals", "mechanism": "Security badges, testimonials", "ethical": True},
            {"lever": "Commitment consistency", "mechanism": "Small steps build momentum", "ethical": True}
        ],
        "common_failures": [
            "Surprise fees or requirements",
            "Too many form fields",
            "No progress visibility"
        ]
    },
    "retention": {
        "user_mindset": "Post-purchase, evaluating satisfaction",
        "primary_need": "Confirmation, support, value realization",
        "key_metrics": ["NPS", "Churn rate", "Repeat purchase", "Engagement"],
        "psychological_levers": [
            {"lever": "Quick wins", "mechanism": "Early value = commitment", "ethical": True},
            {"lever": "Habit formation", "mechanism": "Routine integration", "ethical": True},
            {"lever": "Community", "mechanism": "Belonging and social proof", "ethical": True}
        ],
        "common_failures": [
            "No onboarding",
            "Difficult to get value",
            "No engagement post-purchase"
        ]
    }
}

# Segment-specific considerations
SEGMENTS = {
    "new_users": {
        "characteristics": "High uncertainty, low trust, comparing options",
        "priorities": ["Clear value proposition", "Trust building", "Low-commitment entry"],
        "watch_for": ["Information overload", "Assumed knowledge", "Jargon"]
    },
    "returning": {
        "characteristics": "Familiar with offering, evaluating decision",
        "priorities": ["Remind of value", "Address lingering objections", "Facilitate decision"],
        "watch_for": ["Repetitive content", "Not acknowledging their familiarity"]
    },
    "price_sensitive": {
        "characteristics": "Value-focused, comparison shopping",
        "priorities": ["ROI clarity", "Value stacking", "Payment flexibility"],
        "watch_for": ["Hidden costs", "Unclear pricing", "No value justification"]
    },
    "enterprise": {
        "characteristics": "Multiple stakeholders, longer cycle, risk-averse",
        "priorities": ["Case studies", "ROI documentation", "Support/implementation clarity"],
        "watch_for": ["Consumer-focused messaging", "Missing stakeholder content"]
    },
    "mobile": {
        "characteristics": "Distracted, limited screen, touch interface",
        "priorities": ["Simplified forms", "Clear CTAs", "Fast loading"],
        "watch_for": ["Desktop-designed experiences", "Small touch targets"]
    }
}

# Common funnel types with specific recommendations
FUNNEL_TYPES = {
    "signup": {
        "stages": ["awareness", "interest", "decision", "conversion", "retention"],
        "critical_metrics": ["Form start rate", "Form completion rate", "Activation rate"],
        "key_optimizations": [
            "Reduce form fields to minimum",
            "Show value before asking for commitment",
            "Provide social proof near signup",
            "Immediate value after signup"
        ]
    },
    "checkout": {
        "stages": ["interest", "decision", "conversion"],
        "critical_metrics": ["Cart abandonment rate", "Checkout completion rate"],
        "key_optimizations": [
            "Show total cost early (no surprises)",
            "Guest checkout option",
            "Progress indicator",
            "Trust badges and guarantees"
        ]
    },
    "lead_gen": {
        "stages": ["awareness", "interest", "conversion"],
        "critical_metrics": ["Landing page conversion", "Lead quality score"],
        "key_optimizations": [
            "Clear value exchange",
            "Minimal form fields",
            "Strong proof points",
            "Specific, relevant offer"
        ]
    },
    "saas_trial": {
        "stages": ["awareness", "interest", "decision", "conversion", "retention"],
        "critical_metrics": ["Trial start rate", "Activation rate", "Trial-to-paid conversion"],
        "key_optimizations": [
            "Frictionless trial start (no credit card)",
            "Onboarding to first value",
            "Usage-based nurturing",
            "Clear upgrade path"
        ]
    },
    "ecommerce": {
        "stages": ["awareness", "interest", "consideration", "decision", "conversion", "retention"],
        "critical_metrics": ["Add-to-cart rate", "Cart abandonment", "Repeat purchase rate"],
        "key_optimizations": [
            "High-quality product images",
            "Reviews and social proof",
            "Clear shipping and return info",
            "Post-purchase engagement"
        ]
    }
}

# Dark patterns to flag (ethical violations)
DARK_PATTERNS = [
    {"pattern": "Hidden costs", "description": "Surprise fees revealed late in checkout"},
    {"pattern": "Forced continuity", "description": "Auto-renewal without clear notice"},
    {"pattern": "Confirmshaming", "description": "Guilt-tripping decline options"},
    {"pattern": "Roach motel", "description": "Easy to sign up, hard to cancel"},
    {"pattern": "Misdirection", "description": "Distracting from important information"},
    {"pattern": "Bait and switch", "description": "Advertising one thing, delivering another"},
    {"pattern": "Fake urgency", "description": "False scarcity or countdown timers"},
    {"pattern": "Trick questions", "description": "Confusing opt-in/opt-out language"}
]


def generate_audit(funnel: str, segment: str, stage: Optional[str] = None) -> Result:
    """Generate conversion audit with recommendations."""
    errors = []
    warnings = []
    
    funnel_lower = funnel.lower()
    segment_lower = segment.lower()
    
    # Validate inputs
    if funnel_lower not in FUNNEL_TYPES:
        available = ", ".join(FUNNEL_TYPES.keys())
        warnings.append(f"Funnel '{funnel}' not predefined. Using generic analysis. Available: {available}")
        funnel_data = {
            "stages": list(FUNNEL_STAGES.keys()),
            "critical_metrics": ["Conversion rate at each stage"],
            "key_optimizations": ["Apply stage-specific principles"]
        }
    else:
        funnel_data = FUNNEL_TYPES[funnel_lower]
    
    if segment_lower not in SEGMENTS:
        available = ", ".join(SEGMENTS.keys())
        warnings.append(f"Segment '{segment}' not predefined. Using general recommendations. Available: {available}")
        segment_data = None
    else:
        segment_data = SEGMENTS[segment_lower]
    
    # Determine which stages to analyze
    if stage:
        stage_lower = stage.lower()
        if stage_lower not in FUNNEL_STAGES:
            available = ", ".join(FUNNEL_STAGES.keys())
            errors.append(f"Stage '{stage}' not recognized. Available: {available}")
            return Result(success=False, data={}, errors=errors, warnings=warnings)
        stages_to_analyze = [stage_lower]
    else:
        stages_to_analyze = funnel_data["stages"]
    
    # Build audit
    audit = {
        "funnel_overview": {
            "funnel_type": funnel,
            "target_segment": segment,
            "stages_analyzed": stages_to_analyze,
            "critical_metrics": funnel_data["critical_metrics"],
            "key_optimizations": funnel_data["key_optimizations"]
        },
        "segment_analysis": {
            "segment": segment,
            "characteristics": segment_data["characteristics"] if segment_data else "General audience",
            "priorities": segment_data["priorities"] if segment_data else ["Clear value", "Trust", "Simplicity"],
            "watch_for": segment_data["watch_for"] if segment_data else ["Generic messaging"]
        },
        "stage_analysis": [],
        "ethical_checklist": {
            "dark_patterns_to_avoid": DARK_PATTERNS,
            "ethical_principles": [
                "Transparency: Clear about intent and costs",
                "Autonomy: Respect user's free choice",
                "Beneficence: Genuine value provided",
                "Non-maleficence: Avoid harm",
                "Truthfulness: Honest claims only"
            ]
        },
        "optimization_priorities": []
    }
    
    # Analyze each stage
    for stage_name in stages_to_analyze:
        stage_info = FUNNEL_STAGES[stage_name]
        stage_analysis = {
            "stage": stage_name,
            "user_mindset": stage_info["user_mindset"],
            "primary_need": stage_info["primary_need"],
            "key_metrics": stage_info["key_metrics"],
            "psychological_levers": stage_info["psychological_levers"],
            "common_failures": stage_info["common_failures"],
            "segment_specific_recommendations": _get_segment_recommendations(stage_name, segment_lower)
        }
        audit["stage_analysis"].append(stage_analysis)
    
    # Generate prioritized optimization list
    audit["optimization_priorities"] = _generate_priorities(stages_to_analyze, segment_lower, funnel_lower)
    
    return Result(
        success=True,
        data=audit,
        errors=errors,
        warnings=warnings
    )


def _get_segment_recommendations(stage: str, segment: str) -> List[str]:
    """Get segment-specific recommendations for a stage."""
    recommendations = []
    
    if segment == "new_users":
        if stage == "awareness":
            recommendations.append("Lead with clear value proposition, not features")
        elif stage == "interest":
            recommendations.append("Provide social proof prominently")
        elif stage == "decision":
            recommendations.append("Offer low-commitment entry point")
    
    elif segment == "returning":
        if stage == "awareness":
            recommendations.append("Acknowledge their familiarity")
        elif stage == "decision":
            recommendations.append("Address lingering objections directly")
    
    elif segment == "price_sensitive":
        if stage == "consideration":
            recommendations.append("Emphasize value and ROI, not just price")
        elif stage == "decision":
            recommendations.append("Offer payment flexibility if possible")
    
    elif segment == "enterprise":
        if stage == "consideration":
            recommendations.append("Provide case studies and ROI documentation")
        elif stage == "decision":
            recommendations.append("Address multiple stakeholder concerns")
    
    elif segment == "mobile":
        if stage == "conversion":
            recommendations.append("Minimize form fields, enable autofill")
            recommendations.append("Large touch targets for CTAs")
    
    return recommendations if recommendations else ["Apply general stage principles"]


def _generate_priorities(stages: List[str], segment: str, funnel: str) -> List[Dict]:
    """Generate prioritized optimization recommendations."""
    priorities = []
    
    # High-impact, cross-stage optimizations
    priorities.append({
        "priority": 1,
        "category": "Trust & Credibility",
        "recommendation": "Add social proof (testimonials, logos, numbers) at key decision points",
        "psychology": "Social proof reduces uncertainty, especially for new users",
        "impact": "High"
    })
    
    priorities.append({
        "priority": 2,
        "category": "Friction Reduction",
        "recommendation": "Audit and minimize form fields; remove any non-essential steps",
        "psychology": "Each field/step is a potential drop-off point",
        "impact": "High"
    })
    
    priorities.append({
        "priority": 3,
        "category": "Value Clarity",
        "recommendation": "Ensure value proposition is clear within 5 seconds of page load",
        "psychology": "Users decide quickly whether content is relevant",
        "impact": "High"
    })
    
    if "decision" in stages or "conversion" in stages:
        priorities.append({
            "priority": 4,
            "category": "Risk Reversal",
            "recommendation": "Add or prominently display guarantees, free trials, or easy cancellation",
            "psychology": "Risk reversal addresses loss aversion at decision point",
            "impact": "Medium-High"
        })
    
    if "retention" in stages:
        priorities.append({
            "priority": 5,
            "category": "Onboarding",
            "recommendation": "Design path to first value/success within first session",
            "psychology": "Early value creates commitment and habit formation",
            "impact": "High for LTV"
        })
    
    # Segment-specific priorities
    if segment == "mobile":
        priorities.insert(1, {
            "priority": 0,
            "category": "Mobile Experience",
            "recommendation": "Optimize for mobile: large CTAs, minimal typing, fast load",
            "psychology": "Mobile users are distracted with limited patience",
            "impact": "Critical for mobile segment"
        })
    
    return priorities


def main():
    parser = argparse.ArgumentParser(description="Generate conversion funnel audit")
    parser.add_argument("--funnel", type=str, required=True, 
                       help="Funnel type (signup, checkout, lead_gen, saas_trial, ecommerce)")
    parser.add_argument("--segment", type=str, required=True,
                       help="Target segment (new_users, returning, price_sensitive, enterprise, mobile)")
    parser.add_argument("--stage", type=str, default=None,
                       help="Specific stage to analyze (awareness, interest, consideration, decision, conversion, retention)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    result = generate_audit(args.funnel, args.segment, args.stage)
    
    if args.json:
        print(json.dumps(asdict(result), indent=2))
    else:
        if not result.success:
            print("AUDIT FAILED")
            for error in result.errors:
                print(f"  ERROR: {error}")
            sys.exit(1)
        
        print("=" * 70)
        print("CONVERSION FUNNEL AUDIT REPORT")
        print("=" * 70)
        
        data = result.data
        
        print("\n📊 FUNNEL OVERVIEW")
        overview = data["funnel_overview"]
        print(f"  Funnel Type: {overview['funnel_type']}")
        print(f"  Target Segment: {overview['target_segment']}")
        print(f"  Stages Analyzed: {', '.join(overview['stages_analyzed'])}")
        print(f"  Critical Metrics: {', '.join(overview['critical_metrics'])}")
        
        print("\n👥 SEGMENT ANALYSIS")
        seg = data["segment_analysis"]
        print(f"  Segment: {seg['segment']}")
        print(f"  Characteristics: {seg['characteristics']}")
        print("  Priorities:")
        for p in seg["priorities"]:
            print(f"    • {p}")
        print("  Watch For:")
        for w in seg["watch_for"]:
            print(f"    ⚠ {w}")
        
        print("\n📈 STAGE-BY-STAGE ANALYSIS")
        for stage_data in data["stage_analysis"]:
            print(f"\n  --- {stage_data['stage'].upper()} ---")
            print(f"  User Mindset: {stage_data['user_mindset']}")
            print(f"  Primary Need: {stage_data['primary_need']}")
            print(f"  Key Metrics: {', '.join(stage_data['key_metrics'])}")
            print("  Psychological Levers (Ethical):")
            for lever in stage_data["psychological_levers"]:
                print(f"    ✓ {lever['lever']}: {lever['mechanism']}")
            print("  Common Failures:")
            for failure in stage_data["common_failures"]:
                print(f"    ✗ {failure}")
        
        print("\n🎯 OPTIMIZATION PRIORITIES")
        for opt in data["optimization_priorities"]:
            print(f"\n  #{opt['priority']} [{opt['category']}]")
            print(f"     Recommendation: {opt['recommendation']}")
            print(f"     Psychology: {opt['psychology']}")
            print(f"     Impact: {opt['impact']}")
        
        print("\n⚖️ ETHICAL CHECKLIST")
        print("  Dark Patterns to AVOID:")
        for dp in data["ethical_checklist"]["dark_patterns_to_avoid"][:5]:
            print(f"    ✗ {dp['pattern']}: {dp['description']}")
        
        if result.warnings:
            print("\n⚡ WARNINGS")
            for w in result.warnings:
                print(f"  • {w}")
        
        print("\n" + "=" * 70)
    
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
