"""
Sample Python file demonstrating good memory practices.
The analyzer should find minimal issues here.
"""

from contextlib import contextmanager


def process_file(path: str) -> str:
    """Read a file using a context manager."""
    with open(path, 'r') as f:
        return f.read()


def sum_generator(n: int) -> int:
    """Use a generator expression instead of list comprehension."""
    return sum(x * x for x in range(n))


def build_string(items: list) -> str:
    """Build string efficiently with join."""
    return ", ".join(str(item) for item in items)


def safe_defaults(data=None):
    """Use None default instead of mutable."""
    if data is None:
        data = {}
    data["processed"] = True
    return data
