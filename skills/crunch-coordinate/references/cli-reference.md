# Coordinator CLI Full Reference

## Package Information
- **Name:** `@crunchdao/crunch-cli`
- **Binary:** `crunch-cli`
- **Version:** 1.1.6+

## Installation

```bash
npm install -g @crunchdao/crunch-cli
```

## Configuration

### Global Config File
Location: `~/.crunch/config.json`

```json
{
  "network": "devnet",
  "wallet": "./accounts/coordinator.json",
  "loglevel": "info"
}
```
Is where global profiles are stored. Never change/delete existing profiles except if asked.

### Config Commands
```bash
crunch-cli config set <key> <value>       # Set config value
crunch-cli config show                    # Show current config file
crunch-cli config active                  # Show resolved/active configuration values
crunch-cli config init                    # Initialize config file with defaults
crunch-cli config list-profiles           # List available profiles
crunch-cli config save-profile <name>     # Save current config as a profile
crunch-cli config use <profile>           # Switch to a profile
```

## Global Options

| Flag | Description |
|------|-------------|
| `-n, --network` | Solana network (default: `devnet`) |
| `-w, --wallet` | Path to wallet keypair |
| `-u, --url` | Custom RPC URL |
| `-o, --output` | Output format: `json`, `table`, `yaml` (default: `table`) |
| `-v, --verbose` | Show verbose output |
| `-q, --quiet` | Suppress non-essential output |
| `--dry-run` | Preview without executing |
| `--timeout` | Command timeout in seconds (default: 60) |

## Complete Command Reference

### Coordinator Management

#### `coordinator register <name>`
Register a new coordinator with the protocol.

```bash
crunch-cli coordinator register "AI Research Lab"
```

---

#### `coordinator get [owner]`
Get coordinator details by owner address (defaults to current wallet).

```bash
crunch-cli coordinator get
crunch-cli coordinator get "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"
```

---

#### `coordinator list`
List all coordinators.

```bash
crunch-cli coordinator list
```

---

#### `coordinator get-config`
Get coordinator configuration from the protocol.

```bash
crunch-cli coordinator get-config
```

---

#### `coordinator set-emission-config <coordinatorPct> <stakerPct> <crunchFundPct>`
Set emission configuration percentages (must sum to 100).

```bash
crunch-cli coordinator set-emission-config 50 40 10
```

---

#### `coordinator reset-hotkey`
Reset/regenerate the SMP hotkey.

```bash
crunch-cli coordinator reset-hotkey
```

---

### Competition (Crunch) Management

#### `crunch list [wallet]`
List crunches (optionally for a specific coordinator wallet).

```bash
crunch-cli crunch list
crunch-cli crunch list "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"
```

---

#### `crunch create <name> <payoutAmount> [maxModelsPerCruncher]`
Create a new crunch competition.

```bash
crunch-cli crunch create "Q4 2024 Trading Challenge" 10000 5
```

**Arguments:**
- `name` - Competition name (unique)
- `payoutAmount` - Prize pool in USDC
- `maxModelsPerCruncher` - Max models per participant (default: 2)

---

#### `crunch get <name>`
Get detailed information about a competition.

```bash
crunch-cli crunch get "Synth"
```

---

#### `crunch start <name>`
Start a competition (Created → Active).

```bash
crunch-cli crunch start "Q4 2024 Trading Challenge"
```

---

#### `crunch end <name>`
End a competition (Active → Ended).

```bash
crunch-cli crunch end "Q4 2024 Trading Challenge"
```

---

#### `crunch get-cruncher <crunchName> <cruncherWallet>`
Get cruncher details for a specific competition.

```bash
crunch-cli crunch get-cruncher "Synth" "5abc..."
```

---

#### `crunch set-fund-config <crunchName> <cruncherPct> <dataproviderPct> <computeProviderPct>`
Set fund configuration for a crunch (percentages must sum to 100).

```bash
crunch-cli crunch set-fund-config "Synth" 70 20 10
```

---

### Financial Commands

#### `crunch deposit-reward <crunchName> <amount>`
Deposit USDC rewards to a competition.

```bash
crunch-cli crunch deposit-reward "Synth" 5000
```

---

#### `crunch margin <crunchName>`
Execute margin payout for a competition.

```bash
crunch-cli crunch margin "Synth"
```

---

#### `crunch drain <crunchName>`
Drain remaining USDC from a competition.

```bash
crunch-cli crunch drain "Synth"
```

---

### Checkpoint Commands

#### `crunch checkpoint-create <crunchName> <prizeFileName> [--dryrun]`
Create a checkpoint for payout distribution.

```bash
crunch-cli crunch checkpoint-create "Synth" "./prizes.json"
crunch-cli crunch checkpoint-create "Synth" "./prizes.json" --dryrun
```

**Prize File Format (JSON Lines):**
```json
{"timestamp": 1840417288969, "model": "model_1", "prize": 456.78}
{"timestamp": 1840417288969, "model": "model_2", "prize": 412.34}
{"timestamp": 1840417288969, "model": "model_3", "prize": 130.88}
```

---

#### `crunch checkpoint-get-current <crunchName>`
Get the current checkpoint information.

```bash
crunch-cli crunch checkpoint-get-current "Synth"
```

---

#### `crunch checkpoint-get <crunchName> <checkpointIndex>`
Get checkpoint by index.

```bash
crunch-cli crunch checkpoint-get "Synth" 3
```

---

### Cruncher Commands

#### `cruncher create`
Create a cruncher account.

```bash
crunch-cli cruncher create
```

---

#### `cruncher get`
Get cruncher info for current wallet.

```bash
crunch-cli cruncher get
```

---

#### `cruncher get-address <wallet>`
Get cruncher address from wallet address.

```bash
crunch-cli cruncher get-address "5abc..."
```

---

#### `cruncher register <crunchName>`
Register for a crunch competition.

```bash
crunch-cli cruncher register "Synth"
```

---

#### `cruncher claim <crunchName>`
Claim rewards from a crunch.

```bash
crunch-cli cruncher claim "Synth"
```

---

#### `cruncher get-claim-record <crunchName>`
Get claim record for a cruncher in a crunch.

```bash
crunch-cli cruncher get-claim-record "Synth"
```

---

#### `cruncher get-claimable-checkpoints <crunchName>`
Get claimable checkpoints for a crunch.

```bash
crunch-cli cruncher get-claimable-checkpoints "Synth"
```

---

#### `cruncher model add <crunchName>`
Add a model to a crunch.

```bash
crunch-cli cruncher model add "Synth"
```

---

#### `cruncher model get <crunchName>`
Get model info for a crunch.

```bash
crunch-cli cruncher model get "Synth"
```

---

#### `cruncher model get-crunch-models <crunchName>`
Get all models for a crunch.

```bash
crunch-cli cruncher model get-crunch-models "Synth"
```

---

#### `cruncher model update <crunchName>`
Update model results.

```bash
crunch-cli cruncher model update "Synth"
```

---

### Staking Commands

#### `staking deposit <amount>`
Deposit CRNCH tokens to stake.

```bash
crunch-cli staking deposit 1000
```

---

#### `staking withdraw <amount>`
Withdraw CRNCH tokens from stake.

```bash
crunch-cli staking withdraw 500
```

---

#### `staking delegate <coordinator> <amount>`
Delegate tokens to a coordinator.

```bash
crunch-cli staking delegate "CoordAddr..." 1000
```

---

#### `staking undelegate <coordinator> <amount>`
Undelegate tokens from a coordinator.

```bash
crunch-cli staking undelegate "CoordAddr..." 500
```

---

#### `staking claim`
Claim pending staking rewards.

```bash
crunch-cli staking claim
```

---

#### `staking rewards`
Show claimable rewards.

```bash
crunch-cli staking rewards
```

---

#### `staking positions`
Show your staking positions.

```bash
crunch-cli staking positions
```

---

#### `staking available`
Show available (unstaked) balance.

```bash
crunch-cli staking available
```

---

#### `staking accounts`
Show staking account addresses.

```bash
crunch-cli staking accounts
```

---

#### `staking positions-accounts`
Show position account addresses.

```bash
crunch-cli staking positions-accounts
```

---

### Model & Simulation Commands

> **Note:** Requires Python `crunch-cli` package (`pip install crunch-cli`)

#### `model list`
List available scenarios/simulations.

```bash
crunch-cli model list
```

---

#### `model run <scenario>`
Run a simulation scenario.

```bash
crunch-cli model run "my-scenario"
```

---

#### `model validate <scenario>`
Validate a scenario configuration.

```bash
crunch-cli model validate "my-scenario"
```

---

## JSON Output Mode

All commands support `-o json` for structured output:

```bash
crunch-cli -o json crunch get "Synth"
```

---

## Typical Competition Workflow

1. **Register:** `crunch-cli coordinator register "My Coordinator"`
2. **Get Approved:** Wait for admin approval
3. **Create:** `crunch-cli crunch create "My Competition" 10000 2`
4. **Fund:** `crunch-cli crunch deposit-reward "My Competition" 10000`
5. **Start:** `crunch-cli crunch start "My Competition"`
6. **Monitor:** `crunch-cli crunch get "My Competition"`
7. **Checkpoint:** `crunch-cli crunch checkpoint-create "My Competition" prizes.json`
8. **End:** `crunch-cli crunch end "My Competition"`
9. **Drain:** `crunch-cli crunch drain "My Competition"`
