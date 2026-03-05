#!/usr/bin/env python3
"""
Browser session management for Youmind.
Provides a stateful page session abstraction (not used by default CLI flow).
"""

import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

from patchright.sync_api import BrowserContext

# Add scripts directory to import path
sys.path.insert(0, str(Path(__file__).parent))

from browser_utils import StealthUtils
from config import QUERY_INPUT_SELECTORS, RESPONSE_SELECTORS, THINKING_SELECTORS, YOUMIND_BOARD_URL_PREFIX


class BrowserSession:
    """Represents a single page session connected to one Youmind board."""

    def __init__(self, session_id: str, context: BrowserContext, board_url: str):
        self.id = session_id
        self.created_at = time.time()
        self.last_activity = time.time()
        self.message_count = 0
        self.board_url = board_url
        self.context = context
        self.page = None
        self.stealth = StealthUtils()
        self._initialize()

    def _initialize(self):
        print(f"🚀 Creating session {self.id}...")

        if not self.board_url.startswith(YOUMIND_BOARD_URL_PREFIX):
            raise RuntimeError(f"Invalid Youmind board URL: {self.board_url}")

        self.page = self.context.new_page()
        self.page.goto(self.board_url, wait_until="domcontentloaded", timeout=30000)

        if "sign-in" in self.page.url or "youmind.com" not in self.page.url:
            raise RuntimeError("Authentication required. Run auth_manager.py setup first.")

        self._wait_for_ready()
        self.stealth.random_mouse_movement(self.page)
        self.stealth.random_delay(250, 550)
        print(f"✅ Session {self.id} ready")

    def _wait_for_ready(self):
        for selector in QUERY_INPUT_SELECTORS:
            try:
                self.page.wait_for_selector(selector, timeout=8000, state="visible")
                return
            except Exception:
                continue
        raise RuntimeError("Could not find Youmind chat input")

    def _snapshot_latest_response(self) -> Optional[str]:
        for selector in RESPONSE_SELECTORS:
            try:
                responses = self.page.query_selector_all(selector)
                if responses:
                    text = responses[-1].inner_text().strip()
                    if text:
                        return text
            except Exception:
                continue
        return None

    def _is_thinking(self) -> bool:
        for selector in THINKING_SELECTORS:
            try:
                nodes = self.page.query_selector_all(selector)
                if any(node.is_visible() for node in nodes):
                    return True
            except Exception:
                continue
        return False

    def _first_input_selector(self) -> str:
        for selector in QUERY_INPUT_SELECTORS:
            try:
                self.page.wait_for_selector(selector, timeout=3000, state="visible")
                return selector
            except Exception:
                continue
        raise RuntimeError("Could not locate chat input")

    def ask(self, question: str) -> Dict[str, Any]:
        try:
            self.last_activity = time.time()
            self.message_count += 1

            print(f"💬 [{self.id}] Asking: {question}")
            previous_answer = self._snapshot_latest_response()
            input_selector = self._first_input_selector()

            self.stealth.realistic_click(self.page, input_selector)
            self.stealth.human_type(self.page, input_selector, question)
            self.stealth.random_delay(300, 700)
            self.page.keyboard.press("Enter")

            answer = self._wait_for_latest_answer(previous_answer)
            if not answer:
                raise RuntimeError("Empty response from Youmind")

            return {
                "status": "success",
                "question": question,
                "answer": answer,
                "session_id": self.id,
                "board_url": self.board_url,
            }

        except Exception as e:
            return {
                "status": "error",
                "question": question,
                "error": str(e),
                "session_id": self.id,
            }

    def _wait_for_latest_answer(self, previous_answer: Optional[str], timeout: int = 120) -> str:
        start_time = time.time()
        last_candidate = None
        stable_count = 0

        while time.time() - start_time < timeout:
            if self._is_thinking():
                time.sleep(0.6)
                continue

            candidate = self._snapshot_latest_response()
            if candidate and candidate != previous_answer:
                if candidate == last_candidate:
                    stable_count += 1
                    if stable_count >= 3:
                        return candidate
                else:
                    stable_count = 1
                    last_candidate = candidate

            time.sleep(0.5)

        raise TimeoutError(f"No response received within {timeout} seconds")

    def reset(self):
        self.page.reload(wait_until="domcontentloaded")
        self._wait_for_ready()
        old_count = self.message_count
        self.message_count = 0
        self.last_activity = time.time()
        return old_count

    def close(self):
        if self.page:
            try:
                self.page.close()
            except Exception:
                pass

    def get_info(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "created_at": self.created_at,
            "last_activity": self.last_activity,
            "age_seconds": time.time() - self.created_at,
            "inactive_seconds": time.time() - self.last_activity,
            "message_count": self.message_count,
            "board_url": self.board_url,
        }

    def is_expired(self, timeout_seconds: int = 900) -> bool:
        return (time.time() - self.last_activity) > timeout_seconds


if __name__ == "__main__":
    print("BrowserSession module - use ask_question.py for CLI usage")
