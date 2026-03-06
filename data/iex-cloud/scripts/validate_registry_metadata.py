#!/usr/bin/env python3
"""Validate that metadata, docs, and runtime requirements stay aligned."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILL_FILE = ROOT / "SKILL.md"
METADATA_FILE = ROOT / "registry-metadata.json"
RUNTIME_FILE = ROOT / "scripts" / "iex_cloud_cli.sh"
README_FILES = [
    ROOT / "README.md",
    ROOT / "scripts" / "README.md",
    ROOT / "references" / "api_docs.md",
]

EXPECTED_NAME = "iex-cloud"
EXPECTED_DESCRIPTION = (
    "Use this skill when a task needs IEX Cloud market data through the REST API "
    "(quotes, charts, fundamentals, market lists, and batch calls), including "
    "secure token handling and scriptable CLI usage."
)
EXPECTED_HOMEPAGE = "https://github.com/oscraters/iex-cloud-skill"
EXPECTED_SOURCE_REPOSITORY = "https://github.com/oscraters/iex-cloud-skill.git"
EXPECTED_REQUIRED_ENV_VARS = ["IEX_TOKEN"]
EXPECTED_OPTIONAL_ENV_VARS = ["IEX_CLOUD_TOKEN", "IEX_BASE_URL"]
EXPECTED_REQUIRED_BINARIES = ["curl"]
EXPECTED_OPTIONAL_BINARIES = ["jq"]
EXPECTED_TRUSTED_HOSTS = ["cloud.iexapis.com", "sandbox.iexapis.com"]


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def load_text(path: Path) -> str:
    try:
        return path.read_text()
    except FileNotFoundError:
        fail(f"missing file: {path}")


def load_metadata() -> dict:
    try:
        return json.loads(load_text(METADATA_FILE))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {METADATA_FILE}: {exc}")


def load_skill_frontmatter() -> dict:
    text = load_text(SKILL_FILE)
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        fail("SKILL.md is missing frontmatter")

    parsed: dict[str, object] = {}
    for raw_line in match.group(1).splitlines():
        if not raw_line.strip():
            continue
        key, sep, value = raw_line.partition(":")
        if not sep:
            fail(f"invalid frontmatter line: {raw_line}")
        key = key.strip()
        value = value.strip()
        if key == "metadata":
            try:
                parsed[key] = json.loads(value)
            except json.JSONDecodeError as exc:
                fail(f"invalid JSON in SKILL.md metadata frontmatter: {exc}")
        else:
            parsed[key] = value
    return parsed


def validate_metadata(metadata: dict) -> None:
    if metadata.get("name") != EXPECTED_NAME:
        fail("metadata name mismatch")
    if metadata.get("description") != EXPECTED_DESCRIPTION:
        fail("metadata description mismatch")
    if metadata.get("homepage") != EXPECTED_HOMEPAGE:
        fail("metadata homepage mismatch")
    if metadata.get("source_repository") != EXPECTED_SOURCE_REPOSITORY:
        fail("metadata source_repository mismatch")
    if metadata.get("required_env_vars") != EXPECTED_REQUIRED_ENV_VARS:
        fail("metadata required_env_vars mismatch")
    if metadata.get("optional_env_vars") != EXPECTED_OPTIONAL_ENV_VARS:
        fail("metadata optional_env_vars mismatch")
    if metadata.get("required_binaries") != EXPECTED_REQUIRED_BINARIES:
        fail("metadata required_binaries mismatch")
    if metadata.get("optional_binaries") != EXPECTED_OPTIONAL_BINARIES:
        fail("metadata optional_binaries mismatch")

    credential = metadata.get("primary_credential", {})
    if credential.get("type") != "env_var":
        fail("primary_credential.type must be env_var")
    if credential.get("env_vars") != EXPECTED_REQUIRED_ENV_VARS:
        fail("primary_credential.env_vars must match required_env_vars")

    provenance = metadata.get("provenance", {})
    for field in ("owner", "repository", "remote"):
        if not provenance.get(field):
            fail(f"metadata provenance.{field} is required")


def validate_skill_frontmatter(frontmatter: dict, metadata: dict) -> None:
    if frontmatter.get("name") != metadata.get("name"):
        fail("SKILL.md name must match registry metadata")
    if frontmatter.get("description") != metadata.get("description"):
        fail("SKILL.md description must match registry metadata")
    if frontmatter.get("homepage") != metadata.get("homepage"):
        fail("SKILL.md homepage must match registry metadata")

    openclaw = frontmatter.get("metadata", {}).get("openclaw", {})
    requires = openclaw.get("requires", {})
    if openclaw.get("skillKey") != metadata.get("name"):
        fail("SKILL.md metadata.openclaw.skillKey must match metadata name")
    if openclaw.get("homepage") != metadata.get("homepage"):
        fail("SKILL.md metadata.openclaw.homepage must match registry metadata")
    if openclaw.get("sourceRepository") != metadata.get("source_repository"):
        fail("SKILL.md metadata.openclaw.sourceRepository must match registry metadata")
    if requires.get("env") != metadata.get("required_env_vars"):
        fail("SKILL.md required env vars must match registry metadata")
    if requires.get("optionalEnv") != metadata.get("optional_env_vars"):
        fail("SKILL.md optional env vars must match registry metadata")
    if requires.get("primaryEnv") != metadata.get("primary_credential", {}).get("env_vars"):
        fail("SKILL.md primary env vars must match registry metadata")
    if requires.get("bins") != metadata.get("required_binaries"):
        fail("SKILL.md required binaries must match registry metadata")
    if requires.get("optionalBins") != metadata.get("optional_binaries"):
        fail("SKILL.md optional binaries must match registry metadata")


def validate_runtime(text: str) -> None:
    for token in ('IEX_TOKEN:-${IEX_CLOUD_TOKEN:-}', 'IEX_BASE_URL', 'need_cmd curl'):
        if token not in text:
            fail(f"runtime file missing expected token: {token}")

    if 'cloud.iexapis.com|sandbox.iexapis.com' not in text:
        fail("runtime file must enforce trusted IEX hosts")

    if "raw PATH must be a relative API path" not in text:
        fail("runtime file must validate raw PATH input")

    if "warning: using" not in text and "warn " not in text:
        fail("runtime file must emit visible warnings for explicit base URL overrides")


def validate_docs() -> None:
    required_markers = [
        "skills.entries.iex-cloud.apiKey",
        "openclaw secrets configure",
        "IEX_TOKEN",
        "IEX_CLOUD_TOKEN",
        "IEX_BASE_URL",
    ]
    for path in README_FILES:
        text = load_text(path)
        for marker in required_markers:
            if marker not in text:
                fail(f"{path} is missing required marker: {marker}")


def validate_trusted_hosts_docs() -> None:
    docs_text = "\n".join(load_text(path) for path in README_FILES)
    for host in EXPECTED_TRUSTED_HOSTS:
        if host not in docs_text and host not in load_text(RUNTIME_FILE):
            fail(f"trusted host {host} must appear in docs or runtime")


def main() -> None:
    metadata = load_metadata()
    frontmatter = load_skill_frontmatter()
    runtime_text = load_text(RUNTIME_FILE)

    validate_metadata(metadata)
    validate_skill_frontmatter(frontmatter, metadata)
    validate_runtime(runtime_text)
    validate_docs()
    validate_trusted_hosts_docs()

    print("metadata, docs, and runtime contract are aligned")


if __name__ == "__main__":
    main()
