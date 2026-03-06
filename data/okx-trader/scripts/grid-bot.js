const fs = require('fs');
const path = require('path');
const OKXClient = require('../lib/okx-client');

/**
 * OKX Grid Bot Script - Optimized v2.2
 * Improvements: Path normalization, Batch API execution, Improved logging.
 */

const botType = process.argv[2] || 'main';

function getPaths() {
    const dataRoot = '/root/.openclaw/workspace/okx_data';
    const skillRoot = path.resolve(__dirname, '..');
    
    return {
        auth: path.resolve(dataRoot, 'config.json'),
        settings: path.resolve(dataRoot, 'grid_settings.json'),
        auditLog: path.resolve(dataRoot, 'logs/rescale_audit.json')
    };
}

function loadJSON(p) {
    if (fs.existsSync(p)) return JSON.parse(fs.readFileSync(p, 'utf8'));
    return null;
}

async function main() {
    const paths = getPaths();
    const authData = loadJSON(paths.auth);
    const settings = loadJSON(paths.settings);

    if (!authData || !settings) {
        console.error(`Missing config at ${paths.auth} or ${paths.settings}`);
        process.exit(1);
    }

    const client = new OKXClient(authData);
    const CONFIG = settings[botType];

    if (!CONFIG) {
        console.error(`Bot type ${botType} not found in settings`);
        process.exit(1);
    }

    let auditEntry = { status: 'success', info: '' };

    try {
        // 1. Concurrent Fetch: Ticker, Positions, and Pending Orders
        const [ticker, posData, pendingOrders] = await Promise.all([
            client.request('/market/ticker', 'GET', { instId: CONFIG.instId }),
            client.request('/account/positions', 'GET', { instId: CONFIG.instId }),
            client.request('/trade/orders-pending', 'GET', { instId: CONFIG.instId })
        ]);

        const currentPrice = parseFloat(ticker[0].last);
        let currentPos = 0, avgPx = 0;
        if (posData && posData.length > 0) {
            const pos = posData.find(p => p.instId === CONFIG.instId);
            if (pos) {
                currentPos = parseFloat(pos.pos);
                avgPx = parseFloat(pos.avgPx);
            }
        }

        // 2. Trailing/Rescale Logic
        const range = CONFIG.maxPrice - CONFIG.minPrice;
        const threshold = range * (CONFIG.trailingPercent || 0.1);
        
        if (currentPrice > CONFIG.maxPrice - threshold || currentPrice < CONFIG.minPrice + threshold) {
            console.log(`[${botType}] Rescaling... Price: ${currentPrice}`);
            
            const toCancel = pendingOrders
                .filter(o => Math.abs(parseFloat(o.sz) - CONFIG.sizePerGrid) < 0.000001)
                .map(o => ({ instId: CONFIG.instId, ordId: o.ordId }));
            
            if (toCancel.length > 0) {
                // Batch cancel
                await Promise.all(toCancel.map(o => client.request('/trade/cancel-order', 'POST', JSON.stringify(o))));
            }

            const newMin = Math.round(currentPrice - (range / 2));
            const newMax = Math.round(currentPrice + (range / 2));
            
            settings[botType].minPrice = newMin;
            settings[botType].maxPrice = newMax;
            fs.writeFileSync(paths.settings, JSON.stringify(settings, null, 4));
            
            CONFIG.minPrice = newMin;
            CONFIG.maxPrice = newMax;
            auditEntry.rescaled = true;
        }

        // 3. Grid Calculation
        const step = (CONFIG.maxPrice - CONFIG.minPrice) / (CONFIG.gridCount - 1);
        const grids = Array.from({ length: CONFIG.gridCount }, (_, i) => CONFIG.minPrice + (i * step));

        const activeOrders = new Map();
        pendingOrders.forEach(o => {
            if (Math.abs(parseFloat(o.sz) - CONFIG.sizePerGrid) < 0.000001) {
                activeOrders.set(Math.floor(parseFloat(o.px)), o.ordId);
            }
        });

        const buffer = botType === 'micro' ? 0.001 : 0.003;
        const isOverloaded = CONFIG.maxPosition && Math.abs(currentPos) >= CONFIG.maxPosition;
        const minProfitPx = CONFIG.minProfitGap ? (avgPx * (1 + CONFIG.minProfitGap)) : 0;

        const ordersToPlace = [];
        let protectedSell = 0;

        for (const price of grids) {
            const diff = (price - currentPrice) / currentPrice;
            let side = '';
            if (diff > buffer) side = 'sell';
            else if (diff < -buffer) side = 'buy';
            else continue;

            const priceKey = Math.floor(price);
            if (!activeOrders.has(priceKey)) {
                if (side === 'buy' && isOverloaded) continue;
                if (side === 'sell' && currentPos > 0 && price < minProfitPx) {
                    protectedSell++;
                    continue;
                }

                ordersToPlace.push({
                    instId: CONFIG.instId,
                    tdMode: 'cash',
                    side: side,
                    ordType: 'limit',
                    px: price.toFixed(1),
                    sz: CONFIG.sizePerGrid.toString()
                });
            }
        }

        // 4. Batch Order Placement (with small delay between chunks to avoid rate limit if needed)
        let placedBuy = 0, placedSell = 0;
        if (ordersToPlace.length > 0) {
            console.log(`[${botType}] Placing ${ordersToPlace.length} orders...`);
            const results = await Promise.all(ordersToPlace.map(ord => 
                client.request('/trade/order', 'POST', JSON.stringify(ord))
            ));
            
            ordersToPlace.forEach(o => { if (o.side === 'buy') placedBuy++; else placedSell++; });
        }

        auditEntry.info = `Pos:${currentPos}, Px:${currentPrice}, B:${placedBuy}, S:${placedSell}, Prot:${protectedSell}`;
        console.log(`[${botType}] ${auditEntry.info}`);

        // Persistent Audit Logging
        try {
            let logs = fs.existsSync(paths.auditLog) ? JSON.parse(fs.readFileSync(paths.auditLog, 'utf8')) : [];
            logs.push({ ts: new Date().toISOString(), botType, ...auditEntry });
            fs.writeFileSync(paths.auditLog, JSON.stringify(logs.slice(-200), null, 2));
        } catch (e) {}

    } catch (e) {
        console.error(`[${botType}] Error:`, e.message);
    }
}

main();
