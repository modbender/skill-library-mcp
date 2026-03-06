# Dogecoin RPC Command Cheat Sheet

### Node and Blockchain Info
1. **Get Blockchain Info**:
   - Command: `getblockchaininfo`
   - Returns details about the blockchain, including chain, blocks, headers, difficulty, and network status.

2. **Get Network Info**:
   - Command: `getnetworkinfo`
   - Provides network information including version, protocol version, and connections.

3. **Get Peer Info**:
   - Command: `getpeerinfo`
   - Returns information on connected peers, including sync status.

4. **Get Current Block Count**:
   - Command: `getblockcount`
   - Returns the latest block height currently recognized by the node.

5. **Get Block Hash by Height**:
   - Command: `getblockhash <height>`

6. **Get Block by Hash**:
   - Command: `getblock <blockhash>`

### Wallet Operations
1. **Get Wallet Info**:
   - Command: `getwalletinfo`
   - Retrieves information about the wallet, including balance and transactions.

2. **List Unspent Outputs**:
   - Command: `listunspent [minConf maxConf [addresses]]`
   - Provides a list of unspent transaction outputs (UTXOs).

3. **Send to Address**:
   - Command: `sendtoaddress <address> <amount>`
   - Sends a specified amount to the given address.

4. **Generate a New Address**:
   - Command: `getnewaddress [label]`

5. **Get Received by Address**:
   - Command: `getreceivedbyaddress <address> [minConf]`

### Mining and Fees
1. **Get Mining Info**:
   - Command: `getmininginfo`
   - Provides information about mining status.

2. **Estimate Fee**:
   - Command: `estimatesmartfee <conf_target>`

### Debugging and Logs
1. **Get Memory Pool**:
   - Command: `getrawmempool`
   - Returns all transaction IDs currently in the mempool.

2. **Dump Debug Logs**:
   - File: `debug.log`
   - Can be checked for error messages or warnings about syncing.

## Usage
Run commands like this:
```bash
./bin/dogecoin-cli <command>
```
For example:
```bash
./bin/dogecoin-cli getblockchaininfo
```