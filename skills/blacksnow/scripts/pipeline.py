#!/usr/bin/env python3
"""
BlackSnow Full Pipeline
Integrates harvester, normalizer, accumulator, forecaster, packager, memory, and webhook.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).parent))

from blacksnow_test import Normalizer, Accumulator, Forecaster, Packager, RiskPrimitive
from harvester import harvest_all_sources
from harvester_extended import harvest_all_extended
from memory import BlackSnowMemory

# ============================================================================
# FULL PIPELINE
# ============================================================================

def run_full_pipeline(webhook_url: str = None, verbose: bool = True) -> dict:
    """
    Execute the complete BlackSnow pipeline:
    1. Harvest live data
    2. Normalize to ontology
    3. Accumulate beliefs
    4. Forecast outcomes
    5. Package primitives
    6. Store to memory
    7. Push to webhook (if configured)
    """
    
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "stages": {},
        "primitives": [],
        "webhook": None
    }
    
    # Initialize memory
    memory = BlackSnowMemory()
    
    # 1. Harvest
    if verbose:
        print("=" * 60)
        print("BLACKSNOW FULL PIPELINE")
        print("=" * 60)
        print("\n[1/7] HARVEST: Collecting live signals...")
    
    # Harvest from both basic and extended sources
    raw_signals = harvest_all_sources()
    extended_signals = harvest_all_extended()
    raw_signals.extend(extended_signals)
    
    results["stages"]["harvest"] = {"count": len(raw_signals)}
    
    # Store raw signals
    stored_signals = memory.store_signals(raw_signals)
    if verbose:
        print(f"      Stored {stored_signals} signals to memory")
    
    # 2. Normalize
    if verbose:
        print("\n[2/7] NORMALIZE: Aligning to ontology...")
    
    normalizer = Normalizer()
    # Convert harvested signals to format normalizer expects
    from dataclasses import dataclass
    
    @dataclass
    class RawSig:
        source_id: str
        domain: str
        raw_text: str
        timestamp: str
        confidence: float
    
    normalized_input = [
        RawSig(
            source_id=s.source_id,
            domain=s.domain,
            raw_text=s.raw_text,
            timestamp=s.timestamp,
            confidence=s.confidence
        ) for s in raw_signals
    ]
    
    normalized = normalizer.normalize(normalized_input)
    results["stages"]["normalize"] = {"count": len(normalized)}
    
    if verbose:
        for norm in normalized:
            print(f"      - {norm.ontology_path} | {norm.signal_type} | mag={norm.magnitude:.2f}")
    
    # 3. Accumulate
    if verbose:
        print("\n[3/7] ACCUMULATE: Bayesian evidence stacking...")
    
    accumulator = Accumulator()
    belief_states = accumulator.accumulate(normalized)
    results["stages"]["accumulate"] = {"vectors": dict(belief_states)}
    
    # Update persistent belief states
    memory.update_belief_states(belief_states)
    
    if verbose:
        for vector, belief in belief_states.items():
            print(f"      - {vector}: {belief:.2f}")
    
    # 4. Forecast
    if verbose:
        print("\n[4/7] FORECAST: Horizon modeling...")
    
    forecaster = Forecaster()
    forecasts = forecaster.forecast(belief_states)
    results["stages"]["forecast"] = {"count": len(forecasts)}
    
    if verbose:
        for fc in forecasts:
            print(f"      - {fc['risk_vector']}: horizon={fc['time_horizon_days']}d, conf={fc['confidence']}")
    
    # 5. Package
    if verbose:
        print("\n[5/7] PACKAGE: Generating tradable primitives...")
    
    packager = Packager()
    primitives = packager.package(forecasts, normalized)
    results["stages"]["package"] = {"count": len(primitives)}
    
    # 6. Store vectors
    if verbose:
        print("\n[6/7] PERSIST: Storing to workspace memory...")
    
    stored_vectors = memory.store_vectors(primitives)
    results["stages"]["persist"] = {"stored": stored_vectors}
    
    if verbose:
        print(f"      Stored {stored_vectors} risk primitives")
    
    # 7. Webhook (optional)
    if webhook_url:
        if verbose:
            print(f"\n[7/7] WEBHOOK: Pushing to {webhook_url}...")
        
        from webhook import WebhookConfig, WebhookDelivery
        config = WebhookConfig(url=webhook_url, tier="operator")
        delivery = WebhookDelivery(config)
        webhook_result = delivery.deliver(primitives)
        results["webhook"] = webhook_result
        
        if verbose:
            if webhook_result["success"]:
                print(f"      ✓ Delivered {webhook_result['primitives_sent']} primitives")
            else:
                print(f"      ✗ Failed: {webhook_result['error']}")
    else:
        if verbose:
            print("\n[7/7] WEBHOOK: Skipped (no URL configured)")
    
    # Convert primitives to dict for output
    from dataclasses import asdict
    results["primitives"] = [asdict(p) for p in primitives]
    
    # Summary
    if verbose:
        print("\n" + "=" * 60)
        print("PIPELINE COMPLETE")
        print("=" * 60)
        print(f"Signals harvested: {len(raw_signals)}")
        print(f"Vectors detected:  {len(belief_states)}")
        print(f"Primitives output: {len(primitives)}")
        print()
        
        # Memory status
        status = memory.get_status()
        print(f"Memory: {status['total_signals']} total signals, {status['total_vectors']} total vectors")
        print(f"Storage: {status['storage_path']}")
    
    return results


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    webhook_url = None
    if len(sys.argv) > 1:
        webhook_url = sys.argv[1]
    
    results = run_full_pipeline(webhook_url=webhook_url, verbose=True)
    
    print("\n" + "=" * 60)
    print("OUTPUT: Risk Primitives (JSON)")
    print("=" * 60)
    for prim in results["primitives"]:
        print(json.dumps(prim, indent=2))
        print()
