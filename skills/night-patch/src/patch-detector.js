/**
 * 问题检测器模块
 * 负责检测工作流中的可优化点
 */

const fs = require('fs');
const path = require('path');

class PatchDetector {
  constructor(config) {
    this.config = config;
    this.detectors = {
      shell_alias: this.detectShellAlias.bind(this),
      note_organization: this.detectNoteOrganization.bind(this),
      log_optimization: this.detectLogOptimization.bind(this),
      data_preparation: this.detectDataPreparation.bind(this)
    };
  }
  
  /**
   * 运行所有启用的检测器
   */
  async runAllDetectors() {
    console.log('🔍 开始运行问题检测器...\n');
    
    const allOpportunities = [];
    const detectorStats = {};
    
    for (const [detectorName, detectorFunc] of Object.entries(this.detectors)) {
      // 检查检测器是否启用
      const detectorConfig = this.config.detectors?.[detectorName];
      if (!detectorConfig?.enabled) {
        console.log(`➖ ${detectorName}: 检测器已禁用`);
        continue;
      }
      
      try {
        console.log(`🔧 ${detectorName}: 运行检测...`);
        const opportunities = await detectorFunc(detectorConfig);
        
        detectorStats[detectorName] = opportunities.length;
        
        if (opportunities.length > 0) {
          console.log(`✅ ${detectorName}: 检测到 ${opportunities.length} 个机会`);
          allOpportunities.push(...opportunities);
        } else {
          console.log(`➖ ${detectorName}: 未检测到机会`);
        }
      } catch (error) {
        console.error(`❌ ${detectorName}: 检测失败 - ${error.message}`);
      }
    }
    
    // 汇总统计
    console.log('\n' + '='.repeat(50));
    console.log('检测器运行完成');
    console.log('='.repeat(50));
    
    Object.entries(detectorStats).forEach(([name, count]) => {
      console.log(`  ${name}: ${count} 个机会`);
    });
    
    console.log(`\n总计检测到 ${allOpportunities.length} 个优化机会`);
    
    return allOpportunities;
  }
  
  /**
   * 检测Shell别名机会
   */
  async detectShellAlias(config) {
    const opportunities = [];
    
    try {
      // 尝试读取bash历史记录
      const historyPath = config.command_history_file || '~/.bash_history';
      const expandedPath = historyPath.replace('~', process.env.HOME || '/root');
      
      if (fs.existsSync(expandedPath)) {
        const historyContent = fs.readFileSync(expandedPath, 'utf8');
        const commands = historyContent.split('\n').filter(cmd => cmd.trim());
        
        // 分析命令使用频率
        const commandCounts = {};
        commands.forEach(cmd => {
          // 提取基础命令（去掉参数）
          const baseCmd = cmd.split(' ')[0];
          if (baseCmd && baseCmd.length > 2) { // 忽略太短的命令
            commandCounts[baseCmd] = (commandCounts[baseCmd] || 0) + 1;
          }
        });
        
        // 找出高频命令
        Object.entries(commandCounts).forEach(([cmd, count]) => {
          if (count >= (config.min_usage_count || 3)) {
            // 生成建议的别名（取命令的前两个字母）
            const suggestedAlias = cmd.length > 4 ? cmd.substring(0, 2) : cmd;
            
            opportunities.push({
              type: 'shell_alias',
              detector: 'shell_alias',
              description: `创建 ${suggestedAlias} 别名代替 ${cmd}`,
              original_command: cmd,
              suggested_alias: suggestedAlias,
              usage_count: count,
              risk_level: 'low',
              priority: count, // 使用次数越多优先级越高
              rollback_command: `unalias ${suggestedAlias}`,
              metadata: {
                command: cmd,
                alias: suggestedAlias,
                count: count
              }
            });
          }
        });
      } else {
        // 如果历史文件不存在，提供一些常见的建议
        opportunities.push({
          type: 'shell_alias',
          detector: 'shell_alias',
          description: '创建 ll 别名代替 ls -la',
          original_command: 'ls -la',
          suggested_alias: 'll',
          usage_count: 5,
          risk_level: 'low',
          priority: 5,
          rollback_command: 'unalias ll',
          metadata: { note: '基于常见使用模式建议' }
        });
      }
    } catch (error) {
      console.warn(`Shell别名检测失败: ${error.message}`);
      // 返回一个示例机会用于测试
      opportunities.push({
        type: 'shell_alias',
        detector: 'shell_alias',
        description: '创建 ll 别名代替 ls -la (示例)',
        original_command: 'ls -la',
        suggested_alias: 'll',
        usage_count: 3,
        risk_level: 'low',
        priority: 3,
        rollback_command: 'unalias ll',
        metadata: { note: '示例机会，实际检测失败' }
      });
    }
    
    return opportunities;
  }
  
  /**
   * 检测笔记整理机会
   */
  async detectNoteOrganization(config) {
    const opportunities = [];
    
    try {
      const targetDirs = config.target_directories || ['notes', 'docs', 'memories'];
      const extensions = config.file_extensions || ['.md', '.txt', '.json'];
      const maxScattered = config.max_scattered_files || 5;
      
      // 扫描当前工作目录
      const workspaceDir = process.cwd();
      const allFiles = this.scanDirectory(workspaceDir, extensions, 3); // 最大深度3层
      
      // 按目录统计文件
      const dirStats = {};
      allFiles.forEach(file => {
        const dir = path.dirname(file);
        dirStats[dir] = (dirStats[dir] || 0) + 1;
      });
      
      // 找出散落的文件
      const scatteredFiles = [];
      Object.entries(dirStats).forEach(([dir, count]) => {
        // 如果目录不在目标目录中，且文件数较少，可能是散落的
        const isTargetDir = targetDirs.some(target => dir.includes(target));
        if (!isTargetDir && count <= maxScattered) {
          // 获取该目录下的文件
          const filesInDir = allFiles.filter(file => path.dirname(file) === dir);
          scatteredFiles.push(...filesInDir);
        }
      });
      
      if (scatteredFiles.length > 0) {
        // 分组处理
        const fileGroups = {};
        scatteredFiles.forEach(file => {
          const ext = path.extname(file);
          if (!fileGroups[ext]) fileGroups[ext] = [];
          fileGroups[ext].push(file);
        });
        
        // 为每组文件创建机会
        Object.entries(fileGroups).forEach(([ext, files]) => {
          if (files.length >= 2) { // 至少2个文件才建议整理
            const targetDir = targetDirs.find(dir => 
              dir.includes(ext.replace('.', '')) || dir === 'notes'
            ) || 'notes';
            
            opportunities.push({
              type: 'note_organization',
              detector: 'note_organization',
              description: `整理 ${files.length} 个${ext}文件到 ${targetDir}/ 目录`,
              files: files,
              target_directory: targetDir,
              risk_level: 'low',
              priority: files.length, // 文件越多优先级越高
              rollback_action: `将文件从 ${targetDir}/ 移回原位置`,
              metadata: {
                file_count: files.length,
                extension: ext,
                target_dir: targetDir
              }
            });
          }
        });
      }
    } catch (error) {
      console.warn(`笔记整理检测失败: ${error.message}`);
    }
    
    return opportunities;
  }
  
  /**
   * 检测日志优化机会
   */
  async detectLogOptimization(config) {
    const opportunities = [];
    
    try {
      const logDirs = config.log_directories || ['logs', 'var/log'];
      const maxAgeDays = config.max_log_age_days || 7;
      
      const now = Date.now();
      const maxAgeMs = maxAgeDays * 24 * 60 * 60 * 1000;
      
      // 扫描日志目录
      let oldLogs = [];
      logDirs.forEach(logDir => {
        const fullPath = path.join(process.cwd(), logDir);
        if (fs.existsSync(fullPath) && fs.statSync(fullPath).isDirectory()) {
          const logs = this.scanDirectory(fullPath, ['.log', '.txt'], 2);
          
          logs.forEach(logFile => {
            try {
              const stats = fs.statSync(logFile);
              const ageMs = now - stats.mtimeMs;
              
              if (ageMs > maxAgeMs) {
                oldLogs.push({
                  file: logFile,
                  ageDays: Math.floor(ageMs / (24 * 60 * 60 * 1000)),
                  size: stats.size
                });
              }
            } catch (e) {
              // 忽略无法访问的文件
            }
          });
        }
      });
      
      if (oldLogs.length > 0) {
        const totalSize = oldLogs.reduce((sum, log) => sum + log.size, 0);
        const sizeMB = (totalSize / (1024 * 1024)).toFixed(2);
        
        opportunities.push({
          type: 'log_optimization',
          detector: 'log_optimization',
          description: `清理 ${oldLogs.length} 个旧日志文件 (${sizeMB} MB)`,
          old_logs: oldLogs,
          max_age_days: maxAgeDays,
          risk_level: 'low',
          priority: oldLogs.length,
          rollback_action: '无法回滚（删除操作）',
          metadata: {
            log_count: oldLogs.length,
            total_size_mb: sizeMB,
            max_age_days: maxAgeDays
          }
        });
      }
    } catch (error) {
      console.warn(`日志优化检测失败: ${error.message}`);
    }
    
    return opportunities;
  }
  
  /**
   * 检测数据准备机会
   */
  async detectDataPreparation(config) {
    const opportunities = [];
    
    // 这是一个高级功能，需要具体的数据源配置
    // 这里提供一个示例实现
    
    opportunities.push({
      type: 'data_preparation',
      detector: 'data_preparation',
      description: '准备每日数据摘要报告',
      data_sources: ['system_metrics', 'task_logs'],
      risk_level: 'medium',
      priority: 2,
      rollback_action: '删除生成的报告文件',
      metadata: {
        note: '示例数据准备任务',
        suggested_time: 'before_09:00'
      }
    });
    
    return opportunities;
  }
  
  /**
   * 扫描目录中的特定类型文件
   */
  scanDirectory(dir, extensions, maxDepth, currentDepth = 0) {
    if (currentDepth > maxDepth) return [];
    
    const files = [];
    
    try {
      const items = fs.readdirSync(dir);
      
      items.forEach(item => {
        const fullPath = path.join(dir, item);
        
        try {
          const stats = fs.statSync(fullPath);
          
          if (stats.isDirectory()) {
            // 递归扫描子目录
            const subFiles = this.scanDirectory(fullPath, extensions, maxDepth, currentDepth + 1);
            files.push(...subFiles);
          } else if (stats.isFile()) {
            // 检查文件扩展名
            const ext = path.extname(item).toLowerCase();
            if (extensions.includes(ext)) {
              files.push(fullPath);
            }
          }
        } catch (e) {
          // 忽略无法访问的项目
        }
      });
    } catch (error) {
      // 忽略无法访问的目录
    }
    
    return files;
  }
  
  /**
   * 评估机会的优先级
   */
  evaluateOpportunityPriority(opportunity) {
    let priority = opportunity.priority || 0;
    
    // 根据类型调整优先级
    switch (opportunity.type) {
      case 'shell_alias':
        priority *= 1.5; // Shell别名优先级较高
        break;
      case 'note_organization':
        priority *= 1.2;
        break;
      case 'log_optimization':
        priority *= 1.0;
        break;
      case 'data_preparation':
        priority *= 0.8; // 数据准备优先级较低（风险较高）
        break;
    }
    
    // 根据风险级别调整
    switch (opportunity.risk_level) {
      case 'low':
        priority *= 1.5;
        break;
      case 'medium':
        priority *= 1.0;
        break;
      case 'high':
        priority *= 0.5;
        break;
    }
    
    return Math.round(priority);
  }
  
  /**
   * 排序机会列表
   */
  sortOpportunities(opportunities) {
    return opportunities
      .map(opp => ({
        ...opp,
        calculated_priority: this.evaluateOpportunityPriority(opp)
      }))
      .sort((a, b) => b.calculated_priority - a.calculated_priority);
  }
}

module.exports = PatchDetector;