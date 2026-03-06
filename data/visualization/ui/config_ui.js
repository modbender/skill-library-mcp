// Visualization Parameter Configuration UI
class VisualizationConfigUI {
  constructor() {
    this.configPresets = {
      stock: {
        title: 'Stock Analysis',
        parameters: {
          symbol: { type: 'text', default: 'AAPL', label: 'Stock Symbol' },
          timeframe: { type: 'select', options: ['1M', '3M', '6M', '1Y', '2Y'], default: '3M', label: 'Time Range' },
          indicators: { type: 'checkbox', options: ['price', 'ma50', 'rsi', 'volume', 'macd'], default: ['price', 'ma50', 'rsi'], label: 'Technical Indicators' }
        }
      },
      portfolio: {
        title: 'Portfolio Dashboard',
        parameters: {
          assets: { type: 'keyvalue', default: { 'Tech': 60, 'Finance': 25, 'Energy': 15 }, label: 'Asset Allocation' },
          timeframe: { type: 'select', options: ['Q1', 'Q2', 'Q3', 'Q4', 'YTD'], default: 'YTD', label: 'Time Period' },
          riskMetrics: { type: 'checkbox', options: ['volatility', 'drawdown', 'sharpe'], default: ['volatility', 'drawdown'], label: 'Risk Metrics' }
        }
      },
      macro: {
        title: 'Macroeconomic Analysis',
        parameters: {
          countries: { type: 'multiselect', options: ['US', 'CN', 'EU', 'JP', 'UK'], default: ['US', 'CN', 'EU'], label: 'Countries' },
          indicators: { type: 'checkbox', options: ['gdp', 'inflation', 'unemployment', 'interest_rate'], default: ['gdp', 'inflation'], label: 'Economic Indicators' },
          timeframe: { type: 'range', min: 2020, max: 2026, default: [2020, 2026], label: 'Year Range' }
        }
      },
      crypto: {
        title: 'Cryptocurrency Analysis',
        parameters: {
          symbols: { type: 'multiselect', options: ['BTC', 'ETH', 'SOL', 'ADA', 'DOT'], default: ['BTC', 'ETH', 'SOL'], label: 'Cryptocurrencies' },
          indicators: { type: 'checkbox', options: ['price', 'volume', 'market_cap', 'correlation'], default: ['price', 'volume'], label: 'Market Indicators' },
          timeframe: { type: 'date-range', default: ['2026-01-01', '2026-02-20'], label: 'Date Range' }
        }
      }
    };
  }

  // Generate configuration interface HTML
  generateConfigInterface(templateType) {
    const config = this.configPresets[templateType];
    if (!config) {
      throw new Error(`Unknown template type: ${templateType}`);
    }

    let html = `
<!DOCTYPE html>
<html>
<head>
  <title>${config.title} Configuration</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
    .config-container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    h1 { color: #333; margin-bottom: 30px; }
    .form-group { margin-bottom: 20px; }
    label { display: block; margin-bottom: 5px; font-weight: bold; color: #555; }
    input[type="text"], select, input[type="date"] { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
    .checkbox-group, .multiselect-group { display: flex; flex-wrap: wrap; gap: 10px; }
    .checkbox-item, .multiselect-item { display: flex; align-items: center; gap: 5px; }
    .range-slider { display: flex; align-items: center; gap: 10px; }
    .range-value { min-width: 60px; text-align: center; }
    button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin-top: 20px; }
    button:hover { background: #0056b3; }
    .preview-section { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }
    .smart-suggestions { background: #e7f3ff; padding: 15px; border-radius: 4px; margin-top: 15px; }
    .smart-suggestions h3 { margin-top: 0; color: #007bff; }
  </style>
</head>
<body>
  <div class="config-container">
    <h1>${config.title}</h1>
    <form id="visualizationConfig">
`;

    // Generate form fields based on parameter types
    Object.entries(config.parameters).forEach(([paramName, paramConfig]) => {
      html += `<div class="form-group">`;
      html += `<label for="${paramName}">${paramConfig.label}</label>`;
      
      switch (paramConfig.type) {
        case 'text':
          html += `<input type="text" id="${paramName}" name="${paramName}" value="${paramConfig.default}" />`;
          break;
          
        case 'select':
          html += `<select id="${paramName}" name="${paramName}">`;
          paramConfig.options.forEach(option => {
            const selected = option === paramConfig.default ? 'selected' : '';
            html += `<option value="${option}" ${selected}>${option}</option>`;
          });
          html += `</select>`;
          break;
          
        case 'checkbox':
          html += `<div class="checkbox-group">`;
          paramConfig.options.forEach(option => {
            const checked = paramConfig.default.includes(option) ? 'checked' : '';
            html += `<div class="checkbox-item"><input type="checkbox" id="${paramName}_${option}" name="${paramName}[]" value="${option}" ${checked} /><label for="${paramName}_${option}">${option}</label></div>`;
          });
          html += `</div>`;
          break;
          
        case 'multiselect':
          html += `<div class="multiselect-group">`;
          paramConfig.options.forEach(option => {
            const checked = paramConfig.default.includes(option) ? 'checked' : '';
            html += `<div class="multiselect-item"><input type="checkbox" id="${paramName}_${option}" name="${paramName}[]" value="${option}" ${checked} /><label for="${paramName}_${option}">${option}</label></div>`;
          });
          html += `</div>`;
          break;
          
        case 'keyvalue':
          html += `<div id="${paramName}_container">`;
          Object.entries(paramConfig.default).forEach(([key, value]) => {
            html += `<div class="keyvalue-row" style="display: flex; gap: 10px; margin-bottom: 5px;">
              <input type="text" name="${paramName}_key[]" value="${key}" placeholder="Key" style="flex: 1;" />
              <input type="number" name="${paramName}_value[]" value="${value}" placeholder="Value" style="width: 100px;" />
            </div>`;
          });
          html += `</div>`;
          html += `<button type="button" onclick="addKeyValueRow('${paramName}')">Add Row</button>`;
          break;
          
        case 'range':
          html += `<div class="range-slider">
            <input type="range" id="${paramName}_min" name="${paramName}_min" min="${paramConfig.min}" max="${paramConfig.max}" value="${paramConfig.default[0]}" oninput="updateRangeValue('${paramName}')" />
            <span class="range-value" id="${paramName}_min_value">${paramConfig.default[0]}</span>
            <span>to</span>
            <span class="range-value" id="${paramName}_max_value">${paramConfig.default[1]}</span>
            <input type="range" id="${paramName}_max" name="${paramName}_max" min="${paramConfig.min}" max="${paramConfig.max}" value="${paramConfig.default[1]}" oninput="updateRangeValue('${paramName}')" />
          </div>`;
          break;
          
        case 'date-range':
          html += `<div style="display: flex; gap: 10px;">
            <input type="date" id="${paramName}_start" name="${paramName}_start" value="${paramConfig.default[0]}" />
            <span>to</span>
            <input type="date" id="${paramName}_end" name="${paramName}_end" value="${paramConfig.default[1]}" />
          </div>`;
          break;
      }
      
      html += `</div>`;
    });

    // Add smart suggestions section
    html += `
      <div class="smart-suggestions">
        <h3>💡 Smart Suggestions</h3>
        <p id="smartSuggestions">Based on your selections, we recommend including RSI and volume indicators for comprehensive technical analysis.</p>
      </div>
      
      <button type="submit">Generate Visualization</button>
    </form>
    
    <script>
      function updateRangeValue(paramName) {
        const minVal = document.getElementById(paramName + '_min').value;
        const maxVal = document.getElementById(paramName + '_max').value;
        document.getElementById(paramName + '_min_value').textContent = minVal;
        document.getElementById(paramName + '_max_value').textContent = maxVal;
      }
      
      function addKeyValueRow(paramName) {
        const container = document.getElementById(paramName + '_container');
        const newRow = document.createElement('div');
        newRow.className = 'keyvalue-row';
        newRow.style.display = 'flex';
        newRow.style.gap = '10px';
        newRow.style.marginBottom = '5px';
        newRow.innerHTML = \`
          <input type="text" name="\${paramName}_key[]" placeholder="Key" style="flex: 1;" />
          <input type="number" name="\${paramName}_value[]" placeholder="Value" style="width: 100px;" />
        \`;
        container.appendChild(newRow);
      }
      
      // Smart suggestion logic
      document.getElementById('visualizationConfig').addEventListener('change', updateSmartSuggestions);
      
      function updateSmartSuggestions() {
        // This would contain actual AI-powered suggestion logic
        const templateType = '${templateType}';
        let suggestion = '';
        
        if (templateType === 'stock') {
          const indicators = Array.from(document.querySelectorAll('input[name="indicators[]"]:checked')).map(cb => cb.value);
          if (!indicators.includes('rsi')) {
            suggestion = 'Consider adding RSI indicator to identify overbought/oversold conditions.';
          } else if (!indicators.includes('volume')) {
            suggestion = 'Volume analysis helps confirm price trends and identify potential reversals.';
          } else {
            suggestion = 'Your configuration looks comprehensive for technical analysis!';
          }
        }
        
        document.getElementById('smartSuggestions').textContent = suggestion || 'Adjust your parameters for optimal results.';
      }
    </script>
  </div>
</body>
</html>`;

    return html;
  }

  // Save user preferences
  saveUserPreferences(userId, preferences) {
    const preferencesPath = `/home/admin/.openclaw/workspace/user_preferences/${userId}.json`;
    const fs = require('fs');
    const path = require('path');
    
    // Ensure directory exists
    const dir = path.dirname(preferencesPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    
    fs.writeFileSync(preferencesPath, JSON.stringify(preferences, null, 2));
    return { success: true, path: preferencesPath };
  }

  // Load user preferences
  loadUserPreferences(userId) {
    const preferencesPath = `/home/admin/.openclaw/workspace/user_preferences/${userId}.json`;
    const fs = require('fs');
    
    if (!fs.existsSync(preferencesPath)) {
      return null;
    }
    
    const preferencesData = fs.readFileSync(preferencesPath, 'utf8');
    return JSON.parse(preferencesData);
  }
}

module.exports = VisualizationConfigUI;