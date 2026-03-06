"""
SociClaw CLI helpers.

This is NOT the final OpenClaw command-dispatch integration, but it provides a
reproducible way to exercise the local stack:
- Provision an image account/API key for a provider user id
- Generate an image using the provisioned API key

Examples (PowerShell):
  python -m sociclaw.scripts.cli whoami --provider telegram --provider-user-id 123

  python -m sociclaw.scripts.cli generate-image --provider telegram --provider-user-id 123 --prompt "a blue bird logo"
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from datetime import datetime
from dataclasses import asdict
from pathlib import Path
from typing import List, Optional

from .brand_profile import BrandProfile, default_brand_profile_path, load_brand_profile, save_brand_profile
from .content_generator import ContentGenerator, GeneratedPost
from .research import TrendData, TrendResearcher
from .provisioning_gateway import SociClawProvisioningGatewayClient
from .image_generator import ImageGenerator
from .local_session_store import LocalSessionStore, default_db_path
from .notion_sync import NotionSync
from .runtime_config import RuntimeConfig, RuntimeConfigStore, default_runtime_config_path
from .scheduler import PostPlan, QuarterlyScheduler
from .state_store import StateStore, default_state_path
from .memory_store import SociClawMemoryStore, default_memory_db_path
from .topup_client import TopupClient
from .trello_sync import TrelloSync
from .release_audit import scan_forbidden_terms, scan_placeholders
from .validators import validate_provider, validate_provider_user_id, validate_tx_hash


def _redact_secret(secret: Optional[str]) -> Optional[str]:
    if not secret:
        return secret
    s = str(secret)
    if len(s) <= 8:
        return "***"
    return f"{s[:4]}...{s[-4:]}"


def _validated_provider_fields(provider: str, provider_user_id: str) -> tuple[str, str]:
    try:
        p = validate_provider(provider)
        u = validate_provider_user_id(provider_user_id)
        return p, u
    except ValueError as exc:
        raise SystemExit(str(exc))


def _default_plan_path() -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    return repo_root / ".sociclaw" / "planned_posts.json"


def _load_planned_posts(path: Optional[Path] = None) -> List[dict]:
    plan_path = path or _default_plan_path()
    if not plan_path.exists():
        return []
    try:
        payload = json.loads(plan_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    return list(payload.get("posts", []))


def _save_planned_posts(posts: List[dict], path: Optional[Path] = None) -> Path:
    plan_path = path or _default_plan_path()
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "posts": posts,
    }
    plan_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return plan_path


def _parse_posts_per_day(freq: str) -> int:
    raw = (freq or "").strip().lower()
    if not raw:
        return 1
    if "/day" in raw:
        left = raw.split("/day", 1)[0].strip()
        if left.isdigit():
            return max(1, int(left))
    digits = "".join(ch for ch in raw if ch.isdigit())
    return max(1, int(digits)) if digits else 1


def _resolve_identity_from_runtime(args: argparse.Namespace, runtime: RuntimeConfig) -> tuple[str, str]:
    provider = args.provider or runtime.provider
    provider_user_id = str(args.provider_user_id or runtime.provider_user_id or "")
    if not provider_user_id:
        raise SystemExit("Missing provider_user_id. Run /sociclaw setup first.")
    return _validated_provider_fields(provider, provider_user_id)


def _logo_directed_prompt(base_prompt: str, has_logo_input: bool) -> str:
    if not has_logo_input:
        return base_prompt
    directive = (
        "Use the attached logo image as the primary brand reference. "
        "Integrate the logo naturally, keep it recognizable, and keep visual hierarchy clean like an art director."
    )
    text = (base_prompt or "").strip()
    if not text:
        return directive
    return f"{text}. {directive}"


def _fallback_trend_data(niche: str) -> TrendData:
    topic = (niche or "AI agents").strip()
    hashtags = ["SociClaw", "AI", "Automation"]
    if topic:
        normalized = "".join(ch for ch in topic if ch.isalnum())
        if normalized:
            hashtags.append(normalized[:20])
    return TrendData(
        topics=[topic or "AI agents", "workflow automation", "creator growth"],
        formats={"thread": 10, "image": 8},
        peak_hours=[13, 17, 21],
        hashtags=hashtags,
        sample_posts=[],
    )


def _postplan_from_generated(post: dict) -> PostPlan:
    date_str = str(post.get("date") or datetime.utcnow().strftime("%Y-%m-%d"))
    try:
        date = datetime.fromisoformat(date_str)
    except ValueError:
        date = datetime.utcnow()
    return PostPlan(
        date=date,
        time=int(post.get("time") or 13),
        category=str(post.get("category") or "tips"),
        topic=str(post.get("title") or post.get("body") or "SociClaw update"),
        hashtags=list(post.get("hashtags") or []),
    )


def _generated_post_from_dict(item: dict) -> GeneratedPost:
    return GeneratedPost(
        text=str(item.get("text") or ""),
        image_prompt=str(item.get("image_prompt") or ""),
        title=str(item.get("title") or ""),
        body=str(item.get("body") or ""),
        details=str(item.get("details") or ""),
        hashtags=list(item.get("hashtags") or []),
        category=str(item.get("category") or ""),
        date=str(item.get("date") or ""),
        time=int(item.get("time") or 13),
    )


def cmd_provision_image(args: argparse.Namespace) -> int:
    raise SystemExit("Direct upstream provisioning is not supported in this skill build. Use provision-image-gateway.")


def cmd_whoami(args: argparse.Namespace) -> int:
    provider, provider_user_id = _validated_provider_fields(args.provider, str(args.provider_user_id))
    store = StateStore(Path(args.state_path) if args.state_path else None)
    u = store.get_user(provider=provider, provider_user_id=provider_user_id)
    if not u:
        print(json.dumps({"found": False, "state_path": str(store.path)}, indent=2))
        return 1

    print(
        json.dumps(
            {
                "found": True,
                "provider": u.provider,
                "provider_user_id": u.provider_user_id,
                "image_api_key": _redact_secret(u.image_api_key),
                "wallet_address": u.wallet_address,
                "created_at": u.created_at,
                "updated_at": u.updated_at,
                "state_path": str(store.path),
            },
            indent=2,
        )
    )
    return 0


def cmd_generate_image(args: argparse.Namespace) -> int:
    provider, provider_user_id = _validated_provider_fields(args.provider, str(args.provider_user_id))
    runtime_store = RuntimeConfigStore(Path(args.config_path) if args.config_path else None)
    runtime = runtime_store.load()
    store = StateStore(Path(args.state_path) if args.state_path else None)
    u = store.get_user(provider=provider, provider_user_id=provider_user_id)
    if not u or not u.image_api_key:
        raise SystemExit(
            "Missing provisioned user API key. Run: provision-image-gateway "
            f"--provider {args.provider} --provider-user-id {args.provider_user_id}"
        )

    image_url = args.image_url
    if not image_url:
        same_user = runtime.provider == provider and str(runtime.provider_user_id or "") == str(provider_user_id)
        if same_user and runtime.brand_logo_url:
            image_url = runtime.brand_logo_url

    if "nano-banana" in (args.model or "").lower() and not image_url and not args.dry_run:
        raise SystemExit(
            "Model nano-banana requires an input image. "
            "Set --image-url or configure --brand-logo-url in setup-wizard."
        )

    if args.dry_run:
        print(
            json.dumps(
                {
                    "dry_run": True,
                    "provider": args.provider,
                    "provider_user_id": provider_user_id,
                    "has_api_key": True,
                    "model": args.model,
                    "has_image_url": bool(image_url),
                    "prompt_preview": args.prompt[:120],
                },
                indent=2,
            )
        )
        return 0

    out_dir = Path(args.output_dir) if args.output_dir else None
    gen = ImageGenerator(
        api_key=u.image_api_key,
        model=args.model,
        image_url=image_url,
        output_dir=out_dir,
    )

    prompt = _logo_directed_prompt(args.prompt, bool(image_url))
    # user_address is just an identifier for the upstream image API ("user_id" field)
    r = gen.generate_image(prompt, user_address=f"{u.provider}:{u.provider_user_id}")
    print(json.dumps({"url": r.url, "local_path": str(r.local_path) if r.local_path else None}, indent=2))
    return 0


def cmd_reset(args: argparse.Namespace) -> int:
    if not args.yes and not args.dry_run:
        raise SystemExit("Refusing destructive reset without --yes. Use --dry-run to preview.")

    memory_db_path = getattr(args, "memory_db_path", None)
    target_paths = [
        Path(args.state_path) if args.state_path else default_state_path(),
        Path(args.config_path) if args.config_path else default_runtime_config_path(),
        Path(args.session_db_path) if args.session_db_path else default_db_path(),
        Path(args.brand_profile_path) if args.brand_profile_path else default_brand_profile_path(),
        Path(memory_db_path) if memory_db_path else default_memory_db_path(),
    ]

    seen = set()
    unique_paths = []
    for p in target_paths:
        key = str(p.resolve()) if p.exists() else str(p)
        if key in seen:
            continue
        seen.add(key)
        unique_paths.append(p)

    results = []
    had_error = False
    for path in unique_paths:
        entry = {
            "path": str(path),
            "existed": path.exists(),
            "removed": False,
        }
        if entry["existed"] and not args.dry_run:
            try:
                path.unlink()
                entry["removed"] = True
            except OSError as exc:
                had_error = True
                entry["error"] = str(exc)
        results.append(entry)

    output = {
        "reset": not args.dry_run,
        "dry_run": bool(args.dry_run),
        "files": results,
        "next_step": "/sociclaw setup",
    }
    print(json.dumps(output, indent=2))
    return 1 if had_error else 0


def _prompt_or_value(
    value: Optional[str],
    prompt_text: str,
    default: str = "",
    *,
    non_interactive: bool = False,
) -> str:
    if value is not None:
        return str(value).strip()
    if non_interactive:
        return default
    raw = input(f"{prompt_text} [{default}]: ").strip()
    return raw or default


def _prompt_list_or_value(
    value: Optional[str],
    prompt_text: str,
    default_items: list[str],
    *,
    non_interactive: bool = False,
) -> list[str]:
    if value is not None:
        raw = value.strip()
    else:
        if non_interactive:
            return default_items
        default_txt = ", ".join(default_items)
        raw = input(f"{prompt_text} (comma-separated) [{default_txt}]: ").strip()
        if not raw:
            return default_items
    return [x.strip() for x in raw.split(",") if x.strip()]


def _prompt_bool_or_value(value: Optional[bool], prompt_text: str, default: bool, *, non_interactive: bool = False) -> bool:
    if value is not None:
        return bool(value)
    if non_interactive:
        return default
    default_txt = "y" if default else "n"
    raw = input(f"{prompt_text} [y/n] [{default_txt}]: ").strip().lower()
    if not raw:
        return default
    return raw in {"y", "yes", "true", "1"}


def cmd_setup_wizard(args: argparse.Namespace) -> int:
    path = Path(args.config_path) if args.config_path else None
    store = RuntimeConfigStore(path)
    current = store.load()

    # OpenClaw/automation runners typically execute commands without a TTY.
    # Never block on `input()` in that environment.
    non_interactive = bool(args.non_interactive) or (not sys.stdin.isatty())

    provider = _prompt_or_value(
        args.provider,
        "Provider (telegram, etc)",
        current.provider or "telegram",
        non_interactive=non_interactive,
    )
    provider_user_id = _prompt_or_value(
        args.provider_user_id,
        "Provider user ID",
        current.provider_user_id,
        non_interactive=non_interactive,
    )
    if not provider_user_id:
        raise SystemExit("provider_user_id is required")
    provider, provider_user_id = _validated_provider_fields(provider, provider_user_id)

    cfg = RuntimeConfig(
        provider=provider,
        provider_user_id=provider_user_id,
        user_niche=_prompt_or_value(
            args.user_niche,
            "User niche",
            current.user_niche,
            non_interactive=non_interactive,
        ),
        posting_frequency=_prompt_or_value(
            args.posting_frequency,
            "Posting frequency (e.g. 2/day)",
            current.posting_frequency or "2/day",
            non_interactive=non_interactive,
        ),
        content_language=_prompt_or_value(
            args.content_language,
            "Content language (e.g. en, pt-BR)",
            current.content_language or "en",
            non_interactive=non_interactive,
        ),
        brand_logo_url=_prompt_or_value(
            args.brand_logo_url,
            "Brand/logo image URL or local path (recommended for nano-banana)",
            current.brand_logo_url,
            non_interactive=non_interactive,
        ),
        has_brand_document=_prompt_bool_or_value(
            args.has_brand_document,
            "Do you already have a full brand document",
            current.has_brand_document,
            non_interactive=non_interactive,
        ),
        brand_document_path=_prompt_or_value(
            args.brand_document_path,
            "Brand document path or URL (optional)",
            current.brand_document_path,
            non_interactive=non_interactive,
        ),
        use_trello=_prompt_bool_or_value(
            args.use_trello,
            "Use Trello integration",
            current.use_trello,
            non_interactive=non_interactive,
        ),
        use_notion=_prompt_bool_or_value(
            args.use_notion,
            "Use Notion integration",
            current.use_notion,
            non_interactive=non_interactive,
        ),
        timezone=_prompt_or_value(
            args.timezone,
            "Timezone",
            current.timezone or "UTC",
            non_interactive=non_interactive,
        ),
    )

    saved_path = store.save(cfg)
    print(json.dumps({"saved": True, "path": str(saved_path), "config": cfg.__dict__}, indent=2))
    return 0


def cmd_briefing(args: argparse.Namespace) -> int:
    profile_path = Path(args.path) if args.path else None
    current = load_brand_profile(profile_path)
    non_interactive = bool(args.non_interactive) or (not sys.stdin.isatty())

    updated = BrandProfile(
        name=_prompt_or_value(args.name, "Project name", current.name, non_interactive=non_interactive),
        slogan=_prompt_or_value(args.slogan, "Slogan", current.slogan, non_interactive=non_interactive),
        voice_tone=_prompt_or_value(args.voice_tone, "Voice/Tone", current.voice_tone, non_interactive=non_interactive),
        personality_traits=_prompt_list_or_value(
            args.personality_traits,
            "Personality traits (comma-separated)",
            current.personality_traits,
            non_interactive=non_interactive,
        ),
        visual_style=_prompt_or_value(
            args.visual_style,
            "Visual identity style",
            current.visual_style,
            non_interactive=non_interactive,
        ),
        signature_openers=_prompt_list_or_value(
            args.signature_openers,
            "Signature openers (comma-separated)",
            current.signature_openers,
            non_interactive=non_interactive,
        ),
        content_goals=_prompt_list_or_value(
            args.content_goals,
            "Content goals (comma-separated)",
            current.content_goals,
            non_interactive=non_interactive,
        ),
        cta_style=_prompt_or_value(args.cta_style, "CTA style (question, invitation, challenge)", current.cta_style, non_interactive=non_interactive),
        target_audience=_prompt_or_value(
            args.target_audience,
            "Target audience",
            current.target_audience,
            non_interactive=non_interactive,
        ),
        value_proposition=_prompt_or_value(
            args.value_proposition,
            "Value proposition",
            current.value_proposition,
            non_interactive=non_interactive,
        ),
        key_themes=_prompt_list_or_value(
            args.key_themes,
            "Key themes",
            current.key_themes,
            non_interactive=non_interactive,
        ),
        do_not_say=_prompt_list_or_value(
            args.do_not_say,
            "Do Not Say terms",
            current.do_not_say,
            non_interactive=non_interactive,
        ),
        keywords=_prompt_list_or_value(
            args.keywords,
            "Required keywords",
            current.keywords,
            non_interactive=non_interactive,
        ),
        content_language=_prompt_or_value(
            args.content_language,
            "Content language for generated posts (e.g. en, pt-BR)",
            current.content_language or "en",
            non_interactive=non_interactive,
        ),
        has_brand_document=_prompt_bool_or_value(
            args.has_brand_document,
            "Do you have a complete brand document",
            current.has_brand_document,
            non_interactive=non_interactive,
        ),
        brand_document_path=_prompt_or_value(
            args.brand_document_path,
            "Brand document path or URL (optional)",
            current.brand_document_path,
            non_interactive=non_interactive,
        ),
    )

    out_path = save_brand_profile(updated, profile_path)
    print(json.dumps({"saved": True, "path": str(out_path)}, indent=2))
    return 0


def cmd_home(args: argparse.Namespace) -> int:
    print(
        json.dumps(
            {
                "agent": "SociClaw",
                "message": "Ready. Use setup, plan, generate, status, pay, or reset.",
                "next": "Run /sociclaw setup to configure your account.",
            },
            indent=2,
        )
    )
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    runtime_store = RuntimeConfigStore(Path(args.config_path) if args.config_path else None)
    runtime = runtime_store.load()
    provider, provider_user_id = _resolve_identity_from_runtime(args, runtime)
    memory_db_path = getattr(args, "memory_db_path", None)
    memory_store = SociClawMemoryStore(Path(memory_db_path) if memory_db_path else None)

    if args.days is not None:
        days = max(1, int(args.days))
    elif args.quarter or args.full:
        days = QuarterlyScheduler.FULL_PLAN_DAYS
    else:
        days = QuarterlyScheduler.STARTER_PLAN_DAYS

    if args.posts_per_day is not None:
        posts_per_day = max(1, int(args.posts_per_day))
    elif args.quarter or args.full:
        posts_per_day = QuarterlyScheduler.FULL_PLAN_POSTS_PER_DAY
    else:
        posts_per_day = _parse_posts_per_day(runtime.posting_frequency or "1/day")

    niche = args.topic or runtime.user_niche or "AI agents"
    trend_data = _fallback_trend_data(niche)
    if os.getenv("XAI_API_KEY") and not args.skip_research:
        try:
            researcher = TrendResearcher()
            trend_data = asyncio.run(researcher.research_trends(niche, days=30))
        except Exception as exc:
            trend_data = _fallback_trend_data(niche)
            trend_data.sample_posts = [{"error": f"research_fallback: {exc}"}]

    scheduler = QuarterlyScheduler()
    avoid_topics = memory_store.get_recent_topics(provider=provider, provider_user_id=provider_user_id, limit=40)
    start_date = datetime.utcnow()
    plans = scheduler.generate_quarterly_plan(
        trend_data,
        start_date=start_date,
        days=days,
        posts_per_day=posts_per_day,
        starter_mode=False,
        avoid_topics=avoid_topics,
    )
    generator = ContentGenerator(brand_profile_path=Path(args.brand_profile_path) if args.brand_profile_path else None)
    posts = generator.generate_batch(plans)
    serialized = [asdict(p) for p in posts]
    plan_path = _save_planned_posts(serialized, Path(args.plan_path) if args.plan_path else None)

    trello_cards = 0
    notion_pages = 0
    if args.sync_trello or runtime.use_trello:
        trello = TrelloSync()
        trello.setup_board()
        for post in posts:
            trello.create_card(post)
            trello_cards += 1

    if args.sync_notion or runtime.use_notion:
        notion = NotionSync()
        for post in posts:
            notion.create_page(post, status="Draft")
            notion_pages += 1

    print(
        json.dumps(
            {
                "provider": provider,
                "provider_user_id": provider_user_id,
                "days": days,
                "posts_per_day": posts_per_day,
                "planned_posts": len(posts),
                "plan_path": str(plan_path),
                "trello_cards": trello_cards,
                "notion_pages": notion_pages,
                "starter_mode": days <= QuarterlyScheduler.STARTER_PLAN_DAYS and posts_per_day <= 1,
            },
            indent=2,
        )
    )
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    runtime_store = RuntimeConfigStore(Path(args.config_path) if args.config_path else None)
    runtime = runtime_store.load()
    provider, provider_user_id = _resolve_identity_from_runtime(args, runtime)
    plan_path = Path(args.plan_path) if args.plan_path else None
    planned = _load_planned_posts(plan_path)
    if not planned:
        raise SystemExit("No planned posts found. Run /sociclaw plan first.")

    today = datetime.utcnow().date()
    due_today = []
    future = []
    for item in planned:
        try:
            d = datetime.fromisoformat(str(item.get("date"))).date()
        except Exception:
            d = today
        if d <= today:
            due_today.append(item)
        else:
            future.append(item)

    count = max(1, int(args.count or _parse_posts_per_day(runtime.posting_frequency or "1/day")))
    source = due_today if due_today else future
    selected = source[:count]
    selected_keys = {json.dumps(item, sort_keys=True) for item in selected}
    remaining = [item for item in planned if json.dumps(item, sort_keys=True) not in selected_keys]

    state = StateStore(Path(args.state_path) if args.state_path else None)
    user = state.get_user(provider=provider, provider_user_id=provider_user_id)
    memory_db_path = getattr(args, "memory_db_path", None)
    memory = SociClawMemoryStore(Path(memory_db_path) if memory_db_path else None)

    image_model = args.image_model or os.getenv("SOCICLAW_IMAGE_MODEL") or "nano-banana"
    image_input = args.image_url or runtime.brand_logo_url or None
    model_requires_input = "nano-banana" in (image_model or "").lower()

    can_generate_image = bool(
        user
        and user.image_api_key
        and bool(args.with_image)
        and (not model_requires_input or bool(image_input))
    )

    image_generator = None
    if can_generate_image:
        image_generator = ImageGenerator(
            api_key=user.image_api_key,
            model=image_model,
            image_url=image_input,
            timeout_seconds=int(os.getenv("SOCICLAW_IMAGE_TIMEOUT_SECONDS", "120")),
            poll_interval_seconds=int(os.getenv("SOCICLAW_IMAGE_POLL_INTERVAL_SECONDS", "2")),
        )

    trello = None
    notion = None
    if args.sync_trello or runtime.use_trello:
        trello = TrelloSync()
        trello.setup_board()
    if args.sync_notion or runtime.use_notion:
        notion = NotionSync()

    results = []
    last_entry_id: Optional[int] = None
    for post_data in selected:
        generated_post = _generated_post_from_dict(post_data)
        if not generated_post.text:
            post = _postplan_from_generated(post_data)
            generated_post = ContentGenerator(
                brand_profile_path=Path(args.brand_profile_path) if args.brand_profile_path else None
            ).generate_post(post)

        image_result = None
        if image_generator:
            directed_prompt = _logo_directed_prompt(
                generated_post.image_prompt,
                bool(image_generator.image_url),
            )
            image_result = image_generator.generate_image(
                directed_prompt,
                user_address=f"{provider}:{provider_user_id}",
            )
        post_topic = str(post_data.get("topic") or runtime.user_niche or "SociClaw")
        post_category = str(post_data.get("category") or generated_post.category or "tips")
        try:
            post_date = str(post_data.get("date") or generated_post.date or datetime.utcnow().strftime("%Y-%m-%d"))
        except Exception:
            post_date = datetime.utcnow().strftime("%Y-%m-%d")
        last_entry_id = memory.upsert_generation(
            provider=provider,
            provider_user_id=provider_user_id,
            category=post_category,
            topic=post_topic,
            text=generated_post.text,
            post_date=post_date,
            has_image=bool(image_result),
            with_logo=bool(image_input),
            image_url=(image_result.url if image_result else None),
        )

        card_id = None
        if trello:
            if image_result:
                card = trello.attach_image_to_post(
                    generated_post,
                    image_url=image_result.url,
                    image_path=str(image_result.local_path) if image_result.local_path else None,
                )
            else:
                card = trello.create_card(generated_post)
            card_id = getattr(card, "id", None)

        notion_page_id = None
        if notion:
            page = notion.create_page(generated_post, status="Scheduled", image_url=(image_result.url if image_result else None))
            notion_page_id = page.get("id") if isinstance(page, dict) else None

        results.append(
            {
                "text": generated_post.text,
                "image_prompt": generated_post.image_prompt,
                "image_url": image_result.url if image_result else None,
                "image_local_path": str(image_result.local_path) if image_result and image_result.local_path else None,
                "trello_card_id": card_id,
                "notion_page_id": notion_page_id,
            }
        )

    _save_planned_posts(remaining, plan_path)
    print(
        json.dumps(
            {
                "provider": provider,
                "provider_user_id": provider_user_id,
                "generated": len(results),
                "remaining_planned_posts": len(remaining),
                "image_generation": {
                    "requested": bool(args.with_image),
                    "enabled": bool(image_generator),
                    "model": image_model,
                    "has_logo_input": bool(image_input),
                    "skipped_reason": (
                        "missing_logo_input"
                        if (bool(args.with_image) and model_requires_input and not image_input)
                        else (
                            "missing_api_key"
                            if (bool(args.with_image) and (not user or not user.image_api_key))
                            else ("disabled" if not bool(args.with_image) else None)
                        )
                    ),
                },
                "results": results,
                "memory": {
                    "last_entry_id": last_entry_id,
                    "memory_enabled": True,
                },
            },
            indent=2,
        )
    )
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    runtime_store = RuntimeConfigStore(Path(args.config_path) if args.config_path else None)
    runtime = runtime_store.load()
    plan_path = Path(args.plan_path) if args.plan_path else None
    planned = _load_planned_posts(plan_path)
    if not planned:
        print(json.dumps({"synced": 0, "message": "No planned posts to sync."}, indent=2))
        return 0

    synced_trello = 0
    synced_notion = 0
    if args.target in {"trello", "both"}:
        trello = TrelloSync()
        trello.setup_board()
        for item in planned:
            generated_post = _generated_post_from_dict(item)
            if not generated_post.text:
                post = _postplan_from_generated(item)
                generated_post = ContentGenerator(
                    brand_profile_path=Path(args.brand_profile_path) if args.brand_profile_path else None
                ).generate_post(post)
            trello.create_card(generated_post)
            synced_trello += 1

    if args.target in {"notion", "both"}:
        notion = NotionSync()
        for item in planned:
            generated_post = _generated_post_from_dict(item)
            if not generated_post.text:
                post = _postplan_from_generated(item)
                generated_post = ContentGenerator(
                    brand_profile_path=Path(args.brand_profile_path) if args.brand_profile_path else None
                ).generate_post(post)
            notion.create_page(generated_post, status="Draft")
            synced_notion += 1

    print(
        json.dumps(
            {
                "target": args.target,
                "planned_posts": len(planned),
                "synced_trello": synced_trello,
                "synced_notion": synced_notion,
                "runtime_trello_enabled": runtime.use_trello,
                "runtime_notion_enabled": runtime.use_notion,
            },
            indent=2,
        )
    )
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    runtime_store = RuntimeConfigStore(Path(args.config_path) if args.config_path else None)
    runtime = runtime_store.load()
    provider, provider_user_id = _resolve_identity_from_runtime(args, runtime)
    state = StateStore(Path(args.state_path) if args.state_path else None)
    user = state.get_user(provider=provider, provider_user_id=provider_user_id)
    planned = _load_planned_posts(Path(args.plan_path) if args.plan_path else None)
    sessions = LocalSessionStore(Path(args.session_db_path) if args.session_db_path else None)
    topup = sessions.get_session(_session_user_id(provider, provider_user_id))

    print(
        json.dumps(
            {
                "provider": provider,
                "provider_user_id": provider_user_id,
                "configured": bool(runtime.provider_user_id),
                "has_image_api_key": bool(user and user.image_api_key),
                "brand_logo_configured": bool(runtime.brand_logo_url),
                "planned_posts": len(planned),
                "trello_enabled": runtime.use_trello,
                "notion_enabled": runtime.use_notion,
                "pending_topup_session": bool(topup),
            },
            indent=2,
        )
    )
    return 0


def cmd_pay(args: argparse.Namespace) -> int:
    runtime_store = RuntimeConfigStore(Path(args.config_path) if args.config_path else None)
    runtime = runtime_store.load()
    provider, provider_user_id = _resolve_identity_from_runtime(args, runtime)
    forwarded = argparse.Namespace(
        provider=provider,
        provider_user_id=provider_user_id,
        amount_usd=float(args.amount_usd),
        base_url=args.base_url,
        state_path=args.state_path,
        session_db_path=args.session_db_path,
    )
    return cmd_topup_start(forwarded)


def cmd_paid(args: argparse.Namespace) -> int:
    runtime_store = RuntimeConfigStore(Path(args.config_path) if args.config_path else None)
    runtime = runtime_store.load()
    provider, provider_user_id = _resolve_identity_from_runtime(args, runtime)
    forwarded = argparse.Namespace(
        provider=provider,
        provider_user_id=provider_user_id,
        tx_hash=args.tx_hash,
        session_id=args.session_id,
        base_url=args.base_url,
        wait=bool(args.wait),
        wait_timeout_seconds=int(args.wait_timeout_seconds),
        wait_interval_seconds=int(args.wait_interval_seconds),
        state_path=args.state_path,
        session_db_path=args.session_db_path,
    )
    return cmd_topup_claim(forwarded)


def cmd_check_env(args: argparse.Namespace) -> int:
    tmp_dir = Path(args.tmp_dir) if args.tmp_dir else Path(__file__).resolve().parents[2] / ".tmp"
    result = _collect_env_validation(tmp_dir)
    errors = result["errors"]
    warnings = result["warnings"]
    checks = result["checks"]

    status = "ok"
    rc = 0
    if errors:
        status = "error"
        rc = 1
    elif warnings:
        status = "warn"

    print(
        json.dumps(
            {
                "status": status,
                "errors": errors,
                "warnings": warnings,
                "checks": {
                    "SOCICLAW_PROVISION_URL": checks["SOCICLAW_PROVISION_URL"],
                    "SOCICLAW_IMAGE_API_KEY": checks["SOCICLAW_IMAGE_API_KEY"],
                    "XAI_API_KEY": checks["XAI_API_KEY"],
                    "TRELLO_READY": checks["TRELLO_READY"],
                    "NOTION_READY": checks["NOTION_READY"],
                    "TMP_WRITABLE": checks["TMP_WRITABLE"],
                },
            },
            indent=2,
        )
    )
    return rc


def _collect_env_validation(tmp_dir: Path) -> dict:
    def _has(name: str) -> bool:
        value = os.getenv(name)
        return bool(value and value.strip())

    errors = []
    warnings = []

    has_provision = _has("SOCICLAW_PROVISION_URL")
    has_image_api_key = _has("SOCICLAW_IMAGE_API_KEY")
    if not has_provision and not has_image_api_key:
        errors.append(
            "Set SOCICLAW_PROVISION_URL (recommended) or SOCICLAW_IMAGE_API_KEY (single-account mode)."
        )

    if not _has("XAI_API_KEY"):
        warnings.append("XAI_API_KEY not set (trend research and planning can fail).")

    has_trello_key = _has("TRELLO_API_KEY")
    has_trello_token = _has("TRELLO_TOKEN")
    if has_trello_key ^ has_trello_token:
        warnings.append("Trello env incomplete: set both TRELLO_API_KEY and TRELLO_TOKEN.")

    has_notion_key = _has("NOTION_API_KEY")
    has_notion_db = _has("NOTION_DATABASE_ID")
    if has_notion_key ^ has_notion_db:
        warnings.append("Notion env incomplete: set both NOTION_API_KEY and NOTION_DATABASE_ID.")

    tmp_ok = True
    try:
        tmp_dir.mkdir(parents=True, exist_ok=True)
        probe = tmp_dir / ".write_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
    except Exception:
        tmp_ok = False
        errors.append(f"Cannot write to temp directory: {tmp_dir}")

    return {
        "errors": errors,
        "warnings": warnings,
        "checks": {
            "SOCICLAW_PROVISION_URL": has_provision,
            "SOCICLAW_IMAGE_API_KEY": has_image_api_key,
            "XAI_API_KEY": _has("XAI_API_KEY"),
            "TRELLO_READY": has_trello_key and has_trello_token,
            "NOTION_READY": has_notion_key and has_notion_db,
            "TMP_WRITABLE": tmp_ok,
        },
    }


def _session_user_id(provider: str, provider_user_id: str) -> str:
    return f"{provider}:{provider_user_id}"


def cmd_topup_start(args: argparse.Namespace) -> int:
    provider, provider_user_id = _validated_provider_fields(args.provider, str(args.provider_user_id))
    store = StateStore(Path(args.state_path) if args.state_path else None)
    user = store.get_user(provider=provider, provider_user_id=provider_user_id)
    if not user or not user.image_api_key:
        raise SystemExit(
            "Missing user image API key. Run provisioning first with "
            f"--provider {provider} --provider-user-id {provider_user_id}."
        )

    client = TopupClient(
        api_key=user.image_api_key,
        base_url=args.base_url or None,
    )
    start = client.start_topup(expected_amount_usd=float(args.amount_usd))

    sessions = LocalSessionStore(Path(args.session_db_path) if args.session_db_path else None)
    identity = _session_user_id(provider, provider_user_id)
    sessions.upsert_session(telegram_user_id=identity, session_id=start.session_id)

    print(
        json.dumps(
            {
                "provider": provider,
                "provider_user_id": provider_user_id,
                "session_id": start.session_id,
                "deposit_address": start.deposit_address,
                "amount_usdc_exact": start.amount_usdc_exact,
                "instruction": "Send USDC and then run topup-claim with --tx-hash.",
            },
            indent=2,
        )
    )
    return 0


def cmd_topup_claim(args: argparse.Namespace) -> int:
    provider, provider_user_id = _validated_provider_fields(args.provider, str(args.provider_user_id))
    try:
        tx_hash = validate_tx_hash(args.tx_hash)
    except ValueError as exc:
        raise SystemExit(str(exc))

    store = StateStore(Path(args.state_path) if args.state_path else None)
    user = store.get_user(provider=provider, provider_user_id=provider_user_id)
    if not user or not user.image_api_key:
        raise SystemExit(
            "Missing user image API key. Run provisioning first with "
            f"--provider {provider} --provider-user-id {provider_user_id}."
        )

    sessions = LocalSessionStore(Path(args.session_db_path) if args.session_db_path else None)
    identity = _session_user_id(provider, provider_user_id)
    session_id = args.session_id
    if not session_id:
        session_record = sessions.get_session(identity)
        if not session_record:
            raise SystemExit("No stored topup session found. Run topup-start first or provide --session-id.")
        session_id = session_record.session_id

    client = TopupClient(api_key=user.image_api_key, base_url=args.base_url or None)
    result = client.claim_topup(session_id=str(session_id), tx_hash=tx_hash)

    status = str(result.get("status", "")).lower().strip()
    if args.wait and status in {"pending", "confirming", "confirmed"}:
        deadline = time.time() + int(args.wait_timeout_seconds)
        poll_interval = max(1, int(args.wait_interval_seconds))
        while time.time() < deadline:
            time.sleep(poll_interval)
            status_result = client.status_topup(session_id=str(session_id))
            result = status_result
            status = str(result.get("status", "")).lower().strip()
            if status in {"credited", "failed", "expired"}:
                break

    if status == "credited":
        sessions.delete_session(identity)

    print(json.dumps(result, indent=2))
    return 0


def cmd_topup_status(args: argparse.Namespace) -> int:
    provider, provider_user_id = _validated_provider_fields(args.provider, str(args.provider_user_id))
    store = StateStore(Path(args.state_path) if args.state_path else None)
    user = store.get_user(provider=provider, provider_user_id=provider_user_id)
    if not user or not user.image_api_key:
        raise SystemExit(
            "Missing user image API key. Run provisioning first with "
            f"--provider {provider} --provider-user-id {provider_user_id}."
        )

    sessions = LocalSessionStore(Path(args.session_db_path) if args.session_db_path else None)
    identity = _session_user_id(provider, provider_user_id)
    session_id = args.session_id
    if not session_id:
        session_record = sessions.get_session(identity)
        if not session_record:
            raise SystemExit("No stored topup session found. Run topup-start first or provide --session-id.")
        session_id = session_record.session_id

    client = TopupClient(api_key=user.image_api_key, base_url=args.base_url or None)
    result = client.status_topup(session_id=str(session_id))
    print(json.dumps(result, indent=2))
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    runtime_store = RuntimeConfigStore(Path(args.config_path) if args.config_path else None)
    runtime = runtime_store.load()

    provider = args.provider or runtime.provider
    provider_user_id = str(args.provider_user_id or runtime.provider_user_id or "")
    state_store = StateStore(Path(args.state_path) if args.state_path else None)
    user = None
    if provider and provider_user_id:
        user = state_store.get_user(provider=provider, provider_user_id=provider_user_id)

    profile = load_brand_profile(Path(args.brand_profile_path) if args.brand_profile_path else None)
    sessions = LocalSessionStore(Path(args.session_db_path) if args.session_db_path else None)
    session_record = None
    if provider and provider_user_id:
        session_record = sessions.get_session(_session_user_id(provider, provider_user_id))

    payload = {
        "runtime_config_path": str(runtime_store.path),
        "provider": provider,
        "provider_user_id": provider_user_id,
        "runtime_config": runtime.__dict__,
        "brand_profile_path": str(Path(args.brand_profile_path) if args.brand_profile_path else runtime_store.path.parent / "company_profile.md"),
        "brand_profile_ready": bool(profile.name or profile.keywords or profile.value_proposition),
        "state_user_found": bool(user),
        "state_has_api_key": bool(user and user.image_api_key),
        "topup_session_found": bool(session_record),
        "env": {
            "SOCICLAW_PROVISION_URL": bool(os.getenv("SOCICLAW_PROVISION_URL")),
            "SOCICLAW_IMAGE_API_BASE_URL": bool(os.getenv("SOCICLAW_IMAGE_API_BASE_URL")),
            "XAI_API_KEY": bool(os.getenv("XAI_API_KEY")),
            "TRELLO_READY": bool(os.getenv("TRELLO_API_KEY") and os.getenv("TRELLO_TOKEN")),
            "NOTION_READY": bool(os.getenv("NOTION_API_KEY") and os.getenv("NOTION_DATABASE_ID")),
        },
    }
    print(json.dumps(payload, indent=2))
    return 0


def cmd_trello_normalize(args: argparse.Namespace) -> int:
    try:
        trello = TrelloSync(
            api_key=args.api_key or os.getenv("TRELLO_API_KEY"),
            token=args.token or os.getenv("TRELLO_TOKEN"),
            board_id=args.board_id or os.getenv("TRELLO_BOARD_ID"),
            request_delay_seconds=float(args.request_delay_seconds),
        )
        trello.setup_board()
        open_lists = [lst.name for lst in trello.board.list_lists("open")]
        print(
            json.dumps(
                {
                    "ok": True,
                    "board_id": trello.board_id,
                    "open_lists": open_lists,
                },
                indent=2,
            )
        )
        return 0
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 1


def cmd_smoke(args: argparse.Namespace) -> int:
    runtime_store = RuntimeConfigStore(Path(args.config_path) if args.config_path else None)
    runtime = runtime_store.load()

    provider = args.provider or runtime.provider
    provider_user_id = str(args.provider_user_id or runtime.provider_user_id or "")
    provider, provider_user_id = _validated_provider_fields(provider, provider_user_id)

    env_result = _collect_env_validation(Path(args.tmp_dir) if args.tmp_dir else Path(__file__).resolve().parents[2] / ".tmp")
    env_errors = env_result["errors"]
    env_warnings = env_result["warnings"]
    env_checks = env_result["checks"]

    state_store = StateStore(Path(args.state_path) if args.state_path else None)
    user = state_store.get_user(provider=provider, provider_user_id=provider_user_id)

    content_ok = False
    content_error = None
    sample_post = None
    try:
        generator = ContentGenerator(brand_profile_path=Path(args.brand_profile_path) if args.brand_profile_path else None)
        post = generator.generate_post(
            PostPlan(
                date=datetime.utcnow(),
                time=13,
                category="tips",
                topic=args.sample_topic,
                hashtags=["SociClaw", "AI", "Automation"],
            )
        )
        sample_post = {"text": post.text, "image_prompt": post.image_prompt}
        content_ok = True
    except Exception as exc:
        content_error = str(exc)

    checks = {
        "env_ok": len(env_errors) == 0,
        "user_state_found": bool(user),
        "user_has_image_api_key": bool(user and user.image_api_key),
        "content_generation_ok": content_ok,
    }

    status = "ok"
    if not checks["env_ok"] or not checks["content_generation_ok"] or not checks["user_has_image_api_key"]:
        status = "warn"

    recommendations = []
    if not checks["user_has_image_api_key"]:
        recommendations.append(
            f"Run provision-image-gateway --provider {provider} --provider-user-id {provider_user_id}."
        )
    if not checks["env_ok"]:
        recommendations.append("Run check-env and fix reported errors.")
    if not checks["content_generation_ok"]:
        recommendations.append("Run briefing to initialize brand profile context.")

    print(
        json.dumps(
            {
                "status": status,
                "provider": provider,
                "provider_user_id": provider_user_id,
                "checks": checks,
                "env_checks": env_checks,
                "env_errors": env_errors,
                "env_warnings": env_warnings,
                "content_error": content_error,
                "sample_post": sample_post,
                "recommendations": recommendations,
            },
            indent=2,
        )
    )
    return 0 if status == "ok" else 1


def cmd_e2e_staging(args: argparse.Namespace) -> int:
    runtime_store = RuntimeConfigStore(Path(args.config_path) if args.config_path else None)
    runtime = runtime_store.load()

    provider = args.provider or runtime.provider
    provider_user_id = str(args.provider_user_id or runtime.provider_user_id or "")
    provider, provider_user_id = _validated_provider_fields(provider, provider_user_id)

    steps = []

    env_result = _collect_env_validation(Path(args.tmp_dir) if args.tmp_dir else Path(__file__).resolve().parents[2] / ".tmp")
    env_ok = len(env_result["errors"]) == 0
    steps.append(
        {
            "step": "env_validation",
            "required": True,
            "ok": env_ok,
            "errors": env_result["errors"],
            "warnings": env_result["warnings"],
            "checks": env_result["checks"],
        }
    )

    state_store = StateStore(Path(args.state_path) if args.state_path else None)
    user = state_store.get_user(provider=provider, provider_user_id=provider_user_id)

    if (not user or not user.image_api_key) and args.auto_provision:
        provision_url = args.provision_url or os.getenv("SOCICLAW_PROVISION_URL")
        if provision_url:
            try:
                gateway = SociClawProvisioningGatewayClient(
                    url=provision_url,
                    internal_token=args.internal_token or os.getenv("SOCICLAW_INTERNAL_TOKEN"),
                )
                result = gateway.provision(
                    provider=provider,
                    provider_user_id=provider_user_id,
                    create_api_key=True,
                )
                state_store.upsert_user(
                    provider=provider,
                    provider_user_id=provider_user_id,
                    image_api_key=result.api_key,
                    wallet_address=result.wallet_address,
                )
                user = state_store.get_user(provider=provider, provider_user_id=provider_user_id)
                steps.append(
                    {
                        "step": "auto_provision",
                        "required": True,
                        "ok": bool(user and user.image_api_key),
                        "detail": "Provisioned user via gateway",
                    }
                )
            except Exception as exc:
                steps.append(
                    {
                        "step": "auto_provision",
                        "required": True,
                        "ok": False,
                        "error": str(exc),
                    }
                )
        else:
            steps.append(
                {
                    "step": "auto_provision",
                    "required": True,
                    "ok": False,
                    "error": "Missing provision URL for auto-provision",
                }
            )

    has_user_key = bool(user and user.image_api_key)
    steps.append(
        {
            "step": "user_state",
            "required": True,
            "ok": has_user_key,
            "detail": "Provisioned API key found in local state",
        }
    )

    content_ok = False
    content_error = None
    sample = None
    try:
        generator = ContentGenerator(brand_profile_path=Path(args.brand_profile_path) if args.brand_profile_path else None)
        post = generator.generate_post(
            PostPlan(
                date=datetime.utcnow(),
                time=13,
                category="tips",
                topic=args.sample_topic,
                hashtags=["SociClaw", "AI", "Automation"],
            )
        )
        sample = {"text": post.text, "image_prompt": post.image_prompt}
        content_ok = True
    except Exception as exc:
        content_error = str(exc)
    steps.append(
        {
            "step": "content_generation",
            "required": True,
            "ok": content_ok,
            "error": content_error,
            "sample": sample,
        }
    )

    if args.run_image:
        image_ok = False
        image_error = None
        image_result = None
        if has_user_key:
            try:
                image_url = runtime.brand_logo_url if runtime.provider == provider and str(runtime.provider_user_id or "") == str(provider_user_id) else None
                if "nano-banana" in (args.image_model or "").lower() and not image_url:
                    raise RuntimeError(
                        "Model nano-banana requires an input image. "
                        "Run setup-wizard with --brand-logo-url or test with another model."
                    )
                image_gen = ImageGenerator(
                    api_key=user.image_api_key,
                    model=args.image_model,
                    image_url=image_url,
                )
                image_prompt = _logo_directed_prompt(args.image_prompt, bool(image_url))
                image = image_gen.generate_image(image_prompt, user_address=f"{provider}:{provider_user_id}")
                image_ok = True
                image_result = {"url": image.url, "local_path": str(image.local_path) if image.local_path else None}
            except Exception as exc:
                image_error = str(exc)
        else:
            image_error = "No user API key available"
        steps.append(
            {
                "step": "image_generation",
                "required": True,
                "ok": image_ok,
                "error": image_error,
                "result": image_result,
            }
        )

    if args.run_topup:
        topup_ok = False
        topup_error = None
        topup_result = None
        if has_user_key:
            try:
                topup = TopupClient(
                    api_key=user.image_api_key,
                    base_url=args.base_url or os.getenv("SOCICLAW_IMAGE_API_BASE_URL"),
                )
                started = topup.start_topup(expected_amount_usd=float(args.topup_amount_usd))
                topup_result = {
                    "session_id": started.session_id,
                    "deposit_address": started.deposit_address,
                    "amount_usdc_exact": started.amount_usdc_exact,
                }
                if args.tx_hash:
                    claim = topup.claim_topup(session_id=started.session_id, tx_hash=args.tx_hash)
                    topup_result["claim"] = claim
                topup_ok = True
            except Exception as exc:
                topup_error = str(exc)
        else:
            topup_error = "No user API key available"
        steps.append(
            {
                "step": "topup_flow",
                "required": True,
                "ok": topup_ok,
                "error": topup_error,
                "result": topup_result,
            }
        )

    if args.run_sync:
        sync_results = []
        if args.sync_target in {"trello", "both"}:
            try:
                trello = TrelloSync(request_delay_seconds=0)
                trello.setup_board()
                sync_results.append({"target": "trello", "ok": True})
            except Exception as exc:
                sync_results.append({"target": "trello", "ok": False, "error": str(exc)})

        if args.sync_target in {"notion", "both"}:
            try:
                notion = NotionSync()
                notion.get_pending_posts()
                sync_results.append({"target": "notion", "ok": True})
            except Exception as exc:
                sync_results.append({"target": "notion", "ok": False, "error": str(exc)})

        steps.append(
            {
                "step": "sync_connectivity",
                "required": True,
                "ok": all(x.get("ok") for x in sync_results),
                "targets": sync_results,
            }
        )

    required_failures = [s for s in steps if s.get("required") and not s.get("ok")]
    status = "ok" if not required_failures else "failed"
    print(
        json.dumps(
            {
                "status": status,
                "provider": provider,
                "provider_user_id": provider_user_id,
                "steps": steps,
                "required_failures": len(required_failures),
            },
            indent=2,
        )
    )
    return 0 if status == "ok" else 1


def cmd_release_audit(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[2]
    placeholder_findings = scan_placeholders(root)
    forbidden_terms = [x.strip() for x in (args.forbidden_terms or "").split(",") if x.strip()]
    forbidden_findings = scan_forbidden_terms(root, forbidden_terms)

    findings = []
    for f in placeholder_findings:
        findings.append({"kind": f.kind, "file": f.file, "line": f.line, "value": f.value})
    for f in forbidden_findings:
        findings.append({"kind": f.kind, "file": f.file, "line": f.line, "value": f.value})

    has_placeholder = bool(placeholder_findings)
    has_forbidden = bool(forbidden_findings)
    status = "ok"
    if args.strict:
        if has_placeholder or has_forbidden:
            status = "failed"
    else:
        if has_placeholder or has_forbidden:
            status = "warn"

    payload = {
        "status": status,
        "strict": bool(args.strict),
        "root": str(root),
        "counts": {
            "placeholders": len(placeholder_findings),
            "forbidden_terms": len(forbidden_findings),
            "total": len(findings),
        },
        "findings": findings[: max(1, int(args.max_findings))],
    }
    print(json.dumps(payload, indent=2))
    return 0 if status == "ok" else 1


def cmd_self_update(args: argparse.Namespace) -> int:
    repo_dir = Path(args.repo_dir).resolve() if args.repo_dir else Path(__file__).resolve().parents[2]

    # NOTE: This build intentionally does not execute any remote-update operations.
    # Self-updating (remote code + dependencies) is frequently flagged as high risk by scanners.
    # Provide explicit manual steps instead.
    print(
        json.dumps(
            {
                "ok": True,
                "updated": False,
                "stage": "manual-update-required",
                "repo_dir": str(repo_dir),
                "message": "For security, this build does not run self-update automatically. Run these commands on the host:",
                "steps": [
                    "update the repository on the host using your normal operational process",
                    "create a fresh Python environment for the updated code (or reuse a trusted one)",
                    "install/update dependencies in that environment",
                    "restart your OpenClaw service/bot",
                ],
            },
            indent=2,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="sociclaw", description="SociClaw CLI")
    sub = p.add_subparsers(dest="cmd")
    p.set_defaults(func=cmd_home)

    p_prox = sub.add_parser(
        "provision-image-gateway",
        help="Provision via your backend gateway (recommended; keeps the admin secret server-side)",
    )
    p_prox.add_argument("--provider", required=True, help="e.g. telegram")
    p_prox.add_argument("--provider-user-id", required=True, help="e.g. Telegram user id")
    p_prox.add_argument(
        "--url",
        default=os.getenv("SOCICLAW_PROVISION_URL"),
        help="Gateway URL (e.g. https://api.sociclaw.com/api/sociclaw/provision)",
    )
    p_prox.add_argument(
        "--internal-token",
        default=os.getenv("SOCICLAW_INTERNAL_TOKEN"),
        help="Optional. Use only if your gateway requires server-side auth.",
    )
    p_prox.add_argument("--state-path", default=None, help="Override state path (defaults to .tmp/sociclaw_state.json)")

    def cmd_gateway(args: argparse.Namespace) -> int:
        provider, provider_user_id = _validated_provider_fields(args.provider, str(args.provider_user_id))
        if not args.url:
            raise SystemExit("Missing gateway --url or env SOCICLAW_PROVISION_URL")

        client = SociClawProvisioningGatewayClient(
            url=args.url,
            internal_token=args.internal_token or None,
        )
        res = client.provision(
            provider=provider,
            provider_user_id=provider_user_id,
            create_api_key=True,
        )

        store = StateStore(Path(args.state_path) if args.state_path else None)
        store.upsert_user(
            provider=res.provider,
            provider_user_id=res.provider_user_id,
            image_api_key=res.api_key,
            wallet_address=res.wallet_address,
        )

        print(
            json.dumps(
                {
                    "provider": res.provider,
                    "provider_user_id": res.provider_user_id,
                    "api_key": _redact_secret(res.api_key),
                    "wallet_address": res.wallet_address,
                    "state_path": str(store.path),
                },
                indent=2,
            )
        )
        return 0

    p_prox.set_defaults(func=cmd_gateway)

    p_who = sub.add_parser("whoami", help="Show locally stored provisioned info for a provider user id")
    p_who.add_argument("--provider", required=True)
    p_who.add_argument("--provider-user-id", required=True)
    p_who.add_argument("--state-path", default=None)
    p_who.set_defaults(func=cmd_whoami)

    p_img = sub.add_parser("generate-image", help="Generate an image using the provisioned API key")
    p_img.add_argument("--provider", required=True)
    p_img.add_argument("--provider-user-id", required=True)
    p_img.add_argument("--prompt", required=True)
    p_img.add_argument(
        "--model",
        default=(
            os.getenv("SOCICLAW_IMAGE_MODEL")
            or "nano-banana"
        ),
    )
    p_img.add_argument("--output-dir", default=None)
    p_img.add_argument("--state-path", default=None)
    p_img.add_argument("--config-path", default=None, help="Optional runtime config path")
    p_img.add_argument("--image-url", default=None, help="Optional input image URL or local path (required for img2img models)")
    p_img.add_argument("--dry-run", action="store_true", help="Validate preconditions without calling image API")
    p_img.set_defaults(func=cmd_generate_image)

    p_brief = sub.add_parser(
        "briefing",
        help="Create/update Brand Brain profile used by content generation",
    )
    p_brief.add_argument("--path", default=None, help="Optional path for company_profile.md")
    p_brief.add_argument("--name", default=None)
    p_brief.add_argument("--slogan", default=None)
    p_brief.add_argument("--voice-tone", default=None)
    p_brief.add_argument("--personality-traits", default=None, help="Comma-separated list")
    p_brief.add_argument("--visual-style", default=None)
    p_brief.add_argument("--signature-openers", default=None, help="Comma-separated list of preferred opening phrases")
    p_brief.add_argument("--content-goals", default=None, help="Comma-separated list of outcomes this account should drive")
    p_brief.add_argument("--cta-style", default=None, help="Default CTA style: question|invitation|challenge")
    p_brief.add_argument("--target-audience", default=None)
    p_brief.add_argument("--value-proposition", default=None)
    p_brief.add_argument("--key-themes", default=None, help="Comma-separated list")
    p_brief.add_argument("--do-not-say", default=None, help="Comma-separated list")
    p_brief.add_argument("--keywords", default=None, help="Comma-separated list")
    p_brief.add_argument("--content-language", default=None, help="Content language (e.g. en, pt-BR)")
    p_brief.add_argument("--has-brand-document", action="store_true", default=None)
    p_brief.add_argument("--brand-document-path", default=None)
    p_brief.add_argument("--non-interactive", action="store_true", help="Do not prompt for missing values")
    p_brief.set_defaults(func=cmd_briefing)

    def _add_setup_args(parser_obj: argparse.ArgumentParser) -> None:
        parser_obj.add_argument("--config-path", default=None, help="Optional runtime config path")
        parser_obj.add_argument("--provider", default=None)
        parser_obj.add_argument("--provider-user-id", default=None)
        parser_obj.add_argument("--user-niche", default=None)
        parser_obj.add_argument("--posting-frequency", default=None)
        parser_obj.add_argument("--content-language", default=None)
        parser_obj.add_argument("--brand-logo-url", default=None)
        parser_obj.add_argument("--has-brand-document", action="store_true", default=None)
        parser_obj.add_argument("--brand-document-path", default=None)
        parser_obj.add_argument("--use-trello", action="store_true", default=None)
        parser_obj.add_argument("--use-notion", action="store_true", default=None)
        parser_obj.add_argument("--timezone", default=None)
        parser_obj.add_argument("--non-interactive", action="store_true", help="Do not prompt; keep defaults for missing values")
        parser_obj.set_defaults(func=cmd_setup_wizard)

    p_setup_wizard = sub.add_parser("setup-wizard", help="Interactive local setup wizard (provider/user defaults)")
    _add_setup_args(p_setup_wizard)

    p_setup = sub.add_parser("setup", help="Alias for setup-wizard")
    _add_setup_args(p_setup)

    p_plan = sub.add_parser("plan", help="Generate and store a content plan")
    p_plan.add_argument("--provider", default=None)
    p_plan.add_argument("--provider-user-id", default=None)
    p_plan.add_argument("--config-path", default=None, help="Optional runtime config path")
    p_plan.add_argument("--brand-profile-path", default=None)
    p_plan.add_argument("--plan-path", default=None)
    p_plan.add_argument("--topic", default=None, help="Override niche/topic for planning")
    p_plan.add_argument("--quarter", default=None, help="Quarter label (e.g. Q1) to force full planning mode")
    p_plan.add_argument("--full", action="store_true", help="Generate full quarterly volume")
    p_plan.add_argument("--days", type=int, default=None)
    p_plan.add_argument("--posts-per-day", type=int, default=None)
    p_plan.add_argument("--skip-research", action="store_true", help="Skip X research and use local fallback topics")
    p_plan.add_argument("--memory-db-path", default=None, help="Optional persistent memory DB path")
    p_plan.add_argument("--sync-trello", action="store_true")
    p_plan.add_argument("--sync-notion", action="store_true")
    p_plan.set_defaults(func=cmd_plan)

    p_generate = sub.add_parser("generate", help="Generate due posts and optionally images, then sync")
    p_generate.add_argument("--provider", default=None)
    p_generate.add_argument("--provider-user-id", default=None)
    p_generate.add_argument("--config-path", default=None, help="Optional runtime config path")
    p_generate.add_argument("--state-path", default=None, help="Optional state store path")
    p_generate.add_argument("--brand-profile-path", default=None)
    p_generate.add_argument("--plan-path", default=None)
    p_generate.add_argument("--count", type=int, default=None)
    p_generate.add_argument("--with-image", dest="with_image", action="store_true", default=True, help="Attempt image generation for selected posts (default on)")
    p_generate.add_argument("--no-image", dest="with_image", action="store_false", help="Skip image generation")
    p_generate.add_argument("--image-model", default=None)
    p_generate.add_argument("--image-url", default=None, help="Override logo/input image URL or local path")
    p_generate.add_argument("--memory-db-path", default=None, help="Optional persistent memory DB path")
    p_generate.add_argument("--sync-trello", action="store_true")
    p_generate.add_argument("--sync-notion", action="store_true")
    p_generate.set_defaults(func=cmd_generate)

    p_sync = sub.add_parser("sync", help="Sync stored planned posts to Trello/Notion")
    p_sync.add_argument("--config-path", default=None, help="Optional runtime config path")
    p_sync.add_argument("--brand-profile-path", default=None)
    p_sync.add_argument("--plan-path", default=None)
    p_sync.add_argument("--target", choices=["trello", "notion", "both"], default="both")
    p_sync.set_defaults(func=cmd_sync)

    p_status = sub.add_parser("status", help="Show local readiness and queue status")
    p_status.add_argument("--provider", default=None)
    p_status.add_argument("--provider-user-id", default=None)
    p_status.add_argument("--config-path", default=None)
    p_status.add_argument("--state-path", default=None)
    p_status.add_argument("--session-db-path", default=None)
    p_status.add_argument("--plan-path", default=None)
    p_status.set_defaults(func=cmd_status)

    p_reset = sub.add_parser("reset", help="Reset local SociClaw state/config and restart onboarding")
    p_reset.add_argument("--yes", action="store_true", help="Confirm destructive reset")
    p_reset.add_argument("--dry-run", action="store_true", help="Show what would be removed")
    p_reset.add_argument("--state-path", default=None, help="Optional state store path")
    p_reset.add_argument("--config-path", default=None, help="Optional runtime config path")
    p_reset.add_argument("--session-db-path", default=None, help="Optional topup session DB path")
    p_reset.add_argument("--brand-profile-path", default=None, help="Optional brand profile path")
    p_reset.add_argument("--memory-db-path", default=None, help="Optional persistent memory DB path")
    p_reset.set_defaults(func=cmd_reset)

    p_check = sub.add_parser("check-env", help="Preflight check for required env/settings")
    p_check.add_argument("--tmp-dir", default=None, help="Optional writable temp directory to validate")
    p_check.set_defaults(func=cmd_check_env)

    p_topup_start = sub.add_parser("topup-start", help="Start credits topup (returns deposit address + exact amount)")
    p_topup_start.add_argument("--provider", required=True, help="e.g. telegram")
    p_topup_start.add_argument("--provider-user-id", required=True, help="User id in the provider")
    p_topup_start.add_argument("--amount-usd", required=True, type=float, help="Expected USD amount (e.g. 5)")
    p_topup_start.add_argument("--base-url", default=os.getenv("SOCICLAW_IMAGE_API_BASE_URL"), help="Image API base URL")
    p_topup_start.add_argument("--state-path", default=None, help="Override state store path")
    p_topup_start.add_argument("--session-db-path", default=None, help="Override topup session DB path")
    p_topup_start.set_defaults(func=cmd_topup_start)

    p_pay = sub.add_parser("pay", help="Friendly alias for topup-start using configured provider/user")
    p_pay.add_argument("--provider", default=None)
    p_pay.add_argument("--provider-user-id", default=None)
    p_pay.add_argument("--config-path", default=None)
    p_pay.add_argument("--state-path", default=None)
    p_pay.add_argument("--session-db-path", default=None)
    p_pay.add_argument("--amount-usd", default=5.0, type=float)
    p_pay.add_argument("--base-url", default=os.getenv("SOCICLAW_IMAGE_API_BASE_URL"), help="Image API base URL")
    p_pay.set_defaults(func=cmd_pay)

    p_topup_claim = sub.add_parser("topup-claim", help="Claim a topup by txHash")
    p_topup_claim.add_argument("--provider", required=True, help="e.g. telegram")
    p_topup_claim.add_argument("--provider-user-id", required=True, help="User id in the provider")
    p_topup_claim.add_argument("--tx-hash", required=True, help="Base tx hash")
    p_topup_claim.add_argument("--session-id", default=None, help="Optional explicit session id")
    p_topup_claim.add_argument("--base-url", default=os.getenv("SOCICLAW_IMAGE_API_BASE_URL"), help="Image API base URL")
    p_topup_claim.add_argument("--wait", action="store_true", help="Poll status until terminal state or timeout")
    p_topup_claim.add_argument(
        "--wait-timeout-seconds",
        default=int(os.getenv("SOCICLAW_TOPUP_WAIT_TIMEOUT_SECONDS", "120")),
        type=int,
        help="Max time to wait when --wait is enabled",
    )
    p_topup_claim.add_argument(
        "--wait-interval-seconds",
        default=int(os.getenv("SOCICLAW_TOPUP_WAIT_INTERVAL_SECONDS", "5")),
        type=int,
        help="Polling interval when --wait is enabled",
    )
    p_topup_claim.add_argument("--state-path", default=None, help="Override state store path")
    p_topup_claim.add_argument("--session-db-path", default=None, help="Override topup session DB path")
    p_topup_claim.set_defaults(func=cmd_topup_claim)

    p_paid = sub.add_parser("paid", help="Friendly alias for topup-claim using configured provider/user")
    p_paid.add_argument("--provider", default=None)
    p_paid.add_argument("--provider-user-id", default=None)
    p_paid.add_argument("--config-path", default=None)
    p_paid.add_argument("--state-path", default=None)
    p_paid.add_argument("--session-db-path", default=None)
    p_paid.add_argument("--tx-hash", required=True, help="Base tx hash")
    p_paid.add_argument("--session-id", default=None)
    p_paid.add_argument("--base-url", default=os.getenv("SOCICLAW_IMAGE_API_BASE_URL"), help="Image API base URL")
    p_paid.add_argument("--wait", action="store_true")
    p_paid.add_argument("--wait-timeout-seconds", default=int(os.getenv("SOCICLAW_TOPUP_WAIT_TIMEOUT_SECONDS", "120")), type=int)
    p_paid.add_argument("--wait-interval-seconds", default=int(os.getenv("SOCICLAW_TOPUP_WAIT_INTERVAL_SECONDS", "5")), type=int)
    p_paid.set_defaults(func=cmd_paid)

    p_topup_status = sub.add_parser("topup-status", help="Get topup session status")
    p_topup_status.add_argument("--provider", required=True, help="e.g. telegram")
    p_topup_status.add_argument("--provider-user-id", required=True, help="User id in the provider")
    p_topup_status.add_argument("--session-id", default=None, help="Optional explicit session id")
    p_topup_status.add_argument("--base-url", default=os.getenv("SOCICLAW_IMAGE_API_BASE_URL"), help="Image API base URL")
    p_topup_status.add_argument("--state-path", default=None, help="Override state store path")
    p_topup_status.add_argument("--session-db-path", default=None, help="Override topup session DB path")
    p_topup_status.set_defaults(func=cmd_topup_status)

    p_doctor = sub.add_parser("doctor", help="Show local readiness summary (config/state/brand/env)")
    p_doctor.add_argument("--provider", default=None)
    p_doctor.add_argument("--provider-user-id", default=None)
    p_doctor.add_argument("--config-path", default=None, help="Optional runtime config path")
    p_doctor.add_argument("--state-path", default=None, help="Optional state store path")
    p_doctor.add_argument("--session-db-path", default=None, help="Optional session DB path")
    p_doctor.add_argument("--brand-profile-path", default=None, help="Optional brand profile path")
    p_doctor.set_defaults(func=cmd_doctor)

    p_trello_norm = sub.add_parser(
        "trello-normalize",
        help="Normalize Trello board lists (archive stale lists and move active lists to the left)",
    )
    p_trello_norm.add_argument("--api-key", default=None)
    p_trello_norm.add_argument("--token", default=None)
    p_trello_norm.add_argument("--board-id", default=None)
    p_trello_norm.add_argument("--request-delay-seconds", default=0.0, type=float)
    p_trello_norm.set_defaults(func=cmd_trello_normalize)

    p_smoke = sub.add_parser("smoke", help="Quick local smoke test (env + state + content generation)")
    p_smoke.add_argument("--provider", default=None)
    p_smoke.add_argument("--provider-user-id", default=None)
    p_smoke.add_argument("--config-path", default=None, help="Optional runtime config path")
    p_smoke.add_argument("--state-path", default=None, help="Optional state store path")
    p_smoke.add_argument("--brand-profile-path", default=None, help="Optional brand profile path")
    p_smoke.add_argument("--tmp-dir", default=None, help="Optional tmp directory for env validation")
    p_smoke.add_argument("--sample-topic", default="AI content systems", help="Sample topic for generation check")
    p_smoke.set_defaults(func=cmd_smoke)

    p_e2e = sub.add_parser("e2e-staging", help="End-to-end staging run with pass/fail summary")
    p_e2e.add_argument("--provider", default=None)
    p_e2e.add_argument("--provider-user-id", default=None)
    p_e2e.add_argument("--config-path", default=None)
    p_e2e.add_argument("--state-path", default=None)
    p_e2e.add_argument("--brand-profile-path", default=None)
    p_e2e.add_argument("--tmp-dir", default=None)
    p_e2e.add_argument("--sample-topic", default="AI content systems")
    p_e2e.add_argument("--auto-provision", action="store_true", help="Provision user if local state key is missing")
    p_e2e.add_argument("--provision-url", default=os.getenv("SOCICLAW_PROVISION_URL"))
    p_e2e.add_argument("--internal-token", default=os.getenv("SOCICLAW_INTERNAL_TOKEN"))
    p_e2e.add_argument("--run-image", action="store_true", help="Run real image generation")
    p_e2e.add_argument("--image-prompt", default="SociClaw blue abstract brand icon")
    p_e2e.add_argument("--image-model", default=os.getenv("SOCICLAW_IMAGE_MODEL") or "nano-banana")
    p_e2e.add_argument("--run-topup", action="store_true", help="Run topup start (and optional claim)")
    p_e2e.add_argument("--topup-amount-usd", default=5.0, type=float)
    p_e2e.add_argument("--tx-hash", default=None, help="Optional full tx hash for claim during topup step")
    p_e2e.add_argument("--base-url", default=os.getenv("SOCICLAW_IMAGE_API_BASE_URL"), help="Image/topup API base URL")
    p_e2e.add_argument("--run-sync", action="store_true", help="Test Trello/Notion connectivity")
    p_e2e.add_argument("--sync-target", choices=["trello", "notion", "both"], default="both")
    p_e2e.set_defaults(func=cmd_e2e_staging)

    p_release_audit = sub.add_parser("release-audit", help="Audit repo for placeholders and forbidden terms")
    p_release_audit.add_argument("--root", default=None, help="Repo root to scan")
    p_release_audit.add_argument(
        "--forbidden-terms",
        default="",
        help="Comma-separated list of forbidden terms (optional)",
    )
    p_release_audit.add_argument("--strict", action="store_true", help="Fail on any finding")
    p_release_audit.add_argument("--max-findings", default=200, type=int, help="Max findings to print")
    p_release_audit.set_defaults(func=cmd_release_audit)

    p_self_update = sub.add_parser("self-update", help="Print safe manual update instructions (no code executed)")
    p_self_update.add_argument("--repo-dir", default=None, help="Local skill repo directory")
    p_self_update.add_argument("--yes", action="store_true", help="Accepted for compatibility (no-op)")
    p_self_update.set_defaults(func=cmd_self_update)

    return p


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
