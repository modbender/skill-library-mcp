"""
Sample Python file with various memory-intensive patterns.
Used for testing and demonstrating py-memory-optimizer.
"""

# --- 1. Unclosed file handle ---
def read_data():
    f = open('data.txt', 'r')
    data = f.read()
    return data


# --- 2. Large list comprehension with known range ---
def generate_squares():
    squares = [x ** 2 for x in range(100000)]
    return sum(squares)


# --- 3. String concatenation in a loop ---
def build_report(items):
    report = ""
    for item in items:
        report += f"Item: {item}\n"
    return report


# --- 4. Mutable default argument ---
def collect(value, accumulator=[]):
    accumulator.append(value)
    return accumulator


# --- 5. Global container accumulation ---
_log_entries = []

def log_event(event):
    _log_entries.append(event)


# --- 6. Unnecessary list() wrapping a generator ---
def double_values(data):
    return list(x * 2 for x in data)


# --- Good practices (should produce fewer / no issues) ---
def read_data_good():
    with open('data.txt', 'r') as f:
        return f.read()


def generate_squares_good():
    return sum(x ** 2 for x in range(100000))


def build_report_good(items):
    parts = []
    for item in items:
        parts.append(f"Item: {item}")
    return "\n".join(parts)


def collect_good(value, accumulator=None):
    if accumulator is None:
        accumulator = []
    accumulator.append(value)
    return accumulator
