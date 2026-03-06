# One-click setup idea (Foundry) — connect + settings + budget

## Why this exists

In practice, configuring PotatoTipper for a 🆙 is **3 distinct actions**:

1) Write ERC725Y keys for LSP1 delegates (follow + unfollow)
2) Write ERC725Y key for `PotatoTipper:Settings`
3) Authorize PotatoTipper as operator on $POTATO with a tipping budget

(1) and (2) are **UP storage writes** (ERC725Y). (3) is an **LSP7 token call**.

Depending on how the user operates their 🆙, you might perform these as:
- multiple transactions from the user’s controller, or
- a single KeyManager `executeBatch(...)` (preferred when you have permission), or
- a single LSP20/LSP25 signed relay flow.

## Permissions required (controller)

- Connect (set new LSP1 delegate): `ADDUNIVERSALRECEIVERDELEGATE`
- Disconnect (clear/change LSP1 delegate): `CHANGEUNIVERSALRECEIVERDELEGATE`

Additionally, any approach that calls into the token from the 🆙 context requires the controller to have the relevant **CALL** permissions (LSP6) to call the $POTATO token contract.

## Implementation note

The exact batching mechanism depends on whether you:
- call `IERC725Y(UP).setDataBatch(...)` directly (only possible if controller is allowed to call the UP directly), or
- route through `KeyManager.execute(...)` / `executeBatch(...)`.

Because KeyManager permissions/config differ per 🆙, this repo/skill provides a **template** approach rather than a single hardcoded script.

## Concrete implementation (LSP0 batchCalls)

A ready-to-use Foundry script is available at:
- `scripts/SetupPotatoTipper.s.sol`
- Shell wrapper: `scripts/setup_potato_tipper.sh`

This uses **LSP0's `batchCalls(...)`** function (not KeyManager) and broadcasts from an EOA controller.

### Usage

```bash
TIP_AMOUNT=42000000000000000000 \
MIN_FOLLOWERS=5 \
MIN_POTATO_BALANCE=100000000000000000000 \
TIPPING_BUDGET=1000000000000000000000 \
PRIVATE_KEY=0x... \
./skills/potato-tipper/scripts/setup_potato_tipper.sh luksoTestnet 0xYourUPAddress
```

The script:
1. Encodes LSP1 delegate keys + PotatoTipper:Settings key
2. Builds two batchCalls payloads:
   - `UP.setDataBatch(...)` — connect delegates + configure settings
   - `UP.execute(POTATO.authorizeOperator(...))` — authorize tipping budget
3. Calls `UP.batchCalls([0, 0], [payload1, payload2])`

### Required controller permissions

The calling EOA must have on the target 🆙:
- `ADDUNIVERSALRECEIVERDELEGATE` (to set new LSP1 delegates)
- `CALL` (to call the $POTATO token from the UP context)

