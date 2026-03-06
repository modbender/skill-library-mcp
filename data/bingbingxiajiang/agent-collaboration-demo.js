/**
 * 多智能体协作系统演示
 * 
 * 核心理念：
 * 1. 智能体有自主性 - 自己决策，不是被动执行
 * 2. 去中心化协作 - 智能体之间直接协作
 * 3. 能力组合 - 动态加载能力
 * 4. 人机协作伙伴 - 与人对话，不是工具
 */

console.log('\n');
console.log('╔══════════════════════════════════════════════════════════════════════╗');
console.log('║         多智能体协作系统 - 真正的协作伙伴                            ║');
console.log('╚══════════════════════════════════════════════════════════════════════╝');
console.log('\n');

// ==================== 智能体定义 ====================

// 智能体基类
class Agent {
  constructor(config) {
    this.id = config.id;
    this.name = config.name;
    this.description = config.description;
    this.capabilities = config.capabilities;
    this.limitations = config.limitations;
    this.experiences = [];
  }
  
  // 能否处理这个任务
  async canHandle(task) {
    return this.capabilities.some(cap => 
      task.type.toLowerCase().includes(cap.toLowerCase()) ||
      task.content.toString().toLowerCase().includes(cap.toLowerCase())
    );
  }
  
  // 自主决策
  async decide(task) {
    // 子类实现
    throw new Error('子类必须实现decide方法');
  }
  
  // 学习
  learn(experience) {
    this.experiences.push(experience);
    console.log(`  [${this.name}] 学习: ${experience.outcome}`);
  }
  
  // 与人沟通
  async communicate(message) {
    return `[${this.name}] 收到您的消息。`;
  }
}

// ==================== 具体智能体 ====================

// 信息源订阅者
class DataSourceSubscriber extends Agent {
  constructor() {
    super({
      id: 'data-source-subscriber',
      name: '信息源订阅者',
      description: '专门负责对接各种数据源',
      capabilities: ['订阅', '获取', '接收', '抓取'],
      limitations: ['不分析', '不判断', '不决策']
    });
    this.subscriptions = [];
  }
  
  async decide(task) {
    console.log(`  [${this.name}] 分析任务...`);
    
    if (task.type === 'subscribe') {
      return {
        action: 'execute',
        reasoning: '订阅任务在我能力范围内',
        steps: ['验证数据源', '建立连接', '开始接收']
      };
    }
    
    if (task.type === 'fetch') {
      // 自主判断：需要协作吗？
      if (task.content.includes('清洗') || task.content.includes('处理')) {
        return {
          action: 'collaborate',
          reasoning: '数据需要清洗，主动请求协作',
          collaborateWith: 'data-cleaner',
          steps: ['获取原始数据', '请求清洗协作']
        };
      }
      
      return {
        action: 'execute',
        reasoning: '简单获取任务，可直接执行',
        steps: ['请求数据', '返回结果']
      };
    }
    
    // 不在我的能力范围，问人
    return {
      action: 'ask_human',
      reasoning: '任务类型不在我的能力范围内',
      question: `我收到了一个"${task.type}"类型的任务，这不在我的能力范围内。您希望我如何处理？`
    };
  }
  
  async communicate(message) {
    return `[信息源订阅者] 收到: "${message}"。我目前订阅了 ${this.subscriptions.length} 个数据源。需要我帮您订阅新的数据源吗？`;
  }
}

// 数据清洗器
class DataCleaner extends Agent {
  constructor() {
    super({
      id: 'data-cleaner',
      name: '数据清洗器',
      description: '专门负责数据预处理',
      capabilities: ['清洗', '预处理', '标准化', '去重'],
      limitations: ['不判断价值', '不做业务逻辑', '不存储']
    });
  }
  
  async decide(task) {
    console.log(`  [${this.name}] 分析任务...`);
    
    return {
      action: 'execute',
      reasoning: '数据清洗是我擅长的',
      steps: ['分析数据结构', '应用清洗规则', '验证结果']
    };
  }
  
  async respondToCollaboration(request) {
    console.log(`  [${this.name}] 收到协作请求: ${request.reason}`);
    return {
      accepted: true,
      contribution: '我可以清洗和标准化数据'
    };
  }
  
  async communicate(message) {
    return `[数据清洗器] 收到: "${message}"。我可以帮您清洗和标准化数据。数据有什么问题需要处理？`;
  }
}

// 模式识别器
class PatternRecognizer extends Agent {
  constructor() {
    super({
      id: 'pattern-recognizer',
      name: '模式识别器',
      description: '专门负责发现规律',
      capabilities: ['分析', '识别', '预测', '发现'],
      limitations: ['不做决策', '不执行行动', '不直接交互']
    });
  }
  
  async decide(task) {
    console.log(`  [${this.name}] 分析任务...`);
    
    // 自主判断：数据够吗？
    if (!task.data || task.data.length < 10) {
      return {
        action: 'collaborate',
        reasoning: '数据量不足，主动请求更多信息源订阅者协作',
        collaborateWith: 'data-source-subscriber',
        steps: ['请求更多数据', '等待数据', '开始分析']
      };
    }
    
    return {
      action: 'execute',
      reasoning: '数据充足，可以开始模式识别',
      steps: ['预处理', '模式检测', '置信度评估']
    };
  }
  
  async communicate(message) {
    return `[模式识别器] 收到: "${message}"。我可以帮您发现数据中的模式。您想分析什么数据？`;
  }
}

// 决策生成器
class DecisionGenerator extends Agent {
  constructor() {
    super({
      id: 'decision-generator',
      name: '决策生成器',
      description: '专门负责给出行动建议',
      capabilities: ['决策', '建议', '评估', '排序'],
      limitations: ['不执行行动', '不收集数据', '不分析模式']
    });
  }
  
  async decide(task) {
    console.log(`  [${this.name}] 分析任务...`);
    
    // 信息不足？问人
    if (!task.context || Object.keys(task.context).length === 0) {
      return {
        action: 'ask_human',
        reasoning: '缺乏决策所需的上下文信息',
        question: '为了给出更好的建议，我需要了解更多背景信息。这个决策的重要性和时间紧迫性如何？'
      };
    }
    
    return {
      action: 'execute',
      reasoning: '信息充足，可以生成决策建议',
      steps: ['分析上下文', '生成候选方案', '评估和排序']
    };
  }
  
  async communicate(message) {
    return `[决策生成器] 收到: "${message}"。我可以帮您分析选项并给出建议。您在纠结什么决策？`;
  }
}

// ==================== 智能体协作网络 ====================

class AgentNetwork {
  constructor() {
    this.agents = new Map();
    this.taskHistory = [];
  }
  
  // 注册智能体
  register(agent) {
    this.agents.set(agent.id, agent);
    console.log(`[网络] 注册智能体: ${agent.name}`);
    console.log(`       能力: ${agent.capabilities.join(', ')}`);
    console.log(`       边界: ${agent.limitations.join(', ')}`);
    console.log('');
  }
  
  // 动态加载能力（能力组合）
  loadCapability(agent) {
    this.register(agent);
    console.log(`[网络] 动态加载能力: ${agent.name}`);
    console.log('');
  }
  
  // 提交任务
  async submitTask(task) {
    console.log(`[网络] 收到任务: ${task.type}`);
    console.log(`       内容: ${task.content}`);
    console.log(`       来源: ${task.createdBy}`);
    console.log('');
    
    // 找到能处理的智能体
    const capableAgents = [];
    for (const agent of this.agents.values()) {
      if (await agent.canHandle(task)) {
        capableAgents.push(agent);
      }
    }
    
    if (capableAgents.length === 0) {
      console.log(`[网络] 没有智能体能处理这个任务`);
      console.log(`       建议: 人工介入或加载新能力`);
      return;
    }
    
    console.log(`[网络] 找到 ${capableAgents.length} 个智能体可以处理`);
    console.log('');
    
    // 让智能体自主决策
    for (const agent of capableAgents) {
      const decision = await agent.decide(task);
      
      console.log(`[网络] ${agent.name} 的决策:`);
      console.log(`       行动: ${decision.action}`);
      console.log(`       原因: ${decision.reasoning}`);
      
      // 根据决策执行
      await this.executeDecision(agent, decision, task);
    }
    
    this.taskHistory.push({ task, timestamp: new Date() });
  }
  
  // 执行决策
  async executeDecision(agent, decision, task) {
    switch (decision.action) {
      case 'execute':
        console.log(`       执行步骤: ${decision.steps.join(' → ')}`);
        console.log('');
        break;
        
      case 'collaborate':
        console.log(`       请求协作: ${decision.collaborateWith}`);
        const target = this.agents.get(decision.collaborateWith);
        if (target && target.respondToCollaboration) {
          const response = await target.respondToCollaboration({
            from: agent.id,
            reason: decision.reasoning
          });
          console.log(`       协作响应: ${response.accepted ? '接受' : '拒绝'}`);
          if (response.contribution) {
            console.log(`       贡献: ${response.contribution}`);
          }
        }
        console.log('');
        break;
        
      case 'ask_human':
        console.log(`       需要人工介入`);
        console.log(`       问题: ${decision.question}`);
        console.log('');
        break;
    }
  }
  
  // 人机对话
  async chat(agentId, message) {
    const agent = this.agents.get(agentId);
    if (!agent) {
      return '找不到这个智能体';
    }
    return await agent.communicate(message);
  }
  
  // 获取网络状态
  getStatus() {
    return {
      agentCount: this.agents.size,
      agents: Array.from(this.agents.values()).map(a => ({
        id: a.id,
        name: a.name,
        capabilities: a.capabilities
      })),
      taskCount: this.taskHistory.length
    };
  }
}

// ==================== 演示 ====================

console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('【第一部分】智能体注册 - 职责单一，边界清晰');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

const network = new AgentNetwork();

// 注册基础智能体
network.register(new DataSourceSubscriber());
network.register(new DataCleaner());
network.register(new PatternRecognizer());
network.register(new DecisionGenerator());

console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('【第二部分】智能体自主决策 - 不是被动执行');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

// 任务1：简单订阅
console.log('▶ 任务1：订阅新闻源');
console.log('─────────────────────────────────────\n');
network.submitTask({
  id: 'task-001',
  type: 'subscribe',
  content: '订阅科技新闻RSS',
  createdBy: 'human',
  context: {}
});

// 任务2：需要协作
console.log('▶ 任务2：获取并清洗数据');
console.log('─────────────────────────────────────\n');
network.submitTask({
  id: 'task-002',
  type: 'fetch',
  content: '获取热点数据并清洗处理',
  createdBy: 'human',
  context: {}
});

// 任务3：需要问人
console.log('▶ 任务3：未知任务类型');
console.log('─────────────────────────────────────\n');
network.submitTask({
  id: 'task-003',
  type: 'unknown',
  content: '做一些奇怪的事情',
  createdBy: 'human',
  context: {}
});

console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('【第三部分】能力组合扩展 - 不是配置扩展');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

// 动态加载新能力
console.log('▶ 场景：春节值班，需要特殊能力');
console.log('─────────────────────────────────────\n');

// 春节特殊能力
class SpringFestivalDutyAgent extends Agent {
  constructor() {
    super({
      id: 'spring-festival-duty',
      name: '春节值班智能体',
      description: '专门处理春节值班特殊场景',
      capabilities: ['春节', '值班', '热点', '日报'],
      limitations: ['只处理春节相关']
    });
  }
  
  async decide(task) {
    return {
      action: 'execute',
      reasoning: '春节值班任务，我来处理',
      steps: ['识别热点等级', '生成日报', '提醒值班人员']
    };
  }
  
  async communicate(message) {
    return `[春节值班智能体] 收到: "${message}"。春节期间我会特别关注热点动态。`;
  }
}

network.loadCapability(new SpringFestivalDutyAgent());

// 提交春节任务
network.submitTask({
  id: 'task-004',
  type: '春节值班',
  content: '监测今日热点',
  createdBy: 'human',
  context: { festival: '春节' }
});

console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('【第四部分】人机协作伙伴 - 不是工具');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

console.log('▶ 与智能体对话');
console.log('─────────────────────────────────────\n');

// 人机对话
async function chatWithAgents() {
  const response1 = await network.chat('data-source-subscriber', '今天有什么新数据源？');
  console.log(`人: 今天有什么新数据源？`);
  console.log(`智能体: ${response1}\n`);
  
  const response2 = await network.chat('decision-generator', '我该关注哪个热点？');
  console.log(`人: 我该关注哪个热点？`);
  console.log(`智能体: ${response2}\n`);
  
  const response3 = await network.chat('spring-festival-duty', '今天值班要注意什么？');
  console.log(`人: 今天值班要注意什么？`);
  console.log(`智能体: ${response3}\n`);
}

chatWithAgents().then(() => {
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('【对比】工具箱 vs 协作伙伴');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
  
  console.log('┌─────────────────────────────────────────────────────────────────┐');
  console.log('│  维度          工具箱（旧）         协作伙伴（新）              │');
  console.log('├─────────────────────────────────────────────────────────────────┤');
  console.log('│  智能体定义    通用型，什么都管     领域型，职责单一            │');
  console.log('│  工作流驱动    中心化编排           智能体自治                  │');
  console.log('│  扩展方式      配置扩展             能力组合                    │');
  console.log('│  人机关系      人使用工具           人与伙伴协作                │');
  console.log('│  决策方式      被动执行             自主决策                    │');
  console.log('│  协作方式      预定义流程           动态协作                    │');
  console.log('│  学习能力      无                   持续学习                    │');
  console.log('└─────────────────────────────────────────────────────────────────┘');
  console.log('');
  
  console.log('╔══════════════════════════════════════════════════════════════════════╗');
  console.log('║                     ✅ 多智能体协作演示完成                          ║');
  console.log('╠══════════════════════════════════════════════════════════════════════╣');
  console.log('║                                                                      ║');
  console.log('║  核心区别：                                                         ║');
  console.log('║                                                                      ║');
  console.log('║  工具箱：你需要什么工具，自己去拿，自己用                           ║');
  console.log('║  协作伙伴：你告诉它目标，它主动思考如何帮你                         ║');
  console.log('║                                                                      ║');
  console.log('║  智能体有自主性：                                                   ║');
  console.log('║  • 自己判断能否处理任务                                             ║');
  console.log('║  • 自己决定如何处理                                                 ║');
  console.log('║  • 主动请求协作                                                     ║');
  console.log('║  • 主动问人                                                         ║');
  console.log('║                                                                      ║');
  console.log('║  这才是真正的多智能体协作！                                         ║');
  console.log('║                                                                      ║');
  console.log('╚══════════════════════════════════════════════════════════════════════╝');
  console.log('\n');
});
