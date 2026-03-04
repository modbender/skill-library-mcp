#!/usr/bin/env python3
"""
Generate optimization suggestions for detected memory issues.

Usage:
    from optimizer import generate_suggestion
    suggestion_dict = generate_suggestion(issue)
"""

SUGGESTIONS = {
    "unclosed_file": {
        "suggestion": (
            "Wrap the file operation in a context manager (with statement) "
            "to ensure the file is closed even if an exception occurs."
        ),
        "example_template": "with open({file_arg}) as f:\n    data = f.read()",
        "example_default": "with open('path') as f:\n    data = f.read()",
        "estimated_savings": "Prevents file descriptor leaks and associated memory accumulation.",
    },
    "large_list_comprehension": {
        "suggestion": (
            "Convert the list comprehension to a generator expression "
            "to avoid materializing the entire list in memory."
        ),
        "example_default": "(expr for item in iterable)",
        "savings_by_severity": {
            "low": "~30-50% for small datasets",
            "medium": "~50-70% for medium datasets",
            "high": "~70-90% for large datasets",
        },
    },
    "string_concat_in_loop": {
        "suggestion": (
            "Collect string parts in a list and use ''.join() after the loop. "
            "Each += on a string creates a new object, leading to O(n^2) memory churn."
        ),
        "example_default": "parts = []\nfor item in items:\n    parts.append(str(item))\nresult = ''.join(parts)",
        "estimated_savings": "Reduces temporary string allocations from O(n^2) to O(n).",
    },
    "mutable_default_arg": {
        "suggestion": (
            "Use None as the default and create the mutable object inside the function body. "
            "Mutable defaults are shared across calls and can grow unboundedly."
        ),
        "example_default": "def func(items=None):\n    if items is None:\n        items = []",
        "estimated_savings": "Prevents unexpected data accumulation across function calls.",
    },
    "global_container_append": {
        "suggestion": (
            "Avoid appending to module-level containers from within functions, "
            "as this causes the container to grow for the lifetime of the process. "
            "Consider using local containers, bounded caches, or weak references."
        ),
        "example_default": "# Use a bounded cache or local container instead\nfrom functools import lru_cache",
        "estimated_savings": "Prevents unbounded memory growth over process lifetime.",
    },
    "unnecessary_list_call": {
        "suggestion": (
            "If the result is only iterated once, remove the list() wrapper "
            "and use the generator expression directly to save memory."
        ),
        "example_default": "result = (x for x in iterable)  # instead of list(x for x in iterable)",
        "estimated_savings": "Avoids materializing the full sequence in memory.",
    },
}


def generate_suggestion(issue: dict) -> dict:
    """
    Given a raw issue from the analyzer, produce a suggestion dictionary.

    Returns a dict with keys:
      - suggestion (str): human-readable suggestion text
      - example (str): code example of optimized form
      - estimated_savings (str): memory savings estimate
    """
    issue_type = issue.get("type", "")
    template = SUGGESTIONS.get(issue_type)

    if template is None:
        return {"suggestion": "Review this pattern for potential memory optimization."}

    result = {"suggestion": template["suggestion"]}

    # Build example
    if "example_template" in template:
        file_arg = issue.get("file_arg")
        if file_arg:
            result["example"] = template["example_template"].format(
                file_arg=repr(file_arg)
            )
        else:
            result["example"] = template["example_default"]
    else:
        result["example"] = template["example_default"]

    # Build savings estimate
    if "savings_by_severity" in template:
        severity = issue.get("severity", "medium")
        result["estimated_savings"] = template["savings_by_severity"].get(
            severity, template["savings_by_severity"].get("medium", "Variable")
        )
    elif "estimated_savings" in template:
        result["estimated_savings"] = template["estimated_savings"]

    return result
