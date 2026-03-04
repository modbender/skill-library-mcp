/**
 * 统计追踪器
 * Statistics Tracker
 * 
 * @description 追踪和统计卡片发送的相关数据
 * @author OpenClaw Team
 * @version 1.0.0
 */

class StatsTracker {
  constructor(config = {}) {
    this.config = {
      enableTracking: true,
      retentionDays: 30,
      aggregationInterval: 3600000, // 1小时
      ...config
    };
    
    this.stats = {
      totalSent: 0,
      totalSuccess: 0,
      totalFailed: 0,
      byType: {},
      byFormat: {},
      byHour: {},
      responseTimes: [],
      lastReset: new Date().toISOString()
    };
    
    this.hourlyStats = new Map();
    this.dailyStats = new Map();
    
    // 启动定时任务
    this.startPeriodicTasks();
    
    console.log('📊 StatsTracker initialized');
  }

  /**
   * 记录发送事件
   * @param {string} templateType - 模板类型
   * @param {string} format - 格式类型
   * @param {boolean} success - 是否成功
   * @param {number} duration - 耗时（毫秒）
   */
  recordSend(templateType, format, success, duration) {
    if (!this.config.enableTracking) return;
    
    const timestamp = Date.now();
    const hourKey = this.getHourKey(timestamp);
    const dayKey = this.getDayKey(timestamp);
    
    // 更新总体统计
    this.stats.totalSent++;
    if (success) {
      this.stats.totalSuccess++;
    } else {
      this.stats.totalFailed++;
    }
    
    // 按类型统计
    if (!this.stats.byType[templateType]) {
      this.stats.byType[templateType] = {
        total: 0,
        success: 0,
        failed: 0,
        avgDuration: 0
      };
    }
    this.stats.byType[templateType].total++;
    if (success) {
      this.stats.byType[templateType].success++;
    } else {
      this.stats.byType[templateType].failed++;
    }
    this.updateAverageDuration(this.stats.byType[templateType], duration);
    
    // 按格式统计
    if (!this.stats.byFormat[format]) {
      this.stats.byFormat[format] = {
        total: 0,
        success: 0,
        failed: 0,
        avgDuration: 0
      };
    }
    this.stats.byFormat[format].total++;
    if (success) {
      this.stats.byFormat[format].success++;
    } else {
      this.stats.byFormat[format].failed++;
    }
    this.updateAverageDuration(this.stats.byFormat[format], duration);
    
    // 按小时统计
    this.updateHourlyStats(hourKey, templateType, format, success, duration);
    
    // 按天统计
    this.updateDailyStats(dayKey, templateType, format, success, duration);
    
    // 记录响应时间
    if (duration > 0) {
      this.stats.responseTimes.push({
        timestamp,
        duration,
        templateType,
        format,
        success
      });
      
      // 限制响应时间记录数量
      if (this.stats.responseTimes.length > 1000) {
        this.stats.responseTimes = this.stats.responseTimes.slice(-1000);
      }
    }
  }

  /**
   * 更新平均耗时
   */
  updateAverageDuration(stats, duration) {
    const totalDuration = stats.avgDuration * (stats.total - 1) + duration;
    stats.avgDuration = totalDuration / stats.total;
  }

  /**
   * 更新小时统计
   */
  updateHourlyStats(hourKey, templateType, format, success, duration) {
    if (!this.hourlyStats.has(hourKey)) {
      this.hourlyStats.set(hourKey, {
        hour: hourKey,
        total: 0,
        success: 0,
        failed: 0,
        byType: {},
        byFormat: {},
        avgDuration: 0
      });
    }
    
    const hourStats = this.hourlyStats.get(hourKey);
    hourStats.total++;
    if (success) {
      hourStats.success++;
    } else {
      hourStats.failed++;
    }
    
    // 按类型
    if (!hourStats.byType[templateType]) {
      hourStats.byType[templateType] = { total: 0, success: 0, failed: 0 };
    }
    hourStats.byType[templateType].total++;
    if (success) {
      hourStats.byType[templateType].success++;
    } else {
      hourStats.byType[templateType].failed++;
    }
    
    // 按格式
    if (!hourStats.byFormat[format]) {
      hourStats.byFormat[format] = { total: 0, success: 0, failed: 0 };
    }
    hourStats.byFormat[format].total++;
    if (success) {
      hourStats.byFormat[format].success++;
    } else {
      hourStats.byFormat[format].failed++;
    }
    
    this.updateAverageDuration(hourStats, duration);
  }

  /**
   * 更新日统计
   */
  updateDailyStats(dayKey, templateType, format, success, duration) {
    if (!this.dailyStats.has(dayKey)) {
      this.dailyStats.set(dayKey, {
        day: dayKey,
        total: 0,
        success: 0,
        failed: 0,
        byType: {},
        byFormat: {},
        avgDuration: 0
      });
    }
    
    const dayStats = this.dailyStats.get(dayKey);
    dayStats.total++;
    if (success) {
      dayStats.success++;
    } else {
      dayStats.failed++;
    }
    
    // 按类型
    if (!dayStats.byType[templateType]) {
      dayStats.byType[templateType] = { total: 0, success: 0, failed: 0 };
    }
    dayStats.byType[templateType].total++;
    if (success) {
      dayStats.byType[templateType].success++;
    } else {
      dayStats.byType[templateType].failed++;
    }
    
    // 按格式
    if (!dayStats.byFormat[format]) {
      dayStats.byFormat[format] = { total: 0, success: 0, failed: 0 };
    }
    dayStats.byFormat[format].total++;
    if (success) {
      dayStats.byFormat[format].success++;
    } else {
      dayStats.byFormat[format].failed++;
    }
    
    this.updateAverageDuration(dayStats, duration);
  }

  /**
   * 获取统计信息
   */
  getStats() {
    const now = Date.now();
    
    return {
      summary: {
        totalSent: this.stats.totalSent,
        totalSuccess: this.stats.totalSuccess,
        totalFailed: this.stats.totalFailed,
        successRate: this.stats.totalSent > 0 
          ? Math.round((this.stats.totalSuccess / this.stats.totalSent) * 100)
          : 0,
        lastReset: this.stats.lastReset
      },
      byType: this.stats.byType,
      byFormat: this.stats.byFormat,
      hourly: this.getRecentHourlyStats(24),
      daily: this.getRecentDailyStats(7),
      performance: this.getPerformanceStats(),
      trends: this.getTrends()
    };
  }

  /**
   * 获取性能统计
   */
  getPerformanceStats() {
    if (this.stats.responseTimes.length === 0) {
      return {
        avgDuration: 0,
        minDuration: 0,
        maxDuration: 0,
        medianDuration: 0,
        p95Duration: 0
      };
    }
    
    const durations = this.stats.responseTimes.map(r => r.duration).sort((a, b) => a - b);
    const avgDuration = durations.reduce((sum, d) => sum + d, 0) / durations.length;
    const medianDuration = durations[Math.floor(durations.length * 0.5)];
    const p95Duration = durations[Math.floor(durations.length * 0.95)];
    
    return {
      avgDuration: Math.round(avgDuration),
      minDuration: durations[0],
      maxDuration: durations[durations.length - 1],
      medianDuration,
      p95Duration
    };
  }

  /**
   * 获取趋势分析
   */
  getTrends() {
    const hourlyData = this.getRecentHourlyStats(24);
    const dailyData = this.getRecentDailyStats(7);
    
    return {
      hourly: this.analyzeTrend(hourlyData),
      daily: this.analyzeTrend(dailyData),
      peakHours: this.findPeakHours(hourlyData),
      slowestTypes: this.findSlowestTypes(),
      mostFailedTypes: this.findMostFailedTypes()
    };
  }

  /**
   * 分析趋势
   */
  analyzeTrend(data) {
    if (data.length < 2) return { trend: 'stable', change: 0 };
    
    const recent = data.slice(-Math.ceil(data.length * 0.3));
    const older = data.slice(0, Math.ceil(data.length * 0.3));
    
    const recentAvg = recent.reduce((sum, item) => sum + item.total, 0) / recent.length;
    const olderAvg = older.reduce((sum, item) => sum + item.total, 0) / older.length;
    
    const change = olderAvg > 0 ? ((recentAvg - olderAvg) / olderAvg) * 100 : 0;
    
    let trend = 'stable';
    if (change > 20) trend = 'increasing';
    else if (change < -20) trend = 'decreasing';
    
    return { trend, change: Math.round(change) };
  }

  /**
   * 查找高峰时段
   */
  findPeakHours(hourlyData) {
    return hourlyData
      .sort((a, b) => b.total - a.total)
      .slice(0, 3)
      .map(item => ({
        hour: item.hour,
        total: item.total,
        successRate: item.total > 0 ? Math.round((item.success / item.total) * 100) : 0
      }));
  }

  /**
   * 查找最慢的类型
   */
  findSlowestTypes() {
    const typeStats = Object.entries(this.stats.byType)
      .sort(([,a], [,b]) => b.avgDuration - a.avgDuration)
      .slice(0, 3)
      .map(([type, stats]) => ({
        type,
        avgDuration: Math.round(stats.avgDuration),
        total: stats.total
      }));
    
    return typeStats;
  }

  /**
   * 查找失败最多的类型
   */
  findMostFailedTypes() {
    const typeStats = Object.entries(this.stats.byType)
      .filter(([,stats]) => stats.total > 0)
      .sort(([,a], [,b]) => (b.failed / b.total) - (a.failed / a.total))
      .slice(0, 3)
      .map(([type, stats]) => ({
        type,
        failureRate: Math.round((stats.failed / stats.total) * 100),
        failed: stats.failed,
        total: stats.total
      }));
    
    return typeStats;
  }

  /**
   * 获取最近的小时统计
   */
  getRecentHourlyStats(hours) {
    const now = Date.now();
    const stats = [];
    
    for (let i = hours - 1; i >= 0; i--) {
      const hourTime = now - (i * 3600000);
      const hourKey = this.getHourKey(hourTime);
      const hourStats = this.hourlyStats.get(hourKey);
      
      if (hourStats) {
        stats.push({
          hour: hourKey,
          total: hourStats.total,
          success: hourStats.success,
          failed: hourStats.failed,
          successRate: hourStats.total > 0 ? Math.round((hourStats.success / hourStats.total) * 100) : 0,
          avgDuration: Math.round(hourStats.avgDuration)
        });
      } else {
        stats.push({
          hour: hourKey,
          total: 0,
          success: 0,
          failed: 0,
          successRate: 0,
          avgDuration: 0
        });
      }
    }
    
    return stats;
  }

  /**
   * 获取最近的日统计
   */
  getRecentDailyStats(days) {
    const now = Date.now();
    const stats = [];
    
    for (let i = days - 1; i >= 0; i--) {
      const dayTime = now - (i * 86400000);
      const dayKey = this.getDayKey(dayTime);
      const dayStats = this.dailyStats.get(dayKey);
      
      if (dayStats) {
        stats.push({
          day: dayKey,
          total: dayStats.total,
          success: dayStats.success,
          failed: dayStats.failed,
          successRate: dayStats.total > 0 ? Math.round((dayStats.success / dayStats.total) * 100) : 0,
          avgDuration: Math.round(dayStats.avgDuration)
        });
      } else {
        stats.push({
          day: dayKey,
          total: 0,
          success: 0,
          failed: 0,
          successRate: 0,
          avgDuration: 0
        });
      }
    }
    
    return stats;
  }

  /**
   * 获取小时键
   */
  getHourKey(timestamp) {
    const date = new Date(timestamp);
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}-${String(date.getHours()).padStart(2, '0')}`;
  }

  /**
   * 获取日键
   */
  getDayKey(timestamp) {
    const date = new Date(timestamp);
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
  }

  /**
   * 启动定时任务
   */
  startPeriodicTasks() {
    // 每小时清理过期数据
    setInterval(() => {
      this.cleanupOldData();
    }, 3600000); // 1小时
    
    // 每天生成报告
    setInterval(() => {
      this.generateDailyReport();
    }, 86400000); // 24小时
    
    console.log('⏰ 定时任务已启动');
  }

  /**
   * 清理过期数据
   */
  cleanupOldData() {
    const cutoffTime = Date.now() - (this.config.retentionDays * 86400000);
    
    // 清理小时统计
    for (const [key, stats] of this.hourlyStats) {
      const hourTime = new Date(stats.hour.replace(/-(\d+)$/, 'T$1:00:00')).getTime();
      if (hourTime < cutoffTime) {
        this.hourlyStats.delete(key);
      }
    }
    
    // 清理日统计
    for (const [key, stats] of this.dailyStats) {
      const dayTime = new Date(stats.day).getTime();
      if (dayTime < cutoffTime) {
        this.dailyStats.delete(key);
      }
    }
    
    // 清理响应时间记录
    this.stats.responseTimes = this.stats.responseTimes.filter(
      record => record.timestamp >= cutoffTime
    );
    
    console.log(`🧹 清理了过期数据 (保留${this.config.retentionDays}天)`);
  }

  /**
   * 生成日报
   */
  generateDailyReport() {
    const stats = this.getStats();
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    const dayKey = this.getDayKey(yesterday.getTime());
    const yesterdayStats = this.dailyStats.get(dayKey);
    
    if (yesterdayStats) {
      console.log(`📈 昨日统计报告 (${dayKey}):`);
      console.log(`  - 总发送: ${yesterdayStats.total}`);
      console.log(`  - 成功: ${yesterdayStats.success}`);
      console.log(`  - 失败: ${yesterdayStats.failed}`);
      console.log(`  - 成功率: ${yesterdayStats.total > 0 ? Math.round((yesterdayStats.success / yesterdayStats.total) * 100) : 0}%`);
      console.log(`  - 平均耗时: ${Math.round(yesterdayStats.avgDuration)}ms`);
    }
  }

  /**
   * 导出统计报告
   */
  exportReport(format = 'json') {
    const stats = this.getStats();
    
    switch (format) {
      case 'json':
        return JSON.stringify(stats, null, 2);
      
      case 'csv':
        return this.generateCSVReport(stats);
      
      case 'markdown':
        return this.generateMarkdownReport(stats);
      
      default:
        throw new Error(`不支持的报告格式: ${format}`);
    }
  }

  /**
   * 生成CSV报告
   */
  generateCSVReport(stats) {
    let csv = 'Type,Format,Total,Success,Failed,Success Rate,Avg Duration\n';
    
    // 按类型统计
    for (const [type, typeStats] of Object.entries(stats.byType)) {
      csv += `${type},all,${typeStats.total},${typeStats.success},${typeStats.failed},${Math.round((typeStats.success / typeStats.total) * 100)}%,${Math.round(typeStats.avgDuration)}\n`;
    }
    
    // 按格式统计
    for (const [format, formatStats] of Object.entries(stats.byFormat)) {
      csv += `all,${format},${formatStats.total},${formatStats.success},${formatStats.failed},${Math.round((formatStats.success / formatStats.total) * 100)}%,${Math.round(formatStats.avgDuration)}\n`;
    }
    
    return csv;
  }

  /**
   * 生成Markdown报告
   */
  generateMarkdownReport(stats) {
    let md = '# 飞书卡片发送统计报告\n\n';
    
    // 总体统计
    md += '## 总体统计\n\n';
    md += `| 指标 | 数值 |\n`;
    md += `|------|------|\n`;
    md += `| 总发送数 | ${stats.summary.totalSent} |\n`;
    md += `| 成功数 | ${stats.summary.totalSuccess} |\n`;
    md += `| 失败数 | ${stats.summary.totalFailed} |\n`;
    md += `| 成功率 | ${stats.summary.successRate}% |\n\n`;
    
    // 按类型统计
    md += '## 按类型统计\n\n';
    md += '| 类型 | 总数 | 成功 | 失败 | 成功率 | 平均耗时 |\n';
    md += '|------|------|------|------|--------|----------|\n';
    for (const [type, typeStats] of Object.entries(stats.byType)) {
      md += `| ${type} | ${typeStats.total} | ${typeStats.success} | ${typeStats.failed} | ${Math.round((typeStats.success / typeStats.total) * 100)}% | ${Math.round(typeStats.avgDuration)}ms |\n`;
    }
    
    return md;
  }

  /**
   * 重置统计
   */
  reset() {
    this.stats = {
      totalSent: 0,
      totalSuccess: 0,
      totalFailed: 0,
      byType: {},
      byFormat: {},
      byHour: {},
      responseTimes: [],
      lastReset: new Date().toISOString()
    };
    
    this.hourlyStats.clear();
    this.dailyStats.clear();
    
    console.log('📊 统计已重置');
  }

  /**
   * 更新配置
   */
  updateConfig(newConfig) {
    this.config = { ...this.config, ...newConfig };
    
    if (!this.config.enableTracking) {
      console.log('⚠️ 统计追踪已禁用');
    }
  }

  /**
   * 获取版本信息
   */
  getVersion() {
    return {
      version: '1.0.0',
      buildDate: '2026-02-28',
      module: 'StatsTracker',
      trackingEnabled: this.config.enableTracking,
      retentionDays: this.config.retentionDays
    };
  }
}

module.exports = {
  StatsTracker
};