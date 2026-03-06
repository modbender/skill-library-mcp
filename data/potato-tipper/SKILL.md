---
name: potato-tipper
description: "Skill for AI agents to setup the Potato Tipper on a Universal Profile on LUKSO (requires private key), and learn to build innovative tip-on-follow solutions."
---

# Potato Tipper - OpenClaw Skill

Use this skill for **anything technical** around the Potato Tipper contracts repo: 
- 📖 reading/understanding the Potato Tipper protocol
- ⚙️ setup + configure the Potato Tipper on your Universal Profile on LUKSO UP configuration
- ❓ permissions troubleshooting when setting up
- 💡building new tipping systems using ideas from the Potato Tipper

## What it is (1-paragraph mental model)

The **Potato Tipper** protocol is an LSP1 Universal Receiver Delegate on LUKSO that automatically tips $POTATO tokens to new followers.

PotatoTipper is an **LSP1 Universal Receiver Delegate** that reacts to **LSP26 follow/unfollow notifications** and transfers **LSP7 $POTATO tokens** from the followed user's 🆙 to the new follower 🆙 (when eligible). Per-user settings live in ERC725Y storage under a dedicated data key, and the contract provides self-documenting helper views for config keys.

## What this skill provides

- Understand architecture and LUKSO/LSP integrations (LSP1, LSP7, LSP26, ERC725Y) similar to the Potato Tipper
- Be aware of security and known limitations with this pattern
- Configure a Universal Profile with the required permissions and data keys
- Learn to build innovative integrations using the tip-on-follow pattern. 
- Includes TypeScript (wagmi/viem/ethers + erc725.js) and Solidity code examples.

## Deployed addresses

See `references/addresses.md` for all contract addresses on LUKSO Mainnet and Testnet (PotatoTipper, $POTATO token, LSP26 registry, RPC endpoints, explorers).

## Quick workflows

### 1) Get oriented (repo map)

Read `references/repo-overview.md` for the file map + contract responsibilities.

### 2) Configure a user's 🆙 to use PotatoTipper (one-click)

This uses a Foundry script that performs the full setup in a single `batchCalls` transaction.

**Step 1:** Create the file `script/SetupPotatoTipper.s.sol` inside the Potato Tipper contracts repo:

```solidity
// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.28;

import {Script} from "forge-std/Script.sol";
import {console2} from "forge-std/console2.sol";

interface ILSP0 {
    function batchCalls(uint256[] calldata values, bytes[] calldata payloads) external returns (bytes[] memory);
}

interface IERC725Y {
    function setDataBatch(bytes32[] calldata keys, bytes[] calldata values) external;
}

interface ILSP7 {
    function authorizeOperator(address operator, uint256 amount, bytes calldata data) external;
}

/// @title Setup PotatoTipper via LSP0 batchCalls
/// @notice One-click setup: connect PotatoTipper + set settings + authorize budget
/// @dev Run with: forge script script/SetupPotatoTipper.s.sol:SetupPotatoTipper --rpc-url <rpc> --broadcast
///
/// Required env vars:
/// - PRIVATE_KEY: EOA controller key (must have ADDUNIVERSALRECEIVERDELEGATE + CALL permissions on UP)
/// - UP_ADDRESS: Universal Profile address to configure
/// - POTATO_TIPPER_ADDRESS: PotatoTipper contract address
/// - POTATO_TOKEN_ADDRESS: $POTATO LSP7 token address
/// - TIP_AMOUNT: Amount to tip per follower (in wei, e.g., "1000000000000000000" = 1 POTATO)
/// - MIN_FOLLOWERS: Minimum follower count for eligibility (e.g., "5")
/// - MIN_POTATO_BALANCE: Minimum POTATO balance for eligibility (in wei, e.g., "100000000000000000000" = 100 POTATO)
/// - TIPPING_BUDGET: Total POTATO authorized for tipping (in wei, e.g., "1000000000000000000000" = 1000 POTATO)
contract SetupPotatoTipper is Script {
    bytes32 constant LSP1DELEGATE_ON_FOLLOW_DATA_KEY = 0x0cfc51aec37c55a4d0b1000071e02f9f05bcd5816ec4f3134aa2e5a916669537;
    bytes32 constant LSP1DELEGATE_ON_UNFOLLOW_DATA_KEY = 0x0cfc51aec37c55a4d0b100009d3c0b4012b69658977b099bdaa51eff0f0460f4;
    bytes32 constant POTATO_TIPPER_SETTINGS_KEY = 0xd1d57abed02d4c2d7ce00000e8211998bb257be214c7b0997830cd295066cc6a;

    function run() external {
        address upAddress = vm.envAddress("UP_ADDRESS");
        address potatoTipperAddress = vm.envAddress("POTATO_TIPPER_ADDRESS");
        address potatoTokenAddress = vm.envAddress("POTATO_TOKEN_ADDRESS");
        uint256 tipAmount = vm.envUint("TIP_AMOUNT");
        uint256 minFollowers = vm.envUint("MIN_FOLLOWERS");
        uint256 minPotatoBalance = vm.envUint("MIN_POTATO_BALANCE");
        uint256 tippingBudget = vm.envUint("TIPPING_BUDGET");

        console2.log("=== PotatoTipper Setup ===");
        console2.log("UP Address:", upAddress);
        console2.log("PotatoTipper:", potatoTipperAddress);
        console2.log("POTATO Token:", potatoTokenAddress);
        console2.log("Tip Amount (wei):", tipAmount);
        console2.log("Min Followers:", minFollowers);
        console2.log("Min POTATO Balance (wei):", minPotatoBalance);
        console2.log("Tipping Budget (wei):", tippingBudget);
        console2.log("");

        bytes32[] memory dataKeys = new bytes32[](3);
        dataKeys[0] = POTATO_TIPPER_SETTINGS_KEY;
        dataKeys[1] = LSP1DELEGATE_ON_FOLLOW_DATA_KEY;
        dataKeys[2] = LSP1DELEGATE_ON_UNFOLLOW_DATA_KEY;

        bytes[] memory dataValues = new bytes[](3);
        dataValues[0] = abi.encode(tipAmount, minFollowers, minPotatoBalance);
        dataValues[1] = abi.encodePacked(potatoTipperAddress);
        dataValues[2] = abi.encodePacked(potatoTipperAddress);

        bytes[] memory payloads = new bytes[](2);
        payloads[0] = abi.encodeCall(IERC725Y.setDataBatch, (dataKeys, dataValues));

        bytes memory authorizeCalldata = abi.encodeCall(
            ILSP7.authorizeOperator, (potatoTipperAddress, tippingBudget, "")
        );
        payloads[1] = abi.encodeWithSignature(
            "execute(uint256,address,uint256,bytes)", 0, potatoTokenAddress, 0, authorizeCalldata
        );

        uint256[] memory values = new uint256[](2);
        values[0] = 0;
        values[1] = 0;

        vm.startBroadcast(vm.envUint("PRIVATE_KEY"));

        console2.log("Broadcasting batchCalls to UP...");
        ILSP0(upAddress).batchCalls(values, payloads);

        vm.stopBroadcast();

        console2.log("");
        console2.log("=== Setup Complete ===");
        console2.log("PotatoTipper is now connected to the UP!");
        console2.log("Settings configured:");
        console2.log("  - Tip amount:", tipAmount, "wei");
        console2.log("  - Min followers:", minFollowers);
        console2.log("  - Min POTATO balance:", minPotatoBalance, "wei");
        console2.log("Tipping budget authorized:", tippingBudget, "wei");
    }
}
```

**Step 2:** Run the setup via the shell wrapper:

```bash
TIP_AMOUNT=42000000000000000000 \
MIN_FOLLOWERS=5 \
MIN_POTATO_BALANCE=100000000000000000000 \
TIPPING_BUDGET=1000000000000000000000 \
PRIVATE_KEY=0x... \
./skills/potato-tipper/scripts/setup_potato_tipper.sh luksoTestnet 0xYourUPAddress
```

This single transaction:
- Connects LSP1 delegates (follow + unfollow)
- Sets tip settings
- Authorizes tipping budget

Manual setup details: `references/config-and-data-keys.md`  
Script implementation: `references/foundry-batch-setup.md`

### 5) Permissions (connect / disconnect)

- **To connect:** controller needs `ADDUNIVERSALRECEIVERDELEGATE` permission
- **To disconnect:** controller needs `CHANGEUNIVERSALRECEIVERDELEGATE` permission
- If setup fails with a permission error, this is the most likely cause

Full troubleshooting + UP Browser Extension steps: `references/permissions.md`

### 6) LSP1 implementation requirement

A smart contract MUST implement the `LSP1UniversalReceiver` interface (and report `_INTERFACEID_LSP0` via ERC165) to be eligible to receive tips. The PotatoTipper checks `supportsInterface(_INTERFACEID_LSP0)` on the follower address and rejects EOAs.

When the $POTATO token transfer happens, it calls `universalReceiver(...)` on both sender and recipient 🆙. If the recipient contract does not implement LSP1, the transfer reverts (caught by the PotatoTipper's `try/catch`).

## Code examples

### TypeScript (wagmi / viem / ethers + erc725.js)

Full examples for encoding data keys, connecting/disconnecting from a dApp, and setting tip settings:
→ `references/typescript-examples.md`

### Solidity

- Setting up PotatoTipper for a 🆙 from a smart contract
- Implementing LSP1 to receive tips in a custom contract
- Using `loadTipSettingsRaw` + `decodeTipSettings` free functions from any contract
→ `references/solidity-examples.md`

## Guardrails / gotchas

- **Only 🆙 (LSP0) followers** are eligible (EOAs rejected).
- Follow/unfollow calls MUST come from the **LSP26 Follower Registry** — contract re-validates registry state.
- Uses `try/catch` around LSP7 transfers → returns user-friendly status messages, never reverts.
- "Existing followers" (before installation) are deliberately excluded from tips.
- Settings values (`tipAmount`, `minimumPotatoBalance`) are in **wei** (18 decimals).

## Design patterns + innovative integrations

- Tip-on-Follow hook pattern + self-documenting ERC725Y config: `references/learn-notes.md`
- Expansion ideas (NFT badges, tiered rewards, cross-protocol composability, marketing primitives): `references/innovative-integrations.md`
- Follow→tip event order (debugging): `references/event-flow.md`
- One-click setup / batching notes: `references/foundry-batch-setup.md`
- Security posture + known limitations: `references/security-and-limitations.md`

## Bundled resources

### references/
- `repo-overview.md` — file map + contract responsibilities
- `addresses.md` — deployed addresses on Mainnet + Testnet
- `config-and-data-keys.md` — the 3 config keys + encoding/decoding
- `permissions.md` — required LSP6 permissions (ADD/CHANGE UNIVERSALRECEIVERDELEGATE)
- `typescript-examples.md` — wagmi, viem, ethers + erc725.js code
- `solidity-examples.md` — setup contract, LSP1 receiver, settings reader
- `learn-notes.md` — design patterns (Tip-on-Follow + self-documenting config)
- `innovative-integrations.md` — expansion ideas for new integrations
- `event-flow.md` — follow→tip event emission order (debug)
- `foundry-batch-setup.md` — batching / one-click setup notes
- `security-and-limitations.md` — known limitations + security design

### scripts/
- `setup_potato_tipper.sh` — shell wrapper that clones the repo + runs the Foundry setup script

### assets/
- `assets/abis/UniversalProfile.abi.json` — minimal UP ABI for setData/setDataBatch + reads
- `assets/abis/LSP7DigitalAsset.abi.json` — minimal LSP7 ABI incl. authorizeOperator
- `assets/abis/PotatoTipper.abi.json` — minimal PotatoTipper ABI (events + a few views)
- `assets/abis/KeyManager.abi.json` — minimal KeyManager ABI (execute/executeBatch)


