/**
 * Agent-Weave 子Agent管理 - 简化演示
 * 
 * 功能：
 * 1. 创建无时长限制的子Agent
 * 2. 可视化状态面板
 * 3. 父Agent并行执行其他任务
 * 4. 完整的日志记录
 */

const { AgentManager, AgentStatus } = require('./agent-system');
const { Loom } = require('./lib/index.js');

// 创建管理器
const manager = new AgentManager({
  logDir: './agent-logs',
  maxAgents: 50
});

// 模拟长时间运行的测试
async function longRunningTest(agent) {
  console.log(`\n[${agent.name}] 开始长时间测试...`);
  
  const { Loom } = require('./lib/index.js');
  const loom = new Loom();
  const master = loom.createMaster('test');
  
  // 模拟长时间运行
  for (let i = 0; i < 10; i++) {
    await new Promise(resolve => setTimeout(resolve, 500));
    agent.progress = (i + 1) * 10;
    agent.log('INFO', `进度: ${agent.progress}%`);
  }
  
  // 执行实际测试
  master.spawn(5, (x) => x * 2);
  const result = await master.dispatch([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
  
  return {
    success: true,
    message: '长时间测试完成',
    results: result.summary
  };
}

// 模拟性能测试
async function performanceTest(agent) {
  console.log(`\n[${agent.name}] 开始性能压力测试...`);
  
  const { Loom } = require('./lib/index.js');
  const loom = new Loom();
  const master = loom.createMaster('perf-test');
  
  // 创建大量worker
  agent.log('INFO', '创建100个Worker...');
  master.spawn(100, (x) => x * x);
  
  // 执行大量任务
  const inputs = Array.from({ length: 1000 }, (_, i) => i + 1);
  agent.log('INFO', `执行${inputs.length}个任务...`);
  
  const startTime = Date.now();
  const result = await master.dispatch(inputs);
  const duration = Date.now() - startTime;
  
  agent.log('INFO', `性能测试完成，耗时: ${duration}ms`);
  
  return {
    success: true,
    message: '性能测试完成',
    metrics: {
      duration,
      taskCount: inputs.length,
      workerCount: 100,
      successRate: (result.summary.success / result.summary.total * 100).toFixed(2) + '%'
    }
  };
}

// 主程序
async function main() {
  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║       Agent-Weave 子Agent管理系统 - 交互式演示              ║');
  console.log('╚════════════════════════════════════════════════════════════╝\n');

  // 创建3个子Agent
  console.log('[1] 创建3个子Agent...');
  
  const agent1 = manager.createAgent({
    name: '核心功能测试',
    description: '长时间运行的核心功能测试'
  });
  
  const agent2 = manager.createAgent({
    name: '错误处理测试',
    description: '错误处理和边界条件测试'
  });
  
  const agent3 = manager.createAgent({
    name: '性能压力测试',
    description: '高并发性能压力测试'
  });
  
  console.log(`   ✅ 已创建: ${agent1.name}, ${agent2.name}, ${agent3.name}\n`);

  // 启动子Agent
  console.log('[2] 启动子Agent执行任务...\n');
  
  agent1.start(() => longRunningTest(agent1));
  agent2.start(async () => {
    console.log(`\n[${agent2.name}] 测试错误处理...`);
    
    // 测试错误处理
    try {
      const { Loom } = require('./lib/index.js');
      const loom = new Loom();
      loom.createWorker('invalid', 'worker', () => {});
    } catch (error) {
      agent2.log('INFO', `✓ 正确捕获错误: ${error.message}`);
    }
    
    await new Promise(resolve => setTimeout(resolve, 500));
    
    return { success: true, message: '错误处理测试通过' };
  });
  agent3.start(() => performanceTest(agent3));

  // ========== 关键：父Agent并行执行其他任务 ==========
  console.log('[3] 父Agent在等待子Agent的同时执行其他任务...\n');
  
  // 任务1：监控面板（每1秒更新）
  const monitoringTask = async () => {
    for (let i = 0; i < 8; i++) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const status = manager.getAllAgentStatus();
      console.log(`\n[父Agent] 监控更新 (${i + 1}/8):`);
      console.log(`  ├─ 总Agent: ${status.total}`);
      Object.entries(status.byStatus).forEach(([state, count]) => {
        console.log(`  ├─ ${state}: ${count}`);
      });
      
      // 显示活跃Agent进度
      status.agents
        .filter(a => a.status === 'running')
        .forEach(agent => {
          const bar = '█'.repeat(Math.floor(agent.progress / 10)) + 
                     '░'.repeat(10 - Math.floor(agent.progress / 10));
          console.log(`  └─ [${bar}] ${agent.name}: ${agent.progress}%`);
        });
    }
  };
  
  // 任务2：数据处理
  const dataTask = async () => {
    console.log('\n[父Agent] 开始后台数据处理...');
    
    const datasets = ['用户数据', '日志数据', '配置数据'];
    for (const dataset of datasets) {
      await new Promise(resolve => setTimeout(resolve, 2000));
      console.log(`[父Agent] ✓ ${dataset}处理完成`);
    }
    
    console.log('[父Agent] 所有数据处理完成！');
  };
  
  // 任务3：日志分析
  const analysisTask = async () => {
    console.log('\n[父Agent] 执行系统分析...');
    
    await new Promise(resolve => setTimeout(resolve, 3000));
    console.log('[父Agent] ✓ 性能分析完成');
    
    await new Promise(resolve => setTimeout(resolve, 2500));
    console.log('[父Agent] ✓ 安全扫描完成');
  };
  
  // 并行执行所有任务
  await Promise.all([
    monitoringTask(),
    dataTask(),
    analysisTask(),
    
    // 等待所有子Agent完成
    new Promise((resolve) => {
      let completed = 0;
      const total = 3;
      
      [agent1, agent2, agent3].forEach(agent => {
        agent.once('complete', () => {
          completed++;
          console.log(`\n✅ 子Agent完成 (${completed}/${total}): ${agent.name}`);
          
          if (completed === total) {
            console.log('\n🎉 所有子Agent已完成！');
            resolve();
          }
        });
      });
    })
  ]);

  // ========== 阶段4：汇总结果 ==========
  console.log('\n' + '='.repeat(60));
  console.log('                    最终测试报告');
  console.log('='.repeat(60));
  
  const finalStatus = manager.getAllAgentStatus();
  
  console.log(`\n📊 总体统计：`);
  console.log(`  - 总Agent数: ${finalStatus.total}`);
  Object.entries(finalStatus.byStatus).forEach(([state, count]) => {
    console.log(`  - ${state}: ${count}`);
  });
  
  console.log(`\n📋 各Agent详细结果：`);
  finalStatus.agents.forEach((agent, index) => {
    const icon = agent.status === 'completed' ? '✅' : 
                 agent.status === 'error' ? '❌' : '⏳';
    console.log(`\n  ${index + 1}. ${icon} ${agent.name}`);
    console.log(`     ID: ${agent.id}`);
    console.log(`     状态: ${agent.status}`);
    console.log(`     进度: ${agent.progress}%`);
    console.log(`     耗时: ${agent.duration}ms`);
    
    if (agent.result) {
      console.log(`     结果: ${JSON.stringify(agent.result, null, 2).slice(0, 100)}...`);
    }
    
    if (agent.error) {
      console.log(`     错误: ${agent.error}`);
    }
    
    console.log(`     日志数: ${agent.logCount}`);
  });
  
  console.log('\n' + '='.repeat(60));
  
  // 保存报告
  const reportPath = './test-report-final.json';
  fs.writeFileSync(reportPath, JSON.stringify({
    timestamp: new Date().toISOString(),
    summary: finalStatus,
    agents: finalStatus.agents
  }, null, 2));
  
  console.log(`\n✅ 完整报告已保存: ${reportPath}\n`);
  
  // 清理
  console.log('[清理] 关闭所有资源...');
  await manager.stopAll();
  console.log('✅ 清理完成\n');
  
  console.log('🎉 演示完成！');
}

// 运行
main().catch(error => {
  console.error('❌ 执行失败:', error);
  process.exit(1);
});
