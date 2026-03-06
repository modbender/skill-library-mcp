#!/usr/bin/env python3
"""
Animal Crossing: New Horizons Turnip Price Predictor
Port of the exact algorithm from turnipprophet.io (ac-nh-turnip-prices)
Uses exhaustive enumeration of phase lengths with proper rate tracking.
"""

import json
import sys
import math
from typing import List, Optional, Dict, Any, Tuple

RATE_MULTIPLIER = 10000

def intceil(val: float) -> int:
    return int(val + 0.99999)

def get_price(rate: float, base: int) -> int:
    return intceil(rate * base / RATE_MULTIPLIER)

def min_rate_for_price(price: int, base: int) -> float:
    """Minimum rate that could produce this price via intceil"""
    return RATE_MULTIPLIER * (price - 0.99999) / base

def max_rate_for_price(price: int, base: int) -> float:
    """Maximum rate that could produce this price via intceil"""
    return RATE_MULTIPLIER * (price + 0.00001) / base

def rate_range_for_price(price: int, base: int) -> Tuple[float, float]:
    return (min_rate_for_price(price, base), max_rate_for_price(price, base))

def range_intersect(r1, r2):
    lo = max(r1[0], r2[0])
    hi = min(r1[1], r2[1])
    if lo > hi:
        return None
    return (lo, hi)

def range_length(r):
    return r[1] - r[0]


class PatternResult:
    """Result from evaluating one specific configuration of a pattern"""
    def __init__(self, pattern: int, probability: float, prices: list):
        self.pattern = pattern
        self.probability = probability
        self.prices = prices  # list of (min, max) tuples, length 12


def generate_individual_random_price(
    base: int, known: List[Optional[int]], 
    start: int, length: int,
    rate_min: float, rate_max: float
) -> Tuple[float, list]:
    """
    For periods where each price is independently random in [rate_min, rate_max].
    Returns (probability, [(min,max)...])
    """
    rm = rate_min * RATE_MULTIPLIER
    rx = rate_max * RATE_MULTIPLIER
    rate_range = (rm, rx)
    prob = 1.0
    prices = []
    
    for i in range(start, start + length):
        if i >= 12:
            break
        min_pred = get_price(rm, base)
        max_pred = get_price(rx, base)
        
        if known[i] is not None:
            if known[i] < min_pred or known[i] > max_pred:
                return (0.0, [])
            real_range = rate_range_for_price(known[i], base)
            isect = range_intersect(rate_range, real_range)
            if isect is None:
                return (0.0, [])
            prob *= range_length(isect) / range_length(rate_range)
            if prob <= 0:
                return (0.0, [])
            prices.append((known[i], known[i]))
        else:
            prices.append((min_pred, max_pred))
    
    return (prob, prices)


def generate_decreasing_random_price(
    base: int, known: List[Optional[int]],
    start: int, length: int,
    start_rate_min: float, start_rate_max: float,
    decay_min: float, decay_max: float
) -> Tuple[float, list]:
    """
    Decreasing phase: rate starts in [start_rate_min, start_rate_max],
    then each period rate -= uniform(decay_min, decay_max).
    
    Track the widest possible rate range (don't constrain on known prices,
    just check feasibility and compute probability).
    """
    # Current rate range (scaled) — tracks the UNCONSTRAINED envelope
    cur_min = start_rate_min * RATE_MULTIPLIER
    cur_max = start_rate_max * RATE_MULTIPLIER
    d_min = decay_min * RATE_MULTIPLIER
    d_max = decay_max * RATE_MULTIPLIER
    
    prob = 1.0
    prices = []
    
    for i in range(start, start + length):
        if i >= 12:
            break
            
        min_pred = get_price(cur_min, base)
        max_pred = get_price(cur_max, base)
        
        if known[i] is not None:
            if known[i] < min_pred or known[i] > max_pred:
                return (0.0, [])
            # Calculate probability but DON'T narrow the range
            real_range = rate_range_for_price(known[i], base)
            isect = range_intersect((cur_min, cur_max), real_range)
            if isect is None:
                return (0.0, [])
            cur_range_len = cur_max - cur_min
            if cur_range_len > 0:
                prob *= (isect[1] - isect[0]) / cur_range_len
            if prob <= 0:
                return (0.0, [])
            prices.append((known[i], known[i]))
        else:
            prices.append((min_pred, max_pred))
        
        # Apply decay for next period (always use full envelope)
        cur_min -= d_max  # Max decay = lowest next rate
        cur_max -= d_min  # Min decay = highest next rate
    
    return (prob, prices)


def generate_peak_price(
    base: int, known: List[Optional[int]],
    start: int, rate_min: float, rate_max: float
) -> Tuple[float, list]:
    """
    Pattern 3 peak trio:
      sellPrices[start]   = intceil(randfloat(rate_min, rate) * base) - 1
      sellPrices[start+1] = intceil(rate * base)
      sellPrices[start+2] = intceil(randfloat(rate_min, rate) * base) - 1
    where rate = randfloat(rate_min, rate_max)
    """
    rm = rate_min * RATE_MULTIPLIER
    rx = rate_max * RATE_MULTIPLIER
    prob = 1.0
    prices = []
    rate_range = (rm, rx)
    
    # Middle price (start+1) determines rate
    mid_idx = start + 1
    if mid_idx < 12 and known[mid_idx] is not None:
        mid_min = get_price(rm, base)
        mid_max = get_price(rx, base)
        if known[mid_idx] < mid_min or known[mid_idx] > mid_max:
            return (0.0, [])
        real_range = rate_range_for_price(known[mid_idx], base)
        isect = range_intersect(rate_range, real_range)
        if isect is None:
            return (0.0, [])
        prob *= range_length(isect) / range_length(rate_range)
        if prob <= 0:
            return (0.0, [])
        rate_range = isect
    
    # Left price (start): intceil(randfloat(rate_min, rate) * base) - 1
    left_idx = start
    if left_idx < 12:
        left_min = get_price(rm, base) - 1
        left_max = get_price(rate_range[1], base) - 1
        if known[left_idx] is not None:
            if known[left_idx] < left_min or known[left_idx] > left_max:
                return (0.0, [])
            # Simplified probability for edge prices
            total_range = left_max - left_min + 1
            if total_range > 0:
                prob *= 1.0 / total_range
            prices.append((known[left_idx], known[left_idx]))
        else:
            prices.append((left_min, left_max))
    
    # Middle price (start+1)
    if mid_idx < 12:
        mid_min = get_price(rate_range[0], base)
        mid_max = get_price(rate_range[1], base)
        if known[mid_idx] is not None:
            prices.append((known[mid_idx], known[mid_idx]))
        else:
            prices.append((mid_min, mid_max))
    
    # Right price (start+2): same as left
    right_idx = start + 2
    if right_idx < 12:
        right_min = get_price(rm, base) - 1
        right_max = get_price(rate_range[1], base) - 1
        if known[right_idx] is not None:
            if known[right_idx] < right_min or known[right_idx] > right_max:
                return (0.0, [])
            total_range = right_max - right_min + 1
            if total_range > 0:
                prob *= 1.0 / total_range
            prices.append((known[right_idx], known[right_idx]))
        else:
            prices.append((right_min, right_max))
    
    return (prob, prices)


# ── Pattern generators ──────────────────────────────────────────

def generate_pattern_0(base: int, known: List[Optional[int]]):
    """Pattern 0: Fluctuating - high, dec, high, dec, high
    decPhaseLen1 = 2 or 3; decPhaseLen2 = 5 - decPhaseLen1
    hiPhaseLen1 = 0..6; hiPhaseLen2and3 = 7 - hiPhaseLen1
    hiPhaseLen3 = 0..hiPhaseLen2and3-1
    """
    for dec1_len in (2, 3):
        dec2_len = 5 - dec1_len
        for hi1_len in range(0, 7):
            hi2and3 = 7 - hi1_len
            for hi3_len in range(0, hi2and3):
                hi2_len = hi2and3 - hi3_len
                
                # Weight: uniform over all valid combos
                weight = 1.0 / 2 / 7 / hi2and3
                
                prob = 1.0
                prices = []
                work = 0
                
                # High phase 1
                p, pr = generate_individual_random_price(base, known, work, hi1_len, 0.9, 1.4)
                if p == 0: continue
                prob *= p; prices.extend(pr); work += hi1_len
                
                # Dec phase 1
                p, pr = generate_decreasing_random_price(base, known, work, dec1_len, 0.6, 0.8, 0.04, 0.1)
                if p == 0: continue
                prob *= p; prices.extend(pr); work += dec1_len
                
                # High phase 2
                p, pr = generate_individual_random_price(base, known, work, hi2_len, 0.9, 1.4)
                if p == 0: continue
                prob *= p; prices.extend(pr); work += hi2_len
                
                # Dec phase 2
                p, pr = generate_decreasing_random_price(base, known, work, dec2_len, 0.6, 0.8, 0.04, 0.1)
                if p == 0: continue
                prob *= p; prices.extend(pr); work += dec2_len
                
                # High phase 3
                p, pr = generate_individual_random_price(base, known, work, hi3_len, 0.9, 1.4)
                if p == 0: continue
                prob *= p; prices.extend(pr); work += hi3_len
                
                assert work == 12, f"Pattern 0 work={work}"
                yield PatternResult(0, prob * weight, prices)


def generate_pattern_1(base: int, known: List[Optional[int]]):
    """Pattern 1: Large Spike
    Decreasing, then spike at peakStart (3..9 in sellPrices = 1..7 in our 0-index)
    peakStart in C++ is index into sellPrices[2..13], so offset by 2.
    In our 0-indexed prices array: peak at position (peakStart - 2).
    C++ peakStart range: 3..9 → our peak_start: 1..7
    """
    for peak_start in range(1, 8):  # positions 1-7 in 0-indexed prices
        weight = 1.0 / 7
        prob = 1.0
        prices = []
        work = 0
        
        # Decreasing phase: rate starts 0.85-0.9, decay 0.03-0.05
        p, pr = generate_decreasing_random_price(base, known, 0, peak_start, 0.85, 0.9, 0.03, 0.05)
        if p == 0: continue
        prob *= p; prices.extend(pr); work = peak_start
        
        # Spike: [0.9-1.4, 1.4-2.0, 2.0-6.0, 1.4-2.0, 0.9-1.4]
        spike_rates = [
            (0.9, 1.4),
            (1.4, 2.0),
            (2.0, 6.0),
            (1.4, 2.0),
            (0.9, 1.4),
        ]
        
        failed = False
        for rmin, rmax in spike_rates:
            if work >= 12:
                break
            p, pr = generate_individual_random_price(base, known, work, 1, rmin, rmax)
            if p == 0:
                failed = True
                break
            prob *= p; prices.extend(pr); work += 1
        
        if failed: continue
        
        # Random low tail: 0.4-0.9
        if work < 12:
            p, pr = generate_individual_random_price(base, known, work, 12 - work, 0.4, 0.9)
            if p == 0: continue
            prob *= p; prices.extend(pr)
        
        yield PatternResult(1, prob * weight, prices)


def generate_pattern_2(base: int, known: List[Optional[int]]):
    """Pattern 2: Consistently decreasing
    rate starts 0.85-0.9, decay 0.03-0.05 for all 12 periods
    """
    p, pr = generate_decreasing_random_price(base, known, 0, 12, 0.85, 0.9, 0.03, 0.05)
    if p > 0:
        yield PatternResult(2, p, pr)


def generate_pattern_3(base: int, known: List[Optional[int]]):
    """Pattern 3: Small Spike
    Decreasing, then spike at peakStart (2..9 in sellPrices = 0..7 in our array)
    Spike: [0.9-1.4, 0.9-1.4, peak_trio(1.4-2.0)], then decreasing
    """
    for peak_start in range(0, 8):  # 0-7 in our 0-indexed
        weight = 1.0 / 8
        prob = 1.0
        prices = []
        work = 0
        
        # Decreasing phase 1 (before peak): rate 0.4-0.9, decay 0.03-0.05
        if peak_start > 0:
            p, pr = generate_decreasing_random_price(base, known, 0, peak_start, 0.4, 0.9, 0.03, 0.05)
            if p == 0: continue
            prob *= p; prices.extend(pr)
        work = peak_start
        
        # Two random prices: 0.9-1.4x
        p, pr = generate_individual_random_price(base, known, work, min(2, 12 - work), 0.9, 1.4)
        if p == 0: continue
        prob *= p; prices.extend(pr); work += min(2, 12 - work)
        
        # Peak trio (1.4-2.0 rate)
        if work + 3 <= 12:
            p, pr = generate_peak_price(base, known, work, 1.4, 2.0)
            if p == 0: continue
            prob *= p; prices.extend(pr); work += 3
        
        # Decreasing phase 2 (after peak): rate 0.4-0.9, decay 0.03-0.05
        if work < 12:
            p, pr = generate_decreasing_random_price(base, known, work, 12 - work, 0.4, 0.9, 0.03, 0.05)
            if p == 0: continue
            prob *= p; prices.extend(pr)
        
        yield PatternResult(3, prob * weight, prices)


# ── Main predictor ──────────────────────────────────────────────

TRANSITION_MATRIX = {
    0: [0.20, 0.30, 0.15, 0.35],
    1: [0.50, 0.05, 0.20, 0.25],
    2: [0.25, 0.45, 0.05, 0.25],
    3: [0.45, 0.25, 0.15, 0.15],
}
STEADY_STATE = [4530/13082, 3236/13082, 1931/13082, 3385/13082]

PATTERN_NAMES = {0: "fluctuating", 1: "large_spike", 2: "decreasing", 3: "small_spike"}
PATTERN_DESC = {
    "fluctuating": "Random ups and downs",
    "large_spike": "Big spike (up to 6x buy price)",
    "decreasing": "Continuously decreasing",
    "small_spike": "Small spike (up to 2x buy price)",
}

GENERATORS = {
    0: generate_pattern_0,
    1: generate_pattern_1,
    2: generate_pattern_2,
    3: generate_pattern_3,
}


def predict(buy_price: int, known: List[Optional[int]], previous_pattern: Optional[int] = None):
    # Pad to 12
    known = (known + [None]*12)[:12]
    
    # Prior probabilities
    if previous_pattern is not None and previous_pattern in TRANSITION_MATRIX:
        prior = TRANSITION_MATRIX[previous_pattern]
    else:
        prior = STEADY_STATE
    
    # Collect all results per pattern
    pattern_results: Dict[int, list] = {0: [], 1: [], 2: [], 3: []}
    
    for pat in range(4):
        for result in GENERATORS[pat](buy_price, known):
            pattern_results[pat].append(result)
    
    # Sum probabilities per pattern (weighted by prior)
    pattern_total_prob = {}
    for pat in range(4):
        total = sum(r.probability for r in pattern_results[pat])
        pattern_total_prob[pat] = total * prior[pat]
    
    grand_total = sum(pattern_total_prob.values())
    
    # Normalised posterior probabilities
    if grand_total > 0:
        pattern_probs = {pat: pattern_total_prob[pat] / grand_total for pat in range(4)}
    else:
        pattern_probs = {pat: prior[pat] for pat in range(4)}
    
    # Aggregate min/max across all results, weighted
    predictions = []
    for period in range(12):
        if known[period] is not None:
            predictions.append({"min": known[period], "max": known[period], "patterns": [
                pat for pat in range(4) if pattern_probs[pat] > 0.001
            ]})
            continue
        
        period_min = None
        period_max = None
        contributing = []
        
        for pat in range(4):
            if pattern_probs[pat] < 0.001:
                continue
            for result in pattern_results[pat]:
                if period < len(result.prices):
                    lo, hi = result.prices[period]
                    if period_min is None:
                        period_min = lo
                        period_max = hi
                    else:
                        period_min = min(period_min, lo)
                        period_max = max(period_max, hi)
                    if pat not in contributing:
                        contributing.append(pat)
        
        predictions.append({
            "min": period_min or 0,
            "max": period_max or 0,
            "patterns": contributing,
        })
    
    # Recommendation
    best_pat = max(pattern_probs, key=pattern_probs.get)
    future_max = max((p["max"] for p in predictions if p["max"] > 0), default=0)
    
    if pattern_probs[best_pat] < 0.3:
        rec = "Uncertain pattern — monitor prices and sell when favourable"
    elif best_pat == 1:
        rec = f"Large spike likely! Peak could reach {future_max} bells — wait for it"
    elif best_pat == 2:
        rec = "Decreasing pattern — sell immediately to minimise losses"
    elif best_pat == 3:
        rec = f"Small spike pattern — sell near the peak (~{future_max} bells)"
    else:
        rec = "Fluctuating pattern — sell when prices exceed buy price"
    
    return {
        "pattern_probabilities": {PATTERN_NAMES[p]: round(pattern_probs[p], 6) for p in range(4)},
        "predictions": predictions,
        "recommended_action": rec,
        "pattern_descriptions": PATTERN_DESC,
    }


def main():
    try:
        data = json.load(sys.stdin)
        buy = data["buy_price"]
        prices = data.get("prices", [])
        prev = data.get("previous_pattern")
        
        if not (90 <= buy <= 110):
            raise ValueError("buy_price must be between 90 and 110")
        
        result = predict(buy, prices, prev)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e), "success": False}, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()
