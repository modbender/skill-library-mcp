/**
 * 리스크 관리 모듈 (riskManager.js)
 * - 잔고 확인 및 주문 가능 여부 판단
 * - 최소 주문 금액(min_total) 필터
 * - 사이징 정책
 */

const { Logger } = require('../execution/upbitClient');
const { loadConfig } = require('../config');

const cfg = loadConfig();

class RiskManager {
    /**
     * 주문 실행 전 리스크 검증
     * @param {Object} upbitClient - UpbitClient 인스턴스
     * @param {Object} event - 처리하려는 이벤트
     */
    async evaluate(upbitClient, event) {
        try {
            // 1. 주문 가능 정보 조회 (orders/chance)
            const chance = await upbitClient.request('GET', '/orders/chance', {}, { market: event.market });

            const bidFee = parseFloat(chance.bid_fee);
            const askFee = parseFloat(chance.ask_fee);
            const krwBalance = parseFloat(chance.bid_account.balance);
            const minTotal = parseFloat(chance.market.bid.min_total); // 최소 주문 금액 (KRW)

            if (event.type === 'BUY_SIGNAL') {
                const budget = event.budgetKRW || 10000; // 기본 1만원 또는 설정값

                // 잔고 부족 확인
                if (krwBalance < budget) {
                    return { allow: false, reason: 'INSUFFICIENT_BALANCE', detail: `잔고부족: ${krwBalance.toLocaleString()} KRW` };
                }

                // 최소 주문 금액 미달 확인
                if (budget < minTotal) {
                    return { allow: false, reason: 'UNDER_MIN_TOTAL', detail: `최소주문금액 미달: ${budget} < ${minTotal}` };
                }

                return { allow: true, budgetKRW: budget, fee: bidFee };
            }

            if (
                event.type === 'TARGET_HIT' ||
                event.type === 'STOPLOSS_HIT' ||
                event.type === 'TRAILING_STOP_HIT' ||
                event.type === 'TAKEPROFIT_HARD' ||
                event.type === 'SELL_PRESSURE_HIT'
            ) {
                // 매도의 경우 보유 수량 확인 (accounts)
                const accounts = await upbitClient.request('GET', '/accounts');
                const currency = event.market.split('-')[1];
                const asset = accounts.find(a => a.currency === currency);

                if (!asset || parseFloat(asset.balance) <= 0) {
                    return { allow: false, reason: 'NO_ASSET_TO_SELL' };
                }

                const fullVol = parseFloat(asset.balance);

                // Optional: partial sell for SELL_PRESSURE_HIT (reduce-only)
                let ratio = 1;
                if (event.type === 'SELL_PRESSURE_HIT') {
                    const r = Number(cfg.trading?.aggressive?.pressure?.sellReduceRatio ?? 1);
                    if (Number.isFinite(r) && r > 0 && r < 1) ratio = r;
                }

                let volume = fullVol * ratio;
                // Sell min_total guard (best-effort). Upbit /orders/chance exposes ask.min_total.
                const minSellTotal = parseFloat(chance?.market?.ask?.min_total ?? chance?.market?.bid?.min_total ?? minTotal);
                const current = Number(event?.meta?.current ?? event?.payload?.price ?? 0);
                if (Number.isFinite(current) && current > 0 && Number.isFinite(minSellTotal) && minSellTotal > 0) {
                    const est = current * volume;
                    if (est < minSellTotal) {
                        const fullEst = current * fullVol;
                        if (fullEst >= minSellTotal) {
                            // fallback: sell full position if partial would be rejected
                            volume = fullVol;
                            ratio = 1;
                        } else {
                            return { allow: false, reason: 'UNDER_MIN_TOTAL_SELL', detail: `추정매도금액 미달: ${est} < ${minSellTotal}` };
                        }
                    }
                }

                // Optional local minimum for pressure-based reduce sells
                if (event.type === 'SELL_PRESSURE_HIT') {
                    const localMin = Number(cfg.trading?.aggressive?.pressure?.sellReduceMinKrw ?? 0);
                    if (Number.isFinite(localMin) && localMin > 0 && Number.isFinite(current) && current > 0) {
                        const est = current * volume;
                        if (est < localMin) {
                            const fullEst = current * fullVol;
                            if (fullEst >= localMin) {
                                volume = fullVol;
                                ratio = 1;
                            } else {
                                return { allow: false, reason: 'UNDER_LOCAL_MIN_SELL', detail: `설정 최소매도금액 미달: ${est} < ${localMin}` };
                            }
                        }
                    }
                }

                return { allow: true, volume, fee: askFee, ratio };
            }

            return { allow: false, reason: 'UNKNOWN_EVENT_TYPE' };
        } catch (err) {
            Logger.error(`Risk Evaluation Failed: ${err.message}`);
            return { allow: false, reason: 'ERROR', detail: err.message };
        }
    }
}

module.exports = new RiskManager();
