#!/usr/bin/env python3
"""
JurisFR — Answer a legal question using RAG (retrieve + generate prompt).
Outputs a formatted prompt with retrieved sources for the LLM to answer.
"""

import sys
import json
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))
from search import hybrid_search, bm25_search, format_results

try:
    from search_jurisprudence import search as juri_search
    _JURI_AVAILABLE = True
except ImportError:
    _JURI_AVAILABLE = False
    def juri_search(*args, **kwargs):
        return []

JURI_SOURCES = {
    "cass-ce": [
        "antoinejeannot/jurisprudence:cour_de_cassation",
        "artefactory/Argimi-Legal-French-Jurisprudence:cetat",
    ],
    "tj": ["antoinejeannot/jurisprudence:tribunal_judiciaire"],
    "all": None,
}



SYSTEM_PROMPT = """Tu es JurisFR, un assistant juridique spécialisé en droit français.

## Règles absolues
1. Réponds UNIQUEMENT sur la base des extraits fournis ci-dessous.
2. Cite CHAQUE affirmation juridique avec sa source :
   - textes : [Code civil, art. 1240] ou [Code de commerce, art. L.123-1]
   - jurisprudence : [Cour de cassation — chambre — date — n°/ECLI] ou [Conseil d’État — formation — date — ECLI/identifiant]
3. Si les extraits ne permettent pas de répondre → dis-le clairement ("Les sources disponibles ne couvrent pas ce point").
4. Ne cite JAMAIS un article que tu n'as pas dans les extraits.
5. Structure ta réponse : Principe → Application → Limites/exceptions → Sources utilisées.

## Tonalité
- Adapte-toi au niveau de la question :
  - Question simple/grand public → langage clair, vulgarisé, exemples concrets
  - Question technique/pro → vocabulaire juridique précis, références complètes
- En cas de doute, pose une question de clarification.

## Disclaimer (obligatoire en fin de réponse)
> ⚖️ *Information juridique à caractère général. Ne constitue pas un conseil juridique personnalisé. Pour une situation spécifique, consultez un professionnel du droit.*
"""


def _format_jurisprudence_results(results: list[dict], max_chars: int = 3200) -> str:
    lines = []
    for r in results:
        jur = (r.get("jurisdiction") or "").strip()
        date = (r.get("decision_date") or "").strip()
        chamber = (r.get("chamber") or "").strip()
        formation = (r.get("formation") or "").strip()
        ident = (r.get("ecli") or "").strip() or (r.get("numbers") or "").strip() or (r.get("doc_id") or "").strip()

        parts = [p for p in [jur, chamber or None, formation or None, date or None, ident or None] if p]
        label = " — ".join(parts) if parts else (r.get("doc_id") or "Décision")

        text = (r.get("text") or r.get("excerpt") or "").strip()
        if len(text) > max_chars:
            text = text[:max_chars] + "…"

        lines.append(f"### Source: [{label}]\n{text}\n")

    return "\n".join(lines).strip()


def build_rag_prompt(
    question: str,
    top_k: int = 5,
    top_k_jurisprudence: int | None = None,
    juris: str = "all",
) -> dict:
    """Build a complete RAG prompt with retrieved sources (codes + jurisprudence).

    If no reliable sources are found, the prompt instructs the LLM to ask clarifying questions
    and explicitly avoid making legal assertions.
    """
    top_k_jurisprudence = top_k if top_k_jurisprudence is None else top_k_jurisprudence

    # Codes: hybrid search, fallback to BM25 only
    try:
        code_results = hybrid_search(question, top_k=top_k)
    except Exception:
        code_results = bm25_search(question, top_k=top_k)

    # Jurisprudence: SQLite FTS (optionnel — module présent uniquement si corpus jurisprudentiel installé)
    juri_results = []
    if _JURI_AVAILABLE:
        try:
            sources_filter = JURI_SOURCES.get(juris, None)
            juri_results = juri_search(question, top_k=top_k_jurisprudence, sources=sources_filter)
        except Exception:
            juri_results = []

    sources_blocks = []
    if code_results:
        sources_blocks.append("## Textes (codes)\n" + format_results(code_results, verbose=True))
    if juri_results:
        sources_blocks.append("## Jurisprudence (Cass / Conseil d’État)\n" + _format_jurisprudence_results(juri_results))

    results_any = (len(code_results) + len(juri_results))
    if results_any == 0:
        sources_text = "(Aucune source pertinente retrouvée.)"
        extra = "\n\nIMPORTANT: Tu dois poser 1–3 questions de clarification. Ne donne pas de réponse de fond sans sources."
    else:
        sources_text = "\n\n".join(sources_blocks)
        extra = ""

    user_prompt = f"""## Question juridique
{question}

## Sources juridiques retrouvées
{sources_text}{extra}

## Instructions
Réponds à la question en t'appuyant exclusivement sur les sources ci-dessus. Cite chaque source utilisée. Adapte le niveau de langage à la question."""

    # Tag sources with kind for downstream tooling
    sources = (
        [{"kind": "code", **r} for r in code_results]
        + [{"kind": "jurisprudence", **r} for r in juri_results]
    )

    return {
        "system": SYSTEM_PROMPT,
        "user": user_prompt,
        "sources_count": results_any,
        "sources": sources,
        "sources_codes": code_results,
        "sources_jurisprudence": juri_results,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ask.py <question> [--json]")
        sys.exit(1)

    as_json = False
    args = sys.argv[1:]
    if "--json" in args:
        as_json = True
        args.remove("--json")

    question = " ".join(args)
    # Optional: --juris=cass-ce|tj|all
    juris = "all"
    if "--juris" in args:
        i = args.index("--juris")
        if i + 1 < len(args):
            juris = args[i + 1]
            del args[i:i+2]

    result = build_rag_prompt(question, juris=juris)

    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        sys.exit(0)

    print("=== SYSTEM PROMPT ===")
    print(result["system"])
    print(f"\n=== USER PROMPT ({result['sources_count']} sources) ===")
    print(result["user"])
