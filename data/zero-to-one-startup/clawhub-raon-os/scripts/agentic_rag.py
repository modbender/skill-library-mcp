#!/usr/bin/env python3
"""
Raon OS Agentic RAG — Phase 1+2

아키텍처:
  QueryRouter → 전략 선택 → 실행 → CRAG Critic → 결과

전략:
  factual   → HyDE + Structured Filter
  search    → Multi-Query RAG Fusion (3가지 변형 쿼리)
  realtime  → Tool RAG (웹 스크래핑)
  multistep → Speculative + Recursive RAG (최대 3회)

Python 3.9+ compatible
"""

from __future__ import annotations  # Python 3.9 compatibility

import json
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, Any, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
EVAL_DATA_DIR = BASE_DIR / "eval_data"

# ─── URL 허용 도메인 화이트리스트 (SSRF 방지) ────────────────────────────────
ALLOWED_DOMAINS = [
    "www.jointips.or.kr",
    "k-startup.go.kr",
    "www.nia.or.kr",
    "www.nipa.kr",
    "www.keit.re.kr",
    "www.kibo.or.kr",
    "www.bizinfo.go.kr",
    "api.supabase.co",
    "generativelanguage.googleapis.com",
    "openrouter.ai",
]


def is_allowed_url(url: str) -> bool:
    """URL이 허용된 도메인인지 검증 (SSRF 방지)
    parsed.hostname을 사용해 포트(:PORT)가 포함된 URL도 올바르게 처리.
    """
    from urllib.parse import urlparse
    parsed = urlparse(url)
    hostname = (parsed.hostname or "").lower()
    return any(hostname == d or hostname.endswith("." + d) for d in ALLOWED_DOMAINS)

sys.path.insert(0, str(SCRIPT_DIR))

from raon_llm import chat, embed, cosine_sim, prompt_to_messages


# ─── QueryRouter ─────────────────────────────────────────────────────────────

class QueryRouter:
    """질문 유형 분류기: LLM 우선, 실패 시 heuristic 폴백."""

    QUERY_TYPES = ("factual", "search", "realtime", "multistep")

    def classify(self, query: str) -> str:
        """
        LLM으로 질문 유형 분류:
        - 'factual': 자격조건, 제출서류 등 문서에 있는 사실
        - 'search': 추천, 매칭 등 탐색이 필요한 질문
        - 'realtime': 경쟁률, 마감일, 현재 접수 여부 등 실시간 정보
        - 'multistep': 여러 단계 추론 필요 (가능성 분석, 전략 수립)

        Gemini/LLM 호출로 분류. 실패 시 'search'로 폴백.
        """
        prompt = (
            f"다음 질문의 유형을 분류해. 반드시 아래 4가지 중 하나만 출력해 (한 단어만):\n\n"
            f"질문: {query}\n\n"
            f"분류 기준:\n"
            f"- factual: 자격조건, 제출서류, 지원금액, 심사기준 등 문서에 명시된 사실 질문\n"
            f"- search: 추천, 매칭, 비교, 찾아줘 등 탐색이 필요한 질문\n"
            f"- realtime: 현재 접수중, 마감일, 경쟁률, 최신 뉴스 등 실시간 정보\n"
            f"- multistep: 가능성 분석, 전략 수립, 단계별 계획 등 복합 추론이 필요한 질문\n\n"
            f"답변 (factual/search/realtime/multistep 중 하나만):"
        )

        try:
            result = chat(prompt_to_messages(prompt))
            if result:
                result_lower = result.strip().lower()
                for qtype in self.QUERY_TYPES:
                    if qtype in result_lower:
                        return qtype
        except Exception as e:
            print(f"[QueryRouter] classify LLM 실패: {e}", file=sys.stderr)

        # Fallback: rule-based heuristic
        return self._heuristic_classify(query)

    def _heuristic_classify(self, query: str) -> str:
        """LLM 실패 시 규칙 기반 분류."""
        q = query.lower()

        realtime_kws = ["현재", "지금", "접수중", "마감", "경쟁률", "오늘", "최근", "최신", "언제"]
        multistep_kws = ["전략", "계획", "어떻게 하면", "가능성", "분석", "단계", "로드맵", "방법"]
        factual_kws = ["자격", "조건", "서류", "기준", "요건", "금액", "얼마", "뭐가 필요", "어떤 서류",
                       "신청 방법", "제출", "심사"]

        for kw in realtime_kws:
            if kw in q:
                return "realtime"
        for kw in multistep_kws:
            if kw in q:
                return "multistep"
        for kw in factual_kws:
            if kw in q:
                return "factual"
        return "search"


# ─── HyDE (Hypothetical Document Embeddings) ─────────────────────────────────

def hyde_retrieve(query: str, rag: Any, top_k: int = 5) -> list:
    """
    HyDE 검색:
    1. LLM으로 가상 문서 생성: "이 질문에 답하는 정부공고 내용을 가상으로 작성"
    2. 가상 문서를 임베딩
    3. 임베딩으로 실제 문서 검색
    → 질문 표현과 문서 표현의 미스매치 해결
    """
    # Step 1: LLM으로 가상 문서 생성
    hyde_prompt = (
        f"다음 질문에 답하는 가상의 정부 지원사업 공고문을 3-4문장으로 작성해. "
        f"실제 공고문처럼 구체적으로 작성해.\n\n"
        f"질문: {query}\n\n"
        f"가상 공고문:"
    )

    hypothetical_doc = query  # fallback
    try:
        result = chat(prompt_to_messages(hyde_prompt))
        if result and len(result.strip()) > 10:
            hypothetical_doc = result.strip()
    except Exception as e:
        print(f"[HyDE] 가상 문서 생성 실패: {e}", file=sys.stderr)

    # Step 2 & 3: 가상 문서로 실제 문서 검색
    try:
        return _rag_search(rag, hypothetical_doc, top_k=top_k)
    except Exception as e:
        print(f"[HyDE] 검색 실패: {e}", file=sys.stderr)
        return []


# ─── Reciprocal Rank Fusion ───────────────────────────────────────────────────

def _reciprocal_rank_fusion(result_lists: list, k: int = 60) -> list:
    """Reciprocal Rank Fusion (RRF) 알고리즘으로 여러 결과 목록을 통합."""
    scores: dict = {}
    doc_map: dict = {}

    for results in result_lists:
        for rank, doc in enumerate(results):
            # 텍스트 앞 100자를 ID로 사용
            doc_id = doc.get("text", "")[:100]
            if doc_id not in scores:
                scores[doc_id] = 0.0
                doc_map[doc_id] = doc
            scores[doc_id] += 1.0 / (k + rank + 1)

    sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    result = []
    for doc_id in sorted_ids:
        doc = dict(doc_map[doc_id])
        doc["rrf_score"] = scores[doc_id]
        doc["score"] = scores[doc_id]
        result.append(doc)

    return result


# ─── Multi-Query RAG Fusion ───────────────────────────────────────────────────

def multi_query_retrieve(query: str, rag: Any, n_variants: int = 3, top_k: int = 5) -> list:
    """
    Multi-Query RAG Fusion:
    1. LLM으로 쿼리 3가지 변형 생성 (다른 각도)
       예: "TIPS 자격" → ["TIPS 선정 기준", "TIPS 제외 대상", "TIPS 심사 항목"]
    2. 각 변형으로 검색
    3. Reciprocal Rank Fusion으로 결과 합산
    → 단일 쿼리 RAG가 놓치는 내용 캐치
    """
    # Step 1: 쿼리 변형 생성
    variant_prompt = (
        f"다음 질문을 {n_variants}가지 다른 각도로 재작성해. "
        f"각각 한 줄씩, 번호 없이 출력해.\n\n"
        f"원본 질문: {query}\n\n"
        f"{n_variants}가지 변형 (다른 키워드, 다른 관점 사용):"
    )

    queries = [query]  # 원본 쿼리 항상 포함
    try:
        result = chat(prompt_to_messages(variant_prompt))
        if result:
            variants = [
                line.strip()
                for line in result.strip().split("\n")
                if line.strip() and len(line.strip()) > 3
            ]
            queries.extend(variants[:n_variants])
    except Exception as e:
        print(f"[MultiQuery] 변형 생성 실패: {e}", file=sys.stderr)

    # Step 2: 각 변형으로 검색
    all_results = []
    for q in queries:
        try:
            results = _rag_search(rag, q, top_k=top_k)
            if results:
                all_results.append(results)
        except Exception as e:
            print(f"[MultiQuery] 검색 실패 ({q[:30]}): {e}", file=sys.stderr)

    if not all_results:
        return []

    # Step 3: RRF로 통합
    fused = _reciprocal_rank_fusion(all_results)

    # 중복 제거 (텍스트 앞 100자 기준)
    seen: set = set()
    deduped = []
    for doc in fused:
        doc_id = doc.get("text", "")[:100]
        if doc_id not in seen:
            seen.add(doc_id)
            deduped.append(doc)

    return deduped[:top_k * 2]


# ─── Speculative RAG ─────────────────────────────────────────────────────────

def speculative_retrieve(query: str, rag: Any, top_k: int = 5) -> Tuple[str, list]:
    """
    Speculative RAG:
    1. LLM으로 초안 답변 생성 (검색 없이)
    2. 초안 기반으로 검색 쿼리 생성 ("이걸 확인하려면 뭘 검색해야 하나")
    3. 실제 문서로 검증/보완
    → Speculative RAG: 빠르고 방향성 있는 검색
    """
    # Step 1: 초안 답변 생성 (검색 없이)
    draft_prompt = (
        f"다음 질문에 대한 초안 답변을 작성해. 확실하지 않아도 괜찮음. 아는 범위에서 답변해.\n\n"
        f"질문: {query}\n\n"
        f"초안 답변:"
    )

    draft_answer = ""
    try:
        result = chat(prompt_to_messages(draft_prompt))
        if result:
            draft_answer = result.strip()
    except Exception as e:
        print(f"[Speculative] 초안 생성 실패: {e}", file=sys.stderr)

    # Step 2: 초안에서 검색 쿼리 추출
    search_query = query  # fallback
    if draft_answer:
        sq_prompt = (
            f"다음 초안 답변을 검증하려면 어떤 키워드로 검색해야 할까? 검색 쿼리 하나만 작성해.\n\n"
            f"초안 답변: {draft_answer[:300]}\n\n"
            f"검색 쿼리:"
        )
        try:
            sq_result = chat(prompt_to_messages(sq_prompt))
            if sq_result and len(sq_result.strip()) > 3:
                search_query = sq_result.strip()
        except Exception as e:
            print(f"[Speculative] 검색 쿼리 생성 실패: {e}", file=sys.stderr)

    # Step 3: 실제 문서 검색으로 검증/보완
    try:
        docs = _rag_search(rag, search_query, top_k=top_k)
        return draft_answer, docs
    except Exception as e:
        print(f"[Speculative] 검색 실패: {e}", file=sys.stderr)
        return draft_answer, []


# ─── CRAG Critic ─────────────────────────────────────────────────────────────

def crag_critic(query: str, context: str, answer: str) -> dict:
    """
    CRAG Critic: LLM에게 검색 결과와 답변의 품질을 평가 요청.

    반환:
        {
          "relevant": float (0-1),
          "sufficient": float (0-1),
          "confident": float (0-1),
          "action": "use" | "refine" | "retry_different"
        }
    """
    critic_prompt = (
        f"다음 검색 결과와 답변의 품질을 평가해. JSON으로만 답해.\n\n"
        f"질문: {query}\n"
        f"검색 결과 (일부): {context[:500]}\n"
        f"답변 (일부): {answer[:300]}\n\n"
        f"평가 기준:\n"
        f"- relevant: 검색 결과가 질문과 관련 있는 정도 (0.0~1.0)\n"
        f"- sufficient: 답변에 충분한 정보가 있는지 (0.0~1.0)\n"
        f"- confident: 답변의 신뢰도 (0.0~1.0)\n"
        f'- action: "use" (그대로 사용) / "refine" (쿼리 개선) / "retry_different" (다른 전략)\n\n'
        f"JSON 형식으로만 출력 (설명 없이):\n"
        f'{{"relevant": 0.8, "sufficient": 0.7, "confident": 0.8, "action": "use"}}'
    )

    default_result: dict = {
        "relevant": 0.5,
        "sufficient": 0.5,
        "confident": 0.5,
        "action": "use",
    }

    try:
        result = chat(prompt_to_messages(critic_prompt))
        if result:
            json_match = re.search(r'\{[^}]+\}', result, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                # 값 검증 및 정규화
                for k in ("relevant", "sufficient", "confident"):
                    if k in parsed:
                        try:
                            parsed[k] = float(parsed[k])
                            parsed[k] = max(0.0, min(1.0, parsed[k]))
                        except (ValueError, TypeError):
                            parsed[k] = default_result[k]
                if "action" not in parsed or parsed["action"] not in (
                    "use", "refine", "retry_different"
                ):
                    parsed["action"] = "use"
                return {**default_result, **parsed}
    except Exception as e:
        print(f"[CRAG] Critic 평가 실패: {e}", file=sys.stderr)

    return default_result


# ─── Recursive RAG (ReFRAG) ───────────────────────────────────────────────────

def recursive_retrieve(query: str, rag: Any, max_iterations: int = 3) -> list:
    """
    Recursive RAG (ReFRAG):
    1. 초기 검색
    2. CRAG Critic으로 품질 평가
    3. 미달 시 → 쿼리 리파인 후 재검색
    4. 최대 max_iterations 반복
    → 꼬리에 꼬리를 무는 재검색
    """
    current_query = query
    best_results: list = []

    for iteration in range(max_iterations):
        # 검색
        try:
            results = _rag_search(rag, current_query, top_k=5)
        except Exception as e:
            print(f"[Recursive] 검색 실패 (iter {iteration}): {e}", file=sys.stderr)
            break

        if not results:
            break

        best_results = results

        # CRAG 품질 평가
        context = "\n".join([r.get("text", "")[:200] for r in results[:3]])
        temp_answer = f"검색된 {len(results)}개 문서를 기반으로 답변 준비 중"
        critique = crag_critic(query, context, temp_answer)

        # 충분하면 종료
        if critique.get("action") == "use" or critique.get("sufficient", 0) >= 0.7:
            break

        # 쿼리 리파인
        if critique.get("action") in ("refine", "retry_different"):
            refine_prompt = (
                f"원본 쿼리로 검색했는데 결과가 충분하지 않았어. 더 나은 검색 쿼리를 만들어줘.\n\n"
                f"원본 쿼리: {current_query}\n"
                f"검색 결과 품질: relevant={critique.get('relevant', 0):.1f}, "
                f"sufficient={critique.get('sufficient', 0):.1f}\n\n"
                f"개선된 검색 쿼리 (한 줄):"
            )
            try:
                refined = chat(prompt_to_messages(refine_prompt))
                if refined and len(refined.strip()) > 3:
                    current_query = refined.strip()
                else:
                    break
            except Exception as e:
                print(f"[Recursive] 쿼리 리파인 실패: {e}", file=sys.stderr)
                break
        else:
            break

    return best_results


# ─── 내부 헬퍼: RAG 검색 ──────────────────────────────────────────────────────

def _rag_search(rag: Any, query: str, top_k: int = 5) -> list:
    """rag 객체/모듈에서 검색. hybrid_search → search → 모듈 순으로 시도."""
    if hasattr(rag, "hybrid_search"):
        return rag.hybrid_search(query, top_k=top_k)
    if hasattr(rag, "search"):
        return rag.search(query, top_k=top_k)
    # rag가 모듈일 경우
    import rag_pipeline as _rag_mod
    return _rag_mod.hybrid_search(query, top_k=top_k)


# ─── Tools ───────────────────────────────────────────────────────────────────

class Tools:
    """정부 지원사업 도구 모음."""

    def __init__(self) -> None:
        self._programs_cache: Optional[list] = None

    def _load_programs(self) -> list:
        """eval_data에서 gov_program / success_case / criteria 데이터 로드."""
        if self._programs_cache is not None:
            return self._programs_cache

        programs = []
        if not EVAL_DATA_DIR.exists():
            self._programs_cache = programs
            return programs

        for jsonl_file in sorted(EVAL_DATA_DIR.glob("*.jsonl")):
            try:
                for line in jsonl_file.read_text(encoding="utf-8").strip().split("\n"):
                    line = line.strip()
                    if not line:
                        continue
                    entry = json.loads(line)
                    if entry.get("type") in ("gov_program", "success_case", "criteria"):
                        programs.append(entry)
            except Exception as e:
                print(f"[Tools] {jsonl_file.name} 로드 실패: {e}", file=sys.stderr)

        self._programs_cache = programs
        return programs

    def search_gov_programs(
        self, keywords: list, filters: Optional[dict] = None
    ) -> list:
        """
        eval_data JSON에서 structured filter:
        - keywords: 키워드 리스트
        - filters: {"deadline_after": "2026-03-01", "min_budget": 100000000}
        → 하드 필터 먼저, 소프트 랭킹 나중
        """
        programs = self._load_programs()
        if not programs:
            return []

        filters = filters or {}

        # 하드 필터
        filtered = []
        for p in programs:
            # deadline_after 필터
            if "deadline_after" in filters:
                deadline = p.get("deadline", p.get("meta", {}).get("deadline", ""))
                if deadline and deadline < filters["deadline_after"]:
                    continue

            # min_budget 필터
            if "min_budget" in filters:
                budget_str = str(p.get("budget", p.get("meta", {}).get("budget", "0")))
                nums = re.findall(r"\d+", budget_str.replace(",", ""))
                budget_num = int(nums[0]) if nums else 0
                # 억원 단위 정규화 (숫자가 작으면 억원으로 간주)
                if 0 < budget_num < 1_000:
                    budget_num *= 100_000_000
                if budget_num < filters["min_budget"]:
                    continue

            filtered.append(p)

        # 소프트 랭킹 (키워드 매칭)
        def keyword_score(p: dict) -> float:
            text = json.dumps(p, ensure_ascii=False).lower()
            score = 0.0
            for kw in keywords:
                if str(kw).lower() in text:
                    score += 1.0
            return score

        ranked = sorted(filtered, key=keyword_score, reverse=True)
        return ranked[:20]

    def check_eligibility(
        self, program_name: str, startup_profile: dict
    ) -> dict:
        """
        스타트업 프로필 vs 프로그램 자격조건 매칭.
        - startup_profile: {"age_years": 3, "industry": "AI", "has_tips": False}
        - 반환: {"eligible": True, "reasons": [...], "warnings": [...]}
        """
        programs = self._load_programs()

        # 매칭되는 프로그램 찾기
        matched = None
        for p in programs:
            name = p.get("program", p.get("title", ""))
            if (
                program_name.lower() in name.lower()
                or name.lower() in program_name.lower()
            ):
                matched = p
                break

        if not matched:
            # LLM으로 판단
            eligibility_prompt = (
                f"다음 스타트업이 '{program_name}' 프로그램에 지원할 수 있는지 판단해.\n\n"
                f"스타트업 프로필:\n"
                f"{json.dumps(startup_profile, ensure_ascii=False, indent=2)}\n\n"
                f"JSON 형식으로만 답해:\n"
                f'{{"eligible": true, "reasons": ["이유1"], "warnings": ["주의사항1"]}}'
            )
            try:
                result = chat(prompt_to_messages(eligibility_prompt))
                if result:
                    json_match = re.search(r"\{.*\}", result, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
            except Exception as e:
                print(f"[Tools] eligibility LLM 실패: {e}", file=sys.stderr)

            return {
                "eligible": None,
                "reasons": ["프로그램 정보 없음"],
                "warnings": ["직접 확인 필요"],
            }

        # 규칙 기반 판단
        reasons = []
        warnings = []
        eligible = True

        age = startup_profile.get("age_years", 0)
        description = matched.get("description", "")

        if "7년" in description and age > 7:
            eligible = False
            reasons.append(f"창업 {age}년차 → 7년 초과 (불가)")
        elif age > 0:
            reasons.append(f"창업 {age}년차 → 기간 요건 검토 가능")

        has_tips = startup_profile.get("has_tips", False)
        if "TIPS" in program_name.upper() and not has_tips:
            warnings.append("TIPS 비수혜기업 → 별도 검토 필요")

        return {
            "eligible": eligible,
            "reasons": reasons,
            "warnings": warnings,
            "program_info": {
                "name": matched.get("program", matched.get("title", "")),
                "description": matched.get("description", "")[:200],
            },
        }

    def fetch_realtime(self, url: str) -> str:
        """
        urllib로 URL 페칭 (실시간 정보).
        k-startup.go.kr 등. 타임아웃 5초, 실패 시 "실시간 조회 불가" 반환.
        허용된 도메인(ALLOWED_DOMAINS)만 접근 가능 — SSRF 방지.
        """
        if not is_allowed_url(url):
            raise ValueError(
                f"[fetch_realtime] 허용되지 않은 도메인: {url!r}. "
                f"허용 도메인: {ALLOWED_DOMAINS}"
            )
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; RaonOS/3.0)"},
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                content = resp.read()
                charset = "utf-8"
                ct = resp.headers.get("Content-Type", "")
                if "charset=" in ct:
                    charset = ct.split("charset=")[-1].split(";")[0].strip()
                return content.decode(charset, errors="replace")[:3000]
        except urllib.error.URLError as e:
            print(f"[Tools] fetch_realtime URL 에러 ({url[:50]}): {e}", file=sys.stderr)
            return "실시간 조회 불가"
        except Exception as e:
            print(f"[Tools] fetch_realtime 실패 ({url[:50]}): {e}", file=sys.stderr)
            return "실시간 조회 불가"


# ─── AgenticRAG 메인 클래스 ───────────────────────────────────────────────────

class AgenticRAG:
    """Agentic RAG 오케스트레이터."""

    def __init__(self, rag_pipeline: Any) -> None:
        """
        Args:
            rag_pipeline: rag_pipeline 모듈 또는 hybrid_search/search 메서드를 가진 객체
        """
        self.rag = rag_pipeline
        self.router = QueryRouter()
        self.tools = Tools()

    def _generate_final_answer(
        self,
        query: str,
        docs: list,
        draft: Optional[str] = None,
        startup_profile: Optional[dict] = None,
    ) -> str:
        """검색 결과를 기반으로 최종 답변 생성."""
        if not docs:
            return "관련 정보를 찾지 못했습니다. 더 구체적인 질문을 해주세요."

        context = "\n\n".join(
            [f"[문서 {i + 1}] {doc.get('text', '')[:300]}" for i, doc in enumerate(docs[:5])]
        )

        profile_part = ""
        if startup_profile:
            profile_part = f"\n\n스타트업 프로필: {json.dumps(startup_profile, ensure_ascii=False)}"

        draft_part = ""
        if draft:
            draft_part = f"\n\n참고 초안: {draft[:200]}"

        answer_prompt = (
            f"다음 검색 결과를 바탕으로 질문에 답해. 한국어로, 구체적이고 실용적으로 답해.\n\n"
            f"질문: {query}"
            f"{profile_part}"
            f"{draft_part}\n\n"
            f"검색 결과:\n{context}\n\n"
            f"답변:"
        )

        try:
            result = chat(prompt_to_messages(answer_prompt))
            if result:
                return result.strip()
        except Exception as e:
            print(f"[AgenticRAG] 최종 답변 생성 실패: {e}", file=sys.stderr)

        # Fallback: 첫 번째 문서 텍스트
        return docs[0].get("text", "관련 정보를 찾았지만 답변 생성에 실패했습니다.")[:500]

    def run(
        self,
        query: str,
        startup_profile: Optional[dict] = None,
        max_retries: int = 2,
    ) -> dict:
        """
        메인 엔트리포인트:
        1. 라우팅
        2. 전략별 검색
        3. CRAG 평가
        4. 미달 시 재시도 (다른 전략)
        5. 최종 답변 생성

        반환:
        {
          "answer": str,
          "strategy_used": str,
          "sources": [...],
          "confidence": float,
          "iterations": int
        }
        """
        iterations = 0
        query_type = self.router.classify(query)
        strategy_used = query_type
        docs: list = []
        draft_answer: Optional[str] = None
        confidence = 0.5

        print(
            f"[AgenticRAG] query_type={query_type}, query={query[:50]}",
            file=sys.stderr,
        )

        # 전략별 검색 + CRAG 평가 루프
        for attempt in range(max_retries + 1):
            iterations += 1

            try:
                if query_type == "factual":
                    # HyDE + Structured Filter
                    docs = hyde_retrieve(query, self.rag, top_k=5)
                    if startup_profile:
                        struct_results = self.tools.search_gov_programs(
                            keywords=query.split()[:5]
                        )
                        existing_ids = {d.get("text", "")[:50] for d in docs}
                        for sr in struct_results[:3]:
                            sr_text = sr.get("description", sr.get("summary", ""))
                            if sr_text[:50] not in existing_ids:
                                docs.append(
                                    {"text": sr_text, "meta": sr, "score": 0.5}
                                )

                elif query_type == "search":
                    # Multi-Query RAG Fusion
                    docs = multi_query_retrieve(query, self.rag, n_variants=3, top_k=5)

                elif query_type == "realtime":
                    # Tool RAG
                    struct_results = self.tools.search_gov_programs(
                        keywords=query.split()[:5], filters={}
                    )
                    docs = [
                        {
                            "text": (
                                f"사업명: {r.get('program', r.get('title', ''))}\n"
                                f"{r.get('description', r.get('summary', ''))}"
                            ),
                            "meta": r,
                            "score": 0.7,
                        }
                        for r in struct_results[:5]
                    ]
                    # 실시간 URL 페칭 시도
                    for r in struct_results[:2]:
                        url = r.get("url", r.get("application_url", ""))
                        if url and url.startswith("http"):
                            rt_content = self.tools.fetch_realtime(url)
                            if rt_content != "실시간 조회 불가":
                                docs.insert(
                                    0,
                                    {
                                        "text": f"실시간 정보 ({url}):\n{rt_content[:500]}",
                                        "meta": {"source": url, "type": "realtime"},
                                        "score": 0.9,
                                    },
                                )
                    # 폴백: 벡터 검색
                    if not docs:
                        docs = multi_query_retrieve(query, self.rag, top_k=5)

                elif query_type == "multistep":
                    # Speculative + Recursive RAG
                    draft_answer, spec_docs = speculative_retrieve(
                        query, self.rag, top_k=5
                    )
                    rec_docs = recursive_retrieve(query, self.rag, max_iterations=3)

                    # 병합 + 중복 제거
                    seen: set = set()
                    docs = []
                    for d in spec_docs + rec_docs:
                        doc_id = d.get("text", "")[:80]
                        if doc_id not in seen:
                            seen.add(doc_id)
                            docs.append(d)

                else:
                    # Default: multi-query
                    docs = multi_query_retrieve(query, self.rag, top_k=5)

            except Exception as e:
                print(
                    f"[AgenticRAG] 전략 실행 실패 (attempt {attempt}): {e}",
                    file=sys.stderr,
                )
                # 기본 검색으로 폴백
                try:
                    docs = _rag_search(self.rag, query, top_k=5)
                except Exception as e2:
                    print(f"[AgenticRAG] 기본 검색도 실패: {e2}", file=sys.stderr)
                    docs = []

            if not docs:
                if attempt < max_retries:
                    query_type = "search"
                    strategy_used = f"{strategy_used}→search"
                continue

            # CRAG 평가
            context = "\n".join([d.get("text", "")[:200] for d in docs[:3]])
            temp_answer = draft_answer or f"{len(docs)}개 문서 검색됨"
            critique = crag_critic(query, context, temp_answer)

            action = critique.get("action", "use")
            confidence = (
                critique.get("relevant", 0.5)
                + critique.get("sufficient", 0.5)
                + critique.get("confident", 0.5)
            ) / 3.0

            if action == "use" or attempt >= max_retries:
                break

            # 재시도: 다른 전략으로 전환
            if action == "retry_different":
                strategy_map: dict = {
                    "factual": "search",
                    "search": "multistep",
                    "realtime": "search",
                    "multistep": "search",
                }
                next_type = strategy_map.get(query_type, "search")
                strategy_used = f"{strategy_used}→{next_type}"
                query_type = next_type

        # 최종 답변 생성
        answer = self._generate_final_answer(
            query, docs, draft=draft_answer, startup_profile=startup_profile
        )

        # 소스 정보 추출
        sources = []
        for doc in docs[:5]:
            meta = doc.get("meta", {})
            source: dict = {
                "text": doc.get("text", "")[:150],
                "type": meta.get("type", "unknown") if isinstance(meta, dict) else "unknown",
                "score": float(doc.get("score", doc.get("rrf_score", 0.0))),
            }
            if isinstance(meta, dict):
                if meta.get("title"):
                    source["title"] = meta["title"]
                if meta.get("program"):
                    source["program"] = meta["program"]
            sources.append(source)

        return {
            "answer": answer,
            "strategy_used": strategy_used,
            "sources": sources,
            "confidence": round(confidence if docs else 0.0, 3),
            "iterations": iterations,
        }
