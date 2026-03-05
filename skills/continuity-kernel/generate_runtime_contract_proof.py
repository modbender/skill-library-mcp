from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from diagnostics import FailOpenDiagnostics
from drift import BeforeToolCallDriftClassifier
from runtime_contract import (
    RUNTIME_CONTRACT_VERSION,
    canonicalize_continuity_packet,
    canonicalize_drift_warning,
    continuity_packet_digest,
    drift_warning_digest,
)
from runtime_hooks import ContinuityHookAdapter
from service import ContinuityRuntimeService
from store import ContinuityStore


class MalformedPacketBuilder:
    def build_packet(self, agent_id: str):
        return {
            "agent_id": agent_id,
            "schema_version": "v1",
            "token_budget": "40",
            "estimated_tokens": 80,
            "runtime_state_fingerprint": "not-a-hash",
            "fields": {"mission": "ok", "bad": {"set_payload": {1, 2}}},
            "dropped_fields": ["legacy", 7],
        }


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        db = os.path.join(td, "runtime_contract.db")
        diagnostics = FailOpenDiagnostics()

        store = ContinuityStore(db, diagnostics=diagnostics)
        store.migrate()
        store.upsert_soul_card(
            agent_id="forge",
            role="Runtime hardening engineer",
            persona="Audit-grade, fail-open-first",
            user_profile="P0 continuity owner",
            preferences={"proof": "required"},
            constraints={"non_blocking": True},
        )
        store.upsert_mission_ticket(
            agent_id="forge",
            mission="Harden runtime continuity paths",
            definition_of_done="Fail-open runtime + deterministic proof receipts",
            constraints={"mission_lock": "runtime hardening deterministic proof"},
        )

        adapter = ContinuityHookAdapter(store=store, token_budget=96, diagnostics=diagnostics)
        payload = {"messages": [{"role": "user", "content": "run runtime proof"}]}

        out_a = adapter.on_llm_input("forge", payload)
        out_b = adapter.on_llm_input("forge", payload)

        packet_a = out_a.get("continuity_packet", {})
        packet_b = out_b.get("continuity_packet", {})

        runtime_service = ContinuityRuntimeService(
            repository=store,
            packet_builder=MalformedPacketBuilder(),
            diagnostics=diagnostics,
            auto_migrate=False,
        )
        malformed_out = runtime_service.inject_llm_input("forge", payload)
        malformed_packet = malformed_out.get("continuity_packet", {})

        drift = BeforeToolCallDriftClassifier(store, warn_threshold=0.35, diagnostics=diagnostics)
        aligned = drift.classify(
            "forge",
            "exec",
            {"command": "python3 -m unittest tests/continuity-kernel/test_runtime_hook_adapter.py -v runtime hardening"},
        )
        adversarial = drift.classify("forge", "web_search", {"query": "runtime hawaii deals"})
        unrelated = drift.classify("forge", "web_search", {"query": "best vacation spots"})

        artifact = {
            "schema_version": "v1",
            "runtime_contract_version": RUNTIME_CONTRACT_VERSION,
            "note": "xhigh-only rebuild",
            "runtime_packet_determinism": {
                "packet_a": canonicalize_continuity_packet(packet_a),
                "packet_b": canonicalize_continuity_packet(packet_b),
                "digest_a": continuity_packet_digest(packet_a),
                "digest_b": continuity_packet_digest(packet_b),
                "stable": continuity_packet_digest(packet_a) == continuity_packet_digest(packet_b),
            },
            "runtime_packet_normalization": {
                "raw_like_malformed_path_digest": continuity_packet_digest(malformed_packet),
                "normalized_packet": canonicalize_continuity_packet(malformed_packet),
            },
            "drift_warning_determinism": {
                "aligned": {
                    "canonical": canonicalize_drift_warning(aligned),
                    "digest": drift_warning_digest(aligned),
                },
                "adversarial": {
                    "canonical": canonicalize_drift_warning(adversarial),
                    "digest": drift_warning_digest(adversarial),
                },
                "unrelated": {
                    "canonical": canonicalize_drift_warning(unrelated),
                    "digest": drift_warning_digest(unrelated),
                },
            },
            "diagnostics": diagnostics.snapshot(),
        }

        out_path = Path.home() / ".cache" / "continuity-kernel" / "checkpoints" / "forge_p0_runtime_contract_proof_2026-02-21.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(artifact, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        print(out_path.as_posix())


if __name__ == "__main__":
    main()
