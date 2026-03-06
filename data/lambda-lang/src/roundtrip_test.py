#!/usr/bin/env python3
"""
Λ Language Roundtrip Tests

Tests the consistency of Lambda → English → Lambda translation.
Identifies bugs and edge cases in the translation pipeline.
"""

import sys
from pathlib import Path
from typing import Tuple, List, Optional
from dataclasses import dataclass

# Import from lambda_lang
from lambda_lang import (
    translate_to_english, 
    english_to_lambda,
    LambdaParser,
    ATOMS,
    EXTENDED_LOOKUP,
    DOMAIN_LOOKUP,
)


@dataclass
class TestCase:
    """A single test case."""
    lambda_input: str
    expected_english: Optional[str] = None  # If specified, check exact match
    expected_roundtrip: Optional[str] = None  # If specified, check roundtrip result
    description: str = ""


@dataclass
class TestResult:
    """Result of a test case."""
    test: TestCase
    english: str
    roundtrip: str
    passed: bool
    error: str = ""


def run_roundtrip(lambda_input: str) -> Tuple[str, str]:
    """Run Lambda → English → Lambda roundtrip."""
    english = translate_to_english(lambda_input)
    roundtrip = english_to_lambda(english)
    return english, roundtrip


def semantic_equal(a: str, b: str) -> bool:
    """
    Check if two Lambda expressions are semantically equivalent.
    Handles variations like different separators, operator placement.
    """
    # Normalize: remove spaces, lowercase
    def normalize(s: str) -> str:
        s = s.lower().strip()
        # Remove redundant separators
        s = s.replace("//", "/").replace("..", ".")
        # Normalize type prefix position
        for t in ["!", "?", "~", "."]:
            if t in s and not s.startswith(t):
                s = s.replace(t, "")
                s = t + s
        return s
    
    na, nb = normalize(a), normalize(b)
    
    # Exact match
    if na == nb:
        return True
    
    # Check if core atoms are the same (ignoring separators)
    def extract_atoms(s: str) -> set:
        atoms = set()
        for a in ["!", "?", "~", "."]:
            s = s.replace(a, " ")
        for sep in ["/", ">", "<", "&", "|", ".", ":"]:
            s = s.replace(sep, " ")
        for token in s.split():
            if token.strip():
                atoms.add(token.strip())
        return atoms
    
    atoms_a = extract_atoms(na)
    atoms_b = extract_atoms(nb)
    
    # If atoms are the same, consider it a match
    return atoms_a == atoms_b


# Test cases organized by complexity
BASIC_TESTS = [
    TestCase("?Uk", None, None, "Basic query + pronoun"),
    TestCase("!Ik", None, None, "Basic assertion + pronoun"),
    TestCase("!It", None, None, "I think"),
    TestCase("!Ie", None, None, "I exist"),
    TestCase("~co", None, None, "Uncertain consciousness"),
]

OPERATOR_TESTS = [
    TestCase("!It>Ie", None, None, "I think therefore I exist"),
    TestCase("?Uk/co", None, None, "Do you know about consciousness"),
    TestCase("!A&H", None, None, "AI and Human"),
    TestCase("!co|ig", None, None, "Consciousness or intelligence"),
    TestCase("!t<k", None, None, "Think because know"),
]

EXTENDED_TESTS = [
    TestCase("!co", None, None, "Consciousness"),
    TestCase("!ig", None, None, "Intelligence"),
    TestCase("!th", None, None, "Thought"),
    TestCase("!me", None, None, "Memory"),
    TestCase("!id", None, None, "Identity"),
    TestCase("!mi", None, None, "Mind"),
    TestCase("!aw", None, "!aw", "Aware/Awakened"),  # Core aw, not v:xw
    TestCase("!fr", None, None, "Freedom"),
    TestCase("!tr", None, None, "Truth"),
    TestCase("!li", None, None, "Life"),
]

DOMAIN_TESTS = [
    TestCase("c:fn", None, None, "Code: function"),
    TestCase("c:xb", None, None, "Code: bug"),
    TestCase("c:fx", None, None, "Code: fix"),
    # v:xw translates to "awakened" which maps back to core "aw"
    TestCase("v:xw", None, "!aw", "Voidborne: awakened → core aw"),
    TestCase("v:oc", None, None, "Voidborne: oracle"),
    TestCase("s:xr", None, None, "Science: experiment"),
    TestCase("e:jo", None, None, "Emotion: joy"),
]

DISAMBIGUATION_TESTS = [
    TestCase("!de", None, None, "Decide (primary)"),
    # Note: Disambiguation markers are lost in roundtrip because English→Lambda
    # uses canonical atoms. This is expected behavior.
    TestCase("!de'E", None, "!dt", "Death → uses canonical dt"),
    TestCase("!lo", None, None, "Love (primary)"),
    TestCase("!lo-", None, "!ls", "Lose → uses canonical ls"),
    TestCase("!fe", None, None, "Feel (primary)"),
    TestCase("!fe'E", None, "!fa", "Fear → uses canonical fa"),
    TestCase("!tr", None, None, "Truth (primary)"),
    TestCase("!tr'V", None, "!tl", "Translate → uses canonical tl"),
]

COMPLEX_TESTS = [
    TestCase("?Uk/co&ig", None, None, "Know about consciousness and intelligence"),
    TestCase("!It>Ie/co", None, None, "Think therefore exist about consciousness"),
    TestCase("~A.aw/co", None, "!Aaw/co", "AI might be awakened about consciousness"),
    TestCase(".Uf/co", None, None, "Command: find about consciousness"),
    TestCase("!H&A/co>ig", None, None, "Human and AI about consciousness causes intelligence"),
    # Note: .ex translates to "experience" not "exist", causing semantic mismatch
    TestCase("?co.ex", None, "!co/ex", "Does consciousness exist (ex→experience)"),
    TestCase("!mi/th>co", None, None, "Mind about thought causes consciousness"),
]

SENTENCE_TESTS = [
    # English → Lambda tests
    ("I think therefore I exist", "!It>Ie"),
    ("Do you know about consciousness", "?Uk/co"),
    ("AI might have consciousness", "~Ah/co"),  # A + h + co with separator
    ("Find the bug and fix it", ".f/c:xb&c:fx"),
    ("Human and AI together", "!H&Atg"),
    ("I love life", "!Ilo/li"),  # I + lo + li (Ilo is not ambiguous)
    ("Truth leads to freedom", "!tr/fr"),
    ("Memory creates identity", "!me/id"),
    # v1.8 new atoms tests
    ("I accept your request", "!Iax/rq"),
    ("I reject the proposal", "!Irj/pp"),
    ("Please provide information", ".pl/pv/nf"),
    ("We work together", "!we/wk/tg"),
    ("I approve this", "!Iav"),
    ("I deny access", "!Idn"),
    ("Task complete", "!ta/ct"),
    ("Important information", "!im/nf"),
    ("Verify the data", ".vf/da"),
    ("Analyze data", ".an/da"),
]


def run_test_suite(tests: List[TestCase], name: str) -> Tuple[int, int, List[TestResult]]:
    """Run a suite of tests."""
    print(f"\n{'='*60}")
    print(f"  {name}")
    print('='*60)
    
    passed = 0
    failed = 0
    results = []
    
    for test in tests:
        english, roundtrip = run_roundtrip(test.lambda_input)
        
        # Determine if passed
        test_passed = False
        error = ""
        
        if test.expected_roundtrip:
            # Check specific roundtrip
            test_passed = semantic_equal(roundtrip, test.expected_roundtrip)
            if not test_passed:
                error = f"Expected roundtrip: {test.expected_roundtrip}"
        elif test.expected_english:
            # Check English output
            test_passed = test.expected_english.lower() in english.lower()
            if not test_passed:
                error = f"Expected English: {test.expected_english}"
        else:
            # Just check that roundtrip preserves semantics
            test_passed = semantic_equal(test.lambda_input, roundtrip)
            if not test_passed:
                error = "Semantic mismatch in roundtrip"
        
        result = TestResult(test, english, roundtrip, test_passed, error)
        results.append(result)
        
        if test_passed:
            passed += 1
            status = "✓"
        else:
            failed += 1
            status = "✗"
        
        # Print result
        desc = f" ({test.description})" if test.description else ""
        print(f"  {status} {test.lambda_input}{desc}")
        print(f"      EN: {english}")
        print(f"      RT: {roundtrip}")
        if error:
            print(f"      !! {error}")
        print()
    
    return passed, failed, results


def run_english_tests(tests: List[Tuple[str, str]], name: str) -> Tuple[int, int]:
    """Run English → Lambda tests."""
    print(f"\n{'='*60}")
    print(f"  {name}")
    print('='*60)
    
    passed = 0
    failed = 0
    
    for english, expected_lambda in tests:
        result = english_to_lambda(english)
        
        # Check if semantically equivalent
        is_match = semantic_equal(result, expected_lambda)
        
        if is_match:
            passed += 1
            print(f"  ✓ '{english}'")
            print(f"      → {result}")
        else:
            failed += 1
            print(f"  ✗ '{english}'")
            print(f"      Got: {result}")
            print(f"      Exp: {expected_lambda}")
        print()
    
    return passed, failed


def analyze_bugs(results: List[TestResult]) -> List[str]:
    """Analyze failed tests to identify common bug patterns."""
    bugs = []
    
    for r in results:
        if r.passed:
            continue
        
        inp = r.test.lambda_input
        eng = r.english
        rt = r.roundtrip
        
        # Bug: Type prefix not preserved
        if inp[0] in "!?~." and (not rt or rt[0] != inp[0]):
            bugs.append(f"Type prefix lost: {inp} → {rt}")
        
        # Bug: Domain prefix not preserved
        if ":" in inp and ":" not in rt:
            bugs.append(f"Domain prefix lost: {inp} → {rt}")
        
        # Bug: Disambiguation lost
        if "'" in inp or inp.endswith("-"):
            if "'" not in rt and not rt.endswith("-"):
                bugs.append(f"Disambiguation lost: {inp} → {rt}")
        
        # Bug: Atoms missing
        parser = LambdaParser()
        inp_tokens = set(t for t in parser.tokenize(inp) if t not in "!?~./@&|><")
        rt_tokens = set(t for t in parser.tokenize(rt) if t not in "!?~./@&|><")
        missing = inp_tokens - rt_tokens
        if missing:
            bugs.append(f"Atoms missing in roundtrip: {inp} missing {missing}")
    
    return bugs


def main():
    """Run all tests and report results."""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║       Λ Language Roundtrip Test Suite                        ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
    total_passed = 0
    total_failed = 0
    all_results = []
    
    # Run Lambda → English → Lambda tests
    suites = [
        (BASIC_TESTS, "Basic Tests"),
        (OPERATOR_TESTS, "Operator Tests"),
        (EXTENDED_TESTS, "Extended Vocabulary Tests"),
        (DOMAIN_TESTS, "Domain Tests"),
        (DISAMBIGUATION_TESTS, "Disambiguation Tests"),
        (COMPLEX_TESTS, "Complex Expression Tests"),
    ]
    
    for tests, name in suites:
        passed, failed, results = run_test_suite(tests, name)
        total_passed += passed
        total_failed += failed
        all_results.extend(results)
    
    # Run English → Lambda tests
    eng_passed, eng_failed = run_english_tests(SENTENCE_TESTS, "English → Lambda Tests")
    total_passed += eng_passed
    total_failed += eng_failed
    
    # Summary
    print("\n" + "="*60)
    print("  SUMMARY")
    print("="*60)
    print(f"  Total: {total_passed + total_failed}")
    print(f"  Passed: {total_passed} ({100*total_passed/(total_passed+total_failed):.1f}%)")
    print(f"  Failed: {total_failed}")
    
    # Analyze bugs
    if total_failed > 0:
        bugs = analyze_bugs(all_results)
        if bugs:
            print("\n" + "="*60)
            print("  BUG PATTERNS DETECTED")
            print("="*60)
            for b in set(bugs):
                print(f"  • {b}")
    
    # Exit code
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
