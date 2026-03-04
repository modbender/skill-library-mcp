# Contributing

## Local Development Setup

### Prerequisites

- Rust toolchain (stable) with `rustfmt`
- [editorconfig-checker](https://github.com/editorconfig-checker/editorconfig-checker) for validating file formatting

### Install editorconfig-checker

```sh
brew install editorconfig-checker
```

## Formatting

### EditorConfig

The `.editorconfig` file defines formatting rules for all files in the repo (charset, line endings, indentation, trailing whitespace, final newline). Most editors pick it up automatically — install an [EditorConfig plugin](https://editorconfig.org/#pre-installed) if yours doesn't.

Before committing, verify all files comply:

```sh
ec
```

### Rust

`rustfmt.toml` keeps Rust formatting aligned with `.editorconfig` (120-char lines, Unix line endings). Format all Rust code with:

```sh
cargo fmt
```

## Testing

### Unit Tests

No infrastructure needed — these run locally against mock data:

```sh
cargo test
```

This runs **42 unit tests** (JSON schema validation, error mapping, wallet crypto, output formatting) plus **6 Tier 1 crypto tests** (encryption round-trips, tamper detection, wrong-recipient rejection). These should always pass without any external dependencies.

### Integration Tests (regtest)

Integration tests run the actual `bitkit` binary and LDK nodes against a local Bitcoin regtest network. They require [bitkit-docker](https://github.com/synonymdev/bitkit-docker) running.

#### Setup

1. **Clone bitkit-docker** as a sibling directory (next to bitkit-cli):

   ```sh
   cd ..
   git clone --recurse-submodules git@github.com:synonymdev/bitkit-docker.git
   cd bitkit-docker
   docker compose up -d
   ```

2. **Wait ~30-60 seconds** for services to initialize, then verify:

   ```sh
   curl -s http://localhost:3000/health | jq '.lnd.identity_pubkey'
   ```

   You should see the LND node's public key.

3. If you cloned bitkit-docker to a different location, set the env var:

   ```sh
   export BITKIT_DOCKER_DIR=/path/to/bitkit-docker
   ```

#### Running

Integration tests use `#[ignore]` and must be explicitly included. They should run sequentially to avoid port and state conflicts:

```sh
# All integration tests
cargo test -- --include-ignored --test-threads=1

# By test file
cargo test --test regtest  -- --include-ignored              # Basic CLI (init, balance, info, history, invoice, pay)
cargo test --test channels -- --include-ignored --test-threads=1  # Channel lifecycle (open, pay, close, force-close)
cargo test --test economy  -- --include-ignored --test-threads=1  # Agent-to-agent payments (10-round simulation, multi-hop via LND)
```

**Tier 2 messaging tests** additionally require a Pubky homeserver:

```sh
cargo test --test agent_messaging -- --include-ignored --test-threads=1
```

#### What Each Test File Covers

| File | Tests | What it exercises |
|------|------:|-------------------|
| `tests/regtest.rs` | 6 | CLI binary: init (idempotent), balance, info, history, invoice, pay error codes |
| `tests/channels.rs` | 10 | CLI binary: on-chain funding, open/close/force-close channels, payments to LND, balance tracking, invoice `--wait` mode, `--max-fee` |
| `tests/economy.rs` | 7 | LDK node API: peer connect, channel open, direct payments, bidirectional payments, 10-round economy sim, channel settlement, multi-hop routing via LND |
| `tests/agent_messaging.rs` | 8 | Tier 1 (6): local encryption round-trips, tamper detection. Tier 2 (2): full agent-to-agent invoice+pay via Pubky messenger |

### Test Architecture

The test infrastructure lives in `tests/common/`:

| Module | Purpose |
|--------|---------|
| `mod.rs` — `RegtestEnv` | Spawns the `bitkit` binary with a temp wallet dir, parses `--json` output, mines blocks via `bitcoin-cli` |
| `node.rs` — `TestNode` | Wraps an LDK `Node` with helpers: `create_invoice()`, `pay_invoice()`, `wait_for_payment_success()`, `wait_for_usable_channel()` |
| `messaging.rs` — `TestAgent` | Combines `TestNode` + `PrivateMessengerClient` for agent-to-agent Pubky tests |
| `lnd.rs` | LND integration via LNURL server (`get_info`, `create_invoice`) and REST API (`pay_invoice` with macaroon auth) |

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BITKIT_DOCKER_DIR` | `../bitkit-docker` | Path to the [bitkit-docker](https://github.com/synonymdev/bitkit-docker) clone |

### Troubleshooting

**Docker socket not found**: If you see `Cannot connect to the Docker daemon`, your Docker socket may not be at the default path. Set `DOCKER_HOST`:

```sh
export DOCKER_HOST=unix:///var/run/docker.sock
```

**Flaky channel timeouts**: Economy tests wait up to 30 seconds for channels to become usable. If a test times out on `wait_for_usable_channel`, it's usually a timing issue — retry once. Ensure `--test-threads=1` to avoid resource contention.

**LND insufficient balance**: If LND payment tests fail with `insufficient_balance`, the LND node may need re-funding. Reset with:

```sh
cd bitkit-docker
docker compose down -v
rm -rf ./lnd ./lnurl-server/data
docker compose up -d
```
