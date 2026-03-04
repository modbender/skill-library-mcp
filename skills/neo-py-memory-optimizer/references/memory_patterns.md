# Python Memory Usage Patterns

Reference of common memory-intensive patterns detected by py-memory-optimizer.

## 1. Unclosed File Handles (`unclosed_file`)

**Pattern:** Calling `open()` without a `with` statement.

```python
# Bad
f = open('data.txt')
data = f.read()
# f.close() may never be called if an exception occurs

# Good
with open('data.txt') as f:
    data = f.read()
```

**Risk:** File descriptors are a limited OS resource. Leaked handles accumulate
until the garbage collector finalizes them (non-deterministic) or the process
hits the file descriptor limit.

## 2. Large List Comprehensions (`large_list_comprehension`)

**Pattern:** Building a full list when only iteration is needed.

```python
# Bad – materializes entire list
results = [transform(x) for x in range(1_000_000)]
for r in results:
    process(r)

# Good – lazy evaluation
results = (transform(x) for x in range(1_000_000))
for r in results:
    process(r)
```

**Impact:** A list of 1M integers uses ~8 MB (64-bit pointers) plus object
overhead. A generator uses constant memory.

## 3. String Concatenation in Loops (`string_concat_in_loop`)

**Pattern:** Using `+=` to build strings inside a loop.

```python
# Bad – O(n^2) memory allocations
result = ""
for item in items:
    result += str(item)

# Good – O(n) with join
result = "".join(str(item) for item in items)
```

**Impact:** Each `+=` allocates a new string object and copies all previous
characters. For n iterations the total memory copied is O(n^2).

## 4. Mutable Default Arguments (`mutable_default_arg`)

**Pattern:** Using `[]`, `{}`, or `set()` as default parameter values.

```python
# Bad – list is shared across calls
def add_item(item, items=[]):
    items.append(item)
    return items

# Good
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

**Impact:** The default object persists for the lifetime of the function object.
Repeated calls accumulate data silently.

## 5. Global Container Accumulation (`global_container_append`)

**Pattern:** Appending to a module-level list/set/dict from inside functions.

```python
# Bad
_cache = []

def process(data):
    result = expensive_compute(data)
    _cache.append(result)  # grows forever
    return result
```

**Impact:** The container grows for the entire process lifetime with no bound,
leading to gradual memory exhaustion in long-running services.

## 6. Unnecessary list() Wrapping (`unnecessary_list_call`)

**Pattern:** Wrapping a generator in `list()` when the result is only iterated.

```python
# Potentially wasteful
items = list(x * 2 for x in data)
for item in items:
    use(item)

# Better if only iterated once
items = (x * 2 for x in data)
for item in items:
    use(item)
```

**Impact:** Materializes all items in memory when lazy evaluation would suffice.
