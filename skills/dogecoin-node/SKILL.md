---

name: dogecoin-node

version: 1.0.4

description: A skill to set up and operate a Dogecoin Core full node with RPC access, blockchain tools, and optional tipping functionality.

---


# Dogecoin Node Skill

This skill is designed to fully automate the integration and operation of a Dogecoin Core full node and CLI over RPC, enabling blockchain tools and wallet management for various use cases, including tipping functionality using SQLite.


This skill provides:


## Functionalities
1. **Fetch Wallet Balance**
    - Retrieves the current balance of a Dogecoin wallet address.
    - Example: `/dogecoin-node balance <wallet_address>`

2. **Send DOGE**
    - Send Dogecoin from a connected wallet to a specified address.
    - Example: `/dogecoin-node send <recipient_address> <amount>`

3. **Check Transactions**
    - Retrieve recent transaction details of a wallet.
    - Example: `/dogecoin-node txs <wallet_address>`

4. **Check DOGE Price**
    - Fetch the latest Dogecoin price in USD.
    - Example: `/dogecoin-node price`

5. **Help Command**
    - Display help information about commands.
    - Example: `/dogecoin-node help`

## Installation

### Prerequisites

1. A fully synced Dogecoin Core RPC node.

2. Dogecoin `rpcuser` and `rpcpassword` configured in `dogecoin.conf`.

3. OpenClaw Gateway up-to-date.


### Steps to Configure Node 

1. **Install binaries and Download Dogecoin Core**

```bash

cd ~/downloads

curl -L -o dogecoin-1.14.9-x86_64-linux-gnu.tar.gz \

  https://github.com/dogecoin/dogecoin/releases/download/v1.14.9/dogecoin-1.14.9-x86_64-linux-gnu.tar.gz

```


2. Extract and Place Binaries

```bash

tar xf dogecoin-1.14.9-x86_64-linux-gnu.tar.gz

mkdir -p ~/bin/dogecoin-1.14.9

cp -r dogecoin-1.14.9/* ~/bin/dogecoin-1.14.9/

ln -sf ~/bin/dogecoin-1.14.9/bin/dogecoind ~/dogecoind

ln -sf ~/bin/dogecoin-1.14.9/bin/dogecoin-cli ~/dogecoin-cli

```


3. **Setup Prime Data Directory (for ~/.dogecoin)**

```bash

./dogecoind -datadir=$HOME/.dogecoin -server=1 -listen=0 -daemon

# Wait for RPC to initialize ~30s then stop once RPC is responsive

sleep 30

./dogecoin-cli -datadir=$HOME/.dogecoin stop


```


4. **Configuring RPC Credentials (localhost only)**

```bash

cat > ~/.dogecoin/dogecoin.conf <<'EOF'

server=1

daemon=1

listen=1

# optional: disable inbound until port-forwarding is set

# listen=0

rpcbind=127.0.0.1

rpcallowip=127.0.0.1

rpcuser=<strong-username>

rpcpassword=<strong-password>

txindex=1

EOF

```


5. Start and Sync

```bash

./dogecoind -datadir=$HOME/.dogecoin -daemon


```


Check sync:


```bash

./dogecoin-cli -datadir=$HOME/.dogecoin getblockcount

./dogecoin-cli -datadir=$HOME/.dogecoin getblockchaininfo


```


Stop cleanly:


```bash

./dogecoin-cli -datadir=$HOME/.dogecoin stop


```


## Example Usage (All Telegram Commands, I Would like to add all RPC/CLI cmmands to Telegram commands as well)


* `/dogecoin-node balance D8nLvyHGiDDjSm2UKnWxWehueu5Me5wTix`

* `/dogecoin-node send D8nLvyHGiDDjSm2UKnWxWehueu5Me5wTix 10`

* `/dogecoin-node txs D8nLvyHGiDDjSm2UKnWxWehueu5Me5wTix`

* `/dogecoin-node price`

* `/dogecoin-node help`


## RPC/CLI Commands Cheatsheet


Below is a comprehensive list of commonly used Dogecoin CLI commands. Use these to interact with your node. For a full list of commands, use `./dogecoin-cli help`.


### Blockchain Commands


```bash

./dogecoin-cli getblockcount # Get the current block height

./dogecoin-cli getbestblockhash # Get the hash of the latest block

./dogecoin-cli getblockchaininfo # Detailed blockchain stats

./dogecoin-cli getblockhash 1000 # Get the hash of block 1000

./dogecoin-cli getblock <blockhash> # Details for a specific block


```


### Network Commands


```bash

./dogecoin-cli getconnectioncount # Number of connections to the network

./dogecoin-cli getpeerinfo # Info about connected peers

./dogecoin-cli addnode <address> onetry # Try a one-time connection to a node

./dogecoin-cli ping # Ping all connected nodes


```


### Wallet Commands


```bash

./dogecoin-cli getwalletinfo # Wallet details (balance, keys, etc.)

./dogecoin-cli sendtoaddress <address> <amount> # Send Dogecoin to an address

./dogecoin-cli listunspent # List all unspent transactions

./dogecoin-cli getnewaddress # Generate a new receiving address

./dogecoin-cli dumpprivkey <address> # Export private key for an address (use with caution)


```


### Utility Commands


```bash

./dogecoin-cli stop # Stop the Dogecoin node safely

./dogecoin-cli help # List all available commands and usage details


```


For dynamic queries beyond this list, always refer to: `./dogecoin-cli help`.


---


## Automated Health Check (Optional Feature):

This file serves as your master validation checklist for maintaining the Dogecoin node operational health


### Health Check Script Setup: 

1. 1. To enable the health check feature, create `doge_health_check.sh` at this location, `.openwork/workspace/archive/health/` with the following code:


```bash

mkdir -p ~/.openwork/workspace/archive/health/


cat > ~/.openwork/workspace/archive/health/doge_health_check.sh <<'EOF'

#!/bin/bash


# --- Dogecoin Health Check Automation ---

# Target: ~/.openwork/workspace/archive/health/doge_health_check.sh


echo "Starting Health Check: $(date)"


# 1. Check if Dogecoin Node is Running

if pgrep -x "dogecoind" > /dev/null; then

    echo "[PASS] Dogecoin node process detected."

else

    echo "[FAIL] Dogecoin node is offline. Attempting to start..."

    ~/dogecoind -datadir=$HOME/.dogecoin -daemon

fi


# 2. Check Node Connectivity (Peers)

PEERS=$(~/dogecoin-cli getconnectioncount 2>/dev/null)

if [[ "$PEERS" -gt 0 ]]; then

    echo "[PASS] Node is connected to $PEERS peers."

else

    echo "[WARN] Node has 0 peers. Checking network..."

fi


# 3. Check Disk Space (Alert if < 10GB)

FREE_GB=$(df -BG ~/.dogecoin | awk 'NR==2 {print $4}' | sed 's/G//')

if [ "$FREE_GB" -lt 10 ]; then

    echo "[CRITICAL] Low Disk Space: Only ${FREE_GB}GB remaining!"

fi


# 4. Validate Tipping Database Integrity

DB_PATH="$HOME/.openwork/workspace/archive/tipping/dogecoin_tipping.db"

if [ -f "$DB_PATH" ]; then

    DB_CHECK=$(sqlite3 "$DB_PATH" "PRAGMA integrity_check;")

    if [ "$DB_CHECK" == "ok" ]; then

        echo "[PASS] Tipping database integrity verified."

    else

        echo "[FAIL] Database Error: $DB_CHECK"

    fi

else

    echo "[INFO] Tipping database not yet created."

fi


echo "Health Check Complete."

EOF


```


# 5. Grant execution permissions

chmod +x ~/.openwork/workspace/archive/health/doge_health_check.sh


---


## Tipping Integration (Optional Feature):


Once your node is set up and syncing, you can enable the tipping feature. This allows you to send Dogecoin tips, maintain a user wallet database, and log transactions.


### Tipping Script Setup:


1. To enable the tipping feature, create `dogecoin_tipping.py` at this location, `.openwork/workspace/archive/tipping/` with the following code:


```bash

mkdir -p ~/.openwork/workspace/archive/tipping/


cat > ~/.openwork/workspace/archive/tipping/dogecoin_tipping.py <<'EOF'

import sqlite3

import time

from typing import Optional


class DogecoinTippingDB:

    def __init__(self, db_path: str = "dogecoin_tipping.db"):

        self.conn = sqlite3.connect(db_path)

        self.create_tables()


    def create_tables(self):

        with self.conn:

            self.conn.execute("""

                CREATE TABLE IF NOT EXISTS users (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    username TEXT UNIQUE NOT NULL,

                    wallet_address TEXT NOT NULL

                )

            """)

            self.conn.execute("""

                CREATE TABLE IF NOT EXISTS transactions (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    sender TEXT NOT NULL,

                    receiver TEXT NOT NULL,

                    amount REAL NOT NULL,

                    timestamp INTEGER NOT NULL

                )

            """)


    def add_user(self, username: str, wallet_address: str) -> bool:

        try:

            with self.conn:

                self.conn.execute("INSERT INTO users (username, wallet_address) VALUES (?, ?)", (username, wallet_address))

            return True

        except sqlite3.IntegrityError:

            return False


    def get_wallet_address(self, username: str) -> Optional[str]:

        result = self.conn.execute("SELECT wallet_address FROM users WHERE username = ?", (username,)).fetchone()

        return result[0] if result else None


    def list_users(self) -> list:

        return [row[0] for row in self.conn.execute("SELECT username FROM users").fetchall()]


    def log_transaction(self, sender: str, receiver: str, amount: float):

        timestamp = int(time.time())

        with self.conn:

            self.conn.execute("INSERT INTO transactions (sender, receiver, amount, timestamp) VALUES (?, ?, ?, ?)", (sender, receiver, amount, timestamp))


    def get_sent_tips(self, sender: str, receiver: str) -> tuple:

        result = self.conn.execute("SELECT COUNT(*), SUM(amount) FROM transactions WHERE sender = ? AND receiver = ?", (sender, receiver)).fetchone()

        return result[0], (result[1] if result[1] else 0.0)


class DogecoinTipping:

    def __init__(self):

        self.db = DogecoinTippingDB()


    def send_tip(self, sender: str, receiver: str, amount: float) -> str:

        if amount <= 0: return "Amount must be > 0."

        if not self.db.get_wallet_address(sender): return f"Sender '{sender}' not found."

        if not self.db.get_wallet_address(receiver): return f"Receiver '{receiver}' not found."

        

        self.db.log_transaction(sender, receiver, amount)

        return f"Logged tip of {amount} DOGE from {sender} to {receiver}."


    def command_list_wallets(self) -> str:

        users = self.db.list_users()

        return "Registered wallets: " + ", ".join(users)


    def command_get_address(self, username: str) -> str:

        address = self.db.get_wallet_address(username)

        if address:

            return f"{username}'s wallet address is {address}."

        return f"User '{username}' not found."


    def command_get_tips(self, sender: str, receiver: str) -> str:

        count, total = self.db.get_sent_tips(sender, receiver)

        return f"{sender} has sent {count} tips totaling {total} DOGE to {receiver}."


if __name__ == "__main__":

    tipping = DogecoinTipping()

    print("Dogecoin Tipping System Initialized...MANY TIPS... MUCH WOW")


    # Sample workflow

    print("Adding users...")

    tipping.db.add_user("alice", "D6c9nY8GMEiHVfRA8ZCd8k9ThzLbLc7nfj")

    tipping.db.add_user("bob", "DA2SwTnNNMFJcLjZoRNBrurnzGRFchy54g")


    print("Listing wallets...")

    print(tipping.command_list_wallets())


    print("Fetching wallet addresses...")

    print(tipping.command_get_address("alice"))

    print(tipping.command_get_address("bob"))


    print("Sending tips...")

    print(tipping.send_tip("alice", "bob", 12.5))

    print(tipping.send_tip("alice", "bob", 7.5))


    print("Getting tip summary...")

    print(tipping.command_get_tips("alice", "bob"))

EOF


```


---


Technical usage previously documented. Contact for refinement or extensions!