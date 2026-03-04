const fs = require('fs');
const path = require('path');
const OKXClient = require('../lib/okx-client');

const DATA_ROOT = '/root/.openclaw/workspace/okx_data';
const SNAPSHOT_DIR = path.join(DATA_ROOT, 'snapshots');

function getConfig() {
    const configPath = path.join(DATA_ROOT, 'config.json');
    if (fs.existsSync(configPath)) return JSON.parse(fs.readFileSync(configPath, 'utf8'));
    return {
        apiKey: process.env.OKX_API_KEY,
        secretKey: process.env.OKX_SECRET_KEY,
        passphrase: process.env.OKX_PASSPHRASE,
        isSimulation: process.env.OKX_IS_SIMULATION === 'true'
    };
}

function getGridSettings() {
    const p = path.join(DATA_ROOT, 'grid_settings.json');
    return fs.existsSync(p) ? JSON.parse(fs.readFileSync(p, 'utf8')) : {};
}

async function getAllFills(client, instId) {
    let all = [];
    let after = '';
    const oneDayAgo = Date.now() - 24 * 60 * 60 * 1000;
    for (let i = 0; i < 50; i++) {
        const params = { instId, limit: '100' };
        if (after) params.after = after;
        const fills = await client.request('/trade/fills', 'GET', params);
        if (!fills || fills.length === 0) break;
        const recent = fills.filter(f => parseInt(f.fillTime || f.ts) > oneDayAgo);
        all.push(...recent);
        if (recent.length < fills.length || fills.length < 100) break;
        after = fills[fills.length - 1].billId;
    }
    return all;
}

async function run() {
    try {
        const client = new OKXClient(getConfig());
        const settings = getGridSettings();
        const instIds = [...new Set(Object.values(settings).map(s => s.instId))];

        // 1. Account balance
        const bal = await client.request('/account/balance', 'GET', {});
        const assets = {};
        bal[0].details.forEach(d => {
            if (parseFloat(d.eq) > 0) {
                assets[d.ccy] = {
                    equity: parseFloat(d.eq),
                    available: parseFloat(d.availBal),
                    frozen: parseFloat(d.frozenBal),
                    usd: parseFloat(d.eqUsd),
                    spotUpl: parseFloat(d.spotUpl || 0),
                    spotUplRatio: parseFloat(d.spotUplRatio || 0)
                };
            }
        });
        const totalEquityUsd = parseFloat(bal[0].totalEq);

        // 2. Tickers
        const prices = {};
        for (const instId of instIds) {
            const ticker = await client.request('/market/ticker', 'GET', { instId });
            if (ticker && ticker[0]) prices[instId] = parseFloat(ticker[0].last);
        }

        // 3. 24h fills summary per instrument
        const tradingSummary = {};
        for (const instId of instIds) {
            const fills = await getAllFills(client, instId);
            let buyVol = 0, buyVal = 0, sellVol = 0, sellVal = 0, fees = 0;
            fills.forEach(f => {
                const px = parseFloat(f.fillPx);
                const sz = parseFloat(f.fillSz);
                fees += parseFloat(f.fee || 0);
                if (f.side === 'buy') { buyVol += sz; buyVal += px * sz; }
                else { sellVol += sz; sellVal += px * sz; }
            });
            tradingSummary[instId] = {
                fills: fills.length,
                buyCount: fills.filter(f => f.side === 'buy').length,
                sellCount: fills.filter(f => f.side === 'sell').length,
                buyVol: parseFloat(buyVol.toFixed(8)),
                buyVal: parseFloat(buyVal.toFixed(2)),
                buyAvg: buyVol > 0 ? parseFloat((buyVal / buyVol).toFixed(2)) : 0,
                sellVol: parseFloat(sellVol.toFixed(8)),
                sellVal: parseFloat(sellVal.toFixed(2)),
                sellAvg: sellVol > 0 ? parseFloat((sellVal / sellVol).toFixed(2)) : 0,
                netVol: parseFloat((buyVol - sellVol).toFixed(8)),
                netUsdt: parseFloat((sellVal - buyVal).toFixed(2)),
                fees: parseFloat(fees.toFixed(4))
            };
        }

        // 4. Pending orders count
        const pendingCounts = {};
        for (const instId of instIds) {
            const pending = await client.request('/trade/orders-pending', 'GET', { instId });
            pendingCounts[instId] = Array.isArray(pending) ? pending.length : 0;
        }

        // 5. Build snapshot
        const now = new Date();
        const dateStr = now.toISOString().substring(0, 10);
        const snapshot = {
            timestamp: now.toISOString(),
            totalEquityUsd,
            assets,
            prices,
            tradingSummary24h: tradingSummary,
            pendingOrders: pendingCounts,
            gridSettings: settings
        };

        // 6. Compare with previous snapshot
        const files = fs.existsSync(SNAPSHOT_DIR) ? fs.readdirSync(SNAPSHOT_DIR).filter(f => f.endsWith('.json')).sort() : [];
        let delta = null;
        if (files.length > 0) {
            const prev = JSON.parse(fs.readFileSync(path.join(SNAPSHOT_DIR, files[files.length - 1]), 'utf8'));
            delta = {
                prevDate: files[files.length - 1].replace('.json', ''),
                equityChange: parseFloat((totalEquityUsd - prev.totalEquityUsd).toFixed(2)),
                equityChangePct: parseFloat(((totalEquityUsd - prev.totalEquityUsd) / prev.totalEquityUsd * 100).toFixed(3)),
                assetChanges: {}
            };
            for (const [ccy, cur] of Object.entries(assets)) {
                if (prev.assets && prev.assets[ccy]) {
                    delta.assetChanges[ccy] = {
                        equityChange: parseFloat((cur.equity - prev.assets[ccy].equity).toFixed(8)),
                        usdChange: parseFloat((cur.usd - prev.assets[ccy].usd).toFixed(2))
                    };
                }
            }
            snapshot.delta = delta;
        }

        // 7. Save
        if (!fs.existsSync(SNAPSHOT_DIR)) fs.mkdirSync(SNAPSHOT_DIR, { recursive: true });
        fs.writeFileSync(path.join(SNAPSHOT_DIR, `${dateStr}.json`), JSON.stringify(snapshot, null, 2));

        // 8. Print summary
        console.log(`📸 账户快照 ${dateStr}`);
        console.log(`💰 总权益: $${totalEquityUsd.toFixed(2)}`);
        for (const [ccy, a] of Object.entries(assets)) {
            console.log(`  ${ccy}: ${a.equity} ($${a.usd.toFixed(2)}) 浮盈: $${a.spotUpl.toFixed(2)}`);
        }
        console.log(`\n📊 24h 交易汇总:`);
        for (const [instId, s] of Object.entries(tradingSummary)) {
            console.log(`  ${instId}: ${s.fills}笔 (买${s.buyCount}/卖${s.sellCount}) 净USDT: ${s.netUsdt > 0 ? '+' : ''}${s.netUsdt} 手续费返佣: ${s.fees}`);
        }
        if (delta) {
            console.log(`\n📈 vs ${delta.prevDate}:`);
            console.log(`  权益变化: ${delta.equityChange > 0 ? '+' : ''}$${delta.equityChange} (${delta.equityChangePct > 0 ? '+' : ''}${delta.equityChangePct}%)`);
        }
        console.log(`\n✅ 已保存到 ${SNAPSHOT_DIR}/${dateStr}.json`);

    } catch (e) {
        console.error('Error:', e.message);
    }
}

run();
