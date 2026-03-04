# Permissions required for connecting/disconnecting PotatoTipper

## Context

A Universal Profile (🆙) is controlled by **controllers** — addresses that have been granted specific LSP6 Key Manager permissions. When a dApp or script wants to set ERC725Y data on a 🆙 (which is what "connecting" the PotatoTipper does), the calling address (controller) must have the right permissions.

## Required permissions

### To CONNECT the PotatoTipper → `ADDUNIVERSALRECEIVERDELEGATE`

The controller calling `setDataBatch(...)` on the 🆙 to write the LSP1 delegate data keys **must** have the permission **`ADDUNIVERSALRECEIVERDELEGATE`** (also labeled "Add notifications & automation" in the UP Browser Extension).

This permission allows writing a new LSP1 Universal Receiver Delegate address for a specific notification type ID that was not set before.

### To DISCONNECT the PotatoTipper → `CHANGEUNIVERSALRECEIVERDELEGATE`

The controller calling `setDataBatch(...)` on the 🆙 to clear (set to `0x`) the LSP1 delegate data keys **must** have the permission **`CHANGEUNIVERSALRECEIVERDELEGATE`** (also labeled "Edit notifications & automation" in the UP Browser Extension).

This permission allows changing or removing an existing LSP1 Universal Receiver Delegate address.

## Common troubleshooting

If connecting or disconnecting the PotatoTipper fails with a permission error, the cause is almost always:

1. The controller (e.g., the UP Browser Extension key) **does not have `ADDUNIVERSALRECEIVERDELEGATE`** (when connecting).
2. The controller **does not have `CHANGEUNIVERSALRECEIVERDELEGATE`** (when disconnecting).

### How to fix (UP Browser Extension)

1. Open the Universal Profile Browser Extension.
2. Click on the "Controllers" tab.
3. Click on the "UP Browser Extension" controller.
4. Scroll to **"Add and Edit notifications & automation"** permissions.
5. Toggle ON the relevant permissions.
6. Click "Save Changes" + confirm the transaction.

> **Security tip:** You can toggle these permissions OFF after connecting/disconnecting the PotatoTipper for safety. Only enable them when needed.

