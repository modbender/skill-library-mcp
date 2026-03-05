#!/usr/bin/env python3
"""Unit tests for memory-bench IR metrics and utilities."""
import sys
import math
from pathlib import Path

# Import from rate.py
sys.path.insert(0, str(Path(__file__).parent))
from rate import (
    dcg, ndcg, average_precision, precision_at_k, hit_rate,
    compute_rar, compute_mrr, bootstrap_ci, load_test_set
)


def test_dcg():
    """DCG with known values: ratings [5, 4, 3, 2, 1]."""
    ratings = [5, 4, 3, 2, 1]
    # DCG = (2^5-1)/log2(2) + (2^4-1)/log2(3) + (2^3-1)/log2(4) + (2^2-1)/log2(5) + (2^1-1)/log2(6)
    #     = 31/1 + 15/1.585 + 7/2 + 3/2.322 + 1/2.585
    expected = 31.0 + 15/math.log2(3) + 7/math.log2(4) + 3/math.log2(5) + 1/math.log2(6)
    assert abs(dcg(ratings, 5) - expected) < 0.01, f"DCG mismatch: {dcg(ratings, 5)} != {expected}"

def test_ndcg_perfect():
    """nDCG of a perfectly sorted list should be 1.0."""
    assert ndcg([5, 4, 3, 2, 1]) == 1.0

def test_ndcg_reversed():
    """nDCG of a reversed list should be < 1.0."""
    score = ndcg([1, 2, 3, 4, 5])
    assert 0 < score < 1.0, f"Reversed nDCG should be < 1.0, got {score}"

def test_ndcg_empty():
    """nDCG of empty list should be 0."""
    assert ndcg([]) == 0.0

def test_average_precision():
    """MAP with known relevant positions."""
    # Relevant at positions 1, 3, 5 (0-indexed: 0, 2, 4)
    ratings = [4, 1, 4, 1, 4]  # threshold=3
    # AP = (1/1 + 2/3 + 3/5) / 5 = (1 + 0.667 + 0.6) / 5 = 0.4533
    ap = average_precision(ratings, k=5, threshold=3)
    assert abs(ap - 0.4533) < 0.01, f"AP mismatch: {ap}"

def test_precision_at_k():
    """P@5 with 3 relevant out of 5."""
    ratings = [5, 1, 4, 1, 3]
    assert precision_at_k(ratings, k=5, threshold=3) == 0.6

def test_hit_rate():
    """Hit rate: 1 if any result is relevant."""
    assert hit_rate([1, 1, 1, 1, 1]) == 0.0
    assert hit_rate([1, 1, 3, 1, 1]) == 1.0
    assert hit_rate([]) == 0.0

def test_rar():
    """RAR: fraction above threshold."""
    assert compute_rar([5, 4, 3, 2, 1]) == 0.6
    assert compute_rar([]) == 0.0

def test_mrr():
    """MRR: reciprocal rank of first relevant."""
    assert compute_mrr([1, 1, 4, 1, 1]) == 1/3
    assert compute_mrr([5, 1, 1, 1, 1]) == 1.0
    assert compute_mrr([1, 1, 1, 1, 1]) == 0.0

def test_bootstrap_ci():
    """Bootstrap CI should produce reasonable bounds."""
    values = [0.5] * 20
    ci = bootstrap_ci(values)
    assert ci["mean"] == 0.5
    assert ci["ci_low"] == 0.5
    assert ci["ci_high"] == 0.5

    # With variance
    values = [0.0, 1.0] * 15
    ci = bootstrap_ci(values)
    assert 0.3 < ci["mean"] < 0.7
    assert ci["ci_low"] < ci["ci_high"]

def test_test_set_format():
    """Standard test set should have required fields."""
    queries = load_test_set()
    assert len(queries) == 30, f"Expected 30 queries, got {len(queries)}"
    categories = {"semantic", "episodic", "procedural", "strategic"}
    difficulties = {"easy", "medium", "hard"}
    for q in queries:
        assert "id" in q, f"Missing id in query"
        assert "query" in q, f"Missing query text"
        assert q.get("category") in categories, f"Bad category: {q.get('category')}"
        assert q.get("difficulty") in difficulties, f"Bad difficulty: {q.get('difficulty')}"
    # Check stratification
    cats = {c: sum(1 for q in queries if q["category"] == c) for c in categories}
    for c, n in cats.items():
        assert n >= 5, f"Category {c} has only {n} queries (need ≥5)"


if __name__ == "__main__":
    tests = [f for f in dir() if f.startswith("test_")]
    passed = 0
    failed = 0
    for t in sorted(tests):
        try:
            globals()[t]()
            print(f"  ✅ {t}")
            passed += 1
        except AssertionError as e:
            print(f"  ❌ {t}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ❌ {t}: {type(e).__name__}: {e}")
            failed += 1
    print(f"\n{'✅' if failed == 0 else '❌'} {passed}/{passed+failed} tests passed")
    sys.exit(1 if failed else 0)
