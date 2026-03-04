# Doginals Skill v1.0.2

## Purpose
The Doginals skill enables users to interact with the Doginals and Dunes protocols, facilitating inscription minting, token management, and seamless integration with Dogecoin Core.

## Key Features
- **Doginals.js**: Core library for Dogecoin-native NFTs and inscriptions.
- **Dunes.js**: Supports DRC-20 fungible token minting and management.
- **Bulk Tools**: Includes `auto_inscriber_v4.py` for automated inscriptions and `bulk-mint.sh` for batch operations.
- **Auto-Setup**: Installs all dependencies, sets up Dogecoin Core, and ensures a streamlined configuration.
- **Documentation**: Comprehensive guides (`DoginalsREADME.md` and `DUNES.md`) for easy onboarding.

---

## Installation
Use the provided `install.sh` script to automatically configure all dependencies.

```bash
bash install.sh
```

---

## Usage
### Inscription Management:
```bash
node doginals.js wallet sync
node . mint <address> <path>
node . mint <address> <content type> <hex data>
node . mint <address> "" "" <delegate inscription ID>
```
Examples:
```bash
node . mint D9UcJkdirVLY11UtF77WnC8peg6xRYsogu "text/plain;charset=utf-8" 576f6f6621
node . mint D9UcJkdirVLY11UtF77WnC8peg6xRYsogu C:\doginals-main\ApeStractArtCollecton\DPAYSTONE.html
```

### DRC-20 Token Management:
```bash
node dunes.js wallet sync
node . drc-20 deploy <address> <ticker> <total> <max mint>
node . drc-20 mint <address> <ticker> <amount>
```
Examples:
```bash
node . drc-20 deploy D9pqzxiiUke5eodEzMmxZAxpFcbvwuM4Hg 'DFAT' 100000000 100000000
node . drc-20 mint D9pqzxiiUke5eodEzMmxZAxpFcbvwuM4Hg DCAC 100000000
```

### Bulk Minting (Automated with `auto_inscriber_v4.py`):
Before starting bulk minting, ensure your wallet is synced and properly funded. Place all the files you want inscribed into the `~/.doginals-main/inscribeBulk/` directory. The `auto_inscriber_v4.py` script grabs files from this location for inscription.

#### Steps:
1. Place your files in `~/.doginals-main/inscribeBulk/`.
2. Configure the `auto_inscriber_v4.py` script by specifying:
    - `directory`: Directory path containing files to inscribe (default: `~/.doginals-main/inscribeBulk/`).
    - `file_prefix`: Filename prefix (e.g., `ApeImage` for files like `ApeImage00001.jpg`).
    - `file_extension`: File type (e.g., `jpg`, `png`).
    - `start` and `end`: Range of file numbers to inscribe.

#### Run the Script:
```bash
python3 auto_inscriber_v4.py
```
The script will:
- Inscribe files in batches.
- Automatically sync the wallet if "too-long-mempool-chain" errors occur during inscription.
- Log any errors and update `.json` files with `txid` mappings.

---

## Viewing Transactions
Start the HTTP server:
```bash
node . server
```
Then open your browser to:
```bash
http://localhost:3000/tx/<transaction_id>
```
Replace `<transaction_id>` with the appropriate TXID from your logs.

---

## Notes
- Ensure Dogecoin Core is synced before performing actions.
- Replace sensitive wallet files with your own credentials.

---

## Warnings
- Only use wallets specifically configured for inscriptions to avoid unintended token burns.
- Verify all configurations before running minting or inscription commands.

