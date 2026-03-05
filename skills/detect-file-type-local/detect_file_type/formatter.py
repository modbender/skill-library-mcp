"""Output formatting for file type detection results."""

from __future__ import annotations

import json
from typing import Any, Dict, List


def result_to_dict(path: str, result: Any) -> Dict[str, Any]:
    """Convert a magika result to a plain dict."""
    output = result.output
    return {
        "path": path,
        "label": output.label,
        "mime_type": output.mime_type,
        "score": round(result.score, 4),
        "group": output.group,
        "description": output.description,
        "is_text": output.is_text,
    }


def format_json(results: List[Dict[str, Any]]) -> str:
    """Format results as JSON. Single result returns an object; multiple returns an array."""
    if len(results) == 1:
        return json.dumps(results[0], indent=2)
    return json.dumps(results, indent=2)


def format_human(results: List[Dict[str, Any]]) -> str:
    """Format results as human-readable lines."""
    lines = []
    for r in results:
        lines.append(
            f"{r['path']}: {r['description']} ({r['mime_type']}) [score: {r['score']:.2f}]"
        )
    return "\n".join(lines)


def format_mime(results: List[Dict[str, Any]]) -> str:
    """Format results as bare MIME types, one per line."""
    return "\n".join(r["mime_type"] for r in results)
