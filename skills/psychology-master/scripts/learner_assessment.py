#!/usr/bin/env python3
"""
Learner Assessment Tool

Generates personalized learning recommendations based on age, skill type, and context.
Uses evidence-based developmental psychology and learning science frameworks.

Usage:
    python learner_assessment.py --age 25 --skill coding --context work
    python learner_assessment.py --age 8 --skill english --context school --time 30
"""

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from typing import List, Optional


@dataclass
class Result:
    """Standard result structure for skill scripts."""
    success: bool
    data: dict
    errors: List[str]
    warnings: List[str]


# Developmental stage definitions
DEVELOPMENTAL_STAGES = {
    "early_childhood": {
        "age_range": (3, 6),
        "cognitive": "Preoperational",
        "attention_span": "5-15 minutes",
        "learning_style": "Play-based, sensory, narrative",
        "key_principles": [
            "High repetition with variation",
            "Multisensory engagement",
            "Adult scaffolding essential",
            "Immediate positive feedback",
            "Short sessions (10-20 min max)"
        ]
    },
    "childhood": {
        "age_range": (7, 12),
        "cognitive": "Concrete Operational",
        "attention_span": "15-30 minutes",
        "learning_style": "Guided discovery, visual aids, hands-on",
        "key_principles": [
            "Concrete to abstract progression",
            "Explicit strategy teaching",
            "Gamification effective",
            "Peer collaboration valuable",
            "Growth mindset framing"
        ]
    },
    "adolescence": {
        "age_range": (13, 17),
        "cognitive": "Formal Operational (emerging)",
        "attention_span": "30-45 minutes",
        "learning_style": "Project-based, autonomous, real-world",
        "key_principles": [
            "Autonomy and choice critical",
            "Connect to identity and goals",
            "Peer learning structures",
            "Real-world applications",
            "Safe failure environments"
        ]
    },
    "emerging_adult": {
        "age_range": (18, 25),
        "cognitive": "Post-formal",
        "attention_span": "45-90 minutes (deep work)",
        "learning_style": "Deliberate practice, expert modeling",
        "key_principles": [
            "Challenge at edge of ability",
            "High-quality feedback",
            "Metacognition development",
            "Clear skill pathways",
            "Mentorship valuable"
        ]
    },
    "adult": {
        "age_range": (26, 64),
        "cognitive": "Crystallized intelligence growing",
        "attention_span": "30-60 minutes",
        "learning_style": "Problem-centered, applied, efficient",
        "key_principles": [
            "Leverage prior knowledge",
            "Immediate utility focus",
            "Respect time constraints",
            "Just-in-time learning",
            "Self-directed approach"
        ]
    },
    "older_adult": {
        "age_range": (65, 100),
        "cognitive": "Wisdom, pattern recognition",
        "attention_span": "20-45 minutes with breaks",
        "learning_style": "Self-paced, multimodal, supportive",
        "key_principles": [
            "Reduce time pressure",
            "Overlearning beneficial",
            "Confidence building important",
            "External memory aids",
            "Social learning engagement"
        ]
    }
}

# Skill-specific recommendations
SKILL_FRAMEWORKS = {
    "coding": {
        "name": "Programming",
        "stages": ["Syntax", "Semantics", "Problem decomposition", "Patterns", "Architecture"],
        "methods": {
            "early_childhood": "Not recommended; consider computational thinking games",
            "childhood": "Visual programming (Scratch), game-based, immediate feedback",
            "adolescence": "Project-based, real apps, version control, community",
            "emerging_adult": "Deliberate practice, code review, build portfolio",
            "adult": "Just-in-time learning, project-driven, leverage experience",
            "older_adult": "Slower pace, clear goals, practical applications"
        },
        "practice_structure": "Build projects immediately; avoid tutorial hell"
    },
    "english": {
        "name": "English Language",
        "stages": ["Phonology", "Vocabulary", "Grammar", "Fluency", "Advanced"],
        "methods": {
            "early_childhood": "Immersion, songs, stories, TPR",
            "childhood": "Structured input, games, high-frequency words",
            "adolescence": "Communicative, content-based, real media",
            "emerging_adult": "Comprehensible input, spaced repetition, conversation",
            "adult": "Efficiency focus, spaced repetition, practical contexts",
            "older_adult": "Multimodal, social learning, patient pacing"
        },
        "practice_structure": "Daily exposure; focus on high-frequency vocabulary first"
    },
    "math": {
        "name": "Mathematics",
        "stages": ["Pre-numeric", "Numeric", "Operational", "Abstract"],
        "methods": {
            "early_childhood": "Counting, sorting, concrete manipulatives",
            "childhood": "CRA progression, number sense, manipulatives to symbols",
            "adolescence": "Problem-based, real applications, productive struggle",
            "emerging_adult": "Worked examples then practice, interleaving",
            "adult": "Application-focused, relevant problems",
            "older_adult": "Build on existing knowledge, practical applications"
        },
        "practice_structure": "Concrete-Representational-Abstract sequence"
    },
    "music": {
        "name": "Music",
        "stages": ["Listening", "Basic technique", "Repertoire", "Interpretation", "Mastery"],
        "methods": {
            "early_childhood": "Exploration, rhythm games, singing",
            "childhood": "Fundamentals, simple pieces, ensemble participation",
            "adolescence": "Genre exploration, performance opportunities",
            "emerging_adult": "Deliberate practice, recording analysis",
            "adult": "Goal-focused, efficient practice, enjoyment balance",
            "older_adult": "Social music-making, accessible repertoire"
        },
        "practice_structure": "Distributed practice; quality over quantity"
    },
    "language": {
        "name": "Foreign Language",
        "stages": ["Silent period", "Early production", "Speech emergence", "Intermediate", "Advanced"],
        "methods": {
            "early_childhood": "Immersion, play, songs, native input",
            "childhood": "TPR, stories, games, minimal grammar",
            "adolescence": "Communicative, authentic materials, peer practice",
            "emerging_adult": "Comprehensible input, spaced repetition, immersion",
            "adult": "Efficiency methods, spaced repetition, conversation focus",
            "older_adult": "Social learning, travel contexts, patient pacing"
        },
        "practice_structure": "High-frequency words first; comprehensible input daily"
    }
}

CONTEXTS = {
    "school": {
        "constraints": "Curriculum requirements, grading, peer comparison",
        "opportunities": "Structured environment, teacher support, peer learning",
        "recommendations": ["Complement formal instruction", "Focus on understanding over grades"]
    },
    "work": {
        "constraints": "Limited time, immediate application needed",
        "opportunities": "Clear relevance, motivated learner, resources",
        "recommendations": ["Just-in-time learning", "Apply immediately", "Micro-learning"]
    },
    "hobby": {
        "constraints": "Variable motivation, competing priorities",
        "opportunities": "Intrinsic motivation, flexibility, enjoyment focus",
        "recommendations": ["Maintain enjoyment", "Social connections", "Visible progress"]
    },
    "career_change": {
        "constraints": "Pressure to succeed, time-sensitive, broad scope",
        "opportunities": "High motivation, clear goal, resource investment",
        "recommendations": ["Structured pathway", "Mentorship", "Portfolio building"]
    }
}


def get_developmental_stage(age: int) -> str:
    """Determine developmental stage from age."""
    for stage, info in DEVELOPMENTAL_STAGES.items():
        min_age, max_age = info["age_range"]
        if min_age <= age <= max_age:
            return stage
    return "adult" if age > 64 else "early_childhood"


def generate_assessment(age: int, skill: str, context: str, time_per_day: int) -> Result:
    """Generate personalized learning assessment and recommendations."""
    errors = []
    warnings = []
    
    # Validate inputs
    if age < 3:
        errors.append("Age must be 3 or older for structured learning recommendations")
        return Result(success=False, data={}, errors=errors, warnings=warnings)
    
    skill_lower = skill.lower()
    if skill_lower not in SKILL_FRAMEWORKS:
        available = ", ".join(SKILL_FRAMEWORKS.keys())
        warnings.append(f"Skill '{skill}' not in predefined frameworks. Using general principles. Available: {available}")
        skill_data = None
    else:
        skill_data = SKILL_FRAMEWORKS[skill_lower]
    
    context_lower = context.lower()
    if context_lower not in CONTEXTS:
        available = ", ".join(CONTEXTS.keys())
        warnings.append(f"Context '{context}' not predefined. Using general recommendations. Available: {available}")
        context_data = None
    else:
        context_data = CONTEXTS[context_lower]
    
    # Get developmental stage
    stage = get_developmental_stage(age)
    stage_data = DEVELOPMENTAL_STAGES[stage]
    
    # Build assessment
    assessment = {
        "learner_profile": {
            "age": age,
            "developmental_stage": stage,
            "cognitive_stage": stage_data["cognitive"],
            "optimal_attention_span": stage_data["attention_span"],
            "learning_style": stage_data["learning_style"]
        },
        "skill_target": {
            "skill": skill_data["name"] if skill_data else skill,
            "acquisition_stages": skill_data["stages"] if skill_data else ["Foundation", "Development", "Mastery"],
            "recommended_method": skill_data["methods"].get(stage, "See general principles") if skill_data else "Apply developmental stage principles",
            "practice_structure": skill_data["practice_structure"] if skill_data else "Distributed practice with feedback"
        },
        "context_analysis": {
            "context": context,
            "constraints": context_data["constraints"] if context_data else "Variable",
            "opportunities": context_data["opportunities"] if context_data else "Flexible approach",
            "recommendations": context_data["recommendations"] if context_data else ["Adapt to circumstances"]
        },
        "learning_plan": {
            "session_length": _calculate_session_length(age, time_per_day),
            "sessions_per_week": _calculate_frequency(time_per_day),
            "key_principles": stage_data["key_principles"],
            "spacing_schedule": _get_spacing_schedule(stage),
            "motivation_strategies": _get_motivation_strategies(stage, context_lower)
        },
        "risks_and_mitigations": _get_risks(stage, skill_lower, context_lower)
    }
    
    return Result(
        success=True,
        data=assessment,
        errors=errors,
        warnings=warnings
    )


def _calculate_session_length(age: int, time_available: int) -> str:
    """Calculate optimal session length based on age and available time."""
    stage = get_developmental_stage(age)
    max_lengths = {
        "early_childhood": 15,
        "childhood": 30,
        "adolescence": 45,
        "emerging_adult": 90,
        "adult": 60,
        "older_adult": 40
    }
    max_len = max_lengths.get(stage, 45)
    optimal = min(time_available, max_len)
    return f"{optimal} minutes (max effective: {max_len} min for this age)"


def _calculate_frequency(time_per_day: int) -> str:
    """Calculate recommended frequency."""
    if time_per_day >= 60:
        return "5-7 sessions/week (daily recommended)"
    elif time_per_day >= 30:
        return "4-6 sessions/week"
    else:
        return "Daily micro-sessions (spacing > duration)"


def _get_spacing_schedule(stage: str) -> List[str]:
    """Get appropriate spacing schedule for stage."""
    base = ["Day 1: Initial learning", "Day 2: First review", "Day 4: Second review", 
            "Day 7: Third review", "Day 14: Fourth review", "Day 30: Fifth review"]
    if stage in ["early_childhood", "childhood"]:
        return ["Daily practice with variation", "Review previous day's content each session"]
    return base


def _get_motivation_strategies(stage: str, context: str) -> List[str]:
    """Get motivation strategies appropriate for stage and context."""
    strategies = {
        "early_childhood": ["Praise effort and process", "Use play and stories", "Celebrate small wins"],
        "childhood": ["Gamification with care", "Progress visibility", "Peer collaboration"],
        "adolescence": ["Connect to identity and goals", "Provide autonomy", "Real-world relevance"],
        "emerging_adult": ["Clear skill pathways", "Mentorship connections", "Portfolio building"],
        "adult": ["Immediate application", "Time efficiency", "Visible ROI"],
        "older_adult": ["Social connection", "Celebrate progress", "Reduce anxiety"]
    }
    base = strategies.get(stage, ["Autonomy", "Competence", "Relatedness"])
    
    if context == "hobby":
        base.append("Maintain intrinsic enjoyment above all")
    elif context == "career_change":
        base.append("Track progress toward career goal")
    
    return base


def _get_risks(stage: str, skill: str, context: str) -> List[dict]:
    """Identify risks and mitigations."""
    risks = []
    
    # Stage-specific risks
    stage_risks = {
        "early_childhood": {"risk": "Forcing formal learning too early", "mitigation": "Keep it play-based and pressure-free"},
        "childhood": {"risk": "Comparison anxiety", "mitigation": "Focus on individual progress, growth mindset"},
        "adolescence": {"risk": "Disengagement if not relevant", "mitigation": "Connect to personal goals and identity"},
        "emerging_adult": {"risk": "Overconfidence or perfectionism", "mitigation": "Balanced challenge, embrace iteration"},
        "adult": {"risk": "Time constraints leading to abandonment", "mitigation": "Micro-learning, integrate into routine"},
        "older_adult": {"risk": "Confidence issues", "mitigation": "Celebrate progress, patient support"}
    }
    if stage in stage_risks:
        risks.append(stage_risks[stage])
    
    # Skill-specific risks
    if skill == "coding":
        risks.append({"risk": "Tutorial hell", "mitigation": "Build projects immediately"})
    elif skill in ["english", "language"]:
        risks.append({"risk": "Fear of speaking", "mitigation": "Low-stakes practice, focus on communication over perfection"})
    
    # Context-specific risks
    if context == "career_change":
        risks.append({"risk": "Burnout from pressure", "mitigation": "Sustainable pace, celebrate milestones"})
    
    return risks


def main():
    parser = argparse.ArgumentParser(description="Generate personalized learning assessment")
    parser.add_argument("--age", type=int, required=True, help="Learner age")
    parser.add_argument("--skill", type=str, required=True, help="Skill to learn (coding, english, math, music, language)")
    parser.add_argument("--context", type=str, default="hobby", help="Learning context (school, work, hobby, career_change)")
    parser.add_argument("--time", type=int, default=30, help="Available time per day in minutes")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    result = generate_assessment(args.age, args.skill, args.context, args.time)
    
    if args.json:
        print(json.dumps(asdict(result), indent=2))
    else:
        if not result.success:
            print("ASSESSMENT FAILED")
            for error in result.errors:
                print(f"  ERROR: {error}")
            sys.exit(1)
        
        print("=" * 60)
        print("LEARNER ASSESSMENT REPORT")
        print("=" * 60)
        
        data = result.data
        
        print("\n📋 LEARNER PROFILE")
        profile = data["learner_profile"]
        print(f"  Age: {profile['age']}")
        print(f"  Developmental Stage: {profile['developmental_stage']}")
        print(f"  Cognitive Stage: {profile['cognitive_stage']}")
        print(f"  Optimal Attention Span: {profile['optimal_attention_span']}")
        print(f"  Learning Style: {profile['learning_style']}")
        
        print("\n🎯 SKILL TARGET")
        skill_info = data["skill_target"]
        print(f"  Skill: {skill_info['skill']}")
        print(f"  Acquisition Stages: {' → '.join(skill_info['acquisition_stages'])}")
        print(f"  Recommended Method: {skill_info['recommended_method']}")
        print(f"  Practice Structure: {skill_info['practice_structure']}")
        
        print("\n🌍 CONTEXT ANALYSIS")
        ctx = data["context_analysis"]
        print(f"  Context: {ctx['context']}")
        print(f"  Constraints: {ctx['constraints']}")
        print(f"  Opportunities: {ctx['opportunities']}")
        
        print("\n📅 LEARNING PLAN")
        plan = data["learning_plan"]
        print(f"  Session Length: {plan['session_length']}")
        print(f"  Frequency: {plan['sessions_per_week']}")
        print("  Key Principles:")
        for p in plan["key_principles"]:
            print(f"    • {p}")
        
        print("\n⚠️ RISKS & MITIGATIONS")
        for risk in data["risks_and_mitigations"]:
            print(f"  Risk: {risk['risk']}")
            print(f"  Mitigation: {risk['mitigation']}")
            print()
        
        if result.warnings:
            print("\n⚡ WARNINGS")
            for w in result.warnings:
                print(f"  • {w}")
    
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
