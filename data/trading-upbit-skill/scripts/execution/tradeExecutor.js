/**
 * 통합 매매 실행자 (tradeExecutor.js)
 * - 리스크 관리 확인
 * - 주문 실행 및 상태 전이 (PositionsRepo 활용)
 */

const { Logger } = require('./upbitClient');
const riskManager = require('../risk/riskManager');
const positionsRepo = require('../state/positionsRepo');

function getLastActionTsForMarket(positions, market) {
    let maxTs = 0;
    for (const p of (positions || [])) {
        if (p.market !== market) continue;
        const times = [p?.entry?.openedAt, p?.entry?.createdAt, p?.exit?.closedAt, p?.exit?.triggeredAt].filter(Boolean);
        for (const t of times) {
            const ts = new Date(t).getTime();
            if (Number.isFinite(ts) && ts > maxTs) maxTs = ts;
        }
    }
    return maxTs;
}

class TradeExecutor {
    constructor(orderService, opts = {}) {
        this.orderService = orderService;
        this.dryRun = !!opts.dryRun;
        this.reentryCooldownMs = Number(opts.reentryCooldownMs || 0);
    }

    async execute(event) {
        Logger.info(`[EXECUTOR] start type=${event.type} market=${event.market}`);

        // 1) Risk evaluation (may call Upbit chance/accounts)
        const riskResult = await riskManager.evaluate(this.orderService.client, event);
        if (!riskResult.allow) {
            Logger.warn(`[EXECUTOR] skip reason=${riskResult.reason} detail=${riskResult.detail || ''}`);
            return { ok: false, disposition: 'SKIP', reason: riskResult.reason, detail: riskResult.detail || '' };
        }

        // 2) State transitions + order execution
        if (event.type === 'BUY_SIGNAL') {
            const data = await positionsRepo.load();
            if (data.positions.some(p => p.market === event.market && (p.state === 'OPEN' || p.state === 'ENTRY_PENDING'))) {
                Logger.warn(`[EXECUTOR] skip duplicate position market=${event.market}`);
                return { ok: false, disposition: 'SKIP', reason: 'DUPLICATE_POSITION' };
            }
            // Re-entry cooldown guard (defense-in-depth)
            if (this.reentryCooldownMs > 0) {
                const lastTs = getLastActionTsForMarket(data.positions, event.market);
                const nowTs = Date.now();
                if (lastTs > 0 && (nowTs - lastTs) < this.reentryCooldownMs) {
                    Logger.warn(`[EXECUTOR] skip cooldown market=${event.market} ageMs=${nowTs - lastTs} < cooldownMs=${this.reentryCooldownMs}`);
                    return { ok: false, disposition: 'SKIP', reason: 'REENTRY_COOLDOWN' };
                }
            }


            const pending = await positionsRepo.createEntryPending(event.market, event.meta?.strategy || 'unknown', riskResult.budgetKRW);

            const orderResult = this.dryRun
                ? { uuid: `dry_buy_${Date.now()}`, market: event.market, price: event?.payload?.price, volume: null }
                : await this.orderService.placeMarketBuy(event.market, riskResult.budgetKRW);

            Logger.info(this.dryRun
                ? `[EXECUTOR] DRYRUN buy uuid=${orderResult.uuid}`
                : `[EXECUTOR] buy placed uuid=${orderResult.uuid}`);

            await positionsRepo.updateToOpen(event.market, orderResult);
            return { ok: true, disposition: 'DONE', action: 'BUY', uuid: orderResult.uuid };
        }

        if (event.type === 'TARGET_HIT' || event.type === 'STOPLOSS_HIT' || event.type === 'TRAILING_STOP_HIT' || event.type === 'TAKEPROFIT_HARD' || event.type === 'SELL_PRESSURE_HIT') {
            const isPartial = (event.type === 'SELL_PRESSURE_HIT') && Number(riskResult?.ratio || 1) < 1;

            if (!isPartial) {
                await positionsRepo.updateToExitPending(event.market, event.type);
            }

            const orderResult = this.dryRun
                ? { uuid: `dry_sell_${Date.now()}`, market: event.market, volume: riskResult.volume }
                : await this.orderService.placeMarketSell(event.market, riskResult.volume);

            Logger.info(this.dryRun
                ? `[EXECUTOR] DRYRUN sell uuid=${orderResult.uuid} volume=${riskResult.volume}${isPartial ? ` ratio=${riskResult.ratio}` : ''}`
                : `[EXECUTOR] sell placed uuid=${orderResult.uuid} volume=${riskResult.volume}${isPartial ? ` ratio=${riskResult.ratio}` : ''}`);

            if (isPartial) {
                await positionsRepo.recordPartialExit(event.market, orderResult, event.type, riskResult.ratio, { meta: event.meta || null });
                return { ok: true, disposition: 'DONE_PARTIAL', action: 'SELL_PARTIAL', uuid: orderResult.uuid, ratio: riskResult.ratio };
            }

            await positionsRepo.updateToClosed(event.market, orderResult);
            return { ok: true, disposition: 'DONE', action: 'SELL', uuid: orderResult.uuid };
        }

        return { ok: false, disposition: 'SKIP', reason: 'UNKNOWN_EVENT_TYPE' };
    }
}

module.exports = TradeExecutor;
