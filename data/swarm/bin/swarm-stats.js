#!/usr/bin/env node
/**
 * Swarm Statistics Viewer
 * View performance metrics and edge cases
 */

const { metrics } = require('../lib/metrics');

const args = process.argv.slice(2);
const command = args[0] || 'report';

switch (command) {
  case 'report':
  case 'stats': {
    const days = parseInt(args[1]) || 7;
    const report = metrics.getReport(days);
    
    console.log('\n🐝 SWARM PERFORMANCE REPORT');
    console.log('═'.repeat(50));
    console.log(`Period: ${report.period}`);
    console.log('');
    
    if (report.error) {
      console.log(`ℹ️  ${report.error}`);
      console.log('Run some Swarm tasks to start collecting metrics.');
    } else {
      console.log(`Executions:    ${report.executions}`);
      console.log(`Total Tasks:   ${report.tasks}`);
      console.log(`Success Rate:  ${report.successRate}`);
      console.log(`Avg Speedup:   ${report.avgSpeedup}`);
      console.log(`Total Time:    ${(report.durationMs / 1000 / 60).toFixed(1)} minutes`);
      
      if (report.dailyBreakdown) {
        console.log('\n📅 Daily Breakdown:');
        Object.entries(report.dailyBreakdown).forEach(([date, day]) => {
          console.log(`  ${date}: ${day.executions} runs, ${day.totalTasks} tasks, ${day.avgSpeedup?.toFixed(1) || 'N/A'}x avg`);
        });
      }
    }
    console.log('');
    break;
  }
  
  case 'edge-cases':
  case 'edges':
  case 'issues': {
    const limit = parseInt(args[1]) || 20;
    const edgeCases = metrics.getEdgeCases(limit);
    
    console.log('\n🔍 SWARM EDGE CASES');
    console.log('═'.repeat(50));
    
    if (edgeCases.length === 0) {
      console.log('ℹ️  No edge cases logged yet. This is good!');
    } else {
      edgeCases.forEach((ec, i) => {
        console.log(`\n${i + 1}. [${ec.type.toUpperCase()}] ${ec.description}`);
        console.log(`   Time: ${ec.timestamp}`);
        if (ec.suggestedFix) {
          console.log(`   Fix: ${ec.suggestedFix}`);
        }
      });
    }
    console.log('');
    break;
  }
  
  case 'clear': {
    const fs = require('fs');
    const path = require('path');
    const dir = path.join(process.env.HOME, '.config/clawdbot/swarm-metrics');
    
    if (fs.existsSync(dir)) {
      fs.rmSync(dir, { recursive: true });
      console.log('✓ Metrics cleared');
    } else {
      console.log('ℹ️  No metrics to clear');
    }
    break;
  }
  
  default:
    console.log(`
🐝 Swarm Statistics

Usage:
  swarm-stats report [days]    Show performance report (default: 7 days)
  swarm-stats edge-cases [n]   Show recent edge cases (default: 20)
  swarm-stats clear            Clear all metrics

Examples:
  swarm-stats report 30        Show last 30 days
  swarm-stats edges 10         Show last 10 edge cases
`);
}
