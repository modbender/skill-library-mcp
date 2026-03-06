#!/usr/bin/env python3
"""Generate a mode-aware OpenClaw rollout checklist with hard security gates."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

PROVIDER_LINKS = {
    "local": "https://docs.openclaw.ai/start/getting-started",
    "fly": "https://docs.openclaw.ai/install/fly",
    "render": "https://docs.openclaw.ai/install/render",
    "railway": "https://docs.openclaw.ai/install/railway",
    "hetzner": "https://docs.openclaw.ai/install/hetzner",
    "gcp": "https://docs.openclaw.ai/install/gcp",
}

MODE_PROVIDER_ALLOWED = {
    "local": {"local"},
    "hosted": {"fly", "render", "railway", "hetzner", "gcp"},
}

CHANNEL_LINKS = {
    "telegram": "https://docs.openclaw.ai/channels/telegram",
    "discord": "https://docs.openclaw.ai/channels/discord",
    "slack": "https://docs.openclaw.ai/channels/slack",
}

INTEGRATION_LINKS = {
    "email": "https://docs.openclaw.ai/integrations/gmail",
    "calendar": "https://docs.openclaw.ai/integrations/google-calendar",
}

OS_NOTES = {
    "macos": "Use Homebrew-first install paths and verify shell PATH exports.",
    "linux": "Use distro package manager/system tooling and verify daemon startup strategy.",
    "windows-wsl2": "Run commands inside WSL2 Linux shell and avoid mixed Windows/WSL paths.",
}

DEFAULT_LEDGER_FILE = "openclaw-manager-operations-ledger.md"


def parse_csv(raw: str, *, allowed: set[str], label: str) -> list[str]:
    values = [value.strip().lower() for value in raw.split(",") if value.strip()]
    invalid = sorted({value for value in values if value not in allowed})
    if invalid:
        raise ValueError(f"Unsupported {label}: {', '.join(invalid)}")
    return values


def build_profile(mode: str, provider: str) -> str:
    if mode == "local":
        return "local"
    return f"hosted-{provider}"


def validate_mode_provider(mode: str, provider: str) -> None:
    allowed = MODE_PROVIDER_ALLOWED[mode]
    if provider not in allowed:
        allowed_list = ", ".join(sorted(allowed))
        raise ValueError(f"Provider '{provider}' is invalid for mode '{mode}'. Allowed: {allowed_list}")


def render(
    *,
    mode: str,
    provider: str,
    os_name: str,
    channels: list[str],
    integrations: list[str],
    environment: str,
    exposure: str,
    ledger_file: str,
) -> str:
    now = datetime.now(timezone.utc).isoformat()
    profile = build_profile(mode, provider)

    lines = [
        "# OpenClaw Rollout Plan",
        "",
        f"- Generated: {now}",
        f"- Mode: {mode}",
        f"- Provider: {provider}",
        f"- OS: {os_name}",
        f"- Environment: {environment}",
        f"- Exposure: {exposure}",
        f"- Secrets profile: {profile}",
        f"- Ops ledger: {ledger_file}",
        "",
        "## 1. Scope Lock",
        "- [ ] Confirm operator intent and rollback owner.",
        "- [ ] Confirm mode/provider/OS matrix is valid for this run.",
        "- [ ] Append `scope_lock` entry to ops ledger.",
        "",
        "## 2. Preflight Validation",
        f"- [ ] Validate `.env` with `scripts/validate_openclaw_env.py --env-file .env --profile {profile}`.",
        "- [ ] Block progression on any validation failure.",
        "- [ ] Append `predeploy_validation` entry to ops ledger.",
        "",
        "## 3. Deployment or Install",
    ]

    if mode == "local":
        lines.extend(
            [
                f"- [ ] Follow local install/onboarding guide: {PROVIDER_LINKS['local']}",
                f"- [ ] Apply OS notes: {OS_NOTES[os_name]}",
                "- [ ] Verify local startup, state path permissions, and auth boundaries.",
                "- [ ] If exposure is public, complete security gates before enabling ingress.",
            ]
        )
    else:
        lines.extend(
            [
                f"- [ ] Clone OpenClaw source and follow provider guide: {PROVIDER_LINKS[provider]}",
                "- [ ] Configure persistent state before first traffic.",
                "- [ ] Deploy and capture URL + health endpoint evidence.",
                "- [ ] Verify runtime logs for startup/auth issues and token leakage.",
            ]
        )

    lines.extend(
        [
            "- [ ] Append `deploy_complete` entry to ops ledger.",
            "",
            "## 4. Channels",
        ]
    )

    if channels:
        for channel in channels:
            lines.append(f"- [ ] Configure {channel}: {CHANNEL_LINKS[channel]}")
            lines.append(f"- [ ] Smoke-test {channel} and mark status (`configured`/`pending_credentials`/`blocked`).")
    else:
        lines.append("- [ ] No channels selected for this rollout.")

    lines.extend(["", "## 5. Integrations"])

    if integrations:
        for integration in integrations:
            lines.append(f"- [ ] Configure {integration}: {INTEGRATION_LINKS[integration]}")
            lines.append(f"- [ ] Smoke-test {integration} and record status in ops ledger.")
    else:
        lines.append("- [ ] No integrations selected for this rollout.")

    lines.extend(
        [
            "",
            "## 6. Agent + Memory",
            "- [ ] Document memory persistence strategy and retention expectations.",
            "- [ ] Verify restart/recovery behavior.",
            "- [ ] Confirm agent behavior boundaries for selected environment.",
            "",
            "## 7. Hard Security Gates (Go/No-Go)",
            "- [ ] Gate 1: Secrets profile validation passed.",
            "- [ ] Gate 2: Network/exposure boundaries validated.",
            "- [ ] Gate 3: Channel/integration auth boundaries validated.",
            "- [ ] Gate 4: Runtime/persistence safety validated.",
            "- [ ] Gate 5: Incident readiness and rollback ownership documented.",
            "- [ ] Gate 6: Supply chain patch posture documented.",
            "- [ ] Gate 7: Ops ledger completeness validated.",
            "- [ ] Append `security_gate` entry to ops ledger.",
            "",
            "## 8. Handover",
            "- [ ] Produce provider status summary.",
            "- [ ] Produce channel/integration matrix.",
            "- [ ] Produce security pass/fail table with blockers.",
            "- [ ] Produce next actions ordered by risk.",
            "- [ ] Append `handover` entry to ops ledger.",
            "",
            "## 9. Explicit Blockers",
            "Stop rollout immediately if any are true:",
            "- [ ] Missing required secrets profile key(s).",
            "- [ ] Security gate has any failed mandatory item.",
            "- [ ] Rollback plan or owner missing.",
            "- [ ] Ops ledger missing required phase entries.",
        ]
    )

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate OpenClaw rollout checklist")
    parser.add_argument("--mode", required=True, choices=sorted(MODE_PROVIDER_ALLOWED))
    parser.add_argument("--provider", required=True, choices=sorted(PROVIDER_LINKS))
    parser.add_argument("--os", required=True, choices=sorted(OS_NOTES), dest="os_name")
    parser.add_argument("--channels", default="", help="Comma-separated channels: telegram,discord,slack")
    parser.add_argument("--integrations", default="", help="Comma-separated integrations: email,calendar")
    parser.add_argument("--environment", default="prod", help="Environment label (dev/staging/prod)")
    parser.add_argument("--exposure", required=True, choices=["private", "public"])
    parser.add_argument("--ledger-file", default=DEFAULT_LEDGER_FILE, help="Path to ops ledger markdown file")
    parser.add_argument("--output", required=True, help="Output markdown file")
    args = parser.parse_args()

    try:
        validate_mode_provider(args.mode, args.provider)
        channels = parse_csv(args.channels, allowed=set(CHANNEL_LINKS), label="channels") if args.channels else []
        integrations = (
            parse_csv(args.integrations, allowed=set(INTEGRATION_LINKS), label="integrations")
            if args.integrations
            else []
        )
    except ValueError as err:
        print(f"[ERROR] {err}")
        return 1

    content = render(
        mode=args.mode,
        provider=args.provider,
        os_name=args.os_name,
        channels=channels,
        integrations=integrations,
        environment=args.environment,
        exposure=args.exposure,
        ledger_file=args.ledger_file,
    )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content)

    print(f"[OK] Wrote rollout plan: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
