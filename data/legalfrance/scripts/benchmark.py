#!/usr/bin/env python3
"""JurisFR — Benchmark A/B: with RAG vs without RAG.

Produces a JSON report:
- retrieval score (did we retrieve the expected articles?)
- prompts ready to be fed to an LLM (with/without sources)

Note: V1 focuses on codes only (no jurisprudence).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ask import build_rag_prompt


# 20 normalized test questions covering Code civil + Code de commerce.
# expected_refs are article numbers as they appear in the dataset "number" field.
TEST_QUESTIONS = [
    {"id": 1, "question": "Quelles sont les conditions de la responsabilité civile délictuelle ?", "domain": "Code civil - Responsabilité", "expected_refs": ["1240", "1241"], "difficulty": "easy"},
    {"id": 2, "question": "Un parent est-il responsable des dommages causés par son enfant mineur ?", "domain": "Code civil - Responsabilité", "expected_refs": ["1242"], "difficulty": "medium"},
    {"id": 3, "question": "Quelles sont les conditions de validité d'un contrat ?", "domain": "Code civil - Contrats", "expected_refs": ["1128"], "difficulty": "easy"},
    {"id": 4, "question": "Qu'est-ce que la force majeure en droit des contrats ?", "domain": "Code civil - Contrats", "expected_refs": ["1218"], "difficulty": "medium"},
    {"id": 5, "question": "Dans quels cas peut-on annuler un contrat pour vice du consentement ?", "domain": "Code civil - Contrats", "expected_refs": ["1130", "1131", "1132", "1137", "1140"], "difficulty": "medium"},
    {"id": 6, "question": "Quels sont les droits d'un propriétaire sur son bien immobilier ?", "domain": "Code civil - Propriété", "expected_refs": ["544"], "difficulty": "easy"},
    {"id": 7, "question": "Comment fonctionne la prescription acquisitive (usucapion) ?", "domain": "Code civil - Propriété", "expected_refs": ["2258", "2272"], "difficulty": "hard"},
    {"id": 8, "question": "Quelles sont les conditions pour se marier en France ?", "domain": "Code civil - Famille", "expected_refs": ["144", "146"], "difficulty": "easy"},
    {"id": 9, "question": "Quels sont les différents régimes matrimoniaux ?", "domain": "Code civil - Famille", "expected_refs": ["1393", "1400"], "difficulty": "medium"},
    {"id": 10, "question": "Quel est l'ordre des héritiers en l'absence de testament ?", "domain": "Code civil - Successions", "expected_refs": ["734", "735"], "difficulty": "medium"},
    {"id": 11, "question": "Quel est le capital social minimum pour créer une SARL ?", "domain": "Code de commerce - Sociétés", "expected_refs": ["L223-2"], "difficulty": "easy"},
    {"id": 12, "question": "Quelles sont les obligations du gérant d'une SARL ?", "domain": "Code de commerce - Sociétés", "expected_refs": ["L223-18", "L223-22"], "difficulty": "medium"},
    {"id": 13, "question": "Comment fonctionne la procédure de redressement judiciaire ?", "domain": "Code de commerce - Procédures collectives", "expected_refs": ["L631-1"], "difficulty": "hard"},
    {"id": 14, "question": "Qu'est-ce que l'enrichissement injustifié ?", "domain": "Code civil - Quasi-contrats", "expected_refs": ["1303"], "difficulty": "medium"},
    {"id": 15, "question": "Quels sont les délais de prescription en matière civile ?", "domain": "Code civil - Prescription", "expected_refs": ["2224"], "difficulty": "easy"},
    {"id": 16, "question": "Qu'est-ce qu'un fonds de commerce et quels éléments le composent ?", "domain": "Code de commerce - Fonds de commerce", "expected_refs": ["L141-5"], "difficulty": "medium"},
    {"id": 17, "question": "Quelles sont les obligations du bailleur dans un contrat de bail ?", "domain": "Code civil - Baux", "expected_refs": ["1719", "1720"], "difficulty": "medium"},
    {"id": 18, "question": "Mon voisin fait du bruit tous les soirs, que dit la loi ?", "domain": "Code civil - Troubles de voisinage", "expected_refs": ["544"], "difficulty": "easy"},
    {"id": 19, "question": "J'ai acheté un produit défectueux, quels sont mes recours ?", "domain": "Code civil - Garanties", "expected_refs": ["1641", "1644"], "difficulty": "medium"},
    {"id": 20, "question": "Je veux créer une entreprise seul, quelle forme juridique choisir ?", "domain": "Code de commerce - Création d'entreprise", "expected_refs": ["L223-1"], "difficulty": "easy"},
]


def run_benchmark(output_path: str | None = None):
    results = []

    for q in TEST_QUESTIONS:
        print(f"[{q['id']}/20] {q['question'][:70]}...")

        try:
            rag = build_rag_prompt(q["question"])  # includes sources

            numbers = [str(s.get("number", "")).lower() for s in rag["sources"]]
            refs_found = []
            refs_missing = []
            for ref in q["expected_refs"]:
                if ref.lower() in numbers:
                    refs_found.append(ref)
                else:
                    refs_missing.append(ref)

            results.append({
                **q,
                "sources_count": rag["sources_count"],
                "refs_found": refs_found,
                "refs_missing": refs_missing,
                "retrieval_score": (len(refs_found) / len(q["expected_refs"])) if q["expected_refs"] else 0,
                "rag_prompt_length": len(rag["user"]),
                "status": "ok",
            })
        except Exception as e:
            results.append({
                **q,
                "sources_count": 0,
                "refs_found": [],
                "refs_missing": q["expected_refs"],
                "retrieval_score": 0,
                "error": str(e),
                "status": "error",
            })

    avg_retrieval = sum(r["retrieval_score"] for r in results) / len(results)
    ok_count = sum(1 for r in results if r["status"] == "ok")
    perfect_retrieval = sum(1 for r in results if r["retrieval_score"] == 1.0)

    summary = {
        "total_questions": len(results),
        "successful": ok_count,
        "avg_retrieval_score": round(avg_retrieval, 3),
        "perfect_retrieval": perfect_retrieval,
        "results": results,
    }

    output = json.dumps(summary, ensure_ascii=False, indent=2)
    if output_path:
        Path(output_path).write_text(output)
        print(f"\nResults saved to {output_path}")

    print(f"\n{'='*50}\nBENCHMARK RESULTS\n{'='*50}")
    print(f"Questions: {len(results)}")
    print(f"Successful retrieval: {ok_count}/{len(results)}")
    print(f"Avg retrieval score: {avg_retrieval:.1%}")
    print(f"Perfect retrieval (all refs found): {perfect_retrieval}/{len(results)}")

    for r in results:
        status = "✅" if r["retrieval_score"] == 1.0 else "⚠️" if r["retrieval_score"] > 0 else "❌"
        print(f"  {status} Q{r['id']}: {r['retrieval_score']:.0%} — {r['question'][:50]}...")
        if r.get("refs_missing"):
            print(f"      Missing: {', '.join(r['refs_missing'])}")

    return summary


if __name__ == "__main__":
    SKILL_DIR = Path(__file__).resolve().parent.parent
    output = sys.argv[1] if len(sys.argv) > 1 else str(SKILL_DIR / "data" / "benchmark_results.json")
    run_benchmark(output)
