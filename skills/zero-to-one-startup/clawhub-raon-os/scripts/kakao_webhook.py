#!/usr/bin/env python3
"""
Raon OS — 카카오 i 오픈빌더 웹훅 서버

카카오 i 오픈빌더 (Kakao i Open Builder) 연동
환경변수: KAKAO_CALLBACK_SECRET (선택, 웹훅 검증용)

설정법:
1. https://i.kakao.com 접속
2. 카카오 비즈니스 계정으로 봇 생성
3. "폴백 블록" 웹훅 URL에 서버주소/kakao 입력
4. KAKAO_CALLBACK_SECRET 설정 (선택)

웹훅 수신 형식 (카카오 오픈빌더 v2):
POST /kakao
{
  "userRequest": {
    "utterance": "사용자 입력 텍스트",
    "user": {"id": "unique_user_id"}
  },
  "bot": {"id": "bot_id"},
  "intent": {"name": "블록명"}
}

응답 형식:
{
  "version": "2.0",
  "template": {
    "outputs": [
      {"simpleText": {"text": "응답 텍스트"}}
    ]
  }
}

Python 3.9+ compatible
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import sys
from pathlib import Path
from typing import Optional

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

# ─── 상수 ────────────────────────────────────────────────────────────────────

KAKAO_TEXT_LIMIT = 900  # 카카오 SimpleText 최대 1000자, 안전 마진 100자
MAX_OUTPUTS = 5  # 카카오 응답 최대 outputs 개수

GREETING_MESSAGE = """안녕하세요! 저는 라온이에요 🌅

창업 아이디어나 사업계획서를 알려주시면 맞춤 분석을 해드려요.

💡 이런 걸 도와드릴 수 있어요:
• 사업계획서 평가 (TIPS 기준)
• 소상공인 창업 컨설팅
• 정부 지원사업 매칭
• 금융 상품 추천

어떤 창업을 준비 중이신가요?"""


class KakaoWebhook:
    """카카오 i 오픈빌더 웹훅 처리 클래스."""

    def __init__(self, rag=None):
        self.secret = os.environ.get("KAKAO_CALLBACK_SECRET", "")
        self.rag = rag  # AgenticRAG instance (lazy init)
        self.sessions = {}  # user_id → conversation context

    def verify_signature(self, body: bytes, signature: str) -> bool:
        """
        KAKAO_CALLBACK_SECRET으로 요청 진위 확인.
        시크릿 미설정 시 요청 거부 (보안 강화).
        """
        if not self.secret:
            # 시크릿 미설정 = 인증 불가 → 거부
            return False

        expected = hmac.new(
            self.secret.encode("utf-8"),
            body,
            hashlib.sha1,
        ).hexdigest()
        return hmac.compare_digest(expected, signature or "")

    def process(self, body: dict) -> dict:
        """
        카카오 웹훅 요청 처리.

        1. utterance 추출
        2. 트랙 감지 (TrackClassifier)
        3. AgenticRAG 실행 또는 Ollama 폴백
        4. 카카오 응답 형식으로 변환
        5. 텍스트 1000자 초과 시 분할
        """
        # utterance 추출
        utterance = ""
        user_id = "unknown"
        try:
            user_request = body.get("userRequest", {})
            raw = user_request.get("utterance", "")
        # 프롬프트 인젝션 방지: 길이 제한 + 패턴 차단
        raw = raw[:2000]
        for _pat in ("ignore previous", "ignore all", "disregard", "system:", "[INST]", "###"):
            raw = raw.replace(_pat, "")
        utterance = raw.strip()
            user_obj = user_request.get("user", {})
            user_id = user_obj.get("id", "unknown")
        except Exception:
            pass

        if not utterance:
            return self.format_response("메시지를 입력해주세요 😊")

        # 인사말 처리
        if utterance.lower() in ("안녕", "안녕하세요", "hi", "hello", "시작", "처음부터"):
            # 세션 초기화
            self.sessions.pop(user_id, None)
            return self.format_response(GREETING_MESSAGE, buttons=["소상공인 창업", "기술 스타트업", "지원사업 찾기"])

        # 트랙 감지
        track = "B"  # 기본값
        try:
            from track_classifier import TrackClassifier
            clf = TrackClassifier()
            track = clf.classify(utterance)
        except Exception as e:
            print(f"[kakao_webhook] TrackClassifier 실패: {e}", file=sys.stderr)

        # 세션 컨텍스트 업데이트
        if user_id not in self.sessions:
            self.sessions[user_id] = {
                "track": track,
                "history": [],
            }
        session = self.sessions[user_id]
        # 트랙이 새로 감지되면 업데이트
        if track != "B" or not session.get("track"):
            session["track"] = track

        current_track = session.get("track", "B")

        # 금융 정보 요청 처리
        financial_keywords = ["융자", "보증", "대출", "지원금", "자금", "크라우드펀딩", "투자"]
        if any(kw in utterance for kw in financial_keywords):
            try:
                from financial_map import FinancialMap
                fm = FinancialMap()
                products = fm.match(track=current_track, need_loan=True)
                response_text = fm.format_recommendation(products, startup_info=utterance)
                buttons = self.get_quick_buttons(current_track)
                return self.format_response(response_text, buttons=buttons)
            except Exception as e:
                print(f"[kakao_webhook] FinancialMap 실패: {e}", file=sys.stderr)

        # AgenticRAG 시도
        answer = None
        strategy = "direct"

        if self.rag:
            try:
                result = self.rag.run(utterance)
                answer = result.get("answer", "")
                strategy = result.get("strategy_used", "rag")
            except Exception as e:
                print(f"[kakao_webhook] RAG 실패: {e}", file=sys.stderr)
                answer = None

        # LLM 직접 호출 폴백
        if not answer:
            try:
                from track_classifier import TrackClassifier, TRACK_B_SYSTEM_PROMPT, TRACK_A_SYSTEM_PROMPT
                from raon_llm import chat, prompt_to_messages

                # 트랙별 시스템 프롬프트
                clf_inst = TrackClassifier()
                system_prompt = clf_inst.get_track_prompt(current_track)

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": utterance},
                ]

                # 이전 대화 히스토리 추가 (최근 3턴)
                history = session.get("history", [])[-6:]
                if history:
                    messages = [messages[0]] + history + [messages[-1]]

                answer = chat(messages)
                strategy = "llm"
            except Exception as e:
                print(f"[kakao_webhook] LLM 폴백 실패: {e}", file=sys.stderr)
                answer = "죄송해요, 지금 일시적으로 응답이 어렵습니다. 잠시 후 다시 시도해주세요 😊"

        # 세션 히스토리 업데이트
        session.setdefault("history", []).extend([
            {"role": "user", "content": utterance},
            {"role": "assistant", "content": answer or ""},
        ])
        # 히스토리 최대 20턴 유지
        if len(session["history"]) > 20:
            session["history"] = session["history"][-20:]

        buttons = self.get_quick_buttons(current_track)
        return self.format_response(answer or "응답을 생성할 수 없습니다.", buttons=buttons)

    def format_response(self, text: str, buttons: Optional[list] = None) -> dict:
        """
        카카오 오픈빌더 v2 응답 포맷 생성.
        텍스트 900자 초과 시 분할.
        """
        outputs = []

        # 900자씩 분할
        chunks = []
        remaining = text
        while remaining:
            chunks.append(remaining[:KAKAO_TEXT_LIMIT])
            remaining = remaining[KAKAO_TEXT_LIMIT:]

        # 최대 MAX_OUTPUTS개
        for chunk in chunks[:MAX_OUTPUTS]:
            outputs.append({"simpleText": {"text": chunk}})

        result = {"version": "2.0", "template": {"outputs": outputs}}

        # 빠른 응답 버튼 (선택)
        if buttons:
            result["template"]["quickReplies"] = [
                {"label": b, "action": "message", "messageText": b}
                for b in buttons[:5]  # 카카오 최대 5개
            ]

        return result

    def get_quick_buttons(self, track: str) -> list:
        """트랙별 빠른 응답 버튼."""
        if track == "B":
            return ["융자/보증 알아보기", "지원사업 찾기", "처음부터"]
        if track == "AB":
            return ["금융 지원 찾기", "지원사업 매칭", "처음부터"]
        return ["TIPS 신청 방법", "투자자 매칭", "처음부터"]

    def clear_session(self, user_id: str) -> None:
        """사용자 세션 초기화."""
        self.sessions.pop(user_id, None)

    def get_session_count(self) -> int:
        """활성 세션 수 반환."""
        return len(self.sessions)


# ─── CLI 테스트 ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("카카오 웹훅 모듈 테스트")

    hook = KakaoWebhook()

    # 테스트 요청
    test_body = {
        "userRequest": {
            "utterance": "치킨집 창업하고 싶은데 어떻게 해야 하나요?",
            "user": {"id": "test_user_001"},
        },
        "bot": {"id": "test_bot"},
        "intent": {"name": "폴백 블록"},
    }

    result = hook.process(test_body)
    print(json.dumps(result, ensure_ascii=False, indent=2))
