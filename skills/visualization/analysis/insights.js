// Chart Analysis and Insights Generation
class ChartInsightsGenerator {
  constructor() {
    this.insightTemplates = {
      stock: {
        bullish: 'The price trend shows strong upward momentum with increasing volume, indicating potential continued growth.',
        bearish: 'The declining price trend combined with high volume suggests selling pressure may continue.',
        consolidation: 'Price is trading in a narrow range, suggesting accumulation phase before next major move.',
        rsi_overbought: 'RSI above 70 indicates overbought conditions, potential pullback expected.',
        rsi_oversold: 'RSI below 30 indicates oversold conditions, potential bounce expected.',
        ma_support: 'Price is finding support at the 50-day moving average, suggesting underlying strength.',
        ma_resistance: 'Price is facing resistance at the 50-day moving average, indicating potential reversal.'
      },
      portfolio: {
        diversified: 'Your portfolio shows good diversification across multiple sectors, reducing concentration risk.',
        concentrated: 'High concentration in technology sector increases exposure to sector-specific risks.',
        risk_balanced: 'Risk metrics indicate a balanced risk-return profile suitable for moderate investors.',
        high_risk: 'High volatility and drawdown suggest aggressive risk profile, suitable for experienced investors.',
        low_risk: 'Low volatility indicates conservative allocation, suitable for risk-averse investors.'
      },
      macro: {
        gdp_growth: 'Strong GDP growth indicates healthy economic expansion and potential investment opportunities.',
        inflation_concern: 'Rising inflation may impact purchasing power and require inflation-hedging strategies.',
        unemployment_improving: 'Declining unemployment rate suggests improving labor market conditions.',
        interest_rate_impact: 'Rising interest rates may impact borrowing costs and equity valuations.'
      },
      crypto: {
        high_correlation: 'High correlation between BTC and ETH suggests similar market drivers and limited diversification benefit.',
        volatility_warning: 'Extreme price volatility requires careful position sizing and risk management.',
        market_cap_dominance: 'BTC dominance indicates market leadership and potential stability compared to altcoins.',
        volume_confirmation: 'High trading volume confirms price movements and suggests strong market participation.'
      }
    };
  }

  // Generate insights based on chart data and context
  generateInsights(chartType, data, context = {}) {
    const insights = [];
    
    switch (chartType) {
      case 'stock':
        insights.push(...this.generateStockInsights(data, context));
        break;
      case 'portfolio':
        insights.push(...this.generatePortfolioInsights(data, context));
        break;
      case 'macro':
        insights.push(...this.generateMacroInsights(data, context));
        break;
      case 'crypto':
        insights.push(...this.generateCryptoInsights(data, context));
        break;
      default:
        insights.push('Analysis summary will be generated based on your chart data.');
    }
    
    return insights;
  }

  generateStockInsights(data, context) {
    const insights = [];
    const { symbol, indicators } = context;
    
    // Price trend analysis
    if (data.price && data.price.length > 1) {
      const firstPrice = data.price[0];
      const lastPrice = data.price[data.price.length - 1];
      const changePercent = ((lastPrice - firstPrice) / firstPrice) * 100;
      
      if (changePercent > 5) {
        insights.push(this.insightTemplates.stock.bullish);
      } else if (changePercent < -5) {
        insights.push(this.insightTemplates.stock.bearish);
      } else {
        insights.push(this.insightTemplates.stock.consolidation);
      }
    }
    
    // RSI analysis
    if (indicators.includes('rsi') && data.rsi) {
      const latestRSI = data.rsi[data.rsi.length - 1];
      if (latestRSI > 70) {
        insights.push(this.insightTemplates.stock.rsi_overbought);
      } else if (latestRSI < 30) {
        insights.push(this.insightTemplates.stock.rsi_oversold);
      }
    }
    
    // Moving average analysis
    if (indicators.includes('ma50') && data.price && data.ma50) {
      const latestPrice = data.price[data.price.length - 1];
      const latestMA = data.ma50[data.ma50.length - 1];
      
      if (latestPrice > latestMA && Math.abs(latestPrice - latestMA) / latestMA < 0.02) {
        insights.push(this.insightTemplates.stock.ma_support);
      } else if (latestPrice < latestMA && Math.abs(latestPrice - latestMA) / latestMA < 0.02) {
        insights.push(this.insightTemplates.stock.ma_resistance);
      }
    }
    
    return insights;
  }

  generatePortfolioInsights(data, context) {
    const insights = [];
    const { assets } = context;
    
    // Diversification analysis
    const assetCount = Object.keys(assets).length;
    const maxAllocation = Math.max(...Object.values(assets));
    
    if (assetCount >= 3 && maxAllocation < 50) {
      insights.push(this.insightTemplates.portfolio.diversified);
    } else if (maxAllocation > 60) {
      insights.push(this.insightTemplates.portfolio.concentrated);
    }
    
    // Risk analysis
    if (context.riskMetrics) {
      const { volatility, drawdown } = context.riskMetrics;
      
      if (volatility > 20 || Math.abs(drawdown) > 15) {
        insights.push(this.insightTemplates.portfolio.high_risk);
      } else if (volatility < 10 && Math.abs(drawdown) < 8) {
        insights.push(this.insightTemplates.portfolio.low_risk);
      } else {
        insights.push(this.insightTemplates.portfolio.risk_balanced);
      }
    }
    
    return insights;
  }

  generateMacroInsights(data, context) {
    const insights = [];
    const { indicators, countries } = context;
    
    if (indicators.includes('gdp') && data.gdp) {
      // Check if any country shows strong growth
      const usGDP = data.gdp.US;
      if (usGDP && usGDP[usGDP.length - 1] > usGDP[usGDP.length - 2]) {
        insights.push(this.insightTemplates.macro.gdp_growth);
      }
    }
    
    if (indicators.includes('inflation') && data.inflation) {
      const usInflation = data.inflation.US;
      if (usInflation && usInflation[usInflation.length - 1] > 3) {
        insights.push(this.insightTemplates.macro.inflation_concern);
      }
    }
    
    if (indicators.includes('unemployment') && data.unemployment) {
      const usUnemployment = data.unemployment.US;
      if (usUnemployment && usUnemployment[usUnemployment.length - 1] < usUnemployment[usUnemployment.length - 2]) {
        insights.push(this.insightTemplates.macro.unemployment_improving);
      }
    }
    
    if (indicators.includes('interest_rate') && data.interest_rate) {
      const usInterestRate = data.interest_rate.US;
      if (usInterestRate && usInterestRate[usInterestRate.length - 1] > usInterestRate[usInterestRate.length - 2]) {
        insights.push(this.insightTemplates.macro.interest_rate_impact);
      }
    }
    
    return insights;
  }

  generateCryptoInsights(data, context) {
    const insights = [];
    const { symbols } = context;
    
    // Correlation analysis
    if (symbols.length > 1 && data.correlation) {
      const correlationValue = data.correlation[0][1]; // Simplified
      if (correlationValue > 0.8) {
        insights.push(this.insightTemplates.crypto.high_correlation);
      }
    }
    
    // Volatility analysis
    if (data.price && data.price.BTC) {
      const btcPrices = data.price.BTC;
      const minPrice = Math.min(...btcPrices);
      const maxPrice = Math.max(...btcPrices);
      const volatility = ((maxPrice - minPrice) / minPrice) * 100;
      
      if (volatility > 20) {
        insights.push(this.insightTemplates.crypto.volatility_warning);
      }
    }
    
    // Market cap analysis
    if (data.market_cap && data.market_cap.BTC) {
      const btcMarketCap = data.market_cap.BTC[data.market_cap.BTC.length - 1];
      const totalMarketCap = symbols.reduce((sum, symbol) => 
        sum + (data.market_cap[symbol]?.[data.market_cap[symbol].length - 1] || 0), 0
      );
      const btcDominance = (btcMarketCap / totalMarketCap) * 100;
      
      if (btcDominance > 50) {
        insights.push(this.insightTemplates.crypto.market_cap_dominance);
      }
    }
    
    // Volume analysis
    if (data.volume && data.volume.BTC) {
      const recentVolume = data.volume.BTC.slice(-5);
      const avgVolume = recentVolume.reduce((sum, vol) => sum + vol, 0) / recentVolume.length;
      const prevAvgVolume = data.volume.BTC.slice(-10, -5).reduce((sum, vol) => sum + vol, 0) / 5;
      
      if (avgVolume > prevAvgVolume * 1.2) {
        insights.push(this.insightTemplates.crypto.volume_confirmation);
      }
    }
    
    return insights;
  }

  // Generate comparison insights between two charts
  generateComparisonInsights(chart1, chart2, chartType) {
    const insights = [];
    
    // This would contain logic to compare two datasets
    insights.push(`Comparing ${chart1.title} vs ${chart2.title}`);
    insights.push('Key differences and similarities will be highlighted here.');
    
    return insights;
  }

  // Add annotations to charts
  addChartAnnotations(chartConfig, insights) {
    // This would modify chart configuration to include annotations
    // For now, return the insights as metadata
    return {
      ...chartConfig,
      metadata: {
        ...chartConfig.metadata,
        insights: insights
      }
    };
  }
}

module.exports = ChartInsightsGenerator;