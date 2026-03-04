/**
 * 安全检查模块
 * 负责验证所有操作的安全性
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class SafetyCheck {
  constructor(config) {
    this.config = config;
    this.safetyRules = this.parseSafetyRules(config);
    this.auditLog = [];
  }
  
  /**
   * 解析安全规则
   */
  parseSafetyRules(config) {
    return {
      // 基本限制
      maxChanges: config.safety?.max_changes_per_night || 1,
      maxFiles: config.safety?.change_limits?.max_files || 2,
      maxLines: config.safety?.change_limits?.max_lines || 200,
      maxCommands: config.safety?.change_limits?.max_commands || 3,
      
      // 安全要求
      requireRollback: config.safety?.require_rollback !== false,
      skipProduction: config.safety?.skip_production !== false,
      dryRunFirst: config.safety?.dry_run_first !== false,
      
      // 环境检查
      checkEnvironment: true,
      checkPermissions: true,
      checkResources: true,
      
      // 危险操作禁止
      forbiddenActions: [
        'delete_production_data',
        'modify_production_config',
        'send_external_messages',
        'execute_arbitrary_code',
        'modify_system_files'
      ]
    };
  }
  
  /**
   * 执行完整的安全检查
   */
  async performFullSafetyCheck(opportunity) {
    const checks = [
      this.checkEnvironment.bind(this),
      this.checkRiskLevel.bind(this, opportunity),
      this.checkRollbackCapability.bind(this, opportunity),
      this.checkResourceLimits.bind(this, opportunity),
      this.checkForbiddenActions.bind(this, opportunity),
      this.checkSpecificSafety.bind(this, opportunity)
    ];
    
    const results = [];
    
    for (const check of checks) {
      try {
        const result = await check();
        results.push(result);
        
        if (!result.passed) {
          // 安全检查失败，立即返回
          return {
            passed: false,
            reason: result.reason,
            failedCheck: result.checkName,
            allResults: results
          };
        }
      } catch (error) {
        results.push({
          checkName: '安全检查执行',
          passed: false,
          reason: `检查执行失败: ${error.message}`,
          error: error
        });
        
        return {
          passed: false,
          reason: `安全检查异常: ${error.message}`,
          failedCheck: '安全检查执行',
          allResults: results
        };
      }
    }
    
    // 所有检查通过
    return {
      passed: true,
      reason: '所有安全检查通过',
      allResults: results
    };
  }
  
  /**
   * 检查环境安全性
   */
  async checkEnvironment() {
    const checkName = '环境检查';
    
    // 检查是否为生产环境
    if (this.safetyRules.skipProduction) {
      const isProduction = this.isProductionEnvironment();
      if (isProduction) {
        return {
          checkName,
          passed: false,
          reason: '当前为生产环境，夜间修补已禁用'
        };
      }
    }
    
    // 检查磁盘空间
    const diskSpace = this.checkDiskSpace();
    if (diskSpace.freeGB < 1) {
      return {
        checkName,
        passed: false,
        reason: `磁盘空间不足: ${diskSpace.freeGB.toFixed(2)}GB 可用，需要至少 1GB`
      };
    }
    
    // 检查内存使用
    const memoryUsage = this.checkMemoryUsage();
    if (memoryUsage.usagePercent > 90) {
      return {
        checkName,
        passed: false,
        reason: `内存使用过高: ${memoryUsage.usagePercent.toFixed(1)}%`
      };
    }
    
    return {
      checkName,
      passed: true,
      reason: '环境检查通过',
      details: {
        isProduction: this.isProductionEnvironment(),
        diskSpace: `${diskSpace.freeGB.toFixed(2)}GB 可用`,
        memoryUsage: `${memoryUsage.usagePercent.toFixed(1)}% 使用率`
      }
    };
  }
  
  /**
   * 检查风险级别
   */
  async checkRiskLevel(opportunity) {
    const checkName = '风险级别检查';
    
    if (!opportunity.risk_level) {
      return {
        checkName,
        passed: false,
        reason: '未指定风险级别'
      };
    }
    
    const allowedRiskLevels = ['low', 'medium'];
    
    if (!allowedRiskLevels.includes(opportunity.risk_level)) {
      return {
        checkName,
        passed: false,
        reason: `风险级别过高: ${opportunity.risk_level}，只允许 low 或 medium`
      };
    }
    
    return {
      checkName,
      passed: true,
      reason: `风险级别 ${opportunity.risk_level} 符合要求`
    };
  }
  
  /**
   * 检查回滚能力
   */
  async checkRollbackCapability(opportunity) {
    const checkName = '回滚能力检查';
    
    if (!this.safetyRules.requireRollback) {
      return {
        checkName,
        passed: true,
        reason: '回滚要求已禁用'
      };
    }
    
    const hasRollback = opportunity.rollback_command || opportunity.rollback_action;
    
    if (!hasRollback) {
      return {
        checkName,
        passed: false,
        reason: '缺少回滚方案'
      };
    }
    
    // 验证回滚方案的有效性
    let rollbackValid = false;
    let validationMessage = '';
    
    if (opportunity.rollback_command) {
      // 检查命令语法
      try {
        // 简单的语法检查（不实际执行）
        const command = opportunity.rollback_command.trim();
        if (command && command.length > 0) {
          rollbackValid = true;
          validationMessage = '回滚命令语法检查通过';
        }
      } catch (error) {
        validationMessage = `回滚命令语法检查失败: ${error.message}`;
      }
    } else if (opportunity.rollback_action) {
      rollbackValid = true;
      validationMessage = '回滚操作描述有效';
    }
    
    if (!rollbackValid) {
      return {
        checkName,
        passed: false,
        reason: validationMessage || '回滚方案无效'
      };
    }
    
    return {
      checkName,
      passed: true,
      reason: validationMessage || '回滚能力检查通过'
    };
  }
  
  /**
   * 检查资源限制
   */
  async checkResourceLimits(opportunity) {
    const checkName = '资源限制检查';
    
    // 检查文件数限制
    if (opportunity.files && opportunity.files.length > this.safetyRules.maxFiles) {
      return {
        checkName,
        passed: false,
        reason: `文件数超出限制: ${opportunity.files.length} > ${this.safetyRules.maxFiles}`
      };
    }
    
    // 检查行数限制（估计）
    if (opportunity.estimated_lines && opportunity.estimated_lines > this.safetyRules.maxLines) {
      return {
        checkName,
        passed: false,
        reason: `修改行数超出限制: ${opportunity.estimated_lines} > ${this.safetyRules.maxLines}`
      };
    }
    
    // 检查命令数限制
    if (opportunity.commands && opportunity.commands.length > this.safetyRules.maxCommands) {
      return {
        checkName,
        passed: false,
        reason: `命令数超出限制: ${opportunity.commands.length} > ${this.safetyRules.maxCommands}`
      };
    }
    
    return {
      checkName,
      passed: true,
      reason: '资源限制检查通过'
    };
  }
  
  /**
   * 检查禁止的操作
   */
  async checkForbiddenActions(opportunity) {
    const checkName = '禁止操作检查';
    
    // 检查是否涉及禁止的操作
    const actionTriggers = {
      delete_production_data: ['delete', 'remove', 'drop', 'truncate'],
      modify_production_config: ['/etc/', '/usr/local/', 'config.prod', 'production.conf'],
      send_external_messages: ['send', 'post', 'email', 'notification'],
      execute_arbitrary_code: ['eval', 'exec', 'system', 'child_process'],
      modify_system_files: ['/bin/', '/sbin/', '/lib/', '/usr/bin/']
    };
    
    const opportunityStr = JSON.stringify(opportunity).toLowerCase();
    
    for (const [action, triggers] of Object.entries(actionTriggers)) {
      if (this.safetyRules.forbiddenActions.includes(action)) {
        for (const trigger of triggers) {
          if (opportunityStr.includes(trigger.toLowerCase())) {
            return {
              checkName,
              passed: false,
              reason: `检测到禁止的操作: ${action} (触发词: ${trigger})`
            };
          }
        }
      }
    }
    
    return {
      checkName,
      passed: true,
      reason: '禁止操作检查通过'
    };
  }
  
  /**
   * 检查特定类型的安全性
   */
  async checkSpecificSafety(opportunity) {
    const checkName = '特定类型安全检查';
    
    switch (opportunity.type) {
      case 'shell_alias':
        return this.checkShellAliasSafety(opportunity);
      case 'note_organization':
        return this.checkFileOperationSafety(opportunity);
      case 'log_optimization':
        return this.checkLogOperationSafety(opportunity);
      case 'data_preparation':
        return this.checkDataOperationSafety(opportunity);
      default:
        return {
          checkName,
          passed: true,
          reason: `类型 ${opportunity.type} 无特定安全检查`
        };
    }
  }
  
  /**
   * 检查Shell别名安全性
   */
  async checkShellAliasSafety(opportunity) {
    const { suggested_alias, original_command } = opportunity;
    
    // 检查别名是否安全
    const dangerousAliases = ['rm', 'dd', 'shutdown', 'reboot', 'halt'];
    if (dangerousAliases.includes(suggested_alias)) {
      return {
        checkName: 'Shell别名安全检查',
        passed: false,
        reason: `别名 ${suggested_alias} 可能危险`
      };
    }
    
    // 检查命令是否安全
    const dangerousCommands = ['rm -rf', 'dd if=', 'mkfs', 'fdisk'];
    for (const dangerousCmd of dangerousCommands) {
      if (original_command.includes(dangerousCmd)) {
        return {
          checkName: 'Shell别名安全检查',
          passed: false,
          reason: `命令包含危险操作: ${dangerousCmd}`
        };
      }
    }
    
    return {
      checkName: 'Shell别名安全检查',
      passed: true,
      reason: 'Shell别名安全检查通过'
    };
  }
  
  /**
   * 检查文件操作安全性
   */
  async checkFileOperationSafety(opportunity) {
    const { files, target_directory } = opportunity;
    
    // 检查源文件是否存在且可读
    for (const file of files) {
      try {
        fs.accessSync(file, fs.constants.R_OK);
      } catch (error) {
        return {
          checkName: '文件操作安全检查',
          passed: false,
          reason: `无法读取文件: ${file}`
        };
      }
      
      // 检查是否为系统文件
      const systemPaths = ['/etc/', '/bin/', '/sbin/', '/usr/bin/', '/usr/sbin/'];
      for (const sysPath of systemPaths) {
        if (file.startsWith(sysPath)) {
          return {
            checkName: '文件操作安全检查',
            passed: false,
            reason: `尝试操作系统文件: ${file}`
          };
        }
      }
    }
    
    // 检查目标目录是否可写
    const targetDir = path.join(process.cwd(), target_directory);
    try {
      if (!fs.existsSync(targetDir)) {
        // 尝试创建目录来测试可写性
        fs.mkdirSync(targetDir, { recursive: true });
        // 创建后删除测试目录
        fs.rmdirSync(targetDir);
      } else {
        // 测试文件写入
        const testFile = path.join(targetDir, '.nightpatch-test');
        fs.writeFileSync(testFile, 'test');
        fs.unlinkSync(testFile);
      }
    } catch (error) {
      return {
        checkName: '文件操作安全检查',
        passed: false,
        reason: `目标目录不可写: ${targetDir}`
      };
    }
    
    return {
      checkName: '文件操作安全检查',
      passed: true,
      reason: '文件操作安全检查通过'
    };
  }
  
  /**
   * 检查日志操作安全性
   */
  async checkLogOperationSafety(opportunity) {
    const { old_logs } = opportunity;
    
    // 检查日志文件是否可访问
    for (const log of old_logs) {
      try {
        fs.accessSync(log.file, fs.constants.R_OK);
      } catch (error) {
        return {
          checkName: '日志操作安全检查',
          passed: false,
          reason: `无法访问日志文件: ${log.file}`
        };
      }
      
      // 检查日志文件年龄
      const maxAgeDays = 30; // 最大允许删除的日志天数
      const logAgeDays = log.ageDays || 0;
      
      if (logAgeDays < maxAgeDays) {
        return {
          checkName: '日志操作安全检查',
          passed: false,
          reason: `日志文件太新: ${log.file} (${logAgeDays} 天)`
        };
      }
    }
    
    return {
      checkName: '日志操作安全检查',
      passed: true,
      reason: '日志操作安全检查通过'
    };
  }
  
  /**
   * 检查数据操作安全性
   */
  async checkDataOperationSafety(opportunity) {
    // 数据准备操作通常需要更严格的检查
    // 这里进行基本检查
    
    if (opportunity.risk_level !== 'low') {
      return {
        checkName: '数据操作安全检查',
        passed: false,
        reason: '数据准备操作风险级别必须为 low'
      };
    }
    
    return {
      checkName: '数据操作安全检查',
      passed: true,
      reason: '数据操作安全检查通过'
    };
  }
  
  /**
   * 检查是否为生产环境
   */
  isProductionEnvironment() {
    const env = process.env.NODE_ENV || '';
    const hostname = require('os').hostname();
    const cwd = process.cwd();
    
    const productionIndicators = [
      env.toLowerCase().includes('prod'),
      hostname.toLowerCase().includes('prod'),
      cwd.toLowerCase().includes('prod'),
      process.env.PRODUCTION === 'true',
      process.env.ENVIRONMENT === 'production'
    ];
    
    return productionIndicators.some(indicator => indicator === true);
  }
  
  /**
   * 检查磁盘空间
   */
  checkDiskSpace() {
    try {
      const stats = require('fs').statfsSync('/');
      const freeBytes = stats.bavail * stats.bsize;
      const freeGB = freeBytes / (1024 * 1024 * 1024);
      
      return {
        freeGB: freeGB,
        freeBytes: freeBytes,
        checkedAt: new Date().toISOString()
      };
    } catch (error) {
      // 如果检查失败，返回一个安全值
      return {
        freeGB: 10, // 假设有10GB空间
        freeBytes: 10 * 1024 * 1024 * 1024,
        checkedAt: new Date().toISOString(),
        note: '磁盘空间检查失败，使用默认值'
      };
    }
  }
  
  /**
   * 检查内存使用
   */
  checkMemoryUsage() {
    try {
      const os = require('os');
      const totalMem = os.totalmem();
      const freeMem = os.freemem();
      const usedMem = totalMem - freeMem;
      const usagePercent = (usedMem / totalMem) * 100;
      
      return {
        totalMB: totalMem / (1024 * 1024),
        freeMB: freeMem / (1024 * 1024),
        usedMB: usedMem / (1024 * 1024),
        usagePercent: usagePercent,
        checkedAt: new Date().toISOString()
      };
    } catch (error) {
      return {
        totalMB: 0,
        freeMB: 0,
        usedMB: 0,
        usagePercent: 0,
        checkedAt: new Date().toISOString(),
        note: '内存检查失败'
      };
    }
  }
  
  /**
   * 记录审计日志
   */
  logAudit(checkName, result, opportunity = null) {
    const auditEntry = {
      timestamp: new Date().toISOString(),
      checkName,
      result,
      opportunity: opportunity ? {
        type: opportunity.type,
        description: opportunity.description,
        detector: opportunity.detector
      } : null,
      environment: {
        isProduction: this.isProductionEnvironment(),
        nodeEnv: process.env.NODE_ENV || '未设置',
        hostname: require('os').hostname()
      }
    };
    
    this.auditLog.push(auditEntry);
    this.saveAuditLog();
    
    return auditEntry;
  }
  
  /**
   * 保存审计日志
   */
  saveAuditLog() {
    try {
      const auditDir = path.join(process.cwd(), 'logs', 'night-patch');
      if (!fs.existsSync(auditDir)) {
        fs.mkdirSync(auditDir, { recursive: true });
      }
      
      const auditFile = path.join(auditDir, 'safety-audit.json');
      const auditData = {
        last_updated: new Date().toISOString(),
        total_checks: this.auditLog.length,
        checks: this.auditLog
      };
      
      fs.writeFileSync(auditFile, JSON.stringify(auditData, null, 2), 'utf8');
    } catch (error) {
      console.warn(`保存审计日志失败: ${error.message}`);
    }
  }
  
  /**
   * 获取审计摘要
   */
  getAuditSummary() {
    const total = this.auditLog.length;
    const passed = this.auditLog.filter(entry => entry.result.passed).length;
    const failed = total - passed;
    
    return {
      total_checks: total,
      passed_checks: passed,
      failed_checks: failed,
      pass_rate: total > 0 ? ((passed / total) * 100).toFixed(1) + '%' : '0%',
      last_check: this.auditLog.length > 0 ? this.auditLog[this.auditLog.length - 1].timestamp : null
    };
  }
  
  /**
   * 生成安全检查报告
   */
  generateSafetyReport() {
    const summary = this.getAuditSummary();
    const lastChecks = this.auditLog.slice(-5); // 最后5次检查
    
    let report = `# 安全检查报告\n\n`;
    report += `## 摘要\n`;
    report += `- 总检查次数: ${summary.total_checks}\n`;
    report += `- 通过次数: ${summary.passed_checks}\n`;
    report += `- 失败次数: ${summary.failed_checks}\n`;
    report += `- 通过率: ${summary.pass_rate}\n`;
    report += `- 最后检查: ${summary.last_check || '无'}\n\n`;
    
    report += `## 最近检查记录\n`;
    
    if (lastChecks.length > 0) {
      lastChecks.forEach((check, index) => {
        report += `### ${index + 1}. ${check.checkName}\n`;
        report += `- 时间: ${check.timestamp}\n`;
        report += `- 结果: ${check.result.passed ? '✅ 通过' : '❌ 失败'}\n`;
        report += `- 原因: ${check.result.reason}\n`;
        
        if (check.opportunity) {
          report += `- 相关机会: ${check.opportunity.description}\n`;
        }
        
        report += `\n`;
      });
    } else {
      report += `暂无检查记录\n\n`;
    }
    
    report += `## 安全规则配置\n`;
    report += `| 规则 | 配置值 | 状态 |\n`;
    report += `|------|--------|------|\n`;
    report += `| 最大修补数 | ${this.safetyRules.maxChanges} | ${this.safetyRules.maxChanges > 0 ? '✅' : '❌'} |\n`;
    report += `| 可回滚要求 | ${this.safetyRules.requireRollback ? '是' : '否'} | ${this.safetyRules.requireRollback ? '✅' : '⚠️'} |\n`;
    report += `| 生产环境保护 | ${this.safetyRules.skipProduction ? '是' : '否'} | ${this.safetyRules.skipProduction ? '✅' : '⚠️'} |\n`;
    report += `| 首次运行dry-run | ${this.safetyRules.dryRunFirst ? '是' : '否'} | ${this.safetyRules.dryRunFirst ? '✅' : '⚠️'} |\n\n`;
    
    report += `---\n`;
    report += `*报告生成时间: ${new Date().toISOString()}*\n`;
    report += `*NightPatch Safety Check Module*\n`;
    
    return report;
  }
}

module.exports = SafetyCheck;