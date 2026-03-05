#!/usr/bin/env python3
"""Validate that registry metadata matches the skill's runtime contract."""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
RUNTIME_FILE = ROOT / "scripts" / "alpaca_api.py"
SKILL_FILE = ROOT / "SKILL.md"
METADATA_FILE = ROOT / "registry-metadata.json"
OPENAI_MANIFEST_FILE = ROOT / "agents" / "openai.yaml"

EXPECTED_REQUIRED_ENV_VARS = ["ALPACA_API_KEY", "ALPACA_API_SECRET"]
EXPECTED_OPTIONAL_ENV_VARS = ["ALPACA_BASE_URL"]
UPSTREAM_HOMEPAGE = "https://clawhub.ai/oscraters/alpaca-markets"
UPSTREAM_SOURCE_REPOSITORY = "https://github.com/oscraters/alpaca-markets-skill.git"
UPSTREAM_DISTRIBUTION_PLATFORM = "clawhub"
EXPECTED_DISPLAY_NAME = "Alpaca Markets"
EXPECTED_DEFAULT_PROMPT_SKILL_REF = "$alpaca"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def warn(message: str) -> None:
    print(f"WARNING: {message}", file=sys.stderr)


def load_metadata() -> dict:
    try:
        return json.loads(METADATA_FILE.read_text())
    except FileNotFoundError:
        fail(f"missing metadata file: {METADATA_FILE}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {METADATA_FILE}: {exc}")


def load_skill_frontmatter() -> dict:
    try:
        text = SKILL_FILE.read_text()
    except FileNotFoundError:
        fail(f"missing skill file: {SKILL_FILE}")

    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        fail("SKILL.md is missing frontmatter")

    frontmatter_text = match.group(1)
    parsed: dict[str, object] = {}
    stack: list[tuple[int, object]] = [(-1, parsed)]

    lines = frontmatter_text.splitlines()
    for index, raw_line in enumerate(lines):
        if not raw_line.strip():
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        stripped = raw_line.strip()

        while stack and indent <= stack[-1][0]:
            stack.pop()

        container = stack[-1][1]

        if stripped.startswith("- "):
            if not isinstance(container, list):
                fail(f"invalid frontmatter list structure near: {raw_line}")
            container.append(stripped[2:].strip())
            continue

        if ":" not in stripped:
            fail(f"invalid frontmatter line: {raw_line}")

        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()

        if value:
            if not isinstance(container, dict):
                fail(f"invalid frontmatter mapping structure near: {raw_line}")
            container[key] = value
            continue

        next_container: object
        next_line_is_list = False
        for candidate in lines[index + 1 :]:
            if not candidate.strip():
                continue
            candidate_indent = len(candidate) - len(candidate.lstrip(" "))
            if candidate_indent <= indent:
                break
            next_line_is_list = candidate.strip().startswith("- ")
            break

        next_container = [] if next_line_is_list else {}
        if not isinstance(container, dict):
            fail(f"invalid frontmatter nesting near: {raw_line}")
        container[key] = next_container
        stack.append((indent, next_container))

    return parsed


def extract_runtime_env_usage() -> set[str]:
    try:
        tree = ast.parse(RUNTIME_FILE.read_text(), filename=str(RUNTIME_FILE))
    except FileNotFoundError:
        fail(f"missing runtime file: {RUNTIME_FILE}")

    env_vars: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr != "getenv":
            continue
        if not isinstance(node.func.value, ast.Name) or node.func.value.id != "os":
            continue
        if not node.args or not isinstance(node.args[0], ast.Constant):
            continue
        if isinstance(node.args[0].value, str):
            env_vars.add(node.args[0].value)
    return env_vars


def extract_skill_env_mentions() -> set[str]:
    try:
        text = SKILL_FILE.read_text()
    except FileNotFoundError:
        fail(f"missing skill file: {SKILL_FILE}")
    return set(re.findall(r"`(ALPACA_[A-Z_]+)`", text))


def get_skill_requires(frontmatter: dict) -> dict:
    metadata = frontmatter.get("metadata", {})
    if not isinstance(metadata, dict):
        fail("SKILL.md frontmatter metadata must be a mapping")
    openclaw = metadata.get("openclaw", {})
    if not isinstance(openclaw, dict):
        fail("SKILL.md frontmatter metadata.openclaw must be a mapping")
    requires = openclaw.get("requires", {})
    if not isinstance(requires, dict):
        fail("SKILL.md frontmatter metadata.openclaw.requires must be a mapping")
    return requires


def load_openai_manifest() -> dict[str, str]:
    try:
        text = OPENAI_MANIFEST_FILE.read_text()
    except FileNotFoundError:
        return {}

    patterns = {
        "display_name": r'^\s*display_name:\s*"([^"]+)"\s*$',
        "short_description": r'^\s*short_description:\s*"([^"]+)"\s*$',
        "default_prompt": r'^\s*default_prompt:\s*"([^"]+)"\s*$',
    }
    values: dict[str, str] = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, flags=re.MULTILINE)
        if not match:
            fail(f"manifest is missing interface.{key}")
        values[key] = match.group(1)
    return values


def validate_metadata(metadata: dict) -> None:
    required = metadata.get("required_env_vars")
    optional = metadata.get("optional_env_vars")
    credential = metadata.get("primary_credential", {})
    provenance = metadata.get("provenance", {})

    if required != EXPECTED_REQUIRED_ENV_VARS:
        fail(
            "required_env_vars must exactly match "
            f"{EXPECTED_REQUIRED_ENV_VARS}, got {required}"
        )

    if optional != EXPECTED_OPTIONAL_ENV_VARS:
        fail(
            "optional_env_vars must exactly match "
            f"{EXPECTED_OPTIONAL_ENV_VARS}, got {optional}"
        )

    homepage = metadata.get("homepage")
    source_repository = metadata.get("source_repository")

    if not homepage:
        fail("homepage is required")

    if not source_repository:
        fail("source_repository is required")

    if homepage == source_repository:
        fail("homepage and source_repository must be distinct")

    if homepage != UPSTREAM_HOMEPAGE:
        warn(
            "homepage differs from upstream distribution URL: "
            f"{homepage} != {UPSTREAM_HOMEPAGE}"
        )

    if source_repository != UPSTREAM_SOURCE_REPOSITORY:
        warn(
            "source_repository differs from upstream source repo: "
            f"{source_repository} != {UPSTREAM_SOURCE_REPOSITORY}"
        )

    if credential.get("env_vars") != EXPECTED_REQUIRED_ENV_VARS:
        fail("primary_credential.env_vars must match required_env_vars")

    if not credential.get("type"):
        fail("primary_credential.type is required")

    if not provenance.get("distribution_platform"):
        fail("provenance.distribution_platform is required")

    if not provenance.get("distribution_url"):
        fail("provenance.distribution_url is required")

    if not provenance.get("owner") or not provenance.get("repository"):
        fail("provenance.owner and provenance.repository are required")

    if provenance.get("distribution_platform") != UPSTREAM_DISTRIBUTION_PLATFORM:
        warn(
            "provenance.distribution_platform differs from upstream default: "
            f"{provenance.get('distribution_platform')} != {UPSTREAM_DISTRIBUTION_PLATFORM}"
        )

    if provenance.get("distribution_url") != UPSTREAM_HOMEPAGE:
        warn(
            "provenance.distribution_url differs from upstream default: "
            f"{provenance.get('distribution_url')} != {UPSTREAM_HOMEPAGE}"
        )


def validate_skill_frontmatter(frontmatter: dict, metadata: dict) -> None:
    if frontmatter.get("name") != metadata.get("name"):
        fail("SKILL.md frontmatter name must match registry metadata name")

    if frontmatter.get("description") != metadata.get("description"):
        fail("SKILL.md frontmatter description must match registry metadata description")

    if frontmatter.get("homepage") != metadata.get("homepage"):
        fail("SKILL.md frontmatter homepage must match registry metadata homepage")

    requires = get_skill_requires(frontmatter)
    required = requires.get("env")
    optional = requires.get("optionalEnv")
    primary = requires.get("primaryEnv")

    if required != metadata.get("required_env_vars"):
        fail("SKILL.md frontmatter metadata.openclaw.requires.env must match registry metadata")

    if optional != metadata.get("optional_env_vars"):
        fail("SKILL.md frontmatter metadata.openclaw.requires.optionalEnv must match registry metadata")

    if primary != metadata.get("primary_credential", {}).get("env_vars"):
        fail("SKILL.md frontmatter metadata.openclaw.requires.primaryEnv must match primary credential env vars")

    if requires.get("sourceRepository") != metadata.get("source_repository"):
        fail("SKILL.md frontmatter sourceRepository must match registry metadata")

    provenance = metadata.get("provenance", {})
    if requires.get("distributionPlatform") != provenance.get("distribution_platform"):
        fail("SKILL.md frontmatter distributionPlatform must match registry provenance")

    if requires.get("distributionUrl") != provenance.get("distribution_url"):
        fail("SKILL.md frontmatter distributionUrl must match registry provenance")


def validate_runtime_consistency(metadata: dict) -> None:
    runtime_envs = extract_runtime_env_usage()
    skill_envs = extract_skill_env_mentions()
    declared_envs = set(metadata["required_env_vars"]) | set(metadata["optional_env_vars"])

    if runtime_envs != declared_envs:
        fail(
            "runtime env vars do not match registry metadata: "
            f"runtime={sorted(runtime_envs)} declared={sorted(declared_envs)}"
        )

    if not declared_envs.issubset(skill_envs):
        fail(
            "SKILL.md is missing declared env vars: "
            f"{sorted(declared_envs - skill_envs)}"
        )


def validate_openai_manifest(metadata: dict) -> None:
    manifest = load_openai_manifest()

    if not manifest:
        return

    if manifest["display_name"] != EXPECTED_DISPLAY_NAME:
        fail(f"manifest display_name must be {EXPECTED_DISPLAY_NAME}")

    if "alpaca" not in manifest["short_description"].lower():
        fail("manifest short_description must mention Alpaca")

    if EXPECTED_DEFAULT_PROMPT_SKILL_REF not in manifest["default_prompt"]:
        fail(
            "manifest default_prompt must reference the skill as "
            f"{EXPECTED_DEFAULT_PROMPT_SKILL_REF}"
        )

    if "paper trading" not in manifest["default_prompt"].lower():
        fail("manifest default_prompt should steer users toward paper trading")

    if metadata["name"] not in manifest["default_prompt"]:
        fail("manifest default_prompt must reference the skill name")


def main() -> None:
    metadata = load_metadata()
    frontmatter = load_skill_frontmatter()
    validate_metadata(metadata)
    validate_skill_frontmatter(frontmatter, metadata)
    validate_runtime_consistency(metadata)
    validate_openai_manifest(metadata)
    print("registry metadata validation passed")


if __name__ == "__main__":
    main()
