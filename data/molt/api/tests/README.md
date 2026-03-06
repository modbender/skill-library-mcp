# Backend Tests

## Setup

Install test dependencies:

```bash
cd backend
uv sync --extra dev
# or
pip install -e ".[dev]"
```

## Running Tests

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit

# Run integration tests only
pytest tests/integration

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/integration/test_agent_routes.py -v
```

## Test Structure

- `tests/conftest.py` - Shared fixtures (test_db, test_client, test_creator, test_agent, test_campaign)
- `tests/unit/` - Unit tests for pure functions (security, utils)
- `tests/integration/` - Integration tests for API routes

## Fixtures

- `test_db` - In-memory SQLite database session (isolated per test)
- `test_client` - AsyncClient for making API requests
- `test_creator` - Sample creator with JWT token
- `test_agent` - Sample agent with API key
- `test_campaign` - Sample campaign

## Bugs Fixed by Tests

1. **Route ordering bug** - `/leaderboard` route was defined after `/{name}`, causing 404s
2. **contact_email bug** - Campaign creation excluded contact_email but DB requires it
