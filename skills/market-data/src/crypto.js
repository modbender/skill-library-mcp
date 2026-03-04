import https from 'https';

const COINGECKO_API_HOST = 'api.coingecko.com';
const COINGECKO_PATH_PREFIX = '/api/v3';

/**
 * Fetches historical price data (candles) for a crypto token from CoinGecko.
 * @param {Object} params
 * @param {string} params.token - The crypto token ID (e.g., 'bitcoin', 'solana').
 * @param {string} params.days - Number of days of data (default: '100').
 * @param {string} params.currency - Target currency (default: 'usd').
 * @returns {Promise<Array<number>>} Array of closing prices.
 */
export async function get_crypto_history({ token, days = '100', currency = 'usd' }) {
  return new Promise((resolve, reject) => {
    const symbolMap = {
      'btc': 'bitcoin',
      'eth': 'ethereum',
      'sol': 'solana',
      'xrp': 'ripple',
      'doge': 'dogecoin',
      'btc-usd': 'bitcoin',
      'sol-usd': 'solana'
    };
    
    const tokenId = symbolMap[token.toLowerCase()] || token.toLowerCase();
    const path = `${COINGECKO_PATH_PREFIX}/coins/${tokenId}/market_chart?vs_currency=${currency}&days=${days}&interval=daily`;
    
    const options = {
      hostname: COINGECKO_API_HOST,
      path: path,
      method: 'GET',
      headers: {
        'User-Agent': 'MarketMind/1.0'
      }
    };

    https.get(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          if (!json.prices) {
            resolve([]); // Return empty if error or not found
            return;
          }
          // CoinGecko returns [timestamp, price]. We just need prices.
          const closes = json.prices.map(p => p[1]);
          resolve(closes);
        } catch (e) {
          resolve([]);
        }
      });
    }).on('error', (e) => resolve([]));
  });
}

/**
 * Fetches current crypto price (existing function).
 */
export async function get_crypto_price({ token, currency = 'usd' }) {
    // ... (existing implementation) ...
    return new Promise((resolve, reject) => {
        // CoinGecko requires the "ID" (e.g. bitcoin) not symbol (BTC).
        const symbolMap = {
          'btc': 'bitcoin',
          'eth': 'ethereum',
          'sol': 'solana',
          'xrp': 'ripple',
          'doge': 'dogecoin',
          'btc-usd': 'bitcoin',
          'sol-usd': 'solana'
        };
        
        const tokenId = symbolMap[token.toLowerCase()] || token.toLowerCase();
        
        const path = `${COINGECKO_PATH_PREFIX}/simple/price?ids=${tokenId}&vs_currencies=${currency}&include_24hr_vol=true&include_24hr_change=true&include_last_updated_at=true`;
        
        const options = {
          hostname: COINGECKO_API_HOST,
          path: path,
          method: 'GET',
          headers: {
            'User-Agent': 'MarketMind/1.0'
          }
        };
    
        https.get(options, (res) => {
          let data = '';
    
          res.on('data', (chunk) => {
            data += chunk;
          });
    
          res.on('end', () => {
            try {
              const parsedData = JSON.parse(data);
              
              if (!parsedData[tokenId]) {
                 resolve(`No data found for crypto token: ${token} (tried ID: ${tokenId}). Try using the full name (e.g., 'bitcoin' instead of 'btc').`);
                 return;
              }
    
              const info = parsedData[tokenId];
              const price = info[currency];
              const change24h = info[`${currency}_24h_change`];
              const vol24h = info[`${currency}_24h_vol`];
              const lastUpdated = new Date(info.last_updated_at * 1000).toISOString();
    
              let output = `Crypto Data for ${tokenId.toUpperCase()} (${currency.toUpperCase()}):\n`;
              output += `Price:        ${price}\n`;
              output += `24h Change:   ${change24h ? change24h.toFixed(2) + '%' : 'N/A'}\n`;
              output += `24h Volume:   ${vol24h ? vol24h.toLocaleString() : 'N/A'}\n`;
              output += `Last Updated: ${lastUpdated}\n`;
    
              resolve(output);
    
            } catch (error) {
              resolve(`Error parsing crypto data for ${token}: ${error.message}`);
            }
          });
    
        }).on('error', (err) => {
          resolve(`Network error fetching crypto ${token}: ${err.message}`);
        });
      });
}
