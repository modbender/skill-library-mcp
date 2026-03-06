# Dogecoin Node Skill Heartbeat version: 1.0.4
This file is designed to periodically validate the operational state of the `/dogecoin` skill and its integration with the local node and tipping database.

### Monitoring and Validation Tasks

1. **Gateway Connectivity (CRITICAL)**
   - **Check:** Ensure the [Gateway Dashboard](http://localhost:18789/overview) shows **Status: Connected**.
   - **Validation:** If the status is **Disconnected (1006)**, the agent cannot execute commands. Click **Connect** manually if the automation fails to reconnect, or restart the gateway via `openclaw gateway restart`.

2. **Gateway Skill Registration**
   - **Check:** Verify that the `@GreatApe42069/dogecoin-node` skill appears as **Ready** in the [Skills Registry](http://localhost:18789/skills).
   - **Action:** If missing, run `openclaw skills add ~/.openclaw/skills/dogecoin-node`.

3. **Node Health & Network Sync**
   - **Command:** `~/dogecoin-cli -datadir=$HOME/.dogecoin getblockchaininfo`
   - **Goal:** Verify the node is synchronized (`blocks` should match `headers`) and the block count is increasing.
   - **Peers:** Run `~/dogecoin-cli -datadir=$HOME/.dogecoin getconnectioncount` to ensure active network peers (should be > 0).

4. **Resource & Disk Management**
   - **Disk Space:** Dogecoin node data is heavy (~190GB+). Run `df -h ~/.dogecoin` to ensure at least 10GB of overhead remains.
   - **Database Integrity:** Verify the SQLite tipping database: 
     `sqlite3 ~/.openwork/workspace/archive/tipping/dogecoin_tipping.db "PRAGMA integrity_check;"`

5. **Command Trigger Parsing**
   - Verify that subcommands are correctly handled by testing in Telegram:
      - `/dogecoin-node balance <wallet_address>`
      - `/dogecoin-node send <recipient_address> <amount>`
      - `/dogecoin-node txs <wallet_address>`
      - `/dogecoin-node price`
      - `/dogecoin-node help`
      - `/dogecoin-node health`

6. **Log Monitoring**
   - Check for skill-specific runtime errors or RPC timeouts: 
     `openclaw logs | grep dogecoin`

7. **File Persistence Check**
   - Ensure the required automation scripts exist at their declared paths:
     - **Tipping Engine:** `~/.openwork/workspace/archive/tipping/dogecoin_tipping.py`
     - **Health Monitor:** `~/.openwork/workspace/archive/health/doge_health_check.sh`

### Automation & Cron Setup
- **Automated Health Script:** `~/.openwork/workspace/archive/health/doge_health_check.sh`
- **Dashboard Integration:** Navigate to the [Cron Jobs](http://localhost:18789/cron-jobs) tab and add a new entry pointing to the health script.
- **Recommended Interval:** `*/30 * * * *` (Every 30 minutes).

### Tips
- **Health Indicator:** Always check the "Health" pulse in the top-right of the OpenClaw UI; if it turns Red, the RPC bridge is likely broken.
- **Node Restart:** If the node hangs, use `./dogecoin-cli stop` before restarting to prevent block index corruption.