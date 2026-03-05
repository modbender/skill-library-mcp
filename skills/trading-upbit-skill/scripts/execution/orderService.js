/**
 * 주문 서비스 (orderService.js)
 * - 시장가 매수(Price) / 시장가 매도(Market) 최적화
 * - UpbitClient를 이용한 실제 API 호출
 */

const { Logger } = require('./upbitClient');

class OrderService {
    constructor(upbitClient) {
        this.client = upbitClient;
    }

    /**
     * 시장가 매수 (Entry)
     * @param {string} market - 마켓 코드
     * @param {number} totalKRW - 총 주문 금액
     */
    async placeMarketBuy(market, totalKRW) {
        Logger.info(`[BUY] 시장가 매수 시도: ${market} - ${totalKRW.toLocaleString()} KRW`);

        // 시장가 매수는 ord_type: 'price'
        // volume은 없어야 하며 price가 총 KRW 금액이 됨
        const orderData = {
            market,
            side: 'bid',
            price: totalKRW.toString(),
            ord_type: 'price'
        };

        return this.client.request('POST', '/orders', orderData);
    }

    /**
     * 시장가 매도 (Exit)
     * @param {string} market - 마켓 코드
     * @param {number} volume - 매도 수량
     */
    async placeMarketSell(market, volume) {
        Logger.info(`[SELL] 시장가 매도 시도: ${market} - ${volume}`);

        // 시장가 매도는 ord_type: 'market'
        // price는 없어야 하며 volume이 수량이 됨
        const orderData = {
            market,
            side: 'ask',
            volume: volume.toString(),
            ord_type: 'market'
        };

        return this.client.request('POST', '/orders', orderData);
    }

    /**
     * 주문 조회
     */
    async getOrder(uuid) {
        return this.client.request('GET', '/order', {}, { uuid });
    }

    /**
     * 주문 취소
     */
    async cancelOrder(uuid) {
        return this.client.request('DELETE', '/order', {}, { uuid });
    }
}

module.exports = OrderService;
