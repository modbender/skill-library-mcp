# Testing Traps

- `mock.patch` path — patch where imported, not where defined
- Mock not reset — `mock.reset_mock()` between tests or use `autospec`
- `assert` stripped in `-O` — never use `assert` for validation
- Fixture scope confusion — `function` runs each test, `module` once
- `pytest.raises` without match — catches wrong exception silently
- Async test needs plugin — `pytest-asyncio` + `@pytest.mark.asyncio`
- Mocking `datetime.now()` — mock `datetime` module, not method
