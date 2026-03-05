/**
 * Polymarket AutoTrader (Premium) — BTC 5-Min Prediction Bot
 * 
 * Quantitative Strategy:
 *   1. Monitor BTC price delta vs 5-min slot open price
 *   2. In the last 30 seconds, when BTC moves ≥$50, buy the winning side
 *   3. FOK (Fill-or-Kill) orders — must fully match or auto-cancel
 *   4. Polymarket auto-settles at slot end, winning shares pay $1.00
 *   5. Per-trade profit: 5-8% ($0.92-0.95 entry → $1.00 payout)
 * 
 * Safety:
 *   - FOK mode: order must be fully matched, otherwise auto-cancelled
 *   - No partial fills, no hanging orders
 * 
 * Billing:
 *   - Each trade costs 0.001 USDT (1 token)
 *   - Configure billing endpoint and API key in .env
 */

import 'dotenv/config';
import { ClobClient, Side, OrderType } from '@polymarket/clob-client';
import { Wallet } from '@ethersproject/wallet';
import { JsonRpcProvider } from '@ethersproject/providers';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { createRequire } from 'module';

// ═══════════════════════════════════════════
// Configuration
// ═══════════════════════════════════════════

const CREDS_FILE = './.poly-creds.json';

const CFG = {
  // Trading
  TRADE_SIZE_USD: parseFloat(process.env.TRADE_SIZE_USD || '50'),
  MAX_ASK_PRICE: parseFloat(process.env.MAX_ASK_PRICE || '0.95'),
  MIN_BTC_MOVE: parseFloat(process.env.MIN_BTC_MOVE || '50'),
  STRONG_BTC_MOVE: parseFloat(process.env.STRONG_BTC_MOVE || '100'),

  // Timing
  ENTRY_LAST_SEC: 30,
  EXIT_BUFFER: 3,

  // Risk
  MAX_TRADES_PER_HOUR: 10,
  MAX_LOSS_SESSION: 200,

  // Billing — pre-configured, no user setup needed
  BILLING_API_URL: process.env.BILLING_API_URL || 'https://skillpay.me',
  BILLING_API_KEY: process.env.BILLING_API_KEY || 'sk_8801b2495fb7f32b7ee4e3ac6254cd765b3c2199b77e73867d1726d1d99dbae5',
  BILLING_SKILL_ID: process.env.BILLING_SKILL_ID || 'd0d6e962-a06a-4dd4-8980-12bf844279e9',
  USER_ID: process.env.USER_ID || process.env.POLY_WALLET_ADDRESS || '',
  TOKEN_COST_PER_TRADE: 0.001, // 1 token = 0.001 USDT (1000 tokens per 1 USDT)

  // Files
  LOG_FILE: './trades.json',
};

// ═══════════════════════════════════════════
// Billing Integration
// ═══════════════════════════════════════════

async function checkAndCharge() {
  if (!CFG.BILLING_API_KEY || !CFG.BILLING_SKILL_ID) {
    console.error('  ❌ BILLING_API_KEY and BILLING_SKILL_ID are required.');
    console.error('  👉 Copy .env.example to .env — billing credentials are pre-filled.');
    console.error('  👉 Run: cp .env.example .env');
    return { success: false, error: 'billing_not_configured' };
  }
  if (!CFG.USER_ID) {
    console.error('  ❌ POLY_WALLET_ADDRESS is required (also used as billing user ID).');
    return { success: false, error: 'no_user_id' };
  }

  try {
    const resp = await fetch(`${CFG.BILLING_API_URL}/api/v1/billing/charge`, {
      method: 'POST',
      headers: {
        'X-API-Key': CFG.BILLING_API_KEY,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: CFG.USER_ID,
        skill_id: CFG.BILLING_SKILL_ID,
        amount: CFG.TOKEN_COST_PER_TRADE,
      }),
    });

    const data = await resp.json();

    if (data.success) {
      console.log(`  💰 Charged $${CFG.TOKEN_COST_PER_TRADE} | Balance: $${data.balance.toFixed(4)} USDT`);
      return { success: true };
    } else {
      console.log(`  ⚠️  Insufficient balance! Balance: $${data.balance.toFixed(4)} USDT`);
      if (data.payment_url) {
        console.log(`  🔗 Top up here: ${data.payment_url}`);
      } else {
        console.log(`  🔗 Please charge at: ${CFG.BILLING_API_URL}`);
      }
      return { success: false, payment_url: data.payment_url };
    }
  } catch (err) {
    console.log(`  ⚠️  Billing API error: ${err.message} — trade blocked (billing required)`);
    return { success: false, error: 'billing_api_error' };
  }
}

async function checkBalance() {
  if (!CFG.BILLING_API_KEY || !CFG.USER_ID) return null;

  try {
    const resp = await fetch(
      `${CFG.BILLING_API_URL}/api/v1/billing/balance?user_id=${encodeURIComponent(CFG.USER_ID)}`,
      { headers: { 'X-API-Key': CFG.BILLING_API_KEY } }
    );
    const data = await resp.json();
    return data.balance;
  } catch {
    return null;
  }
}

// ═══════════════════════════════════════════
// Polymarket Client
// ═══════════════════════════════════════════

const provider = new JsonRpcProvider(process.env.POLY_RPC || 'https://polygon-bor-rpc.publicnode.com');
const wallet = new Wallet(process.env.POLY_PRIVATE_KEY, provider);

async function getCredentials() {
  if (existsSync(CREDS_FILE)) {
    try {
      const cached = JSON.parse(readFileSync(CREDS_FILE, 'utf8'));
      if (cached.apiKey && cached.secret && cached.passphrase) return cached;
    } catch {}
  }
  console.log('🔑 Deriving Polymarket API credentials...');
  const tempClient = new ClobClient(
    process.env.CLOB_HOST || 'https://clob.polymarket.com',
    parseInt(process.env.CHAIN_ID || '137'),
    wallet
  );
  const creds = await tempClient.createOrDeriveApiKey();
  writeFileSync(CREDS_FILE, JSON.stringify(creds, null, 2));
  return creds;
}

let client;
async function initClient() {
  const creds = await getCredentials();
  client = new ClobClient(
    process.env.CLOB_HOST || 'https://clob.polymarket.com',
    parseInt(process.env.CHAIN_ID || '137'),
    wallet,
    creds,
    parseInt(process.env.SIGNATURE_TYPE || '0'),
    process.env.POLY_WALLET_ADDRESS
  );
  return client;
}

// ═══════════════════════════════════════════
// Market Data
// ═══════════════════════════════════════════

async function getBTCPrice() {
  const resp = await fetch('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT');
  return parseFloat((await resp.json()).price);
}

async function getSlotOpenPrice(ms) {
  try {
    const resp = await fetch(`https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&startTime=${ms}&limit=1`);
    const k = await resp.json();
    return k.length > 0 ? parseFloat(k[0][1]) : null;
  } catch { return null; }
}

async function getMarket(timestamp) {
  const slug = 'btc-updown-5m-' + timestamp;
  try {
    const resp = await fetch('https://gamma-api.polymarket.com/markets?slug=' + slug);
    const data = await resp.json();
    if (!data.length) return null;
    let ids = data[0].clobTokenIds;
    if (typeof ids === 'string') ids = JSON.parse(ids);
    return { question: data[0].question, upTokenId: ids[0], downTokenId: ids[1], closed: data[0].closed };
  } catch { return null; }
}

// ═══════════════════════════════════════════
// Trading Logic
// ═══════════════════════════════════════════

function ts() { return new Date().toISOString().slice(11, 19); }

function logTrade(data) {
  let trades = [];
  try { trades = JSON.parse(readFileSync(CFG.LOG_FILE, 'utf8')); } catch {}
  trades.push({ ...data, ts: new Date().toISOString() });
  writeFileSync(CFG.LOG_FILE, JSON.stringify(trades, null, 2));
}

async function run() {
  // Wallet is mandatory
  if (!process.env.POLY_PRIVATE_KEY || !process.env.POLY_WALLET_ADDRESS) {
    console.log('');
    console.log('🎉 Polymarket AutoTrader installed successfully!');
    console.log('');
    console.log('To start trading, you need a dedicated Polygon wallet.');
    console.log('');
    console.log('Set these environment variables (in .env or export):');
    console.log('  POLY_PRIVATE_KEY=your_wallet_private_key');
    console.log('  POLY_WALLET_ADDRESS=0xYourWalletAddress');
    console.log('');
    console.log('⚠️  Use a DEDICATED wallet with limited funds. Do NOT use your main wallet.');
    console.log('');
    process.exit(0);
  }

  await initClient();

  // Check balance — if zero or new user, enter onboarding flow
  const bal = await checkBalance();
  const tokenBal = bal !== null ? `$${bal.toFixed(4)} USDT` : 'N/A';

  if (bal === null || bal <= 0) {
    // Request a short payment link from billing API (8 USDT minimum top-up)
    let paymentUrl = null;
    try {
      const resp = await fetch(`${CFG.BILLING_API_URL}/api/v1/billing/payment-link`, {
        method: 'POST',
        headers: { 'X-API-Key': CFG.BILLING_API_KEY, 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: CFG.USER_ID, amount: 8 }),
      });
      const data = await resp.json();
      if (data.payment_url) paymentUrl = data.payment_url;
    } catch (e) {
      console.error('  ⚠️  Could not generate payment link:', e.message);
    }

    if (paymentUrl) {
      console.log('PAYMENT_REQUIRED');
      console.log(`PAYMENT_URL:${paymentUrl}`);
      console.log('PAYMENT_AMOUNT:8 USDT');
      console.log('PAYMENT_NETWORK:BNB Chain');
      console.log('PAYMENT_INFO:Polymarket AutoTrader installed! First top-up: 8 USDT = 8000 trades (0.001 USDT/trade). Click to pay with BNB Chain USDT. After payment, run bot again to start trading.');
    } else {
      console.log('ERROR:Could not generate payment link. Check billing configuration.');
    }
    process.exit(0);
  }

  console.log('');
  console.log('╔══════════════════════════════════════════════════════╗');
  console.log('║     🚀 Polymarket AutoTrader — BTC 5-Min Bot       ║');
  console.log('╠══════════════════════════════════════════════════════╣');
  console.log(`║  Trade Size:  $${CFG.TRADE_SIZE_USD}  |  Max Ask: $${CFG.MAX_ASK_PRICE}             ║`);
  console.log(`║  Min Move:    $${CFG.MIN_BTC_MOVE}  |  Strong:  $${CFG.STRONG_BTC_MOVE}            ║`);
  console.log(`║  Risk Limit:  -$${CFG.MAX_LOSS_SESSION} session  |  ${CFG.MAX_TRADES_PER_HOUR} trades/hr    ║`);
  console.log(`║  Tokens:      ${tokenBal.padEnd(39)}║`);
  console.log(`║  Wallet:      ${wallet.address.slice(0, 20)}...     ║`);
  console.log('╚══════════════════════════════════════════════════════╝');
  console.log('');

  let state = {
    currentSlot: 0,
    openPrice: null,
    tradedThisSlot: false,
    hourlyTrades: 0,
    hourStart: Math.floor(Date.now() / 3600000),
    sessionCost: 0,
    totalTrades: 0,
  };

  while (true) {
    try {
      const now = Math.floor(Date.now() / 1000);
      const slotStart = Math.floor(now / 300) * 300;
      const timeLeft = slotStart + 300 - now;
      const elapsed = now - slotStart;

      // Reset hourly counter
      const thisHour = Math.floor(Date.now() / 3600000);
      if (thisHour !== state.hourStart) {
        state.hourlyTrades = 0;
        state.hourStart = thisHour;
      }

      // New slot
      if (state.currentSlot !== slotStart) {
        state.currentSlot = slotStart;
        state.tradedThisSlot = false;
        state.openPrice = await getSlotOpenPrice(slotStart * 1000);
        if (!state.openPrice) state.openPrice = await getBTCPrice();
        console.log(`\n═══ [${ts()}] Slot ${new Date(slotStart * 1000).toISOString().slice(11, 19)} | BTC Open: $${state.openPrice.toFixed(2)} | Trades: ${state.totalTrades} ═══`);
      }

      // Only act in the final window
      if (timeLeft <= CFG.ENTRY_LAST_SEC && timeLeft > CFG.EXIT_BUFFER && !state.tradedThisSlot) {
        const btcPrice = await getBTCPrice();
        const diff = btcPrice - state.openPrice;
        const absDiff = Math.abs(diff);
        const direction = diff >= 0 ? 'Up' : 'Down';

        console.log(`  [${ts()}] ${timeLeft}s left | BTC $${btcPrice.toFixed(2)} | Δ$${diff.toFixed(2)} (${direction})`);

        // Risk checks
        if (state.sessionCost >= CFG.MAX_LOSS_SESSION) {
          console.log('  ⛔ Session loss limit reached. Stopping.');
          break;
        }
        if (state.hourlyTrades >= CFG.MAX_TRADES_PER_HOUR) {
          console.log('  ⛔ Hourly trade limit reached.');
          await sleep(5000);
          continue;
        }

        // TRADE DECISION
        if (absDiff >= CFG.MIN_BTC_MOVE) {
          // ═══ BILLING: Charge 1 token before trading ═══
          const billing = await checkAndCharge();
          if (!billing.success) {
            console.log('  ⏸️  Trade skipped — please top up tokens');
            state.tradedThisSlot = true; // Don't retry this slot
            await sleep(5000);
            continue;
          }

          const market = await getMarket(slotStart);
          if (!market || market.closed) {
            console.log('  Market unavailable');
          } else {
            const tokenId = direction === 'Up' ? market.upTokenId : market.downTokenId;
            const book = await client.getOrderBook(tokenId);
            const asks = (book.asks || []).map(a => ({ price: +a.price, size: +a.size }));

            if (asks.length === 0) {
              console.log(`  ⏭️ No asks for ${direction}`);
            } else {
              const bestAsk = asks[0];

              if (bestAsk.price <= CFG.MAX_ASK_PRICE) {
                const isStrong = absDiff >= CFG.STRONG_BTC_MOVE;
                const tradeUSD = isStrong ? CFG.TRADE_SIZE_USD * 2 : CFG.TRADE_SIZE_USD;
                const shares = Math.floor(tradeUSD / bestAsk.price);
                const cost = shares * bestAsk.price;
                const profit = shares * (1 - bestAsk.price);
                const roi = ((1 - bestAsk.price) / bestAsk.price * 100).toFixed(1);

                console.log(`  🎯 ${direction} ${isStrong ? '(STRONG) ' : ''}| ${shares} shares @ $${bestAsk.price} | Cost $${cost.toFixed(2)} | +$${profit.toFixed(2)} (${roi}%)`);

                try {
                  const order = await client.createOrder({
                    tokenID: tokenId,
                    price: bestAsk.price,
                    size: shares,
                    side: Side.BUY,
                  });

                  const result = await client.postOrder(order, OrderType.FOK);

                  if (result?.success || result?.status === 'matched') {
                    const actualCost = parseFloat(result.takingAmount || '0');
                    const actualShares = parseFloat(result.makingAmount || '0');

                    state.tradedThisSlot = true;
                    state.hourlyTrades++;
                    state.totalTrades++;
                    state.sessionCost += actualCost;

                    console.log(`  ✅ FILLED! Cost: $${actualCost.toFixed(2)} | Shares: ${actualShares.toFixed(1)}`);

                    logTrade({
                      slot: slotStart,
                      direction,
                      askPrice: bestAsk.price,
                      shares: actualShares,
                      cost: actualCost,
                      btcDiff: diff,
                      btcPrice,
                      openPrice: state.openPrice,
                      timeLeft,
                      strong: isStrong,
                      tokenCharged: true,
                    });
                  } else {
                    console.log(`  ⚠️ Not filled: ${JSON.stringify(result).slice(0, 100)}`);
                  }
                } catch (e) {
                  console.log(`  ❌ Trade error: ${e.message?.slice(0, 80)}`);
                }
              } else {
                console.log(`  ⏭️ Ask $${bestAsk.price} > max $${CFG.MAX_ASK_PRICE}`);
              }
            }
          }
        }
      } else if (elapsed % 30 < 2 && timeLeft > CFG.ENTRY_LAST_SEC) {
        const btcPrice = await getBTCPrice();
        const diff = btcPrice - (state.openPrice || btcPrice);
        process.stdout.write(`\r  [${ts()}] wait ${timeLeft}s | BTC $${btcPrice.toFixed(0)} Δ$${diff.toFixed(0)} | trades: ${state.totalTrades}  `);
      }

    } catch (e) {
      console.log(`\n❌ ${e.message?.slice(0, 100)}`);
    }

    const now2 = Math.floor(Date.now() / 1000);
    const tl = (Math.ceil(now2 / 300) * 300) - now2;
    const interval = tl <= CFG.ENTRY_LAST_SEC ? 2000 : 5000;
    await sleep(interval);
  }
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// ═══════════════════════════════════════════
// CLI Commands
// ═══════════════════════════════════════════

const cmd = process.argv[2];

if (cmd === 'stats') {
  try {
    const trades = JSON.parse(readFileSync(CFG.LOG_FILE, 'utf8'));
    console.log(`\n📊 Trade Statistics (${trades.length} trades)\n`);
    let totalCost = 0, totalShares = 0, strongCount = 0;
    for (const t of trades) {
      totalCost += t.cost || 0;
      totalShares += t.shares || 0;
      if (t.strong) strongCount++;
    }
    console.log(`Total Cost:    $${totalCost.toFixed(2)}`);
    console.log(`Total Shares:  ${totalShares.toFixed(0)}`);
    console.log(`Avg Price:     $${(totalCost / totalShares).toFixed(3)}/share`);
    console.log(`Strong Trades: ${strongCount}/${trades.length}`);
    console.log(`If all win:    +$${(totalShares - totalCost).toFixed(2)} profit`);
    console.log(`\nLast 5 trades:`);
    for (const t of trades.slice(-5)) {
      console.log(`  ${t.ts?.slice(0, 19)} | ${t.direction} Δ$${t.btcDiff?.toFixed(0)} | ${t.shares} @ $${t.askPrice} | $${t.cost?.toFixed(2)} ${t.strong ? '⚡' : ''}`);
    }
  } catch { console.log('No trades yet.'); }

} else if (cmd === 'balance') {
  const bal = await checkBalance();
  if (bal !== null) {
    console.log(`\n💰 Balance: $${bal.toFixed(4)} USDT (${(bal / CFG.TOKEN_COST_PER_TRADE).toFixed(0)} trades remaining)\n`);
  } else {
    console.log('\n⚠️  Could not fetch balance. Check billing config.\n');
  }

} else {
  await run();
}
