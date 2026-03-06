#!/usr/bin/env bash
# setup.sh — Install ragas evaluation dependencies for OpenClaw ragas-eval skill
set -euo pipefail

# ── Pretty output ─────────────────────────────────────────────────────────────
BOLD="\033[1m"; RESET="\033[0m"
GREEN="\033[32m"; YELLOW="\033[33m"; RED="\033[31m"

ok()   { echo -e "${GREEN}✓${RESET} $*"; }
warn() { echo -e "${YELLOW}⚠${RESET}  $*"; }
info() { echo -e "${BOLD}→${RESET} $*"; }
err()  { echo -e "${RED}✗${RESET} $*" >&2; }

echo -e "\n${BOLD}rag-eval — Dependency Setup${RESET}"
echo "────────────────────────────────────────────────"

# ── Virtual environment recommendation ────────────────────────────────────────
if [[ -z "${VIRTUAL_ENV:-}" ]]; then
    warn "No virtual environment detected. Global pip install will modify your system Python."
    echo "  Recommended: python3 -m venv .venv && source .venv/bin/activate && bash scripts/setup.sh"
    echo ""
    # Give user 3 seconds to Ctrl-C
    info "Continuing with global install in 3 seconds... (Ctrl-C to abort)"
    sleep 3
fi

# ── Python version check ──────────────────────────────────────────────────────
PYTHON=$(command -v python3 2>/dev/null || command -v python 2>/dev/null || true)
if [[ -z "$PYTHON" ]]; then
    err "Python 3.10+ is required but was not found in PATH."
    err "Install from: https://www.python.org/downloads/"
    exit 1
fi

PY_VER=$("$PYTHON" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)

if [[ "$PY_MAJOR" -lt 3 || ( "$PY_MAJOR" -eq 3 && "$PY_MINOR" -lt 10 ) ]]; then
    err "Python 3.10+ required; found Python $PY_VER."
    err "Upgrade at: https://www.python.org/downloads/"
    exit 1
fi
ok "Python $PY_VER"

# ── Upgrade pip silently ──────────────────────────────────────────────────────
info "Upgrading pip..."
"$PYTHON" -m pip install --quiet --upgrade pip
ok "pip up to date"

# ── Core ragas packages ───────────────────────────────────────────────────────
info "Installing ragas + datasets..."
"$PYTHON" -m pip install --quiet "ragas>=0.2.0" "datasets>=2.0"
ok "ragas + datasets"

# ── LangChain integrations (required for LLM-as-judge) ───────────────────────
info "Installing LangChain core + integrations..."
"$PYTHON" -m pip install --quiet \
    "langchain-core>=0.3" \
    "langchain-community>=0.3" \
    "langchain-openai>=0.2" \
    "langchain-anthropic>=0.2"
ok "langchain-core, langchain-community, langchain-openai, langchain-anthropic"

# ── Optional: HuggingFace offline embeddings ─────────────────────────────────
info "Installing optional offline embeddings (HuggingFace)..."
if "$PYTHON" -m pip install --quiet langchain-huggingface sentence-transformers 2>/dev/null; then
    ok "langchain-huggingface + sentence-transformers (offline AnswerRelevancy enabled)"
else
    warn "HuggingFace embeddings not installed — set OPENAI_API_KEY for AnswerRelevancy metric"
    echo "  To install manually: pip install langchain-huggingface sentence-transformers"
fi

# ── API key status ────────────────────────────────────────────────────────────
echo ""
echo "────────────────────────────────────────────────"
echo -e "${BOLD}API Key Status${RESET}"

if [[ -n "${OPENAI_API_KEY:-}" ]]; then
    ok "OPENAI_API_KEY is set (LLM judge + embeddings ready)"
else
    warn "OPENAI_API_KEY not set"
    echo "  → export OPENAI_API_KEY=sk-..."
fi

if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
    ok "ANTHROPIC_API_KEY is set (Claude Haiku judge ready)"
else
    warn "ANTHROPIC_API_KEY not set"
    echo "  → export ANTHROPIC_API_KEY=sk-ant-..."
fi

if [[ -z "${OPENAI_API_KEY:-}" && -z "${ANTHROPIC_API_KEY:-}" ]]; then
    err "At least one API key is required for LLM-as-judge scoring."
    echo "  Ragas uses an LLM internally to evaluate faithfulness and relevancy."
    echo ""
fi

# ── Verify ragas import ───────────────────────────────────────────────────────
info "Verifying ragas installation..."
if "$PYTHON" -c "
import ragas
from ragas.dataset_schema import SingleTurnSample, EvaluationDataset
from ragas.metrics import Faithfulness, AnswerRelevancy
print('OK')
" 2>/dev/null | grep -q OK; then
    ok "ragas imports successfully"
else
    err "ragas import check failed. Try: pip install --upgrade 'ragas>=0.2.0'"
    exit 1
fi

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}Setup complete!${RESET}"
echo ""
echo "Quick test (requires OPENAI_API_KEY or ANTHROPIC_API_KEY):"
echo "  echo '{\"question\":\"What is RAG?\",\"answer\":\"RAG combines retrieval with generation.\",\"contexts\":[\"RAG stands for Retrieval-Augmented Generation.\"]}' | python3 scripts/run_eval.py"
echo ""
