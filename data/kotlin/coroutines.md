# Coroutines & Flows

## Basics

- `suspend` functions only callable from coroutines — don't block, use `withContext(Dispatchers.IO)` for IO
- `launch` for fire-and-forget — `async/await` when you need the result
- `viewModelScope` auto-cancels on ViewModel clear — don't use `GlobalScope` in Android

## Structured Concurrency

- Child coroutine failure cancels parent — use `supervisorScope` to isolate failures
- Always use scoped coroutines — GlobalScope leaks and never cancels
- `coroutineScope` suspends until all children complete — use for parallel decomposition

## Flows

- `flow` for reactive streams — collect in lifecycle-aware scope with `repeatOnLifecycle`
- Use `stateIn` or `shareIn` to share flows — avoid multiple upstream collections
- `flowOn` changes upstream context only — downstream stays on collector's dispatcher

## StateFlow & SharedFlow

- `StateFlow` requires initial value, never completes — use for UI state
- `SharedFlow` for events, no initial value — replay 0 means late collectors miss events
- Don't use `SharedFlow(replay=1)` as poor man's StateFlow — use StateFlow for state
- `MutableStateFlow.update {}` is atomic — use instead of `.value = .value + 1`

## Flow Operators

- `conflate` drops intermediate values under backpressure — UI only needs latest
- `buffer` decouples producer/consumer speed — prevents slow collector blocking emitter
- `distinctUntilChanged` skips duplicates — useful for StateFlow-like behavior
- `catch` only catches upstream exceptions — doesn't affect downstream

## Testing Coroutines

- `runTest` automatically skips delays — virtual time, tests run fast
- `StandardTestDispatcher` for manual time control — use `advanceTimeBy()`
- `UnconfinedTestDispatcher` runs coroutines eagerly — no need to advance
- `advanceUntilIdle()` processes all pending coroutines — call before assertions
- Inject dispatchers, don't hardcode `Dispatchers.IO` — test with `TestDispatcher`
