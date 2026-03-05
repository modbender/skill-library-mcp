# ClawBrain Tests

This directory contains comprehensive integration tests for ClawBrain.

## Test Files

| File | Description |
|------|-------------|
| `run_integration_tests.sh` | Main test runner script (Docker-based) |
| `run_local_tests.sh` | Run tests locally without Docker |
| `integration_test.py` | Core integration tests (12 tests) |
| `test_openclaw_container.py` | OpenClaw-specific integration test |
| `test_openclaw_integration.sh` | Real system OpenClaw restart test |
| `Dockerfile.test` | Docker image simulating OpenClaw |

## Running Tests

### Docker-based Integration Tests (Recommended)

Run the full integration test suite in a Docker container that simulates an OpenClaw environment:

```bash
# Run all tests (13 tests total)
./tests/run_integration_tests.sh

# Force rebuild the container
./tests/run_integration_tests.sh --build

# Open a shell in the container for debugging
./tests/run_integration_tests.sh --shell
```

### Local Tests

Run tests directly without Docker:

```bash
# Install test dependencies
pip install clawbrain[all]

# Run integration tests
python tests/integration_test.py

# Run encryption tests
python test_encryption.py
```

### Real OpenClaw Integration Test

If you have OpenClaw/ClawdBot installed, test the full integration:

```bash
# Run the OpenClaw restart test
./tests/test_openclaw_integration.sh

# Skip the restart prompt
./tests/test_openclaw_integration.sh --skip-restart
```

## Test Coverage

### Core Integration Tests (12 tests)

| Test | Description |
|------|-------------|
| Import | Verify ClawBrain can be imported |
| Initialization | Test Brain class initialization with SQLite |
| Remember/Recall | Test basic memory storage and retrieval |
| Encryption Available | Verify cryptography library is installed |
| Secret Encryption | Verify secrets are encrypted in database |
| Auto Migration | Test automatic migration of unencrypted secrets |
| CLI Available | Test CLI responds to --help |
| Hooks Directory | Verify hooks are properly structured |
| Brain Bridge | Verify brain_bridge.py exists |
| Multiple Agents | Test agent isolation for memories |
| Health Check | Test health_check() method |
| Get Unencrypted Secrets | Test get_unencrypted_secrets() method |

### OpenClaw Container Test (1 test, 6 steps)

| Step | Description |
|------|-------------|
| Platform Detection | Detects if running in OpenClaw or ClawdBot |
| Skill Installation | Verifies skill directory and files |
| Hook Installation | Verifies hooks are installed and valid JS |
| Brain Bridge | Verifies brain_bridge.py syntax |
| CLI Test | Verifies CLI responds |
| Brain Functionality | Tests remember/recall with encryption |

## Container Environment

The Docker container simulates:

- OpenClaw directory structure (`~/.openclaw/`)
- Skills installation (`~/.openclaw/skills/clawbrain/`)
- Hooks installation (`~/.openclaw/hooks/clawbrain-startup/`)
- Python 3.11 with all dependencies
- Node.js for hook testing

## Adding New Tests

Add new test functions to `integration_test.py`:

```python
def test_my_new_feature():
    """Test description."""
    from clawbrain import Brain
    
    # Your test code here
    assert something == expected
    log("Test passed message")
```

Then add it to the `tests` list in `main()`:

```python
tests = [
    # ... existing tests ...
    ("My New Feature", test_my_new_feature),
]
```

## Troubleshooting

### "Read-only file system" errors
The container mounts the source as read-only. Tests use temp directories for write operations.

### PostgreSQL/Redis connection errors
These are expected in the test container - it only has SQLite available.

### Key generation messages
`Generated new encryption key at...` is normal - each test creates a fresh Brain instance.
