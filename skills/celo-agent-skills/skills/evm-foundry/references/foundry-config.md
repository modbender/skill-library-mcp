# Foundry Configuration Reference

## foundry.toml Structure

```toml
[profile.default]
src = "src"
out = "out"
libs = ["lib"]
solc = "0.8.28"
optimizer = true
optimizer_runs = 200

# Celo RPC endpoints
[rpc_endpoints]
celo = "https://forno.celo.org"
celo_sepolia = "https://forno.celo-sepolia.celo-testnet.org"
localhost = "http://127.0.0.1:8545"

# Block explorer verification
[etherscan]
celo = { key = "${CELOSCAN_API_KEY}", chain = 42220, url = "https://api.celoscan.io/api" }
celo_sepolia = { key = "${CELOSCAN_API_KEY}", chain = 11142220, url = "https://api.etherscan.io/v2/api" }
```

## Compiler Settings

```toml
[profile.default]
solc = "0.8.28"
evm_version = "cancun"
optimizer = true
optimizer_runs = 200
via_ir = false
```

## Testing Configuration

```toml
[profile.default]
fuzz = { runs = 256 }
invariant = { runs = 256, depth = 15 }
verbosity = 2
```

## Formatter Configuration

```toml
[fmt]
line_length = 120
tab_width = 4
bracket_spacing = true
int_types = "long"
multiline_func_header = "all"
quote_style = "double"
number_underscore = "thousands"
```

## Remappings

Create `remappings.txt`:

```
@openzeppelin/contracts/=lib/openzeppelin-contracts/contracts/
forge-std/=lib/forge-std/src/
```

Or in `foundry.toml`:

```toml
[profile.default]
remappings = [
    "@openzeppelin/contracts/=lib/openzeppelin-contracts/contracts/",
    "forge-std/=lib/forge-std/src/"
]
```

## Multiple Profiles

```toml
[profile.default]
optimizer_runs = 200

[profile.ci]
verbosity = 4
fuzz = { runs = 1000 }

[profile.production]
optimizer_runs = 1000000
via_ir = true
```

Use with: `FOUNDRY_PROFILE=ci forge test`
