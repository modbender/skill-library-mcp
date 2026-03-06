"""YAML parsing for PersonaNexus files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from board_skill.types import AgentIdentity

# Maximum file size to read (10 MB) — prevents memory exhaustion from oversized files
MAX_FILE_SIZE = 10_000_000


class ParseError(Exception):
    """Raised when YAML parsing fails."""

    def __init__(self, message: str, source: str | None = None, line: int | None = None):
        self.source = source
        self.line = line
        loc = ""
        if source:
            loc += f" in {source}"
        if line is not None:
            loc += f" at line {line}"
        super().__init__(f"{message}{loc}")


class IdentityParser:
    """Parses YAML identity files into Pydantic models."""

    def parse_yaml(self, content: str, source: str = "<string>") -> dict[str, Any]:
        """Parse raw YAML string into a dictionary."""
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as exc:
            line = None
            if hasattr(exc, "problem_mark") and exc.problem_mark is not None:
                line = exc.problem_mark.line + 1
            raise ParseError(str(exc), source=source, line=line) from exc

        if not isinstance(data, dict):
            raise ParseError("Expected a YAML mapping at the top level", source=source)

        return data

    def parse_file(self, path: str | Path) -> dict[str, Any]:
        """Load and parse a YAML file into a dictionary."""
        path = Path(path)
        if not path.exists():
            raise ParseError(f"File not found: {path}")
        if not path.is_file():
            raise ParseError(f"Not a file: {path}")

        file_size = path.stat().st_size
        if file_size > MAX_FILE_SIZE:
            raise ParseError(
                f"File {path} is too large ({file_size:,} bytes, max {MAX_FILE_SIZE:,})"
            )

        content = path.read_text(encoding="utf-8")
        return self.parse_yaml(content, source=str(path))

    def load_identity(self, path: str | Path) -> AgentIdentity:
        """Load a YAML file and construct a validated AgentIdentity model."""
        data = self.parse_file(path)
        return AgentIdentity.model_validate(data)

    def load_identity_from_string(self, content: str, source: str = "<string>") -> AgentIdentity:
        """Parse a YAML string and construct a validated AgentIdentity model."""
        data = self.parse_yaml(content, source=source)
        return AgentIdentity.model_validate(data)


# Module-level convenience functions
_parser = IdentityParser()


def parse_yaml(content: str, source: str = "<string>") -> dict[str, Any]:
    """Parse YAML string into a dictionary."""
    return _parser.parse_yaml(content, source)


def parse_file(path: str | Path) -> dict[str, Any]:
    """Load and parse a YAML file into a dictionary."""
    return _parser.parse_file(path)


def parse_identity_file(path: str | Path, base_dir: str | Path | None = None) -> AgentIdentity:
    """Load a YAML file and return a validated AgentIdentity model."""
    if base_dir:
        path_parts = Path(path).parts
        if ".." in path_parts or str(path).startswith(("/", "\\")):
            raise ParseError(
                f"Invalid path '{path}': must be a relative path without '..' components"
            )
        path = Path(base_dir) / path
    return _parser.load_identity(path)
