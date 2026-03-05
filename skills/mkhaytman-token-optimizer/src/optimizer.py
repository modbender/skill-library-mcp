from __future__ import annotations

import json
import re
import subprocess
from collections import Counter, defaultdict
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cleanup import evaluate_session
from compression import summarize_transcript_events
from models import analyze_task, select_optimal_model


class TokenOptimizer:
    def __init__(self, config: dict, openclaw_home: Path | None = None):
        self.config = config
        self.openclaw_home = openclaw_home or Path.home() / ".openclaw"
        self.sessions_dir = self.openclaw_home / "agents/main/sessions"
        self.workspace_dir = self.openclaw_home / "workspace"
        self.output_dir = self.workspace_dir / "token-usage"
        self.compressed_dir = self.output_dir / "compressed"

    def _run_json(self, args: list[str]) -> dict:
        proc = subprocess.run(args, capture_output=True, text=True, check=True)
        return json.loads(proc.stdout)

    def get_sessions(self) -> list[dict]:
        data = self._run_json(["openclaw", "sessions", "--json"])
        sessions = data.get("sessions", []) if isinstance(data, dict) else []
        return self.normalize_sessions(sessions)

    @staticmethod
    def normalize_sessions(sessions: list[dict]) -> list[dict]:
        # openclaw sessions can include both base keys and run keys that point to the same
        # session snapshot; collapse obvious duplicates to avoid double counting.
        best: dict[tuple[str, int, int], dict] = {}
        for s in sessions:
            sid = str(s.get("sessionId") or "")
            updated = int(s.get("updatedAt") or 0)
            total = int(s.get("totalTokens") or 0)
            sig = (sid, updated, total)
            current = best.get(sig)
            if current is None:
                best[sig] = s
                continue

            key_new = str(s.get("key") or "")
            key_cur = str(current.get("key") or "")
            # Prefer canonical key over run key when both exist.
            if ":run:" in key_cur and ":run:" not in key_new:
                best[sig] = s

        return list(best.values())

    def get_usage_cost(self, days: int = 30) -> dict | None:
        try:
            data = self._run_json(["openclaw", "gateway", "usage-cost", "--days", str(days), "--json"])
            return data if isinstance(data, dict) else None
        except Exception:
            return None

    @staticmethod
    def parse_period(period: str) -> timedelta:
        m = re.match(r"^(\d+)([dhwm])$", period.strip().lower())
        if not m:
            raise ValueError("Invalid period. Use 1d, 7d, 30d, 12h, 2w.")
        val = int(m.group(1))
        unit = m.group(2)
        if unit == "h":
            return timedelta(hours=val)
        if unit == "d":
            return timedelta(days=val)
        if unit == "w":
            return timedelta(weeks=val)
        if unit == "m":
            return timedelta(days=30 * val)
        raise ValueError("Unsupported period unit")

    def filter_sessions_by_period(self, sessions: list[dict], period: str) -> list[dict]:
        delta = self.parse_period(period)
        cutoff_ms = int((datetime.now(timezone.utc) - delta).timestamp() * 1000)
        return [s for s in sessions if int(s.get("updatedAt") or 0) >= cutoff_ms]

    def transcript_events(self, session_id: str) -> list[dict]:
        path = self.sessions_dir / f"{session_id}.jsonl"
        if not path.exists():
            return []
        out: list[dict] = []
        with path.open("r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except Exception:
                    continue
        return out

    def collect_tool_stats(self, sessions: list[dict]) -> dict:
        tool_calls = Counter()
        tool_token_est = Counter()
        duplicate_calls = Counter()
        large_tool_outputs = Counter()

        large_cutoff = int(self.config["toolOptimization"].get("largeOutputChars", 4000))

        for s in sessions:
            sid = s.get("sessionId")
            if not sid:
                continue

            seen = set()
            events = self.transcript_events(str(sid))
            for event in events:
                if event.get("type") != "message":
                    continue
                msg = event.get("message")
                if not isinstance(msg, dict):
                    continue

                role = msg.get("role")
                if role == "assistant":
                    usage = msg.get("usage") if isinstance(msg.get("usage"), dict) else {}
                    total_t = int(usage.get("totalTokens") or 0)
                    names = []
                    for part in msg.get("content", []):
                        if isinstance(part, dict) and part.get("type") == "toolCall":
                            name = part.get("name")
                            args = part.get("arguments")
                            if isinstance(name, str):
                                names.append((name, args))
                    if names:
                        share = total_t / max(1, len(names))
                        for name, args in names:
                            tool_calls[name] += 1
                            tool_token_est[name] += int(share)
                            key = f"{name}:{json.dumps(args, sort_keys=True, ensure_ascii=True)}"
                            if key in seen:
                                duplicate_calls[name] += 1
                            seen.add(key)

                elif role == "toolResult":
                    text_len = 0
                    content = msg.get("content")
                    if isinstance(content, list):
                        for part in content:
                            if isinstance(part, dict) and part.get("type") == "text":
                                text = part.get("text")
                                if isinstance(text, str):
                                    text_len += len(text)
                    if text_len >= large_cutoff:
                        name = str(msg.get("toolName") or "unknown")
                        large_tool_outputs[name] += 1

        return {
            "toolCalls": dict(tool_calls),
            "toolTokenEstimate": dict(tool_token_est),
            "duplicateCalls": dict(duplicate_calls),
            "largeToolOutputs": dict(large_tool_outputs),
        }

    def model_optimization_opportunities(self, sessions: list[dict]) -> dict:
        opportunities = []
        potential_savings = 0

        prefs = self.config.get("models", {}).get("preferences", {})
        simple_target = prefs.get("simple", "anthropic/claude-3-5-sonnet-latest")

        for s in sessions:
            key = str(s.get("key") or "")
            text = key.lower()
            model = str(s.get("model") or "")
            tokens = int(s.get("totalTokens") or 0)
            context_tokens = int(s.get("contextTokens") or 200000)

            complexity = analyze_task(text)
            recommended = select_optimal_model(text, context_tokens, prefs)
            if "opus" in model.lower() and complexity.simple:
                save = int(tokens * 0.30)
                potential_savings += save
                opportunities.append(
                    {
                        "sessionKey": key,
                        "currentModel": model,
                        "recommendedModel": recommended or simple_target,
                        "estimatedTokenSavings": save,
                        "reason": "Simple task running on Opus model",
                    }
                )

        opportunities.sort(key=lambda x: x["estimatedTokenSavings"], reverse=True)
        return {
            "count": len(opportunities),
            "estimatedSavings": potential_savings,
            "items": opportunities[:20],
        }

    def analyze(self, period: str = "7d") -> dict:
        sessions = self.get_sessions()
        recent = self.filter_sessions_by_period(sessions, period)

        total_tokens = sum(int(s.get("totalTokens") or 0) for s in recent)
        by_model = Counter(str(s.get("model") or "unknown") for s in recent)
        near_limit = [
            s
            for s in recent
            if (int(s.get("contextTokens") or 0) > 0)
            and (int(s.get("totalTokens") or 0) / int(s.get("contextTokens") or 1) >= self.config["alerts"]["warnAt"])
        ]

        tool_stats = self.collect_tool_stats(recent)
        model_opt = self.model_optimization_opportunities(recent)

        duplicate_total = sum(tool_stats["duplicateCalls"].values())
        duplicate_token_savings = int(sum(tool_stats["toolTokenEstimate"].values()) * 0.15) if duplicate_total else 0
        large_output_count = sum(tool_stats["largeToolOutputs"].values())
        truncation_savings = large_output_count * 1200

        estimated_total_savings = model_opt["estimatedSavings"] + duplicate_token_savings + truncation_savings

        top_sessions = sorted(
            recent,
            key=lambda s: int(s.get("totalTokens") or 0),
            reverse=True,
        )[:10]

        usage_cost = self.get_usage_cost(days=max(1, int(self.parse_period(period).days or 1)))

        return {
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "period": period,
            "sessionsAnalyzed": len(recent),
            "totalTokens": total_tokens,
            "nearLimitSessions": len(near_limit),
            "topSessions": [
                {
                    "sessionKey": s.get("key"),
                    "model": s.get("model"),
                    "totalTokens": int(s.get("totalTokens") or 0),
                    "contextTokens": int(s.get("contextTokens") or 0),
                }
                for s in top_sessions
            ],
            "byModel": dict(by_model),
            "toolStats": tool_stats,
            "modelOptimization": model_opt,
            "estimatedSavings": {
                "modelSelection": model_opt["estimatedSavings"],
                "deduplication": duplicate_token_savings,
                "truncation": truncation_savings,
                "total": estimated_total_savings,
            },
            "usageCost": usage_cost,
        }

    def health_check(self, active_minutes: int | None = None) -> dict:
        sessions = self.get_sessions()
        if active_minutes is not None:
            threshold_ms = active_minutes * 60000
            sessions = [s for s in sessions if int(s.get("ageMs") or 0) <= threshold_ms]

        warn_at = float(self.config["alerts"]["warnAt"])
        urgent_at = float(self.config["alerts"]["urgentAt"])
        max_idle = int(self.config["sessionManagement"]["maxIdleMinutes"])

        health = [evaluate_session(s, warn_at=warn_at, urgent_at=urgent_at, max_idle_minutes=max_idle) for s in sessions]
        by_status = Counter(h.status for h in health)

        return {
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "count": len(health),
            "statusSummary": dict(by_status),
            "sessions": [asdict(h) for h in health],
        }

    def cleanup_plan(self) -> dict:
        report = self.health_check()
        sessions = report["sessions"]
        stuck = [s for s in sessions if s["status"] == "stuck"]
        urgent = [s for s in sessions if s["status"] == "urgent"]

        actions: list[dict] = []
        for s in stuck[:20]:
            actions.append(
                {
                    "action": "restart_gateway",
                    "sessionKey": s["key"],
                    "reason": s["reason"],
                }
            )

        for s in urgent[:20]:
            actions.append(
                {
                    "action": "recommend_reset",
                    "sessionKey": s["key"],
                    "reason": s["reason"],
                }
            )

        return {
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "stuckCount": len(stuck),
            "urgentCount": len(urgent),
            "actions": actions,
        }

    def apply_cleanup(self) -> dict:
        plan = self.cleanup_plan()
        if plan["stuckCount"] <= 0:
            return {
                "applied": False,
                "message": "No stuck sessions detected; no restart applied.",
                "plan": plan,
            }

        subprocess.run(["openclaw", "gateway", "restart"], check=False)
        return {
            "applied": True,
            "message": "Gateway restart requested due to stuck sessions near context limit.",
            "plan": plan,
        }

    def compress_session(self, session_key: str | None = None, threshold: float = 0.8, keep_recent: int = 20) -> dict:
        sessions = self.get_sessions()
        target = None

        if session_key:
            q = session_key.lower()
            for s in sessions:
                k = str(s.get("key") or "").lower()
                if k == q or q in k:
                    target = s
                    break
        else:
            target = next((s for s in sessions if s.get("key") == "agent:main:main"), None)
            if target is None and sessions:
                target = sorted(sessions, key=lambda x: int(x.get("updatedAt") or 0), reverse=True)[0]

        if target is None:
            raise RuntimeError("No matching session found")

        total = int(target.get("totalTokens") or 0)
        context = int(target.get("contextTokens") or 0)
        utilization = (float(total) / float(context)) if context > 0 else 0.0

        sid = str(target.get("sessionId") or "")
        events = self.transcript_events(sid)
        summary = summarize_transcript_events(events, keep_recent=keep_recent)

        self.compressed_dir.mkdir(parents=True, exist_ok=True)
        out_path = self.compressed_dir / f"{sid}-compressed.md"

        lines = [
            f"# Compressed Context: {target.get('key')}",
            "",
            f"- Session ID: `{sid}`",
            f"- Model: `{target.get('model')}`",
            f"- Tokens: `{total}/{context}` ({utilization:.0%})",
            "",
            "## Original Task",
            summary.get("firstUser", "(no user prompt found)"),
            "",
            "## Tool Call Summary",
        ]

        tool_calls = summary.get("toolCalls", {})
        if tool_calls:
            for name, count in sorted(tool_calls.items(), key=lambda kv: kv[1], reverse=True):
                lines.append(f"- `{name}`: {count}")
        else:
            lines.append("- No tool calls detected.")

        lines.extend(["", "## Recent Conversation", ""])
        recent = summary.get("recent", [])
        if recent:
            for item in recent:
                role = item.get("role", "unknown")
                text = item.get("text", "")
                lines.append(f"- **{role}**: {text}")
        else:
            lines.append("- No recent text messages detected.")

        lines.extend(
            [
                "",
                "## Compression Guidance",
                "- Keep this file in context, not the full raw transcript.",
                "- Re-run `token-optimize --compress` after major tool-heavy steps.",
                "- If utilization remains high, start a fresh session and continue from this summary.",
            ]
        )

        out_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")

        return {
            "sessionKey": target.get("key"),
            "sessionId": sid,
            "utilization": utilization,
            "threshold": threshold,
            "compressed": utilization >= threshold,
            "output": str(out_path),
        }

    def preflight_optimize(self, actions: list[dict], session_limit: int = 180000) -> dict:
        # Lightweight estimator based on operation type hints.
        costs = {
            "web_search": 4000,
            "web_fetch": 10000,
            "browser": 15000,
            "read": 6000,
            "write": 2000,
            "sessions_spawn": 12000,
            "summarize": 18000,
        }

        current = 0
        session_index = 1
        planned = []

        for action in actions:
            kind = str(action.get("type") or action.get("tool") or "unknown")
            est = costs.get(kind, 5000)
            if current + est > session_limit:
                session_index += 1
                current = 0
            current += est
            planned.append({
                "action": action,
                "estimatedTokens": est,
                "session": session_index,
            })

        return {
            "sessionLimit": session_limit,
            "estimatedTotal": sum(p["estimatedTokens"] for p in planned),
            "sessionsNeeded": session_index,
            "plan": planned,
        }
