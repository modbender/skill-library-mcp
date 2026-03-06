// Cryptocurrency Analysis Template
function generateCryptoTemplate(params) {
  const {
    symbols = ['BTC', 'ETH', 'SOL'],
    timeframe = '2026-01-01 to 2026-02-20',
    indicators = ['price', 'volume', 'market_cap', 'correlation']
  } = params;

  // Generate mock crypto data
  const dates = Array.from({length: 50}, (_, i) => {
    const date = new Date('2026-01-01');
    date.setDate(date.getDate() + i);
    return date.toISOString().split('T')[0];
  });
  
  const priceData = {
    BTC: Array.from({length: 50}, () => 45000 + Math.random()*10000),
    ETH: Array.from({length: 50}, () => 3000 + Math.random()*1000),
    SOL: Array.from({length: 50}, () => 100 + Math.random()*50)
  };
  
  const volumeData = {
    BTC: Array.from({length: 50}, () => 20 + Math.random()*10),
    ETH: Array.from({length: 50}, () => 15 + Math.random()*8),
    SOL: Array.from({length: 50}, () => 5 + Math.random()*3)
  };
  
  const marketCapData = {
    BTC: Array.from({length: 50}, () => 850 + Math.random()*100),
    ETH: Array.from({length: 50}, () => 350 + Math.random()*50),
    SOL: Array.from({length: 50}, () => 45 + Math.random()*10)
  };

  const charts = [];
  
  if (indicators.includes('price')) {
    charts.push({
      type: 'line',
      title: 'Cryptocurrency Price Trends (USD)',
      data: {
        labels: dates,
        datasets: symbols.map(symbol => ({
          label: symbol,
          data: priceData[symbol],
          borderColor: getColorForCrypto(symbol)
        }))
      }
    });
  }
  
  if (indicators.includes('volume')) {
    charts.push({
      type: 'bar',
      title: 'Trading Volume (Billion USD)',
      data: {
        labels: dates,
        datasets: symbols.map(symbol => ({
          label: symbol,
          data: volumeData[symbol],
          backgroundColor: getColorForCrypto(symbol, 0.6)
        }))
      }
    });
  }
  
  if (indicators.includes('market_cap')) {
    charts.push({
      type: 'line',
      title: 'Market Capitalization (Billion USD)',
      data: {
        labels: dates,
        datasets: symbols.map(symbol => ({
          label: symbol,
          data: marketCapData[symbol],
          borderColor: getColorForCrypto(symbol)
        }))
      }
    });
  }
  
  if (indicators.includes('correlation')) {
    // Calculate correlation matrix
    const correlationMatrix = calculateCorrelationMatrix(symbols, priceData);
    charts.push({
      type: 'heatmap',
      title: 'Price Correlation Matrix',
      data: correlationMatrix,
      options: {
        xLabels: symbols,
        yLabels: symbols,
        colorScheme: 'viridis'
      }
    });
  }

  return {
    composite: true,
    charts: charts,
    metadata: {
      title: 'Cryptocurrency Market Analysis',
      description: `Analyzing ${symbols.join(', ')} from ${timeframe} with key market indicators`
    }
  };
}

function getColorForCrypto(symbol, opacity = 1) {
  const colors = {
    'BTC': `rgba(247, 147, 26, ${opacity})`,
    'ETH': `rgba(109, 110, 112, ${opacity})`,
    'SOL': `rgba(51, 187, 217, ${opacity})`,
    'ADA': `rgba(0, 203, 166, ${opacity})`,
    'DOT': `rgba(212, 43, 106, ${opacity})`
  };
  return colors[symbol] || `rgba(136, 136, 136, ${opacity})`;
}

function calculateCorrelationMatrix(symbols, priceData) {
  // Simplified correlation calculation (in real implementation would use proper stats)
  const matrix = [];
  for (let i = 0; i < symbols.length; i++) {
    const row = [];
    for (let j = 0; j < symbols.length; j++) {
      if (i === j) {
        row.push(1.0); // Perfect correlation with self
      } else if (i < j) {
        // Higher correlation between major cryptos
        const correlation = symbols.includes('BTC') && symbols.includes('ETH') ? 0.85 : 0.6;
        row.push(correlation);
      } else {
        // Use symmetric value
        row.push(matrix[j][i]);
      }
    }
    matrix.push(row);
  }
  return matrix;
}

module.exports = { generateCryptoTemplate };