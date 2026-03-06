"""Log and error text parser for OpenClaw diagnostics."""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from .error_extraction_helpers import extract_timestamp, extract_error_code


@dataclass
class ParsedError:
    """Structured parsed error with metadata."""
    raw_text: str
    error_code: str | None
    error_message: str
    source: str  # "log" | "stderr" | "json" | "stacktrace"
    line_number: int | None
    timestamp: str | None
    context_lines: list[str]


ERROR_PATTERNS = [
    r'(?i)(error|fatal|exception|failed|failure):\s*(.+)',
    r'(?i)(\w+Error):\s*(.+)',
    r'(?i)code:\s*([A-Z_]+)',
    r'(?i)HTTP\s+([4-5]\d{2})',
]


class ErrorParser:
    """Parser for extracting errors from logs and text."""

    def parse_log_file(self, path: Path) -> list[ParsedError]:
        """Parse log file for errors."""
        errors = []
        if not path.exists():
            return errors

        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            for i, line in enumerate(lines, start=1):
                error = self._detect_error_line(line, i)
                if error:
                    start = max(0, i - 3)
                    end = min(len(lines), i + 2)
                    error.context_lines = [lines[j].rstrip() for j in range(start, end)]
                    errors.append(error)
        except IOError:
            pass

        return errors

    def parse_text(self, text: str) -> list[ParsedError]:
        """Parse arbitrary text for errors."""
        errors = []
        lines = text.split('\n')

        for i, line in enumerate(lines, start=1):
            error = self._detect_error_line(line, i)
            if error:
                start = max(0, i - 3)
                end = min(len(lines), i + 2)
                error.context_lines = lines[start:end]
                errors.append(error)

        return errors

    def parse_json_error(self, text: str) -> ParsedError | None:
        """Parse OpenClaw JSON error format.

        Expected: {"code": "ERROR_CODE", "message": "...", "details": {...}}
        """
        try:
            data = json.loads(text)
            if isinstance(data, dict) and "code" in data and "message" in data:
                return ParsedError(
                    raw_text=text,
                    error_code=data.get("code"),
                    error_message=data.get("message", ""),
                    source="json",
                    line_number=None,
                    timestamp=data.get("timestamp"),
                    context_lines=[text]
                )
        except (json.JSONDecodeError, ValueError):
            pass
        return None

    def _detect_error_line(self, line: str, line_num: int) -> ParsedError | None:
        """Detect if line contains error using regex patterns."""
        line_stripped = line.strip()
        if not line_stripped:
            return None

        timestamp = extract_timestamp(line)

        for pattern in ERROR_PATTERNS:
            match = re.search(pattern, line)
            if match:
                error_code = extract_error_code(line)
                message = match.group(2) if len(match.groups()) >= 2 else match.group(0)

                return ParsedError(
                    raw_text=line_stripped,
                    error_code=error_code,
                    error_message=message.strip(),
                    source="log",
                    line_number=line_num,
                    timestamp=timestamp,
                    context_lines=[]
                )

        error_code = extract_error_code(line)
        if error_code:
            return ParsedError(
                raw_text=line_stripped,
                error_code=error_code,
                error_message=line_stripped,
                source="log",
                line_number=line_num,
                timestamp=timestamp,
                context_lines=[]
            )

        return None

    def parse_stdin(self) -> list[ParsedError]:
        """Parse errors from stdin."""
        text = sys.stdin.read()
        return self.parse_text(text)
