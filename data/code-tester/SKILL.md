---
name: code-tester
description: Build, run, and test code projects for Rust, Go, and Java. Automatically detect project type, run unit tests if available, and report build status. Use after code changes to verify that project builds successfully, unit tests pass if they exist, and application runs without errors. Communicate results back to the requesting agent for fixing and re-testing.
metadata: {"clawdbot":{"command":"test_repo"}}
---

# Code Tester

Test code projects to verify builds and tests pass.

## Workflow

When asked to test changes:

1. **Detect project type** in specified directory:
   - Rust: `Cargo.toml` + `src/` directory
   - Go: `go.mod`, `go.sum`, or `main.go`
   - Java: `pom.xml` or `build.gradle` / `build.gradle.kts`

2. **Run tests** (only if tests exist):
   - Skip if no tests found
   - Run project-specific test commands
   - Capture test results

3. **Build the project**:
   - Run build commands
   - Capture build output and errors

4. **Report results**:
   - Clear summary of what happened
   - Test results (if run)
   - Build status
   - Any errors encountered

## Communication Protocol

When testing for another agent:

**Format your report like:**

```
Testing: <directory>
Project type: <rust|go|java>
Detected tests: <yes|no>

=== Results ===
✓ Tests: <passed/skipped/failed>
✓/✗ Build: <passed/failed>

<Relevant error messages if any>
```

**If everything passes:**
- Report success clearly
- Provide next steps if needed

**If something fails:**
- Report what failed (tests or build)
- Include error logs
- Suggest what to fix

## Running Tests

Execute the test script:

```bash
/root/.openclaw/workspace/skills/code-tester/scripts/test.sh <directory>
```

The script will:
- Auto-detect project type
- Run tests (if available)
- Build the project
- Return exit code 0 on success, 1 on failure

## Testing Strategy

- **Rust**: `cargo test` → `cargo build`
- **Go**: `go test ./...` → `go build`
- **Java Maven**: `mvn test` → `mvn compile`
- **Java Gradle**: `./gradlew test` → `./gradlew build -x test`

Always run from the project directory. The script handles detection automatically.
