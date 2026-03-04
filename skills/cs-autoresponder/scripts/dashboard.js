#!/usr/bin/env node
/**
 * dashboard.js - 일일 CS 요약 대시보드
 * 특정 날짜의 CS 로그를 분석하여 통계 생성
 */

const fs = require('fs');
const path = require('path');
const CSLogger = require('../lib/logger');

function loadConfig(configPath) {
  const fullPath = path.resolve(configPath);
  
  if (!fs.existsSync(fullPath)) {
    console.error(`❌ Config file not found: ${fullPath}`);
    process.exit(1);
  }

  return JSON.parse(fs.readFileSync(fullPath, 'utf-8'));
}

function printDashboard(config, date) {
  const logger = new CSLogger(config);
  const stats = logger.generateStats(date);

  console.log(`\n📊 CS 대시보드 - ${config.name} (${date})`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  console.log(`총 문의수: ${stats.totalInquiries}건`);
  console.log(`자동 처리: ${stats.autoResponded}건 (${stats.autoResponseRate}%)`);
  console.log(`에스컬레이션: ${stats.escalated}건 (${(100 - parseFloat(stats.autoResponseRate)).toFixed(1)}%)`);
  console.log();

  // 카테고리별
  if (Object.keys(stats.categoryBreakdown).length > 0) {
    console.log(`카테고리별:`);
    Object.entries(stats.categoryBreakdown)
      .sort((a, b) => b[1] - a[1])
      .forEach(([category, count]) => {
        console.log(`  • ${category}: ${count}건`);
      });
    console.log();
  }

  // 채널별
  if (Object.keys(stats.channelBreakdown).length > 0) {
    console.log(`채널별:`);
    Object.entries(stats.channelBreakdown)
      .sort((a, b) => b[1] - a[1])
      .forEach(([channel, count]) => {
        const channelEmoji = {
          instagram: '📷',
          kakao: '💬',
          email: '📧'
        }[channel] || '📱';
        console.log(`  ${channelEmoji} ${channel}: ${count}건`);
      });
    console.log();
  }

  console.log(`평균 응답시간: ${stats.avgResponseTime}초`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`);

  // 개선 제안
  if (stats.totalInquiries > 0) {
    const autoRate = parseFloat(stats.autoResponseRate);
    
    if (autoRate < 70) {
      console.log(`💡 자동 응답율이 낮습니다 (${stats.autoResponseRate}%). FAQ를 보강하세요.`);
    } else if (autoRate > 90) {
      console.log(`🎉 자동 응답율이 우수합니다 (${stats.autoResponseRate}%)!`);
    }

    if (stats.escalated > 10) {
      console.log(`⚠️  에스컬레이션이 많습니다 (${stats.escalated}건). 복잡한 문의가 증가했는지 확인하세요.`);
    }

    console.log();
  }
}

// CLI
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.includes('--help') || args.includes('-h')) {
    console.log(`
Usage: node dashboard.js --config <path> [--date <YYYY-MM-DD>]

Options:
  --config    고객사 설정 파일 경로 (필수)
  --date      조회할 날짜 (기본값: 오늘)

Example:
  node dashboard.js --config config/example.json --date 2026-02-18
    `);
    process.exit(0);
  }

  const configPath = args[args.indexOf('--config') + 1];
  const dateIndex = args.indexOf('--date');
  const date = dateIndex !== -1 
    ? args[dateIndex + 1] 
    : new Date().toISOString().split('T')[0];

  if (!configPath) {
    console.error('❌ Missing --config argument. Use --help for usage.');
    process.exit(1);
  }

  // 날짜 형식 검증
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) {
    console.error('❌ Invalid date format. Use YYYY-MM-DD.');
    process.exit(1);
  }

  const config = loadConfig(configPath);
  printDashboard(config, date);
}

module.exports = printDashboard;
