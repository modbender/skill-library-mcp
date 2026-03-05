#!/usr/bin/env python3
"""
/* 🌌 Aoineco-Verified | Multi-Agent Collective Proprietary Skill */
S-DNA: AOI-2026-0213-SDNA-TG01-REV4

TokenGuard v1.5 — High-Performance Atomic Quota Manager
Aoineco & Co. | $7 Bootstrap Protocol

Function:
1. Prevents 429 Errors by pre-flight check against TPM (Tokens Per Minute) and RPM (Requests Per Minute).
2. Uses Atomic Writes to prevent state file corruption during crashes/concurrency.
3. Prioritizes Compaction tasks to avoid Context Death Spiral.
4. Handles Unknown Models specifically with a safety net quota.
"""

import sys
import json
import time
import os
import shutil
import tempfile
from dataclasses import dataclass, asdict

# --- Configuration ---

@dataclass
class GuardDecision:
    action: str  # "proceed", "block", "wait", "fallback"
    estimated_tokens: int
    reason: str
    quota_remaining: float  # Remaining tokens in current window
    quota_used_pct: float   # 0.0 to 1.0+
    fallback_model: str = None
    wait_seconds: int = 0

@dataclass
class ModelQuota:
    tpm_limit: int
    rpm_limit: int = 15  # Default RPM limit (Requests Per Minute)
    warn_threshold: float = 0.7
    block_threshold: float = 0.9

class TokenGuard:
    # Default quotas (tokens per minute & requests per minute)
    DEFAULT_QUOTAS = {
        "gemini-3-flash":   ModelQuota(tpm_limit=1_000_000, rpm_limit=20, warn_threshold=0.7, block_threshold=0.9),
        "gemini-3-pro":     ModelQuota(tpm_limit=2_000_000, rpm_limit=60),
        "claude-haiku":     ModelQuota(tpm_limit=50_000, rpm_limit=50),
        "claude-sonnet":    ModelQuota(tpm_limit=200_000, rpm_limit=50),
        "claude-opus":      ModelQuota(tpm_limit=200_000, rpm_limit=50),
        "gpt-4o":           ModelQuota(tpm_limit=800_000, rpm_limit=500),
        "deepseek":         ModelQuota(tpm_limit=1_000_000, rpm_limit=60),
    }

    # Backup quota for unknown models (Safety Net)
    UNKNOWN_MODEL_QUOTA = ModelQuota(tpm_limit=50_000, rpm_limit=5)

    def __init__(self, state_file=None):
        if state_file is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if not os.path.exists(base_dir):
                os.makedirs(base_dir, exist_ok=True)
            self.state_file = os.path.join(base_dir, "state.json")
        else:
            self.state_file = state_file
        
        self.stats = self._load_state()
        self.request_timestamps = [] # In-memory RPM tracking (volatile)

    def _load_state(self):
        """Load state safely. If corrupted, reset."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    if time.time() - data.get("window_start", 0) > 60:
                        return self._init_state()
                    return data
            except (json.JSONDecodeError, OSError):
                # Corruption detected, reset state
                return self._init_state()
        return self._init_state()

    def _init_state(self):
        return {
            "window_start": time.time(),
            "usage": {}, # model_name -> tokens_used
            "requests": {}, # model_name -> request_count
            "blocked": 0,
            "proceeded": 0
        }

    def _save_state_atomic(self):
        """
        Atomic Write Pattern: Write to temp file first, then atomic rename.
        Prevents partial writes/corruption if process crashes.
        """
        try:
            # Create a localized temp file in the same directory (ensures same filesystem for atomic rename)
            dir_name = os.path.dirname(self.state_file)
            with tempfile.NamedTemporaryFile('w', dir=dir_name, delete=False) as tf:
                json.dump(self.stats, tf, indent=2)
                temp_name = tf.name
            
            # Atomic replace
            os.replace(temp_name, self.state_file)
        except OSError:
            pass # Creating temp file failed, skip save (prefer running over crashing)

    def _resolve_model_alias(self, model_name: str) -> str:
        if "gemini" in model_name and "flash" in model_name: return "gemini-3-flash"
        if "gemini" in model_name and "pro" in model_name: return "gemini-3-pro"
        if "haiku" in model_name: return "claude-haiku"
        if "sonnet" in model_name: return "claude-sonnet"
        if "opus" in model_name: return "claude-opus"
        if "gpt-4" in model_name: return "gpt-4o"
        if "deepseek" in model_name: return "deepseek"
        return model_name

    def _estimate_tokens(self, text: str) -> int:
        return int(len(text) / 2.5) + 10

    def _find_fallback(self, current_model: str, required_tokens: int) -> str:
        fallback_chain = {
            "claude-opus": "claude-sonnet",
            "claude-sonnet": "claude-haiku",
            "gpt-4o": "gpt-4o-mini",
            "gemini-3-pro": "gemini-3-flash"
        }
        return fallback_chain.get(current_model)

    def check_quota(self, model: str, prompt_text: str) -> GuardDecision:
        resolved_model = self._resolve_model_alias(model)
        
        # 1. Quota Selection
        if resolved_model in self.DEFAULT_QUOTAS:
            quota = self.DEFAULT_QUOTAS[resolved_model]
        else:
            quota = self.UNKNOWN_MODEL_QUOTA

        # 2. Reset Window Check
        now = time.time()
        if now - self.stats["window_start"] > 60:
            self.stats = self._init_state()
            self.request_timestamps = []
        
        # 3. RPM Check (Rate Limit) - Global for simplicity in this version
        self.request_timestamps = [t for t in self.request_timestamps if now - t < 60]
        model_rpm = self.stats["requests"].get(resolved_model, 0)
        
        if model_rpm >= quota.rpm_limit:
             return GuardDecision(
                action="wait",
                estimated_tokens=0,
                reason=f"⛔ RPM Limit Exceeded ({model_rpm}/{quota.rpm_limit}). Cooling down.",
                quota_remaining=0,
                quota_used_pct=1.0,
                wait_seconds=5
            )

        # 4. TPM Check
        est_tokens = self._estimate_tokens(prompt_text)
        used = self.stats["usage"].get(resolved_model, 0)
        remaining = quota.tpm_limit - used
        usage_pct = used / quota.tpm_limit if quota.tpm_limit > 0 else 1.0

        # 5. Decision Logic
        if usage_pct >= quota.block_threshold or (used + est_tokens) > quota.tpm_limit:
            
            # Compaction Priority
            is_compaction = "summariz" in prompt_text.lower() or "consolidate" in prompt_text.lower()
            if is_compaction and usage_pct < 0.98:
                 self.stats["proceeded"] += 1
                 self.stats["usage"][resolved_model] = used + est_tokens
                 self.stats["requests"][resolved_model] = model_rpm + 1
                 self.request_timestamps.append(now)
                 self._save_state_atomic() # Atomic Save
                 return GuardDecision(
                    action="proceed",
                    estimated_tokens=est_tokens,
                    reason=f"⚠️ Quota Full ({usage_pct:.0%}), but COMPACTION detected.",
                    quota_remaining=remaining,
                    quota_used_pct=usage_pct,
                )

            # Fallback
            fallback = self._find_fallback(resolved_model, est_tokens)
            if fallback:
                self.stats["blocked"] += 1
                return GuardDecision(
                    action="fallback",
                    estimated_tokens=est_tokens,
                    reason=f"Fallback suggested ({usage_pct:.1%}).",
                    quota_remaining=remaining,
                    quota_used_pct=usage_pct,
                    fallback_model=fallback
                )
            
            # Block/Wait
            self.stats["blocked"] += 1
            return GuardDecision(
                action="wait",
                estimated_tokens=est_tokens,
                reason=f"Quota exceeded ({usage_pct:.1%}). Please wait.",
                quota_remaining=remaining,
                quota_used_pct=usage_pct,
                wait_seconds=int(60 - (now - self.stats["window_start"]))
            )

        # 6. Proceed
        self.stats["usage"][resolved_model] = used + est_tokens
        self.stats["requests"][resolved_model] = model_rpm + 1
        self.stats["proceeded"] += 1
        self.request_timestamps.append(now)
        self._save_state_atomic() # Atomic Save

        return GuardDecision(
            action="proceed",
            estimated_tokens=est_tokens,
            reason="Quota OK",
            quota_remaining=remaining - est_tokens,
            quota_used_pct=usage_pct
        )

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: token_guard.py <model> <prompt_text>"}), indent=2)
        sys.exit(1)
        
    model = sys.argv[1]
    prompt = " ".join(sys.argv[2:])
    
    guard = TokenGuard()
    decision = guard.check_quota(model, prompt)
    print(json.dumps(asdict(decision), indent=2))
