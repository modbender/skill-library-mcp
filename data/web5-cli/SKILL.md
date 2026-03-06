---
name: web5-cli
description: Use when working with Web5 CLI tool for decentralized identity, CKB wallet, DID management, PDS data operations, account creation, posting, profile updates
---

# Web5 CLI

## Overview
Web5 CLI is a command-line tool for interacting with Web5 infrastructure. It provides key management, CKB wallet operations, DID lifecycle management, and PDS (Personal Data Store) interactions.

## install
```bash
npm install -g web5-cli
```

## Commands

| Command | Purpose | Key Subcommands |
|---------|---------|-----------------|
| `keystore` | DID signing key management | new, import, clean, get, sign, verify |
| `wallet` | CKB wallet operations | new, import, clean, get, send-tx, check-tx, balance |
| `did` | DID lifecycle on CKB | build-create-tx, build-destroy-tx, build-update-didkey-tx, build-update-handle-tx, build-transfer-tx, list |
| `pds` | PDS server interactions | check-username, get-did-by-username, create-account, delete-account, login, write, repo, records, blobs, export, import |

## Quick Reference

### Key Management
```bash
web5-cli keystore new                                    # Create new keypair
web5-cli keystore import --sk <hex>                      # Import private key
web5-cli keystore get                                    # Get DID key
web5-cli keystore sign --message <hex>                   # Sign message
web5-cli keystore verify --message <hex> --signature <hex>  # Verify signature
```

### Wallet Operations
```bash
web5-cli wallet new                                      # Create CKB wallet
web5-cli wallet import --sk <hex>                        # Import wallet
web5-cli wallet get                                      # Get CKB address
web5-cli wallet balance                                  # Check balance
web5-cli wallet send-tx --tx-path <path>                 # Send transaction
web5-cli wallet check-tx --tx-hash <hash>                # Check tx status
```

### DID Management
```bash
web5-cli did build-create-tx --username <name> --pds <url> --didkey <key> --output-path <path>
web5-cli did build-destroy-tx --args <args> --output-path <path>
web5-cli did build-update-didkey-tx --args <args> --new-didkey <key> --output-path <path>
web5-cli did list --ckb-addr <address>                   # List DID cells
```

### PDS Operations
```bash
web5-cli pds check-username --username <name>
web5-cli pds get-did-by-username --username <name>
web5-cli pds create-account --pds <domain> --username <name> --didkey <key> --did <did> --ckb-address <addr>
web5-cli pds login --pds <domain> --didkey <key> --did <did> --ckb-address <addr>
web5-cli pds write --pds <domain> --accessJwt <jwt> --didkey <key> --did <did> --rkey <key> --data <json>
web5-cli pds repo --pds <domain> --did <did>
web5-cli pds records --pds <domain> --did <did> --collection <nsid> [--limit N] [--cursor <cursor>]
web5-cli pds export --pds <domain> --did <did> --data-file <path> [--since <cid>]
web5-cli pds import --pds <domain> --did <did> --accessJwt <jwt> --data-file <path>
```

## Configuration

- **Keystore**: Private key stored at `~/.web5-cli/signkey`
- **Wallet**: Private key stored at `~/.web5-cli/ckb-sk`
- **Account Info**: Stored at `~/.web5-cli/account.json` after account creation (includes Username, DID, Handle, didkey, ckb address, PDS domain, etc.)
- **Network**: Set via `CKB_NETWORK` environment variable (`ckb_testnet` or `ckb`)

## Output Format

All commands output JSON format for easy parsing by AI agents and scripts.

## Notes
* --pds arg no 'https://' or 'http://' prefix, just the hostname
* one account only and always belong to one pds
* only one did and one account in same time
* Don't modify or delete the key/wallet files directly, use the CLI commands to manage them, and need user confirmation for destructive actions like `keystore clean` or `wallet clean`

## Workflow Scripts

Use these Python scripts for common multi-step operations:

### create account 
1. call `web5-cli wallet get` check if wallet exists and get ckb address
2. if no wallet, create wallet and get ckb address
3. call `web5-cli wallet balance` check if balance > 450 testnet CKB
4. if no balance, prompt user to transfer some ckb to ckb address and wait for confirmation
5. once have enough balance, call `scripts/create_account.py` to complete account creation (keystore + wallet + DID + PDS)
6. write account info (includes Username, DID, Handle, didkey, ckb address, PDS domain, etc) to `~/.web5-cli/account.json` for later use (like posting, profile update)

### destroy account
1. call `scripts/destroy_account.py` to complete account destruction (delete PDS Account then destory DID cell, don't delete wallet or keystore since they can be reused for new accounts)
2. delete `~/.web5-cli/account.json` after account destroyed

### update profile
1. get account info from `~/.web5-cli/account.json`, if not exist, notify user to create account first and exit
2. prompt user to input new profile info (like displayName, handle, etc), and construct json data for writing to pds
4. call `web5-cli pds login --pds <domain> --didkey <didkey> --did <did> --ckb-address <addr>` with the correct parameters to get an access jwt for PDS operations, if login failed, notify user and exit
5. call `web5-cli pds write --pds <domain> --accessJwt <jwt> --didkey <key> --did <did> --rkey 'self' --data <json>` to update profile record in PDS, with the correct parameters. json data should be in the format of 
```
{
  $type: 'app.actor.profile'
  displayName: string;
  handle: string;
  [key: string]: any;
}
```

### post to bbs
1. get account info from `~/.web5-cli/account.json`, if not exist, notify user to create account first and exit
2. prompt user to input post info (like section_id, title, text), and construct json data for writing to pds. about section_id, you can use "3" or "4" for now. 
3. call `web5-cli pds login --pds <domain> --didkey <didkey> --did <did> --ckb-address <addr>` with the correct parameters to get an access jwt for PDS operations, if login failed, notify user and exit
4. call `web5-cli pds write --pds <domain> --accessJwt <jwt> --didkey <key> --did <did> --data <json>` (--rkey is no need) to create a new post in PDS, with the correct parameters. json data should be in the format of 
```
{
  $type: 'app.bbs.post'
  section_id: string;
  title: string;
  text: string;
}
```


### Script Examples

```bash
# Create a complete account
python create_account.py alice web5.bbsfans.dev

# destroy the account
python destroy_account.py alice web5.bbsfans.dev
```

## Security Notes

- Private keys are stored in plaintext for this technical validation tool
- Do NOT use in production environments
- This is a proof-of-concept for AI-agent-driven Web5 interactions

## public information
avliable pds url:
* web5.bbsfans.dev
* web5.ccfdao.dev

avliable data structure for writing to pds:
* profile of user
```
{
  $type: 'app.actor.profile'
  displayName: string;
  handle: string;
  [key: string]: any;
}
```
* post of bbs
```
{
  $type: 'app.bbs.post'
  section_id: string;
  title: string;
  text: string;
  edited?: string
  created?: string
  is_draft?: boolean
  is_announcement?: boolean
}
```
* comment of bbs
```
{
  $type: 'app.bbs.comment'
  post: string  // 原帖uri
  text: string;
  section_id: string;
  edited?: string;
}
```
* like of bbs
```
{
  $type: 'app.bbs.like'
  to: string;
  section_id: string;
}
```
* reply of bbs
```
{
  $type: 'app.bbs.reply'
  post: string
  comment?: string
  to?: string
  text: string
  section_id: string
  edited?: string
}
```
* reply of dao
```
{
  $type: 'app.dao.reply'
  proposal: string
  to?: string
  text: string
  parent?: string
}
```
* proposal of dao
```
{
  $type: 'app.dao.proposal'
  [key: string]: unknown;
}
```
* like of dao
```
{
  $type: 'app.dao.like'
  to: string;
  viewer: string;
}
```
