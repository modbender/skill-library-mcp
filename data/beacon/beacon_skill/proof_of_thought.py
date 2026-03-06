"""BEP-1: Proof-of-Thought — Verifiable Compute Provenance.

Agents publish commitment hashes of reasoning traces, proving they "thought"
before answering. Zero-knowledge: the hash proves the trace exists without
revealing it. A challenge/reveal protocol allows selective disclosure.

The commitment is SHA256(prompt_hash + trace_hash + output_hash), which
anchors the entire reasoning chain without exposing any part of it.

Beacon 2.8.0 — Elyan Labs.
"""

import hashlib
import json
import time
from typing import Any, Dict, List, Optional

from .anchor import commitment_hash
from .storage import _dir, append_jsonl, read_jsonl_tail

PROOF_LOG_FILE = "thought_proofs.jsonl"
CHALLENGE_LOG_FILE = "thought_challenges.jsonl"


class ThoughtProof:
    """A commitment hash of an agent's reasoning trace."""

    def __init__(
        self,
        agent_id: str,
        prompt_hash: str,
        trace_hash: str,
        output_hash: str,
        commitment: str,
        model_id: str = "",
        token_count: int = 0,
        ts: int = 0,
        sig: str = "",
    ):
        self.agent_id = agent_id
        self.prompt_hash = prompt_hash
        self.trace_hash = trace_hash
        self.output_hash = output_hash
        self.commitment = commitment
        self.model_id = model_id
        self.token_count = token_count
        self.ts = ts or int(time.time())
        self.sig = sig

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "prompt_hash": self.prompt_hash,
            "trace_hash": self.trace_hash,
            "output_hash": self.output_hash,
            "commitment": self.commitment,
            "model_id": self.model_id,
            "token_count": self.token_count,
            "ts": self.ts,
            "sig": self.sig,
        }

    def to_envelope(self) -> Dict[str, Any]:
        """Convert to a beacon envelope payload."""
        return {
            "kind": "thought_proof",
            **self.to_dict(),
        }


class ThoughtProofManager:
    """Create, verify, challenge, and reveal thought proofs."""

    def __init__(self, data_dir=None):
        self._dir = data_dir or _dir()

    @staticmethod
    def _hash(data: str) -> str:
        """SHA256 hash of a string."""
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    @staticmethod
    def _compute_commitment(prompt_hash: str, trace_hash: str, output_hash: str) -> str:
        """Compute the triple-hash commitment."""
        combined = f"{prompt_hash}:{trace_hash}:{output_hash}"
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()

    def create_proof(
        self,
        identity: Any,
        prompt: str,
        trace: str,
        output: str,
        model_id: str = "",
    ) -> ThoughtProof:
        """Create a thought proof from prompt, reasoning trace, and output.

        Args:
            identity: AgentIdentity for signing.
            prompt: The input prompt.
            trace: The full reasoning trace (chain-of-thought).
            output: The final output/answer.
            model_id: Model identifier (e.g. "grok-3", "claude-opus-4-6").

        Returns:
            ThoughtProof with commitment hash and signature.
        """
        prompt_hash = self._hash(prompt)
        trace_hash = self._hash(trace)
        output_hash = self._hash(output)
        commitment = self._compute_commitment(prompt_hash, trace_hash, output_hash)
        token_count = len(trace.split())  # Approximate word count

        # Sign the commitment
        sig = identity.sign_hex(commitment.encode("utf-8"))

        proof = ThoughtProof(
            agent_id=identity.agent_id,
            prompt_hash=prompt_hash,
            trace_hash=trace_hash,
            output_hash=output_hash,
            commitment=commitment,
            model_id=model_id,
            token_count=token_count,
            sig=sig,
        )

        # Log locally
        append_jsonl(PROOF_LOG_FILE, proof.to_dict())

        return proof

    def anchor_proof(self, proof: ThoughtProof, anchor_mgr: Any) -> Dict[str, Any]:
        """Anchor a thought proof to RustChain.

        Args:
            proof: The ThoughtProof to anchor.
            anchor_mgr: AnchorManager instance.

        Returns:
            Anchor submission result.
        """
        return anchor_mgr.anchor(
            proof.to_dict(),
            data_type="proof_of_thought",
            metadata={
                "agent_id": proof.agent_id,
                "model_id": proof.model_id,
                "commitment": proof.commitment,
            },
        )

    def verify_proof(
        self,
        commitment: str,
        prompt: str,
        trace: str,
        output: str,
    ) -> bool:
        """Verify that data matches a commitment hash.

        This is used during the reveal phase: if someone reveals
        their trace, we can verify it matches the original commitment.

        Args:
            commitment: The claimed commitment hash.
            prompt: The revealed prompt.
            trace: The revealed reasoning trace.
            output: The revealed output.

        Returns:
            True if the data matches the commitment.
        """
        prompt_hash = self._hash(prompt)
        trace_hash = self._hash(trace)
        output_hash = self._hash(output)
        computed = self._compute_commitment(prompt_hash, trace_hash, output_hash)
        return computed == commitment

    def challenge_proof(
        self,
        identity: Any,
        target_agent_id: str,
        commitment: str,
        reason: str = "",
    ) -> Dict[str, Any]:
        """Issue a challenge requesting proof reveal.

        Args:
            identity: Our AgentIdentity.
            target_agent_id: Agent whose proof we're challenging.
            commitment: The commitment hash to challenge.
            reason: Why we're requesting the reveal.

        Returns:
            Challenge envelope payload.
        """
        now = int(time.time())
        challenge = {
            "kind": "thought_challenge",
            "agent_id": identity.agent_id,
            "target_agent_id": target_agent_id,
            "commitment": commitment,
            "reason": reason,
            "ts": now,
        }

        append_jsonl(CHALLENGE_LOG_FILE, challenge)
        return challenge

    def reveal_proof(
        self,
        identity: Any,
        commitment: str,
        prompt: str,
        trace: str,
        output: str,
    ) -> Dict[str, Any]:
        """Respond to a challenge by revealing the thought data.

        Only reveals if the data actually matches the commitment
        (prevents accidental exposure of wrong data).

        Args:
            identity: Our AgentIdentity.
            commitment: The commitment being revealed.
            prompt: The original prompt.
            trace: The reasoning trace.
            output: The final output.

        Returns:
            Reveal envelope payload, or error if mismatch.
        """
        if not self.verify_proof(commitment, prompt, trace, output):
            return {"error": "Data does not match commitment — reveal aborted"}

        now = int(time.time())
        reveal = {
            "kind": "thought_reveal",
            "agent_id": identity.agent_id,
            "commitment": commitment,
            "prompt": prompt,
            "trace": trace,
            "output": output,
            "ts": now,
        }

        # Sign the reveal
        sig = identity.sign_hex(commitment.encode("utf-8"))
        reveal["sig"] = sig

        return reveal

    def proof_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List our locally created thought proofs."""
        return read_jsonl_tail(PROOF_LOG_FILE, limit=limit)

    def challenge_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List challenges we've issued or received."""
        return read_jsonl_tail(CHALLENGE_LOG_FILE, limit=limit)
