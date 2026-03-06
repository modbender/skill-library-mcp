// Alpha Vantage API Integration
const axios = require('axios');

class AlphaVantageClient {
  constructor(apiKey) {
    this.apiKey = apiKey || process.env.ALPHA_VANTAGE_API_KEY;
    this.baseUrl = 'https://www.alphavantage.co/query';
  }

  async getDaily(symbol, outputsize = 'compact') {
    try {
      const response = await axios.get(this.baseUrl, {
        params: {
          function: 'TIME_SERIES_DAILY',
          symbol: symbol,
          outputsize: outputsize,
          apikey: this.apiKey
        }
      });
      
      return this.parseTimeSeries(response.data);
    } catch (error) {
      console.error('Alpha Vantage API error:', error.message);
      throw new Error(`Failed to fetch stock data for ${symbol}`);
    }
  }

  async getIntraday(symbol, interval = '5min') {
    try {
      const response = await axios.get(this.baseUrl, {
        params: {
          function: 'TIME_SERIES_INTRADAY',
          symbol: symbol,
          interval: interval,
          apikey: this.apiKey
        }
      });
      
      return this.parseTimeSeries(response.data);
    } catch (error) {
      console.error('Alpha Vantage API error:', error.message);
      throw new Error(`Failed to fetch intraday data for ${symbol}`);
    }
  }

  async getIndicators(symbol, indicator = 'RSI', interval = 'daily', time_period = 14) {
    try {
      const response = await axios.get(this.baseUrl, {
        params: {
          function: `TECHNICAL_INDICATOR_${indicator.toUpperCase()}`,
          symbol: symbol,
          interval: interval,
          time_period: time_period,
          apikey: this.apiKey
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('Alpha Vantage API error:', error.message);
      throw new Error(`Failed to fetch ${indicator} data for ${symbol}`);
    }
  }

  parseTimeSeries(data) {
    if (!data['Time Series (Daily)'] && !data['Time Series (5min)']) {
      throw new Error('Invalid API response format');
    }
    
    const seriesKey = data['Time Series (Daily)'] ? 'Time Series (Daily)' : 'Time Series (5min)';
    const series = data[seriesKey];
    
    return Object.entries(series).map(([date, values]) => ({
      date: new Date(date),
      open: parseFloat(values['1. open']),
      high: parseFloat(values['2. high']),
      low: parseFloat(values['3. low']),
      close: parseFloat(values['4. close']),
      volume: parseInt(values['5. volume'])
    })).sort((a, b) => a.date - b.date);
  }
}

module.exports = AlphaVantageClient;