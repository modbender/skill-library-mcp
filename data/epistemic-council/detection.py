"""
epistemic_council/detection.py

Cross-domain detection engine. This is the first piece that actually tests
whether Epistemic Council produces anything useful.

MVP scope: Analogical detection only (A-type insights). We look for structural
similarity between claim sets from two different domains. The other insight
types (C, O, S) come later once we know A-type detection works.

How it works:
  1. Pull visible claims from both domains off the substrate
  2. Send them to the model with a structured prompt that asks it to
     identify structural similarities
  3. Parse the model's output into candidate insights
  4. Apply a cross-domain confidence penalty (domain distance)
  5. Write anything above the threshold to the substrate as an insight

The confidence penalty is the key mechanism here. An insight that maps
directly between closely-related concepts gets penalized less than one
that maps between distant concepts. This is empirically calibratable —
after the first few runs, we'll have data on whether the penalties are
set right.
"""

import time
import uuid
from dataclasses import dataclass, field
from typing import Optional

from substrate import Substrate, InsightType
from agent import ModelClient, DOMAINS


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class DetectionConfig:
    """
    Tunable parameters for cross-domain detection.
    These are initial guesses. They get calibrated after the first
    human review pass — don't treat them as gospel.
    """
    # Minimum confidence an insight must have before it's written
    min_confidence_threshold: float = 0.25

    # Base penalty applied to all cross-domain insights.
    # Rationale: any cross-domain claim is inherently less certain than
    # a within-domain claim. This is the floor penalty.
    base_cross_domain_penalty: float = 0.15

    # Additional penalty per unit of domain distance (0.0 to 1.0).
    # Domain distance is computed from overlap between key concepts.
    # No overlap = distance 1.0 = max penalty. Full overlap = distance 0.0 = no extra penalty.
    distance_penalty_weight: float = 0.2

    # Max insights written per detection run.
    # Prevents flooding the substrate with low-quality signal.
    max_insights_per_run: int = 5


# ---------------------------------------------------------------------------
# Domain distance
# ---------------------------------------------------------------------------

def compute_domain_distance(domain_a: str, domain_b: str) -> float:
    """
    Jaccard distance between two domains based on key concept overlap.

    distance = 1 - |intersection| / |union|

    Returns 0.0 if domains are identical, 1.0 if they share nothing.
    This is a rough proxy. It'll be refined once we have empirical data
    on which domain pairs actually produce valid insights.
    """
    if domain_a not in DOMAINS or domain_b not in DOMAINS:
        return 1.0  # Unknown domain = max distance

    concepts_a = set(DOMAINS[domain_a].key_concepts)
    concepts_b = set(DOMAINS[domain_b].key_concepts)

    intersection = concepts_a & concepts_b
    union = concepts_a | concepts_b

    if not union:
        return 1.0

    return 1.0 - (len(intersection) / len(union))


def compute_confidence_penalty(domain_a: str, domain_b: str, config: DetectionConfig) -> float:
    """
    Total confidence penalty for a cross-domain insight.
    
    penalty = base_penalty + (distance * distance_weight)
    
    Clamped to [0.0, 0.8] — we never want to penalize so hard that
    nothing can survive, and we never want to give a free pass.
    """
    distance = compute_domain_distance(domain_a, domain_b)
    penalty = config.base_cross_domain_penalty + (distance * config.distance_penalty_weight)
    return max(0.0, min(0.8, penalty))


# ---------------------------------------------------------------------------
# Detection engine
# ---------------------------------------------------------------------------

class DetectionEngine:
    """
    Looks at claims from two domains and finds analogical patterns.

    Usage:
        substrate = Substrate("epistemic.db")
        client = ModelClient("qwen2.5:14b")
        engine = DetectionEngine(substrate, client)
        insights = engine.detect("computer_science", "biology")
    """

    def __init__(
        self,
        substrate: Substrate,
        model_client: ModelClient,
        config: Optional[DetectionConfig] = None,
    ):
        self.substrate = substrate
        self.model = model_client
        self.config = config or DetectionConfig()
        self.agent_id = f"detection_engine_{uuid.uuid4().hex[:8]}"

    def detect(self, domain_a: str, domain_b: str) -> list[str]:
        """
        Main entry point. Pulls claims from both domains, runs analogical
        detection, writes valid insights to the substrate.
        Returns list of insight event IDs that were written.
        """
        print(f"\n🔬 Detection engine: scanning {domain_a} ↔ {domain_b}")

        # Pull claims (filter out visibility-pruned events)
        claims_a = [e for e in self.substrate.get_claims_by_domain(domain_a)
                    if not self.substrate.is_visibility_pruned(e.event_id)]
        claims_b = [e for e in self.substrate.get_claims_by_domain(domain_b)
                    if not self.substrate.is_visibility_pruned(e.event_id)]

        if not claims_a or not claims_b:
            print(f"⚠️  No claims in one or both domains. Nothing to detect.")
            print(f"    {domain_a}: {len(claims_a)} claims | {domain_b}: {len(claims_b)} claims")
            return []

        print(f"    {domain_a}: {len(claims_a)} claims | {domain_b}: {len(claims_b)} claims")

        # Compute penalty for this domain pair
        penalty = compute_confidence_penalty(domain_a, domain_b, self.config)
        print(f"    Cross-domain confidence penalty: {penalty:.2f}")

        # Build prompt and query model
        prompt = self._build_detection_prompt(claims_a, claims_b, domain_a, domain_b)
        print(f"🔍 Detection engine: querying model...")
        raw_response = self.model.generate(prompt, temperature=0.2)

        # Parse candidates
        candidates = self._parse_insights(raw_response, domain_a, domain_b)
        print(f"📋 Detection engine: {len(candidates)} candidate insights parsed")

        # Apply penalty and filter
        insight_ids = []
        for candidate in candidates:
            adjusted_confidence = candidate["confidence"] - penalty
            if adjusted_confidence < self.config.min_confidence_threshold:
                print(f"   ✗ Dropped (conf {adjusted_confidence:.2f} < threshold): {candidate['text'][:70]}...")
                continue

            # Cap at max insights per run
            if len(insight_ids) >= self.config.max_insights_per_run:
                print(f"   ✗ Dropped (max {self.config.max_insights_per_run} insights per run reached)")
                break

            iid = self.substrate.write_insight(
                agent_id=self.agent_id,
                domain="cross_domain",
                insight_text=candidate["text"],
                insight_type=InsightType.ANALOGICAL,
                confidence=adjusted_confidence,
                source_claim_ids=candidate["source_claim_ids"],
                cross_domain_flag=True,
            )
            # write_insight returns a SubstrateEvent; extract event_id
            if hasattr(iid, 'event_id'):
                iid = iid.event_id
            insight_ids.append(iid)
            print(f"   ✓ Insight written (conf={adjusted_confidence:.2f}): {candidate['text'][:70]}...")

        print(f"📦 Detection engine: {len(insight_ids)} insights written to substrate\n")
        return insight_ids

    # -----------------------------------------------------------------
    # Prompt construction
    # -----------------------------------------------------------------

    def _build_detection_prompt(
        self,
        claims_a: list,
        claims_b: list,
        domain_a: str,
        domain_b: str,
    ) -> str:
        """
        Build the detection prompt. This is structured to:
          1. Present claims from both domains clearly
          2. Ask specifically for structural analogies (not surface similarities)
          3. Require the model to cite which specific claims support each analogy
          4. Ask for confidence scores
        """
        claims_a_text = "\n".join(
            f"  [CS-{i+1}] (conf={e.confidence:.2f}) {e.content['text']}"
            for i, e in enumerate(claims_a)
        )
        claims_b_text = "\n".join(
            f"  [BIO-{i+1}] (conf={e.confidence:.2f}) {e.content['text']}"
            for i, e in enumerate(claims_b)
        )

        # Build a mapping from index to event_id so we can resolve references later
        # (stored on self temporarily for use during parsing)
        self._current_claim_map_a = {f"CS-{i+1}": e.event_id for i, e in enumerate(claims_a)}
        self._current_claim_map_b = {f"BIO-{i+1}": e.event_id for i, e in enumerate(claims_b)}

        prompt = f"""You are analyzing claims from two different domains to find STRUCTURAL ANALOGIES.

A structural analogy is NOT a surface-level similarity. It is a case where the
underlying mechanism, pattern, or logical structure in one domain maps onto a
similar structure in another domain — even though the specific entities and
context are completely different.

DOMAIN A — {domain_a}:
{claims_a_text}

DOMAIN B — {domain_b}:
{claims_b_text}

TASK: Identify structural analogies between these two sets of claims.
For each analogy you find:
  - Explain the shared structural pattern (not just "both involve optimization")
  - Cite the specific claims from each domain that support it (use the labels like CS-1, BIO-2)
  - Assign a confidence score (0.0 to 1.0) reflecting how strong the structural
    mapping actually is. Be conservative — weak analogies should score below 0.4.

IMPORTANT:
  - Do NOT flag surface similarities (e.g. "both systems have agents" is not an analogy)
  - Do NOT invent connections that aren't supported by the claims above
  - If you find no genuine structural analogies, say so explicitly

FORMAT each analogy exactly like this:

ANALOGY: [description of the structural pattern]
SOURCES: [comma-separated list of claim labels, e.g. CS-2, CS-4, BIO-1, BIO-3]
CONFIDENCE: [number between 0.0 and 1.0]
---

Produce between 0 and 5 analogies. Be precise and conservative.
"""
        return prompt

    # -----------------------------------------------------------------
    # Response parsing
    # -----------------------------------------------------------------

    def _parse_insights(
        self,
        raw_response: str,
        domain_a: str,
        domain_b: str,
    ) -> list[dict]:
        """
        Parse model output into structured insight candidates.
        Resolves claim label references (CS-1, BIO-2) back to actual
        substrate event IDs using the map built during prompt construction.
        """
        insights = []
        current = {}

        for line in raw_response.split("\n"):
            line = line.strip()

            if line.startswith("ANALOGY:"):
                if current and "text" in current and "confidence" in current:
                    insights.append(current)
                current = {"text": line[len("ANALOGY:"):].strip()}

            elif line.startswith("SOURCES:") and current:
                raw_sources = line[len("SOURCES:"):].strip()
                current["source_claim_ids"] = self._resolve_sources(raw_sources)

            elif line.startswith("CONFIDENCE:") and current:
                current["confidence"] = self._parse_confidence(line[len("CONFIDENCE:"):].strip())

            elif line == "---":
                if current and "text" in current and "confidence" in current:
                    insights.append(current)
                    current = {}

        # Catch last entry
        if current and "text" in current and "confidence" in current:
            insights.append(current)

        # Ensure all insights have source_claim_ids (even if empty)
        for insight in insights:
            if "source_claim_ids" not in insight:
                insight["source_claim_ids"] = []

        # If model said "no analogies found" or similar, return empty
        no_analogy_signals = [
            "no genuine", "no structural", "no analogy", "no analogies",
            "cannot identify", "did not find",
        ]
        if not insights and any(s in raw_response.lower() for s in no_analogy_signals):
            print(f"   ℹ️  Model explicitly reported no analogies found")
            return []

        return insights

    def _resolve_sources(self, raw_sources: str) -> list[str]:
        """
        Turn "CS-2, CS-4, BIO-1, BIO-3" into actual substrate event IDs.
        Silently skips any labels it can't resolve — better to have
        partial provenance than to crash.
        """
        resolved = []
        labels = [s.strip().rstrip(".") for s in raw_sources.split(",")]

        for label in labels:
            label = label.strip()
            if label in self._current_claim_map_a:
                resolved.append(self._current_claim_map_a[label])
            elif label in self._current_claim_map_b:
                resolved.append(self._current_claim_map_b[label])
            # else: silently skip unresolvable labels

        return resolved

    def _parse_confidence(self, raw: str) -> float:
        """Same logic as agent — handles variations in model formatting."""
        raw = raw.strip().rstrip(".")
        if "/" in raw:
            raw = raw.split("/")[0].strip()
        raw = raw.replace("%", "").strip()
        try:
            val = float(raw)
            if val > 1.0:
                val = val / 100.0
            return max(0.0, min(1.0, val))
        except ValueError:
            return 0.2