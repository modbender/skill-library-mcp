# Android-Specific Kotlin

## Lifecycle-Aware Coroutines

- `repeatOnLifecycle(STARTED)` restarts collection when lifecycle resumes — stops on STOPPED
- Don't collect flows in `onCreate` without lifecycle awareness — leaks if Activity destroyed
- `flowWithLifecycle` for single flow observation — extension on Flow, less boilerplate
- `Lifecycle.launchWhenStarted` is deprecated — use `repeatOnLifecycle` instead
- `lifecycleScope` tied to Activity/Fragment — auto-cancels on destroy

## Compose State

- `remember` survives recomposition, not configuration change — use `rememberSaveable` for rotation
- `rememberSaveable` serializes state — only works with `Saver` or Parcelable types
- `derivedStateOf` for computed state — recalculates only when dependencies change
- Snapshot system tracks reads during composition — triggers recomposition on change
- `mutableStateListOf` not `mutableListOf` wrapped in `mutableStateOf` — won't track internal changes

## Compose Performance

- `key()` helps identify items in lists — prevents unnecessary recomposition
- Lambda stability matters — use `remember` for lambdas with captures
- `@Stable` and `@Immutable` annotations help compiler skip recomposition
- Avoid reading state in composition scope if only needed in callbacks — defer reads

## ViewModel Integration

- `collectAsStateWithLifecycle` is the gold standard — lifecycle-aware + Compose state
- Expose `StateFlow` from ViewModel, not `LiveData` — better for Compose
- `savedStateHandle` for process death survival — inject into ViewModel
- One-shot events: use `Channel` or `SharedFlow(replay=0)` — not StateFlow
