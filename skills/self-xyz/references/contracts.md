# Smart Contract Integration — Celo / Solidity

## SelfVerificationRoot

Abstract contract to inherit from. Handles proof verification via Hub V2 callback pattern.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import { SelfVerificationRoot } from "@selfxyz/contracts/contracts/abstract/SelfVerificationRoot.sol";

contract MyVerifier is SelfVerificationRoot {
    mapping(address => bool) public verified;

    constructor(address hubV2, string memory scopeSeed)
        SelfVerificationRoot(hubV2, scopeSeed)
    {}

    // Return the config ID registered via Hub V2
    function getConfigId(
        bytes32,          // attestationId
        bytes32,          // nullifier
        bytes memory      // userDefinedData
    ) internal view override returns (uint256) {
        return configId;  // stored after calling setVerificationConfigV2
    }

    // Called by Hub V2 after successful proof verification
    function customVerificationHook(
        bytes memory output,
        bytes memory userData
    ) internal override {
        address user = abi.decode(userData, (address));
        verified[user] = true;
    }
}
```

## Verification Flow

1. Deploy contract with Hub V2 address and a scope seed string
2. Register verification config → get `configId`
3. User submits proof by calling `verifySelfProof(proofPayload, userContextData)`
4. Hub V2 validates the proof
5. Hub V2 calls back `onVerificationSuccess` → triggers `customVerificationHook`

## Hub V2 Addresses

| Network | Address |
|---------|---------|
| Celo Mainnet | `0xe57F4773bd9c9d8b6Cd70431117d353298B9f5BF` |
| Celo Sepolia | `0x16ECBA51e18a4a7e61fdC417f0d47AFEeDfbed74` |
| Celo Sepolia Staging | `0x68c931C9a534D37aa78094877F46fE46a49F1A51` |

## Registering a Verification Config

```solidity
import { IIdentityVerificationHubV2 } from "@selfxyz/contracts/contracts/interfaces/IIdentityVerificationHubV2.sol";

// Build config using SelfUtils
bytes memory config = SelfUtils.buildVerificationConfig(
    true,   // ofac
    true,   // excludedCountries enabled
    18,     // minimumAge
    // ... country list, disclosure flags
);

uint256 configId = IIdentityVerificationHubV2(hubV2).setVerificationConfigV2(config);
```

## Working with userDefinedData

For contracts needing multiple verification configs (e.g., different tiers).

```solidity
contract TieredVerifier is SelfVerificationRoot {
    mapping(bytes32 => uint256) public configIds;

    function registerConfig(string memory tier, bytes memory config) external onlyOwner {
        bytes32 key = keccak256(abi.encodePacked(tier));
        configIds[key] = IIdentityVerificationHubV2(hubV2).setVerificationConfigV2(config);
    }

    function getConfigId(
        bytes32,
        bytes32,
        bytes memory userDefinedData
    ) internal view override returns (uint256) {
        bytes32 key = keccak256(userDefinedData);
        return configIds[key];
    }

    function customVerificationHook(
        bytes memory output,
        bytes memory userData
    ) internal override {
        // Parse output for disclosed attributes
        // GenericDiscloseOutputV2 has pre-extracted string fields
    }
}
```

**Frontend must pass `userDefinedData`:**

```typescript
const selfApp = new SelfAppBuilder({
  // ...
  endpoint: "0xcontractaddress",  // lowercase!
  endpointType: "celo",
  userDefinedData: "premium",     // matches contract tier key
}).build();
```

## GenericDiscloseOutputV2

Struct returned in `customVerificationHook` output with pre-extracted fields:

```solidity
struct GenericDiscloseOutputV2 {
    string issuingState;
    string name;
    string nationality;
    string dateOfBirth;
    string gender;
    string expiryDate;
    string idNumber;
    // ... additional fields
}
```

Decode in hook:

```solidity
function customVerificationHook(bytes memory output, bytes memory) internal override {
    GenericDiscloseOutputV2 memory disclosed = abi.decode(output, (GenericDiscloseOutputV2));
    // Use disclosed.nationality, disclosed.name, etc.
}
```

## Scope & Replay Prevention

- Constructor Poseidon-hashes `contractAddress + scopeSeed` → unique scope
- Same scope seed on different contracts produces different scopes
- Nullifiers are scope-bound — one proof per scope per person (Sybil resistance)
- Cross-contract replay is impossible by design

## Foundry Setup

```bash
forge install selfxyz/self
```

```toml
# foundry.toml
[profile.default]
remappings = ["@selfxyz/contracts/=lib/self/contracts/"]
```
