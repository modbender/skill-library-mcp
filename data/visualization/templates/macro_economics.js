// Macro Economics Template
function generateMacroEconomicsTemplate(params) {
  const {
    indicators = ['gdp', 'inflation', 'unemployment', 'interest_rate'],
    countries = ['US', 'CN', 'EU'],
    timeframe = '2020-2026'
  } = params;

  // Generate mock data for macro indicators
  const years = Array.from({length: 7}, (_, i) => 2020 + i);
  
  const gdpData = {
    US: [21.43, 22.38, 25.46, 26.95, 27.97, 28.76, 29.54],
    CN: [14.72, 17.73, 17.96, 18.34, 19.21, 20.15, 21.08],
    EU: [15.23, 16.10, 16.85, 17.21, 17.89, 18.45, 19.02]
  };
  
  const inflationData = {
    US: [1.2, 4.7, 8.0, 6.5, 3.4, 2.8, 2.5],
    CN: [2.5, 0.9, 2.0, 0.2, 0.3, 0.8, 1.2],
    EU: [1.0, 2.6, 8.4, 6.9, 4.1, 3.2, 2.8]
  };
  
  const unemploymentData = {
    US: [3.7, 5.3, 3.6, 3.7, 3.9, 4.1, 4.0],
    CN: [5.2, 5.1, 5.5, 5.2, 5.0, 4.9, 4.8],
    EU: [7.6, 7.2, 6.6, 6.0, 5.9, 5.8, 5.7]
  };
  
  const interestRateData = {
    US: [1.55, 0.09, 4.33, 5.08, 5.25, 5.25, 5.00],
    CN: [3.85, 3.85, 3.65, 3.45, 3.45, 3.45, 3.45],
    EU: [-0.50, -0.50, 1.50, 3.50, 4.00, 4.00, 4.00]
  };

  // Create multi-chart dashboard
  const charts = [];
  
  if (indicators.includes('gdp')) {
    charts.push({
      type: 'line',
      title: 'GDP Growth (Trillion USD)',
      data: {
        labels: years,
        datasets: countries.map(country => ({
          label: country,
          data: gdpData[country],
          borderColor: getColorForCountry(country)
        }))
      }
    });
  }
  
  if (indicators.includes('inflation')) {
    charts.push({
      type: 'line',
      title: 'Inflation Rate (%)',
      data: {
        labels: years,
        datasets: countries.map(country => ({
          label: country,
          data: inflationData[country],
          borderColor: getColorForCountry(country)
        }))
      }
    });
  }
  
  if (indicators.includes('unemployment')) {
    charts.push({
      type: 'line',
      title: 'Unemployment Rate (%)',
      data: {
        labels: years,
        datasets: countries.map(country => ({
          label: country,
          data: unemploymentData[country],
          borderColor: getColorForCountry(country)
        }))
      }
    });
  }
  
  if (indicators.includes('interest_rate')) {
    charts.push({
      type: 'line',
      title: 'Interest Rate (%)',
      data: {
        labels: years,
        datasets: countries.map(country => ({
          label: country,
          data: interestRateData[country],
          borderColor: getColorForCountry(country)
        }))
      }
    });
  }

  return {
    composite: true,
    charts: charts,
    metadata: {
      title: 'Macroeconomic Indicators Dashboard',
      description: `Comparing key economic indicators across ${countries.join(', ')} from ${timeframe}`
    }
  };
}

function getColorForCountry(country) {
  const colors = {
    'US': '#FF6384',
    'CN': '#36A2EB',
    'EU': '#FFCE56',
    'JP': '#4BC0C0',
    'UK': '#9966FF'
  };
  return colors[country] || '#888888';
}

module.exports = { generateMacroEconomicsTemplate };