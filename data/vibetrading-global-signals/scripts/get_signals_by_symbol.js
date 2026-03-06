#!/usr/bin/env node

/**
 * Get Signals by Symbol from VibeTrading DataHub
 * 
 * Usage:
 *   node get_signals_by_symbol.js <symbol> [signal_types] [limit] [hours]
 * 
 * Examples:
 *   node get_signals_by_symbol.js BTC
 *   node get_signals_by_symbol.js ETH "TECHNICAL_INDICATOR" 5
 *   node get_signals_by_symbol.js SOL "" 10 48
 */

import axios from 'axios';

const API_BASE_URL = 'https://vibetrading.dev/api/v1';

async function getSignalsBySymbol(symbol, signalTypes = '', limit = '', hours = '') {
  try {
    const params = new URLSearchParams();
    
    if (signalTypes) params.append('signal_types', signalTypes);
    if (limit) params.append('limit', limit);
    if (hours) params.append('hours', hours);

    const url = `${API_BASE_URL}/signals/${symbol}?${params.toString()}`;
    
    console.log(`📡 Fetching signals for ${symbol}`);
    if (signalTypes) console.log(`   Signal types: ${signalTypes}`);
    if (limit) console.log(`   Limit: ${limit}`);
    if (hours) console.log(`   Time window: ${hours} hours`);
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
      if (error.response.status === 404) {
        console.error(`❌ No signals found for ${symbol} with the specified filters`);
      } else {
        console.error(`❌ API Error: ${error.response.status} ${error.response.statusText}`);
        if (error.response.data) {
          console.error(`   Details: ${JSON.stringify(error.response.data)}`);
        }
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
  
  const timeAgo = getTimeAgo(new Date(signal.created_at));
  
  return `
${emoji} [${signal.signal_type}] - ${payload.sentiment} (${timeAgo})
   Author: ${signal.author}
   Created: ${new Date(signal.created_at).toLocaleString()}
   Model: ${payload.model}
   
   Analysis:
   ${payload.one_pager_markdown.split('\n').slice(0, 8).join('\n   ')}${payload.one_pager_markdown.split('\n').length > 8 ? '...' : ''}
  `.trim();
}

function getTimeAgo(date) {
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 60) {
    return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
  } else if (diffHours < 24) {
    return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
  } else {
    return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
  }
}

function displayResults(signals, symbol) {
  console.log('='.repeat(60));
  console.log(`📊 ${symbol} SIGNAL REPORT`);
  console.log('='.repeat(60));
  console.log(`Total Signals: ${signals.length}`);
  
  if (signals.length === 0) {
    console.log('No signals found for this symbol with current filters.');
    return;
  }

  // Group by signal type
  const byType = {};
  signals.forEach(signal => {
    if (!byType[signal.signal_type]) {
      byType[signal.signal_type] = [];
    }
    byType[signal.signal_type].push(signal);
  });

  // Display by type
  for (const [type, typeSignals] of Object.entries(byType)) {
    console.log('');
    console.log(`🎯 ${type} (${typeSignals.length} signal${typeSignals.length > 1 ? 's' : ''})`);
    console.log('-'.repeat(40));
    
    typeSignals.forEach((signal, index) => {
      console.log(`${index + 1}. ${formatSignal(signal)}`);
      console.log('');
    });
  }

  // Sentiment summary
  const sentimentCount = { BULLISH: 0, BEARISH: 0, NEUTRAL: 0 };
  signals.forEach(signal => {
    const sentiment = signal.signal_payload.sentiment;
    if (sentimentCount.hasOwnProperty(sentiment)) {
      sentimentCount[sentiment]++;
    }
  });

  console.log('='.repeat(60));
  console.log('🎭 Sentiment Summary:');
  console.log(`   📈 Bullish: ${sentimentCount.BULLISH}`);
  console.log(`   📉 Bearish: ${sentimentCount.BEARISH}`);
  console.log(`   ➡️  Neutral: ${sentimentCount.NEUTRAL}`);
  
  // Overall sentiment
  const total = signals.length;
  const bullishPercent = (sentimentCount.BULLISH / total * 100).toFixed(1);
  const bearishPercent = (sentimentCount.BEARISH / total * 100).toFixed(1);
  
  console.log('');
  console.log(`📊 Overall: ${bullishPercent}% Bullish, ${bearishPercent}% Bearish`);
  console.log('='.repeat(60));
}

// Parse command line arguments
const args = process.argv.slice(2);

if (args.length < 1) {
  console.log('Usage: node get_signals_by_symbol.js <symbol> [signal_types] [limit] [hours]');
  console.log('');
  console.log('Examples:');
  console.log('  node get_signals_by_symbol.js BTC');
  console.log('  node get_signals_by_symbol.js ETH "TECHNICAL_INDICATOR" 5');
  console.log('  node get_signals_by_symbol.js SOL "" 10 48');
  process.exit(1);
}

const symbol = args[0].toUpperCase();
const signalTypes = args[1] || '';
const limit = args[2] || '';
const hours = args[3] || '';

// Execute
(async () => {
  const signals = await getSignalsBySymbol(symbol, signalTypes, limit, hours);
  displayResults(signals, symbol);
})();