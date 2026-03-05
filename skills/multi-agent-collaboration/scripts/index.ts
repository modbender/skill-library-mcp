/**
 * AI协作操作系统 - 主入口
 * 一站式集成：统一记忆系统 + 信息信号识别 + 工作流资产沉淀 + 个人目标追踪
 */

// 导出核心模块
export { UnifiedMemorySystem } from './core/memory';
export type { 
  MemoryEntry, 
  MemoryLevel, 
  MemoryCategory, 
  SystemType, 
  MemoryConfig,
  AIMirrorInsight 
} from './core/memory';

// 导出三个子系统
export { SignalRecognitionSystem } from './systems/signal';
export { WorkflowAssetSystem } from './systems/workflow';
export { PersonalGoalSystem } from './systems/goal';

// 导入
import { UnifiedMemorySystem, MemoryConfig } from './core/memory';
import { SignalRecognitionSystem } from './systems/signal';
import { WorkflowAssetSystem } from './systems/workflow';
import { PersonalGoalSystem } from './systems/goal';

/**
 * AI协作操作系统 - 完整集成类
 * 
 * 一行代码创建，自动关联所有系统：
 * const ai = new AICollaborationSystem('my_system');
 */
export class AICollaborationSystem {
  public memory: UnifiedMemorySystem;
  public signal: SignalRecognitionSystem;
  public workflow: WorkflowAssetSystem;
  public goal: PersonalGoalSystem;
  
  constructor(
    skillName: string = 'ai_system',
    baseDir: string = 'memory',
    config?: Partial<MemoryConfig>
  ) {
    // 初始化统一记忆系统
    this.memory = new UnifiedMemorySystem(skillName, baseDir, config);
    
    // 初始化三个子系统，共享同一个记忆实例
    this.signal = new SignalRecognitionSystem(this.memory);
    this.workflow = new WorkflowAssetSystem(this.memory);
    this.goal = new PersonalGoalSystem(this.memory);
    
    // 记录初始化
    this.memory.addToL1('系统初始化', 'AI协作操作系统启动完成', 'rule', 5);
  }
  
  // ========== 便捷方法 ==========
  
  getSummary(): string { return this.memory.getSummary(); }
  healthCheck(): any { return this.memory.healthCheck(); }
  generateInsight(): any { return this.memory.generateMirrorInsight(); }
  
  syncAllSystems(): void {
    this.signal.syncToOtherSystems();
    this.workflow.syncToOtherSystems();
    this.goal.syncToOtherSystems();
  }
  
  queryAll(query: string): any { return this.memory.queryAll(query); }
  
  // ========== 每日工作流 ==========
  
  dailyScan(rawSignals: any[]): any {
    const date = new Date().toISOString().split('T')[0];
    return this.signal.generateDailyScanReport(date, rawSignals);
  }
  
  dailyWorkflow(tasks: string[], responses: any[]): any {
    const date = new Date().toISOString().split('T')[0];
    return this.workflow.generateDailyWorkflowReport(date, tasks, responses);
  }
  
  dailyGoalTracking(goals: any[], timeLog: Record<string, number>, ideal: Record<string, number>): any {
    return this.goal.analyzeEnergyAllocation(timeLog, ideal);
  }
  
  // ========== 每周工作流 ==========
  
  weeklyReview(goals: any[], timeLog: any, ideal: any, priorities: any): any {
    const period = `${new Date(Date.now() - 7*24*60*60*1000).toISOString().split('T')[0]} - ${new Date().toISOString().split('T')[0]}`;
    return this.goal.generateWeeklySelfAwarenessReport(period, goals, timeLog, ideal, priorities);
  }
}

export default AICollaborationSystem;
