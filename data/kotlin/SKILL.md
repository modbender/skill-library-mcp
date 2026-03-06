---
name: Kotlin
slug: kotlin
version: 1.0.1
description: Build robust Android and multiplatform apps with Kotlin idioms, coroutines, and null safety.
metadata: {"clawdbot":{"emoji":"🟠","requires":{"bins":["kotlin"]},"os":["linux","darwin","win32"]}}
---

## Quick Reference

| Topic | File |
|-------|------|
| Null safety operators and patterns | `nullsafety.md` |
| Coroutines, flows, structured concurrency | `coroutines.md` |
| Collections, sequences, data classes | `collections.md` |
| Scope functions, extensions, sealed classes | `idioms.md` |
| Java interop and common Kotlin mistakes | `interop.md` |
| Android lifecycle, Compose state | `android.md` |
| Delegation, inline, reified, multiplatform | `advanced.md` |

## Critical Rules

### Null Safety
- `!!` asserts non-null — crashes on null, use only when you've already checked
- Platform types from Java are risky — add null checks or use `@Nullable`/`@NonNull` annotations
- Elvis with `return`/`throw` for early exit — `val name = user?.name ?: return`

### Coroutines
- `viewModelScope` auto-cancels on ViewModel clear — don't use `GlobalScope` in Android
- Structured concurrency: child coroutine failure cancels parent — use `supervisorScope` to isolate
- `StateFlow` needs initial value and never completes — `SharedFlow` for one-shot events
- Inject dispatchers for testability — don't hardcode `Dispatchers.IO`

### Collections & Data Classes
- `first()` throws on empty — use `firstOrNull()` for safe access
- Only constructor properties in `equals`/`hashCode` — body properties ignored
- `mutableStateListOf` for Compose — wrapping `mutableListOf` in state won't track changes

### Scope Functions & Extensions
- Don't nest scope functions — readability drops fast, extract to named functions
- Extensions are resolved statically — not polymorphic, receiver type matters at compile time

### Android/Compose
- `repeatOnLifecycle(STARTED)` for flow collection — `launchWhenStarted` is deprecated
- `remember` survives recomposition only — use `rememberSaveable` for config changes
- `collectAsStateWithLifecycle` is the gold standard — lifecycle-aware + Compose state

### Java Interop
- `==` is structural equality in Kotlin — `===` for reference, opposite of Java
- SAM conversion only for Java interfaces — Kotlin interfaces need explicit `fun interface`
- `@JvmStatic`, `@JvmOverloads`, `@JvmField` for Java-friendly APIs
