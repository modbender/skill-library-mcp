# Testing Traps

- `jest.mock()` hoisted — runs before imports, can't use variables from file
- Mock not cleaned between tests — `jest.clearAllMocks()` in `beforeEach`
- `async` test without `await` — test passes before promise resolves/rejects
- `toEqual` vs `toBe` — `toBe` uses `===`, fails on equal objects
- Timer mocks — `jest.useFakeTimers()` needed, real timers make tests flaky
- Snapshot too big — small changes break test, snapshot should be focused
- `done()` callback timeout — forgetting to call `done` hangs test
