#!/usr/bin/env python3
"""
BlackSnow Test Runner
Demonstrates the ambient risk detection pipeline with live data.
"""

import json
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import random

# ============================================================================
# ONTOLOGY
# ============================================================================

ONTOLOGY = {
    "infra.energy.grid": ["grid", "power", "electricity", "outage", "transmission", "utility", "blackout"],
    "infra.energy.oil": ["oil", "petroleum", "crude", "refinery", "pipeline", "fuel", "gas"],
    "infra.transport.rail": ["rail", "railway", "train", "freight", "locomotive", "amtrak"],
    "infra.transport.port": ["port", "shipping", "container", "maritime", "dock", "cargo", "vessel"],
    "infra.transport.aviation": ["airport", "aviation", "flight", "airline", "faa", "aircraft"],
    "infra.transport.road": ["highway", "bridge", "road", "traffic", "trucking", "dot"],
    "labor.union": ["union", "strike", "grievance", "collective", "bargaining", "nlrb", "workers"],
    "labor.attrition": ["resignation", "attrition", "turnover", "layoff", "departure", "fired", "quit"],
    "legal.regulation": ["regulation", "compliance", "draft", "consultation", "amendment", "rule", "policy"],
    "supply.procurement": ["tender", "procurement", "contract", "bid", "rfp", "award", "solicitation"],
    "supply.inventory": ["inventory", "stockpile", "shortage", "buffer", "warehouse", "supply chain"],
    "emergency.disaster": ["disaster", "emergency", "storm", "hurricane", "tornado", "flood", "fire", "wildfire", "earthquake", "tsunami", "fema", "evacuation", "shelter"],
    "emergency.weather": ["winter storm", "blizzard", "ice storm", "severe weather", "heat wave", "drought", "snow", "freeze"],
    "emergency.public_health": ["pandemic", "outbreak", "epidemic", "quarantine", "public health", "cdc", "contamination"],
    "finance.credit": ["credit", "default", "bankruptcy", "debt", "loan", "mortgage", "foreclosure"],
    "finance.market": ["market", "stock", "trading", "volatility", "crash", "recession", "inflation"],
}

SIGNAL_TYPES = {
    "deferral": 0.6,
    "acceleration": 0.8,
    "substitution": 0.5,
    "language_shift": 0.7,
    "attrition_spike": 0.9,
    "grievance_surge": 0.6,
    "inventory_buffer": 0.5,
    "disaster_declaration": 0.95,
    "emergency_response": 0.85,
    "weather_event": 0.75,
}

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class RawSignal:
    source_id: str
    domain: str
    raw_text: str
    timestamp: str
    confidence: float

@dataclass
class NormalizedSignal:
    normalized_id: str
    ontology_path: str
    signal_type: str
    magnitude: float
    temporal_marker: str
    source_refs: List[str]

@dataclass
class RiskPrimitive:
    risk_vector: str
    signal_confidence: float
    time_horizon_days: str
    contributing_domains: List[str]
    likely_outcomes: List[str]
    tradability: Dict[str, bool]

# ============================================================================
# AGENTS
# ============================================================================

class Harvester:
    """Collects data from approved sources."""
    
    def __init__(self):
        self.sources = []
    
    def ingest_mock_data(self) -> List[RawSignal]:
        """Generate mock signals for demonstration."""
        mock_signals = [
            RawSignal(
                source_id="sam.gov:tender:2026-02-06:78432",
                domain="procurement.federal",
                raw_text="Emergency maintenance contract for Northeast grid infrastructure. Expedited timeline requested due to deferred Q4 maintenance backlog.",
                timestamp=datetime.utcnow().isoformat() + "Z",
                confidence=0.92
            ),
            RawSignal(
                source_id="nlrb:filing:2026-02-05:grievance-1847",
                domain="labor.filings",
                raw_text="Collective bargaining unit files grievance regarding mandatory overtime and safety protocol changes at power generation facility.",
                timestamp=(datetime.utcnow() - timedelta(days=1)).isoformat() + "Z",
                confidence=0.88
            ),
            RawSignal(
                source_id="fedreg:draft:2026-02-04:energy-grid-resilience",
                domain="regulatory.draft",
                raw_text="Extended consultation period for grid resilience standards. Third extension granted due to stakeholder concerns.",
                timestamp=(datetime.utcnow() - timedelta(days=2)).isoformat() + "Z",
                confidence=0.85
            ),
            RawSignal(
                source_id="sec:8k:2026-02-03:utility-corp",
                domain="corporate.filings",
                raw_text="Chief Operations Officer resignation effective immediately. Interim leadership appointed pending permanent replacement.",
                timestamp=(datetime.utcnow() - timedelta(days=3)).isoformat() + "Z",
                confidence=0.95
            ),
        ]
        return mock_signals


class Normalizer:
    """Maps raw signals to unified ontology."""
    
    def normalize(self, signals: List[RawSignal]) -> List[NormalizedSignal]:
        normalized = []
        for sig in signals:
            # Detect ontology path
            ontology_path = self._detect_ontology(sig.raw_text)
            signal_type = self._detect_signal_type(sig.raw_text)
            
            norm = NormalizedSignal(
                normalized_id=hashlib.md5(sig.source_id.encode()).hexdigest()[:12],
                ontology_path=ontology_path,
                signal_type=signal_type,
                magnitude=SIGNAL_TYPES.get(signal_type, 0.5) * sig.confidence,
                temporal_marker="2026-Q1",
                source_refs=[sig.source_id]
            )
            normalized.append(norm)
        return normalized
    
    def _detect_ontology(self, text: str) -> str:
        text_lower = text.lower()
        scores = {}
        for path, keywords in ONTOLOGY.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[path] = score
        if scores:
            return max(scores, key=scores.get)
        return "unknown"
    
    def _detect_signal_type(self, text: str) -> str:
        text_lower = text.lower()
        if any(w in text_lower for w in ["defer", "backlog", "delayed", "postpone"]):
            return "deferral"
        if any(w in text_lower for w in ["expedite", "emergency", "urgent", "immediate"]):
            return "acceleration"
        if any(w in text_lower for w in ["grievance", "complaint", "dispute"]):
            return "grievance_surge"
        if any(w in text_lower for w in ["resign", "departure", "exit", "leave"]):
            return "attrition_spike"
        if any(w in text_lower for w in ["extension", "consultation", "draft"]):
            return "language_shift"
        if any(w in text_lower for w in ["disaster", "fema", "declaration", "declared"]):
            return "disaster_declaration"
        if any(w in text_lower for w in ["storm", "hurricane", "tornado", "flood", "blizzard", "ice storm", "winter storm"]):
            return "weather_event"
        if any(w in text_lower for w in ["evacuation", "shelter", "rescue", "response"]):
            return "emergency_response"
        return "unknown"


class Accumulator:
    """Bayesian evidence accumulation."""
    
    def __init__(self):
        self.belief_states = {}
    
    def accumulate(self, signals: List[NormalizedSignal]) -> Dict[str, float]:
        for sig in signals:
            vector = sig.ontology_path
            if vector not in self.belief_states:
                self.belief_states[vector] = 0.0
            # Simple Bayesian update (simplified)
            prior = self.belief_states[vector]
            likelihood = sig.magnitude
            posterior = prior + likelihood * (1 - prior)
            self.belief_states[vector] = min(posterior, 0.99)
        return self.belief_states


class Forecaster:
    """Horizon modeling and outcome prediction."""
    
    def forecast(self, belief_states: Dict[str, float]) -> List[Dict]:
        forecasts = []
        for vector, confidence in belief_states.items():
            if confidence > 0.3:
                outcomes = self._generate_outcomes(vector, confidence)
                horizon = self._estimate_horizon(confidence)
                forecasts.append({
                    "risk_vector": vector,
                    "confidence": round(confidence, 2),
                    "time_horizon_days": horizon,
                    "outcomes": outcomes
                })
        return forecasts
    
    def _generate_outcomes(self, vector: str, confidence: float) -> List[Dict]:
        outcome_templates = {
            "infra.energy.grid": [
                {"event": "localized_outage", "base_prob": 0.4},
                {"event": "price_volatility", "base_prob": 0.3},
                {"event": "policy_intervention", "base_prob": 0.2},
            ],
            "labor.union": [
                {"event": "work_slowdown", "base_prob": 0.5},
                {"event": "strike_action", "base_prob": 0.3},
                {"event": "contract_renegotiation", "base_prob": 0.4},
            ],
            "emergency.disaster": [
                {"event": "infrastructure_damage", "base_prob": 0.6},
                {"event": "supply_chain_disruption", "base_prob": 0.5},
                {"event": "insurance_claims_surge", "base_prob": 0.7},
                {"event": "federal_aid_deployment", "base_prob": 0.4},
            ],
            "emergency.weather": [
                {"event": "travel_disruption", "base_prob": 0.6},
                {"event": "power_outage", "base_prob": 0.5},
                {"event": "commodity_price_spike", "base_prob": 0.4},
            ],
            "infra.transport.port": [
                {"event": "shipping_delays", "base_prob": 0.5},
                {"event": "cargo_rerouting", "base_prob": 0.4},
                {"event": "supply_shortage", "base_prob": 0.3},
            ],
            "infra.transport.rail": [
                {"event": "freight_delays", "base_prob": 0.5},
                {"event": "service_disruption", "base_prob": 0.4},
            ],
        }
        templates = outcome_templates.get(vector, [{"event": "disruption", "base_prob": 0.3}])
        return [
            {"event": o["event"], "probability": round(o["base_prob"] * confidence, 2)}
            for o in templates
        ]
    
    def _estimate_horizon(self, confidence: float) -> str:
        if confidence > 0.8:
            return "7-14"
        elif confidence > 0.6:
            return "14-30"
        elif confidence > 0.4:
            return "30-60"
        else:
            return "60-90"


class Packager:
    """Converts to sellable primitives."""
    
    def package(self, forecasts: List[Dict], normalized: List[NormalizedSignal]) -> List[RiskPrimitive]:
        primitives = []
        for fc in forecasts:
            # Find contributing domains
            domains = set()
            for sig in normalized:
                if sig.ontology_path == fc["risk_vector"]:
                    domains.add(sig.signal_type)
            
            primitive = RiskPrimitive(
                risk_vector=fc["risk_vector"],
                signal_confidence=fc["confidence"],
                time_horizon_days=fc["time_horizon_days"],
                contributing_domains=list(domains),
                likely_outcomes=[o["event"] for o in fc["outcomes"]],
                tradability=self._assess_tradability(fc["risk_vector"])
            )
            primitives.append(primitive)
        return primitives
    
    def _assess_tradability(self, vector: str) -> Dict[str, bool]:
        tradability_map = {
            "infra.energy": {"insurance": True, "commodities": True, "logistics": True, "policy": True},
            "infra.transport": {"insurance": True, "commodities": False, "logistics": True, "policy": False},
            "labor": {"insurance": False, "commodities": False, "logistics": True, "policy": True},
            "legal": {"insurance": True, "commodities": False, "logistics": False, "policy": True},
            "supply": {"insurance": False, "commodities": True, "logistics": True, "policy": False},
        }
        for prefix, trad in tradability_map.items():
            if vector.startswith(prefix):
                return trad
        return {"insurance": False, "commodities": False, "logistics": False, "policy": False}


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def run_blacksnow_pipeline():
    print("=" * 60)
    print("BLACKSNOW - Ambient Risk Detection Pipeline")
    print("=" * 60)
    print()
    
    # 1. Harvest
    print("[1/5] HARVESTER: Ingesting signals...")
    harvester = Harvester()
    raw_signals = harvester.ingest_mock_data()
    print(f"      Collected {len(raw_signals)} raw signals")
    for sig in raw_signals:
        print(f"      - {sig.source_id[:40]}...")
    print()
    
    # 2. Normalize
    print("[2/5] NORMALIZER: Aligning to ontology...")
    normalizer = Normalizer()
    normalized = normalizer.normalize(raw_signals)
    for norm in normalized:
        print(f"      - {norm.ontology_path} | {norm.signal_type} | mag={norm.magnitude:.2f}")
    print()
    
    # 3. Accumulate
    print("[3/5] ACCUMULATOR: Bayesian evidence stacking...")
    accumulator = Accumulator()
    belief_states = accumulator.accumulate(normalized)
    for vector, belief in belief_states.items():
        print(f"      - {vector}: {belief:.2f}")
    print()
    
    # 4. Forecast
    print("[4/5] FORECASTER: Horizon modeling...")
    forecaster = Forecaster()
    forecasts = forecaster.forecast(belief_states)
    for fc in forecasts:
        print(f"      - {fc['risk_vector']}: horizon={fc['time_horizon_days']}d, conf={fc['confidence']}")
    print()
    
    # 5. Package
    print("[5/5] PACKAGER: Generating tradable primitives...")
    packager = Packager()
    primitives = packager.package(forecasts, normalized)
    print()
    
    # Output
    print("=" * 60)
    print("OUTPUT: Risk Primitives")
    print("=" * 60)
    for prim in primitives:
        print(json.dumps(asdict(prim), indent=2))
        print()
    
    return primitives


if __name__ == "__main__":
    run_blacksnow_pipeline()
