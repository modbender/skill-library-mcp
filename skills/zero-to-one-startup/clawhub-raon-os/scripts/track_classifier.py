#!/usr/bin/env python3
"""
Raon OS — 트랙 자동 감지 모듈

Track A (기술창업/벤처): TIPS, R&D, 기술집약
Track B (소상공인/로컬): 자영업, 프랜차이즈, 로컬비즈
Track AB (혼합): 기술 기반 자영업, 푸드테크 등

Python 3.9+ compatible
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

# ─── 키워드 사전 ──────────────────────────────────────────────────────────────

TRACK_B_KEYWORDS = [
    "치킨", "카페", "음식점", "식당", "편의점", "뷰티", "미용", "헬스장",
    "소상공인", "자영업", "프랜차이즈", "상가", "매장", "가게",
    "유튜버", "크리에이터", "웹툰", "게임개발", "콘텐츠",
    "네일", "피부관리", "마사지", "인테리어", "세탁", "제과", "베이커리",
    "바", "술집", "고깃집", "분식", "떡볶이", "샌드위치", "도시락",
    "쇼핑몰", "온라인쇼핑", "스마트스토어", "블로그", "인스타",
]

TRACK_A_KEYWORDS = [
    "SaaS", "AI", "딥러닝", "하드웨어", "바이오", "반도체", "로봇",
    "B2B", "플랫폼", "API", "솔루션", "R&D", "특허", "기술창업",
    "머신러닝", "LLM", "클라우드", "데이터", "IoT", "블록체인",
    "바이오테크", "헬스테크", "핀테크", "애그테크", "모빌리티",
    "드론", "우주", "양자", "나노", "딥테크", "스타트업 투자",
    "TIPS", "팁스", "벤처", "엑셀러레이터", "VC 투자",
]

# 혼합 트랙 키워드 (AB)
TRACK_AB_KEYWORDS = [
    "푸드테크", "에듀테크", "리테일테크", "뷰티테크", "헬스케어앱",
    "배달앱", "O2O", "스마트팜", "스마트팩토리", "키오스크",
    "크리에이터 이코노미", "라이브커머스", "DTC",
]

# ─── 시스템 프롬프트 ──────────────────────────────────────────────────────────

TRACK_A_SYSTEM_PROMPT = """당신은 기술창업 전문 평가자입니다. TIPS, R&D, 기술혁신성 관점으로 평가하세요."""

TRACK_B_SYSTEM_PROMPT = """당신은 소상공인 창업 전문 컨설턴트입니다.
절대 "기술성", "R&D", "혁신성" 기준으로 평가하지 마세요.
대신 아래 5가지 기준으로 평가하세요:
1. 입지/상권 적합성 (25점)
2. 대표자 경험/전문성 (20점)
3. 서비스/상품 차별화 (25점)
4. 자금 조달 계획 (15점)
5. 지역 특화 가능성 (15점)

질문할 때는 쉬운 말을 사용하세요:
- "기술적 차별성" → "다른 가게보다 뭐가 더 특별한가요?"
- "시장 침투 전략" → "처음 손님을 어떻게 모을 계획인가요?"
- "수익 구조" → "한 달에 얼마나 벌 수 있을 것 같으세요?"
- "운영 리스크" → "장사하면서 어려울 것 같은 부분은 뭔가요?"
"""

TRACK_AB_SYSTEM_PROMPT = """당신은 소상공인 기반 기술창업 전문 컨설턴트입니다.
기술적 요소와 사업 실행력을 균형있게 평가하세요.
기술로 차별화하되, 현장 실행력과 상권 이해도도 중요합니다."""


# ─── TrackClassifier ─────────────────────────────────────────────────────────

class TrackClassifier:
    """트랙 자동 감지: 키워드 매칭 → LLM 분류 폴백."""

    def classify(self, text: str) -> str:
        """
        1. 키워드 매칭 먼저 (빠름)
        2. 판단 불가 시 LLM 분류 (raon_llm.chat 사용)
        반환: "A" | "B" | "AB"
        """
        # 1단계: 키워드 매칭
        track = self._keyword_classify(text)
        if track != "UNKNOWN":
            return track

        # 2단계: LLM 분류
        return self._llm_classify(text)

    def _keyword_classify(self, text: str) -> str:
        """키워드 기반 빠른 분류."""
        text_lower = text.lower()

        score_a = 0
        score_b = 0
        score_ab = 0

        for kw in TRACK_A_KEYWORDS:
            if kw.lower() in text_lower:
                score_a += 1

        for kw in TRACK_B_KEYWORDS:
            if kw.lower() in text_lower:
                score_b += 1

        for kw in TRACK_AB_KEYWORDS:
            if kw.lower() in text_lower:
                score_ab += 1

        # 혼합 키워드가 있고, A/B 모두 점수 있으면 AB
        if score_ab >= 1 and (score_a >= 1 or score_b >= 1):
            return "AB"
        if score_a >= 1 and score_b >= 1:
            return "AB"
        if score_b >= 2:
            return "B"
        if score_a >= 1:
            return "A"
        if score_b == 1:
            return "B"

        return "UNKNOWN"

    def _llm_classify(self, text: str) -> str:
        """LLM 기반 트랙 분류. 실패 시 'B' 기본값."""
        try:
            from raon_llm import chat, prompt_to_messages

            prompt = (
                "다음 창업 아이템이 어떤 트랙에 해당하는지 분류해.\n\n"
                "트랙 정의:\n"
                "- A: 기술창업/벤처 (TIPS, R&D, 기술집약, SaaS, AI, 바이오 등)\n"
                "- B: 소상공인/로컬 (자영업, 프랜차이즈, 음식점, 카페, 뷰티샵 등)\n"
                "- AB: 혼합 (푸드테크, 뷰티테크, 스마트스토어 기술 등 기술+자영업 결합)\n\n"
                f"창업 아이템:\n{text[:1000]}\n\n"
                "답변은 A, B, AB 중 하나만 (다른 설명 없이):"
            )

            result = chat(prompt_to_messages(prompt))
            if result:
                result_clean = result.strip().upper()
                if "AB" in result_clean:
                    return "AB"
                if result_clean.startswith("A"):
                    return "A"
                if result_clean.startswith("B"):
                    return "B"
        except Exception as e:
            print(f"[TrackClassifier] LLM 분류 실패: {e}", file=sys.stderr)

        # 기본값: B (소상공인 안전 처리)
        return "B"

    def get_track_prompt(self, track: str) -> str:
        """트랙별 평가 시스템 프롬프트 반환."""
        if track == "B":
            return TRACK_B_SYSTEM_PROMPT
        if track == "AB":
            return TRACK_AB_SYSTEM_PROMPT
        return TRACK_A_SYSTEM_PROMPT

    def get_track_label(self, track: str) -> str:
        """트랙 한글 라벨."""
        labels = {
            "A": "기술창업/벤처 (Track A)",
            "B": "소상공인/로컬 (Track B)",
            "AB": "기술+소상공인 혼합 (Track AB)",
        }
        return labels.get(track, track)


# ─── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="트랙 자동 감지")
    parser.add_argument("--text", "-t", required=True, help="창업 아이템 설명")
    args = parser.parse_args()

    clf = TrackClassifier()
    track = clf.classify(args.text)
    print(f"트랙: {clf.get_track_label(track)}")
    print(f"시스템 프롬프트:\n{clf.get_track_prompt(track)}")
