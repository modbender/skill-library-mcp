/**
 * 多智能体协同控制器 V1.4 - 核心缺失功能补全
 * 
 * 实现：多智能体协同 + 用户选项 + 自动激活
 * 
 * 决策树：
 * - 模块1必须先执行
 * - 模块2/3/4可以任意顺序（但不能跳过模块1）
 * - 每轮执行完展示用户选项
 * - 用户可以随时退出
 */

import { UnifiedMemorySystem } from './core/memory';

// ========== 类型定义 ==========

// 模块类型
export type ModuleType = 'module1' | 'module2' | 'module3' | 'module4';

// 模块名称映射
export const MODULE_NAMES: Record<ModuleType, string> = {
  'module1': '信息守护者',
  'module2': '内容趋势优化系统',
  'module3': '状态洞察模块',
  'module4': '工作流沉淀系统'
};

// 可选的执行路径
export type ExecutionPath = 
  | '1→2→3→4'   // 完整流程
  | '1→2'        // 信息+创作
  | '1→2→3'      // 信息+创作+状态
  | '1→2→4'      // 信息+创作+工作流
  | '1→3'        // 信息+状态
  | '1→3→4'      // 信息+状态+工作流
  | '1→4'        // 信息+工作流
  | '1'           // 只执行模块1

// 用户选择
export type UserChoice = 
  | 'continue_to_module2'
  | 'continue_to_module3'
  | 'continue_to_module4'
  | 'exit';

// 执行状态
export interface ExecutionState {
  sessionId: string;
  currentModule: ModuleType;
  executedModules: ModuleType[];
  pendingModules: ModuleType[];
  userChoices: UserChoice[];
  startTime: string;
  lastUpdateTime: string;
}

// 模块输出
export interface ModuleOutput {
  module: ModuleType;
  output: any;
  timestamp: string;
  success: boolean;
}

// 用户选项菜单
export interface UserOptionMenu {
  currentModule: ModuleType;
  nextOptions: {
    value: UserChoice;
    label: string;
    description: string;
  }[];
  canExit: boolean;
}

// ========== 多智能体协同控制器 ==========

export class MultiAgentCoordinator {
  private memory: UnifiedMemorySystem;
  private currentState: ExecutionState | null = null;
  
  constructor(memory: UnifiedMemorySystem) {
    this.memory = memory;
  }

  // ========== 核心功能：启动协同流程 ==========
  
  /**
   * 启动多智能体协同流程
   * @param intent 识别的用户意图
   * @returns 第一个用户选项菜单
   */
  startCooperation(intent: any): UserOptionMenu {
    // 生成会话ID
    const sessionId = this.generateSessionId();
    
    // 根据意图确定初始执行路径
    const initialModules = this.determineInitialModules(intent);
    
    // 初始化执行状态
    this.currentState = {
      sessionId,
      currentModule: 'module1',
      executedModules: [],
      pendingModules: initialModules,
      userChoices: [],
      startTime: new Date().toISOString(),
      lastUpdateTime: new Date().toISOString()
    };
    
    // 返回第一个用户选项
    return this.generateOptionMenu();
  }

  // ========== 核心功能：模块执行后展示选项 ==========
  
  /**
   * 模块执行完成后，生成用户选项菜单
   * 这是核心的"协同"逻辑
   */
  generateOptionMenu(): UserOptionMenu {
    if (!this.currentState) {
      throw new Error('No active session');
    }
    
    const current = this.currentState.currentModule;
    const nextOptions: UserOptionMenu['nextOptions'] = [];
    
    // 根据当前模块确定下一步选项
    switch (current) {
      case 'module1':
        // 模块1后，可以继续到2/3/4，或退出
        nextOptions.push(
          {
            value: 'continue_to_module2',
            label: '继续到模块2（内容趋势优化系统）',
            description: '基于信息生成创作方案'
          },
          {
            value: 'continue_to_module3',
            label: '继续到模块3（状态洞察模块）',
            description: '分析个人状态'
          },
          {
            value: 'continue_to_module4',
            label: '继续到模块4（工作流沉淀系统）',
            description: '生成工作流报告'
          }
        );
        break;
        
      case 'module2':
        // 模块2后，可以继续到3/4，或退出
        nextOptions.push(
          {
            value: 'continue_to_module3',
            label: '继续到模块3（状态洞察模块）',
            description: '分析个人状态'
          },
          {
            value: 'continue_to_module4',
            label: '继续到模块4（工作流沉淀系统）',
            description: '生成工作流报告'
          }
        );
        break;
        
      case 'module3':
        // 模块3后，可以继续到4，或退出
        nextOptions.push(
          {
            value: 'continue_to_module4',
            label: '继续到模块4（工作流沉淀系统）',
            description: '生成工作流报告'
          }
        );
        break;
        
      case 'module4':
        // 模块4是最后一个，不能继续
        nextOptions = [];
        break;
    }
    
    return {
      currentModule: current,
      nextOptions,
      canExit: true
    };
  }

  // ========== 核心功能：处理用户选择 ==========
  
  /**
   * 处理用户的选择，更新状态并返回下一步
   */
  handleUserChoice(choice: UserChoice): {
    nextModule: ModuleType | null;
    menu: UserOptionMenu | null;
    isComplete: boolean;
    finalReport: any;
  } {
    if (!this.currentState) {
      throw new Error('No active session');
    }
    
    // 记录用户选择
    this.currentState.userChoices.push(choice);
    
    // 如果用户退出
    if (choice === 'exit') {
      const report = this.generateFinalReport();
      this.currentState = null;
      return {
        nextModule: null,
        menu: null,
        isComplete: true,
        finalReport: report
      };
    }
    
    // 确定下一个模块
    const nextModule = this.mapChoiceToModule(choice);
    
    if (!nextModule) {
      throw new Error('Invalid choice');
    }
    
    // 更新状态
    this.currentState.executedModules.push(this.currentState.currentModule);
    this.currentState.currentModule = nextModule;
    this.currentState.lastUpdateTime = new Date().toISOString();
    
    // 生成下一个菜单
    const menu = this.generateOptionMenu();
    
    // 检查是否完成（模块4执行完）
    const isComplete = nextModule === 'module4';
    
    return {
      nextModule,
      menu,
      isComplete: false,
      finalReport: null
    };
  }

  // ========== 辅助方法 ==========
  
  /**
   * 根据意图确定初始执行模块
   */
  private determineInitialModules(intent: any): ModuleType[] {
    const intentType = intent?.intent || 'full';
    
    switch (intentType) {
      case 'information':
        return ['module1'];
      case 'content':
        return ['module1', 'module2'];
      case 'status':
        return ['module1', 'module3'];
      case 'workflow':
        return ['module1', 'module4'];
      case 'full':
      default:
        return ['module1', 'module2', 'module3', 'module4'];
    }
  }

  /**
   * 将用户选择映射到下一个模块
   */
  private mapChoiceToModule(choice: UserChoice): ModuleType | null {
    switch (choice) {
      case 'continue_to_module2': return 'module2';
      case 'continue_to_module3': return 'module3';
      case 'continue_to_module4': return 'module4';
      default: return null;
    }
  }

  /**
   * 生成最终交付报告
   */
  private generateFinalReport(): any {
    if (!this.currentState) return null;
    
    return {
      session_info: {
        session_id: this.currentState.sessionId,
        start_time: this.currentState.startTime,
        end_time: new Date().toISOString(),
        execution_path: this.currentState.executedModules.join(' → ') + 
          (this.currentState.currentModule ? ' → ' + this.currentState.currentModule : '')
      },
      user_choices: this.currentState.userChoices,
      executed_modules: this.currentState.executedModules,
      final_module: this.currentState.currentModule
    };
  }

  /**
   * 生成会话ID
   */
  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // ========== 状态查询 ==========
  
  /**
   * 获取当前状态
   */
  getState(): ExecutionState | null {
    return this.currentState;
  }

  /**
   * 检查是否有活动会话
   */
  hasActiveSession(): boolean {
    return this.currentState !== null;
  }

  /**
   * 获取执行摘要
   */
  getSummary(): string {
    if (!this.currentState) {
      return '无活动会话';
    }
    
    const state = this.currentState;
    return `
=== 多智能体协同状态 ===
会话ID: ${state.sessionId}
当前模块: ${MODULE_NAMES[state.currentModule]}
已执行: ${state.executedModules.map(m => MODULE_NAMES[m]).join(' → ')}
待执行: ${state.pendingModules.map(m => MODULE_NAMES[m]).join(' → ')}
用户选择: ${state.userChoices.length}次
    `.trim();
  }
}

export default MultiAgentCoordinator;
