#!/usr/bin/env node

/**
 * 禅道任务数据分析脚本
 * 
 * 功能：
 * - 从禅道 API/数据库获取任务数据
 * - 分析员工任务数量、工时、难度
 * - 计算工作效率和饱和度
 * - 生成可视化报告
 */

const fs = require('fs');
const path = require('path');

// 配置
const CONFIG = {
  zentaoUrl: process.env.ZENTAO_URL || 'http://localhost/zentao',
  apiKey: process.env.ZENTAO_API_KEY || '',
  dbConfig: {
    host: process.env.ZENTAO_DB_HOST || 'localhost',
    database: process.env.ZENTAO_DB_NAME || 'zentao',
    user: process.env.ZENTAO_DB_USER || 'root',
    password: process.env.ZENTAO_DB_PASS || ''
  }
};

// 命令行参数解析
function parseArgs() {
  const args = process.argv.slice(2);
  const params = {};
  
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--start' && args[i + 1]) {
      params.start = args[++i];
    } else if (args[i] === '--end' && args[i + 1]) {
      params.end = args[++i];
    } else if (args[i] === '--user' && args[i + 1]) {
      params.user = args[++i];
    } else if (args[i] === '--project' && args[i + 1]) {
      params.project = args[++i];
    } else if (args[i] === '--team-report') {
      params.teamReport = true;
    } else if (args[i] === '--output' && args[i + 1]) {
      params.output = args[++i];
    } else if (args[i] === '--format' && args[i + 1]) {
      params.format = args[++i];
    }
  }
  
  return params;
}

// 模拟数据（实际使用时替换为 API 调用）
function fetchTaskData(params) {
  console.log('📡 正在获取禅道任务数据...');
  
  // TODO: 实现真实的 API 调用或数据库查询
  // 示例：const response = await fetch(`${CONFIG.zentaoUrl}/api/v1/tasks`, { ... })
  
  // 模拟数据用于演示
  return {
    employees: [
      {
        name: '张三',
        tasks: [
          { id: 1, title: '功能开发 A', estimatedHours: 8, actualHours: 6, difficulty: 3, status: 'done' },
          { id: 2, title: 'Bug 修复 B', estimatedHours: 4, actualHours: 5, difficulty: 2, status: 'done' },
          { id: 3, title: '代码评审 C', estimatedHours: 2, actualHours: 2, difficulty: 1, status: 'done' },
          { id: 4, title: '需求分析 D', estimatedHours: 6, actualHours: 8, difficulty: 4, status: 'doing' }
        ]
      },
      {
        name: '李四',
        tasks: [
          { id: 5, title: 'UI 设计 E', estimatedHours: 10, actualHours: 12, difficulty: 3, status: 'done' },
          { id: 6, title: '接口开发 F', estimatedHours: 8, actualHours: 7, difficulty: 4, status: 'done' },
          { id: 7, title: '测试 G', estimatedHours: 5, actualHours: 6, difficulty: 2, status: 'doing' }
        ]
      },
      {
        name: '王五',
        tasks: [
          { id: 8, title: '部署 H', estimatedHours: 4, actualHours: 3, difficulty: 2, status: 'done' },
          { id: 9, title: '文档 I', estimatedHours: 6, actualHours: 8, difficulty: 1, status: 'done' },
          { id: 10, title: '优化 J', estimatedHours: 8, actualHours: 10, difficulty: 3, status: 'doing' },
          { id: 11, title: '重构 K', estimatedHours: 12, actualHours: 15, difficulty: 5, status: 'doing' },
          { id: 12, title: '调研 L', estimatedHours: 6, actualHours: 4, difficulty: 3, status: 'done' }
        ]
      }
    ]
  };
}

// 计算员工效率指标
function calculateEmployeeMetrics(employee) {
  const tasks = employee.tasks;
  const totalTasks = tasks.length;
  const completedTasks = tasks.filter(t => t.status === 'done').length;
  const totalEstimatedHours = tasks.reduce((sum, t) => sum + t.estimatedHours, 0);
  const totalActualHours = tasks.reduce((sum, t) => sum + t.actualHours, 0);
  const avgDifficulty = tasks.reduce((sum, t) => sum + t.difficulty, 0) / totalTasks;
  
  // 效率指标
  const completionRate = (completedTasks / totalTasks * 100).toFixed(1);
  const efficiencyRatio = (totalEstimatedHours / totalActualHours).toFixed(2);
  const avgTaskHours = (totalActualHours / completedTasks).toFixed(1);
  
  // 饱和度指标（假设标准工时为 40 小时/周）
  const standardHours = 40;
  const workloadRate = (totalActualHours / standardHours * 100).toFixed(1);
  const taskDensity = (totalTasks / 5).toFixed(1); // 假设 5 个工作日
  
  return {
    name: employee.name,
    totalTasks,
    completedTasks,
    inProgressTasks: totalTasks - completedTasks,
    totalEstimatedHours,
    totalActualHours,
    avgDifficulty: avgDifficulty.toFixed(1),
    completionRate: `${completionRate}%`,
    efficiencyRatio,
    avgTaskHours: `${avgTaskHours}h`,
    workloadRate: `${workloadRate}%`,
    taskDensity: `${taskDensity} tasks/day`,
    saturationLevel: workloadRate > 100 ? '过载' : workloadRate > 70 ? '饱和' : workloadRate > 40 ? '正常' : '低负载'
  };
}

// 生成团队报告
function generateTeamReport(data) {
  console.log('\n' + '='.repeat(60));
  console.log('📊 禅道团队工作效率分析报告');
  console.log('='.repeat(60));
  
  const metrics = data.employees.map(emp => calculateEmployeeMetrics(emp));
  
  console.log('\n👥 员工效率概览:\n');
  console.log('┌─────────┬────────┬──────────┬────────────┬──────────┬────────────┬────────────┐');
  console.log('│ 姓名    │ 任务数 │ 完成率   │ 工时效率比 │ 负载率   │ 饱和度     │ 平均难度   │');
  console.log('├─────────┼────────┼──────────┼────────────┼──────────┼────────────┼────────────┤');
  
  metrics.forEach(m => {
    console.log(`│ ${m.name.padEnd(7)} │ ${String(m.totalTasks).padEnd(6)} │ ${m.completionRate.padEnd(8)} │ ${String(m.efficiencyRatio).padEnd(10)} │ ${m.workloadRate.padEnd(8)} │ ${m.saturationLevel.padEnd(10)} │ ${m.avgDifficulty.padEnd(10)} │`);
  });
  
  console.log('└─────────┴────────┴──────────┴────────────┴──────────┴────────────┴────────────┘');
  
  // 效率排名
  console.log('\n🏆 效率排名 (按工时效率比):\n');
  const sortedByEfficiency = [...metrics].sort((a, b) => parseFloat(b.efficiencyRatio) - parseFloat(a.efficiencyRatio));
  sortedByEfficiency.forEach((m, i) => {
    const medal = i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : '  ';
    console.log(`${medal} ${i + 1}. ${m.name} - 效率比：${m.efficiencyRatio} (完成 ${m.completedTasks}/${m.totalTasks} 任务)`);
  });
  
  // 饱和度预警
  console.log('\n⚠️  饱和度预警:\n');
  const overloaded = metrics.filter(m => m.saturationLevel === '过载');
  const underloaded = metrics.filter(m => m.saturationLevel === '低负载');
  
  if (overloaded.length > 0) {
    console.log('🔴 过载员工：');
    overloaded.forEach(m => console.log(`   - ${m.name}: 负载率 ${m.workloadRate}`));
  }
  
  if (underloaded.length > 0) {
    console.log('🟢 低负载员工：');
    underloaded.forEach(m => console.log(`   - ${m.name}: 负载率 ${m.workloadRate}`));
  }
  
  if (overloaded.length === 0 && underloaded.length === 0) {
    console.log('✅ 团队工作负载均衡');
  }
  
  // 优化建议
  console.log('\n💡 优化建议:\n');
  if (overloaded.length > 0 && underloaded.length > 0) {
    console.log('1. 任务重新分配：将过载员工的部分任务转移给低负载员工');
    overloaded.forEach(over => {
      underloaded.forEach(under => {
        console.log(`   - 建议：从 ${over.name} 转移 1-2 个任务给 ${under.name}`);
      });
    });
  }
  
  const avgEfficiency = metrics.reduce((sum, m) => sum + parseFloat(m.efficiencyRatio), 0) / metrics.length;
  if (avgEfficiency < 1) {
    console.log('2. 效率提升：团队平均效率比低于 1，建议优化工作流程或提供培训');
  }
  
  console.log('3. 定期回顾：建议每周进行工作量回顾和调整');
  
  console.log('\n' + '='.repeat(60));
  console.log(`报告生成时间：${new Date().toLocaleString('zh-CN')}`);
  console.log('='.repeat(60) + '\n');
  
  return metrics;
}

// 导出数据
function exportData(metrics, params) {
  const outputDir = params.output || './output';
  const format = params.format || 'json';
  
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  
  if (format === 'json') {
    const outputPath = path.join(outputDir, `zentao-report-${timestamp}.json`);
    fs.writeFileSync(outputPath, JSON.stringify(metrics, null, 2));
    console.log(`📄 JSON 报告已导出：${outputPath}`);
  } else if (format === 'csv') {
    const headers = Object.keys(metrics[0]).join(',');
    const rows = metrics.map(m => Object.values(m).join(',')).join('\n');
    const csv = headers + '\n' + rows;
    const outputPath = path.join(outputDir, `zentao-report-${timestamp}.csv`);
    fs.writeFileSync(outputPath, csv);
    console.log(`📄 CSV 报告已导出：${outputPath}`);
  }
}

// 主函数
async function main() {
  const params = parseArgs();
  
  console.log('🚀 禅道任务数据分析启动...\n');
  console.log('参数:', JSON.stringify(params, null, 2));
  
  try {
    // 获取数据
    const data = fetchTaskData(params);
    
    // 生成报告
    const metrics = generateTeamReport(data);
    
    // 导出数据
    if (params.output) {
      exportData(metrics, params);
    }
    
    console.log('✅ 分析完成!\n');
  } catch (error) {
    console.error('❌ 分析失败:', error.message);
    process.exit(1);
  }
}

// 运行
main();
