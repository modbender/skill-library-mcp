const { request } = require('./api-client');

/**
 * 업비트 공용 시세 조회 모듈 (market.js)
 */

const BASE_URL = 'https://api.upbit.com/v1';

/**
 * 마켓 코드 조회 (전체 종목 리스트)
 */
async function getMarkets(filterKRW = true) {
    const data = await request({
        method: 'get',
        url: `${BASE_URL}/market/all?isDetails=false`
    });

    return filterKRW ? data.filter(m => m.market.startsWith('KRW-')) : data;
}

/**
 * 캔들 조회 (통합 함수)
 */
async function getCandles(unit, market, count = 1, subUnit = 1) {
    let url = `${BASE_URL}/candles/${unit}`;
    if (unit === 'minutes') {
        url += `/${subUnit}`;
    }

    return request({
        method: 'get',
        url,
        params: { market, count }
    });
}

/**
 * 현재가 정보 조회 (Ticker)
 */
async function getTickers(markets) {
    const marketsStr = Array.isArray(markets) ? markets.join(',') : markets;
    return request({
        method: 'get',
        url: `${BASE_URL}/ticker`,
        params: { markets: marketsStr }
    });
}

/**
 * 호가 조회 (Orderbook)
 */
async function getOrderbooks(markets) {
    const marketsStr = Array.isArray(markets) ? markets.join(',') : markets;
    return request({
        method: 'get',
        url: `${BASE_URL}/orderbook`,
        params: { markets: marketsStr }
    });
}

module.exports = {
    getMarkets,
    getCandles,
    getTickers,
    getOrderbooks
};

// 테스트 코드
if (require.main === module) {
    (async () => {
        try {
            console.log('--- Market Module Test ---');
            const btcTicker = await getTickers('KRW-BTC');
            console.log('BTC Ticker:', btcTicker[0].trade_price);

            const krwMarkets = await getMarkets();
            console.log('KRW Markets Count:', krwMarkets.length);
        } catch (err) {
            console.error('Test Failed:', err.message);
        }
    })();
}
