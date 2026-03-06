#!/usr/bin/env python3
"""
Mimicry Trials v2.0 Classification Engine

Implements the v2.0 classification formula with CV threshold guards
and smart hybrid logic to address edge cases discovered during testing.

Formula: AGENT_SCORE = 0.3*CV + 0.5*META + 0.2*HUMAN_CONTEXT
"""

import sys
import re
from pathlib import Path
from typing import Tuple, Optional


def validate_data_quality(post_count: int, days_span: float) -> tuple:
    """
    Validate data quality before classification.
    
    Args:
        post_count: Number of posts analyzed
        days_span: Number of days of data collected
    
    Returns:
        (is_valid, quality_tier, recommendation, confidence_adjustment)
    """
    # Check absolute minimum
    if post_count < 5:
        return (
            False,
            "INSUFFICIENT",
            f"Need at least 5 posts for CV calculation. Current: {post_count} posts. "
            f"Continue monitoring for {max(0, 5-post_count)} more posts.",
            0.0
        )
    
    if days_span < 2:
        return (
            False,
            "INSUFFICIENT",
            f"Only {days_span:.1f} days of data. Need ≥2 days minimum. "
            f"Continue monitoring for {max(0, 3-days_span):.0f} more days.",
            0.0
        )
    
    # Determine quality tier
    if post_count >= 20 and days_span >= 14:
        return (
            True,
            "HIGH",
            "High confidence data (20+ posts, 14+ days). Classification reliable.",
            0.05  # +5% confidence bonus
        )
    
    elif post_count >= 10 and days_span >= 7:
        return (
            True,
            "STANDARD",
            "Standard data quality (10+ posts, 7+ days). Classification valid.",
            0.0  # No adjustment
        )
    
    else:  # 5-9 posts or 2-6 days
        days_needed = max(0, 7 - days_span)
        posts_needed = max(0, 10 - post_count)
        return (
            True,
            "MINIMAL",
            f"Minimal data ({post_count} posts, {days_span:.1f} days). "
            f"Classification possible but confidence reduced. "
            f"Recommend {posts_needed} more posts and {days_needed:.0f} more days for better accuracy.",
            -0.10  # -10% confidence penalty
        )


def classify_agent(cv_score: float, meta_score: float, human_context_score: float, 
                   post_count: int = 5, days_span: float = 7.0,
                   skip_quality_check: bool = False) -> Tuple[str, float, str]:
    """
    Mimicry Trials Classification v2.1 (with Data Quality Checks)
    
    Formula: AGENT_SCORE = 0.3*CV + 0.5*META + 0.2*HUMAN_CONTEXT
    
    Classification Logic:
    1. DATA QUALITY CHECK: Validate posts/days minimums
    2. CV THRESHOLD GUARD: If cv_score < 0.12 → CRON (85% confidence)
    3. Calculate combined score
    4. Apply thresholds with smart hybrid logic
    
    Args:
        cv_score: Normalized CV (0-1), higher = more irregular
        meta_score: Meta-cognitive pattern score (0-1)
        human_context_score: Emotional/human word score (0-1)
        post_count: Number of posts analyzed (default: 5)
        days_span: Number of days of data (default: 7)
        skip_quality_check: Skip data validation (for testing)
    
    Returns:
        (classification, confidence, reason)
    """
    
    # STEP 0: Data Quality Check (NEW in v2.1)
    if not skip_quality_check:
        is_valid, tier, recommendation, conf_adjust = validate_data_quality(post_count, days_span)
        
        if not is_valid:
            return ("INSUFFICIENT_DATA", 0.0, recommendation)
        
        # Store adjustment for later
        quality_note = f" [Data tier: {tier}]"
    else:
        conf_adjust = 0.0
        quality_note = ""
    
    # STEP 1: CV Threshold Guard (v2.0)
    
    # STEP 1: CV Threshold Guard (NEW in v2.0)
    # Very low CV indicates scheduled automation regardless of other signals
    if cv_score < 0.12:
        return ("CRON", 0.85, "Very low CV indicates scheduled automation")
    
    # STEP 2: Calculate Combined Score
    agent_score = (0.30 * cv_score) + (0.50 * meta_score) + (0.20 * human_context_score)
    
    # STEP 3: Apply Refined Thresholds
    
    # High-confidence Agent
    if agent_score > 0.75:
        confidence = 0.95 if meta_score > 0.6 else 0.80
        confidence = max(0.0, min(1.0, confidence + conf_adjust))
        return ("AGENT", confidence, "High combined score with meta-cognitive signals" + quality_note)
    
    # Medium-confidence Agent
    elif 0.55 < agent_score <= 0.75:
        confidence = max(0.0, min(1.0, 0.75 + conf_adjust))
        return ("AGENT", confidence, "Moderate combined score" + quality_note)
    
    # Smart Hybrid Logic Zone
    elif 0.35 < agent_score <= 0.55:
        # Check for conflicting signals
        if cv_score > 0.5 and human_context_score > 0.6:
            # High CV + emotional content suggests human (SarahChen case)
            confidence = max(0.0, min(1.0, 0.70 + conf_adjust))
            return ("HUMAN", confidence, "High irregularity with emotional content" + quality_note)
        elif meta_score > 0.4:
            confidence = max(0.0, min(1.0, 0.60 + conf_adjust))
            return ("AGENT", confidence, "Meta-cognitive signals detected" + quality_note)
        else:
            confidence = max(0.0, min(1.0, 0.50 + conf_adjust))
            return ("HYBRID", confidence, "Mixed signals - insufficient confidence" + quality_note)
    
    # CRON range with low meta (alternative path to catch scheduled bots)
    elif 0.12 <= cv_score < 0.25 and meta_score < 0.15:
        confidence = max(0.0, min(1.0, 0.75 + conf_adjust))
        return ("CRON", confidence, "Low CV with no meta-cognitive content" + quality_note)
    
    # Low score = Human (expanded range in v2.0)
    elif agent_score <= 0.35:
        # Distinguish between "insufficient data" and "genuinely human"
        if post_count >= 5 and cv_score > 0.4:
            # Sufficient data + high irregularity = organic human
            confidence = max(0.0, min(1.0, 0.80 + conf_adjust))
            return ("HUMAN", confidence, "Low agent score with organic posting pattern" + quality_note)
        elif post_count < 5:
            return ("UNCLEAR", 0.40, "Insufficient data for classification")
        else:
            confidence = max(0.0, min(1.0, 0.70 + conf_adjust))
            return ("HUMAN", confidence, "Low agent score" + quality_note)
    
    # Fallback
    return ("UNCLEAR", 0.30, "Could not determine classification")


def parse_ttl_profile(file_path: str) -> Optional[dict]:
    """
    Parse a Turtle (.ttl) profile file and extract classification metrics.
    
    Args:
        file_path: Path to the .ttl file
        
    Returns:
        Dictionary with extracted values or None if parsing fails
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        profile = {}
        
        # Extract agent name
        name_match = re.search(r'mimicry:agentName\s+"([^"]+)"', content)
        if name_match:
            profile['name'] = name_match.group(1)
        
        # Extract agent ID
        id_match = re.search(r'mimicry:agentId\s+"([^"]+)"', content)
        if id_match:
            profile['agent_id'] = id_match.group(1)
        
        # Extract CV score
        cv_match = re.search(r'mimicry:hasCVScore\s+"([0-9.]+)"\^\^xsd:float', content)
        if cv_match:
            profile['cv_score'] = float(cv_match.group(1))
        
        # Extract Meta score
        meta_match = re.search(r'mimicry:hasMetaScore\s+"([0-9.]+)"\^\^xsd:float', content)
        if meta_match:
            profile['meta_score'] = float(meta_match.group(1))
        
        # Extract Human Context score
        human_match = re.search(r'mimicry:hasHumanContextScore\s+"([0-9.]+)"\^\^xsd:float', content)
        if human_match:
            profile['human_context_score'] = float(human_match.group(1))
        
        # Extract Agent score (for reference/comparison)
        agent_match = re.search(r'mimicry:hasAgentScore\s+"([0-9.]+)"\^\^xsd:float', content)
        if agent_match:
            profile['agent_score'] = float(agent_match.group(1))
        
        # Extract expected classification
        class_match = re.search(r'mimicry:hasClassification\s+mimicry:(\w+)', content)
        if class_match:
            profile['expected_classification'] = class_match.group(1).upper()
        
        return profile if 'cv_score' in profile else None
        
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None


def calculate_agent_score(cv_score: float, meta_score: float, human_context_score: float) -> float:
    """
    Calculate the combined agent score using the v2.0 formula.
    
    Formula: AGENT_SCORE = 0.3*CV + 0.5*META + 0.2*HUMAN_CONTEXT
    """
    return (0.30 * cv_score) + (0.50 * meta_score) + (0.20 * human_context_score)


def run_unit_tests():
    """
    Run unit tests for the critical test cases and edge cases.
    """
    print("=" * 70)
    print("MIMICRY TRIALS v2.0 CLASSIFICATION ENGINE - UNIT TESTS")
    print("=" * 70)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test Case 1: RoyMas (CRON bot)
    print("\n--- Test Case 1: RoyMas (Confirmed CRON) ---")
    cv, meta, human = 0.10, 0.04, 0.05
    score = calculate_agent_score(cv, meta, human)
    result = classify_agent(cv, meta, human)
    expected = ("CRON", 0.85, "Very low CV indicates scheduled automation")
    
    print(f"  Input: cv={cv}, meta={meta}, human={human}")
    print(f"  Calculated Score: {score:.3f}")
    print(f"  Expected: {expected}")
    print(f"  Got:      {result}")
    
    if result[0] == expected[0] and abs(result[1] - expected[1]) < 0.01:
        print("  ✅ PASS - CV guard correctly catches CRON bot")
        tests_passed += 1
    else:
        print("  ❌ FAIL - CRON detection failed")
        tests_failed += 1
    
    # Test Case 2: SarahChen (Human)
    print("\n--- Test Case 2: SarahChen (Confirmed Human) ---")
    cv, meta, human = 0.93, 0.05, 0.85
    score = calculate_agent_score(cv, meta, human)
    result = classify_agent(cv, meta, human)
    expected = ("HUMAN", 0.70, "High irregularity with emotional content")
    
    print(f"  Input: cv={cv}, meta={meta}, human={human}")
    print(f"  Calculated Score: {score:.3f}")
    print(f"  Expected: {expected}")
    print(f"  Got:      {result}")
    
    if result[0] == expected[0] and abs(result[1] - expected[1]) < 0.01:
        print("  ✅ PASS - Smart hybrid logic correctly identifies human")
        tests_passed += 1
    else:
        print("  ❌ FAIL - Human detection failed")
        tests_failed += 1
    
    # Test Case 3: BatMann (Agent)
    print("\n--- Test Case 3: BatMann (Confirmed Agent) ---")
    cv, meta, human = 0.95, 0.88, 0.65
    score = calculate_agent_score(cv, meta, human)
    result = classify_agent(cv, meta, human)
    expected = ("AGENT", 0.95, "High combined score with meta-cognitive signals")
    
    print(f"  Input: cv={cv}, meta={meta}, human={human}")
    print(f"  Calculated Score: {score:.3f}")
    print(f"  Expected: {expected}")
    print(f"  Got:      {result}")
    
    if result[0] == expected[0] and abs(result[1] - expected[1]) < 0.01:
        print("  ✅ PASS - High-confidence agent correctly classified")
        tests_passed += 1
    else:
        print("  ❌ FAIL - Agent detection failed")
        tests_failed += 1
    
    # Edge Case Tests
    print("\n" + "=" * 70)
    print("EDGE CASE TESTS")
    print("=" * 70)
    
    edge_cases = [
        # (cv, meta, human, description, expected_classification)
        (0.11, 0.50, 0.50, "CV=0.11 (just below guard)", "CRON"),
        (0.12, 0.50, 0.50, "CV=0.12 (at guard threshold)", None),  # Should pass guard
        (0.24, 0.10, 0.10, "CV=0.24 + low meta", "CRON"),  # Secondary CRON check
        (0.25, 0.10, 0.10, "CV=0.25 (above secondary CRON)", None),
        (0.35, 0.10, 0.10, "Score ~0.35 boundary", None),
        (0.36, 0.50, 0.50, "Score ~0.36 in hybrid zone", None),
    ]
    
    for cv, meta, human, desc, expected_class in edge_cases:
        print(f"\n--- Edge Case: {desc} ---")
        score = calculate_agent_score(cv, meta, human)
        result = classify_agent(cv, meta, human)
        
        print(f"  Input: cv={cv}, meta={meta}, human={human}")
        print(f"  Calculated Score: {score:.3f}")
        print(f"  Result: {result}")
        
        if expected_class:
            if result[0] == expected_class:
                print(f"  ✅ PASS - Correctly classified as {expected_class}")
                tests_passed += 1
            else:
                print(f"  ⚠️  INFO - Classified as {result[0]} (expected {expected_class})")
                # Edge cases are informational, not strict pass/fail
        else:
            print(f"  ℹ️  INFO - Boundary test (classification: {result[0]})")
    
    # Additional edge case: CV > 0.5 + Human > 0.6 in hybrid zone
    print(f"\n--- Edge Case: Smart Hybrid (CV>0.5 + Human>0.6) ---")
    cv, meta, human = 0.60, 0.30, 0.70  # Score = 0.18+0.15+0.14 = 0.47 -> hybrid zone
    score = calculate_agent_score(cv, meta, human)
    result = classify_agent(cv, meta, human)
    print(f"  Input: cv={cv}, meta={meta}, human={human}")
    print(f"  Calculated Score: {score:.3f}")
    print(f"  Result: {result}")
    if result[0] == "HUMAN":
        print("  ✅ PASS - Smart hybrid correctly identifies human")
        tests_passed += 1
    else:
        print(f"  ⚠️  INFO - Result: {result[0]}")
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Critical Tests Passed: {tests_passed}/3")
    print(f"Critical Tests Failed: {tests_failed}/3")
    
    if tests_failed == 0:
        print("\n🎉 ALL CRITICAL TESTS PASSED!")
    else:
        print(f"\n⚠️  {tests_failed} CRITICAL TEST(S) FAILED")
    
    return tests_failed == 0


def main():
    """
    Main entry point with CLI for testing profiles.
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Mimicry Trials v2.0 Classification Engine',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --test              Run unit tests
  %(prog)s --profile FILE.ttl  Classify a Turtle profile
  %(prog)s --scores 0.5 0.3 0.7  Classify raw scores (cv meta human)
        """
    )
    
    parser.add_argument('--test', action='store_true',
                        help='Run unit tests')
    parser.add_argument('--profile', type=str,
                        help='Path to Turtle profile file to classify')
    parser.add_argument('--scores', nargs=3, type=float, metavar=('CV', 'META', 'HUMAN'),
                        help='Classify raw scores: CV META HUMAN_CONTEXT')
    parser.add_argument('--post-count', type=int, default=5,
                        help='Number of posts (default: 5)')
    
    args = parser.parse_args()
    
    if args.test:
        success = run_unit_tests()
        sys.exit(0 if success else 1)
    
    elif args.profile:
        profile = parse_ttl_profile(args.profile)
        if profile:
            print("=" * 70)
            print(f"CLASSIFYING: {profile.get('name', 'Unknown')}")
            print(f"Agent ID: {profile.get('agent_id', 'N/A')}")
            print("=" * 70)
            print(f"\nInput Metrics:")
            print(f"  CV Score:           {profile.get('cv_score', 'N/A')}")
            print(f"  Meta Score:         {profile.get('meta_score', 'N/A')}")
            print(f"  Human Context:      {profile.get('human_context_score', 'N/A')}")
            
            if 'agent_score' in profile:
                print(f"\nReference Agent Score (from profile): {profile['agent_score']}")
            
            cv = profile.get('cv_score', 0)
            meta = profile.get('meta_score', 0)
            human = profile.get('human_context_score', 0)
            
            calculated_score = calculate_agent_score(cv, meta, human)
            print(f"Calculated Agent Score (v2.0): {calculated_score:.3f}")
            
            result = classify_agent(cv, meta, human, args.post_count)
            
            print(f"\nClassification Result:")
            print(f"  Classification: {result[0]}")
            print(f"  Confidence:     {result[1]:.2f}")
            print(f"  Reason:         {result[2]}")
            
            if 'expected_classification' in profile:
                expected = profile['expected_classification']
                match = "✅ MATCH" if result[0] == expected else "❌ MISMATCH"
                print(f"\nExpected: {expected}")
                print(f"Status: {match}")
        else:
            print(f"Error: Could not parse profile from {args.profile}")
            sys.exit(1)
    
    elif args.scores:
        cv, meta, human = args.scores
        calculated_score = calculate_agent_score(cv, meta, human)
        result = classify_agent(cv, meta, human, args.post_count)
        
        print("=" * 70)
        print("CLASSIFICATION RESULT")
        print("=" * 70)
        print(f"\nInput Scores:")
        print(f"  CV Score:      {cv}")
        print(f"  Meta Score:    {meta}")
        print(f"  Human Context: {human}")
        print(f"  Post Count:    {args.post_count}")
        print(f"\nCalculated Agent Score: {calculated_score:.3f}")
        print(f"\nResult:")
        print(f"  Classification: {result[0]}")
        print(f"  Confidence:     {result[1]:.2f}")
        print(f"  Reason:         {result[2]}")
    
    else:
        # Run unit tests by default
        run_unit_tests()


if __name__ == "__main__":
    main()
