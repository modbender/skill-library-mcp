#!/usr/bin/env node
/**
 * Crypto Whale Monitor (v2.0)
 * 
 * Usage:
 *   node scripts/monitor.js [wallet1] [wallet2] ...
 *   OR
 *   node scripts/monitor.js (reads from ../references/wallets.md by default)
 * 
 * Description:
 *   Checks ETH balances of specified wallets using a public RPC.
 *   Alerts if balance exceeds threshold (WHALE_THRESHOLD_ETH).
 */

const fs = require('fs');
const path = require('path');

// --- Configuration ---
const RPC_URL = process.env.RPC_URL || 'https://eth.llamarpc.com'; // Free public endpoint
const WHALE_THRESHOLD_ETH = 100; // Alert if > 100 ETH
const DEFAULT_WALLETS_FILE = path.join(__dirname, '../references/wallets.md');

// --- Helpers ---

/**
 * Parses wallet addresses from command line args or a markdown/text file.
 */
function getTargetWallets() {
    const args = process.argv.slice(2);
    if (args.length > 0) {
        return args.filter(isValidAddress);
    }

    if (fs.existsSync(DEFAULT_WALLETS_FILE)) {
        try {
            const content = fs.readFileSync(DEFAULT_WALLETS_FILE, 'utf8');
            // Extract anything looking like an ETH address (0x followed by 40 hex chars)
            const regex = /0x[a-fA-F0-9]{40}/g;
            const matches = content.match(regex);
            if (matches) {
                return [...new Set(matches)]; // Unique addresses
            }
        } catch (err) {
            console.error(`Error reading ${DEFAULT_WALLETS_FILE}:`, err.message);
        }
    }

    // Fallback if no file or args
    return [
        '0xBE0eB53F46cd790Cd13851d5EfF43D12404d33E8', // Binance 7
        '0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B'  // Vitalik Buterin
    ];
}

function isValidAddress(addr) {
    return /^0x[a-fA-F0-9]{40}$/i.test(addr);
}

/**
 * Fetches ETH balance for a single address.
 */
async function getBalance(address) {
    try {
        const response = await fetch(RPC_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                jsonrpc: "2.0",
                method: "eth_getBalance",
                params: [address, "latest"],
                id: 1
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status}`);
        }

        const data = await response.json();
        if (data.error) {
            throw new Error(`RPC Error: ${data.error.message}`);
        }

        return data.result; // Hex string
    } catch (error) {
        console.error(`[!] Failed to check ${address}: ${error.message}`);
        return null;
    }
}

// --- Main Execution ---

async function main() {
    console.log(`\n🐳 Crypto Whale Monitor`);
    console.log(`=========================`);
    
    const wallets = getTargetWallets();
    
    if (wallets.length === 0) {
        console.error("No valid wallet addresses found. Provide args or check references/wallets.md.");
        process.exit(1);
    }

    console.log(`Monitoring ${wallets.length} wallet(s)... (Threshold: ${WHALE_THRESHOLD_ETH} ETH)\n`);

    let whaleCount = 0;

    for (const address of wallets) {
        const hexBalance = await getBalance(address);
        
        if (hexBalance) {
            const balanceWei = BigInt(hexBalance);
            // 1 ETH = 10^18 Wei
            const balanceEth = Number(balanceWei) / 1e18;
            
            const isWhale = balanceEth >= WHALE_THRESHOLD_ETH;
            const icon = isWhale ? "🚨 WHALE" : "Checked";
            
            // Output format: [ICON] Address: Balance
            console.log(`${icon} | ${address} | ${balanceEth.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ETH`);
            
            if (isWhale) whaleCount++;
        }
        
        // Small delay to be polite to public RPC
        await new Promise(r => setTimeout(r, 200)); 
    }

    console.log(`\n✅ Scan complete. Found ${whaleCount} whale(s) above threshold.`);
}

main().catch(err => {
    console.error("Fatal Error:", err);
    process.exit(1);
});
