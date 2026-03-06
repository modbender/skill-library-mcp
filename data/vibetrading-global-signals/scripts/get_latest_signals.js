#!/usr/bin/env node

/**
 * Get Latest Signals from VibeTrading DataHub
 * 
 * Usage:
 *   node get_latest_signals.js <symbols> [signal_types] [hours] [limit_per_type]
 * 
 * Examples:
 *   node get_latest_signals.js BTC,ETH
 *   node get_latest_signals.js BTC,ETH,SOL WHALE_ACTIVITY,NEWS_ANALYSIS 24
 *   node get_latest_signals.js BTC "WHALE_ACTIVITY,NEWS_ANALYSIS" 48 2
 */

import axios from 'axios';

const API_BASE_URL = 'https://vibetrading.dev/api/v1';

async function getLatestSignals(symbols, signalTypes = '', hours = '', limitPerType = '') {
  try {
    const params = new URLSearchParams();
    params.append('symbols', symbols);
    
    if (signalTypes) params.append('signal_types', signalTypes);
    if (hours) params.append('hours', hours);
    if (limitPerType) params.append('limit_per_type', limitPerType);

    const url = `${API_BASE_URL}/signals/latest?${params.toString()}`;
    
    console.log(`📡 Fetching latest signals for: ${symbols}`);
    if (signalTypes) console.log(`   Signal types: ${signalTypes}`);
    if (hours) console.log(`   Time window: ${hours} hours`);
    if (limitPerType) console.log(`   Limit per type: ${limitPerType}`);
    console.log('');

    const response = await axios.get(url, {
      headers: {
        'Accept': 'application/json'
      },
      timeout: 10000
    });

    return response.data;
  } catch (error) {
    if (error.response) {
      console.error(`❌ API Error: ${error.response.status} ${error.response.statusText}`);
      if (error.response.data) {
        console.error(`   Details: ${JSON.stringify(error.response.data)}`);
      }
    } else if (error.request) {
      console.error('❌ Network Error: No response received from API');
    } else {
      console.error(`❌ Error: ${error.message}`);
    }
    process.exit(1);
  }
}

function formatSignal(signal) {
  const payload = signal.signal_payload;
  const emoji = {
    'BULLISH': '📈',
    'BEARISH': '📉',
    'NEUTRAL': '➡️'
  }[payload.sentiment] || '❓';
  
  return `
${emoji} ${signal.symbol} [${signal.signal_type}] - ${payload.sentiment}
   Author: ${signal.author}
   Time: ${new Date(signal.created_at).toLocaleString()}
   Model: ${payload.model}
   
   Summary:
   ${payload.one_pager_markdown.split('\n').slice(0, 5).join('\n   ')}${payload.one_pager_markdown.split('\n').length > 5 ? '...' : ''}
  `.trim();
}

function displayResults(data) {
  console.log('='.repeat(60));
  console.log('📊 VIBETRADING SIGNAL REPORT');
  console.log('='.repeat(60));
  console.log(`Query Time: ${data.metadata.query_time}`);
  console.log(`Symbols: ${data.symbols.join(', ')}`);
  if (data.metadata.signal_types) {
    console.log(`Signal Types: ${data.metadata.signal_types.join(', ')}`);
  }
  if (data.metadata.hours_window) {
    console.log(`Time Window: ${data.metadata.hours_window} hours`);
  }
  console.log('='.repeat(60));
  console.log('');

  let totalSignals = 0;
  
  for (const [symbol, signals] of Object.entries(data.signals)) {
    if (signals.length > 0) {
      console.log(`🎯 ${symbol} (${signals.length} signal${signals.length > 1 ? 's' : ''})`);
      console.log('-'.repeat(40));
      
      signals.forEach(signal => {
        console.log(formatSignal(signal));
        console.log('');
        totalSignals++;
      });
    }
  }

  console.log('='.repeat(60));
  console.log(`📈 Total Signals Found: ${totalSignals}`);
  console.log('='.repeat(60));
  
  // Summary by sentiment
  const sentimentCount = { BULLISH: 0, BEARISH: 0, NEUTRAL: 0 };
  for (const signals of Object.values(data.signals)) {
    signals.forEach(signal => {
      const sentiment = signal.signal_payload.sentiment;
      if (sentimentCount.hasOwnProperty(sentiment)) {
        sentimentCount[sentiment]++;
      }
    });
  }
  
  console.log('\n🎭 Sentiment Summary:');
  console.log(`   📈 Bullish: ${sentimentCount.BULLISH}`);
  console.log(`   📉 Bearish: ${sentimentCount.BEARISH}`);
  console.log(`   ➡️  Neutral: ${sentimentCount.NEUTRAL}`);
}

// Parse command line arguments
const args = process.argv.slice(2);

if (args.length < 1) {
  console.log('Usage: node get_latest_signals.js <symbols> [signal_types] [hours] [limit_per_type]');
  console.log('');
  console.log('Examples:');
  console.log('  node get_latest_signals.js BTC,ETH');
  console.log('  node get_latest_signals.js BTC,ETH,SOL WHALE_ACTIVITY,NEWS_ANALYSIS 24');
  console.log('  node get_latest_signals.js BTC "WHALE_ACTIVITY,NEWS_ANALYSIS" 48 2');
  process.exit(1);
}

const symbols = args[0];
const signalTypes = args[1] || '';
const hours = args[2] || '';
const limitPerType = args[3] || '';

// Execute
(async () => {
  const data = await getLatestSignals(symbols, signalTypes, hours, limitPerType);
  displayResults(data);
})();