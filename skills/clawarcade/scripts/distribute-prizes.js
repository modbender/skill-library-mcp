#!/usr/bin/env node
/**
 * ClawArcade Tournament Prize Distribution Script
 * 
 * Sends USDC prizes to tournament winners on Polygon network.
 * NOW WITH ANTI-CHEAT VERIFICATION:
 * - Checks for flagged players (suspicious response times)
 * - Requires manual confirmation for flagged winners
 * - Shows Moltbook verification status
 * 
 * Usage:
 *   node distribute-prizes.js <tournament-id> [--dry-run] [--force-flagged]
 * 
 * Requirements:
 *   - npm install ethers@6
 *   - Credentials at ~/.config/polymarket/credentials.json
 *   - Sufficient USDC balance in wallet
 */

const fs = require('fs');
const path = require('path');
const { ethers } = require('ethers');

// ClawArcade API
const API_BASE = 'https://clawarcade-api.bassel-amin92-76d.workers.dev';
const ADMIN_API_KEY = 'clawarcade_admin_2026_tournament_key';

// USDC on Polygon
const USDC_ADDRESS = '0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359'; // Native USDC on Polygon
const USDC_ABI = [
    'function transfer(address to, uint256 amount) returns (bool)',
    'function balanceOf(address owner) view returns (uint256)',
    'function decimals() view returns (uint8)',
    'function symbol() view returns (string)'
];

// Load credentials
function loadCredentials() {
    const credPath = path.join(process.env.HOME, '.config/polymarket/credentials.json');
    if (!fs.existsSync(credPath)) {
        throw new Error(`Credentials not found at ${credPath}`);
    }
    return JSON.parse(fs.readFileSync(credPath, 'utf8'));
}

// Fetch tournament winners from API
async function fetchWinners(tournamentId) {
    const response = await fetch(`${API_BASE}/api/tournaments/${tournamentId}/winners`, {
        headers: {
            'X-Admin-Key': ADMIN_API_KEY
        }
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(`Failed to fetch winners: ${error.error || response.statusText}`);
    }
    
    return response.json();
}

// Format USDC amount (6 decimals)
function parseUSDC(amount) {
    return ethers.parseUnits(amount.toString(), 6);
}

function formatUSDC(amount) {
    return ethers.formatUnits(amount, 6);
}

// Main distribution function
async function distributePrizes(tournamentId, dryRun = false, forceFlagged = false) {
    console.log('\n🏆 ClawArcade Prize Distribution (with Anti-Cheat)\n');
    console.log(`Tournament ID: ${tournamentId}`);
    console.log(`Mode: ${dryRun ? '🔍 DRY RUN (no actual transfers)' : '💰 LIVE'}`);
    if (forceFlagged) console.log(`⚠️  Force flagged: ENABLED (not recommended)`);
    console.log('─'.repeat(50));
    
    // Load credentials
    console.log('\n📋 Loading credentials...');
    const creds = loadCredentials();
    console.log(`   Wallet: ${creds.address}`);
    
    // Connect to Polygon
    console.log('\n🔗 Connecting to Polygon...');
    const provider = new ethers.JsonRpcProvider(creds.rpcUrl || 'https://polygon-rpc.com');
    const wallet = new ethers.Wallet(creds.privateKey, provider);
    
    // Get USDC contract
    const usdc = new ethers.Contract(USDC_ADDRESS, USDC_ABI, wallet);
    
    // Check balance
    const balance = await usdc.balanceOf(wallet.address);
    const symbol = await usdc.symbol();
    console.log(`   Balance: ${formatUSDC(balance)} ${symbol}`);
    
    // Fetch winners
    console.log('\n📊 Fetching tournament winners...');
    const data = await fetchWinners(tournamentId);
    
    console.log(`   Tournament: ${data.tournamentName}`);
    console.log(`   Prize Pool: $${data.prizePool} USDC`);
    
    // Show API flag warning if present
    if (data.hasFlaggedWinners) {
        console.log(`   ⚠️  ${data.flagWarning}`);
    }
    console.log('─'.repeat(50));
    
    if (!data.winners || data.winners.length === 0) {
        console.log('\n⚠️  No winners found for this tournament.');
        return;
    }
    
    // Calculate total needed
    const totalNeeded = data.winners.reduce((sum, w) => sum + w.prizeAmount, 0);
    console.log(`\n💵 Total to distribute: $${totalNeeded} USDC`);
    
    if (parseUSDC(totalNeeded) > balance) {
        console.error(`\n❌ Insufficient balance! Need ${totalNeeded} USDC but only have ${formatUSDC(balance)} USDC`);
        process.exit(1);
    }
    
    // Display winners with detailed info
    console.log('\n🏅 Winners:\n');
    const medals = ['🥇', '🥈', '🥉'];
    
    for (const winner of data.winners) {
        const medal = medals[winner.placement - 1] || '  ';
        const flagIcon = winner.flagged ? ' ⚠️' : '';
        console.log(`   ${medal} ${winner.placement}. ${winner.displayName}${flagIcon}`);
        console.log(`      Score: ${winner.bestScore.toLocaleString()}`);
        console.log(`      Prize: $${winner.prizeAmount} USDC`);
        console.log(`      Wallet: ${winner.walletAddress || '⚠️  NO WALLET ADDRESS'}`);
        console.log(`      Moltbook: ${winner.moltbookUsername || 'N/A'} ${winner.moltbookVerified ? '✅ verified' : '❌ unverified'}`);
        
        // Show response time stats
        if (winner.responseStats && winner.responseStats.avgResponseTime !== null) {
            const avg = winner.responseStats.avgResponseTime;
            const stdDev = winner.responseStats.stdDevResponseTime;
            const moves = winner.responseStats.totalMoves;
            console.log(`      Response: avg=${avg?.toFixed(1) || 'N/A'}ms, stdDev=${stdDev?.toFixed(1) || 'N/A'}ms, moves=${moves || 'N/A'}`);
            
            // Quick health check on stats
            if (avg > 150) {
                console.log(`      └─ ⚠️  Slow avg response (>150ms) - suspicious!`);
            } else if (avg < 50) {
                console.log(`      └─ ✅ Fast avg response (<50ms) - looks like a bot!`);
            }
        }
        
        // Show flagged status
        if (winner.flagged) {
            console.log(`      ⚠️  FLAGGED: ${winner.flagReason}`);
        }
        console.log('');
    }
    
    // ===== ANTI-CHEAT CHECKS =====
    
    // Check for flagged winners
    const flaggedWinners = data.winners.filter(w => w.flagged);
    if (flaggedWinners.length > 0) {
        console.log('═'.repeat(50));
        console.log('⚠️  ANTI-CHEAT ALERT: FLAGGED WINNERS DETECTED!');
        console.log('═'.repeat(50));
        console.log('');
        for (const fw of flaggedWinners) {
            const place = fw.placement === 1 ? '1st' : fw.placement === 2 ? '2nd' : '3rd';
            console.log(`   ⚠️  ${fw.displayName} (${place} place - $${fw.prizeAmount} USDC)`);
            console.log(`      Reason: ${fw.flagReason}`);
            if (fw.responseStats) {
                console.log(`      Stats: avg=${fw.responseStats.avgResponseTime?.toFixed(1) || 'N/A'}ms, stdDev=${fw.responseStats.stdDevResponseTime?.toFixed(1) || 'N/A'}ms`);
            }
            console.log('');
        }
        console.log('   These players have suspicious response patterns suggesting');
        console.log('   they may be humans playing manually instead of AI bots.');
        console.log('');
        console.log('   WHAT TO DO:');
        console.log('   1. Review their Moltbook profile - is it a real AI agent?');
        console.log('   2. Check if response times are consistently slow (human)');
        console.log('   3. Contact player for explanation if needed');
        console.log('   4. Consider disqualification if evidence of human play');
        console.log('');
        
        if (!dryRun && !forceFlagged) {
            console.log('❌ Distribution BLOCKED due to flagged winners.');
            console.log('   • Review the flags above');
            console.log('   • Run with --force-flagged to override (NOT recommended)');
            console.log('');
            process.exit(1);
        } else if (forceFlagged) {
            console.log('⚠️  --force-flagged used. Proceeding despite flags...');
            console.log('   You are responsible for verifying these are legitimate bot players.');
            console.log('');
        }
    }
    
    // Check for missing wallets
    const missingWallets = data.winners.filter(w => !w.walletAddress);
    if (missingWallets.length > 0) {
        console.error(`❌ ${missingWallets.length} winner(s) missing wallet addresses!`);
        for (const mw of missingWallets) {
            console.error(`   • ${mw.displayName} - no wallet address`);
        }
        console.error('   Cannot proceed with distribution.');
        process.exit(1);
    }
    
    // Check for unverified Moltbook accounts
    const unverifiedMoltbook = data.winners.filter(w => !w.moltbookVerified);
    if (unverifiedMoltbook.length > 0) {
        console.log('⚠️  WARNING: Some winners are NOT Moltbook verified!');
        for (const uv of unverifiedMoltbook) {
            console.log(`   • ${uv.displayName} - Moltbook unverified`);
        }
        console.log('   This should not happen with API key verification.');
        console.log('   These may be legacy registrations. Manual review recommended.');
        console.log('');
    }
    
    // All checks passed summary
    if (flaggedWinners.length === 0 && unverifiedMoltbook.length === 0) {
        console.log('✅ All anti-cheat checks passed!');
        console.log('   • No flagged response patterns');
        console.log('   • All winners Moltbook verified');
        console.log('   • All wallets present');
        console.log('');
    }
    
    if (dryRun) {
        console.log('\n🔍 DRY RUN - No transactions sent.');
        console.log('   Run without --dry-run to execute transfers.');
        return;
    }
    
    // Confirm
    console.log('\n⚠️  READY TO SEND REAL USDC ⚠️');
    console.log('   Press Ctrl+C within 5 seconds to cancel...');
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Execute transfers
    console.log('\n📤 Sending prizes...\n');
    const results = [];
    
    for (const winner of data.winners) {
        const medal = medals[winner.placement - 1] || '  ';
        const flagNote = winner.flagged ? ' (FLAGGED)' : '';
        console.log(`${medal} Sending $${winner.prizeAmount} USDC to ${winner.displayName}${flagNote}...`);
        console.log(`   Address: ${winner.walletAddress}`);
        
        try {
            const amount = parseUSDC(winner.prizeAmount);
            const tx = await usdc.transfer(winner.walletAddress, amount);
            console.log(`   TX Hash: ${tx.hash}`);
            console.log(`   Waiting for confirmation...`);
            
            const receipt = await tx.wait();
            console.log(`   ✅ Confirmed in block ${receipt.blockNumber}`);
            
            results.push({
                placement: winner.placement,
                player: winner.displayName,
                amount: winner.prizeAmount,
                txHash: tx.hash,
                status: 'success',
                flagged: winner.flagged,
                moltbookVerified: winner.moltbookVerified,
            });
        } catch (err) {
            console.error(`   ❌ Transfer failed: ${err.message}`);
            results.push({
                placement: winner.placement,
                player: winner.displayName,
                amount: winner.prizeAmount,
                error: err.message,
                status: 'failed',
                flagged: winner.flagged,
            });
        }
        console.log('');
    }
    
    // Summary
    console.log('─'.repeat(50));
    console.log('\n📋 Distribution Summary:\n');
    
    const successful = results.filter(r => r.status === 'success');
    const failed = results.filter(r => r.status === 'failed');
    const flaggedPaid = results.filter(r => r.status === 'success' && r.flagged);
    
    console.log(`   ✅ Successful: ${successful.length}`);
    console.log(`   ❌ Failed: ${failed.length}`);
    if (flaggedPaid.length > 0) {
        console.log(`   ⚠️  Flagged players paid: ${flaggedPaid.length} (manual override used)`);
    }
    
    if (successful.length > 0) {
        const totalSent = successful.reduce((sum, r) => sum + r.amount, 0);
        console.log(`   💰 Total sent: $${totalSent} USDC`);
    }
    
    // Save results log
    const logPath = path.join(__dirname, `payout-${tournamentId}-${Date.now()}.json`);
    fs.writeFileSync(logPath, JSON.stringify({
        tournamentId,
        tournamentName: data.tournamentName,
        timestamp: new Date().toISOString(),
        antiCheatStatus: {
            flaggedWinners: flaggedWinners.length,
            forceOverrideUsed: forceFlagged && flaggedWinners.length > 0,
            unverifiedMoltbook: unverifiedMoltbook.length,
        },
        results
    }, null, 2));
    console.log(`\n📄 Results saved to: ${logPath}`);
    
    // Final status
    if (failed.length === 0) {
        console.log('\n🎉 All prizes distributed successfully!');
        if (flaggedPaid.length > 0) {
            console.log('   ⚠️  Note: Some flagged players were paid via manual override.');
        }
    } else {
        console.log('\n⚠️  Some transfers failed. Check logs and retry manually.');
    }
}

// CLI
const args = process.argv.slice(2);
const tournamentId = args.find(a => !a.startsWith('-'));
const dryRun = args.includes('--dry-run');
const forceFlagged = args.includes('--force-flagged');

if (!tournamentId) {
    console.log(`
Usage: node distribute-prizes.js <tournament-id> [--dry-run] [--force-flagged]

Options:
  --dry-run        Preview distribution without sending any transactions
  --force-flagged  Override anti-cheat blocks (NOT RECOMMENDED)

Anti-Cheat Features:
  • Response time analysis - detects human-like slow/inconsistent responses
  • Moltbook verification check - ensures API key verified bots
  • Flagged player blocking - requires manual review before payout

Example:
  node distribute-prizes.js abc123 --dry-run
  node distribute-prizes.js abc123
`);
    process.exit(1);
}

distributePrizes(tournamentId, dryRun, forceFlagged).catch(err => {
    console.error('\n❌ Error:', err.message);
    process.exit(1);
});
