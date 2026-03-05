"""
Sample Python functions for testing py-test-creator.

This module contains a variety of function signatures to demonstrate
the test generation capabilities, including:
- Simple functions with various return types
- Functions with complex type hints
- Functions with default arguments
- Functions with *args and **kwargs
- Class methods (both instance and class methods)
- Static methods
- Async functions (for completeness)
"""

from typing import List, Dict, Tuple, Optional, Union, Any, Callable


# ===== Simple Functions =====

def add(a: int, b: int) -> int:
    """Add two integers and return their sum."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Subtract b from a and return the result."""
    return a - b


def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b


def divide(a: float, b: float) -> float:
    """Divide a by b. Raises ZeroDivisionError if b is zero."""
    if b == 0:
        raise ZeroDivisionError("division by zero")
    return a / b


def greet(name: str) -> str:
    """Return a greeting message for the given name."""
    return f"Hello, {name}!"


def is_even(n: int) -> bool:
    """Check if an integer is even."""
    return n % 2 == 0


# ===== Functions with Default Arguments =====

def power(base: float, exponent: int = 2) -> float:
    """Raise base to the power of exponent (default 2)."""
    return base ** exponent


def create_message(
    recipient: str,
    subject: str = "No Subject",
    body: str = "",
    priority: int = 0
) -> str:
    """Create an email message string."""
    return f"To: {recipient}\nSubject: {subject}\n\n{body}"


def format_name(
    first: str,
    last: str,
    middle: Optional[str] = None,
    title: str = "Mr./Ms."
) -> str:
    """Format a full name with optional middle name."""
    if middle:
        return f"{title} {first} {middle} {last}"
    return f"{title} {first} {last}"


# ===== Functions with Complex Type Hints =====

def process_numbers(
    numbers: List[int],
    multiplier: int = 1,
    filter_fn: Optional[Callable[[int], bool]] = None
) -> List[int]:
    """Process a list of numbers by multiplying and optionally filtering."""
    result = [n * multiplier for n in numbers]
    if filter_fn:
        result = [n for n in result if filter_fn(n)]
    return result


def merge_dicts(
    dict1: Dict[str, Any],
    dict2: Dict[str, Any],
    overwrite: bool = True
) -> Dict[str, Any]:
    """Merge two dictionaries. If overwrite is False, dict1 values take precedence."""
    if overwrite:
        return {**dict1, **dict2}
    else:
        return {**dict2, **dict1}


def calculate_stats(
    values: List[float]
) -> Dict[str, Optional[float]]:
    """Calculate statistics for a list of numbers."""
    if not values:
        return {"mean": None, "min": None, "max": None, "sum": None}

    return {
        "mean": sum(values) / len(values),
        "min": min(values),
        "max": max(values),
        "sum": sum(values)
    }


# ===== Functions with *args and **kwargs =====

def concat_strings(*strings: str) -> str:
    """Concatenate any number of strings."""
    return "".join(strings)


def sum_all(*numbers: Union[int, float]) -> Union[int, float]:
    """Sum all provided numbers."""
    return sum(numbers)


def create_user(
    username: str,
    email: str,
    *,
    age: Optional[int] = None,
    active: bool = True,
    **metadata
) -> Dict[str, Any]:
    """Create a user dictionary with required fields and optional metadata."""
    user = {
        "username": username,
        "email": email,
        "active": active
    }
    if age is not None:
        user["age"] = age
    user.update(metadata)
    return user


def call_with_context(
    func: Callable[..., Any],
    *args: Any,
    context: Optional[Dict[str, Any]] = None,
    **kwargs: Any
) -> Any:
    """Call a function with additional context."""
    if context:
        # In real use, might modify args/kwargs based on context
        pass
    return func(*args, **kwargs)


# ===== Functions with Union and Optional types =====

def parse_int(value: Union[str, int]) -> int:
    """Parse an integer from string or return integer."""
    if isinstance(value, str):
        return int(value.strip())
    return value


def safe_divide(
    a: float,
    b: float,
    default: Optional[float] = None
) -> Optional[float]:
    """Divide a by b, returning default if b is zero."""
    try:
        return a / b
    except ZeroDivisionError:
        return default


def first_or_none(
    items: List[Any],
    predicate: Optional[Callable[[Any], bool]] = None
) -> Optional[Any]:
    """Return first item matching predicate, or first item if no predicate, or None."""
    if not items:
        return None

    if predicate:
        for item in items:
            if predicate(item):
                return item
        return None

    return items[0]


# ===== Functions returning Tuples =====

def min_max(values: List[Union[int, float]]) -> Tuple[Union[int, float], Union[int, float]]:
    """Return minimum and maximum of a list."""
    if not values:
        raise ValueError("Cannot compute min/max of empty list")
    return min(values), max(values)


def partition(
    items: List[Any],
    predicate: Callable[[Any], bool]
) -> Tuple[List[Any], List[Any]]:
    """Partition items into two lists based on predicate."""
    true_items = []
    false_items = []
    for item in items:
        if predicate(item):
            true_items.append(item)
        else:
            false_items.append(item)
    return true_items, false_items


# ===== Class Methods =====

class Calculator:
    """A simple calculator class for demonstration."""

    def __init__(self, initial: float = 0):
        """Initialize calculator with starting value."""
        self.value = initial

    def add(self, amount: float) -> float:
        """Add amount to current value."""
        self.value += amount
        return self.value

    def subtract(self, amount: float) -> float:
        """Subtract amount from current value."""
        self.value -= amount
        return self.value

    def reset(self) -> None:
        """Reset value to zero."""
        self.value = 0

    @classmethod
    def from_string(cls, s: str) -> "Calculator":
        """Create calculator from a string representation."""
        return cls(initial=float(s))

    @staticmethod
    def is_valid_number(s: str) -> bool:
        """Check if string represents a valid number."""
        try:
            float(s)
            return True
        except ValueError:
            return False


class DataProcessor:
    """Process data collections."""

    def __init__(self, data: List[Any]):
        self.data = data

    def filter(self, predicate: Callable[[Any], bool]) -> List[Any]:
        """Filter data using predicate."""
        return [item for item in self.data if predicate(item)]

    def map(self, func: Callable[[Any], Any]) -> List[Any]:
        """Apply function to all data items."""
        return [func(item) for item in self.data]

    def reduce(self, func: Callable[[Any, Any], Any], initial: Any) -> Any:
        """Reduce data using function and initial value."""
        result = initial
        for item in self.data:
            result = func(result, item)
        return result


# ===== Async Function (for completeness) =====

async def fetch_data(url: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
    """Async fetch data from URL (simulated)."""
    # This is a stub - real implementation would use aiohttp
    return {"url": url, "timeout": timeout}


async def process_items(
    items: List[Any],
    processor: Callable[[Any], Any]
) -> List[Any]:
    """Process items concurrently (simulated)."""
    results = []
    for item in items:
        result = await processor(item)
        results.append(result)
    return results


# ===== Helper Functions Used in Tests =====

def is_positive(n: Union[int, float]) -> bool:
    """Check if number is positive."""
    return n > 0


def is_empty(collection: Any) -> bool:
    """Check if collection is empty."""
    if collection is None:
        return True
    if isinstance(collection, (str, list, dict, set, tuple)):
        return len(collection) == 0
    return False


def fibonacci(n: int) -> int:
    """Calculate nth Fibonacci number (naive recursive)."""
    if n <= 0:
        raise ValueError("n must be positive")
    if n == 1 or n == 2:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)
