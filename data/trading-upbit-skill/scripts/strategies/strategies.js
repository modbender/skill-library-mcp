/**
 * 매매 전략 모듈
 */

/**
 * 변동성 돌파 전략 (Volatility Breakout Strategy)
 * @param {Object} currentCandle - 현재가 포함된 캔들 { open, high, low, close }
 * @param {number} prevRange - 전일 고가 - 전일 저가
 * @param {number} k - 변동성 계수 (기본 0.5)
 */
function volatilityBreakout(currentCandle, prevRange, k = 0.5) {
    const targetPrice = currentCandle.open + (prevRange * k);
    return {
        targetPrice,
        signal: currentCandle.close > targetPrice ? 'BUY' : 'HOLD',
        isBreakout: currentCandle.high > targetPrice,
        meta: { prevRange, k }
    };
}

module.exports = {
    volatilityBreakout
};
