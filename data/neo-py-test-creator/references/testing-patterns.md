# Testing Patterns for pytest

A comprehensive guide to common testing patterns when generating pytest-compatible unit tests. This reference covers idioms, best practices, and advanced features to make your tests more robust, maintainable, and expressive.

## 1. Fixtures

Fixtures provide reusable test context and resources. They are the cornerstone of composable test suites.

### Basic Fixture

```python
import pytest

@pytest.fixture
def sample_data():
    """Provides a sample data dictionary for tests."""
    return {"name": "test", "value": 42}
```

**Usage:**
```python
def test_with_fixture(sample_data):
    assert sample_data["value"] == 42
```

### Fixture Scopes

Control fixture lifecycle with scopes: `function` (default), `class`, `module`, `package`, `session`.

```python
@pytest.fixture(scope="module")
def database_connection():
    conn = connect_to_db()
    yield conn
    conn.close()  # Executed after all tests in the module
```

### Fixture with teardown (yield)

```python
@pytest.fixture
def temp_file():
    fd, path = tempfile.mkstemp()
    yield path
    os.close(fd)
    os.remove(path)
```

### Parametrized Fixtures

Combine fixtures with `pytest.mark.parametrize` or use `pytest.fixture(params=...)`.

```python
@pytest.fixture(params=["json", "xml", "yaml"])
def data_format(request):
    return request.param

def test_format_handling(data_format):
    assert data_format in ["json", "xml", "yaml"]
```

## 2. Parametrization

Run the same test logic with multiple input sets using `@pytest.mark.parametrize`.

### Simple Parametrization

```python
import pytest

@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
])
def test_addition(a, b, expected):
    assert add(a, b) == expected
```

### Multiple Parameters

```python
@pytest.mark.parametrize("input_str,expected_len", [
    ("hello", 5),
    ("", 0),
    ("a", 1),
])
@pytest.mark.parametrize(" multiplier", [1, 2, 3])
def test_string_multiply(input_str, multiplier, expected_len):
    result = input_str * multiplier
    assert len(result) == expected_len * multiplier
```

### Indirect Parametrization

When parameters are used to instantiate fixtures, use `indirect=True`.

```python
@pytest.fixture
def config(request):
    return {"mode": request.param}

@pytest.mark.parametrize("config", ["debug", "release"], indirect=True)
def test_config_mode(config):
    assert config["mode"] in ["debug", "release"]
```

### Parametrize with IDs

Improve readability of test IDs in verbose output.

```python
@pytest.mark.parametrize("n,expected", [
    (1, 1),
    (2, 1),
    (3, 2),
], ids=["first", "second", "third"])
def test_fibonacci(n, expected):
    assert fibonacci(n) == expected
```

## 3. Marks

Use marks to categorize, skip, or xfail tests.

### Skip

```python
@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    pass
```

Or conditionally:
```python
import sys

@pytest.mark.skipif(sys.version_info < (3, 9), reason="Requires Python 3.9+")
def test_new_feature():
    pass
```

### Expected Fail (xfail)

```python
@pytest.mark.xfail(reason="Known bug in parser")
def test_known_broken():
    assert parse("invalid") is True
```

If the test unexpectedly passes, it will be reported as XPASS.

### Custom Marks

Register custom marks in `pytest.ini` to avoid warnings:

```ini
[pytest]
markers =
    integration: integration tests
    slow: slow running tests
```

Then use:
```python
@pytest.mark.integration
def test_api_integration():
    pass
```

Run with `pytest -m "integration"`.

## 4. Assertions

pytest provides powerful assertions with introspection.

### Assert Rewriting

```python
def test_assertion_introspection():
    data = {"a": 1, "b": 2}
    assert data["a"] + data["b"] == 3
    # On failure, shows values of subexpressions
```

### Approximate Comparisons for Floats

```python
import pytest

def test_float_division():
    result = 1 / 3
    assert result == pytest.approx(0.33333, rel=1e-4)
```

### Context Managers

#### `pytest.raises` for exceptions

```python
def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def test_divide_by_zero_message():
    with pytest.raises(ZeroDivisionError, match="division by zero"):
        divide(10, 0)
```

#### `pytest.warns` for warnings

```python
def test_deprecation():
    with pytest.warns(DeprecationWarning):
        use_old_function()
```

#### `pytest.deprecated_call` (newer)

```python
def test_deprecated():
    with pytest.deprecated_call():
        deprecated_api()
```

### List/Dict Comparisons

```python
def test_list_ignoring_order():
    assert [1, 2, 3] == [3, 2, 1]  # fails due to order
    assert set([1,2,3]) == set([3,2,1])  # passes

def test_dict_subset():
    data = {"name": "Alice", "age": 30, "city": "Paris"}
    assert {"name": "Alice", "age": 30} <= data  # subset check
```

## 5. Test Discovery & Structure

### Naming Conventions

- Test files: `test_*.py` or `*_test.py`
- Test functions: `test_*()`
- Test classes: `Test*` (no `__init__`)

### Classes as test containers

```python
class TestCalculator:
    def test_add(self):
        assert add(1, 1) == 2

    def test_subtract(self):
        assert subtract(2, 1) == 1

    @pytest.fixture(autouse=True)
    def setup(self):
        self.calc = Calculator()
```

### Module-level setup/teardown

```python
def setup_module(module):
    # Runs once per module
    pass

def teardown_module(module):
    # Cleanup after module
    pass
```

## 6. Capturing Output

### `capsys` and `capfd`

```python
def test_stdout(capsys):
    print("hello")
    captured = capsys.readouterr()
    assert captured.out == "hello\n"

def test_stderr(capsys):
    sys.stderr.write("error\n")
    captured = capsys.readouterr()
    assert captured.err == "error\n"
```

### `caplog` for logging capture

```python
def test_logging(caplog):
    logger = logging.getLogger("myapp")
    logger.info("test message")
    assert "test message" in caplog.text
```

## 7. Temporary Files and Directories

`tmp_path` (pathlib.Path) and `tmpdir` (py.path.local) fixtures.

```python
def test_write_file(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("content")
    assert file.read_text() == "content"

def test_temp_dir(tmpdir):
    sub = tmpdir.mkdir("sub")
    file = sub.join("data.json")
    file.write('{"key": "value"}')
    import json
    data = json.loads(file.read())
    assert data["key"] == "value"
```

## 8. Monkeypatching

Replace objects during tests without permanent changes.

```python
def test_api_call(monkeypatch):
    def mock_get(*args, **kwargs):
        class Response:
            status_code = 200
            def json(self):
                return {"status": "ok"}
        return Response()

    monkeypatch.setattr(requests, "get", mock_get)
    result = call_api()
    assert result == {"status": "ok"}
```

## 9. Mocking (unittest.mock)

pytest works seamlessly with `unittest.mock`.

```python
from unittest.mock import patch, MagicMock

def test_with_mock():
    with patch("module.dependency") as mock_dep:
        mock_dep.return_value = "mocked"
        result = function_under_test()
        assert result == "expected"
        mock_dep.assert_called_once_with("expected_arg")
```

### Common patterns

- `patch()`: decorator or context manager
- `MagicMock()`: generic mock with magic methods
- `Mock(spec=RealClass)`: restrict to real class interface
- `return_value` vs `side_effect`

## 10. Test Organization Patterns

### Arrange-Act-Assert (AAA)

```python
def test_sort_list():
    # Arrange
    data = [3, 1, 2]
    # Act
    result = sorted(data)
    # Assert
    assert result == [1, 2, 3]
```

### Given-When-Then (BDD style)

```python
def test_user_creation():
    given_user_exists_in_database()
    when_user_is_updated()
    then_database_reflects_changes()
```

### Table-Driven Tests

Use parametrization to express multiple scenarios clearly.

```python
@pytest.mark.parametrize("input,expected", [
    ("", 0),
    ("a", 1),
    ("abc", 3),
])
def test_string_length(input, expected):
    assert len(input) == expected
```

## 11. Best Practices for Generated Tests

When automatically generating test code, adhere to these principles:

**Isolation:** Each test must be independent; avoid shared state across tests unless using fixtures with appropriate scopes.

**Idempotency:** Tests should produce the same result regardless of execution order.

**Clear Assertions:** Prefer specific assertions (`assert result == expected`) over generic ones (`assert result`). Use `pytest.approx` for floats.

**Descriptive Names:** Test function names should convey scenario, e.g., `test_add_negative_numbers_returns_negative`.

**Docstrings:** Include a brief description of what the test verifies; often derived from the function's docstring.

**Edge Coverage:** Include tests for boundary conditions, `None` values, empty collections, and invalid inputs that raise exceptions.

**Minimalism:** Only assert what is necessary. Avoid testing implementation details unless required.

**Consistency:** Follow the project's style guide (e.g., PEP8, Black formatting). Include imports (`import pytest`) and avoid unnecessary boilerplate.

## 12. Common Patterns for Auto-Generated Tests

Based on function signature and type hints, apply these patterns:

| Parameter Type | Example Values | Assertion Pattern |
|----------------|----------------|-------------------|
| `int` / `float` | `0`, `-1`, `1`, large values | equality, range checks |
| `str` | `""`, `"a"`, `"test"` | length, content |
| `bool` | `True`, `False` | direct equality |
| `List[T]` | `[]`, `[0]`, `[0,1]` | length, membership |
| `Dict[K,V]` | `{}`, `{"key": "value"}` | containment |
| `Optional[T]` | `None`, valid value | `is None` / `is not None` |
| `Union[A,B]` | value of each type | isinstance checks |
| `Callable` | `lambda x: x`, real function | `callable(result)` |

For functions that raise exceptions (indicated by docstring or known error conditions):

```python
def test_raises_<condition>(...):
    with pytest.raises(ExpectedException):
        func(...)
```

## 13. Configuration Hints

Common `pytest.ini` settings useful for generated test suites:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --strict-markers
markers =
    unit: unit tests
    integration: integration tests
```

Generated tests should respect project configuration. Avoid hardcoding paths or assumptions.

## 14. Further Resources

- [pytest Documentation](https://docs.pytest.org/en/stable/)
- [pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [pytest Parametrization](https://docs.pytest.org/en/stable/parametrize.html)
- [Python Testing with pytest](https://pragprog.com/titles/bopytest2/python-testing-with-pytest-second-edition/) (book)
