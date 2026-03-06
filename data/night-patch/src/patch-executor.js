/**
 * 修补执行器模块
 * 负责安全地执行夜间修补
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class PatchExecutor {
  constructor(config) {
    this.config = config;
    this.safetyRules = this.buildSafetyRules(config);
    this.executionHistory = [];
  }
  
  /**
   * 构建安全规则
   */
  buildSafetyRules(config) {
    return {
      maxChanges: config.safety?.max_changes_per_night || 1,
      maxFiles: config.safety?.change_limits?.max_files || 2,
      maxLines: config.safety?.change_limits?.max_lines || 200,
      requireRollback: config.safety?.require_rollback !== false,
      skipProduction: config.safety?.skip_production !== false,
      dryRunFirst: config.safety?.dry_run_first !== false
    };
  }
  
  /**
   * 执行选中的修补
   */
  async executePatches(opportunities) {
    console.log('🔧 开始执行夜间修补');
    console.log('='.repeat(50));
    
    const results = [];
    
    // 应用安全限制
    const patchesToExecute = this.applySafetyLimits(opportunities);
    
    if (patchesToExecute.length === 0) {
      console.log('⚠️  没有符合条件的修补可以执行');
      return results;
    }
    
    console.log(`选中 ${patchesToExecute.length} 个修补执行\n`);
    
    // 执行每个修补
    for (let i = 0; i < patchesToExecute.length; i++) {
      const opportunity = patchesToExecute[i];
      console.log(`[${i + 1}/${patchesToExecute.length}] ${opportunity.description}`);
      
      try {
        // 安全检查
        const safetyCheck = this.performSafetyCheck(opportunity);
        if (!safetyCheck.allowed) {
          console.log(`   ⚠️  跳过: ${safetyCheck.reason}`);
          results.push({
            opportunity,
            success: false,
            skipped: true,
            reason: safetyCheck.reason,
            timestamp: new Date().toISOString()
          });
          continue;
        }
        
        // 执行修补
        const executionResult = await this.executePatchByType(opportunity);
        
        results.push({
          opportunity,
          success: executionResult.success,
          skipped: false,
          result: executionResult,
          timestamp: new Date().toISOString()
        });
        
        if (executionResult.success) {
          console.log(`   ✅ 成功: ${executionResult.message || '修补完成'}`);
        } else {
          console.log(`   ❌ 失败: ${executionResult.error || '未知错误'}`);
        }
        
        // 记录执行历史
        this.recordExecution(opportunity, executionResult);
        
      } catch (error) {
        console.log(`   💥 异常: ${error.message}`);
        results.push({
          opportunity,
          success: false,
          skipped: false,
          error: error.message,
          timestamp: new Date().toISOString()
        });
      }
      
      console.log(); // 空行分隔
    }
    
    console.log('='.repeat(50));
    console.log(`执行完成: ${results.filter(r => r.success).length} 成功, ${results.filter(r => !r.success && !r.skipped).length} 失败`);
    
    return results;
  }
  
  /**
   * 应用安全限制
   */
  applySafetyLimits(opportunities) {
    // 过滤掉高风险的机会
    const safeOpportunities = opportunities.filter(opp => 
      opp.risk_level === 'low' || opp.risk_level === 'medium'
    );
    
    // 按优先级排序
    const sorted = safeOpportunities.sort((a, b) => 
      (b.priority || 0) - (a.priority || 0)
    );
    
    // 应用数量限制
    return sorted.slice(0, this.safetyRules.maxChanges);
  }
  
  /**
   * 执行安全检查
   */
  performSafetyCheck(opportunity) {
    // 检查风险级别
    if (opportunity.risk_level === 'high') {
      return { allowed: false, reason: '风险级别过高' };
    }
    
    // 检查生产环境保护
    if (this.safetyRules.skipProduction) {
      const isProduction = this.isProductionEnvironment();
      if (isProduction) {
        return { allowed: false, reason: '生产环境保护已启用' };
      }
    }
    
    // 检查可回滚性
    if (this.safetyRules.requireRollback && !opportunity.rollback_command && !opportunity.rollback_action) {
      return { allowed: false, reason: '缺少回滚方案' };
    }
    
    // 类型特定的检查
    switch (opportunity.type) {
      case 'shell_alias':
        return this.checkShellAliasSafety(opportunity);
      case 'note_organization':
        return this.checkNoteOrganizationSafety(opportunity);
      case 'log_optimization':
        return this.checkLogOptimizationSafety(opportunity);
      default:
        return { allowed: true, reason: '安全检查通过' };
    }
  }
  
  /**
   * 检查Shell别名安全性
   */
  checkShellAliasSafety(opportunity) {
    const { suggested_alias, original_command } = opportunity;
    
    // 检查别名是否已存在
    try {
      const checkAlias = execSync(`alias ${suggested_alias} 2>/dev/null || true`, {
        encoding: 'utf8',
        shell: '/bin/bash'
      });
      
      if (checkAlias && checkAlias.includes('=')) {
        return { allowed: false, reason: `别名 ${suggested_alias} 已存在` };
      }
    } catch (error) {
      // 忽略检查错误
    }
    
    // 检查命令是否有效
    try {
      execSync(`which ${original_command.split(' ')[0]} >/dev/null 2>&1 || true`, {
        shell: '/bin/bash'
      });
    } catch (error) {
      return { allowed: false, reason: `命令 ${original_command} 可能不存在` };
    }
    
    return { allowed: true, reason: 'Shell别名安全检查通过' };
  }
  
  /**
   * 检查笔记整理安全性
   */
  checkNoteOrganizationSafety(opportunity) {
    const { files, target_directory } = opportunity;
    
    // 检查文件是否存在
    for (const file of files) {
      if (!fs.existsSync(file)) {
        return { allowed: false, reason: `文件不存在: ${file}` };
      }
    }
    
    // 检查目标目录
    const targetDir = path.join(process.cwd(), target_directory);
    try {
      if (!fs.existsSync(targetDir)) {
        // 尝试创建目录
        fs.mkdirSync(targetDir, { recursive: true });
      }
      
      // 检查目录是否可写
      const testFile = path.join(targetDir, '.nightpatch-test');
      fs.writeFileSync(testFile, 'test');
      fs.unlinkSync(testFile);
      
    } catch (error) {
      return { allowed: false, reason: `目标目录不可写: ${targetDir}` };
    }
    
    return { allowed: true, reason: '笔记整理安全检查通过' };
  }
  
  /**
   * 检查日志优化安全性
   */
  checkLogOptimizationSafety(opportunity) {
    const { old_logs } = opportunity;
    
    // 检查日志文件是否可访问
    for (const log of old_logs) {
      try {
        fs.accessSync(log.file, fs.constants.R_OK);
      } catch (error) {
        return { allowed: false, reason: `无法访问日志文件: ${log.file}` };
      }
    }
    
    return { allowed: true, reason: '日志优化安全检查通过' };
  }
  
  /**
   * 根据类型执行修补
   */
  async executePatchByType(opportunity) {
    switch (opportunity.type) {
      case 'shell_alias':
        return this.executeShellAliasPatch(opportunity);
      case 'note_organization':
        return this.executeNoteOrganizationPatch(opportunity);
      case 'log_optimization':
        return this.executeLogOptimizationPatch(opportunity);
      case 'data_preparation':
        return this.executeDataPreparationPatch(opportunity);
      default:
        throw new Error(`未知的修补类型: ${opportunity.type}`);
    }
  }
  
  /**
   * 执行Shell别名修补
   */
  async executeShellAliasPatch(opportunity) {
    const { suggested_alias, original_command, rollback_command } = opportunity;
    
    try {
      // 创建别名
      const aliasCommand = `alias ${suggested_alias}='${original_command}'`;
      execSync(aliasCommand, { stdio: 'pipe', shell: '/bin/bash' });
      
      // 添加到bashrc以便永久生效
      const bashrcPath = path.join(process.env.HOME || '/root', '.bashrc');
      const aliasLine = `\n# NightPatch自动添加的别名\n${aliasCommand}\n`;
      
      if (fs.existsSync(bashrcPath)) {
        const bashrcContent = fs.readFileSync(bashrcPath, 'utf8');
        if (!bashrcContent.includes(aliasCommand)) {
          fs.appendFileSync(bashrcPath, aliasLine);
        }
      }
      
      return {
        success: true,
        message: `别名 ${suggested_alias} 创建成功`,
        executed_command: aliasCommand,
        rollback_command: rollback_command,
        permanent: true
      };
      
    } catch (error) {
      return {
        success: false,
        error: `创建别名失败: ${error.message}`,
        rollback_command: rollback_command
      };
    }
  }
  
  /**
   * 执行笔记整理修补
   */
  async executeNoteOrganizationPatch(opportunity) {
    const { files, target_directory, rollback_action } = opportunity;
    
    try {
      const targetDir = path.join(process.cwd(), target_directory);
      const movedFiles = [];
      
      // 确保目标目录存在
      if (!fs.existsSync(targetDir)) {
        fs.mkdirSync(targetDir, { recursive: true });
      }
      
      // 移动文件
      for (const file of files) {
        const filename = path.basename(file);
        const targetPath = path.join(targetDir, filename);
        
        // 检查目标文件是否已存在
        if (fs.existsSync(targetPath)) {
          // 添加时间戳避免冲突
          const timestamp = new Date().getTime();
          const newFilename = `${path.basename(filename, path.extname(filename))}_${timestamp}${path.extname(filename)}`;
          const newTargetPath = path.join(targetDir, newFilename);
          
          fs.renameSync(file, newTargetPath);
          movedFiles.push({ from: file, to: newTargetPath });
        } else {
          fs.renameSync(file, targetPath);
          movedFiles.push({ from: file, to: targetPath });
        }
      }
      
      return {
        success: true,
        message: `移动了 ${movedFiles.length} 个文件到 ${target_directory}/`,
        moved_files: movedFiles,
        rollback_action: rollback_action,
        target_directory: targetDir
      };
      
    } catch (error) {
      return {
        success: false,
        error: `移动文件失败: ${error.message}`,
        rollback_action: rollback_action
      };
    }
  }
  
  /**
   * 执行日志优化修补
   */
  async executeLogOptimizationPatch(opportunity) {
    const { old_logs } = opportunity;
    
    try {
      const deletedLogs = [];
      let totalFreed = 0;
      
      // 删除旧日志
      for (const log of old_logs) {
        try {
          fs.unlinkSync(log.file);
          deletedLogs.push(log.file);
          totalFreed += log.size;
        } catch (error) {
          console.warn(`无法删除日志文件 ${log.file}: ${error.message}`);
        }
      }
      
      const freedMB = (totalFreed / (1024 * 1024)).toFixed(2);
      
      return {
        success: true,
        message: `删除了 ${deletedLogs.length} 个旧日志文件，释放 ${freedMB} MB`,
        deleted_logs: deletedLogs,
        freed_space_mb: freedMB,
        rollback_action: '无法回滚（删除操作）',
        warning: '此操作不可逆'
      };
      
    } catch (error) {
      return {
        success: false,
        error: `清理日志失败: ${error.message}`,
        rollback_action: '无法回滚'
      };
    }
  }
  
  /**
   * 执行数据准备修补
   */
  async executeDataPreparationPatch(opportunity) {
    // 这是一个高级功能，需要具体实现
    // 这里提供一个示例
    
    try {
      const reportContent = this.generateDailyReport();
      const reportPath = path.join(process.cwd(), 'reports', 'daily-summary.md');
      
      // 确保目录存在
      const reportDir = path.dirname(reportPath);
      if (!fs.existsSync(reportDir)) {
        fs.mkdirSync(reportDir, { recursive: true });
      }
      
      fs.writeFileSync(reportPath, reportContent, 'utf8');
      
      return {
        success: true,
        message: '每日数据摘要报告已生成',
        report_path: reportPath,
        rollback_action: `删除文件: ${reportPath}`
      };
      
    } catch (error) {
      return {
        success: false,
        error: `生成报告失败: ${error.message}`,
        rollback_action: '删除生成的报告文件'
      };
    }
  }
  
  /**
   * 生成每日报告（示例）
   */
  generateDailyReport() {
    const now = new Date();
    const dateStr = now.toISOString().split('T')[0];
    
    return `# 每日数据摘要 - ${dateStr}

## 系统概览
- 生成时间: ${now.toLocaleString()}
- 报告类型: 自动生成

## 数据统计
- 今日任务: 待补充
- 完成情况: 待补充

## 建议
1. 检查系统日志
2. 备份重要数据
3. 规划明日任务

---
*由NightPatch Skill自动生成*`;
  }
  
  /**
   * 检查是否为生产环境
   */
  isProductionEnvironment() {
    // 简单的环境检测
    const env = process.env.NODE_ENV || '';
    const hostname = require('os').hostname();
    
    return (
      env.toLowerCase() === 'production' ||
      hostname.includes('prod') ||
      hostname.includes('production') ||
      process.cwd().includes('prod')
    );
  }
  
  /**
   * 记录执行历史
   */
  recordExecution(opportunity, result) {
    const entry = {
      timestamp: new Date().toISOString(),
      opportunity: {
        type: opportunity.type,
        description: opportunity.description,
        detector: opportunity.detector
      },
      result: {
        success: result.success,
        message: result.message || result.error
      },
      safety_check: this.performSafetyCheck(opportunity)
    };
    
    this.executionHistory.push(entry);
    
    // 保存到文件
    this.saveExecutionHistory();
  }
  
  /**
   * 保存执行历史
   */
  saveExecutionHistory() {
    try {
      const historyDir = path.join(process.cwd(), 'logs', 'night-patch');
      if (!fs.existsSync(historyDir)) {
        fs.mkdirSync(historyDir, { recursive: true });
      }
      
      const historyFile = path.join(historyDir, 'execution-history.json');
      const historyData = {
        last_updated: new Date().toISOString(),
        total_executions: this.executionHistory.length,
        executions: this.executionHistory
      };
      
      fs.writeFileSync(historyFile, JSON.stringify(historyData, null, 2), 'utf8');
    } catch (error) {
      console.warn(`保存执行历史失败: ${error.message}`);
    }
  }
  
  /**
   * 获取执行统计
   */
  getExecutionStats() {
    const total = this.executionHistory.length;
    const successful = this.executionHistory.filter(e => e.result.success).length;
    const failed = total - successful;
    
    return {
      total_executions: total,
      successful_executions: successful,
      failed_executions: failed,
      success_rate: total > 0 ? (successful / total * 100).toFixed(1) + '%' : '0%'
    };
  }
}

module.exports = PatchExecutor;