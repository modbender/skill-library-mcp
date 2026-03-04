#!/usr/bin/env python3
"""
Raon OS — RAG Pipeline (Chunker + Embedder + Retriever)
Python 3.9+ compatible (no 3.10+ union type hints)

임베딩/LLM: raon_llm.py 범용 클라이언트 위임
  → OpenRouter / Gemini / OpenAI / Ollama 자동감지
  → 임베딩 없으면 BM25 keyword 검색 폴백

Usage:
    python3 rag_pipeline.py ingest --data-dir ../eval_data
    python3 rag_pipeline.py search --query "TIPS 합격하려면?"
    python3 rag_pipeline.py eval
"""

from __future__ import annotations  # Python 3.9 compatibility
import argparse
import json
import math
import os
import sys
import time
from pathlib import Path

# raon_llm: 범용 LLM/임베딩 클라이언트 (.env 자동로드 포함)
from raon_llm import (
    chat as _raon_chat,
    embed as _raon_embed,
    cosine_sim as cosine_similarity,
    detect_embed_provider,
    prompt_to_messages,
)

BASE_DIR = Path(__file__).resolve().parent.parent
EVAL_DATA_DIR = BASE_DIR / "eval_data"
VECTOR_STORE_PATH = BASE_DIR / "vector_store.json"

EMBED_MODEL = os.environ.get("EMBED_MODEL", "bge-m3")  # Ollama 폴백용 힌트


# ─── BM25 (simple keyword scoring) ───

# kiwipiepy 형태소 분석기 (lazy init)
_kiwi_instance = None
_kiwi_available = None

def _get_kiwi():
    """kiwipiepy Kiwi 인스턴스를 lazy 로딩."""
    global _kiwi_instance, _kiwi_available
    if _kiwi_available is None:
        try:
            from kiwipiepy import Kiwi
            _kiwi_instance = Kiwi()
            _kiwi_available = True
        except ImportError:
            _kiwi_available = False
    return _kiwi_instance if _kiwi_available else None


def _tokenize_kiwi(text: str) -> list[str]:
    """kiwipiepy 형태소 분석 기반 토크나이저."""
    kiwi = _get_kiwi()
    if kiwi is None:
        return _tokenize_bigram(text)
    tokens = []
    for token in kiwi.tokenize(text):
        form = token.form.lower()
        # 의미 있는 품사만: NNG(일반명사), NNP(고유명사), VV(동사), VA(형용사),
        # SL(외국어), SN(숫자), NNB(의존명사), XR(어근)
        if token.tag in ('NNG', 'NNP', 'VV', 'VA', 'SL', 'SN', 'NNB', 'XR', 'MAG'):
            tokens.append(form)
    return tokens


def _tokenize_bigram(text: str) -> list[str]:
    """Fallback: character n-gram + word tokenizer for Korean/English."""
    import re
    words = re.findall(r'[가-힣a-zA-Z0-9]+', text.lower())
    bigrams = []
    for w in words:
        if any('\uac00' <= c <= '\ud7a3' for c in w):
            for i in range(len(w) - 1):
                bigrams.append(w[i:i+2])
    return words + bigrams


def _tokenize(text: str) -> list[str]:
    """Korean/English tokenizer: kiwipiepy if available, else bigram fallback."""
    return _tokenize_kiwi(text)


def _build_bm25_index(store: list[dict]) -> dict:
    """Build inverted index for BM25 scoring."""
    import math
    doc_count = len(store)
    # doc frequency per term
    df = {}
    doc_tokens = []
    avg_dl = 0
    for item in store:
        tokens = _tokenize(item["text"])
        doc_tokens.append(tokens)
        avg_dl += len(tokens)
        seen = set()
        for t in tokens:
            if t not in seen:
                df[t] = df.get(t, 0) + 1
                seen.add(t)
    avg_dl = avg_dl / max(doc_count, 1)
    return {"df": df, "doc_tokens": doc_tokens, "avg_dl": avg_dl, "N": doc_count}


def bm25_score(query: str, doc_idx: int, index: dict, k1: float = 1.5, b: float = 0.75) -> float:
    """BM25 score for a single document."""
    import math
    q_tokens = _tokenize(query)
    doc_tokens = index["doc_tokens"][doc_idx]
    dl = len(doc_tokens)
    avg_dl = index["avg_dl"]
    N = index["N"]
    df = index["df"]

    # Term frequency in doc
    tf_map = {}
    for t in doc_tokens:
        tf_map[t] = tf_map.get(t, 0) + 1

    score = 0.0
    for qt in q_tokens:
        if qt not in tf_map:
            continue
        tf = tf_map[qt]
        doc_freq = df.get(qt, 0)
        idf = math.log((N - doc_freq + 0.5) / (doc_freq + 0.5) + 1)
        tf_norm = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / max(avg_dl, 1)))
        score += idf * tf_norm
    return score


def hybrid_search(query: str, top_k: int = 3, model: str = EMBED_MODEL,
                  store: list[dict] | None = None,
                  vector_weight: float = 0.6, bm25_weight: float = 0.4) -> list[dict]:
    """Hybrid search: vector cosine + BM25."""
    if store is None:
        store = load_vector_store()
    if not store:
        return []

    # BM25 인덱스 (항상 빌드)
    bm25_index = _build_bm25_index(store)
    raw_bm25 = [bm25_score(query, i, bm25_index) for i in range(len(store))]
    max_bm25 = max(raw_bm25) if raw_bm25 else 1.0
    bm25_scores = [s / max_bm25 if max_bm25 > 0 else 0.0 for s in raw_bm25]

    # Vector scores (폴백: 벡터 없으면 BM25 전용)
    q_emb = get_embedding(query, model)
    if not q_emb:
        # BM25 전용 모드
        scored = []
        for i, item in enumerate(store):
            scored.append({**item, "score": bm25_scores[i], "bm25_score": bm25_scores[i]})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    vector_scores = []
    for item in store:
        sim = cosine_similarity(q_emb, item.get("embedding", []))
        vector_scores.append(sim)

    # Combine
    scored = []
    for i, item in enumerate(store):
        combined = vector_weight * vector_scores[i] + bm25_weight * bm25_scores[i]
        scored.append({**item, "score": combined,
                       "vector_score": vector_scores[i],
                       "bm25_score": bm25_scores[i]})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


# ─── Chunker ───

def chunk_jsonl_entry(entry: dict) -> list[dict]:
    """JSONL 항목을 검색 가능한 chunk(들)로 변환."""
    entry_type = entry.get("type", "unknown")
    chunks = []
    
    # 메타데이터 (검색에 안 쓰이지만 결과 표시용)
    meta = {
        "type": entry_type,
        "source": entry.get("source", ""),
        "tags": entry.get("tags", []),
    }
    
    if entry_type == "success_case":
        # 성공사례: title + summary + tips를 하나의 chunk로
        text_parts = []
        if entry.get("title"):
            text_parts.append(entry["title"])
        if entry.get("program"):
            text_parts.append(f"프로그램: {entry['program']}")
        if entry.get("year"):
            text_parts.append(f"연도: {entry['year']}")
        if entry.get("summary"):
            text_parts.append(entry["summary"])
        if entry.get("tips"):
            text_parts.append(f"팁: {entry['tips']}")
        
        meta["title"] = entry.get("title", "")
        meta["program"] = entry.get("program", "")
        chunks.append({"text": "\n".join(text_parts), "meta": meta})
    
    elif entry_type == "criteria":
        text_parts = []
        if entry.get("category"):
            text_parts.append(f"카테고리: {entry['category']}")
        if entry.get("criteria"):
            text_parts.append(f"심사기준: {entry['criteria']}")
        if entry.get("description"):
            text_parts.append(entry["description"])
        if entry.get("weight"):
            text_parts.append(f"가중치: {entry['weight']}")
        
        meta["category"] = entry.get("category", "")
        meta["criteria"] = entry.get("criteria", "")
        chunks.append({"text": "\n".join(text_parts), "meta": meta})
    
    elif entry_type == "gov_program":
        text_parts = []
        if entry.get("program"):
            text_parts.append(f"사업명: {entry['program']}")
        if entry.get("category"):
            text_parts.append(f"분류: {entry['category']}")
        if entry.get("year"):
            text_parts.append(f"연도: {entry['year']}")
        if entry.get("description"):
            text_parts.append(entry["description"])
        if entry.get("budget"):
            text_parts.append(f"예산: {entry['budget']}")
        
        meta["program"] = entry.get("program", "")
        meta["year"] = entry.get("year", "")
        chunks.append({"text": "\n".join(text_parts), "meta": meta})
    
    elif entry_type == "vc_investment":
        text_parts = []
        if entry.get("title"):
            text_parts.append(entry["title"])
        if entry.get("category"):
            text_parts.append(f"분류: {entry['category']}")
        if entry.get("year"):
            text_parts.append(f"연도: {entry['year']}")
        if entry.get("data"):
            text_parts.append(entry["data"])
        
        meta["title"] = entry.get("title", "")
        meta["year"] = entry.get("year", "")
        chunks.append({"text": "\n".join(text_parts), "meta": meta})
    
    else:
        # Fallback: 모든 string 필드를 합침
        text_parts = [f"{k}: {v}" for k, v in entry.items() 
                      if isinstance(v, str) and k not in ("source", "type")]
        chunks.append({"text": "\n".join(text_parts), "meta": meta})
    
    return chunks


def load_all_chunks(data_dir: Path) -> list[dict]:
    """eval_data/ 내 모든 JSONL 파일에서 chunk 추출."""
    all_chunks = []
    for jsonl_file in sorted(data_dir.glob("*.jsonl")):
        count = 0
        for line in jsonl_file.read_text().strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            chunks = chunk_jsonl_entry(entry)
            for c in chunks:
                c["meta"]["file"] = jsonl_file.name
            all_chunks.extend(chunks)
            count += 1
        print(f"  📄 {jsonl_file.name}: {count}건 → {len([c for c in all_chunks if c['meta'].get('file') == jsonl_file.name])} chunks")
    return all_chunks


# ─── Embedder (raon_llm 위임) ────────────────────────────────────────────────
# 실제 구현은 raon_llm.embed()가 담당:
#   Gemini text-embedding-004 → OpenAI text-embedding-3-small → Ollama → []

def get_embedding(text: str, model: str = EMBED_MODEL) -> list:
    """raon_llm.embed()로 위임. 실패 시 [] (BM25 폴백)."""
    return _raon_embed(text)


def get_embeddings_batch(texts: list, model: str = EMBED_MODEL) -> list:
    """배치 임베딩. raon_llm.embed() 순차 호출."""
    return [_raon_embed(t) for t in texts]


def embed_chunks(chunks: list[dict], model: str = EMBED_MODEL, batch_size: int = 50) -> list[dict]:
    """모든 chunk에 임베딩 벡터 추가 (배치 처리)."""
    total = len(chunks)
    for batch_start in range(0, total, batch_size):
        batch = chunks[batch_start:batch_start + batch_size]
        texts = [c["text"] for c in batch]
        if batch_start == 0 or (batch_start + batch_size) % 500 == 0:
            print(f"  🔄 임베딩 {batch_start + 1}–{min(batch_start + batch_size, total)}/{total}...")
        embeddings = get_embeddings_batch(texts, model)
        for chunk, emb in zip(batch, embeddings):
            chunk["embedding"] = emb
    # 임베딩 실패한 것 제거
    valid = [c for c in chunks if c.get("embedding")]
    print(f"  ✅ 임베딩 완료: {len(valid)}/{total} 성공")
    return valid


# ─── Vector Store ───

def save_vector_store(chunks: list[dict], path: Path = VECTOR_STORE_PATH):
    """벡터 저장소를 JSON으로 저장."""
    store = []
    for c in chunks:
        store.append({
            "text": c["text"],
            "meta": c["meta"],
            "embedding": c["embedding"],
        })
    path.write_text(json.dumps(store, ensure_ascii=False))
    size_mb = path.stat().st_size / 1024 / 1024
    print(f"  💾 저장: {path.name} ({len(store)}건, {size_mb:.1f}MB)")


def load_vector_store(path: Path = VECTOR_STORE_PATH) -> list[dict]:
    """벡터 저장소 로드."""
    if not path.exists():
        return []
    return json.loads(path.read_text())


# ─── Retriever ───

# cosine_similarity: raon_llm.cosine_sim 으로 import (상단 참조)


def rerank(query: str, candidates: list, top_k: int = 3,
           llm_model: str = "") -> list:
    """LLM 기반 reranker: 후보 문서들을 쿼리 관련성 순으로 재정렬.
    llm_model 파라미터는 하위 호환용 (raon_llm이 자동 감지)."""
    if not candidates:
        return []
    if len(candidates) <= top_k:
        return candidates

    # 후보 문서 텍스트 준비 (번호 매기기)
    doc_list = []
    for i, c in enumerate(candidates):
        preview = c["text"][:300].replace("\n", " ")
        doc_list.append(f"[{i}] {preview}")
    docs_text = "\n".join(doc_list)

    prompt = (
        f"쿼리: {query}\n\n"
        f"다음 문서들 중 쿼리와 가장 관련 있는 순서대로 문서 번호를 나열해. "
        f"상위 {top_k}개만 쉼표로 구분해서 번호만 출력해. 설명 없이 번호만.\n\n"
        f"{docs_text}\n\n"
        f"답변 (번호만, 예: 3,1,7):"
    )

    response_text = _raon_chat(prompt_to_messages(prompt)) or ""
    if not response_text:
        print(f"  ⚠️ Rerank LLM 호출 실패, 원본 순서 반환")
        return candidates[:top_k]

    # 응답에서 숫자 추출
    import re
    numbers = re.findall(r'\d+', response_text)
    seen = set()
    reranked = []
    for n in numbers:
        idx = int(n)
        if 0 <= idx < len(candidates) and idx not in seen:
            seen.add(idx)
            reranked.append(candidates[idx])
        if len(reranked) >= top_k:
            break

    # LLM이 충분한 결과를 못 줬으면 원본에서 채움
    if len(reranked) < top_k:
        for c in candidates:
            if c not in reranked:
                reranked.append(c)
            if len(reranked) >= top_k:
                break

    return reranked


def search(query: str, top_k: int = 3, model: str = EMBED_MODEL,
           store: list[dict] | None = None) -> list[dict]:
    """쿼리로 top-k 검색."""
    if store is None:
        store = load_vector_store()
    if not store:
        print("❌ 벡터 저장소가 비어있습니다. 먼저 ingest를 실행하세요.")
        return []
    
    q_emb = get_embedding(query, model)
    if not q_emb:
        return []
    
    scored = []
    for item in store:
        sim = cosine_similarity(q_emb, item["embedding"])
        scored.append({**item, "score": sim})
    
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


# ─── Commands ───

def cmd_ingest(args):
    """JSONL 데이터를 chunk → embed → 저장."""
    data_dir = Path(args.data_dir) if args.data_dir else EVAL_DATA_DIR
    model = args.model or EMBED_MODEL

    print(f"🚀 RAG 인제스트 시작")
    print(f"   데이터: {data_dir}")
    print(f"   모델: {model}")

    # 1) Chunk
    print(f"\n📦 1단계: 청킹")
    chunks = load_all_chunks(data_dir)
    print(f"   총 {len(chunks)} chunks")

    # 임베딩 가능 여부 판단 (raon_llm 자동감지)
    embed_prov = detect_embed_provider()

    if embed_prov == "none":
        print(f"\n⚠️ 임베딩 프로바이더 없음 — BM25 keyword 검색 모드로 동작")
        print(f"   벡터 검색 사용: ~/.openclaw/.env 에 GEMINI_API_KEY 또는 OPENAI_API_KEY 추가")
        # 임베딩 없이 청크 저장 (BM25 전용)
        for c in chunks:
            c["embedding"] = []
        print(f"\n💾 2단계: 저장 (BM25 전용)")
        save_vector_store(chunks)
        print(f"\n✅ 인제스트 완료 (BM25 모드)! {len(chunks)}건 저장")
        return

    # 2) Embed
    print(f"\n🧠 2단계: 임베딩")
    print(f"   엔진: {embed_prov}")
    chunks = embed_chunks(chunks, model)

    # 3) Save
    print(f"\n💾 3단계: 저장")
    save_vector_store(chunks)

    print(f"\n✅ 인제스트 완료! {len(chunks)}건 벡터 저장소 생성")


def cmd_search(args):
    """쿼리 검색."""
    use_rerank = getattr(args, 'rerank', False)
    model = args.model or EMBED_MODEL

    if use_rerank:
        # Top-10 후보 → LLM rerank → Top-k
        candidates = hybrid_search(args.query, top_k=10, model=model)
        print(f"\n🔍 쿼리: {args.query} (rerank: ON, 후보 {len(candidates)}건)")
        results = rerank(args.query, candidates, top_k=args.top_k)
    else:
        results = hybrid_search(args.query, top_k=args.top_k, model=model)
        print(f"\n🔍 쿼리: {args.query}")

    print(f"   결과: {len(results)}건\n")
    for i, r in enumerate(results, 1):
        score_str = f"score: {r['score']:.4f}" if 'score' in r else ""
        print(f"  [{i}] ({score_str}) [{r['meta'].get('type','')}]")
        print(f"      {r['text'][:150]}...")
        print()


def cmd_eval(args):
    """10개 테스트 쿼리로 품질 검증."""
    queries = [
        "TIPS 합격하려면 어떻게 준비해야 해?",
        "초기창업패키지 심사기준은?",
        "예비창업패키지 합격 후기 알려줘",
        "2026년 정부 창업지원사업 뭐가 있어?",
        "벤처투자 현황 알려줘",
        "TIPS 운영사별 차이점은?",
        "창업도약패키지 신청 자격은?",
        "청년창업사관학교 합격 노하우",
        "시리즈A 투자 받으려면?",
        "정부지원사업 가점 받는 방법",
    ]
    
    model = args.model or EMBED_MODEL
    store = load_vector_store()
    if not store:
        print("❌ 벡터 저장소 없음. 먼저 ingest 실행 필요.")
        return
    
    print(f"📊 RAG 품질 검증 (모델: {model}, 저장소: {len(store)}건)")
    print(f"{'='*70}\n")
    
    results_log = []
    
    for qi, query in enumerate(queries, 1):
        results = hybrid_search(query, top_k=3, model=model, store=store)
        print(f"Q{qi}: {query}")
        
        query_results = []
        for i, r in enumerate(results, 1):
            rtype = r["meta"].get("type", "?")
            score = r["score"]
            title = r["meta"].get("title", r["meta"].get("criteria", r["meta"].get("program", "")))
            text_preview = r["text"][:120].replace("\n", " ")
            
            # 자동 relevance 판정 (score 기반)
            if score >= 0.7:
                relevance = "HIGH"
            elif score >= 0.5:
                relevance = "MED"
            else:
                relevance = "LOW"
            
            print(f"  #{i} [{relevance}] (sim={score:.4f}) [{rtype}] {title}")
            print(f"      {text_preview}...")
            
            query_results.append({
                "rank": i,
                "score": round(score, 4),
                "relevance": relevance,
                "type": rtype,
                "title": title,
                "text_preview": text_preview,
            })
        
        print()
        results_log.append({"query": query, "results": query_results})
    
    # 결과 저장
    report_path = BASE_DIR / "rag_eval_report.json"
    report_path.write_text(json.dumps(results_log, ensure_ascii=False, indent=2))
    print(f"📝 결과 저장: {report_path.name}")
    
    # 요약
    print(f"\n{'='*70}")
    print("📈 요약")
    high_count = sum(1 for q in results_log for r in q["results"] if r["relevance"] == "HIGH")
    med_count = sum(1 for q in results_log for r in q["results"] if r["relevance"] == "MED")
    low_count = sum(1 for q in results_log for r in q["results"] if r["relevance"] == "LOW")
    total_results = sum(len(q["results"]) for q in results_log)
    print(f"  HIGH: {high_count}/{total_results}, MED: {med_count}/{total_results}, LOW: {low_count}/{total_results}")
    
    # 쿼리별 top-1 relevance
    top1_high = sum(1 for q in results_log if q["results"] and q["results"][0]["relevance"] == "HIGH")
    print(f"  Top-1 HIGH 비율: {top1_high}/{len(queries)} ({top1_high/len(queries)*100:.0f}%)")


def main():
    parser = argparse.ArgumentParser(description="Raon OS RAG Pipeline")
    sub = parser.add_subparsers(dest="command")
    
    p_ingest = sub.add_parser("ingest", help="JSONL → chunk → embed → 저장")
    p_ingest.add_argument("--data-dir", default=str(EVAL_DATA_DIR))
    p_ingest.add_argument("--model", default=EMBED_MODEL)
    
    p_search = sub.add_parser("search", help="쿼리 검색")
    p_search.add_argument("--query", "-q", required=True)
    p_search.add_argument("--top-k", "-k", type=int, default=3)
    p_search.add_argument("--model", default=EMBED_MODEL)
    p_search.add_argument("--rerank", action="store_true", default=False,
                          help="LLM reranker로 Top-10→Top-k 정밀도 향상")
    
    p_eval = sub.add_parser("eval", help="10개 테스트 쿼리 품질 검증")
    p_eval.add_argument("--model", default=EMBED_MODEL)
    
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    {"ingest": cmd_ingest, "search": cmd_search, "eval": cmd_eval}[args.command](args)


if __name__ == "__main__":
    main()
