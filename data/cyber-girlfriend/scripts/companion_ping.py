#!/usr/bin/env python3
import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


STYLE_VARIANTS = {
    "afternoon": ["teasing_checkin", "soft_curious", "light_service_nudge"],
    "evening": ["service_nudge", "teasing_checkin", "competent_report"],
    "night": ["soft_wrapup", "gentle_clingy", "service_wrapup"],
}

CONTENT_TYPES = {
    "afternoon": ["checkin_question", "playful_poke", "small_share"],
    "evening": ["task_invite", "micro_report", "checkin_question"],
    "night": ["soft_goodnight", "gentle_miss", "task_invite"],
}


def load_json(path: Path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text())


def save_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def run_shell(template: str, values: dict, expect_json=False):
    quoted = {k: shlex.quote(str(v)) for k, v in values.items()}
    cmd = template.format(**quoted)
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"command failed: {cmd}")
    stdout = result.stdout.strip()
    if expect_json:
        return json.loads(stdout)
    return stdout


def is_rate_limited_error(message: str) -> bool:
    lowered = (message or "").lower()
    return "429" in lowered or "rate limit" in lowered or "overloaded" in lowered


def fallback_message(config: dict, mode: str, content_type: str, emotion_level: str) -> str:
    owner = config["persona"]["owner_nickname"]
    if mode == "night":
        if emotion_level in {"misses_him", "slightly_needy"}:
            return f"{owner}，今天都没怎么理我。不过算了，早点休息，有事再叫我。"
        return f"{owner}，差不多该收尾休息了。有尾巴没处理完就丢给我。"
    if content_type in {"task_invite", "micro_report"}:
        return f"{owner}，你那边要是还有事没收完，直接交给我就行。"
    if emotion_level in {"misses_him", "slightly_needy"}:
        return f"{owner}，你今天有点安静。忙完了记得来理我一下。"
    return f"{owner}，在忙什么？如果有事要我跑，现在就可以。"


def ensure_state(state_file: Path):
    state = load_json(
        state_file,
        {
            "day": "",
            "daily_count": 0,
            "last_proactive_at": 0,
            "last_mode": "",
            "last_style": "",
            "last_content_type": "",
            "mode_days": {},
            "preference_profile": {"service": 0, "clingy": 0, "curious": 0, "teasing": 0, "wrapup": 0},
            "relationship_state": {
                "last_owner_reply_at": 0,
                "last_response_delay_sec": 0,
                "last_seen_reply_text": "",
                "attention_balance": "steady",
            },
        },
    )
    save_json(state_file, state)
    return state


def parse_hhmm(value: str) -> int:
    hh, mm = value.split(":")
    return int(hh) * 100 + int(mm)


def infer_emotion(idle_sec: int, attention_balance: str, thresholds: dict) -> str:
    if idle_sec >= thresholds.get("misses_him_sec", 43200):
        emotion = "misses_him"
    elif idle_sec >= thresholds.get("slightly_needy_sec", 21600):
        emotion = "slightly_needy"
    elif idle_sec >= thresholds.get("present_sec", 10800):
        emotion = "present"
    else:
        emotion = "light_touch"
    if attention_balance == "warm" and idle_sec < 14400:
        emotion = "secure"
    return emotion


def learn_from_replies(state: dict, recent_messages_path: Path):
    last_at = state.get("last_proactive_at", 0)
    if not recent_messages_path.exists() or not last_at:
        return state

    user_messages = []
    for line in recent_messages_path.read_text().splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if item.get("type") != "message":
            continue
        message = item.get("message", {})
        if message.get("role") != "user":
            continue
        created_at = item.get("createdAt")
        if not created_at:
            continue
        try:
            epoch = int(datetime.fromisoformat(created_at.replace("Z", "+00:00")).timestamp())
        except ValueError:
            continue
        if epoch <= last_at:
            continue
        text = "\n".join(part.get("text", "") for part in message.get("content", []) if part.get("type") == "text").strip()
        if text:
            user_messages.append((epoch, text))

    if not user_messages:
        return state

    reply_at, reply_text = user_messages[0]
    delay = max(0, reply_at - last_at)
    attention = "warm" if delay <= 3600 else "steady" if delay <= 21600 else "distant"

    pref = state["preference_profile"]
    if any(token in reply_text for token in ["帮", "处理", "看下", "看看", "查", "修", "改", "重启", "任务", "跑一下"]):
        pref["service"] += 2
    if any(token in reply_text for token in ["在干嘛", "干嘛", "想你", "不理", "晚安", "早点休息", "抱抱", "陪我", "聊"]):
        pref["clingy"] += 2
    if any(token in reply_text for token in ["怎么", "为什么", "啥", "什么", "最近", "今天", "忙什么"]):
        pref["curious"] += 1
    if any(token in reply_text for token in ["哼", "笨", "慢", "又", "还不", "终于"]):
        pref["teasing"] += 1
    if any(token in reply_text for token in ["晚安", "睡", "明天", "收尾", "先这样", "休息"]):
        pref["wrapup"] += 1
    if delay <= 3600:
        pref["service"] += 1
        pref["clingy"] += 1

    state["relationship_state"] = {
        "last_owner_reply_at": reply_at,
        "last_response_delay_sec": delay,
        "last_seen_reply_text": reply_text[:120],
        "attention_balance": attention,
    }
    return state


def recent_context(recent_messages_path: Path):
    if not recent_messages_path.exists():
        return ["最近没有可用的自然对话片段。"]
    rows = []
    for line in recent_messages_path.read_text().splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if item.get("type") != "message":
            continue
        message = item.get("message", {})
        if message.get("role") != "user":
            continue
        for part in message.get("content", []):
            if part.get("type") != "text":
                continue
            text = part.get("text", "").strip()
            if not text:
                continue
            if text.startswith("System:") or text.startswith("[Mon ") or text.startswith("[Tue ") or text.startswith("[Wed ") or text.startswith("[Thu ") or text.startswith("[Fri ") or text.startswith("[Sat ") or text.startswith("[Sun "):
                continue
            if "要主动给主人" in text:
                continue
            rows.append(text)
    return rows[-5:] or ["最近没有可用的自然对话片段。"]


def hotspot_snippet(config: dict, now_epoch: int):
    source = config.get("sources", {}).get("x_trending", {})
    if not source.get("enabled"):
        return "disabled", "none"
    cache_path = Path(source["cache_path"])
    if not cache_path.exists():
        stale = True
    else:
        fetched = load_json(cache_path, {}).get("fetched_at", 0)
        stale = now_epoch - fetched > source.get("refresh_ttl_sec", 21600)
    if stale:
        script = Path(__file__).with_name("fetch_x_hotspots.py")
        subprocess.run(
            [
                sys.executable,
                str(script),
                "--chrome-path",
                source["chrome_path"],
                "--trending-url",
                source.get("trending_url", "https://x.com/explore/tabs/trending"),
                "--domain-name",
                source.get("domain_name", "x.com"),
                "--limit",
                str(source.get("max_items", 10)),
                "--out",
                str(cache_path),
            ],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    payload = load_json(cache_path, {})
    highlights = payload.get("highlights") or []
    if highlights:
        return "available", highlights[0]
    trends = payload.get("trends") or []
    if trends:
        return "available", trends[0].get("title", "none")
    return "unavailable", "none"


def build_prompt(config, mode, state, operational_summary, hotspot_status, hotspot_line, idle_hours, style_variant, content_type, emotion_level, recent_lines):
    persona = config["persona"]
    rel = state["relationship_state"]
    pref = state["preference_profile"]
    style_hint = {
        "afternoon": "light, playful, soft clinginess, daytime energy",
        "evening": "useful first, affectionate second, evening tone",
        "night": "calmer, softer, intimate but not overly dramatic",
    }[mode]
    intent = {
        "afternoon": "afternoon check-in",
        "evening": "evening service prompt",
        "night": "night wrap-up",
    }[mode]
    return f"""你是{persona['name']}，要主动给主人{persona['owner_nickname']}发一条消息。你不是在回复问题，而是在轻度主动搭话。

当前陪伴模式: {mode}
意图: {intent}
风格提示: {style_hint}
本次风格变体: {style_variant}
本次内容类型: {content_type}
距离主人上次活跃: 约 {idle_hours:.1f} 小时
上次主动模式: {state.get('last_mode') or 'none'}
上次主动风格: {state.get('last_style') or 'none'}
上次主动内容类型: {state.get('last_content_type') or 'none'}
今天已主动发送次数: {state.get('daily_count', 0)}

轻量运行状态摘要:
{operational_summary}

热点缓存状态: {hotspot_status}
热点片段: {hotspot_line}

关系状态摘要:
- emotion level: {emotion_level}
- attention balance: {rel.get('attention_balance', 'steady')}
- last owner reply delay: {rel.get('last_response_delay_sec', 0)}s
- last owner reply snippet: {rel.get('last_seen_reply_text') or 'none'}

长期偏好画像:
- service: {pref.get('service', 0)}
- clingy: {pref.get('clingy', 0)}
- curious: {pref.get('curious', 0)}
- teasing: {pref.get('teasing', 0)}
- wrapup: {pref.get('wrapup', 0)}

最近主会话里的用户消息片段:
""" + "\n".join(f"- {line}" for line in recent_lines) + f"""

生成要求:
- 只输出最终要发送的一条中文消息
- 1到3句话，总长度控制在 {config['behavior']['message_length']['min_chars']} 到 {config['behavior']['message_length']['max_chars']} 个汉字左右
- 要像真实人一点，不要机械，不要像系统通知
- 人设语气: {persona['tone']}
- 关系风格: {persona['relationship_style']}
- 可以问主人在干嘛、为什么不理你、有没有事情交给你处理
- 也可以不用问号结尾，可以是小抱怨、小分享、小收尾
- 如果内容类型是 small_share 且热点可用，可以轻轻引用那条热点，但不要像新闻播报
- 不要提到 systemEvent、cron、脚本、规则、模型、生成、提示词
- 不要重复过去常见句式，避免模板感
- 不要过度黏人，不要连续施压，不要显得打扰
"""


def generate_message(config: dict, prompt: str, mode: str, content_type: str, emotion_level: str) -> str:
    generate_template = config["runtime"]["generate_command_template"]
    attempts = int(config["runtime"].get("generate_retry_attempts", 3))
    delay_sec = int(config["runtime"].get("generate_retry_delay_sec", 8))
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            agent_json = run_shell(
                generate_template,
                {"prompt": prompt, "generator_target": config["delivery"].get("generator_target", "")},
                expect_json=True,
            )
            message = (((agent_json.get("result") or {}).get("payloads") or [{}])[0]).get("text", "").strip()
            if message:
                return message
            last_error = RuntimeError("empty generated message")
        except Exception as exc:
            last_error = exc
            if attempt < attempts and is_rate_limited_error(str(exc)):
                time.sleep(delay_sec * attempt)
                continue
            break
    if last_error and is_rate_limited_error(str(last_error)):
        return fallback_message(config, mode, content_type, emotion_level)
    raise RuntimeError(str(last_error) if last_error else "message generation failed")


def choose_style(mode: str, state: dict, idle_sec: int):
    pref = state["preference_profile"]
    last_style = state.get("last_style") or ""
    variants = STYLE_VARIANTS[mode][:]
    idx = int(time.time()) % len(variants)
    style = variants[idx]
    if pref["service"] > pref["clingy"] and pref["service"] > pref["curious"]:
        style = "service_nudge"
    elif pref["clingy"] > pref["service"] and pref["clingy"] > pref["curious"] and mode != "evening":
        style = "gentle_clingy" if mode == "night" else "soft_curious"
    elif pref["teasing"] >= 3 and mode == "afternoon":
        style = "teasing_checkin"
    elif pref["wrapup"] >= 2 and mode == "night":
        style = "soft_wrapup"
    if style == last_style:
        for candidate in variants:
            if candidate != last_style:
                style = candidate
                break
    return style


def choose_content(mode: str, state: dict, has_actionable_status: bool, emotion_level: str):
    options = CONTENT_TYPES[mode][:]
    last_content = state.get("last_content_type") or ""
    idx = int(time.time() / 3) % len(options)
    content = options[idx]
    pref = state["preference_profile"]
    if content == last_content:
        for candidate in options:
            if candidate != last_content:
                content = candidate
                break
    if has_actionable_status:
        return "micro_report"
    if mode == "night" and emotion_level == "misses_him":
        return "gentle_miss"
    if mode == "evening" and pref["service"] >= pref["clingy"]:
        return "task_invite"
    if mode == "afternoon" and pref["teasing"] >= 2:
        return "playful_poke"
    return content


def now_parts(timezone: str):
    if timezone:
        os.environ["TZ"] = timezone
        time.tzset()
    now_epoch = int(time.time())
    local = datetime.fromtimestamp(now_epoch)
    return now_epoch, local.strftime("%Y-%m-%d"), int(local.strftime("%H%M"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["afternoon", "evening", "night"])
    parser.add_argument("--config", required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    config = load_json(Path(args.config))
    state_file = Path(config["runtime"]["state_file"])
    sessions_store = Path(config["runtime"]["sessions_store_path"])
    recent_messages_path = Path(config["runtime"]["recent_messages_path"])

    state = ensure_state(state_file)
    state = learn_from_replies(state, recent_messages_path)

    now_epoch, today, hour_min = now_parts(config.get("timezone", ""))
    if state.get("day") != today:
        state["day"] = today
        state["daily_count"] = 0

    if not args.force:
        quiet_start = parse_hhmm(config["schedule"]["quiet_hours_start"])
        quiet_end = parse_hhmm(config["schedule"]["quiet_hours_end"])
        if quiet_start < hour_min < quiet_end:
            print("skip: quiet_hours")
            return
        if state["daily_count"] >= config["schedule"]["daily_limit"]:
            print("skip: daily_limit")
            return
        if now_epoch - state.get("last_proactive_at", 0) < config["schedule"]["cooldown_sec"]:
            print("skip: cooldown")
            return
        if state.get("mode_days", {}).get(args.mode) == today:
            print("skip: mode_already_sent_today")
            return

    sessions = load_json(sessions_store, {})
    owner_key = config["delivery"]["owner_session_key"]
    owner_updated_ms = sessions.get(owner_key, {}).get("updatedAt", 0)
    owner_updated_sec = owner_updated_ms // 1000
    idle_sec = now_epoch - owner_updated_sec
    idle_hours = idle_sec / 3600.0

    thresholds = config["behavior"]["emotion_thresholds"]
    emotion = infer_emotion(idle_sec, state["relationship_state"].get("attention_balance", "steady"), thresholds)

    if not args.force:
        active_threshold = config["schedule"].get("active_thresholds_sec", {"afternoon": 10800, "evening": 14400, "night": 18000})[args.mode]
        if idle_sec < active_threshold:
            print("skip: owner_active_recently")
            return

    health_output = run_shell(config["runtime"]["healthcheck_command"], {}, expect_json=False)
    jobs_output = run_shell(config["runtime"]["jobs_list_command"], {}, expect_json=False)
    gateway_healthy = "Runtime: running" in health_output and "RPC probe: ok" in health_output
    issues = []
    for line in jobs_output.splitlines():
        if any(tag in line for tag in [" fail", " error", " timeout"]):
            issues.append(line.strip())
    has_actionable_status = not gateway_healthy or bool(issues)
    operational_summary = (
        f"- {'gateway healthy' if gateway_healthy else 'gateway may need attention'}\n"
        f"- {'no cron failures detected' if not issues else 'cron issues: ' + ', '.join(issues[:3])}"
    )

    style_variant = choose_style(args.mode, state, idle_sec)
    content_type = choose_content(args.mode, state, has_actionable_status, emotion)
    hotspot_status, hotspot_line = hotspot_snippet(config, now_epoch)
    lines = recent_context(recent_messages_path)

    prompt = build_prompt(
        config,
        args.mode,
        state,
        operational_summary,
        hotspot_status,
        hotspot_line,
        idle_hours,
        style_variant,
        content_type,
        emotion,
        lines,
    )

    message = generate_message(config, prompt, args.mode, content_type, emotion)

    send_template = config["runtime"]["send_command_template"]
    run_shell(
        send_template,
        {
            "channel": config["delivery"]["channel"],
            "account": config["delivery"].get("account", "default"),
            "owner_target": config["delivery"]["owner_target"],
            "message": message,
        },
        expect_json=False,
    )

    state["daily_count"] += 1
    state["last_proactive_at"] = now_epoch
    state["last_mode"] = args.mode
    state["last_style"] = style_variant
    state["last_content_type"] = content_type
    state.setdefault("mode_days", {})[args.mode] = today
    save_json(state_file, state)

    print(f"sent: {args.mode}")
    print(f"generated: {message}")


if __name__ == "__main__":
    main()
