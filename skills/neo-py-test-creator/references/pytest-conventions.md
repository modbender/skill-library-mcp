# pytest Conventions and Best Practices

This reference guide documents the standard pytest patterns and conventions used by the py-test-creator skill when generating test code.

## Table of Contents

- [Test File Organization](#test-file-organization)
- [Test Function Naming](#test-function-naming)
- [Assertions](#assertions)
- [Fixtures](#fixtures)
- [Markers](#markers)
- [Parametrization](#parametrization)
- [Exception Testing](#exception-testing)
- [Coverage](#coverage)

---

## Test File Organization

Test files should follow these conventions:

1. **Naming**: Test files are named `test_<module>.py` where `<module>` is the name of the module being tested. For example, tests for `utils.py` are in `test_utils.py`.

2. **Location**: Test files can be placed alongside the code or in a separate `tests/` directory. The py-test-creator skill places generated tests in the same directory as the source file by default.

3. **Imports**: Test files should import the module under test and pytest. Use explicit imports:
   ```python
   import pytest
   from mymodule import myfunction
   ```

4. **Structure**: A test file contains:
   - Module docstring (auto-generated)
   - Imports
   - Test functions (and optionally fixtures)
   - No global code execution (only definitions)

---

## Test Function Naming

Test functions must be named `test_<description>` so pytest can discover them automatically.

### Patterns

- **Simple functions**: `test_function_name()`
- **Class methods**: `test_classname_methodname()`
- **Edge cases**: `test_function_name_edgecase_condition`
- **Exception cases**: `test_function_name_raises_exception_type`

Examples:
```python
def test_add():
    assert add(1, 2) == 3

def test_user_create_validation_error():
    with pytest.raises(ValidationError):
        User.create(invalid_data)

def test_process_data_with_none_input():
    result = process_data(None)
    assert result is None
```

---

## Assertions

Use plain `assert` statements for test validation. pytest provides detailed introspection on assertion failures.

### Basic Assertions

```python
def test_add():
    result = add(2, 3)
    assert result == 5

def test_greater_than():
    assert 10 > 5

def test_contains():
    items = [1, 2, 3]
    assert 2 in items
```

### Assertions with Messages

Include a message to make failures clearer:

```python
def test_divide():
    result = divide(10, 2)
    assert result == 5, "Divide failed: expected 5"
```

### Multiple Assertions

It's acceptable to have multiple assertions in a test function when testing related aspects:

```python
def test_user_properties():
    user = User("Alice", 30)
    assert user.name == "Alice"
    assert user.age == 30
    assert user.is_adult is True
```

---

## Fixtures

Fixtures provide reusable test data and setup/teardown logic.

### Simple Fixture

```python
@pytest.fixture
def sample_user():
    return User(name="Test", age=25)

def test_user_greeting(sample_user):
    assert sample_user.greet() == "Hello, Test!"
```

### Fixture with Scope

Fixtures can have different scopes (`function`, `class`, `module`, `session`):

```python
@pytest.fixture(scope="module")
def database_connection():
    conn = connect_db()
    yield conn
    conn.close()
```

### Parametrized Fixtures

Use `params` to run a fixture with multiple values:

```python
@pytest.fixture(params=[1, 2, 3])
def number(request):
    return request.param

def test_double(number):
    assert double(number) == number * 2
```

---

## Markers

Markers categorize tests and modify their behavior.

### Built-in Markers

- `@pytest.mark.skip`: Skip this test
- `@pytest.mark.skipif(condition)`: Skip conditionally
- `@pytest.mark.xfail`: Expected to fail
- `@pytest.mark.parametrize`: Parametrize tests (see below)

### Custom Markers

Register custom markers in `pytest.ini`:

```ini
[pytest]
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: integration tests
    unit: unit tests (default)
```

Use custom markers:

```python
@pytest.mark.integration
def test_api_endpoint():
    response = requests.get("/api/health")
    assert response.status_code == 200

@pytest.mark.slow
def test_large_dataset_processing():
    # This test takes several seconds
    pass
```

---

## Parametrization

Parametrization runs the same test with multiple input values.

### Basic Parametrization

```python
@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
])
def test_add(a, b, expected):
    assert add(a, b) == expected
```

### Multiple Parameters

```python
@pytest.mark.parametrize("x", [1, 2])
@pytest.mark.parametrize("y", [10, 20])
def test_multiply(x, y):
    assert multiply(x, y) == x * y
# This creates 4 test cases: (1,10), (1,20), (2,10), (2,20)
```

### Parametrization with Indirect

Use `indirect=True` to pass parameters to fixtures:

```python
@pytest.mark.parametrize("user_role", ["admin", "user", "guest"], indirect=True)
def test_access_control(user_role):
    assert user_role.permissions is not None
```

---

## Exception Testing

Test that code raises expected exceptions.

### `pytest.raises()`

```python
def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def test_invalid_type():
    with pytest.raises(TypeError) as exc_info:
        add("a", 2)
    assert "unsupported operand type" in str(exc_info.value)
```

### `pytest.raises()` with Match

Match exception message using regex:

```python
def test_invalid_age():
    with pytest.raises(ValueError, match="Age must be positive"):
        User(age=-5)
```

---

## Coverage

Add coverage hints to guide coverage reporting.

### Excluding Lines

Use `# pragma: no cover` to exclude lines from coverage:

```python
def __repr__(self):
    return f"<Node {self.id}>"  # pragma: no cover

if TYPE_CHECKING:  # pragma: no cover
    from .models import Database  # type-only import
```

### Marking for Coverage

Exclude entire branches:

```python
if feature_flag:  # pragma: no cover
    # New code path not yet in production
    return new_behavior()
else:
    return old_behavior()
```

---

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest Fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [pytest Markers](https://docs.pytest.org/en/stable/how-to/mark.html)
- [pytest Parametrization](https://docs.pytest.org/en/stable/how-to/parametrize.html)
