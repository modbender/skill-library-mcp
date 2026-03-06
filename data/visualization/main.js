// Visualization Skill Core Logic (Browser-based Rendering)
// Uses OpenClaw's canvas tool for client-side chart generation

const AlphaVantageClient = require('./data/alpha_vantage');
const { generateHeatmapConfig } = require('./charts/heatmap');
const { generateRadarConfig } = require('./charts/radar');
const { exportToPDF } = require('./render/pdf_export');
const { generateMacroEconomicsTemplate } = require('./templates/macro_economics');
const { generateCryptoTemplate } = require('./templates/crypto');
const CustomTemplateManager = require('./templates/custom_template');
const VisualizationConfigUI = require('./ui/config_ui');
const ChartInsightsGenerator = require('./analysis/insights');
const { CloudStorage } = require('./cloud/aws_lambda');
const VisualizationSecurity = require('./security/auth');

async function generateVisualization(context) {
  const { prompt, template, format = 'png', userId } = context;
  
  // Parse user request into structured parameters
  const params = parseRequest(prompt);
  
  // Generate Chart.js configuration based on template
  let chartConfig;
  switch(params.template) {
    case 'stock':
      chartConfig = await generateStockChartConfig(params);
      break;
    case 'portfolio':
      chartConfig = generatePortfolioChartConfig(params);
      break;
    case 'industry':
      chartConfig = generateIndustryChartConfig(params);
      break;
    case 'heatmap':
      chartConfig = generateHeatmapConfig(params.data, params.options);
      break;
    case 'radar':
      chartConfig = generateRadarConfig(params.data, params.options);
      break;
    case 'macro':
      chartConfig = generateMacroEconomicsTemplate(params);
      break;
    case 'crypto':
      chartConfig = generateCryptoTemplate(params);
      break;
    case 'custom':
      const templateManager = new CustomTemplateManager();
      const customTemplate = templateManager.loadTemplate(params.templateName);
      chartConfig = customTemplate;
      break;
    default:
      throw new Error('Unsupported visualization template');
  }
  
  // Generate insights and analysis
  const insightsGenerator = new ChartInsightsGenerator();
  const insights = insightsGenerator.generateInsights(params.template, params.data, params);
  chartConfig = insightsGenerator.addChartAnnotations(chartConfig, insights);
  
  // Render based on requested format
  if (format === 'pdf') {
    const outputPath = `/home/admin/.openclaw/workspace/visualization_${params.template}_${Date.now()}.pdf`;
    const result = await exportToPDF(chartConfig, outputPath);
    
    // Upload to cloud storage if requested
    if (params.cloudStorage) {
      const cloudStorage = new CloudStorage();
      const cloudResult = await cloudStorage.uploadChart(result.path, `visualization_${params.template}_${Date.now()}.pdf`, params.cloudProvider);
      result.cloudUrl = cloudResult.url;
    }
    
    return result;
  } else {
    // Render via OpenClaw's browser-based canvas
    const result = await renderChartInBrowser(chartConfig, params.template);
    
    // Add insights to result
    result.insights = insights;
    
    // Upload to cloud storage if requested
    if (params.cloudStorage) {
      const cloudStorage = new CloudStorage();
      const cloudResult = await cloudStorage.uploadChart(result.path, `visualization_${params.template}_${Date.now()}.png`, params.cloudProvider);
      result.cloudUrl = cloudResult.url;
    }
    
    return result;
  }
}

// Stock Technical Analysis Config (with real data integration)
async function generateStockChartConfig(params) {
  const { symbol, indicators = ['price', 'ma50', 'rsi', 'volume'] } = params;
  
  // Fetch real stock data if API key is available
  let priceData, rsiData;
  try {
    const alphaVantage = new AlphaVantageClient();
    priceData = await alphaVantage.getDaily(symbol, 'compact');
    
    if (indicators.includes('rsi')) {
      const rsiResponse = await alphaVantage.getIndicators(symbol, 'RSI', 'daily', 14);
      // Parse RSI data (implementation depends on API response format)
      rsiData = Object.entries(rsiResponse).map(([date, value]) => ({
        date: new Date(date),
        rsi: parseFloat(value)
      })).sort((a, b) => a.date - b.date);
    }
  } catch (error) {
    console.warn('Using mock data due to API error:', error.message);
    // Fall back to mock data
    priceData = generateMockPriceData(symbol);
    rsiData = generateMockRSIData();
  }
  
  // Extract dates and values
  const dates = priceData.map(d => d.date.toISOString().split('T')[0]);
  const closePrices = priceData.map(d => d.close);
  const volumes = priceData.map(d => d.volume);
  
  // Calculate moving average
  const ma50Data = calculateMovingAverage(closePrices, 50);
  
  return {
    type: 'line',
    data: {
      labels: dates,
      datasets: [
        {
          label: `${symbol} Price`,
          data: closePrices,
          borderColor: '#4BC0C0',
          tension: 0.1
        },
        ...(indicators.includes('ma50') ? [{
          label: '50-Day MA',
          data: ma50Data,
          borderColor: '#FF6384',
          borderDash: [5, 5]
        }] : []),
        ...(indicators.includes('rsi') ? [{
          label: 'RSI',
          data: rsiData?.map(d => d.rsi) || Array(dates.length).fill(50),
          borderColor: '#FFCE56',
          yAxisID: 'y1'
        }] : []),
        ...(indicators.includes('volume') ? [{
          label: 'Volume',
          data: volumes,
          type: 'bar',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          yAxisID: 'y2'
        }] : [])
      ]
    },
    options: {
      responsive: true,
      interaction: {
        mode: 'index',
        intersect: false
      },
      scales: {
        y: {
          type: 'linear',
          display: true,
          position: 'left',
        },
        ...(indicators.includes('rsi') ? {
          y1: {
            type: 'linear',
            display: true,
            position: 'right',
            grid: {
              drawOnChartArea: false,
            },
            min: 0,
            max: 100
          }
        } : {}),
        ...(indicators.includes('volume') ? {
          y2: {
            type: 'linear',
            display: true,
            position: 'right',
            grid: {
              drawOnChartArea: false,
            },
          }
        } : {})
      }
    }
  };
}

// Mock data generators (fallback when API fails)
function generateMockPriceData(symbol) {
  const today = new Date();
  return Array.from({length: 30}, (_, i) => {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    return {
      date,
      open: 150 + Math.random()*20,
      high: 170 + Math.random()*10,
      low: 140 + Math.random()*10,
      close: 160 + Math.random()*15,
      volume: 1000000 + Math.random()*500000
    };
  }).reverse();
}

function generateMockRSIData() {
  const today = new Date();
  return Array.from({length: 30}, (_, i) => {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    return {
      date,
      rsi: 30 + Math.random()*40
    };
  }).reverse();
}

function calculateMovingAverage(data, window) {
  const result = [];
  for (let i = 0; i < data.length; i++) {
    if (i < window - 1) {
      result.push(null);
    } else {
      const sum = data.slice(i - window + 1, i + 1).reduce((a, b) => a + b, 0);
      result.push(sum / window);
    }
  }
  return result;
}

// Portfolio Dashboard Config
function generatePortfolioChartConfig(params) {
  const { assets, riskMetrics } = params;
  
  // Asset allocation pie chart
  const pieConfig = {
    type: 'pie',
    data: {
      labels: Object.keys(assets),
      datasets: [{
        data: Object.values(assets),
        backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']
      }]
    }
  };
  
  // Performance line chart
  const performanceConfig = {
    type: 'line',
    data: {
      labels: Array.from({length: 90}, (_, i) => 
        new Date(Date.now() - i*86400000).toISOString().split('T')[0]
      ),
      datasets: [{
        label: 'Portfolio Value',
        data: Array.from({length: 90}, (_, i) => 
          100 + Math.random()*20 - i*0.1
        ),
        borderColor: '#FF6384',
        fill: true
      }]
    }
  };
  
  return {
    composite: true,
    charts: [pieConfig, performanceConfig],
    metadata: { riskMetrics }
  };
}

// Industry Comparison Config
function generateIndustryChartConfig(params) {
  const { sectors, metrics } = params;
  
  // Bar chart for returns/volatility
  const barConfig = {
    type: 'bar',
    data: {
      labels: sectors,
      datasets: [
        {
          label: 'Annual Return (%)',
          data: metrics.returns || sectors.map(() => 10 + Math.random()*15),
          backgroundColor: 'rgba(54, 162, 235, 0.6)'
        },
        {
          label: 'Volatility (%)',
          data: metrics.volatility || sectors.map(() => 15 + Math.random()*10),
          backgroundColor: 'rgba(255, 99, 132, 0.6)'
        }
      ]
    }
  };
  
  // Scatter plot for risk-return
  const scatterData = sectors.map((sector, i) => ({
    x: metrics.volatility?.[i] || 15 + Math.random()*10,
    y: metrics.returns?.[i] || 10 + Math.random()*15,
    label: sector
  }));
  
  const scatterConfig = {
    type: 'scatter',
    data: {
      datasets: [{
        label: 'Sectors',
        data: scatterData,
        backgroundColor: 'rgba(75, 192, 192, 0.6)'
      }]
    },
    options: {
      scales: {
        x: {
          title: { display: true, text: 'Volatility (%)' }
        },
        y: {
          title: { display: true, text: 'Return (%)' }
        }
      }
    }
  };
  
  return {
    composite: true,
    charts: [barConfig, scatterConfig]
  };
}

// Browser-based rendering using OpenClaw's canvas tool
async function renderChartInBrowser(chartConfig, template) {
  // Generate HTML page with Chart.js
  const htmlContent = `
<!DOCTYPE html>
<html>
<head>
  <title>Visualization</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body { margin: 0; padding: 20px; background: white; }
    .chart-container { width: 1200px; height: 800px; margin: 0 auto; }
    .composite { display: flex; flex-wrap: wrap; justify-content: center; }
    .composite > div { margin: 10px; }
    /* Interactive features */
    canvas { cursor: pointer; }
    .tooltip { 
      position: absolute; 
      background: rgba(0,0,0,0.8); 
      color: white; 
      padding: 5px; 
      border-radius: 3px; 
      pointer-events: none;
      display: none;
    }
    .insights-section {
      margin-top: 30px;
      padding: 20px;
      background: #f8f9fa;
      border-radius: 8px;
    }
    .insights-section h3 {
      margin-top: 0;
      color: #495057;
    }
    .insights-list {
      list-style-type: none;
      padding: 0;
    }
    .insights-list li {
      padding: 8px 0;
      border-bottom: 1px solid #e9ecef;
    }
    .insights-list li:last-child {
      border-bottom: none;
    }
  </style>
</head>
<body>
  ${chartConfig.composite 
    ? `<div class="composite">
        ${chartConfig.charts.map((_, i) => 
          `<div class="chart-container" id="chart${i}"></div>`
        ).join('')}
       </div>`
    : '<div class="chart-container"><canvas id="chart"></canvas></div>'
  }
  <div class="tooltip" id="tooltip"></div>
  
  <!-- Insights Section -->
  ${chartConfig.metadata?.insights ? `
  <div class="insights-section">
    <h3>📊 Analysis Insights</h3>
    <ul class="insights-list">
      ${chartConfig.metadata.insights.map(insight => `<li>${insight}</li>`).join('')}
    </ul>
  </div>
  ` : ''}
  
  <script>
    // Basic interactivity
    function setupInteractivity(canvas, chart) {
      canvas.addEventListener('mousemove', (event) => {
        const tooltip = document.getElementById('tooltip');
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        const activePoints = chart.getElementsAtEventForMode(event, 'nearest', { intersect: true }, true);
        if (activePoints.length) {
          const firstPoint = activePoints[0];
          const dataset = chart.data.datasets[firstPoint.datasetIndex];
          const value = dataset.data[firstPoint.index];
          tooltip.innerHTML = \`\${dataset.label}: \${value}\`;
          tooltip.style.display = 'block';
          tooltip.style.left = (event.pageX + 10) + 'px';
          tooltip.style.top = (event.pageY + 10) + 'px';
        } else {
          tooltip.style.display = 'none';
        }
      });
      
      canvas.addEventListener('mouseleave', () => {
        document.getElementById('tooltip').style.display = 'none';
      });
    }
    
    ${chartConfig.composite 
      ? chartConfig.charts.map((config, i) => 
          `const chart${i} = new Chart(document.getElementById('chart${i}'), ${JSON.stringify(config)});
           setupInteractivity(document.getElementById('chart${i}'), chart${i});`
        ).join('\n')
      : `const chart = new Chart(document.getElementById('chart'), ${JSON.stringify(chartConfig)});
         setupInteractivity(document.getElementById('chart'), chart);`
    }
    
    // Add risk metrics if available
    ${chartConfig.metadata?.riskMetrics 
      ? `
        const metrics = ${JSON.stringify(chartConfig.metadata.riskMetrics)};
        const info = document.createElement('div');
        info.innerHTML = \`
          <h3>Risk Metrics</h3>
          <p>Volatility: \${metrics.volatility}%</p>
          <p>Max Drawdown: \${metrics.drawdown}%</p>
          <p>Sharpe Ratio: \${metrics.sharpe}</p>
        \`;
        document.body.appendChild(info);
        `
      : ''
    }
  </script>
</body>
</html>`;

  // Save HTML to workspace
  const fs = require('fs');
  const outputPath = `/home/admin/.openclaw/workspace/visualization_${template}_${Date.now()}.html`;
  fs.writeFileSync(outputPath, htmlContent);
  
  // Use OpenClaw's canvas tool to render and capture
  const { canvas } = require('openclaw-tools');
  const snapshot = await canvas.present({
    url: `file://${outputPath}`,
    width: 1600,
    height: 1200,
    delayMs: 2000
  });
  
  return { 
    path: snapshot.path, 
    type: 'image/png',
    htmlPath: outputPath
  };
}

// Helper functions
function parseRequest(prompt) {
  // Extract parameters from natural language prompt
  const template = 
    prompt.includes('股票') || prompt.includes('stock') ? 'stock' :
    prompt.includes('投资组合') || prompt.includes('portfolio') ? 'portfolio' :
    prompt.includes('行业') || prompt.includes('industry') ? 'industry' :
    prompt.includes('热力图') || prompt.includes('heatmap') ? 'heatmap' :
    prompt.includes('雷达图') || prompt.includes('radar') ? 'radar' :
    prompt.includes('宏观') || prompt.includes('macro') ? 'macro' :
    prompt.includes('加密货币') || prompt.includes('crypto') ? 'crypto' :
    prompt.includes('自定义') || prompt.includes('custom') ? 'custom' :
    'stock';
  
  // Check for format requests
  const format = 
    prompt.includes('PDF') || prompt.includes('pdf') ? 'pdf' :
    'png';
  
  // Check for cloud storage requests
  const cloudStorage = prompt.includes('云存储') || prompt.includes('cloud');
  const cloudProvider = 
    prompt.includes('AWS') ? 'aws' :
    prompt.includes('Google') ? 'google' :
    prompt.includes('Azure') ? 'azure' :
    'aws';
  
  return {
    template,
    format,
    cloudStorage,
    cloudProvider,
    symbol: extractSymbol(prompt) || 'AAPL',
    indicators: ['price', 'ma50', 'rsi', 'volume'],
    assets: { 
      '科技股': 60, 
      '金融股': 25, 
      '能源股': 15 
    },
    riskMetrics: {
      volatility: 15,
      drawdown: -8,
      sharpe: 1.2
    },
    sectors: ['科技', '金融', '能源'],
    metrics: {},
    data: [], // For heatmap/radar
    options: {},
    templateName: extractTemplateName(prompt)
  };
}

function extractSymbol(prompt) {
  const match = prompt.match(/([A-Z]{2,5})/);
  return match ? match[1] : null;
}

function extractTemplateName(prompt) {
  const match = prompt.match(/模板[:：]\s*(\w+)/);
  return match ? match[1] : null;
}

module.exports = { generateVisualization };