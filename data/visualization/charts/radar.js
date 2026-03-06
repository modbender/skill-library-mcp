// Radar Chart Configuration
function generateRadarConfig(data, options = {}) {
  const {
    title = 'Multi-dimensional Analysis',
    labels = [],
    datasets = [],
    colorScheme = 'default'
  } = options;

  // Color schemes for multiple datasets
  const colorSchemes = {
    default: [
      { backgroundColor: 'rgba(255, 99, 132, 0.2)', borderColor: 'rgba(255, 99, 132, 1)' },
      { backgroundColor: 'rgba(54, 162, 235, 0.2)', borderColor: 'rgba(54, 162, 235, 1)' },
      { backgroundColor: 'rgba(255, 206, 86, 0.2)', borderColor: 'rgba(255, 206, 86, 1)' },
      { backgroundColor: 'rgba(75, 192, 192, 0.2)', borderColor: 'rgba(75, 192, 192, 1)' }
    ],
    financial: [
      { backgroundColor: 'rgba(255, 99, 132, 0.2)', borderColor: 'rgba(255, 99, 132, 1)' }, // Risk
      { backgroundColor: 'rgba(54, 162, 235, 0.2)', borderColor: 'rgba(54, 162, 235, 1)' }, // Return
      { backgroundColor: 'rgba(75, 192, 192, 0.2)', borderColor: 'rgba(75, 192, 192, 1)' }, // Liquidity
      { backgroundColor: 'rgba(153, 102, 255, 0.2)', borderColor: 'rgba(153, 102, 255, 1)' } // Stability
    ]
  };

  const colors = colorSchemes[colorScheme] || colorSchemes.default;

  // Ensure we have enough colors for all datasets
  const formattedDatasets = datasets.map((dataset, index) => ({
    label: dataset.label || `Dataset ${index + 1}`,
    data: dataset.data,
    ...colors[index % colors.length]
  }));

  return {
    type: 'radar',
    data: {
      labels: labels,
      datasets: formattedDatasets
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: title
        },
        legend: {
          display: formattedDatasets.length > 1
        }
      },
      scales: {
        r: {
          angleLines: {
            display: true
          },
          suggestedMin: 0,
          suggestedMax: Math.max(...datasets.flatMap(d => d.data)) * 1.1
        }
      }
    }
  };
}

module.exports = { generateRadarConfig };