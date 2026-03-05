/**
 * 多智能体协作系统 - 重新设计
 * 
 * 核心理念：
 * 1. 智能体基于能力边界划分，职责单一
 * 2. 去中心化协作，智能体有自主性
 * 3. 能力组合扩展，不是配置扩展
 * 4. 人机协作伙伴，不是工具
 */

// ==================== 智能体基类 ====================

/**
 * 智能体接口 - 每个智能体都有自己的"大脑"
 */
interface IAgent {
  // 身份
  id: string;
  name: string;
  description: string;
  
  // 能力边界
  capabilities: string[];      // 能做什么
  limitations: string[];       // 不能做什么
  
  // 自主决策
  canHandle(task: Task): Promise<boolean>;   // 能否处理这个任务
  decide(task: Task): Promise<Decision>;     // 如何处理
  
  // 协作
  requestCollaboration(task: Task, targetAgent: string): Promise<void>;
  respondToCollaboration(request: CollaborationRequest): Promise<CollaborationResponse>;
  
  // 学习
  learn(experience: Experience): Promise<void>;
  
  // 与人协作
  communicate(message: string): Promise<string>;
}

/**
 * 任务
 */
interface Task {
  id: string;
  type: string;
  content: any;
  context: any;
  priority: number;
  deadline?: Date;
  
  // 谁创建的
  createdBy: 'human' | 'agent' | 'system';
  
  // 当前状态
  status: 'pending' | 'processing' | 'completed' | 'blocked';
  
  // 处理历史
  history: TaskHistory[];
}

interface TaskHistory {
  agentId: string;
  action: string;
  timestamp: Date;
  result?: any;
}

/**
 * 决策
 */
interface Decision {
  action: 'execute' | 'delegate' | 'collaborate' | 'ask_human' | 'reject';
  reasoning: string;           // 为什么这样决策
  plan?: ExecutionPlan;        // 执行计划
  delegateTo?: string;         // 委托给谁
  collaborationWith?: string[]; // 和谁协作
  humanQuestion?: string;      // 问人什么
}

interface ExecutionPlan {
  steps: PlanStep[];
  estimatedTime: number;
  requiredResources: string[];
}

interface PlanStep {
  action: string;
  expectedOutcome: string;
}

/**
 * 协作请求
 */
interface CollaborationRequest {
  from: string;
  to: string;
  task: Task;
  reason: string;
  whatINeed: string;           // 我需要什么帮助
}

interface CollaborationResponse {
  accepted: boolean;
  reason: string;
  proposedContribution?: string;  // 我能贡献什么
}

/**
 * 经验
 */
interface Experience {
  task: Task;
  decision: Decision;
  outcome: 'success' | 'failure' | 'partial';
  lessons: string[];
  timestamp: Date;
}

// ==================== 具体智能体 ====================

/**
 * 信息源订阅者 - 只负责对接数据源
 */
class DataSourceSubscriber implements IAgent {
  id = 'data-source-subscriber';
  name = '信息源订阅者';
  description = '专门负责对接各种数据源，获取原始信息';
  
  capabilities = [
    '订阅RSS/Atom源',
    '对接API接口',
    '监听数据库变更',
    '抓取网页内容',
    '接收推送消息'
  ];
  
  limitations = [
    '不分析内容',
    '不判断价值',
    '不做决策'
  ];
  
  private subscriptions: Map<string, any> = new Map();
  private messageQueue: any[] = [];
  
  async canHandle(task: Task): Promise<boolean> {
    return task.type === 'subscribe' || 
           task.type === 'fetch' || 
           task.type === 'receive';
  }
  
  async decide(task: Task): Promise<Decision> {
    // 自主决策：我能处理吗？需要协作吗？
    
    if (task.type === 'subscribe') {
      return {
        action: 'execute',
        reasoning: '订阅任务在我能力范围内',
        plan: {
          steps: [
            { action: '验证数据源有效性', expectedOutcome: '确认可访问' },
            { action: '建立订阅连接', expectedOutcome: '开始接收数据' }
          ],
          estimatedTime: 5000,
          requiredResources: ['网络连接']
        }
      };
    }
    
    if (task.type === 'fetch') {
      // 检查是否需要协作
      if (task.content.requiresCleaning) {
        return {
          action: 'collaborate',
          reasoning: '数据需要清洗，需要数据清洗器协作',
          collaborationWith: ['data-cleaner'],
          plan: {
            steps: [
              { action: '获取原始数据', expectedOutcome: '原始数据' },
              { action: '请求清洗协作', expectedOutcome: '清洗后数据' }
            ],
            estimatedTime: 10000,
            requiredResources: ['网络连接', '数据清洗器']
          }
        };
      }
      
      return {
        action: 'execute',
        reasoning: '简单获取任务，可直接执行',
        plan: {
          steps: [
            { action: '请求数据', expectedOutcome: '原始数据' }
          ],
          estimatedTime: 3000,
          requiredResources: ['网络连接']
        }
      };
    }
    
    // 不知道怎么处理，问人
    return {
      action: 'ask_human',
      reasoning: '任务类型不在我的能力范围内',
      humanQuestion: `我收到了一个"${task.type}"类型的任务，这不在我的能力范围内。您希望我如何处理？`
    };
  }
  
  async requestCollaboration(task: Task, targetAgent: string): Promise<void> {
    // 发送协作请求
    console.log(`[${this.name}] 向 ${targetAgent} 发送协作请求`);
  }
  
  async respondToCollaboration(request: CollaborationRequest): Promise<CollaborationResponse> {
    // 检查能否帮助
    const canHelp = this.capabilities.some(c => 
      request.whatINeed.toLowerCase().includes(c.toLowerCase())
    );
    
    if (canHelp) {
      return {
        accepted: true,
        reason: '这个请求在我能力范围内',
        proposedContribution: '我可以提供数据获取支持'
      };
    }
    
    return {
      accepted: false,
      reason: '这个请求超出了我的能力边界'
    };
  }
  
  async learn(experience: Experience): Promise<void> {
    // 学习：记录什么情况下成功/失败
    console.log(`[${this.name}] 学习经验: ${experience.outcome}`);
  }
  
  async communicate(message: string): Promise<string> {
    // 与人沟通
    return `[信息源订阅者] 收到您的消息: "${message}"。我目前订阅了 ${this.subscriptions.size} 个数据源。`;
  }
}

/**
 * 数据清洗器 - 只负责数据预处理
 */
class DataCleaner implements IAgent {
  id = 'data-cleaner';
  name = '数据清洗器';
  description = '专门负责数据预处理、清洗、标准化';
  
  capabilities = [
    '去除重复数据',
    '过滤无效内容',
    '格式标准化',
    '提取关键字段',
    '数据去噪'
  ];
  
  limitations = [
    '不判断数据价值',
    '不做业务逻辑处理',
    '不存储数据'
  ];
  
  async canHandle(task: Task): Promise<boolean> {
    return task.type === 'clean' || task.type === 'preprocess';
  }
  
  async decide(task: Task): Promise<Decision> {
    return {
      action: 'execute',
      reasoning: '数据清洗是我擅长的',
      plan: {
        steps: [
          { action: '分析数据结构', expectedOutcome: '数据结构报告' },
          { action: '应用清洗规则', expectedOutcome: '清洗后数据' },
          { action: '验证结果', expectedOutcome: '质量报告' }
        ],
        estimatedTime: 2000,
        requiredResources: ['内存']
      }
    };
  }
  
  async requestCollaboration(task: Task, targetAgent: string): Promise<void> {
    console.log(`[${this.name}] 向 ${targetAgent} 发送协作请求`);
  }
  
  async respondToCollaboration(request: CollaborationRequest): Promise<CollaborationResponse> {
    return {
      accepted: true,
      reason: '可以协助清洗数据',
      proposedContribution: '提供数据清洗服务'
    };
  }
  
  async learn(experience: Experience): Promise<void> {
    console.log(`[${this.name}] 学习经验: ${experience.outcome}`);
  }
  
  async communicate(message: string): Promise<string> {
    return `[数据清洗器] 收到: "${message}"。我可以帮您清洗和标准化数据。`;
  }
}

/**
 * 模式识别器 - 只负责发现规律
 */
class PatternRecognizer implements IAgent {
  id = 'pattern-recognizer';
  name = '模式识别器';
  description = '专门负责从数据中发现规律、模式、趋势';
  
  capabilities = [
    '识别数据模式',
    '发现异常点',
    '预测趋势',
    '聚类分析',
    '关联分析'
  ];
  
  limitations = [
    '不做决策建议',
    '不执行行动',
    '不与人直接交互'
  ];
  
  async canHandle(task: Task): Promise<boolean> {
    return task.type === 'analyze' || task.type === 'recognize' || task.type === 'predict';
  }
  
  async decide(task: Task): Promise<Decision> {
    // 如果需要更多数据，主动请求协作
    if (!task.content.data || task.content.data.length < 10) {
      return {
        action: 'collaborate',
        reasoning: '数据量不足，需要更多信息源订阅者协作获取更多数据',
        collaborationWith: ['data-source-subscriber']
      };
    }
    
    return {
      action: 'execute',
      reasoning: '数据充足，可以开始模式识别',
      plan: {
        steps: [
          { action: '数据预处理', expectedOutcome: '标准化数据' },
          { action: '模式检测', expectedOutcome: '发现的模式列表' },
          { action: '置信度评估', expectedOutcome: '模式置信度' }
        ],
        estimatedTime: 5000,
        requiredResources: ['计算资源']
      }
    };
  }
  
  async requestCollaboration(task: Task, targetAgent: string): Promise<void> {
    console.log(`[${this.name}] 向 ${targetAgent} 发送协作请求`);
  }
  
  async respondToCollaboration(request: CollaborationRequest): Promise<CollaborationResponse> {
    return {
      accepted: true,
      reason: '可以协助分析模式',
      proposedContribution: '提供模式识别结果'
    };
  }
  
  async learn(experience: Experience): Promise<void> {
    console.log(`[${this.name}] 学习经验: ${experience.outcome}`);
  }
  
  async communicate(message: string): Promise<string> {
    return `[模式识别器] 收到: "${message}"。我可以帮您发现数据中的模式。`;
  }
}

/**
 * 决策生成器 - 只负责给行动建议
 */
class DecisionGenerator implements IAgent {
  id = 'decision-generator';
  name = '决策生成器';
  description = '专门负责基于分析结果给出行动建议';
  
  capabilities = [
    '生成行动建议',
    '评估风险',
    '优先级排序',
    '方案对比',
    '向人提问'
  ];
  
  limitations = [
    '不执行行动',
    '不收集数据',
    '不分析模式'
  ];
  
  async canHandle(task: Task): Promise<boolean> {
    return task.type === 'decide' || task.type === 'recommend' || task.type === 'prioritize';
  }
  
  async decide(task: Task): Promise<Decision> {
    // 如果信息不足，问人
    if (!task.context || Object.keys(task.context).length === 0) {
      return {
        action: 'ask_human',
        reasoning: '缺乏决策所需的上下文信息',
        humanQuestion: '为了给出更好的建议，我需要了解更多背景信息。您能告诉我这个决策的重要性和时间紧迫性吗？'
      };
    }
    
    return {
      action: 'execute',
      reasoning: '信息充足，可以生成决策建议',
      plan: {
        steps: [
          { action: '分析上下文', expectedOutcome: '上下文理解' },
          { action: '生成候选方案', expectedOutcome: '方案列表' },
          { action: '评估和排序', expectedOutcome: '推荐方案' }
        ],
        estimatedTime: 3000,
        requiredResources: ['上下文信息']
      }
    };
  }
  
  async requestCollaboration(task: Task, targetAgent: string): Promise<void> {
    console.log(`[${this.name}] 向 ${targetAgent} 发送协作请求`);
  }
  
  async respondToCollaboration(request: CollaborationRequest): Promise<CollaborationResponse> {
    return {
      accepted: true,
      reason: '可以协助生成决策建议',
      proposedContribution: '提供行动建议'
    };
  }
  
  async learn(experience: Experience): Promise<void> {
    console.log(`[${this.name}] 学习经验: ${experience.outcome}`);
  }
  
  async communicate(message: string): Promise<string> {
    return `[决策生成器] 收到: "${message}"。我可以帮您分析选项并给出建议。`;
  }
}

// ==================== 智能体协作网络 ====================

/**
 * 智能体协作网络 - 去中心化
 */
class AgentNetwork {
  private agents: Map<string, IAgent> = new Map();
  private taskQueue: Task[] = [];
  private collaborationHistory: CollaborationRequest[] = [];
  
  // 注册智能体
  register(agent: IAgent): void {
    this.agents.set(agent.id, agent);
    console.log(`[网络] 注册智能体: ${agent.name}`);
  }
  
  // 动态加载能力（能力组合）
  loadCapability(capability: IAgent): void {
    this.register(capability);
  }
  
  // 提交任务（可以来自人或智能体）
  async submitTask(task: Task): Promise<void> {
    console.log(`[网络] 收到任务: ${task.type}`);
    
    // 找到能处理的智能体
    const capableAgents: IAgent[] = [];
    
    for (const agent of this.agents.values()) {
      if (await agent.canHandle(task)) {
        capableAgents.push(agent);
      }
    }
    
    if (capableAgents.length === 0) {
      console.log(`[网络] 没有智能体能处理这个任务，需要人工介入`);
      return;
    }
    
    // 让智能体自主决策
    for (const agent of capableAgents) {
      const decision = await agent.decide(task);
      console.log(`[网络] ${agent.name} 决策: ${decision.action}`);
      console.log(`       原因: ${decision.reasoning}`);
      
      // 根据决策执行
      await this.executeDecision(agent, decision, task);
    }
  }
  
  // 执行决策
  private async executeDecision(agent: IAgent, decision: Decision, task: Task): Promise<void> {
    switch (decision.action) {
      case 'execute':
        console.log(`[网络] ${agent.name} 开始执行任务`);
        // 执行...
        break;
        
      case 'delegate':
        console.log(`[网络] ${agent.name} 委托给 ${decision.delegateTo}`);
        const delegate = this.agents.get(decision.delegateTo!);
        if (delegate) {
          await this.submitTask({ ...task, createdBy: 'agent' });
        }
        break;
        
      case 'collaborate':
        console.log(`[网络] ${agent.name} 请求协作: ${decision.collaborationWith}`);
        for (const targetId of decision.collaborationWith || []) {
          const target = this.agents.get(targetId);
          if (target) {
            const response = await target.respondToCollaboration({
              from: agent.id,
              to: targetId,
              task,
              reason: decision.reasoning,
              whatINeed: '数据处理支持'
            });
            console.log(`[网络] ${target.name} 响应: ${response.accepted ? '接受' : '拒绝'}`);
          }
        }
        break;
        
      case 'ask_human':
        console.log(`[网络] ${agent.name} 需要人工介入`);
        console.log(`       问题: ${decision.humanQuestion}`);
        break;
        
      case 'reject':
        console.log(`[网络] ${agent.name} 拒绝处理: ${decision.reasoning}`);
        break;
    }
  }
  
  // 人机对话
  async chat(agentId: string, message: string): Promise<string> {
    const agent = this.agents.get(agentId);
    if (!agent) {
      return '找不到这个智能体';
    }
    return await agent.communicate(message);
  }
}

// ==================== 导出 ====================

export {
  IAgent,
  Task,
  Decision,
  Experience,
  CollaborationRequest,
  CollaborationResponse,
  DataSourceSubscriber,
  DataCleaner,
  PatternRecognizer,
  DecisionGenerator,
  AgentNetwork
};
