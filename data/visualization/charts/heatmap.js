// Heatmap Chart Configuration
function generateHeatmapConfig(data, options = {}) {
  const {
    title = 'Correlation Matrix',
    xLabels = [],
    yLabels = [],
    colorScheme = 'viridis',
    showValues = true
  } = options;

  // Generate color scale based on scheme
  const colorSchemes = {
    viridis: ['#440154', '#482878', '#3e4989', '#31688e', '#26828e', '#1f9e89', '#35b779', '#6ece58', '#b5de2b', '#fde725'],
    plasma: ['#0d0887', '#46039f', '#7201a8', '#9c179e', '#bd3786', '#d8576b', '#ed7953', '#fb9f3a', '#fdca26', '#f0f921'],
    inferno: ['#000004', '#1b0c41', '#4a0c6b', '#781c6d', '#a52c60', '#cf4446', '#ed6925', '#fb9b06', '#e7c51c', '#fcffa4']
  };

  const colors = colorSchemes[colorScheme] || colorSchemes.viridis;
  
  // Normalize data to 0-1 range for color mapping
  const flatData = data.flat();
  const min = Math.min(...flatData);
  const max = Math.max(...flatData);
  const range = max - min || 1;

  const normalizedData = data.map(row => 
    row.map(value => (value - min) / range)
  );

  return {
    type: 'heatmap',
    data: {
      datasets: [{
        label: title,
        data: normalizedData.map((row, y) => 
          row.map((value, x) => ({
            x: xLabels[x] || x,
            y: yLabels[y] || y,
            v: data[y][x]
          }))
        ).flat(),
        backgroundColor: (context) => {
          const value = context.dataset.data[context.dataIndex].v;
          const normalized = (value - min) / range;
          const colorIndex = Math.floor(normalized * (colors.length - 1));
          return colors[colorIndex];
        },
        borderWidth: 1,
        borderColor: 'rgba(0,0,0,0.1)'
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: title
        },
        tooltip: {
          callbacks: {
            label: (context) => `${context.raw.x} vs ${context.raw.y}: ${context.raw.v.toFixed(2)}`
          }
        }
      },
      scales: {
        x: {
          type: 'category',
          labels: xLabels.length ? xLabels : data[0].map((_, i) => i),
          position: 'bottom'
        },
        y: {
          type: 'category',
          labels: yLabels.length ? yLabels : data.map((_, i) => i),
          reverse: true
        }
      }
    }
  };
}

module.exports = { generateHeatmapConfig };