const { request } = require("./client");
const { UpbitError } = require("./errors");

function requireOpt(name, v) {
  if (v === undefined || v === null || v === "") throw new UpbitError(`Missing required option: --${name}`);
}

const upbit = {
  async listTradingPairs({ is_details = false } = {}) {
    return request({
      path: "/v1/market/all",
      query: { is_details }
    });
  },

  async listCandles(type, opts = {}) {
    const market = opts.market;
    requireOpt("market", market);

    const count = opts.count ?? 200;
    const to = opts.to;

    let path = "";
    const query = { market, count, to };

    switch (type) {
      case "seconds":
        path = "/v1/candles/seconds";
        break;

      case "minutes": {
        const unit = Number(opts.unit ?? 1);
        const allowed = new Set([1, 3, 5, 10, 15, 30, 60, 240]);
        if (!allowed.has(unit)) throw new UpbitError("Invalid --unit for minutes. Allowed: 1,3,5,10,15,30,60,240");
        path = `/v1/candles/minutes/${unit}`;
        break;
      }

      case "days":
        path = "/v1/candles/days";
        if (opts.converting_price_unit) query.converting_price_unit = opts.converting_price_unit;
        break;

      case "weeks":
        path = "/v1/candles/weeks";
        break;

      case "months":
        path = "/v1/candles/months";
        break;

      case "years":
        path = "/v1/candles/years";
        break;

      default:
        throw new UpbitError(`Unknown candle type: ${type}`);
    }

    return request({ path, query });
  },

  async recentTrades({ market, count = 50, to, cursor, daysAgo } = {}) {
    requireOpt("market", market);
    return request({
      path: "/v1/trades/ticks",
      query: { market, count, to, cursor, daysAgo }
    });
  },

  async tickersByPairs({ markets } = {}) {
    requireOpt("markets", markets);
    return request({
      path: "/v1/ticker",
      query: { markets }
    });
  },

  async tickersByMarket({ quote } = {}) {
    requireOpt("quote", quote);
    return request({
      path: "/v1/ticker/all",
      query: { quote_currencies: quote }
    });
  },

  async orderbooks({ markets, level, count } = {}) {
    requireOpt("markets", markets);
    return request({
      path: "/v1/orderbook",
      query: { markets, level, count }
    });
  }
};

module.exports = { upbit };

