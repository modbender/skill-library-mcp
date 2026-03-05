#!/usr/bin/env python3
"""Run an end-to-end onboarding pass and generate a reusable profile."""

from __future__ import annotations

import argparse
import json
import os
from getpass import getpass
from pathlib import Path


def _ensure_requests_runtime() -> int:
    """Ensure `requests` is available and fail with explicit setup instructions."""
    try:
        import requests  # noqa: F401

        return 0
    except ModuleNotFoundError:
        print("Missing Python dependency: requests")
        print("Run: python3 -m venv .venv-salesforce && .venv-salesforce/bin/python -m pip install requests")
        print("Then re-run onboarding with: .venv-salesforce/bin/python scripts/onboarding.py")
        return 1


def _guided_setup_walkthrough() -> None:
    print("\nNeed help finding credentials? Quick setup path:")
    print("1) Salesforce -> Setup -> App Manager -> New Connected App")
    print("2) Copy Consumer Key and Consumer Secret")
    print("3) Use org URL as instance URL (https://<your-domain>.my.salesforce.com)")
    print("4) Use a dedicated least-privilege integration user")


def _prompt_and_save_credentials(
    missing: list[str],
    save_credentials,
    guided: bool = False,
    persist: bool = True,
) -> bool:
    """Prompt user for missing credentials and persist or set session-only creds."""
    if not sys.stdin.isatty():
        print(
            "Missing credentials and no interactive TTY available. "
            "Pass --client-id/--client-secret/--instance-url or run in an interactive terminal."
        )
        return False

    print("\nWelcome to Salesforce Query onboarding.")
    print("This skill discovers your Salesforce schema and builds reusable GTM mappings for research workflows.")
    print("\nTo continue, authenticate with:")
    print("- SALESFORCE_CLIENT_ID (Connected App Consumer Key)")
    print("- SALESFORCE_CLIENT_SECRET (Connected App Consumer Secret)")
    print("- SALESFORCE_INSTANCE_URL (https://<your-domain>.my.salesforce.com)")
    print("\nSafe handling:")
    print("- Use a trusted local terminal")
    print("- Use a dedicated least-privilege integration user")
    print("- Credentials are stored in macOS Keychain by default")
    print("- Use --no-save to keep credentials in-memory for this run only")
    print("\nIf you already have credentials, paste them now.")
    print("If not, type 'help' when prompted for quick setup guidance.")
    print("Automation option: --client-id/--client-secret/--instance-url [--no-save]")

    if guided:
        _guided_setup_walkthrough()

    client_id = ""
    if "SALESFORCE_CLIENT_ID" in missing:
        client_id = input("\nEnter SALESFORCE_CLIENT_ID: ").strip()
        if client_id.lower() == "help":
            _guided_setup_walkthrough()
            client_id = input("Enter SALESFORCE_CLIENT_ID: ").strip()

    client_secret = ""
    if "SALESFORCE_CLIENT_SECRET" in missing:
        client_secret = getpass("Enter SALESFORCE_CLIENT_SECRET (hidden): ").strip()

    instance_url = ""
    if "SALESFORCE_INSTANCE_URL" in missing:
        instance_url = input("Enter SALESFORCE_INSTANCE_URL: ").strip()

    if not all([client_id, client_secret, instance_url]):
        print("Credential capture aborted or incomplete.")
        return False

    if persist:
        save_credentials(client_id=client_id, client_secret=client_secret, instance_url=instance_url)
        print("Credentials saved.")
        print("Tip: run `python3 scripts/credential_doctor.py` to verify local credential file safety.")
    else:
        os.environ['SALESFORCE_CLIENT_ID'] = client_id
        os.environ['SALESFORCE_CLIENT_SECRET'] = client_secret
        os.environ['SALESFORCE_INSTANCE_URL'] = instance_url
        print("Credentials set for this run only (not written to disk).")

    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Salesforce skill onboarding")
    parser.add_argument("--out", default=str(Path.home() / ".config" / "openclaw" / "salesforce_profile.json"))
    parser.add_argument("--client-id", help="Salesforce Connected App client id")
    parser.add_argument("--client-secret", help="Salesforce Connected App client secret")
    parser.add_argument("--instance-url", help="Salesforce instance URL")
    parser.add_argument("--non-interactive", action="store_true", help="Fail instead of prompting for credentials")
    parser.add_argument("--guided", action="store_true", help="Show quick credential setup guidance before prompts")
    parser.add_argument("--no-save", action="store_true", help="Do not persist credentials; use session-only env vars")
    args = parser.parse_args()

    runtime_status = _ensure_requests_runtime()
    if runtime_status != 0:
        return runtime_status

    from salesforce_client import (
        MissingCredentialsError,
        SalesforceClient,
        check_credentials,
        save_credentials,
    )
    from schema_discovery import SchemaDiscovery, infer_open_questions

    if args.client_id and args.client_secret and args.instance_url:
        cid = args.client_id.strip()
        csec = args.client_secret.strip()
        iurl = args.instance_url.strip()
        if args.no_save:
            os.environ['SALESFORCE_CLIENT_ID'] = cid
            os.environ['SALESFORCE_CLIENT_SECRET'] = csec
            os.environ['SALESFORCE_INSTANCE_URL'] = iurl
        else:
            save_credentials(client_id=cid, client_secret=csec, instance_url=iurl)

    is_configured, missing = check_credentials()
    if not is_configured:
        if args.non_interactive:
            print("Missing credentials:", ", ".join(missing))
            return 1
        if not _prompt_and_save_credentials(
            missing,
            save_credentials,
            guided=args.guided,
            persist=(not args.no_save),
        ):
            return 1

    try:
        sf = SalesforceClient()
    except MissingCredentialsError as exc:
        print(exc)
        return 1

    discovery = SchemaDiscovery(sf)
    schema = discovery.discover()
    questions = infer_open_questions(schema)

    profile = {
        "org": {"instance_url": sf.instance_url, "api_version": sf.API_VERSION},
        "capabilities": {
            "objects": schema["available"],
            "missing_defaults": schema["missing"],
        },
        "signals": schema["signals"],
        "open_questions": questions,
    }

    out_path = Path(args.out).expanduser()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(profile, indent=2))

    print(f"Wrote onboarding profile: {out_path}")
    print("Available objects:", ", ".join(schema["available"]))
    if questions:
        print("\nFollow-up questions:")
        for i, q in enumerate(questions, 1):
            print(f"{i}. {q}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
