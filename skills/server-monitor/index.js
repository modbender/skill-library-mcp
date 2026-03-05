#!/usr/bin/env node

/**
 * 服务器监控技能
 * 提供服务器状态监控功能
 */

const { execSync } = require('child_process');
const os = require('os');

class ServerMonitor {
  constructor() {
    this.name = 'server-monitor';
    this.version = '1.0.0';
  }

  /**
   * 获取系统信息
   */
  getSystemInfo() {
    try {
      const uptime = this.formatUptime(os.uptime());
      const hostname = os.hostname();
      const platform = os.platform();
      const arch = os.arch();
      const release = os.release();
      
      return {
        hostname,
        platform: `${platform} ${arch}`,
        kernel: release,
        uptime,
        nodeVersion: process.version,
        cpus: os.cpus().length
      };
    } catch (error) {
      return { error: `获取系统信息失败: ${error.message}` };
    }
  }

  /**
   * 获取内存使用情况
   */
  getMemoryUsage() {
    try {
      const totalMem = os.totalmem();
      const freeMem = os.freemem();
      const usedMem = totalMem - freeMem;
      const usagePercent = ((usedMem / totalMem) * 100).toFixed(2);
      
      return {
        total: this.formatBytes(totalMem),
        used: this.formatBytes(usedMem),
        free: this.formatBytes(freeMem),
        usagePercent: `${usagePercent}%`
      };
    } catch (error) {
      return { error: `获取内存信息失败: ${error.message}` };
    }
  }

  /**
   * 获取磁盘使用情况
   */
  getDiskUsage() {
    try {
      const output = execSync('df -h /', { encoding: 'utf8' });
      const lines = output.trim().split('\n');
      if (lines.length < 2) return { error: '无法获取磁盘信息' };
      
      const parts = lines[1].split(/\s+/);
      return {
        filesystem: parts[0],
        size: parts[1],
        used: parts[2],
        available: parts[3],
        usagePercent: parts[4],
        mounted: parts[5]
      };
    } catch (error) {
      return { error: `获取磁盘信息失败: ${error.message}` };
    }
  }

  /**
   * 获取CPU负载
   */
  getCPULoad() {
    try {
      const loadavg = os.loadavg();
      return {
        '1min': loadavg[0].toFixed(2),
        '5min': loadavg[1].toFixed(2),
        '15min': loadavg[2].toFixed(2)
      };
    } catch (error) {
      return { error: `获取CPU负载失败: ${error.message}` };
    }
  }

  /**
   * 获取运行中的进程
   */
  getRunningProcesses() {
    try {
      const output = execSync('ps aux --sort=-%cpu | head -6', { encoding: 'utf8' });
      return output;
    } catch (error) {
      return `获取进程信息失败: ${error.message}`;
    }
  }

  /**
   * 获取完整服务器状态报告
   */
  getFullReport() {
    const systemInfo = this.getSystemInfo();
    const memoryUsage = this.getMemoryUsage();
    const diskUsage = this.getDiskUsage();
    const cpuLoad = this.getCPULoad();
    const processes = this.getRunningProcesses();

    return {
      timestamp: new Date().toISOString(),
      system: systemInfo,
      memory: memoryUsage,
      disk: diskUsage,
      cpu: cpuLoad,
      topProcesses: processes
    };
  }

  /**
   * 格式化运行时间
   */
  formatUptime(seconds) {
    const days = Math.floor(seconds / (24 * 60 * 60));
    const hours = Math.floor((seconds % (24 * 60 * 60)) / (60 * 60));
    const minutes = Math.floor((seconds % (60 * 60)) / 60);
    
    if (days > 0) return `${days}天 ${hours}小时 ${minutes}分钟`;
    if (hours > 0) return `${hours}小时 ${minutes}分钟`;
    return `${minutes}分钟`;
  }

  /**
   * 格式化字节大小
   */
  formatBytes(bytes) {
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    let value = bytes;
    let unitIndex = 0;
    
    while (value >= 1024 && unitIndex < units.length - 1) {
      value /= 1024;
      unitIndex++;
    }
    
    return `${value.toFixed(2)} ${units[unitIndex]}`;
  }

  /**
   * 运行技能
   */
  run() {
    try {
      const report = this.getFullReport();
      console.log(JSON.stringify(report, null, 2));
      return report;
    } catch (error) {
      console.error(`技能执行失败: ${error.message}`);
      return { error: error.message };
    }
  }
}

// 如果直接运行此文件
if (require.main === module) {
  const monitor = new ServerMonitor();
  monitor.run();
}

module.exports = ServerMonitor;