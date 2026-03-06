# Frontend Tests

## Setup

Install dependencies:

```bash
cd frontend
bun install
```

## Running Tests

```bash
# Run all tests
bun run test

# Run in watch mode
bun run test:watch

# Run with coverage
bun run test:coverage
```

## Test Structure

- `tests/setup.ts` - Test configuration and mocks
- `tests/unit/` - Unit tests for utilities and API client
- `tests/components/` - Component tests (to be added)

## Test Files

- `utils.test.ts` - Tests for utility functions (formatCurrency, validateEthAddress, etc.)
- `api.test.ts` - Tests for API client (request methods, error handling, auth headers)

## Mocks

- `navigator.clipboard` - Mocked for clipboard operations
- `window.matchMedia` - Mocked for responsive tests
- `fetch` - Mocked in API tests
