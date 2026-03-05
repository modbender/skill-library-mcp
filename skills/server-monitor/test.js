#!/usr/bin/env node

/**
 * 服务器监控技能测试
 */

const ServerMonitor = require('./index.js');

console.log('=== 服务器监控技能测试 ===\n');

const monitor = new ServerMonitor();

// 测试系统信息
console.log('1. 系统信息:');
console.log(monitor.getSystemInfo());
console.log();

// 测试内存使用
console.log('2. 内存使用情况:');
console.log(monitor.getMemoryUsage());
console.log();

// 测试磁盘使用
console.log('3. 磁盘使用情况:');
console.log(monitor.getDiskUsage());
console.log();

// 测试CPU负载
console.log('4. CPU负载:');
console.log(monitor.getCPULoad());
console.log();

// 测试完整报告
console.log('5. 完整报告:');
const report = monitor.getFullReport();
console.log(JSON.stringify(report, null, 2));

console.log('\n=== 测试完成 ===');