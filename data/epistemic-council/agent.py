"""
epistemic_council/agent.py

Domain-specialist agents. Each one owns a domain, reasons within it,
and writes claims to the substrate. They don't talk to each other directly —
all interaction goes through the substrate.

The agent is a thin wrapper around three things:
  1. A domain definition (scope, boundaries, what it can and can't claim)
  2. A prompt strategy (how we frame queries to the model for this domain)
  3. A connection to the substrate (where output lands)

The model itself is handled by ModelClient — agents don't know or care
whether that's a local Ollama instance or an API call.
"""

import time
import uuid
from dataclasses import dataclass, field
from typing import Optional

from substrate import Substrate, InsightType


# ---------------------------------------------------------------------------
# Domain definition
# ---------------------------------------------------------------------------

@dataclass
class DomainDefinition:
    """
    Defines what a domain agent can and can't do.
    This is the boundary the agent is supposed to stay within.
    The adversarial layer will check whether it actually does.
    """
    name: str                                    # e.g. "computer_science"
    description: str                             # Human-readable scope
    key_concepts: list[str] = field(default_factory=list)   # Core vocabulary
    boundary_rules: list[str] = field(default_factory=list) # What's out of scope
    overlap_zones: list[str] = field(default_factory=list)  # Where other domains touch


# Predefined domains for MVP. These are the two we start with.

DOMAIN_COMPUTER_SCIENCE = DomainDefinition(
    name="computer_science",
    description=(
        "Algorithm design, computational complexity, data structures, "
        "optimization problems, search strategies, distributed systems, "
        "and formal methods in computing."
    ),
    key_concepts=[
        "algorithm", "complexity", "optimization", "search", "graph",
        "sorting", "hashing", "parallelism", "convergence", "state space",
        "fitness function", "heuristic", "greedy", "dynamic programming",
        "divide and conquer", "distributed consensus",
    ],
    boundary_rules=[
        "Do not make claims about biological mechanisms or evolution as causal explanations.",
        "Do not claim biological systems 'invented' or 'designed' algorithms.",
        "Stick to computational and mathematical properties of systems.",
    ],
    overlap_zones=[
        "Optimization theory (shared with biology via evolutionary algorithms)",
        "Graph theory (shared with biology via network structures)",
        "Emergent behavior (shared with biology via swarm systems)",
    ],
)

DOMAIN_BIOLOGY = DomainDefinition(
    name="biology",
    description=(
        "Evolutionary systems, natural selection, swarm behavior, "
        "biological networks, adaptation mechanisms, ecological optimization, "
        "and emergent properties of biological populations."
    ),
    key_concepts=[
        "evolution", "natural selection", "fitness", "adaptation", "mutation",
        "population", "swarm", "colony", "emergence", "ecosystem",
        "genetic algorithm", "ant colony", "slime mold", "neural network (biological)",
        "ecological niche", "co-evolution", "selection pressure",
    ],
    boundary_rules=[
        "Do not make claims about computational complexity classes.",
        "Do not claim biological systems are 'running algorithms' in a literal sense.",
        "Stick to observed biological phenomena and mechanisms.",
    ],
    overlap_zones=[
        "Optimization (shared with CS via evolutionary computation)",
        "Network structure (shared with CS via biological networks)",
        "Emergent behavior (shared with CS via swarm intelligence)",
    ],
)

DOMAINS = {
    "computer_science": DOMAIN_COMPUTER_SCIENCE,
    "biology": DOMAIN_BIOLOGY,
}


# ---------------------------------------------------------------------------
# Model client — abstraction over how we talk to the model
# ---------------------------------------------------------------------------

class ModelClient:
    """
    Talks to a local model via Ollama HTTP API.
    
    Setup (do this once before running anything):
        ollama pull qwen2.5:14b
    
    Or whatever model you want. The agent doesn't care about the model name —
    it's configured at init time.
    """

    def __init__(self, model_name: str = "qwen2.5:14b", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self._verify_connection()

    def _verify_connection(self):
        """Check that Ollama is running and the model is available."""
        import requests
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            resp.raise_for_status()
            available = [m["name"] for m in resp.json().get("models", [])]
            if self.model_name not in available:
                print(f"⚠️  Model '{self.model_name}' not found locally.")
                print(f"    Run: ollama pull {self.model_name}")
                print(f"    Available: {available}")
                raise RuntimeError(f"Model {self.model_name} not available")
            print(f"✅ Model client connected: {self.model_name}")
        except requests.ConnectionError:
            raise RuntimeError(
                "Cannot connect to Ollama. Make sure it's running:\n"
                "    ollama serve"
            )

    def generate(self, prompt: str, temperature: float = 0.3) -> str:
        """
        Send a prompt, get a response. Blocking call.
        Temperature is low by default — we want consistent, careful reasoning,
        not creative hallucination.
        """
        import requests
        resp = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature},
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["response"].strip()


# ---------------------------------------------------------------------------
# Domain agent
# ---------------------------------------------------------------------------

class DomainAgent:
    """
    A single domain-specialist agent. Owns one domain, reasons within it,
    writes claims to the shared substrate.

    Usage:
        substrate = Substrate("epistemic.db")
        client = ModelClient("qwen2.5:14b")
        agent = DomainAgent("computer_science", substrate, client)
        agent.reason("How do ant colony optimization algorithms work?")
    """

    def __init__(
        self,
        domain_name: str,
        substrate: Substrate,
        model_client: ModelClient,
    ):
        if domain_name not in DOMAINS:
            raise ValueError(f"Unknown domain: {domain_name}. Available: {list(DOMAINS.keys())}")

        self.domain = DOMAINS[domain_name]
        self.agent_id = f"agent_{domain_name}_{uuid.uuid4().hex[:8]}"
        self.substrate = substrate
        self.model = model_client
        print(f"🤖 Agent initialized: {self.agent_id} (domain: {self.domain.name})")

    def reason(self, query: str, context: Optional[str] = None) -> list[str]:
        """
        Main entry point. Takes a query, produces claims, writes them
        to the substrate. Returns the list of claim IDs that were written.

        The prompt is structured to:
          1. Ground the agent in its domain definition
          2. Enforce boundary rules
          3. Ask for explicit confidence scores
          4. Require reasoning traces (not just conclusions)
        """
        prompt = self._build_prompt(query, context)
        print(f"🔍 {self.domain.name}: reasoning on query...")

        raw_response = self.model.generate(prompt)
        print(f"📝 {self.domain.name}: parsing response...")

        claims = self._parse_claims(raw_response)
        claim_ids = []

        for claim in claims:
            cid = self.substrate.write_claim(
                agent_id=self.agent_id,
                domain=self.domain.name,
                claim_text=claim["text"],
                confidence=claim["confidence"],
                reasoning_trace=claim.get("reasoning", ""),
            )
            # write_claim now returns SubstrateEvent; extract event_id
            if hasattr(cid, 'event_id'):
                cid = cid.event_id
            claim_ids.append(cid)
            print(f"   ✓ Claim written (conf={claim['confidence']:.2f}): {claim['text'][:80]}...")

        print(f"📦 {self.domain.name}: {len(claim_ids)} claims written to substrate")
        return claim_ids

    # -----------------------------------------------------------------
    # Prompt construction
    # -----------------------------------------------------------------

    def _build_prompt(self, query: str, context: Optional[str] = None) -> str:
        """
        Build the reasoning prompt. This is where domain boundaries
        get enforced — at the prompt level. The adversarial layer will
        verify whether the model actually respected them.
        """
        boundary_text = "\n".join(f"  - {r}" for r in self.domain.boundary_rules)
        concepts_text = ", ".join(self.domain.key_concepts)

        prompt = f"""You are an expert reasoning agent specialized in {self.domain.name}.

DOMAIN: {self.domain.description}

KEY CONCEPTS: {concepts_text}

BOUNDARY RULES (you must not violate these):
{boundary_text}

TASK: Analyze the following query and produce a set of distinct claims.
Each claim must be:
  - A single, falsifiable statement within your domain
  - Accompanied by a confidence score (0.0 to 1.0) reflecting how confident
    you are based on your domain knowledge
  - Accompanied by a brief reasoning trace explaining WHY you believe it

QUERY: {query}
"""

        if context:
            prompt += f"\nADDITIONAL CONTEXT:\n{context}\n"

        prompt += """
FORMAT YOUR RESPONSE as a structured list. Each claim must follow this exact format:

CLAIM: [your claim statement]
CONFIDENCE: [a number between 0.0 and 1.0]
REASONING: [1-3 sentences explaining your reasoning]
---

Produce between 3 and 7 claims. Be precise. Stay within your domain boundaries.
"""
        return prompt

    # -----------------------------------------------------------------
    # Response parsing
    # -----------------------------------------------------------------

    def _parse_claims(self, raw_response: str) -> list[dict]:
        """
        Parse the model's structured response into claim objects.
        Robust to minor formatting variations — models don't always
        follow instructions perfectly.
        """
        claims = []
        current = {}

        for line in raw_response.split("\n"):
            line = line.strip()

            if line.startswith("CLAIM:"):
                # If we already have a complete claim buffered, save it
                if current and "text" in current and "confidence" in current:
                    claims.append(current)
                current = {"text": line[len("CLAIM:"):].strip()}

            elif line.startswith("CONFIDENCE:") and current:
                raw_conf = line[len("CONFIDENCE:"):].strip()
                current["confidence"] = self._parse_confidence(raw_conf)

            elif line.startswith("REASONING:") and current:
                current["reasoning"] = line[len("REASONING:"):].strip()

            elif line == "---":
                if current and "text" in current and "confidence" in current:
                    claims.append(current)
                    current = {}

        # Catch the last claim if there's no trailing ---
        if current and "text" in current and "confidence" in current:
            claims.append(current)

        # Fallback: if parsing produced nothing, treat the whole response
        # as a single low-confidence claim so we don't silently drop output
        if not claims:
            print(f"⚠️  {self.domain.name}: structured parsing failed, falling back to raw response")
            claims = [{
                "text": raw_response[:500],
                "confidence": 0.2,
                "reasoning": "Fallback: model did not follow structured format",
            }]

        return claims

    def _parse_confidence(self, raw: str) -> float:
        """
        Extract a float from whatever the model gave us.
        Handles "0.7", "0.7/1.0", "70%", plain garbage, etc.
        """
        raw = raw.strip().rstrip(".")
        # Strip trailing /1.0 or /1
        if "/" in raw:
            raw = raw.split("/")[0].strip()
        # Strip % sign
        raw = raw.replace("%", "").strip()

        try:
            val = float(raw)
            # If they wrote 70 meaning 70%, normalize
            if val > 1.0:
                val = val / 100.0
            return max(0.0, min(1.0, val))
        except ValueError:
            return 0.3  # Default low confidence if we can't parse it