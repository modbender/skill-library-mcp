/**
 * Agent-Weave 子Agent管理系统
 * 功能：无时长限制、状态追踪、日志记录、异步通信
 */

const { EventEmitter } = require('events');
const fs = require('fs');
const path = require('path');

// 子Agent状态枚举
const AgentStatus = {
  PENDING: 'pending',      // 等待启动
  RUNNING: 'running',      // 运行中
  PAUSED: 'paused',        // 暂停
  COMPLETED: 'completed',  // 完成
  ERROR: 'error',          // 错误
  CANCELLED: 'cancelled'   // 取消
};

/**
 * 子Agent实例
 */
class SubAgent extends EventEmitter {
  constructor(id, config = {}) {
    super();
    this.id = id;
    this.name = config.name || `agent-${id.slice(0, 8)}`;
    this.status = AgentStatus.PENDING;
    this.config = config;
    this.startTime = null;
    this.endTime = null;
    this.progress = 0;
    this.result = null;
    this.error = null;
    this.logs = [];
    this.metrics = {
      cpuUsage: [],
      memoryUsage: [],
      taskCount: 0,
      successCount: 0,
      failCount: 0
    };
    
    // 心跳检测
    this.lastHeartbeat = Date.now();
    this.heartbeatInterval = null;
  }
  
  /**
   * 启动子Agent
   */
  async start(taskFn) {
    this.status = AgentStatus.RUNNING;
    this.startTime = Date.now();
    this.log('INFO', `Agent ${this.name} 启动`);
    
    // 启动心跳
    this.startHeartbeat();
    
    try {
      // 执行任务
      this.result = await this.executeTask(taskFn);
      this.status = AgentStatus.COMPLETED;
      this.log('INFO', `Agent ${this.name} 完成`);
    } catch (error) {
      this.error = error;
      this.status = AgentStatus.ERROR;
      this.log('ERROR', `Agent ${this.name} 错误: ${error.message}`);
    } finally {
      this.endTime = Date.now();
      this.stopHeartbeat();
      this.emit('complete', this.getStatus());
    }
  }
  
  /**
   * 执行任务
   */
  async executeTask(taskFn) {
    // 模拟长时间运行的任务
    for (let i = 0; i < 10; i++) {
      if (this.status === AgentStatus.CANCELLED) {
        throw new Error('Task cancelled');
      }
      
      await new Promise(resolve => setTimeout(resolve, 100));
      this.progress = (i + 1) * 10;
      this.log('DEBUG', `进度: ${this.progress}%`);
      this.emit('progress', { progress: this.progress });
    }
    
    return { success: true, data: 'Task completed' };
  }
  
  /**
   * 暂停
   */
  pause() {
    if (this.status === AgentStatus.RUNNING) {
      this.status = AgentStatus.PAUSED;
      this.log('INFO', `Agent ${this.name} 暂停`);
    }
  }
  
  /**
   * 恢复
   */
  resume() {
    if (this.status === AgentStatus.PAUSED) {
      this.status = AgentStatus.RUNNING;
      this.log('INFO', `Agent ${this.name} 恢复`);
    }
  }
  
  /**
   * 取消
   */
  cancel() {
    this.status = AgentStatus.CANCELLED;
    this.log('INFO', `Agent ${this.name} 取消`);
  }
  
  /**
   * 记录日志
   */
  log(level, message) {
    const entry = {
      timestamp: new Date().toISOString(),
      level,
      message
    };
    this.logs.push(entry);
    this.emit('log', entry);
  }
  
  /**
   * 启动心跳
   */
  startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      this.lastHeartbeat = Date.now();
      this.emit('heartbeat', { agentId: this.id, timestamp: this.lastHeartbeat });
    }, 5000);
  }
  
  /**
   * 停止心跳
   */
  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }
  
  /**
   * 获取状态
   */
  getStatus() {
    return {
      id: this.id,
      name: this.name,
      status: this.status,
      progress: this.progress,
      startTime: this.startTime,
      endTime: this.endTime,
      duration: this.endTime ? this.endTime - this.startTime : Date.now() - this.startTime,
      result: this.result,
      error: this.error ? this.error.message : null,
      logCount: this.logs.length,
      lastHeartbeat: this.lastHeartbeat
    };
  }
}

/**
 * Agent管理器 - 父Agent使用
 */
class AgentManager extends EventEmitter {
  constructor(config = {}) {
    super();
    this.agents = new Map();
    this.config = {
      logDir: config.logDir || './agent-logs',
      maxAgents: config.maxAgents || 100,
      heartbeatTimeout: config.heartbeatTimeout || 30000,
      ...config
    };
    
    // 确保日志目录存在
    if (!fs.existsSync(this.config.logDir)) {
      fs.mkdirSync(this.config.logDir, { recursive: true });
    }
    
    // 启动监控
    this.startMonitoring();
  }
  
  /**
   * 创建子Agent
   */
  createAgent(agentConfig = {}) {
    if (this.agents.size >= this.config.maxAgents) {
      throw new Error(`已达到最大Agent数量限制: ${this.config.maxAgents}`);
    }
    
    const id = `agent-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const agent = new SubAgent(id, agentConfig);
    
    // 监听事件
    agent.on('progress', (data) => {
      this.emit('agent:progress', { agentId: id, ...data });
    });
    
    agent.on('log', (entry) => {
      this.emit('agent:log', { agentId: id, ...entry });
      this.writeLogToFile(id, entry);
    });
    
    agent.on('heartbeat', (data) => {
      this.emit('agent:heartbeat', data);
    });
    
    agent.on('complete', (status) => {
      this.emit('agent:complete', { agentId: id, status });
      this.saveAgentState(id);
    });
    
    this.agents.set(id, agent);
    this.emit('agent:created', { agentId: id, config: agentConfig });
    
    return agent;
  }
  
  /**
   * 获取Agent
   */
  getAgent(id) {
    return this.agents.get(id);
  }
  
  /**
   * 获取所有Agent状态
   */
  getAllAgentStatus() {
    const status = {
      total: this.agents.size,
      byStatus: {},
      agents: []
    };
    
    for (const [id, agent] of this.agents) {
      const agentStatus = agent.getStatus();
      status.agents.push(agentStatus);
      
      // 统计各状态数量
      if (!status.byStatus[agentStatus.status]) {
        status.byStatus[agentStatus.status] = 0;
      }
      status.byStatus[agentStatus.status]++;
    }
    
    return status;
  }
  
  /**
   * 显示Agent状态面板
   */
  displayStatusPanel() {
    const status = this.getAllAgentStatus();
    
    console.clear();
    console.log('╔════════════════════════════════════════════════════════════╗');
    console.log('║              Agent-Weave 子Agent管理面板                    ║');
    console.log('╠════════════════════════════════════════════════════════════╣');
    console.log(`║  总Agent数: ${status.total.toString().padEnd(3)} │ 运行中: ${(status.byStatus.running || 0).toString().padEnd(3)} │ 待处理: ${(status.byStatus.pending || 0).toString().padEnd(3)}  ║`);
    console.log(`║  已完成: ${(status.byStatus.completed || 0).toString().padEnd(5)} │ 错误: ${(status.byStatus.error || 0).toString().padEnd(5)} │ 已取消: ${(status.byStatus.cancelled || 0).toString().padEnd(3)} ║`);
    console.log('╠════════════════════════════════════════════════════════════╣');
    
    // 显示活跃Agent
    const activeAgents = status.agents.filter(a => 
      a.status === 'running' || a.status === 'pending'
    );
    
    if (activeAgents.length > 0) {
      console.log('║  活跃Agent列表:                                              ║');
      console.log('╠════════════════════════════════════════════════════════════╣');
      
      activeAgents.slice(0, 10).forEach(agent => {
        const shortId = agent.id.slice(0, 8);
        const statusIcon = agent.status === 'running' ? '▶' : '⏸';
        const progress = '█'.repeat(Math.floor(agent.progress / 10)) + '░'.repeat(10 - Math.floor(agent.progress / 10));
        
        console.log(`║  ${statusIcon} ${shortId} │ ${agent.status.padEnd(8)} │ ${progress} ${agent.progress.toString().padStart(3)}% ║`);
      });
      
      if (activeAgents.length > 10) {
        console.log(`║  ... 还有 ${activeAgents.length - 10} 个Agent ...                               ║`);
      }
    } else {
      console.log('║  当前没有活跃的Agent                                          ║');
    }
    
    console.log('╚════════════════════════════════════════════════════════════╝');
    console.log(`\n最后更新: ${new Date().toLocaleTimeString()} | 按 Ctrl+C 退出\n`);
  }
  
  /**
   * 启动监控
   */
  startMonitoring() {
    // 定期检查心跳
    setInterval(() => {
      const now = Date.now();
      for (const [id, agent] of this.agents) {
        if (agent.status === 'running') {
          const lastHeartbeat = agent.lastHeartbeat || agent.startTime;
          if (now - lastHeartbeat > this.config.heartbeatTimeout) {
            agent.log('WARN', '心跳超时');
            this.emit('agent:timeout', { agentId: id });
          }
        }
      }
    }, 5000);
    
    // 定期刷新状态面板
    setInterval(() => {
      this.displayStatusPanel();
    }, 1000);
  }
  
  /**
   * 写入日志到文件
   */
  writeLogToFile(agentId, entry) {
    const logFile = path.join(this.config.logDir, `${agentId}.log`);
    const line = `[${entry.timestamp}] [${entry.level}] ${entry.message}\n`;
    fs.appendFileSync(logFile, line);
  }
  
  /**
   * 保存Agent状态
   */
  saveAgentState(agentId) {
    const agent = this.agents.get(agentId);
    if (!agent) return;
    
    const stateFile = path.join(this.config.logDir, `${agentId}.json`);
    const state = agent.getStatus();
    fs.writeFileSync(stateFile, JSON.stringify(state, null, 2));
  }
  
  /**
   * 停止所有Agent
   */
  async stopAll() {
    const promises = [];
    for (const [id, agent] of this.agents) {
      if (agent.status === 'running') {
        promises.push(new Promise((resolve) => {
          agent.once('complete', resolve);
          agent.cancel();
        }));
      }
    }
    await Promise.all(promises);
  }
}

module.exports = {
  AgentManager,
  SubAgent,
  AgentStatus
};
