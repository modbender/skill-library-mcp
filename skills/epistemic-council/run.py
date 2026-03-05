"""
epistemic_council/run.py

The entry point. Orchestrates the full pipeline:

  1. Both domain agents reason on a shared query
  2. Claims land in the substrate
  3. Detection engine scans for cross-domain analogies
  4. Adversarial validation challenges insights
  5. Results are printed for human review

Usage:
    python run.py

Prerequisites:
    ollama serve                    # Ollama must be running
    ollama pull glm-4.7-flash         # Model must be pulled
    pip install requests            # Only external dependency
"""

import os
import sys
from pathlib import Path

from substrate import Substrate
from agent import DomainAgent, ModelClient
from detection import DetectionEngine, DetectionConfig
from challenge_orchestrator import ChallengeOrchestrator


# ---------------------------------------------------------------------------
# Query bank
# ---------------------------------------------------------------------------

QUERIES = [
    {
        "id": "optimization_under_constraints",
        "text": (
            "How do systems find good solutions to complex optimization problems "
            "when they cannot evaluate every possible option? Focus on strategies "
            "that work well in large, uncertain search spaces."
        ),
    },
    {
        "id": "emergent_collective_behavior",
        "text": (
            "How do large groups of simple agents produce intelligent collective "
            "behavior without any central coordinator? What makes some collective "
            "strategies robust and others fragile?"
        ),
    },
    {
        "id": "adaptation_to_changing_environment",
        "text": (
            "How do systems adapt their strategies when the environment they "
            "operate in changes over time? What makes adaptation fast versus slow, "
            "and what are the tradeoffs involved?"
        ),
    },
]


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def run(query_id: str = "optimization_under_constraints", db_path: str = "epistemic.db"):
    """
    Execute one full cycle of the epistemic council loop.

    Args:
        query_id: Which query from QUERIES to use
        db_path:  Path to the SQLite substrate file
    """
    # Find the query
    query = next((q for q in QUERIES if q["id"] == query_id), None)
    if query is None:
        print(f"❌ Unknown query_id: {query_id}")
        print(f"   Available: {[q['id'] for q in QUERIES]}")
        return

    print("=" * 70)
    print("  EPISTEMIC COUNCIL — PHASE 2 RUN")
    print("=" * 70)
    print(f"\n📌 Query: {query['id']}")
    print(f"   {query['text']}\n")

    # --- Substrate ---------------------------------------------------------
    print("─" * 70)
    print("  PHASE 1: SUBSTRATE")
    print("─" * 70)
    substrate = Substrate(db_path)
    print(f"✅ Substrate initialized: {db_path} ({substrate.event_count()} existing events)\n")

    # --- Model client ------------------------------------------------------
    print("─" * 70)
    print("  PHASE 2: MODEL")
    print("─" * 70)
    model_client = ModelClient("glm-4.7-flash")
    print()

    # --- Domain agents -----------------------------------------------------
    print("─" * 70)
    print("  PHASE 3: DOMAIN AGENTS")
    print("─" * 70)

    cs_agent = DomainAgent("computer_science", substrate, model_client)
    bio_agent = DomainAgent("biology", substrate, model_client)
    print()

    # CS agent reasons first
    print(f"── {cs_agent.domain.name} ──")
    cs_claim_ids = cs_agent.reason(query["text"])
    print()

    # Then biology
    print(f"── {bio_agent.domain.name} ──")
    bio_claim_ids = bio_agent.reason(query["text"])
    print()

    # --- Detection ---------------------------------------------------------
    print("─" * 70)
    print("  PHASE 4: CROSS-DOMAIN DETECTION")
    print("─" * 70)

    engine = DetectionEngine(substrate, model_client)
    insight_ids = engine.detect("computer_science", "biology")
    print()

    # --- Adversarial Validation --------------------------------------------
    print("─" * 70)
    print("  PHASE 5: ADVERSARIAL VALIDATION")
    print("─" * 70)

    if not insight_ids:
        print("⚠️  No insights to validate.\n")
        validated_insights = []
        challenged_insights = []
        rejected_insights = []
    else:
        orchestrator = ChallengeOrchestrator(substrate, model_client.base_url)
        
        # Get insight events
        insight_events = [substrate.get_event(iid) for iid in insight_ids]
        
        # Run validation
        validated_insights, challenged_insights, rejected_insights = orchestrator.validate_batch(
            insight_events, query["text"]
        )
    print()

    # --- Summary -----------------------------------------------------------
    print("─" * 70)
    print("  PHASE 6: RESULTS")
    print("─" * 70)

    print(f"\n📊 Substrate state:")
    print(f"   Total events:      {substrate.event_count()}")
    print(f"   CS claims:         {len(cs_claim_ids)}")
    print(f"   Biology claims:    {len(bio_claim_ids)}")
    print(f"   Insights found:    {len(insight_ids)}")
    print(f"   Validated:         {len(validated_insights)}")
    print(f"   Challenged:        {len(challenged_insights)}")
    print(f"   Rejected:          {len(rejected_insights)}\n")

    if not insight_ids:
        print("⚠️  No insights were written. Either:")
        print("   - The model didn't find structural analogies")
        print("   - Confidence scores fell below threshold after penalty")
        print("   - The query didn't produce claims with enough overlap")
        print("\n   Try a different query or adjust DetectionConfig thresholds.")
    else:
        # Show validated insights
        if validated_insights:
            print("✅ VALIDATED INSIGHTS:\n")
            for i, (insight, result) in enumerate(validated_insights, 1):
                print(f"  [{i}] (confidence: {result['original_confidence']:.2f} → {result['final_confidence']:.2f})")
                print(f"      {insight.content['text'][:100]}...")
                print(f"      Passed: {result['passes']}/3 challenges")
                print(f"      Type: {insight.content['insight_type']}")
                print(f"      Source claims: {len(insight.parent_ids)}")
                print()
        
        # Show challenged insights needing review
        if challenged_insights:
            print("⚠️  CHALLENGED INSIGHTS (need human review):\n")
            for i, (insight, result) in enumerate(challenged_insights, 1):
                print(f"  [{i}] (confidence: {result['original_confidence']:.2f} → {result['final_confidence']:.2f})")
                print(f"      {insight.content['text'][:100]}...")
                print(f"      Passed: {result['passes']}/3 challenges")
                print()
        
        # Show rejected insights
        if rejected_insights:
            print("❌ REJECTED INSIGHTS:\n")
            for i, (insight, result) in enumerate(rejected_insights, 1):
                print(f"  [{i}] (confidence: {result['original_confidence']:.2f} → {result['final_confidence']:.2f})")
                print(f"      {insight.content['text'][:100]}...")
                print(f"      Failed: {3 - result['passes']}/3 challenges")
                print()

    # --- Integrity check ---------------------------------------------------
    print("─" * 70)
    print("  INTEGRITY CHECK")
    print("─" * 70)
    verification = substrate.verify_all()
    failed_list = verification.get("failed", [])
    status = "✅ PASSED" if not failed_list else "❌ FAILED"
    print(f"   {status} — {verification['passed']}/{verification['total']} events verified")
    if failed_list:
        print(f"   Failed: {failed_list}")

    print("\n" + "=" * 70)
    print("  RUN COMPLETE")
    print("=" * 70 + "\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Epistemic Council — Phase 2 Run")
    parser.add_argument(
        "--query", "-q",
        default="optimization_under_constraints",
        choices=[q["id"] for q in QUERIES],
        help="Which query to run (default: optimization_under_constraints)",
    )
    parser.add_argument(
        "--db", "-d",
        default="epistemic.db",
        help="Path to substrate database (default: epistemic.db)",
    )
    parser.add_argument(
        "--list-queries",
        action="store_true",
        help="Print available queries and exit",
    )

    args = parser.parse_args()

    if args.list_queries:
        print("\nAvailable queries:\n")
        for q in QUERIES:
            print(f"  {q['id']}")
            print(f"    {q['text']}\n")
        sys.exit(0)

    run(query_id=args.query, db_path=args.db)
