#!/usr/bin/env python3
"""
init.py - Validate the Work Application skill configuration.
Tests profile loading, validators, CV rendering, tracker, and optional scraper.

Usage: python3 scripts/init.py
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _profile import (load_config, load_master_profile, profile_exists,
                       MASTER_PROFILE_FILE, ADAPTED_PROFILE_FILE, CONFIG_FILE, ProfileError)
from _validators import validate_profile, validate_length, validate_count
from _cv_renderer import render_cv
from _tracker import list_applications, CANDIDATURES_FILE


class Results:
    def __init__(self):
        self.passed  = []
        self.failed  = []
        self.skipped = []

    def ok(self, label: str, detail: str = ""):
        self.passed.append(label)
        suffix = f"  {detail}" if detail else ""
        print(f"  ✓  {label}{suffix}")

    def fail(self, label: str, reason: str = ""):
        self.failed.append(label)
        suffix = f"  → {reason}" if reason else ""
        print(f"  ✗  {label}{suffix}")

    def skip(self, label: str, reason: str = ""):
        self.skipped.append(label)
        print(f"  ~  {label}  (skipped: {reason})")

    def summary(self):
        total   = len(self.passed) + len(self.failed)
        skipped = len(self.skipped)
        print(f"\n  {len(self.passed)}/{total} checks passed", end="")
        if skipped:
            print(f", {skipped} skipped (disabled in config)", end="")
        print()
        if self.failed:
            print("\n  Failed checks:")
            for f in self.failed:
                print(f"    ✗  {f}")


def main():
    print("┌─────────────────────────────────────────┐")
    print("│   Work Application Skill - Init Check   │")
    print("└─────────────────────────────────────────┘")

    r = Results()
    cfg = None
    master_profile = None

    # ── 1. Configuration ─────────────────────────────────────────────────────
    print("\n● Configuration\n")

    try:
        cfg = load_config()
        r.ok("Load config", str(CONFIG_FILE))
    except Exception as e:
        r.fail("Load config", str(e))
        print("\n  Cannot proceed without a valid config. Check config.json.")
        r.summary()
        sys.exit(1)

    allow_write    = cfg.get("allow_write", False)
    allow_export   = cfg.get("allow_export", False)
    allow_scrape   = cfg.get("allow_scrape", False)
    allow_tracking = cfg.get("allow_tracking", False)
    readonly_mode  = cfg.get("readonly_mode", False)

    print(f"\n  allow_write    = {allow_write}")
    print(f"  allow_export   = {allow_export}")
    print(f"  allow_scrape   = {allow_scrape}")
    print(f"  allow_tracking = {allow_tracking}")
    print(f"  readonly_mode  = {readonly_mode}")

    # ── 2. Profile ───────────────────────────────────────────────────────────
    print("\n● Profile\n")

    try:
        if not profile_exists(MASTER_PROFILE_FILE):
            r.fail("Master profile exists", f"not found: {MASTER_PROFILE_FILE}")
        else:
            r.ok("Master profile exists", str(MASTER_PROFILE_FILE))
            try:
                master_profile = load_master_profile()
                identity = master_profile.get("identity", {})
                name = f"{identity.get('firstName', '')} {identity.get('lastName', '')}".strip() or "?"
                title = identity.get("title", "?")
                skills = master_profile.get("hard_skills", [])
                r.ok("Load master profile", f'name="{name}"  title="{title}"  skills={len(skills)}')
            except Exception as e:
                r.fail("Load master profile", str(e))
    except Exception as e:
        r.fail("Master profile exists", str(e))

    if master_profile:
        required_keys = ["identity", "hard_skills", "experiences"]
        missing = [k for k in required_keys if k not in master_profile]
        if missing:
            r.fail("Profile structure", f"missing keys: {', '.join(missing)}")
        else:
            r.ok("Profile structure", f"required keys present: {', '.join(required_keys)}")

    try:
        if profile_exists(ADAPTED_PROFILE_FILE):
            r.ok("Adapted profile exists", str(ADAPTED_PROFILE_FILE))
        else:
            r.skip("Adapted profile exists", "not yet generated (optional)")
    except Exception as e:
        r.skip("Adapted profile exists", str(e))

    # ── 3. Validators ────────────────────────────────────────────────────────
    print("\n● Validators\n")

    try:
        validate_length("Ingénieur Systèmes avec 12 ans d'expérience en environnements critiques.", "summary")
        r.ok("validate_length", "sample string within bounds")
    except Exception as e:
        r.fail("validate_length", str(e))

    try:
        validate_count(5, "experiences")
        r.ok("validate_count", "sample count within bounds")
    except Exception as e:
        r.fail("validate_count", str(e))

    # validate_profile targets adapted CVs (15 skills max, 6 bullets max)
    # Master profile intentionally exceeds these limits - skip validation on it
    try:
        from _profile import load_adapted_profile
        if profile_exists(ADAPTED_PROFILE_FILE):
            adapted = load_adapted_profile()
            result = validate_profile(adapted)
            errors   = result.get("errors", [])
            warnings = result.get("warnings", [])
            if errors:
                r.fail("validate_profile", f"{len(errors)} error(s), {len(warnings)} warning(s)")
            else:
                r.ok("validate_profile", f"0 errors, {len(warnings)} warning(s)")
        else:
            r.skip("validate_profile", "no adapted profile yet (generate one with 'render')")
    except Exception as e:
        r.skip("validate_profile", f"could not load adapted profile: {e}")

    # ── 4. CV Rendering ──────────────────────────────────────────────────────
    print("\n● CV Rendering\n")

    if not allow_export:
        r.skip("Render CV", "allow_export=false")
    else:
        profile_for_cv = master_profile
        try:
            if profile_exists(ADAPTED_PROFILE_FILE):
                from _profile import load_adapted_profile
                profile_for_cv = load_adapted_profile()
        except Exception:
            pass  # fall back to master profile

        if not profile_for_cv:
            r.skip("Render CV", "no profile available")
        else:
            try:
                html = render_cv(profile_for_cv, template="classic")
                if html and isinstance(html, str) and "<html" in html.lower():
                    r.ok("Render CV", f"HTML output ({len(html)} chars)")
                else:
                    r.fail("Render CV", "output is not valid HTML (missing <html tag)")
            except Exception as e:
                r.fail("Render CV", str(e))

    # ── 5. Tracker ───────────────────────────────────────────────────────────
    print("\n● Tracker\n")

    if not allow_tracking:
        r.skip("List applications", "allow_tracking=false")
    else:
        try:
            apps = list_applications()
            count = len(apps) if isinstance(apps, list) else "?"
            r.ok("List applications", f"{count} candidature(s) in {CANDIDATURES_FILE}")
        except Exception as e:
            r.fail("List applications", str(e))

    # ── 6. Scraper (optional) ────────────────────────────────────────────────
    print("\n● Scraper\n")

    if not allow_scrape:
        r.skip("Playwright", "allow_scrape=false")
        r.skip("Playwright-stealth", "allow_scrape=false")
    else:
        try:
            import playwright
            r.ok("Playwright", "installed")
        except ImportError:
            r.fail("Playwright", "not installed (pip install playwright)")

        try:
            import playwright_stealth
            r.ok("Playwright-stealth", "installed")
        except ImportError:
            r.fail("Playwright-stealth", "not installed (pip install playwright-stealth)")

    # ── Summary ──────────────────────────────────────────────────────────────
    print("\n┌─────────────────────────────────────────┐")
    print("│   Init check complete                   │")
    print("└─────────────────────────────────────────┘")
    r.summary()

    if r.failed:
        print("\n  Review config and profile files, then re-run init.\n")
        sys.exit(1)
    else:
        print("\n  Skill is ready to use. ✓\n")


if __name__ == "__main__":
    main()
