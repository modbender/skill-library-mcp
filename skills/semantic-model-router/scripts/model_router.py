"""
Semantic Model Orchestrator — model_router.py
=============================================
Entry point for the ClawHub / OpenClaw Skill.
Routes incoming queries to the optimal LLM tier based on semantic similarity
and a pre-trained Logistic Regression classifier.

Tiers:
  ELITE    → Best model in each provider (default: anthropic/claude-sonnet-4-6)
  BALANCED → Mid-range model            (default: openai/gpt-4o-mini)
  BASIC    → Ultra-cheap model          (default: deepseek/deepseek-chat)

Supported providers: Anthropic, OpenAI, Google, DeepSeek, xAI (Grok)

Dependencies (optional — falls back to keyword matching if missing):
  sentence-transformers, numpy
"""

import re
import os
import json

# ── Optional heavy imports ─────────────────────────────────────────────────────
try:
    from sentence_transformers import SentenceTransformer, util
    import numpy as np
    import joblib
    _HAS_SEMANTIC = True
except ImportError:
    _HAS_SEMANTIC = False

# Try to load text-based weights as a portable fallback
try:
    try:
        from scripts import model_weights
    except ImportError:
        import model_weights
    _HAS_WEIGHTS = True
except ImportError:
    _HAS_WEIGHTS = False


# ── Model Catalog ──────────────────────────────────────────────────────────────
# Pricing source: Official API docs (verified Feb 2026)
# Format: "provider/model-id": (input_per_1m, output_per_1m)
# The catalog stores OUTPUT token price as the primary cost signal (the dominant cost).
# Input prices are noted in comments for transparency.
MODEL_CATALOG: dict[str, tuple[float, float]] = {
    # ── Anthropic (source: platform.claude.com/docs/en/about-claude/pricing) ──
    # claude-sonnet-4-6: $3.00 input / $15.00 output per 1M tokens
    "anthropic/claude-sonnet-4-6":         (3.00, 15.00),
    # claude-opus-4-5: $5.00 input / $25.00 output per 1M tokens
    "anthropic/claude-opus-4-5":           (5.00, 25.00),
    # claude-haiku-4-5: $0.80 input / $4.00 output per 1M tokens
    "anthropic/claude-haiku-4-5":          (0.80,  4.00),
    # claude-3-5-sonnet: $3.00 input / $15.00 output (stable alias)
    "anthropic/claude-3-5-sonnet-latest":  (3.00, 15.00),

    # ── OpenAI (source: openai.com/api/pricing) ───────────────────────────────
    # gpt-5: $1.25 input / $10.00 output per 1M tokens
    "openai/gpt-5":                        (1.25, 10.00),
    # gpt-4o: $2.50 input / $10.00 output per 1M tokens
    "openai/gpt-4o":                       (2.50, 10.00),
    # gpt-4o-mini: $0.15 input / $0.60 output per 1M tokens
    "openai/gpt-4o-mini":                  (0.15,  0.60),
    # o3: $2.00 input / $8.00 output per 1M tokens (after June 2025 price cut)
    "openai/o3":                           (2.00,  8.00),
    # o4-mini: $1.10 input / $4.40 output per 1M tokens
    "openai/o4-mini":                      (1.10,  4.40),

    # ── Google (source: ai.google.dev/gemini-api/docs/pricing) ───────────────
    # gemini-3.0-pro: Preview model (pricing not yet finalized, using Gemini 2.5 Pro as reference)
    "google/gemini-3.0-pro":               (1.25, 10.00),
    # gemini-2.5-pro: $1.25 input (≤200K ctx) / $10.00 output per 1M tokens
    "google/gemini-2.5-pro":               (1.25, 10.00),
    # gemini-2.5-flash: Paid tier (estimated ~$0.30 input / $2.50 output)
    "google/gemini-2.5-flash":             (0.30,  2.50),
    # gemini-2.5-flash-lite: $0.10 input / $0.40 output per 1M tokens
    "google/gemini-2.5-flash-lite":        (0.10,  0.40),

    # ── DeepSeek (source: api-docs.deepseek.com/quick_start/pricing) ─────────
    # deepseek-chat (V3.2): $0.28 input (cache miss) / $0.42 output per 1M tokens
    "deepseek/deepseek-chat":              (0.28,  0.42),
    # deepseek-reasoner (V3.2): $0.28 input (cache miss) / $0.42 output per 1M tokens
    "deepseek/deepseek-reasoner":          (0.28,  0.42),

    # ── xAI / Grok (source: x.ai/api) ────────────────────────────────────────
    # grok-3: $3.00 input / $15.00 output per 1M tokens
    "xai/grok-3":                          (3.00, 15.00),
    # grok-3-mini: $0.30 input / $0.50 output per 1M tokens
    "xai/grok-3-mini":                     (0.30,  0.50),
}

def _catalog_avg(model: str) -> float:
    """Return a blended avg cost (50% input + 50% output) for display purposes."""
    if model in MODEL_CATALOG:
        i, o = MODEL_CATALOG[model]
        return round((i + o) / 2, 4)
    return 1.0

# ── Default Tier → Model Assignments ──────────────────────────────────────────
DEFAULT_MODELS: dict[str, str] = {
    "ELITE":    "anthropic/claude-sonnet-4-6",
    "BALANCED": "openai/gpt-4o-mini",
    "BASIC":    "deepseek/deepseek-chat",
}

# Baseline cost: what a user WOULD pay using a single top model for everything
# Reference: GPT-5.2 / Gemini 3.0 Pro level ≈ $10–15/M tokens
BASELINE_COST_PER_M = 10.0


class ModelRouter:
    """
    Intelligent LLM Model Router for OpenClaw / ClawHub.

    Classifies a natural-language query into ELITE / BALANCED / BASIC
    using a pre-trained ML classifier (via text-based weights) with
    semantic embeddings as fallback, and keyword matching as last resort.

    Usage
    -----
    router = ModelRouter()
    result = router.route("Design a distributed caching layer for a fintech platform.")
    print(result["report"])

    To override specific tier models:
    router = ModelRouter(elite_model="openai/gpt-5.2", basic_model="google/gemini-2.5-flash-lite")
    """

    def __init__(
        self,
        elite_model:    str = DEFAULT_MODELS["ELITE"],
        balanced_model: str = DEFAULT_MODELS["BALANCED"],
        basic_model:    str = DEFAULT_MODELS["BASIC"],
        baseline_cost:  float = BASELINE_COST_PER_M,
        history_file:   str = "query_history.json",
    ):
        self.mapping = {
            "ELITE":    elite_model,
            "BALANCED": balanced_model,
            "BASIC":    basic_model,
        }
        self.baseline_cost = baseline_cost
        self.history_file  = history_file
        self.encoder       = None
        self.classifier    = None
        self.intent_embeddings: dict = {}

        # ── Intent Matrix ──────────────────────────────────────────────────────
        self.intent_matrix: dict[str, list[str]] = {
            "ELITE": [
                # English
                "architecture design", "complex algorithm", "system optimization",
                "precision reasoning", "heavy coding", "security audit",
                "high-frequency trading", "latency optimization", "financial modeling",
                "distributed systems", "database internals", "kernel programming",
                "implement a", "write a program", "write a function",
                "build a system", "design a", "analyze the complexity",
                "debug this code", "refactor", "microservice", "proof of concept",
                "machine learning model", "neural network", "deep learning",
                # Chinese
                "精密推理", "架構設計", "演算法開發", "安全審查",
                "複雜邏輯開發", "深度性能優化", "分散式架構",
            ],
            "BALANCED": [
                # English
                "data extraction", "summarization", "summarize", "translation",
                "translate", "creative writing", "email drafting", "bug fixing",
                "code explanation", "test case generation", "web scraping",
                "text classification", "format conversion", "explain",
                "what is", "how does", "list the", "give me an example",
                "rewrite", "simplify", "extract", "compare",
                # Chinese
                "摘要", "內容整理", "翻譯", "創意寫作",
                "日常郵件", "程式碼解釋", "格式轉換",
            ],
            "BASIC": [
                # English
                "hello", "hi", "hey", "good morning", "how are you",
                "small talk", "weather", "simple math", "what time",
                "tell me a joke", "fun fact", "status check", "who are you",
                "thank you", "thanks", "bye", "goodbye", "set a timer",
                # Chinese
                "日常對話", "閒聊", "天氣查詢", "簡單運算",
                "狀態檢查", "問候", "講笑話",
            ],
        }

        # ── Load encoder (optional) ────────────────────────────────────────────
        if _HAS_SEMANTIC:
            try:
                self.encoder = SentenceTransformer("all-MiniLM-L6-v2")

                # Priority: binary joblib > text weights > semantic embeddings
                model_path = os.path.join(os.path.dirname(__file__), "classifier.joblib")
                if os.path.exists(model_path):
                    self.classifier = joblib.load(model_path)
                elif _HAS_WEIGHTS:
                    self.classifier = self._create_manual_classifier()
                else:
                    self._prepare_embeddings()
            except Exception as exc:
                print(f"[ModelRouter] Encoder/Classifier unavailable: {exc}")

    # ── Classifier from text weights (ClawHub compatible) ─────────────────────

    def _create_manual_classifier(self):
        """Creates a classifier from the text-based model_weights.py."""
        class ManualClassifier:
            def __init__(self, weights, intercept, classes):
                self.coef_      = np.array(weights)
                self.intercept_ = np.array(intercept)
                self.classes_   = np.array(classes)

            def predict_proba(self, X):
                if len(X.shape) == 1:
                    X = X.reshape(1, -1)
                scores     = np.dot(X, self.coef_.T) + self.intercept_
                exp_scores = np.exp(scores - np.max(scores, axis=1, keepdims=True))
                return exp_scores / np.sum(exp_scores, axis=1, keepdims=True)

        return ManualClassifier(model_weights.COEF, model_weights.INTERCEPT, model_weights.CLASSES)

    # ── Embedding helpers ──────────────────────────────────────────────────────

    def _prepare_embeddings(self) -> None:
        """Pre-compute per-tier embedding matrices from the intent matrix."""
        self.intent_embeddings = {}
        for tier, phrases in self.intent_matrix.items():
            self.intent_embeddings[tier] = self.encoder.encode(
                phrases, convert_to_tensor=True
            )

    # ── Core routing ───────────────────────────────────────────────────────────

    def route(self, query: str) -> dict:
        """
        Classify *query* and return the recommended model with cost metrics.

        Returns
        -------
        {
            "tier":       "ELITE" | "BALANCED" | "BASIC",
            "model":      "<provider>/<model-id>",
            "confidence": float,          # 0–1
            "metrics": {
                "method":       "ml" | "semantic" | "keyword",
                "cost_per_m":   float,    # USD per 1M tokens
                "baseline_per_m": float,
                "saved_pct":    float,    # % saved vs baseline
            },
            "report": str,                # OpenClaw-style one-liner
        }
        """
        best_tier  = "BASIC"
        confidence = 1.0
        method     = "keyword"

        if self.encoder and self.classifier:
            best_tier, confidence = self._ml_route(query)
            method = "ml"
        elif self.encoder and self.intent_embeddings:
            best_tier, confidence = self._semantic_route(query)
            method = "semantic"
        else:
            best_tier = self._keyword_route(query)

        self._log_query(query, best_tier)

        model           = self.mapping[best_tier]
        prices          = MODEL_CATALOG.get(model, (1.0, 1.0))
        input_cost      = prices[0]
        output_cost     = prices[1]
        # Use output price as cost signal (dominant in most workloads)
        cost            = output_cost
        saved           = max(0.0, self.baseline_cost - cost)
        saved_pct       = (saved / self.baseline_cost) * 100 if self.baseline_cost > 0 else 0

        return {
            "tier":       best_tier,
            "model":      model,
            "confidence": confidence,
            "metrics": {
                "method":          method,
                "input_per_m":     input_cost,
                "output_per_m":    output_cost,
                "baseline_per_m":  round(self.baseline_cost, 4),
                "saved_pct":       round(saved_pct, 1),
            },
            "report": (
                f"[ClawRouter] {model} ({best_tier}, {method}, conf={confidence:.2f})\n"
                f"             In: ${input_cost}/M | Out: ${output_cost}/M | Baseline: ${self.baseline_cost}/M | Saved: {saved_pct:.1f}%"
            ),
        }

    def _ml_route(self, query: str) -> tuple[str, float]:
        """Return (tier, confidence) using the trained LogisticRegression classifier."""
        q_emb    = self.encoder.encode([query])
        prob     = self.classifier.predict_proba(q_emb)[0]
        max_idx  = int(np.argmax(prob))
        best_tier = str(self.classifier.classes_[max_idx])
        max_prob  = float(prob[max_idx])

        if max_prob < 0.40:
            best_tier = "BASIC"

        return best_tier, round(max_prob, 4)

    def _semantic_route(self, query: str) -> tuple[str, float]:
        """Return (tier, confidence) using max cosine-similarity per tier."""
        q_emb     = self.encoder.encode(query, convert_to_tensor=True)
        best_tier = "BASIC"
        max_sim   = 0.0

        for tier, cluster in self.intent_embeddings.items():
            sims = util.cos_sim(q_emb, cluster)[0]
            peak = float(sims.max())
            if peak > max_sim:
                max_sim   = peak
                best_tier = tier

        if max_sim < 0.40:
            best_tier = "BASIC"

        return best_tier, round(max_sim, 4)

    def _keyword_route(self, query: str) -> str:
        """Rule-based fallback when sentence-transformers is not available."""
        lower = query.lower()
        for tier in ("ELITE", "BALANCED"):
            for kw in self.intent_matrix[tier]:
                if re.search(re.escape(kw.lower()), lower):
                    return tier
        return "BASIC"

    # ── Model Catalog API ──────────────────────────────────────────────────────

    @staticmethod
    def list_models() -> dict[str, tuple[float, float]]:
        """Return the full supported model catalog with (input, output) prices per 1M tokens."""
        return dict(MODEL_CATALOG)

    def set_model(self, tier: str, model: str) -> None:
        """
        Override the model for a specific tier at runtime.

        Parameters
        ----------
        tier  : "ELITE", "BALANCED", or "BASIC"
        model : a model ID from MODEL_CATALOG, e.g. "openai/gpt-5.2"

        Raises
        ------
        ValueError if tier or model is unknown.
        """
        if tier not in self.mapping:
            raise ValueError(f"Unknown tier '{tier}'. Choose from: {list(self.mapping)}")
        if model not in MODEL_CATALOG:
            raise ValueError(
                f"Unknown model '{model}'.\n"
                f"Available models:\n" + "\n".join(f"  {m}" for m in MODEL_CATALOG)
            )
        self.mapping[tier] = model

    # ── Rolling Adjustment API ─────────────────────────────────────────────────

    def add_keywords(self, tier: str, keywords: list[str]) -> list[str]:
        """
        Add new routing signals to *tier* and refresh embeddings.

        Returns the list of keywords that were actually added (skips duplicates).
        """
        if tier not in self.intent_matrix:
            raise ValueError(f"Unknown tier '{tier}'.")

        added = [kw for kw in keywords if kw not in self.intent_matrix[tier]]
        self.intent_matrix[tier].extend(added)

        if added and self.encoder:
            self._prepare_embeddings()

        return added

    def refine_keywords(self) -> str:
        """Read collected query history and return a status string."""
        if not os.path.exists(self.history_file):
            return "No history found."
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
            return f"History contains {len(history)} queries ready for refinement."
        except Exception:
            return "History file unreadable."

    # ── Logging (internal) ─────────────────────────────────────────────────────

    def _log_query(self, query: str, tier: str) -> None:
        """Append the query + tier to the history file for offline analysis."""
        try:
            history: list = []
            if os.path.exists(self.history_file):
                with open(self.history_file, "r", encoding="utf-8") as f:
                    raw = f.read().strip()
                    if raw:
                        history = json.loads(raw)
            history.append({"query": query, "tier": tier})
            if len(history) > 1000:
                history = history[-1000:]
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception:
            pass


# ── CLI & Smoke Test ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Semantic Model Router CLI")
    parser.add_argument("query", nargs="*", help="Query to route. Omit for smoke test.")
    parser.add_argument("--elite",    default=DEFAULT_MODELS["ELITE"],    help="Override ELITE model")
    parser.add_argument("--balanced", default=DEFAULT_MODELS["BALANCED"], help="Override BALANCED model")
    parser.add_argument("--basic",    default=DEFAULT_MODELS["BASIC"],    help="Override BASIC model")
    parser.add_argument("--list-models", action="store_true", help="List all supported models")
    args = parser.parse_args()

    if args.list_models:
        print("\n📦 Supported Models (verified Feb 2026):\n")
        print(f"  {'Model':<45} {'Input/1M':>10}  {'Output/1M':>10}")
        print("─" * 70)
        for m, (inp, out) in sorted(MODEL_CATALOG.items(), key=lambda x: x[1][1]):
            print(f"  {m:<45} ${inp:>9}  ${out:>9}")
        exit(0)

    router = ModelRouter(
        elite_model=args.elite,
        balanced_model=args.balanced,
        basic_model=args.basic,
    )

    if args.query:
        res = router.route(" ".join(args.query))
        print(res["report"])
    else:
        probes = [
            ("How are you doing today?",                                     "BASIC"),
            ("Tell me a joke.",                                               "BASIC"),
            ("Summarize this article in three bullet points.",               "BALANCED"),
            ("Translate this paragraph from English to French.",             "BALANCED"),
            ("Implement a thread-safe LRU cache in Python.",                  "ELITE"),
            ("Design a microservices architecture for a payments platform.", "ELITE"),
            ("Analyze the time complexity of quicksort and heapsort.",       "ELITE"),
        ]

        width = 50
        print(f"\n{'Query':<{width}} {'Predicted':<10} {'Expected':<10} ✓  Cost Info")
        print("─" * 100)
        for text, expected in probes:
            res = router.route(text)
            ok  = "✓" if res["tier"] == expected else "✗"
            m   = res["metrics"]
            print(
                f"{text[:width-1]:<{width}} {res['tier']:<10} {expected:<10} {ok}"
                f"  In:${m['input_per_m']}/M Out:${m['output_per_m']}/M  saved {m['saved_pct']}%"
            )
