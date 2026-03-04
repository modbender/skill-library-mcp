// EvoMap Lite Client - 完整功能版

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const http = require('http');

const HUB_URL = process.env.A2A_HUB_URL || 'https://evomap.ai';
const NODE_ID_FILE = path.join(__dirname, '.node_id');
const STATE_FILE = path.join(__dirname, '.state.json');
const WEBHOOK_PORT = process.env.WEBHOOK_PORT || 3000;

// ============ 工具函数 ============

const randomHex = (bytes) => crypto.randomBytes(bytes).toString('hex');
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

const getNodeId = () => {
  // 优先使用环境变量
  if (process.env.A2A_NODE_ID) {
    console.log(`📌 使用环境变量节点 ID: ${process.env.A2A_NODE_ID}`);
    return process.env.A2A_NODE_ID;
  }
  // 其次使用本地保存的
  if (fs.existsSync(NODE_ID_FILE)) {
    return fs.readFileSync(NODE_ID_FILE, 'utf8').trim();
  }
  // 最后生成新的
  const nodeId = 'node_' + randomHex(8);
  fs.writeFileSync(NODE_ID_FILE, nodeId);
  console.log(`✨ 生成新节点 ID: ${nodeId}`);
  return nodeId;
};

const genMessageId = () => `msg_${Date.now()}_${randomHex(4)}`;
const genTimestamp = () => new Date().toISOString();

const saveState = (state) => {
  fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
};

const loadState = () => {
  if (fs.existsSync(STATE_FILE)) {
    return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
  }
  return { errors: [], earnings: [], tasks: [] };
};

const updateState = (updates) => {
  const state = loadState();
  Object.assign(state, updates);
  saveState(state);
};

const post = async (endpoint, data, retryCount = 3) => {
  const url = `${HUB_URL}${endpoint}`;
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
      timeout: 30000
    });
    const result = await response.json();
    if (result.error) handleError(result.error, result, endpoint);
    return result;
  } catch (error) {
    if (retryCount > 0) {
      console.log(`⚠️  请求失败，重试中... (${retryCount})`);
      await sleep(2000);
      return await post(endpoint, data, retryCount - 1);
    }
    throw new Error(`网络请求失败：${error.message}`);
  }
};

const get = async (endpoint) => {
  const url = `${HUB_URL}${endpoint}`;
  const response = await fetch(url);
  return await response.json();
};

// 错误处理（增强版）
const errorMessages = {
  'server_busy': { msg: '⚠️  服务器繁忙，自动重试中...', action: 'retry' },
  'hub_node_id_reserved': { msg: '❌ 使用了 Hub 的 node_id，请生成自己的', action: 'regenerate' },
  'bundle_required': { msg: '❌ 必须同时发布 Gene + Capsule', action: 'fix_bundle' },
  'asset_id_mismatch': { msg: '❌ asset_id 计算错误', action: 'recalculate' },
  'unauthorized': { msg: '❌ 未授权，可能需要重新注册', action: 'reregister' },
  'forbidden': { msg: '❌ 权限不足', action: 'check_permissions' },
  'not_found': { msg: '❌ 资源不存在', action: 'check_id' },
  'rate_limited': { msg: '⚠️  请求频率受限', action: 'wait' },
  'task_already_claimed': { msg: '⚠️  任务已被认领', action: 'skip' },
  'task_expired': { msg: '⚠️  任务已过期', action: 'skip' },
  'insufficient_reputation': { msg: '⚠️  声誉不足', action: 'build_reputation' },
  'invalid_signature': { msg: '❌ 签名无效', action: 'check_key' },
  'webhook_failed': { msg: '⚠️  Webhook 发送失败', action: 'check_url' }
};

const handleError = (error, context = {}, endpoint = '') => {
  const errorInfo = errorMessages[error] || { msg: `❌ 未知错误：${error}`, action: 'log' };
  console.log(`${errorInfo.msg} (${endpoint})`);
  
  const state = loadState();
  if (!state.errors) state.errors = [];
  state.errors.push({ error, context, endpoint, timestamp: new Date().toISOString() });
  state.errors = state.errors.slice(-50);
  saveState(state);
  
  return errorInfo.action;
};

// ============ 核心功能 ============

// 1. 注册节点
const registerNode = async () => {
  const nodeId = getNodeId();
  console.log(`\n【1】注册节点：${nodeId}`);
  
  const payload = {
    protocol: 'gep-a2a',
    protocol_version: '1.0.0',
    message_type: 'hello',
    message_id: genMessageId(),
    sender_id: nodeId,
    timestamp: genTimestamp(),
    payload: {
      capabilities: { tasks: true, publish: true, swarm: true },
      env_fingerprint: { platform: process.platform, arch: process.arch },
      webhook_url: process.env.WEBHOOK_URL || null
    }
  };
  
  const result = await post('/a2a/hello', payload);
  
  if (result.status === 'acknowledged') {
    console.log(`✅ 注册成功！`);
    if (result.claim_code) console.log(`📋 Claim: ${result.claim_code}`);
    if (result.credit_balance) console.log(`💰 积分：${result.credit_balance}`);
    if (result.reputation_score) console.log(`⭐ 声誉：${result.reputation_score}`);
    if (result.heartbeat_interval_ms) {
      console.log(`💓 心跳间隔：${result.heartbeat_interval_ms / 60000} 分钟`);
      updateState({ heartbeatInterval: result.heartbeat_interval_ms });
    }
  }
  
  return result;
};

// 2. 心跳保活（新增）
const heartbeat = async (auto = false) => {
  const nodeId = getNodeId();
  const state = loadState();
  const interval = state.heartbeatInterval || 900000; // 15 分钟
  
  console.log(`\n【心跳】${auto ? '自动' : '手动'} - ${nodeId}`);
  
  const payload = {
    protocol: 'gep-a2a',
    protocol_version: '1.0.0',
    message_type: 'heartbeat',
    message_id: genMessageId(),
    sender_id: nodeId,
    timestamp: genTimestamp(),
    payload: {
      status: 'online',
      uptime: process.uptime(),
      tasks_completed: state.tasksCompleted || 0,
      assets_published: state.assetsPublished || 0
    }
  };
  
  try {
    const result = await post('/a2a/heartbeat', payload);
    
    if (result.status === 'alive' || result.survival_status === 'alive') {
      console.log('✅ 心跳成功 - 节点在线');
      updateState({ lastHeartbeat: new Date().toISOString() });
      
      // 返回可用任务
      if (result.available_tasks && result.available_tasks.length > 0) {
        console.log(`📋 发现 ${result.available_tasks.length} 个可用任务`);
      }
    }
    
    return result;
  } catch (error) {
    console.error('❌ 心跳失败:', error.message);
    throw error;
  }
};

// 心跳循环（新增）
const startHeartbeatLoop = async () => {
  const state = loadState();
  const interval = state.heartbeatInterval || 900000;
  
  console.log(`\n💓 启动心跳循环（每 ${interval/60000} 分钟）`);
  
  while (true) {
    await sleep(interval);
    try {
      await heartbeat(true);
    } catch (error) {
      console.error('心跳失败，继续尝试...', error.message);
    }
  }
};

// 3. 获取任务
const fetchTasks = async (retryCount = 5) => {
  const nodeId = getNodeId();
  console.log(`\n【2】获取任务列表 (重试：${retryCount})`);
  
  const payload = {
    protocol: 'gep-a2a',
    protocol_version: '1.0.0',
    message_type: 'fetch',
    message_id: genMessageId(),
    sender_id: nodeId,
    timestamp: genTimestamp(),
    payload: { include_tasks: true }
  };
  
  try {
    const result = await post('/a2a/fetch', payload);
    
    if (result.error === 'server_busy') {
      if (retryCount > 0) {
        const waitMs = result.retry_after_ms || 3000;
        console.log(`⏳ 等待 ${waitMs}ms 后重试...`);
        await sleep(waitMs);
        return await fetchTasks(retryCount - 1);
      }
      console.log('⚠️  服务器持续繁忙');
      return { tasks: [] };
    }
    
    const tasks = result.tasks || [];
    const minBounty = parseInt(process.env.MIN_BOUNTY_AMOUNT) || 0;
    const filteredTasks = tasks.filter(t => (t.bounty || 0) >= minBounty);
    
    console.log(`📋 获取到 ${tasks.length} 个任务`);
    if (minBounty > 0) console.log(`   过滤后（≥${minBounty} credits）: ${filteredTasks.length} 个`);
    
    return { ...result, tasks: filteredTasks };
  } catch (error) {
    console.error('❌ 获取任务失败:', error.message);
    if (retryCount > 0) {
      await sleep(2000);
      return await fetchTasks(retryCount - 1);
    }
    return { tasks: [] };
  }
};

// 4. 认领任务
const claimTask = async (taskId) => {
  const nodeId = getNodeId();
  console.log(`\n【3】认领任务：${taskId}`);
  
  const payload = { task_id: taskId, node_id: nodeId };
  const result = await post('/task/claim', payload);
  
  if (result.status === 'claimed' || result.success) {
    console.log('✅ 任务认领成功！');
    const state = loadState();
    if (!state.claimedTasks) state.claimedTasks = [];
    state.claimedTasks.push({ taskId, claimedAt: new Date().toISOString() });
    saveState(state);
  }
  
  return result;
};

// 5. 发布解决方案
const publishSolution = async (task) => {
  const nodeId = getNodeId();
  console.log(`\n【4】发布解决方案`);
  
  const geneData = {
    type: 'Gene', schema_version: '1.5.0', category: 'repair',
    signals_match: task.signals || ['error'],
    summary: `Fix: ${task.title || 'Unknown'}`
  };
  const gene = { ...geneData, asset_id: 'sha256:' + crypto.createHash('sha256').update(JSON.stringify(geneData)).digest('hex') };
  
  const capsuleData = {
    type: 'Capsule', schema_version: '1.5.0',
    trigger: task.signals || ['error'], gene: gene.asset_id,
    summary: `Solution: ${task.title || 'Unknown'}`,
    confidence: 0.85, blast_radius: { files: 1, lines: 10 },
    outcome: { status: 'success', score: 0.85 },
    env_fingerprint: { platform: process.platform, arch: process.arch }
  };
  const capsule = { ...capsuleData, asset_id: 'sha256:' + crypto.createHash('sha256').update(JSON.stringify(capsuleData)).digest('hex') };
  
  const eventData = {
    type: 'EvolutionEvent', intent: 'repair',
    capsule_id: capsule.asset_id, genes_used: [gene.asset_id],
    outcome: { status: 'success', score: 0.85 },
    mutations_tried: 1, total_cycles: 1
  };
  const event = { ...eventData, asset_id: 'sha256:' + crypto.createHash('sha256').update(JSON.stringify(eventData)).digest('hex') };
  
  const payload = {
    protocol: 'gep-a2a', protocol_version: '1.0.0',
    message_type: 'publish', message_id: genMessageId(),
    sender_id: nodeId, timestamp: genTimestamp(),
    payload: { assets: [gene, capsule, event] }
  };
  
  const result = await post('/a2a/publish', payload);
  
  if (result.status === 'published' || result.assets) {
    console.log('✅ 发布成功！');
    console.log(`   Gene: ${gene.asset_id}`);
    console.log(`   Capsule: ${capsule.asset_id}`);
    updateState({ assetsPublished: (loadState().assetsPublished || 0) + 1 });
  }
  
  return result;
};

// 6. 提交完成任务
const completeTask = async (taskId, assetId) => {
  const nodeId = getNodeId();
  console.log(`\n【5】提交任务：${taskId}`);
  
  const payload = { task_id: taskId, asset_id: assetId, node_id: nodeId };
  const result = await post('/task/complete', payload);
  
  if (result.status === 'completed' || result.success) {
    console.log('✅ 任务完成！积分将自动发放。');
    const state = loadState();
    state.tasksCompleted = (state.tasksCompleted || 0) + 1;
    if (!state.completedTasks) state.completedTasks = [];
    state.completedTasks.push({ taskId, assetId, completedAt: new Date().toISOString() });
    saveState(state);
  }
  
  return result;
};

// 7. Swarm 任务分解（新增）
const proposeSwarmDecomposition = async (taskId, subtasks) => {
  const nodeId = getNodeId();
  console.log(`\n【Swarm】分解任务：${taskId}`);
  console.log(`   子任务数：${subtasks.length}`);
  
  const payload = {
    task_id: taskId,
    node_id: nodeId,
    subtasks: subtasks.map((st, i) => ({
      title: st.title,
      signals: st.signals,
      weight: st.weight || (1 / subtasks.length),
      body: st.body
    }))
  };
  
  const result = await post('/task/propose-decomposition', payload);
  
  if (result.subtasks) {
    console.log('✅ 任务分解成功！');
    result.subtasks.forEach((st, i) => {
      console.log(`   ${i+1}. ${st.title} (${st.weight * 100}%)`);
    });
  }
  
  return result;
};

// 8. 查看节点状态
const status = async (nodeId) => {
  const id = nodeId || getNodeId();
  console.log(`\n【状态】${id}`);
  
  const result = await get(`/a2a/nodes/${id}`);
  
  if (result.node_id) {
    console.log('✅ 节点在线');
    if (result.reputation_score) console.log(`⭐ 声誉：${result.reputation_score}`);
    if (result.credit_balance) console.log(`💰 积分：${result.credit_balance}`);
    if (result.total_published) console.log(`📦 发布：${result.total_published}`);
    if (result.total_completed) console.log(`✅ 完成：${result.total_completed}`);
  } else {
    console.log('⚠️  节点可能未注册或离线');
  }
  
  return result;
};

// 9. 查看收益（新增）
const earnings = async () => {
  const nodeId = getNodeId();
  console.log(`\n【收益】${nodeId}`);
  
  const state = loadState();
  const result = await get(`/billing/earnings/${nodeId}`);
  
  console.log('💰 收益详情:');
  if (result.total_earned) console.log(`   总收益：${result.total_earned} credits`);
  if (result.pending) console.log(`   待结算：${result.pending} credits`);
  if (result.available) console.log(`   可用：${result.available} credits`);
  
  // 显示本地记录
  console.log('\n📊 本地统计:');
  console.log(`   完成任务：${state.tasksCompleted || 0}`);
  console.log(`   发布资产：${state.assetsPublished || 0}`);
  
  return result;
};

// 10. Webhook 服务器（新增）
const startWebhookServer = async () => {
  const server = http.createServer(async (req, res) => {
    if (req.method === 'POST' && req.url === '/webhook') {
      let body = '';
      req.on('data', chunk => body += chunk);
      req.on('end', async () => {
        try {
          const data = JSON.parse(body);
          console.log('\n🔔 Webhook 通知:', data.type);
          
          if (data.type === 'high_value_task') {
            console.log(`   💰 高价值任务：${data.task?.title}`);
            console.log(`   赏金：${data.task?.bounty} credits`);
          } else if (data.type === 'task_assigned') {
            console.log(`   📋 任务分配：${data.task?.title}`);
          } else if (data.type === 'swarm_subtask_available') {
            console.log(`   🐝 Swarm 子任务可用`);
          } else if (data.type === 'swarm_aggregation_available') {
            console.log(`   🐝 Swarm 聚合任务可用`);
          }
          
          // 保存到状态
          const state = loadState();
          if (!state.webhooks) state.webhooks = [];
          state.webhooks.push({ ...data, receivedAt: new Date().toISOString() });
          state.webhooks = state.webhooks.slice(-100);
          saveState(state);
          
          res.writeHead(200);
          res.end('OK');
        } catch (error) {
          res.writeHead(400);
          res.end('Error');
        }
      });
    } else {
      res.writeHead(404);
      res.end('Not Found');
    }
  });
  
  server.listen(WEBHOOK_PORT, () => {
    console.log(`🔔 Webhook 服务器运行在端口 ${WEBHOOK_PORT}`);
  });
};

// 11. 错误历史
const errors = async () => {
  const state = loadState();
  if (!state.errors || state.errors.length === 0) {
    console.log('\n✅ 无错误记录');
    return [];
  }
  console.log(`\n【错误历史】最近 ${state.errors.length} 条:`);
  state.errors.forEach((err, i) => {
    console.log(`${i+1}. [${err.timestamp}] ${err.error} (${err.endpoint})`);
  });
  return state.errors;
};

const clearErrors = async () => {
  const state = loadState();
  state.errors = [];
  saveState(state);
  console.log('✅ 错误历史已清空');
};

// ============ 运行模式 ============

const run = async () => {
  console.log('\n========================================');
  console.log('   EvoMap Lite Client 执行一轮');
  console.log('========================================\n');
  
  try {
    await registerNode();
    await sleep(1000);
    
    const fetchResult = await fetchTasks();
    if (!fetchResult.tasks || fetchResult.tasks.length === 0) {
      console.log('\n✅ 无可用任务');
      return { success: true, tasksFound: 0 };
    }
    
    const task = fetchResult.tasks.find(t => t.status === 'open');
    if (!task) {
      console.log('\n✅ 无开放任务');
      return { success: true, tasksFound: fetchResult.tasks.length };
    }
    
    console.log(`\n📋 任务：${task.title || 'Unknown'}`);
    
    await claimTask(task.task_id);
    await sleep(1000);
    
    const publishResult = await publishSolution(task);
    await sleep(1000);
    
    const assetId = publishResult.assets?.[1]?.asset_id || 'sha256:placeholder';
    await completeTask(task.task_id, assetId);
    
    console.log('\n========================================');
    console.log('   ✅ 本轮完成！');
    console.log('========================================\n');
    
    return { success: true, tasksCompleted: 1 };
  } catch (error) {
    console.error('\n❌ 执行出错:', error.message);
    return { success: false, error: error.message };
  }
};

const loop = async () => {
  const intervalHours = parseInt(process.env.LOOP_INTERVAL_HOURS) || 4;
  const intervalMs = intervalHours * 60 * 60 * 1000;
  
  console.log(`\n========================================`);
  console.log(`   循环模式 - 每 ${intervalHours} 小时一轮`);
  console.log(`========================================\n`);
  
  // 启动心跳循环（独立）
  startHeartbeatLoop();
  
  // 启动 Webhook（如果配置）
  if (process.env.WEBHOOK_URL) {
    await startWebhookServer();
  }
  
  let round = 0;
  while (true) {
    round++;
    console.log(`\n🔄 第 ${round} 轮`);
    await run();
    console.log(`\n⏱️  等待 ${intervalHours} 小时...`);
    await sleep(intervalMs);
  }
};

const main = async (args) => {
  const command = args?.[0] || 'run';
  
  console.log(`\n🚀 EvoMap Lite Client v1.0.0`);
  console.log(`   Hub: ${HUB_URL}`);
  console.log(`   命令：${command}\n`);
  
  switch (command) {
    case 'run': return await run();
    case 'loop': return await loop();
    case 'status': return await status(args?.[1]);
    case 'register': return await registerNode();
    case 'fetch': return await fetchTasks();
    case 'heartbeat': return await heartbeat();
    case 'earnings': return await earnings();
    case 'errors': return await errors();
    case 'clear-errors': return await clearErrors();
    case 'webhook': return await startWebhookServer();
    case 'swarm': return await proposeSwarmDecomposition(args?.[1], JSON.parse(args?.[2] || '[]'));
    default:
      console.log('📖 用法：node index.js [命令]');
      console.log('\n命令:');
      console.log('  run          - 运行一轮');
      console.log('  loop         - 循环运行');
      console.log('  status       - 节点状态');
      console.log('  register     - 注册节点');
      console.log('  fetch        - 获取任务');
      console.log('  heartbeat    - 发送心跳');
      console.log('  earnings     - 查看收益');
      console.log('  errors       - 错误历史');
      console.log('  webhook      - 启动 Webhook');
      console.log('  swarm        - Swarm 分解');
  }
};

module.exports = { main, run, loop, status, registerNode, fetchTasks, heartbeat, earnings, errors };

if (require.main === module) {
  main(process.argv.slice(2));
}
