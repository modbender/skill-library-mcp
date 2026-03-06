/**
 * IRONMAN Solana Bot — Alert System
 * OpenClaw + Telegram integration
 */

const axios = require('axios');
const { config } = require('./config');

async function sendTelegram(msg) {
  try {
    await axios.post(
      `https://api.telegram.org/bot${config.botToken}/sendMessage`,
      { chat_id: config.chatId, text: msg, parse_mode: 'HTML' },
      { timeout: 8000 }
    );
  } catch (e) {
    console.error('[Alert] Telegram error:', e.message);
  }
}

function formatArbitrageAlert(opp) {
  return `
🔴 <b>ARBITRAGE OPPORTUNITY DETECTED</b>

Token: <code>${opp.token.slice(0,20)}...</code>
Input: ${opp.inputSol} SOL
Output: ${opp.outputSol.toFixed(6)} SOL
Profit: <b>${opp.profitPct.toFixed(3)}%</b> = ${opp.profitSol.toFixed(6)} SOL
USD: ~$${opp.profitUSD?.toFixed(4) || '?'}

Route:
Buy:  ${opp.buyRoute}
Sell: ${opp.sellRoute}

⚡ Act fast — opportunity lasts <2 seconds!
`.trim();
}

function formatWhaleTrade(tx) {
  const changes = tx.tokenChanges
    .map(c => `${c.action}: ${Math.abs(c.change).toFixed(2)} of ${c.mint.slice(0,12)}...`)
    .join('\n');
    
  return `
🐋 <b>WHALE ACTIVITY DETECTED</b>

Wallet: AgmLJBM...zN51
DEX: ${tx.dex}
SOL Change: ${tx.solChange.toFixed(4)} SOL

Tokens:
${changes}

Time: ${new Date(tx.timestamp * 1000).toLocaleTimeString()}
`.trim();
}

module.exports = { sendTelegram, formatArbitrageAlert, formatWhaleTrade };
