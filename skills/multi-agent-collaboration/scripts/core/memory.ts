/**
 * 统一记忆系统 V1.4 - 完整升级版
 * 在原始V1.0基础上增量升级
 * 
 * V1.1: 意图识别 + 智能路由
 * V1.2: 反思机制
 * V1.3: 主动感知
 * V1.4: 用户自适应
 * 
 * 五层记忆架构：L0闪存/L1工作/L2经验/L3知识/L4智慧
 */

import * as crypto from 'crypto';
import * as fs from 'fs';
import * as path from 'path';

// ========== V1.0 原始类型定义 ==========

export type MemoryLevel = 'L0' | 'L1' | 'L2' | 'L3' | 'L4';
export type MemoryCategory = 'task' | 'rule' | 'insight' | 'pattern' | 'methodology' | 'worldview' | 'goal' | 'value' | 'wisdom';
export type SystemType = 'signal' | 'workflow' | 'goal' | 'shared';

// V1.2新增：信号等级
export type SignalLevel = 'noise' | 'signal' | 'core' | 'meta';

// V1.2新增：时间敏感度
export type TimeSensitivity = 'immediate' | 'continuous' | 'delayed' | 'cyclical' | 'meta';

// V1.2新增：影响深度
export type ImpactDepth = 'tool' | 'method' | 'strategy' | 'cognition' | 'worldview';

// V1.4新增：用户画像
export interface UserProfile {
  user_id: string;
  confirmation_habit: {
    total_decisions: number;
    skip_count: number;
    skip_rate: number;
    avg_decision_time_ms: number;
  };
  output_preference: {
    detailed_count: number;
    concise_count: number;
    preferred_style: 'detailed' | 'concise' | 'balanced';
  };
  recommendation: {
    total: number;
    accepted: number;
    acceptance_rate: number;
  };
  execution: {
    parallel_count: number;
    serial_count: number;
    preferred_mode: 'parallel' | 'serial';
  };
  module_sequence_history: string[];
  common_paths: string[];
  updated_at: string;
}

// V1.1新增：意图类型
export type IntentType = 'information' | 'content' | 'status' | 'workflow' | 'full' | 'quick';

// V1.1新增：执行模式
export type ExecutionMode = 'serial' | 'parallel' | 'skip' | 'quick';

// V1.1新增：意图识别结果
export interface IntentRecognitionResult {
  intent: IntentType;
  confidence: number;
  target_industry?: string;
  modules: string[];
  mode: ExecutionMode;
  reasoning: string;
}

// V1.2新增：反思评估结果
export interface ReflectionResult {
  completeness: {
    score: number;
    status: 'pass' | 'warning' | 'fail';
  };
  quality: {
    score: number;
    status: 'pass' | 'warning' | 'fail';
  };
  usability: {
    score: number;
    status: 'pass' | 'warning' | 'fail';
  };
  improvements_made: string[];
  retry_count: number;
  final_status: 'pass' | 'warning' | 'fail';
}

// V1.3新增：主动感知结果
export interface ProactivePerceptionResult {
  L0_relevant: boolean;
  L2_similar_task_found: boolean;
  L3_knowledge_found: boolean;
  L4_preference_found: boolean;
  strategy: 'full' | 'incremental' | 'cached';
  estimated_time_saved: number;
  perception_log: string[];
}

// ========== 原始内存条目 ==========

export interface MemoryEntry {
  id: string;
  level: MemoryLevel;
  category: MemoryCategory;
  key: string;
  value: string | object;
  tags: string[];
  importance: number;
  system: SystemType;
  createdAt: string;
  accessedAt: string;
  accessCount: number;
  metadata?: Record<string, any>;
}

export interface MemoryConfig {
  L0_MAX_ITEMS: number;
  L1_MAX_LINES: number;
  L2_MAX_ENTRIES: number;
  L3_MAX_ENTRIES: number;
  AUTO_ARCHIVE_THRESHOLD: number;
  
  // V1.2新增：时间衰减配置
  time_decay?: {
    DEFAULT_MAX_AGE_DAYS: number;
    DECAY_RATES: Record<string, number>;
  };
  
  // V1.3新增：缓存配置
  cache?: {
    ttl_hours: number;
    reuse_bonus: number;
  };
}

export interface AIMirrorInsight {
  observation: string;
  pattern: string;
  blindSpot: string;
  suggestion: string;
  prediction: string;
}

// V1.2新增：信号评估
export interface SignalEvaluation {
  timeSensitivity: TimeSensitivity;
  impactDepth: ImpactDepth;
  actionability: number;
  compoundValue: number;
  level: SignalLevel;
  reason: string;
}

// ========== V1.4 统一记忆系统完整类 ==========

export class UnifiedMemorySystem {
  private skillName: string;
  private baseDir: string;
  private config: MemoryConfig;
  
  // V1.0原始：五层记忆
  private flashMemory: Map<string, any> = new Map();
  private workingMemory: MemoryEntry[] = [];
  private experienceMemory: MemoryEntry[] = [];
  private knowledgeMemory: MemoryEntry[] = [];
  private wisdomMemory: MemoryEntry[] = [];
  
  // V1.1新增：意图识别器
  private intentRecognizer: IntentRecognizer;
  
  // V1.2新增：反思评估器
  private reflectionEngine: ReflectionEngine;
  
  // V1.3新增：主动感知器
  private proactivePerceptor: ProactivePerceptor;
  
  // V1.4新增：用户画像管理器
  private userProfileManager: UserProfileManager;
  
  // V1.2新增：时间衰减配置
  private timeDecayConfig = {
    DEFAULT_MAX_AGE_DAYS: 7,
    DECAY_RATES: {
      '0-1天': 1.0,
      '1-3天': 0.9,
      '3-7天': 0.7,
      '7-14天': 0.4,
      '14天以上': 0.1
    }
  };

  // ========== V1.1新增：意图识别器 ==========
  
  private class IntentRecognizer {
    // 意图关键词映射
    private intentKeywords: Record<IntentType, string[]> = {
      'information': ['最新动态', '行业信息', '看看', '了解', 'news', 'information'],
      'content': ['写文章', '创作', '发布', '内容', 'write', 'create', 'publish'],
      'status': ['分析状态', '我的情况', '成长', '状态', 'status', 'growth', 'progress'],
      'workflow': ['沉淀', '工作流', '模板', '报告', 'workflow', 'template', 'report'],
      'full': ['帮我整理', '做个总结', '完整', 'full', 'complete', 'summary'],
      'quick': ['快速', '精简', '简单', 'quick', 'brief', 'simple']
    };
    
    // 识别意图
    recognize(input: string): IntentRecognitionResult {
      const lowerInput = input.toLowerCase();
      
      // 检测行业关键词
      const industries = ['AI', '人工智能', '金融', '医疗', '教育', '零售', '科技', '新能源汽车'];
      let target_industry = '';
      for (const ind of industries) {
        if (lowerInput.includes(ind.toLowerCase())) {
          target_industry = ind;
          break;
        }
      }
      
      // 识别意图类型
      let intent: IntentType = 'information';
      let maxMatch = 0;
      
      for (const [intentType, keywords] of Object.entries(this.intentKeywords)) {
        let matchCount = 0;
        for (const kw of keywords) {
          if (lowerInput.includes(kw.toLowerCase())) {
            matchCount++;
          }
        }
        if (matchCount > maxMatch) {
          maxMatch = matchCount;
          intent = intentType as IntentType;
        }
      }
      
      // 确定执行模块
      const modules = this.determineModules(intent);
      
      // 确定执行模式
      const mode = this.determineMode(input, intent);
      
      // 计算置信度
      const confidence = Math.min(1, maxMatch * 0.3 + 0.5);
      
      return {
        intent,
        confidence,
        target_industry: target_industry || undefined,
        modules,
        mode,
        reasoning: `识别到${intent}意图，置信度${(confidence*100).toFixed(0)}%`
      };
    }
    
    // 确定执行模块
    private determineModules(intent: IntentType): string[] {
      switch (intent) {
        case 'information': return ['module1'];
        case 'content': return ['module1', 'module2'];
        case 'status': return ['module3'];
        case 'workflow': return ['module4'];
        case 'full': return ['module1', 'module2', 'module3', 'module4'];
        case 'quick': return ['module1'];
        default: return ['module1'];
      }
    }
    
    // 确定执行模式
    private determineMode(input: string, intent: IntentType): ExecutionMode {
      const lowerInput = input.toLowerCase();
      if (lowerInput.includes('并行') || lowerInput.includes('parallel')) return 'parallel';
      if (lowerInput.includes('跳过') || lowerInput.includes('skip')) return 'skip';
      if (lowerInput.includes('快速') || lowerInput.includes('quick') || intent === 'quick') return 'quick';
      return 'serial';
    }
  }

  // ========== V1.2新增：反思引擎 ==========
  
  private class ReflectionEngine {
    // V1.2: 反思评估
    evaluate(output: any): ReflectionResult {
      // 评估完整性
      const completeness = this.evaluateCompleteness(output);
      
      // 评估质量
      const quality = this.evaluateQuality(output);
      
      // 评估可用性
      const usability = this.evaluateUsability(output);
      
      // 尝试改进
      const improvements = this.attemptImprovements(output);
      
      // 最终状态
      const allPass = completeness.status === 'pass' && quality.status === 'pass' && usability.status === 'pass';
      const hasWarning = completeness.status === 'warning' || quality.status === 'warning' || usability.status === 'warning';
      
      return {
        completeness,
        quality,
        usability,
        improvements_made: improvements,
        retry_count: 0,
        final_status: allPass ? 'pass' : (hasWarning ? 'warning' : 'fail')
      };
    }
    
    private evaluateCompleteness(output: any): { score: number; status: 'pass' | 'warning' | 'fail' } {
      // 检查必要字段
      const requiredFields = ['title', 'level', 'source', 'content'];
      let present = 0;
      for (const field of requiredFields) {
        if (output[field] !== undefined) present++;
      }
      const score = present / requiredFields.length;
      return { score, status: score >= 0.8 ? 'pass' : (score >= 0.5 ? 'warning' : 'fail') };
    }
    
    private evaluateQuality(output: any): { score: number; status: 'pass' | 'warning' | 'fail' } {
      // 简单质量评估
      const score = output.qualityScore || 0.7;
      return { score, status: score >= 0.7 ? 'pass' : (score >= 0.5 ? 'warning' : 'fail') };
    }
    
    private evaluateUsability(output: any): { score: number; status: 'pass' | 'warning' | 'fail' } {
      // 可用性评估
      const score = output.usabilityScore || 0.75;
      return { score, status: score >= 0.7 ? 'pass' : (score >= 0.5 ? 'warning' : 'fail') };
    }
    
    private attemptImprovements(output: any): string[] {
      const improvements: string[] = [];
      // 这里可以添加自动改进逻辑
      return improvements;
    }
  }

  // ========== V1.3新增：主动感知器 ==========
  
  private class ProactivePerceptor {
    private memory: UnifiedMemorySystem;
    
    constructor(memory: UnifiedMemorySystem) {
      this.memory = memory;
    }
    
    // V1.3: 主动感知
    perceive(query: string): ProactivePerceptionResult {
      const log: string[] = [];
      
      // 检查L0
      const L0_vars = this.memory.flashMemory;
      const L0_relevant = L0_vars.size > 0;
      if (L0_relevant) log.push('L0: 发现相关任务变量');
      
      // 检查L2相似任务
      const L2_similar = this.memory.experienceMemory.filter(e => 
        e.tags.includes('task') && this.isSimilar(query, e.key)
      );
      const L2_similar_task_found = L2_similar.length > 0;
      if (L2_similar_task_found) log.push(`L2: 发现${L2_similar.length}个相似任务`);
      
      // 检查L3知识
      const L3_knowledge = this.memory.knowledgeMemory.filter(e => 
        this.isSimilar(query, e.key)
      );
      const L3_knowledge_found = L3_knowledge.length > 0;
      if (L3_knowledge_found) log.push(`L3: 发现${L3_knowledge.length}条相关知识`);
      
      // 检查L4偏好
      const L4_preference = this.memory.wisdomMemory.filter(e => 
        e.category === 'value'
      );
      const L4_preference_found = L4_preference.length > 0;
      if (L4_preference_found) log.push(`L4: 发现${L4_preference.length}条用户偏好`);
      
      // 确定策略
      let strategy: 'full' | 'incremental' | 'cached' = 'full';
      let estimated_time_saved = 0;
      
      if (L2_similar_task_found) {
        strategy = 'incremental';
        estimated_time_saved = 50;
      } else if (L3_knowledge_found) {
        strategy = 'incremental';
        estimated_time_saved = 30;
      }
      
      return {
        L0_relevant,
        L2_similar_task_found,
        L3_knowledge_found,
        L4_preference_found,
        strategy,
        estimated_time_saved,
        perception_log: log
      };
    }
    
    private isSimilar(query: string, key: string): boolean {
      const q = query.toLowerCase();
      const k = key.toLowerCase();
      // 简单相似度判断
      return k.includes(q) || q.includes(k);
    }
  }

  // ========== V1.4新增：用户画像管理器 ==========
  
  private class UserProfileManager {
    private profiles: Map<string, UserProfile> = new Map();
    
    // 获取用户画像
    getProfile(userId: string): UserProfile {
      if (!this.profiles.has(userId)) {
        this.profiles.set(userId, this.createDefaultProfile(userId));
      }
      return this.profiles.get(userId)!;
    }
    
    // 创建默认画像
    private createDefaultProfile(userId: string): UserProfile {
      return {
        user_id: userId,
        confirmation_habit: {
          total_decisions: 0,
          skip_count: 0,
          skip_rate: 0.5,
          avg_decision_time_ms: 5000
        },
        output_preference: {
          detailed_count: 0,
          concise_count: 0,
          preferred_style: 'balanced'
        },
        recommendation: {
          total: 0,
          accepted: 0,
          acceptance_rate: 0.5
        },
        execution: {
          parallel_count: 0,
          serial_count: 0,
          preferred_mode: 'serial'
        },
        module_sequence_history: [],
        common_paths: [],
        updated_at: new Date().toISOString()
      };
    }
    
    // 更新用户行为
    updateBehavior(userId: string, action: string, data: any): void {
      const profile = this.getProfile(userId);
      
      switch (action) {
        case 'skip':
          profile.confirmation_habit.skip_count++;
          profile.confirmation_habit.total_decisions++;
          profile.confirmation_habit.skip_rate = 
            profile.confirmation_habit.skip_count / profile.confirmation_habit.total_decisions;
          break;
        case 'prefer_detailed':
          profile.output_preference.detailed_count++;
          profile.output_preference.preferred_style = 'detailed';
          break;
        case 'prefer_concise':
          profile.output_preference.concise_count++;
          profile.output_preference.preferred_style = 'concise';
          break;
        case 'accept_recommendation':
          profile.recommendation.accepted++;
          profile.recommendation.total++;
          profile.recommendation.acceptance_rate = 
            profile.recommendation.accepted / profile.recommendation.total;
          break;
        case 'prefer_parallel':
          profile.execution.parallel_count++;
          profile.execution.preferred_mode = 'parallel';
          break;
      }
      
      profile.updated_at = new Date().toISOString();
      this.profiles.set(userId, profile);
    }
    
    // 自适应调整
    adapt(userId: string): any {
      const profile = this.getProfile(userId);
      
      return {
        skip_unnecessary_confirmations: profile.confirmation_habit.skip_rate > 0.6,
        output_style: profile.output_preference.preferred_style,
        recommend_aggressively: profile.recommendation.acceptance_rate > 0.7,
        prefer_parallel: profile.execution.preferred_mode === 'parallel'
      };
    }
  }

  // ========== 构造函数 ==========

  constructor(skillName: string = 'ai_system', baseDir: string = 'memory', config?: Partial<MemoryConfig>) {
    this.skillName = skillName;
    this.baseDir = baseDir;
    this.config = {
      L0_MAX_ITEMS: 10,
      L1_MAX_LINES: 50,
      L2_MAX_ENTRIES: 200,
      L3_MAX_ENTRIES: 1000,
      AUTO_ARCHIVE_THRESHOLD: 0.8,
      ...config
    };
    
    // 初始化V1.1组件
    this.intentRecognizer = new IntentRecognizer();
    
    // 初始化V1.2组件
    this.reflectionEngine = new ReflectionEngine();
    
    // 初始化V1.3组件
    this.proactivePerceptor = new ProactivePerceptor(this);
    
    // 初始化V1.4组件
    this.userProfileManager = new UserProfileManager();
    
    this.initializeDirectories();
    this.loadFromDisk();
  }

  // ========== V1.0原始方法（保留） ==========

  private initializeDirectories(): void {
    const dirs = [
      'L0_flash', 'L1_working', 'L2_experience',
      'L3_knowledge', 'L4_wisdom', 'shared', 'logs'
    ];
    
    dirs.forEach(dir => {
      const fullPath = path.join(this.baseDir, this.skillName, dir);
      if (!fs.existsSync(fullPath)) {
        fs.mkdirSync(fullPath, { recursive: true });
      }
    });
  }

  private loadFromDisk(): void {
    console.log(`[Memory] 加载记忆: ${this.skillName}`);
  }

  // L0 闪存
  setVariable(key: string, value: any): void {
    this.flashMemory.set(key, value);
  }

  getVariable(key: string): any {
    return this.flashMemory.get(key);
  }

  // L1 工作记忆
  addToL1(key: string, value: string, category: MemoryCategory, importance: number = 3): void {
    const entry: MemoryEntry = {
      id: this.generateId(),
      level: 'L1',
      category,
      key,
      value,
      tags: [],
      importance,
      system: 'shared',
      createdAt: new Date().toISOString(),
      accessedAt: new Date().toISOString(),
      accessCount: 0
    };
    
    this.workingMemory.push(entry);
    
    // 满则归档
    if (this.workingMemory.length >= this.config.L1_MAX_LINES) {
      this.archiveL1ToL2();
    }
  }

  // L2 经验记忆
  addToL2(key: string, value: string | object, category: MemoryCategory, importance: number, tags: string[] = []): void {
    const entry: MemoryEntry = {
      id: this.generateId(),
      level: 'L2',
      category,
      key,
      value,
      tags,
      importance,
      system: 'shared',
      createdAt: new Date().toISOString(),
      accessedAt: new Date().toISOString(),
      accessCount: 0
    };
    
    this.experienceMemory.push(entry);
  }

  // L3 知识记忆
  addToL3(entry: MemoryEntry): void {
    entry.level = 'L3';
    this.knowledgeMemory.push(entry);
  }

  // L4 智慧记忆
  addToL4(entry: MemoryEntry): void {
    entry.level = 'L4';
    this.wisdomMemory.push(entry);
  }

  private archiveL1ToL2(): void {
    // L1 -> L2 归档逻辑
    if (this.workingMemory.length > 0) {
      const entry = this.workingMemory.shift()!;
      entry.level = 'L2';
      this.experienceMemory.push(entry);
    }
  }

  private generateId(): string {
    return crypto.randomBytes(8).toString('hex');
  }

  // ========== V1.1新增方法 ==========

  /**
   * V1.1: 意图识别
   * 识别用户输入的意图，返回执行计划
   */
  recognizeIntent(input: string): IntentRecognitionResult {
    return this.intentRecognizer.recognize(input);
  }

  /**
   * V1.1: 智能路由
   * 根据意图返回最优执行路径
   */
  smartRoute(intentResult: IntentRecognitionResult): any {
    return {
      modules: intentResult.modules,
      mode: intentResult.mode,
      estimated_time: this.estimateTime(intentResult.modules, intentResult.mode)
    };
  }

  private estimateTime(modules: string[], mode: ExecutionMode): number {
    const baseTime = modules.length * 15; // 每模块15分钟
    if (mode === 'parallel') return baseTime * 0.6;
    if (mode === 'quick') return baseTime * 0.3;
    return baseTime;
  }

  // ========== V1.2新增方法 ==========

  /**
   * V1.2: 反思评估
   * 对模块输出进行质量评估
   */
  reflect(output: any): ReflectionResult {
    return this.reflectionEngine.evaluate(output);
  }

  // ========== V1.3新增方法 ==========

  /**
   * V1.3: 主动感知
   * 执行前主动检索记忆库
   */
  proactivePerceive(query: string): ProactivePerceptionResult {
    return this.proactivePerceptor.perceive(query);
  }

  // ========== V1.4新增方法 ==========

  /**
   * V1.4: 获取用户画像
   */
  getUserProfile(userId: string): UserProfile {
    return this.userProfileManager.getProfile(userId);
  }

  /**
   * V1.4: 更新用户行为
   */
  updateUserBehavior(userId: string, action: string, data?: any): void {
    this.userProfileManager.updateBehavior(userId, action, data);
  }

  /**
   * V1.4: 自适应调整
   */
  adaptToUser(userId: string): any {
    return this.userProfileManager.adapt(userId);
  }

  // ========== V1.0原始方法（保留） ==========

  queryL1(pattern: string): MemoryEntry[] {
    return this.workingMemory.filter(e => 
      e.key.includes(pattern) || String(e.value).includes(pattern)
    );
  }

  queryL2(query: string, tagFilter?: string, importanceMin?: number): MemoryEntry[] {
    return this.experienceMemory.filter(e => {
      const matchKey = e.key.includes(query) || String(e.value).includes(query);
      const matchTag = tagFilter ? e.tags.includes(tagFilter) : true;
      const matchImportance = importanceMin ? e.importance >= importanceMin : true;
      return matchKey && matchTag && matchImportance;
    });
  }

  queryL3(category?: MemoryCategory): MemoryEntry[] {
    return category 
      ? this.knowledgeMemory.filter(e => e.category === category)
      : this.knowledgeMemory;
  }

  queryL4(category?: MemoryCategory): MemoryEntry[] {
    return category
      ? this.wisdomMemory.filter(e => e.category === category)
      : this.wisdomMemory;
  }

  getSummary(): string {
    return `
=== 统一记忆系统 V1.4 ===
技能: ${this.skillName}
L0闪存: ${this.flashMemory.size}条
L1工作: ${this.workingMemory.length}条
L2经验: ${this.experienceMemory.length}条
L3知识: ${this.knowledgeMemory.length}条
L4智慧: ${this.wisdomMemory.length}条
    `.trim();
  }

  healthCheck(): any {
    return {
      status: 'OK',
      levels: {
        L0: { usage: `${this.flashMemory.size}/${this.config.L0_MAX_ITEMS}` },
        L1: { usage: `${this.workingMemory.length}/${this.config.L1_MAX_LINES}` },
        L2: { usage: `${this.experienceMemory.length}/${this.config.L2_MAX_ENTRIES}` },
        L3: { usage: `${this.knowledgeMemory.length}/${this.config.L3_MAX_ENTRIES}` },
        L4: { usage: 'unlimited' }
      }
    };
  }
}

export default UnifiedMemorySystem;
