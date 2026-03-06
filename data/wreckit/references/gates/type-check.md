# Gate: Type Check

**Question:** Does it compile?

## Process

Run `scripts/detect-stack.sh` to auto-detect language, then execute:

| Language | Command |
|----------|---------|
| TypeScript | `tsc --noEmit` |
| Python | `mypy --strict` (or `pyright`) |
| Rust | `cargo check` |
| Go | `go vet ./...` |
| Java/Kotlin | `./gradlew compileJava` or `mvn compile` |
| Swift | `swift build` |
| No type system | Skip gate, note in proof bundle |

## Pass/Fail

- **Pass:** Zero type errors.
- **Fail:** Any type error. No exceptions.
