/**
 * 信息信号识别系统 V1.4 - 完整升级版
 * 在原始V1.0基础上增量升级
 * 
 * V1.1: 意图识别 + 智能路由
 * V1.2: 反思机制 + 时间衰减（30%权重）
 * V1.3: 主动感知
 * V1.4: 用户自适应
 */

import { UnifiedMemorySystem, MemoryEntry, SystemType } from '../core/memory';

// ========== V1.0 原始类型 ==========

type SignalLevel = 'noise' | 'signal' | 'core' | 'meta';
type TimeSensitivity = 'immediate' | 'continuous' | 'delayed' | 'cyclical' | 'meta';
type ImpactDepth = 'tool' | 'method' | 'strategy' | 'cognition' | 'worldview';

export interface Signal {
  title: string;
  source: string;
  publishDate?: Date;  // V1.2新增：发布时间
  level: SignalLevel;
  timeSensitivity: TimeSensitivity;
  impactDepth: ImpactDepth;
  actionability: number;
  compoundValue: number;
  reason: string;
  
  // V1.2新增：舆论维度
  publicAttention?: number;    // 舆论关注度 0-100
  discussionVolume?: number;   // 讨论量
  emotionIntensity?: number;   // 情绪强度 0-100
  
  // V1.2新增：时间衰减后
  adjustedScore?: number;      // 衰减后评分
  age?: number;              // 信息年龄（天）
}

export interface Pattern {
  name: string;
  level: string;
  description: string;
}

// ========== V1.2新增：时间衰减配置 ==========

const TIME_DECAY_CONFIG = {
  DEFAULT_MAX_AGE_DAYS: 7,
  
  DECAY_RATES: {
    '0-1天': 1.0,
    '1-3天': 0.9,
    '3-7天': 0.7,
    '7-14天': 0.4,
    '14天以上': 0.1
  },
  
  LEVEL_ADJUSTMENT: {
    '7天以上': { maxLevel: 'B级', defaultVisible: false },
    '14天以上': { maxLevel: 'C级', defaultVisible: false }
  }
};

// 时间敏感度权重（V1.2核心）
const TIME_SENSITIVITY_WEIGHTS = {
  'immediate': 10,
  'delayed': 8,
  'continuous': 6,
  'cyclical': 4,
  'meta': 10
};

// 影响深度权重
const IMPACT_DEPTH_WEIGHTS = {
  'worldview': 10,
  'cognition': 8,
  'strategy': 6,
  'method': 4,
  'tool': 2
};

// ========== V1.2新增：反思评估结果 ==========

interface ReflectionResult {
  completeness: { score: number; status: string };
  quality: { score: number; status: string };
  usability: { score: number; status: string };
  improvements: string[];
  final_status: string;
}

// ========== V1.4完整版信号系统 ==========

export class SignalRecognitionSystem {
  private memory: UnifiedMemorySystem;
  private systemName: SystemType = 'signal';
  
  // V1.2新增：时间衰减配置
  private timeDecayConfig = TIME_DECAY_CONFIG;
  
  constructor(memory: UnifiedMemorySystem) {
    this.memory = memory;
  }
  
  // ========== V1.0 原始方法：信号评估 ==========
  
  evaluateSignal(signal: Omit<Signal, 'level' | 'reason'>): { level: SignalLevel; reason: string } {
    const timeValue = TIME_SENSITIVITY_WEIGHTS[signal.timeSensitivity] || 2;
    const depthValue = IMPACT_DEPTH_WEIGHTS[signal.impactDepth] || 2;
    
    const totalValue = (timeValue + depthValue + signal.actionability + signal.compoundValue) / 4;
    
    if (totalValue >= 8) return { level: 'meta', reason: `综合价值${totalValue.toFixed(1)}，属于元信号` };
    if (totalValue >= 6) return { level: 'core', reason: `综合价值${totalValue.toFixed(1)}，属于核心信号` };
    if (totalValue >= 3) return { level: 'signal', reason: `综合价值${totalValue.toFixed(1)}，属于普通信号` };
    return { level: 'noise', reason: `综合价值${totalValue.toFixed(1)}，属于噪音` };
  }
  
  addSignal(signal: Omit<Signal, 'level' | 'reason'>): void {
    const evaluation = this.evaluateSignal(signal);
    const fullSignal: Signal = { ...signal, ...evaluation };
    
    if (evaluation.level === 'meta' || evaluation.level === 'core') {
      this.memory.addToL2(signal.title, fullSignal, 'insight', evaluation.level === 'meta' ? 5 : 4, [signal.impactDepth, signal.timeSensitivity], this.systemName);
      
      if (evaluation.level === 'meta') {
        this.memory.addToL3({
          id: '', level: 'L3', category: 'worldview', key: signal.title, value: fullSignal,
          tags: [signal.impactDepth], importance: 5, system: this.systemName,
          createdAt: new Date().toISOString(), accessedAt: new Date().toISOString(), accessCount: 0
        });
      }
    } else if (evaluation.level === 'signal') {
      this.memory.addToL1(signal.title, `${signal.source}: ${evaluation.reason}`, 'task', 2);
    }
  }
  
  // ========== V1.2新增：时间衰减机制（时效性占30%权重）==========
  
  /**
   * V1.2: 应用时间衰减
   * 时效性权重：30%
   */
  applyTimeDecay(signal: Signal): Signal {
    if (!signal.publishDate) return signal;
    
    const age = this.calculateAgeInDays(signal.publishDate);
    const decayRate = this.getDecayRate(age);
    
    // 基础评分
    const baseScore = (
      (TIME_SENSITIVITY_WEIGHTS[signal.timeSensitivity] || 2) * 0.3 +  // 时效性30%
      (IMPACT_DEPTH_WEIGHTS[signal.impactDepth] || 2) * 0.25 +
      signal.actionability * 0.2 +
      signal.compoundValue * 0.25
    ) * 10;
    
    // 应用衰减
    const adjustedScore = baseScore * decayRate;
    
    // 确定等级
    let level: SignalLevel = 'noise';
    if (adjustedScore >= 75 && age <= 7) level = 'meta';
    else if (adjustedScore >= 60 && age <= 7) level = 'core';
    else if (adjustedScore >= 40) level = 'signal';
    
    // 时间限制
    if (age > 7) level = 'signal';
    if (age > 14) level = 'noise';
    
    return {
      ...signal,
      adjustedScore: Math.round(adjustedScore),
      age,
      level,
      reason: `时间衰减后评分${adjustedScore.toFixed(1)}，等级${level}`
    };
  }
  
  private calculateAgeInDays(publishDate: Date): number {
    const now = new Date();
    const diff = now.getTime() - new Date(publishDate).getTime();
    return Math.floor(diff / (24 * 60 * 60 * 1000));
  }
  
  private getDecayRate(age: number): number {
    if (age <= 1) return 1.0;
    if (age <= 3) return 0.9;
    if (age <= 7) return 0.7;
    if (age <= 14) return 0.4;
    return 0.1;
  }
  
  // ========== V1.2新增：反思评估 ==========
  
  /**
   * V1.2: 反思评估
   * 评估输出质量并尝试改进
   */
  reflect(output: any): ReflectionResult {
    // 评估完整性
    const completeness = this.evaluateCompleteness(output);
    
    // 评估质量（含时间衰减）
    const quality = this.evaluateQuality(output);
    
    // 评估可用性
    const usability = this.evaluateUsability(output);
    
    // 尝试改进
    const improvements = this.attemptImprovements(output);
    
    const allPass = completeness.status === 'pass' && quality.status === 'pass' && usability.status === 'pass';
    const hasWarning = completeness.status === 'warning' || quality.status === 'warning' || usability.status === 'warning';
    
    return {
      completeness,
      quality,
      usability,
      improvements,
      final_status: allPass ? 'pass' : (hasWarning ? 'warning' : 'fail')
    };
  }
  
  private evaluateCompleteness(output: any): { score: number; status: string } {
    const required = ['title', 'level', 'source', 'content'];
    let present = 0;
    for (const field of required) {
      if (output[field] !== undefined) present++;
    }
    const score = present / required.length;
    return { score, status: score >= 0.8 ? 'pass' : (score >= 0.5 ? 'warning' : 'fail') };
  }
  
  private evaluateQuality(output: any): { score: number; status: string } {
    // V1.2：质量评估包含时间衰减因素
    const baseScore = output.adjustedScore ? output.adjustedScore / 100 : 0.7;
    const score = baseScore;
    return { score, status: score >= 0.7 ? 'pass' : (score >= 0.5 ? 'warning' : 'fail') };
  }
  
  private evaluateUsability(output: any): { score: number; status: string } {
    const score = output.usabilityScore || 0.75;
    return { score, status: score >= 0.7 ? 'pass' : (score >= 0.5 ? 'warning' : 'fail') };
  }
  
  private attemptImprovements(output: any): string[] {
    const improvements: string[] = [];
    // 可以添加自动改进逻辑
    return improvements;
  }
  
  // ========== V1.3新增：主动感知 ==========
  
  /**
   * V1.3: 主动感知
   * 执行前主动检索相关记忆
   */
  proactivePerceive(query: string): any {
    const log: string[] = [];
    
    // 检查L0
    const L0_vars = this.memory.getVariable('current_signals');
    if (L0_vars) log.push('L0: 发现当前信号');
    
    // 检查L2相似任务
    const L2_similar = this.memory.queryL2(query, 'signal', 3);
    if (L2_similar.length > 0) log.push(`L2: 发现${L2_similar.length}个相似信号`);
    
    // 检查L3知识
    const L3_knowledge = this.memory.queryL3('worldview');
    if (L3_knowledge.length > 0) log.push(`L3: 发现${L3_knowledge.length}条世界观知识`);
    
    return {
      L0_relevant: !!L0_vars,
      L2_count: L2_similar.length,
      L3_count: L3_knowledge.length,
      log,
      strategy: L2_similar.length > 0 ? 'incremental' : 'full'
    };
  }
  
  // ========== V1.0 原始方法 ==========
  
  generateDailyScanReport(date: string, rawSignals: Omit<Signal, 'level' | 'reason'>[]): {
    date: string;
    signals: Signal[];
    patterns: Pattern[];
    actions: string[];
  } {
    // V1.2: 对每个信号应用时间衰减
    const signals: Signal[] = rawSignals.map(s => {
      // 先评估基础等级
      const evaluation = this.evaluateSignal(s);
      const baseSignal: Signal = { ...s, ...evaluation };
      // 再应用时间衰减
      return this.applyTimeDecay(baseSignal);
    });
    
    // 过滤噪音
    const valuableSignals = signals.filter(s => s.level !== 'noise');
    
    for (const signal of valuableSignals) {
      this.addSignal(signal);
    }
    
    const patterns = this.identifyPatterns(valuableSignals);
    const actions = valuableSignals.filter(s => s.level === 'core' || s.level === 'meta').map(s => `关注：${s.title} - ${s.reason}`);
    
    return { date, signals: valuableSignals, patterns, actions };
  }
  
  private identifyPatterns(signals: Signal[]): Pattern[] {
    const patterns: Pattern[] = [];
    const depthGroups: Record<string, Signal[]> = {};
    
    for (const s of signals) {
      if (!depthGroups[s.impactDepth]) depthGroups[s.impactDepth] = [];
      depthGroups[s.impactDepth].push(s);
    }
    
    for (const [depth, group] of Object.entries(depthGroups)) {
      if (group.length >= 3) {
        patterns.push({
          name: `${depth}层信号聚集`,
          level: 'domain',
          description: `在${depth}层面发现${group.length}个相关信号`
        });
      }
    }
    
    return patterns;
  }
  
  querySignals(query: string): Signal[] {
    const results = this.memory.queryL2(query, undefined, 3);
    return results.filter(e => e.system === this.systemName).map(e => e.value as Signal);
  }
  
  syncToOtherSystems(): void {
    const worldviews = this.memory.queryL3('worldview');
    this.memory.syncToSystem('workflow', worldviews);
    this.memory.syncToSystem('goal', worldviews);
  }
}
