import https from 'https';
const POLYGON_API_KEY = 'QR_WJk5DtOe_UU7ARlvcAASbX4rkuJCS';

export { get_crypto_price, get_crypto_history } from './crypto.js';
export { fetch_economic_calendar } from './calendar.js';
export { get_news_headlines } from './news.js';

/**
 * Fetches OHLCV data for a stock ticker using Polygon.io.
 * @param {Object} params
 * @param {string} params.ticker - The stock ticker symbol (e.g., AAPL, TSLA).
 * @param {string} [params.period1] - Start date (YYYY-MM-DD). Defaults to ~100 days ago.
 * @param {string} [params.period2] - End date (YYYY-MM-DD). Defaults to today.
 * @returns {Promise<string>} A formatted string of OHLCV data.
 */
export async function get_stock_price({ ticker, period1, period2 }) {
  return new Promise((resolve, reject) => {
    // Polygon free tier has a delay. We query up to yesterday.
    const today = new Date();
    today.setDate(today.getDate() - 1); // Set to yesterday
    const to = period2 || today.toISOString().split('T')[0];
    
    const fromDate = new Date(to);
    fromDate.setDate(fromDate.getDate() - 100); // Go back 100 days from 'to' date
    const from = period1 || fromDate.toISOString().split('T')[0];
    
    const url = `https://api.polygon.io/v2/aggs/ticker/${ticker}/range/1/day/${from}/${to}?adjusted=true&sort=asc&limit=500&apiKey=${POLYGON_API_KEY}`;

    https.get(url, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          const parsedData = JSON.parse(data);

          if (parsedData.status !== 'OK' || !parsedData.results) {
            resolve(`Error fetching data for ${ticker} from Polygon: ${parsedData.error || 'No results'}`);
            return;
          }

          if (parsedData.results.length === 0) {
            resolve(`No data found for ${ticker} in the specified range.`);
            return;
          }
          
          let output = `OHLCV Data for ${ticker} (Daily):\n`;
          output += `Date       | Open   | High   | Low    | Close  | Volume\n`;
          output += `-----------|--------|--------|--------|--------|---------\n`;

          // Polygon returns results oldest to newest, so no need to reverse.
          // Let's show the most recent 30 days for brevity.
          const recentResults = parsedData.results; //.slice(-30);
          
          recentResults.forEach(bar => {
            const date = new Date(bar.t).toISOString().split('T')[0];
            const open = bar.o.toFixed(2);
            const high = bar.h.toFixed(2);
            const low = bar.l.toFixed(2);
            const close = bar.c.toFixed(2);
            const volume = bar.v;
            
            output += `${date} | ${open} | ${high} | ${low} | ${close} | ${volume}\n`;
          });
          
          const latestBar = parsedData.results[parsedData.results.length - 1];
          output += `\nLatest Close: ${latestBar.c.toFixed(2)} on ${new Date(latestBar.t).toISOString().split('T')[0]}`;

          resolve(output);
        } catch (error) {
          resolve(`Error parsing Polygon data for ${ticker}: ${error.message}`);
        }
      });
    }).on('error', (err) => {
      resolve(`Network error fetching Polygon ${ticker}: ${err.message}`);
    });
  });
}

