# Solidity examples

## 1) A smart contract that sets up PotatoTipper for a Universal Profile

A contract can programmatically connect the PotatoTipper and configure settings for a 🆙. The calling contract must be a controller of the target 🆙 with `ADDUNIVERSALRECEIVERDELEGATE` permission.

```solidity
// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.28;

import {IERC725Y} from "@erc725/smart-contracts/contracts/interfaces/IERC725Y.sol";
import {ILSP7DigitalAsset as ILSP7} from "@lukso/lsp7-contracts/contracts/ILSP7DigitalAsset.sol";

interface IPotatoTipperConfig {
    function encodeConfigDataKeysValues(
        TipSettings memory tipSettings
    ) external view returns (bytes32[] memory, bytes[] memory);
}

struct TipSettings {
    uint256 tipAmount;
    uint256 minimumFollowers;
    uint256 minimumPotatoBalance;
}

contract PotatoTipperSetup {
    address public immutable POTATO_TIPPER;
    ILSP7 public immutable POTATO_TOKEN;

    constructor(address potatoTipper_, address potatoToken_) {
        POTATO_TIPPER = potatoTipper_;
        POTATO_TOKEN = ILSP7(potatoToken_);
    }

    /// @notice Connect the PotatoTipper + configure settings + authorize budget in one transaction.
    ///
    /// @dev The caller must ensure this contract (or the EOA/UP calling execute) has
    ///      ADDUNIVERSALRECEIVERDELEGATE permission on the target UP.
    ///
    /// @param universalProfile Address of the 🆙 to configure.
    /// @param tipAmount Amount of 🥔 to tip per follower (in wei).
    /// @param minimumFollowers Minimum follower count for eligibility.
    /// @param minimumPotatoBalance Minimum 🥔 balance for eligibility (in wei).
    /// @param tippingBudget Total 🥔 authorized for tipping (operator allowance).
    function setupPotatoTipper(
        address universalProfile,
        uint256 tipAmount,
        uint256 minimumFollowers,
        uint256 minimumPotatoBalance,
        uint256 tippingBudget
    ) external {
        // 1. Use the self-documenting helper to encode keys + values
        TipSettings memory settings = TipSettings({
            tipAmount: tipAmount,
            minimumFollowers: minimumFollowers,
            minimumPotatoBalance: minimumPotatoBalance
        });

        (bytes32[] memory dataKeys, bytes[] memory dataValues) =
            IPotatoTipperConfig(POTATO_TIPPER).encodeConfigDataKeysValues(settings);

        // 2. Set LSP1 delegate + settings on the UP
        IERC725Y(universalProfile).setDataBatch(dataKeys, dataValues);

        // 3. Authorize PotatoTipper as operator on the $POTATO token
        //    (this call must come FROM the UP, not this contract directly)
        //    Shown here for illustration — in practice, the UP executes this.
    }
}
```

## 2) LSP1 implementation requirement for receiving tips

Any smart contract that wants to **receive** tips from the PotatoTipper (i.e., be a valid "follower") MUST implement the `LSP1UniversalReceiver` interface. This is because the PotatoTipper calls `transfer(... force: false ...)` on the $POTATO token, which notifies both sender and recipient via LSP1.

If the follower is a standard 🆙 (Universal Profile), it already implements LSP1. But if you're building a **custom smart contract** that should be able to receive tips, it must:

```solidity
// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.28;

import {IERC165} from "@openzeppelin/contracts/interfaces/IERC165.sol";
import {ERC165Checker} from "@openzeppelin/contracts/utils/introspection/ERC165Checker.sol";
import {ILSP1UniversalReceiver} from "@lukso/lsp1-contracts/contracts/ILSP1UniversalReceiver.sol";
import {ILSP1UniversalReceiverDelegate} from "@lukso/lsp1-contracts/contracts/ILSP1UniversalReceiverDelegate.sol";
import {LSP2Utils} from "@lukso/lsp2-contracts/contracts/LSP2Utils.sol";
import {_INTERFACEID_LSP0} from "@lukso/lsp0-contracts/contracts/LSP0Constants.sol";
import {
    _INTERFACEID_LSP1_DELEGATE,
    _LSP1_UNIVERSAL_RECEIVER_DELEGATE_PREFIX,
    _LSP1_UNIVERSAL_RECEIVER_DELEGATE_KEY
} from "@lukso/lsp1-contracts/contracts/LSP1Constants.sol";

/// @notice Example contract that can receive $POTATO tips with full LSP1 delegate forwarding.
/// @dev Must support LSP0 interface ID (the PotatoTipper checks `supportsInterface(_INTERFACEID_LSP0)`).
///
/// The `universalReceiver` implementation below mirrors the delegate forwarding pattern from the
/// LSP0ERC725AccountCore contract (the core of every Universal Profile):
/// https://github.com/lukso-network/lsp-smart-contracts/blob/cc1c96c460c6013bf71720b9f0a1a94e65229bd0/packages/lsp0-contracts/contracts/LSP0ERC725AccountCore.sol#L436-L511
///
/// It performs two delegate lookups:
///   1. A **global** delegate stored under `_LSP1_UNIVERSAL_RECEIVER_DELEGATE_KEY`
///   2. A **type-specific** delegate stored under `_LSP1_UNIVERSAL_RECEIVER_DELEGATE_PREFIX + bytes20(typeId)`
///
/// This allows external delegate contracts to react to incoming notifications (e.g., auto-accept
/// tokens, log events, trigger side effects) without modifying this contract.
contract PotatoTipReceiver is IERC165, ILSP1UniversalReceiver {
    using ERC165Checker for address;

    event UniversalReceiver(
        address indexed from,
        uint256 indexed value,
        bytes32 indexed typeId,
        bytes receivedData,
        bytes returnedValue
    );

    address public owner;

    mapping(bytes32 => bytes) internal _store;

    modifier onlyOwner() {
        require(msg.sender == owner, "PotatoTipReceiver: caller is not owner");
        _;
    }

    constructor(address initialOwner) {
        owner = initialOwner;
    }

    function supportsInterface(bytes4 interfaceId) external pure returns (bool) {
        return
            interfaceId == _INTERFACEID_LSP0 ||
            interfaceId == type(ILSP1UniversalReceiver).interfaceId ||
            interfaceId == type(IERC165).interfaceId;
    }

    function setData(bytes32 dataKey, bytes memory dataValue) external onlyOwner {
        _store[dataKey] = dataValue;
    }

    function getData(bytes32 dataKey) external view returns (bytes memory) {
        return _store[dataKey];
    }

    /// @notice Called by the $POTATO token (or any LSP7/LSP8) when this contract receives a transfer.
    /// @dev Adapted from LSP0ERC725AccountCore.universalReceiver:
    /// https://github.com/lukso-network/lsp-smart-contracts/blob/cc1c96c460c6013bf71720b9f0a1a94e65229bd0/packages/lsp0-contracts/contracts/LSP0ERC725AccountCore.sol#L436-L511
    ///
    /// Step 1 — query the global LSP1 delegate (`_LSP1_UNIVERSAL_RECEIVER_DELEGATE_KEY`).
    ///          If an address is stored and it supports the LSP1Delegate interface, forward the
    ///          notification via `universalReceiverDelegate(...)`.
    ///
    /// Step 2 — query a type-specific LSP1 delegate (`_LSP1_UNIVERSAL_RECEIVER_DELEGATE_PREFIX + typeId`).
    ///          Same check-and-forward logic for granular per-typeId handling.
    function universalReceiver(
        bytes32 typeId,
        bytes calldata receivedData
    ) external payable returns (bytes memory returnedValues) {
        // --- Step 1: global delegate ---
        bytes memory lsp1DelegateValue = _store[_LSP1_UNIVERSAL_RECEIVER_DELEGATE_KEY];
        bytes memory resultDefaultDelegate;

        if (lsp1DelegateValue.length >= 20) {
            address lsp1Delegate = address(bytes20(lsp1DelegateValue));

            if (lsp1Delegate.supportsERC165InterfaceUnchecked(_INTERFACEID_LSP1_DELEGATE)) {
                resultDefaultDelegate = ILSP1UniversalReceiverDelegate(lsp1Delegate)
                    .universalReceiverDelegate(msg.sender, msg.value, typeId, receivedData);
            }
        }

        // --- Step 2: type-specific delegate ---
        bytes32 lsp1TypeIdDelegateKey = LSP2Utils.generateMappingKey(
            _LSP1_UNIVERSAL_RECEIVER_DELEGATE_PREFIX,
            bytes20(typeId)
        );

        bytes memory lsp1TypeIdDelegateValue = _store[lsp1TypeIdDelegateKey];
        bytes memory resultTypeIdDelegate;

        if (lsp1TypeIdDelegateValue.length >= 20) {
            address lsp1Delegate = address(bytes20(lsp1TypeIdDelegateValue));

            if (lsp1Delegate.supportsERC165InterfaceUnchecked(_INTERFACEID_LSP1_DELEGATE)) {
                resultTypeIdDelegate = ILSP1UniversalReceiverDelegate(lsp1Delegate)
                    .universalReceiverDelegate(msg.sender, msg.value, typeId, receivedData);
            }
        }

        returnedValues = abi.encode(resultDefaultDelegate, resultTypeIdDelegate);

        emit UniversalReceiver(msg.sender, msg.value, typeId, receivedData, returnedValues);
    }
}
```

> **Important:** The PotatoTipper explicitly checks `follower.supportsInterface(_INTERFACEID_LSP0)` — so the receiving contract MUST report LSP0 support. EOAs are rejected.
>
> **How delegate forwarding works:** The `universalReceiver` function performs two lookups in internal storage, mirroring the exact pattern used by [LSP0ERC725AccountCore](https://github.com/lukso-network/lsp-smart-contracts/blob/cc1c96c460c6013bf71720b9f0a1a94e65229bd0/packages/lsp0-contracts/contracts/LSP0ERC725AccountCore.sol#L436-L511):
>
> 1. **Global delegate** — an address stored under `_LSP1_UNIVERSAL_RECEIVER_DELEGATE_KEY` is called for *every* notification, regardless of `typeId`.
> 2. **Type-specific delegate** — an address stored under `_LSP1_UNIVERSAL_RECEIVER_DELEGATE_PREFIX + bytes20(typeId)` is called only for that particular `typeId` (e.g., LSP7 token received).
>
> Both delegates must implement the `ILSP1UniversalReceiverDelegate` interface. The owner of the contract can configure delegates via `setData(...)` using the same ERC725Y data keys a Universal Profile would use.

## 3) Using `loadTipSettingsRaw` and `decodeTipSettings` from any contract

The free functions in `PotatoTipperSettingsLib.sol` can be re-used in **any** Solidity contract to read and decode a user's PotatoTipper settings from their 🆙. This is useful for building protocols that integrate with the PotatoTipper contract.

To implement:
1. copy the `PotatoTipperSettingsLib.sol` file in your repository
2. import the free functions (via `using for` directive, or by importing the functions from the file `./path/to/PotatoTipperSettingsLib.sol` directly)

```solidity
// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.28;

import {IERC725Y} from "@erc725/smart-contracts/contracts/interfaces/IERC725Y.sol";

// Import the free functions and the TipSettings struct
import "./PotatoTipperSettingsLib.sol" as SettingsLib;
import {TipSettings} from "./PotatoTipperSettingsLib.sol";

// Attach free functions to types (same pattern as the PotatoTipper contract)
using {SettingsLib.loadTipSettingsRaw} for IERC725Y;
using {SettingsLib.decodeTipSettings} for bytes;

contract PotatoTipperReader {

    /// @notice Read and decode a user's PotatoTipper settings from their 🆙.
    /// @param userUP Address of the user's Universal Profile.
    /// @return settings The decoded tip settings (tipAmount, minimumFollowers, minimumPotatoBalance).
    function getUserTipSettings(address userUP) external view returns (TipSettings memory settings) {
        // Step 1: Load raw bytes from the ERC725Y storage of the user's UP
        bytes memory rawSettings = IERC725Y(userUP).loadTipSettingsRaw();

        // Step 2: Decode the raw bytes into the TipSettings struct
        (bool success, TipSettings memory decoded, bytes memory error) = rawSettings.decodeTipSettings();

        require(success, string(error));
        return decoded;
    }

    /// @notice Check if a user has the PotatoTipper configured (tip amount > 0).
    function hasPotatoTipperConfigured(address userUP) external view returns (bool) {
        bytes memory rawSettings = IERC725Y(userUP).loadTipSettingsRaw();

        if (rawSettings.length != 96) return false;

        (bool success, TipSettings memory decoded,) = rawSettings.decodeTipSettings();
        return success && decoded.tipAmount > 0;
    }

    /// @notice Example: a protocol that gives bonus rewards to users who tip generously.
    function isGenerousTipper(address userUP, uint256 threshold) external view returns (bool) {
        bytes memory rawSettings = IERC725Y(userUP).loadTipSettingsRaw();
        (bool success, TipSettings memory decoded,) = rawSettings.decodeTipSettings();

        if (!success) return false;
        return decoded.tipAmount >= threshold;
    }
}
```

### How the free functions work

- **`loadTipSettingsRaw(IERC725Y)`**: Calls `getData(POTATO_TIPPER_SETTINGS_DATA_KEY)` on the target ERC725Y contract (🆙). Returns the raw `bytes` value.
- **`decodeTipSettings(bytes)`**: Validates the raw bytes (must be exactly 96 bytes = 3 × `uint256`), then `abi.decode`s into `(tipAmount, minimumFollowers, minimumPotatoBalance)`. Returns a success flag, the decoded struct, and an error message if invalid.

These are **free functions** (not bound to a contract), so any contract can import and use them without inheriting from anything.

