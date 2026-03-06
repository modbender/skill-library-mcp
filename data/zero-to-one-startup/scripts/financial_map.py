#!/usr/bin/env python3
"""
Raon OS — 금융맵 (융자/보증/크라우드펀딩 정보 제공)

- KODIT (신용보증기금)
- KIBO (기술보증기금)
- 소진공 정책자금
- Wadiz/Tumblbug 크라우드펀딩

Python 3.9+ compatible
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional, List

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

# ─── 금융 상품 DB ─────────────────────────────────────────────────────────────

FINANCIAL_PRODUCTS = [
    {
        "name": "청년창업 특례보증 (KODIT)",
        "provider": "신용보증기금",
        "type": "보증",
        "track": ["A", "B", "AB"],
        "target": "39세 이하 창업 3년 이내",
        "max_amount": "1억원",
        "rate": "시중금리 - 0.5%",
        "url": "https://www.kodit.co.kr",
        "keywords": ["청년", "창업", "보증"],
        "description": "신용이 부족해도 보증서로 은행 대출 가능",
    },
    {
        "name": "기술보증 (KIBO)",
        "provider": "기술보증기금",
        "type": "보증",
        "track": ["A", "AB"],
        "target": "기술 기반 창업기업",
        "max_amount": "5억원",
        "url": "https://www.kibo.or.kr",
        "keywords": ["기술", "특허", "IP"],
        "description": "기술력으로 보증, 담보 없이 최대 5억 가능",
    },
    {
        "name": "소상공인 정책자금",
        "provider": "소상공인시장진흥공단",
        "type": "융자",
        "track": ["B"],
        "target": "소상공인 (매출 10억 이하)",
        "max_amount": "7천만원",
        "rate": "2.0% (2026 기준)",
        "url": "https://www.semas.or.kr/web/SUB01/SUB0101.cmdc",
        "keywords": ["소상공인", "자영업", "음식점"],
        "description": "국민은행·기업은행 등 협력은행 통해 저금리 융자",
    },
    {
        "name": "Wadiz 크라우드펀딩",
        "provider": "Wadiz",
        "type": "크라우드펀딩",
        "track": ["B", "AB"],
        "target": "제조/콘텐츠/F&B 창업자",
        "max_amount": "제한없음 (시장 반응에 따라)",
        "url": "https://www.wadiz.kr",
        "keywords": ["제조", "굿즈", "음식", "콘텐츠"],
        "description": "초기 고객 확보 + 자금 조달 동시 가능. 성공 시 투자자 관심도 UP",
    },
    {
        "name": "희망리턴패키지",
        "provider": "소상공인시장진흥공단",
        "type": "지원금",
        "track": ["B"],
        "target": "폐업 위기 또는 전환 희망 소상공인",
        "max_amount": "최대 500만원",
        "url": "https://www.semas.or.kr",
        "keywords": ["폐업", "전환", "재기"],
        "description": "폐업 컨설팅, 점포 철거비, 재취업/재창업 교육 지원",
    },
    {
        "name": "TIPS (기술창업투자프로그램)",
        "provider": "중소벤처기업부",
        "type": "지원금+투자",
        "track": ["A"],
        "target": "기술 기반 초기 스타트업",
        "max_amount": "5억원 (R&D)",
        "url": "https://www.jointips.or.kr",
        "keywords": ["AI", "바이오", "딥테크", "R&D"],
        "description": "민간 투자 매칭 + 정부 R&D 최대 5억",
    },
    {
        "name": "Tumblbug 크라우드펀딩",
        "provider": "Tumblbug",
        "type": "크라우드펀딩",
        "track": ["B", "AB"],
        "target": "창작/문화/라이프스타일 창업자",
        "max_amount": "제한없음",
        "url": "https://www.tumblbug.com",
        "keywords": ["창작", "문화", "굿즈", "독립출판"],
        "description": "창작자 중심 펀딩 플랫폼. 소규모 프로젝트에 강점",
    },
    {
        "name": "소상공인 스마트화 지원사업",
        "provider": "소상공인시장진흥공단",
        "type": "지원금",
        "track": ["B", "AB"],
        "target": "소상공인 디지털 전환 희망 사업자",
        "max_amount": "최대 400만원",
        "url": "https://www.semas.or.kr",
        "keywords": ["디지털", "스마트", "키오스크", "앱"],
        "description": "POS, 키오스크, 스마트오더 등 디지털 전환 비용 지원",
    },
]


# ─── FinancialMap ─────────────────────────────────────────────────────────────

class FinancialMap:
    """트랙 + 키워드 기반 금융 상품 매칭 및 추천."""

    def match(
        self,
        track: str,
        keywords: Optional[List[str]] = None,
        need_loan: bool = False,
    ) -> List[dict]:
        """
        트랙 + 키워드 기반 금융 상품 매칭.

        Args:
            track: "A" | "B" | "AB"
            keywords: 추가 키워드 필터 (예: ["청년", "음식점"])
            need_loan: True면 융자/보증 우선 정렬

        Returns:
            매칭된 금융 상품 목록 (관련도 높은 순)
        """
        results = []

        for product in FINANCIAL_PRODUCTS:
            # 트랙 필터
            if track not in product["track"] and track != "AB":
                continue
            if track == "AB":
                # AB면 A, B, AB 모두 포함
                pass

            score = 0

            # 트랙 완전 일치 가산점
            if track in product["track"]:
                score += 2
            # AB 상품은 AB 트랙에서 높은 점수
            if "AB" in product["track"] and track == "AB":
                score += 1

            # 키워드 매칭
            if keywords:
                product_kws = " ".join(product.get("keywords", []) + [product["description"]])
                for kw in keywords:
                    if kw in product_kws:
                        score += 1

            # 융자 우선 필터
            if need_loan and product["type"] in ("융자", "보증"):
                score += 2

            results.append((score, product))

        # 점수 내림차순 정렬
        results.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in results]

    def format_recommendation(
        self,
        products: List[dict],
        startup_info: str = "",
    ) -> str:
        """
        금융 상품 추천 텍스트 생성.
        LLM 사용 가능 시 맞춤형, 실패 시 기본 포맷 반환.
        """
        if not products:
            return "현재 조건에 맞는 금융 상품이 없습니다. 소진공(1357)에 문의해 보세요."

        # 기본 텍스트 포맷 (LLM 없이도 동작)
        lines = ["💰 **맞춤 금융 상품 추천**\n"]
        for i, p in enumerate(products[:4], 1):
            emoji = ["🥇", "🥈", "🥉", "4️⃣"][i - 1] if i <= 4 else f"{i}."
            lines.append(f"{emoji} **{p['name']}** ({p['provider']})")
            lines.append(f"   - 유형: {p['type']}")
            lines.append(f"   - 대상: {p['target']}")
            lines.append(f"   - 최대 금액: {p['max_amount']}")
            if p.get("rate"):
                lines.append(f"   - 금리: {p['rate']}")
            lines.append(f"   - 💡 {p['description']}")
            lines.append(f"   - 🔗 {p['url']}")
            lines.append("")

        basic_text = "\n".join(lines)

        # LLM 으로 맞춤형 추천 텍스트 생성 시도
        if startup_info:
            try:
                from raon_llm import chat, prompt_to_messages

                product_summary = "\n".join([
                    f"- {p['name']}: {p['description']} (최대 {p['max_amount']})"
                    for p in products[:4]
                ])
                prompt = (
                    f"아래 창업자 정보와 금융 상품을 참고해서 맞춤 추천 설명을 작성해.\n"
                    f"쉬운 말로, 2-3문장씩 왜 이 상품이 맞는지 설명해줘. 전문용어 금지.\n\n"
                    f"창업자 정보:\n{startup_info[:500]}\n\n"
                    f"추천 상품:\n{product_summary}\n\n"
                    f"형식: 각 상품에 대해 '이 상품은 {startup_info[:30]}에게 좋은 이유: ...' 형식으로"
                )
                llm_result = chat(prompt_to_messages(prompt))
                if llm_result:
                    return basic_text + "\n---\n🤖 **라온의 맞춤 설명:**\n" + llm_result
            except Exception as e:
                print(f"[FinancialMap] LLM 추천 실패: {e}", file=sys.stderr)

        return basic_text

    def get_summary(self, track: str) -> str:
        """트랙별 금융 지원 요약."""
        summaries = {
            "A": "기술창업 Track A: TIPS R&D 최대 5억 + KIBO 기술보증 가능. 특허/기술력이 핵심입니다.",
            "B": "소상공인 Track B: 소진공 정책자금(연 2%, 최대 7천만원) + 청년이면 KODIT 특례보증. "
                 "크라우드펀딩(Wadiz)으로 초기 고객 확보도 가능.",
            "AB": "혼합 Track AB: 기술성분은 KIBO 보증, 사업체분은 소진공 자금 활용 가능. "
                  "Wadiz 크라우드펀딩으로 시장 검증도 추천.",
        }
        return summaries.get(track, "소진공(1357)에 문의하세요.")


# ─── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="금융 상품 매칭")
    parser.add_argument("--track", "-t", default="B", choices=["A", "B", "AB"])
    parser.add_argument("--keywords", "-k", nargs="*", default=[])
    parser.add_argument("--loan", action="store_true", help="융자/보증 우선")
    args = parser.parse_args()

    fm = FinancialMap()
    products = fm.match(track=args.track, keywords=args.keywords, need_loan=args.loan)
    print(fm.format_recommendation(products))
