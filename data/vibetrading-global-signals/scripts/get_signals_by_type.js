#!/usr/bin/env node

/**
 * Get Signals by Symbol and Type from VibeTrading DataHub
 * 
 * Usage:
 *   node get_signals_by_type.js <symbol> <signal_type> [limit] [hours]
 * 
 * Examples:
 *   node get_signals_by_type.js BTC WHALE_ACTIVITY
 *   node get_signals_by_type.js ETH FUNDING_RATE 3
 *   node get_signals_by_type.js SOL TECHNICAL_INDICATOR 5 72
 */

import axios from 'axios';

const API_BASE_URL = 'https://vibetrading.dev/api/v1';

async function getSignalsByType(symbol, signalType, limit = '', hours = '') {
  try {
    const params = new URLSearchParams();
    
    if (limit) params.append('limit', limit);
    if (hours) params.append('hours', hours);

    const url = `${API_BASE_URL}/signals/${symbol}/${signalType}?${params.toString()}`;
    
    console.log(`📡 Fetching ${signalType} signals for ${symbol}`);
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
        console.error(`❌ No ${signalType} signals found for ${symbol}`);
        console.error('   Try a different signal type or time window.');
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

function formatSignalDetail(signal) {
  const payload = signal.signal_payload;
  const emoji = {
    'BULLISH': '📈',
    'BEARISH': '📉',
    'NEUTRAL': '➡️'
  }[payload.sentiment] || '❓';
  
  const timeAgo = getTimeAgo(new Date(signal.created_at));
  
  return `
${emoji} ${payload.sentiment} Signal (${timeAgo})
   Signal ID: ${signal.id}
   Author: ${signal.author}
   Created: ${new Date(signal.created_at).toLocaleString()}
   Model: ${payload.model}
   Timestamp: ${payload.timestamp}
   
   Full Analysis:
   ${'='.repeat(50)}
   ${payload.one_pager_markdown}
   ${'='.repeat(50)}
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

function displayTypeInfo(signalType) {
  const typeInfo = {
    'WHALE_ACTIVITY': {
      description: 'Whale wallet movement analysis',
      keyMetrics: ['sentiment', 'whale_count', 'transaction_volume']
    },
    'NEWS_ANALYSIS': {
      description: 'Crypto news sentiment analysis',
      keyMetrics: ['sentiment', 'news_source', 'articles_count', 'fear_greed_index']
    },
    'FUNDING_RATE': {
      description: 'Perpetual funding rate signals',
      keyMetrics: ['sentiment', 'funding_rate', 'history_hours']
    },
    'TECHNICAL_INDICATOR': {
      description: 'Multi-timeframe technical analysis',
      keyMetrics: ['sentiment', 'interval', 'sentiment_1h', 'sentiment_4h']
    }
  };

  const info = typeInfo[signalType] || { description: 'Unknown signal type' };
  
  console.log(`📋 ${signalType}: ${info.description}`);
  if (info.keyMetrics) {
    console.log(`   Key Metrics: ${info.keyMetrics.join(', ')}`);
  }
  console.log('');
}

function displayResults(signals, symbol, signalType) {
  console.log('='.repeat(60));
  console.log(`📊 ${symbol} - ${signalType} SIGNALS`);
  console.log('='.repeat(60));
  
  displayTypeInfo(signalType);
  
  console.log(`Total Signals: ${signals.length}`);
  console.log('');

  if (signals.length === 0) {
    console.log('No signals found.');
    return;
  }

  // Display each signal
  signals.forEach((signal, index) => {
    console.log(`🎯 Signal ${index + 1}/${signals.length}`);
    console.log('-'.repeat(40));
    console.log(formatSignalDetail(signal));
    
    // Add separator between signals
    if (index < signals.length - 1) {
      console.log('\n' + '─'.repeat(60) + '\n');
    }
  });

  // Sentiment distribution
  const sentimentCount = { BULLISH: 0, BEARISH: 0, NEUTRAL: 0 };
  signals.forEach(signal => {
    const sentiment = signal.signal_payload.sentiment;
    if (sentimentCount.hasOwnProperty(sentiment)) {
      sentimentCount[sentiment]++;
    }
  });

  console.log('\n' + '='.repeat(60));
  console.log('📈 Signal Statistics:');
  console.log(`   📈 Bullish: ${sentimentCount.BULLISH}`);
  console.log(`   📉 Bearish: ${sentimentCount.BEARISH}`);
  console.log(`   ➡️  Neutral: ${sentimentCount.NEUTRAL}`);
  
  // Time distribution
  const now = new Date();
  const signalsByRecency = {
    'Last hour': 0,
    'Last 24h': 0,
    'Last 7 days': 0,
    'Older': 0
  };

  signals.forEach(signal => {
    const signalTime = new Date(signal.created_at);
    const diffHours = (now - signalTime) / 3600000;
    
    if (diffHours < 1) {
      signalsByRecency['Last hour']++;
    } else if (diffHours < 24) {
      signalsByRecency['Last 24h']++;
    } else if (diffHours < 168) {
      signalsByRecency['Last 7 days']++;
    } else {
      signalsByRecency['Older']++;
    }
  });

  console.log('\n⏰ Time Distribution:');
  for (const [period, count] of Object.entries(signalsByRecency)) {
    if (count > 0) {
      console.log(`   ${period}: ${count}`);
    }
  }
  
  console.log('='.repeat(60));
}

// Parse command line arguments
const args = process.argv.slice(2);

if (args.length < 2) {
  console.log('Usage: node get_signals_by_type.js <symbol> <signal_type> [limit] [hours]');
  console.log('');
  console.log('Examples:');
  console.log('  node get_signals_by_type.js BTC WHALE_ACTIVITY');
  console.log('  node get_signals_by_type.js ETH FUNDING_RATE 3');
  console.log('  node get_signals_by_type.js SOL TECHNICAL_INDICATOR 5 72');
  console.log('');
  console.log('Available Signal Types:');
  console.log('  whale_activity, news_analysis, funding_rate, technical_indicator');
  process.exit(1);
}

const symbol = args[0].toUpperCase();
const signalType = args[1].toLowerCase();
const limit = args[2] || '';
const hours = args[3] || '';

// Validate signal type
const validTypes = ['whale_activity', 'news_analysis', 'funding_rate', 'technical_indicator'];
if (!validTypes.includes(signalType)) {
  console.error(`❌ Invalid signal type: ${signalType}`);
  console.error(`   Valid types: ${validTypes.join(', ')}`);
  process.exit(1);
}

// Execute
(async () => {
  const signals = await getSignalsByType(symbol, signalType, limit, hours);
  displayResults(signals, symbol, signalType);
})();