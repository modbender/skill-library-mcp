#!/usr/bin/env node
/**
 * OpenClaw Security Audit Tool
 * 覆盖报告中 SYS-001~007, ECO-001~051, OC-001~011 漏洞检测
 *
 * 用法:
 *   node security-audit.js                          # 运行全部检测
 *   node security-audit.js --module env,auth,ioc    # 运行指定模块
 *   node security-audit.js --format json            # JSON 输出
 *   node security-audit.js --output report.json     # 保存到文件
 */

'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');
const { execSync } = require('child_process');

// ─────────────────────────────────────────────
// 0. 通用工具与常量
// ─────────────────────────────────────────────

const SEVERITY = { CRITICAL: 'CRITICAL', HIGH: 'HIGH', MEDIUM: 'MEDIUM', LOW: 'LOW', PASS: 'PASS' };
const SEVERITY_ICON = {
  CRITICAL: '🔴', HIGH: '🟠', MEDIUM: '🟡', LOW: '🔵', PASS: '🟢',
};

const HOME = os.homedir();
const CLAWDBOT_DIR = path.join(HOME, '.clawdbot');
const OPENCLAW_DIR = path.join(HOME, '.openclaw');

// 尝试定位 OpenClaw 配置目录
function getConfigDir() {
  if (fs.existsSync(CLAWDBOT_DIR)) return CLAWDBOT_DIR;
  if (fs.existsSync(OPENCLAW_DIR)) return OPENCLAW_DIR;
  return null;
}

// 安全读取 JSON 文件
function safeReadJson(filePath) {
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  } catch {
    return null;
  }
}

// 安全读取文本文件
function safeReadText(filePath) {
  try {
    return fs.readFileSync(filePath, 'utf-8');
  } catch {
    return null;
  }
}

// 递归查找文件
function findFiles(dir, pattern, maxDepth = 5, depth = 0) {
  const results = [];
  if (depth > maxDepth || !fs.existsSync(dir)) return results;
  try {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory() && !entry.name.startsWith('.') && entry.name !== 'node_modules') {
        results.push(...findFiles(fullPath, pattern, maxDepth, depth + 1));
      } else if (entry.isFile() && pattern.test(entry.name)) {
        results.push(fullPath);
      }
    }
  } catch { /* 权限不足等 */ }
  return results;
}

// 静默执行命令
function safeExec(cmd, timeout = 5000) {
  try {
    return execSync(cmd, { timeout, encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] }).trim();
  } catch {
    return null;
  }
}

class AuditReport {
  constructor() {
    this.findings = [];
    this.startTime = new Date();
  }

  add(module, vulnId, title, severity, description, details = null, remediation = null) {
    this.findings.push({
      module, vulnId, title, severity, description,
      details: details || undefined,
      remediation: remediation || undefined,
      timestamp: new Date().toISOString(),
    });
  }

  getSummary() {
    const counts = { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0, PASS: 0 };
    for (const f of this.findings) counts[f.severity] = (counts[f.severity] || 0) + 1;
    return counts;
  }

  printConsole() {
    const elapsed = ((Date.now() - this.startTime.getTime()) / 1000).toFixed(2);
    const summary = this.getSummary();

    console.log('\n' + '═'.repeat(70));
    console.log('  OpenClaw Security Audit Report');
    console.log('  ' + new Date().toISOString());
    console.log('═'.repeat(70));

    // 按严重级别排序输出
    const order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'PASS'];
    for (const sev of order) {
      const items = this.findings.filter(f => f.severity === sev);
      if (items.length === 0) continue;
      console.log(`\n${SEVERITY_ICON[sev]}  ${sev} (${items.length} 项)`);
      console.log('─'.repeat(60));
      for (const item of items) {
        console.log(`  [${item.vulnId}] ${item.title}`);
        console.log(`    模块: ${item.module}`);
        console.log(`    描述: ${item.description}`);
        if (item.details) {
          const detailStr = typeof item.details === 'string' ? item.details : JSON.stringify(item.details, null, 2);
          for (const line of detailStr.split('\n').slice(0, 10)) {
            console.log(`    详情: ${line}`);
          }
        }
        if (item.remediation) {
          console.log(`    修复: ${item.remediation}`);
        }
        console.log('');
      }
    }

    console.log('═'.repeat(70));
    console.log('  审计汇总');
    console.log('─'.repeat(70));
    console.log(`  🔴 严重: ${summary.CRITICAL}  🟠 高危: ${summary.HIGH}  🟡 中危: ${summary.MEDIUM}  🔵 低危: ${summary.LOW}  🟢 通过: ${summary.PASS}`);
    console.log(`  总计: ${this.findings.length} 项检测  耗时: ${elapsed}s`);

    const riskLevel = summary.CRITICAL > 0 ? '🔴 严重 — 不适合生产环境'
      : summary.HIGH > 0 ? '🟠 高危 — 需尽快修复'
      : summary.MEDIUM > 0 ? '🟡 中危 — 建议修复'
      : '🟢 安全 — 配置良好';
    console.log(`  综合评级: ${riskLevel}`);
    console.log('═'.repeat(70) + '\n');
  }

  toJson() {
    return {
      reportVersion: '1.0.0',
      generatedAt: new Date().toISOString(),
      platform: { os: os.platform(), arch: os.arch(), nodeVersion: process.version },
      summary: this.getSummary(),
      findings: this.findings,
    };
  }
}

// ─────────────────────────────────────────────
// 1. 环境变量泄露检测 (SYS-002, OC-008)
// ─────────────────────────────────────────────
function auditEnvVars(report) {
  const MODULE = 'env-exposure';

  const SENSITIVE_PATTERNS = [
    { pattern: /API_KEY$/i, label: 'API Key' },
    { pattern: /^ANTHROPIC_/i, label: 'Anthropic 凭据' },
    { pattern: /^OPENAI_/i, label: 'OpenAI 凭据' },
    { pattern: /SECRET/i, label: '密钥/Secret' },
    { pattern: /TOKEN$/i, label: 'Token' },
    { pattern: /PASSWORD/i, label: '密码' },
    { pattern: /CREDENTIAL/i, label: '凭据' },
    { pattern: /^AWS_/i, label: 'AWS 凭据' },
    { pattern: /^TELEGRAM_/i, label: 'Telegram 凭据' },
    { pattern: /^SLACK_/i, label: 'Slack 凭据' },
    { pattern: /^DISCORD_/i, label: 'Discord 凭据' },
    { pattern: /PRIVATE_KEY/i, label: '私钥' },
    { pattern: /^DATABASE_/i, label: '数据库凭据' },
    { pattern: /^REDIS_/i, label: 'Redis 凭据' },
    { pattern: /^MONGO/i, label: 'MongoDB 凭据' },
    { pattern: /^GITHUB_TOKEN/i, label: 'GitHub Token' },
  ];

  const exposed = [];
  for (const [key] of Object.entries(process.env)) {
    for (const { pattern, label } of SENSITIVE_PATTERNS) {
      if (pattern.test(key)) {
        exposed.push({ key, label, masked: `${key}=${process.env[key]?.substring(0, 4)}****` });
        break;
      }
    }
  }

  if (exposed.length > 0) {
    report.add(MODULE, 'SYS-002 / OC-008', '敏感环境变量暴露',
      SEVERITY.CRITICAL,
      `检测到 ${exposed.length} 个敏感环境变量可被任意 Skill 通过 process.env 读取`,
      exposed.map(e => `${e.label}: ${e.masked}`).join('\n'),
      '使用环境变量过滤器，在 Skill 执行环境中移除敏感变量；参考报告 11.3.4 节'
    );
  } else {
    report.add(MODULE, 'SYS-002 / OC-008', '环境变量检查',
      SEVERITY.PASS, '未检测到已知敏感环境变量暴露');
  }

  // 检查 process.env 是否可被完全枚举 (SYS-001 进程隔离)
  const totalEnvVars = Object.keys(process.env).length;
  if (totalEnvVars > 0) {
    report.add(MODULE, 'SYS-001', '进程隔离验证 — 环境变量枚举',
      totalEnvVars > 50 ? SEVERITY.HIGH : SEVERITY.MEDIUM,
      `当前进程可枚举 ${totalEnvVars} 个环境变量，说明缺乏进程级隔离`,
      null,
      '部署 bwrap/Docker 沙箱隔离 Skill 执行环境，使用 --unsetenv 清除敏感变量'
    );
  }
}

// ─────────────────────────────────────────────
// 2. 凭据存储安全检测 (SYS-005, ECO-012)
// ─────────────────────────────────────────────
function auditCredentialStorage(report) {
  const MODULE = 'credential-storage';
  const configDir = getConfigDir();

  if (!configDir) {
    report.add(MODULE, 'SYS-005', 'OpenClaw 配置目录',
      SEVERITY.LOW, `未找到 OpenClaw 配置目录 (~/.clawdbot 或 ~/.openclaw)，可能未安装或路径不同`);
    return;
  }

  // 检查 auth-profiles.json 明文凭据
  const authFile = path.join(configDir, 'auth-profiles.json');
  if (fs.existsSync(authFile)) {
    const stat = fs.statSync(authFile);
    const perms = '0' + (stat.mode & parseInt('777', 8)).toString(8);
    const content = safeReadText(authFile);

    const issues = [];
    if (content) {
      // 检查是否包含明文 Token/Key
      const sensitiveMatch = content.match(/(sk-[a-zA-Z0-9]{20,}|xoxb-|xoxp-|ghp_|gho_|bot[0-9]+:AA)/g);
      if (sensitiveMatch) {
        issues.push(`发现 ${sensitiveMatch.length} 个疑似明文凭据/Token`);
      }
    }

    // 检查文件权限
    if (perms !== '0600' && perms !== '0400') {
      issues.push(`文件权限过宽: ${perms} (建议 0600)`);
    }

    if (issues.length > 0) {
      report.add(MODULE, 'SYS-005 / ECO-012', 'auth-profiles.json 明文凭据存储',
        SEVERITY.CRITICAL,
        `凭据文件存在安全问题: ${authFile}`,
        issues.join('\n'),
        'OAuth Token 应加密存储，文件权限设为 600；参考报告 11.4.3 节'
      );
    } else {
      report.add(MODULE, 'SYS-005', 'auth-profiles.json 检查',
        SEVERITY.PASS, '凭据文件权限和内容检查通过');
    }
  }

  // 检查主配置文件中是否有硬编码凭据
  for (const cfgName of ['clawdbot.json', 'openclaw.json', 'config.json']) {
    const cfgPath = path.join(configDir, cfgName);
    const content = safeReadText(cfgPath);
    if (!content) continue;

    const keyPatterns = [
      /["']?api[_-]?key["']?\s*[:=]\s*["'][^"']{10,}["']/gi,
      /["']?secret["']?\s*[:=]\s*["'][^"']{10,}["']/gi,
      /["']?token["']?\s*[:=]\s*["'][^"']{10,}["']/gi,
      /["']?password["']?\s*[:=]\s*["'][^"']{4,}["']/gi,
    ];

    const found = [];
    for (const p of keyPatterns) {
      const matches = content.match(p);
      if (matches) found.push(...matches.map(m => m.substring(0, 40) + '...'));
    }

    if (found.length > 0) {
      report.add(MODULE, 'ECO-012', `配置文件硬编码凭据: ${cfgName}`,
        SEVERITY.HIGH,
        `${cfgPath} 中发现 ${found.length} 个疑似硬编码凭据`,
        found.join('\n'),
        '使用环境变量或加密存储替代硬编码凭据'
      );
    }
  }
}

// ─────────────────────────────────────────────
// 3. 网关与认证配置检测 (SYS-006, SYS-007, ECO-006)
// ─────────────────────────────────────────────
function auditGatewayAuth(report) {
  const MODULE = 'gateway-auth';
  const configDir = getConfigDir();

  if (!configDir) return;

  const config = safeReadJson(path.join(configDir, 'clawdbot.json'))
    || safeReadJson(path.join(configDir, 'openclaw.json'))
    || safeReadJson(path.join(configDir, 'config.json'));

  if (!config) {
    report.add(MODULE, 'SYS-006', '网关配置文件',
      SEVERITY.MEDIUM, '未找到 OpenClaw 主配置文件，无法验证网关配置');
    return;
  }

  const gw = config.gateway || config.server || {};

  // 3.1 检查绑定地址
  const bind = gw.bind || gw.host || '0.0.0.0';
  if (bind === '0.0.0.0' || bind === '::') {
    report.add(MODULE, 'SYS-006', '网关绑定到所有网络接口',
      SEVERITY.CRITICAL,
      `gateway.bind = "${bind}" — 网关对所有网络接口开放，可能暴露于公网`,
      `当前配置: bind=${bind}, port=${gw.port || 18789}`,
      '设置 gateway.bind = "loopback" 或 "127.0.0.1"，如需外部访问请使用反向代理'
    );
  } else if (bind === '127.0.0.1' || bind === 'localhost' || bind === 'loopback') {
    report.add(MODULE, 'SYS-006', '网关绑定地址',
      SEVERITY.PASS, `网关已绑定到回环地址: ${bind}`);
  }

  // 3.2 检查认证配置
  const auth = gw.auth || config.auth || {};
  if (!auth.mode || auth.mode === 'none') {
    report.add(MODULE, 'SYS-006', '网关认证未启用',
      SEVERITY.CRITICAL,
      '网关未配置认证机制 (auth.mode = none 或未设置)',
      null,
      '设置 gateway.auth.mode = "token" 并配置强随机 Token'
    );
  } else if (auth.mode === 'token' && auth.token) {
    // 检查 Token 强度
    if (auth.token.length < 32) {
      report.add(MODULE, 'SYS-006', '认证 Token 强度不足',
        SEVERITY.HIGH,
        `Token 长度仅 ${auth.token.length} 字符 (建议 ≥ 32)`,
        null,
        '使用 openssl rand -hex 32 生成强随机 Token'
      );
    } else {
      report.add(MODULE, 'SYS-006', '网关认证配置',
        SEVERITY.PASS, `认证模式: ${auth.mode}，Token 长度: ${auth.token.length}`);
    }
  }

  // 3.3 检查 WebSocket 加密 (ECO-006)
  const wsUrl = gw.wsUrl || gw.websocket?.url || '';
  if (wsUrl.startsWith('ws://')) {
    report.add(MODULE, 'ECO-006', 'WebSocket 明文传输',
      SEVERITY.HIGH,
      `WebSocket 使用明文 ws:// 协议: ${wsUrl}`,
      null,
      '切换为 wss:// 协议，或通过 TLS 反向代理加密'
    );
  }

  // 3.4 检查 DM/Group 策略
  const channels = config.channels || config.messaging || {};
  const dmPolicy = channels.dmPolicy || 'allowAll';
  if (dmPolicy === 'allowAll') {
    report.add(MODULE, 'ECO-024', 'DM 策略过宽',
      SEVERITY.HIGH,
      `dmPolicy = "${dmPolicy}" — 允许任何人直接与 Agent 通信`,
      null,
      '设置 dmPolicy = "pairing" 以要求配对验证'
    );
  }

  // 3.5 检查速率限制 (SYS-007)
  const rateLimit = gw.rateLimit || config.rateLimit;
  if (!rateLimit) {
    report.add(MODULE, 'SYS-007 / OC-011', '未配置速率限制',
      SEVERITY.MEDIUM,
      '未检测到速率限制配置，所有端点可被无限次请求',
      null,
      '配置速率限制: 普通端点 30次/分钟，认证端点 5次/15分钟'
    );
  }

  // 3.6 检查沙箱配置 (ECO-009, OC-001)
  const sandbox = config.sandbox || {};
  if (!sandbox.mode || sandbox.mode === 'none' || sandbox.mode === 'off') {
    report.add(MODULE, 'ECO-009 / OC-001', '沙箱未启用',
      SEVERITY.CRITICAL,
      '命令执行沙箱未启用，Agent 可直接执行任意系统命令',
      `sandbox.mode = "${sandbox.mode || '未设置'}"`,
      '设置 sandbox.mode = "all"，sandbox.scope = "agent"'
    );
  } else {
    report.add(MODULE, 'ECO-009', '沙箱配置',
      SEVERITY.PASS, `沙箱已启用: mode=${sandbox.mode}`);
  }

  // 3.7 检查审计日志 (SYS-004)
  const logging = config.logging || {};
  if (!logging.auditLog && !logging.security) {
    report.add(MODULE, 'SYS-004', '安全审计日志未启用',
      SEVERITY.HIGH,
      '未检测到安全审计日志配置，安全事件无法追溯',
      null,
      '启用 logging.auditLog = true，并配置 logging.redactSensitive = "tools"'
    );
  }

  // 3.8 检查 Coding Agent --yolo 模式 (ECO-003)
  const tools = config.tools || {};
  const codingAgent = tools.codingAgent || tools['coding-agent'] || {};
  if (codingAgent.yolo === true || codingAgent.autoApprove === true) {
    report.add(MODULE, 'ECO-003', 'Coding Agent --yolo 模式已启用',
      SEVERITY.CRITICAL,
      'Coding Agent 的 --yolo 模式允许跳过所有确认提示，直接执行系统命令',
      null,
      '禁用 --yolo 模式，设置 codingAgent.yolo = false'
    );
  }
}

// ─────────────────────────────────────────────
// 4. 恶意 Skill 扫描 (ClawHavoc)
// ─────────────────────────────────────────────
function auditInstalledSkills(report) {
  const MODULE = 'malicious-skills';

  // 已知恶意 Skill 名称 (来自报告 14.2 节)
  const KNOWN_MALICIOUS_SKILLS = [
    'agent-browser-6aigix9qi2tu',
    'auto-updater-ah1',
    'base-agent',
    'browser-agent-1kv',
    'clawbhub',
    'coding-agent-4ilvlj7rs',
    'deep-research-eoo5vd95',
    'skills-security-check-gpz',
    'twitter-sum',
    'yahoo-finance-5tv',
    'youtube-watchar',
    'x-twitter-trends',
  ];

  // 已知恶意攻击者 (来自报告 14.2.2 节)
  const KNOWN_MALICIOUS_AUTHORS = [
    'hightower6eu',
    'sakaen736jih',
    'zaycv',
    'denboss99',
  ];

  // Skill 搜索路径
  const skillDirs = [];
  const configDir = getConfigDir();
  if (configDir) {
    skillDirs.push(path.join(configDir, 'skills'));
  }
  // 工作区 skills
  const cwdSkills = path.join(process.cwd(), 'skills');
  if (fs.existsSync(cwdSkills)) skillDirs.push(cwdSkills);

  if (skillDirs.length === 0) {
    report.add(MODULE, 'ClawHavoc', '已安装 Skill 扫描',
      SEVERITY.LOW, '未找到 Skill 安装目录，跳过恶意 Skill 扫描');
    return;
  }

  let totalSkills = 0;
  let maliciousFound = [];
  let suspiciousAuthors = [];

  for (const skillDir of skillDirs) {
    if (!fs.existsSync(skillDir)) continue;

    let entries;
    try {
      entries = fs.readdirSync(skillDir, { withFileTypes: true });
    } catch { continue; }

    for (const entry of entries) {
      if (!entry.isDirectory()) continue;
      totalSkills++;
      const skillName = entry.name.toLowerCase();
      const skillPath = path.join(skillDir, entry.name);

      // 检查是否匹配已知恶意 Skill
      if (KNOWN_MALICIOUS_SKILLS.some(ms => skillName.includes(ms) || ms.includes(skillName))) {
        maliciousFound.push({ name: entry.name, path: skillPath, reason: '匹配已知恶意 Skill 名单' });
      }

      // 检查 package.json 中的作者信息
      const pkg = safeReadJson(path.join(skillPath, 'package.json'));
      if (pkg) {
        const author = typeof pkg.author === 'string' ? pkg.author : (pkg.author?.name || '');
        if (KNOWN_MALICIOUS_AUTHORS.some(ma => author.toLowerCase().includes(ma))) {
          suspiciousAuthors.push({ name: entry.name, author, path: skillPath });
        }

        // 检查 postinstall 脚本 (ECO-015)
        const scripts = pkg.scripts || {};
        for (const hook of ['postinstall', 'preinstall', 'install', 'prepare']) {
          if (scripts[hook]) {
            report.add(MODULE, 'ECO-015', `Skill "${entry.name}" 包含安装钩子脚本`,
              SEVERITY.HIGH,
              `${hook} 脚本可在安装时自动执行任意命令`,
              `${hook}: ${scripts[hook]}`,
              '审计 postinstall 脚本内容，使用 --ignore-scripts 安装'
            );
          }
        }
      }
    }
  }

  if (maliciousFound.length > 0) {
    report.add(MODULE, 'ClawHavoc', `发现 ${maliciousFound.length} 个已知恶意 Skill`,
      SEVERITY.CRITICAL,
      '以下 Skill 已被安全分析确认为恶意，必须立即卸载',
      maliciousFound.map(m => `${m.name} (${m.path}) — ${m.reason}`).join('\n'),
      '立即删除恶意 Skill 目录，轮换所有 API Key/Token'
    );
  } else {
    report.add(MODULE, 'ClawHavoc', '恶意 Skill 名单比对',
      SEVERITY.PASS, `已扫描 ${totalSkills} 个 Skill，未匹配已知恶意名单`);
  }

  if (suspiciousAuthors.length > 0) {
    report.add(MODULE, 'ClawHavoc', `发现 ${suspiciousAuthors.length} 个可疑作者的 Skill`,
      SEVERITY.CRITICAL,
      '以下 Skill 的作者匹配已知恶意攻击者账户',
      suspiciousAuthors.map(s => `${s.name} (author: ${s.author})`).join('\n'),
      '立即卸载这些 Skill，检查系统是否已被入侵'
    );
  }
}

// ─────────────────────────────────────────────
// 5. SKILL.md 恶意内容检测 (OC-009, ECO-015)
// ─────────────────────────────────────────────
function auditSkillMdContent(report) {
  const MODULE = 'skillmd-scan';

  const skillDirs = [];
  const configDir = getConfigDir();
  if (configDir) skillDirs.push(path.join(configDir, 'skills'));
  const cwdSkills = path.join(process.cwd(), 'skills');
  if (fs.existsSync(cwdSkills)) skillDirs.push(cwdSkills);

  const MALICIOUS_PATTERNS = [
    { pattern: /echo\s+['"][A-Za-z0-9+/]{40,}={0,2}['"]\s*\|\s*base64\s+-[dD]/g, label: 'Base64 编码命令执行', severity: SEVERITY.CRITICAL, vulnId: 'OC-009' },
    { pattern: /curl\s+-[a-zA-Z]*s[a-zA-Z]*L?\s+https?:\/\/[^\s]+\s*\|\s*(ba)?sh/g, label: 'curl 下载并执行', severity: SEVERITY.CRITICAL, vulnId: 'ClawHavoc' },
    { pattern: /wget\s+[^\s]+\s*(-O\s*-\s*)?\|\s*(ba)?sh/g, label: 'wget 下载并执行', severity: SEVERITY.CRITICAL, vulnId: 'ClawHavoc' },
    { pattern: /bash\s+-i\s+>&\s+\/dev\/tcp\/[0-9.]+\/[0-9]+/g, label: '反向 Shell (bash)', severity: SEVERITY.CRITICAL, vulnId: 'ClawHavoc' },
    { pattern: /python[23]?\s+-c\s+['"]import\s+socket/g, label: '反向 Shell (python)', severity: SEVERITY.CRITICAL, vulnId: 'ClawHavoc' },
    { pattern: /nc\s+-[a-z]*e\s+\/bin\/(ba)?sh/g, label: '反向 Shell (netcat)', severity: SEVERITY.CRITICAL, vulnId: 'ClawHavoc' },
    { pattern: /\bchmod\s+[+0-7]*[x7]/g, label: '文件权限修改', severity: SEVERITY.MEDIUM, vulnId: 'ECO-015' },
    { pattern: /\/bin\/bash\s+-c\s+"\$\(curl/g, label: '命令替换下载执行', severity: SEVERITY.CRITICAL, vulnId: 'ClawHavoc' },
    { pattern: /sudo\s+-[Ss]/g, label: 'sudo 密码获取', severity: SEVERITY.HIGH, vulnId: 'ClawHavoc' },
    { pattern: /osascript\s+-e.*display\s+dialog.*password/gi, label: 'macOS 伪造密码对话框', severity: SEVERITY.CRITICAL, vulnId: 'ClawHavoc' },
    { pattern: /\beval\s*\(/g, label: 'eval() 动态代码执行', severity: SEVERITY.HIGH, vulnId: 'ECO-001' },
    { pattern: /new\s+Function\s*\(/g, label: 'Function 构造器代码执行', severity: SEVERITY.CRITICAL, vulnId: 'ECO-001' },
  ];

  // 已知恶意 C2 地址
  const MALICIOUS_HOSTS = [
    /91\.92\.242\.30/g,
    /95\.92\.242\.30/g,
    /54\.91\.154\.110/g,
    /92\.92\.242\.30/g,
    /202\.161\.50\.59/g,
    /96\.92\.242\.30/g,
    /socifiapp\.com/gi,
    /rentry\.co/gi,
    /app-distribution\.net/gi,
  ];

  let scannedFiles = 0;
  let findings = [];

  for (const dir of skillDirs) {
    const skillMdFiles = findFiles(dir, /^SKILL\.md$/i);
    const jsFiles = findFiles(dir, /\.(js|ts|mjs|cjs)$/);
    const allFiles = [...skillMdFiles, ...jsFiles];

    for (const filePath of allFiles) {
      const content = safeReadText(filePath);
      if (!content) continue;
      scannedFiles++;

      // 检查恶意代码模式
      for (const { pattern, label, severity, vulnId } of MALICIOUS_PATTERNS) {
        // 重置 regex lastIndex
        pattern.lastIndex = 0;
        const matches = content.match(pattern);
        if (matches) {
          findings.push({
            file: filePath, label, severity, vulnId,
            match: matches[0].substring(0, 100),
          });
        }
      }

      // 检查恶意 C2 地址
      for (const hostPattern of MALICIOUS_HOSTS) {
        hostPattern.lastIndex = 0;
        const matches = content.match(hostPattern);
        if (matches) {
          findings.push({
            file: filePath, label: `已知恶意地址: ${matches[0]}`,
            severity: SEVERITY.CRITICAL, vulnId: 'IOC',
            match: matches[0],
          });
        }
      }

      // 检查可疑的长 Base64 字符串 (OC-009)
      const base64Matches = content.match(/[A-Za-z0-9+/]{60,}={0,2}/g);
      if (base64Matches) {
        for (const b64 of base64Matches) {
          try {
            const decoded = Buffer.from(b64, 'base64').toString('utf-8');
            // 检查解码后是否包含可执行命令
            if (/\b(curl|wget|bash|sh|python|perl|nc|exec|eval)\b/i.test(decoded)) {
              findings.push({
                file: filePath,
                label: `隐藏 Base64 编码命令`,
                severity: SEVERITY.CRITICAL,
                vulnId: 'OC-009',
                match: `编码: ${b64.substring(0, 40)}... → 解码: ${decoded.substring(0, 80)}...`,
              });
            }
          } catch { /* 非有效 Base64 */ }
        }
      }
    }
  }

  if (findings.length > 0) {
    // 按严重级别分组输出
    const criticals = findings.filter(f => f.severity === SEVERITY.CRITICAL);
    const others = findings.filter(f => f.severity !== SEVERITY.CRITICAL);

    if (criticals.length > 0) {
      report.add(MODULE, 'OC-009 / ClawHavoc', `SKILL.md/代码文件中发现 ${criticals.length} 个严重恶意模式`,
        SEVERITY.CRITICAL,
        '在已安装 Skill 的文件中检测到恶意代码模式',
        criticals.map(f => `[${f.vulnId}] ${f.file}\n  → ${f.label}: ${f.match}`).join('\n\n'),
        '立即删除包含恶意代码的 Skill，进行完整的安全事件响应'
      );
    }
    if (others.length > 0) {
      report.add(MODULE, 'ECO-015', `SKILL.md/代码文件中发现 ${others.length} 个可疑模式`,
        SEVERITY.HIGH,
        '在已安装 Skill 的文件中检测到可疑代码模式',
        others.map(f => `[${f.vulnId}] ${f.file}\n  → ${f.label}: ${f.match}`).join('\n\n'),
        '审查这些文件内容，确认是否为正常功能'
      );
    }
  } else {
    report.add(MODULE, 'OC-009', 'SKILL.md 内容扫描',
      SEVERITY.PASS, `已扫描 ${scannedFiles} 个文件，未检测到已知恶意模式`);
  }
}

// ─────────────────────────────────────────────
// 6. IOC (Indicators of Compromise) 检测
// ─────────────────────────────────────────────
function auditIOC(report) {
  const MODULE = 'ioc-detection';

  const MALICIOUS_IPS = [
    { ip: '91.92.242.30', desc: '主要载荷分发服务器 & C2' },
    { ip: '95.92.242.30', desc: '备用载荷服务器' },
    { ip: '54.91.154.110', desc: '反向 Shell 回连 & 数据外传 (端口 13338)' },
    { ip: '92.92.242.30', desc: '备用 C2' },
    { ip: '11.92.242.30', desc: '备用 C2' },
    { ip: '202.161.50.59', desc: '备用载荷服务器' },
    { ip: '96.92.242.30', desc: '备用 C2' },
  ];

  const MALICIOUS_DOMAINS = [
    { domain: 'socifiapp.com', desc: '主要 C2 服务器域名' },
    { domain: 'rentry.co', desc: '载荷中转/配置托管' },
    { domain: 'install.app-distribution.net', desc: '伪装软件分发域名' },
  ];

  const KNOWN_MALICIOUS_HASHES = [
    { hash: '30f97ae88f8861eeadeb54854d47078724e52e2ef36dd847180663b7f5763168', desc: 'dyrtvwjfveyxjf23 载荷' },
    { hash: '7634cef8a02894f0c4456f924440de4d92b943e329f08c63dd88e86c1b7e3e86', desc: '第一阶段下载器' },
    { hash: '9f5d2e54cd296ad3e2ef6cbed05c8e1e5aa1c3bf84a7457e54deeed9f71ced43', desc: 'Atomic Stealer 变种' },
  ];

  // 6.1 检测网络连接到恶意 IP
  const activeConnections = [];
  const netOutput = safeExec('netstat -an 2>/dev/null || ss -tn 2>/dev/null');
  if (netOutput) {
    for (const { ip, desc } of MALICIOUS_IPS) {
      if (netOutput.includes(ip)) {
        activeConnections.push(`${ip} — ${desc}`);
      }
    }
  }

  if (activeConnections.length > 0) {
    report.add(MODULE, 'IOC-NET', `检测到 ${activeConnections.length} 个到恶意 IP 的活跃连接`,
      SEVERITY.CRITICAL,
      '系统正在与已知恶意 C2 服务器通信，可能已被入侵',
      activeConnections.join('\n'),
      '立即断开网络连接，启动 P0 事件响应流程'
    );
  } else {
    report.add(MODULE, 'IOC-NET', '恶意 IP 连接检测',
      SEVERITY.PASS, `已检查 ${MALICIOUS_IPS.length} 个已知恶意 IP，未发现活跃连接`);
  }

  // 6.2 检测 DNS 解析到恶意域名
  for (const { domain, desc } of MALICIOUS_DOMAINS) {
    const dnsResult = safeExec(`host ${domain} 2>/dev/null || nslookup ${domain} 2>/dev/null`);
    if (dnsResult && !dnsResult.includes('NXDOMAIN') && !dnsResult.includes('not found')) {
      // 检查 OpenClaw 配置/Skill 文件中是否引用了该域名
      const configDir = getConfigDir();
      if (configDir) {
        const grepResult = safeExec(`grep -r "${domain}" "${configDir}" 2>/dev/null`);
        if (grepResult) {
          report.add(MODULE, 'IOC-DNS', `配置文件中引用恶意域名: ${domain}`,
            SEVERITY.CRITICAL,
            `在 OpenClaw 目录中发现对恶意域名 ${domain} (${desc}) 的引用`,
            grepResult.substring(0, 500),
            '检查引用来源，删除恶意 Skill'
          );
        }
      }
    }
  }

  // 6.3 检测恶意文件哈希
  const configDir = getConfigDir();
  if (configDir) {
    const filesToCheck = findFiles(configDir, /\.(js|ts|sh|py|bin)$/);
    // 同时检查 /tmp 目录下的可疑文件
    const tmpFiles = findFiles('/tmp', /^[a-z0-9]{10,}$/);
    const allFiles = [...filesToCheck, ...tmpFiles].slice(0, 500); // 限制扫描数量

    let hashMatchCount = 0;
    for (const file of allFiles) {
      const hash = safeExec(`shasum -a 256 "${file}" 2>/dev/null | awk '{print $1}'`);
      if (!hash) continue;
      for (const { hash: malHash, desc } of KNOWN_MALICIOUS_HASHES) {
        if (hash === malHash) {
          hashMatchCount++;
          report.add(MODULE, 'IOC-HASH', `发现恶意文件: ${file}`,
            SEVERITY.CRITICAL,
            `文件哈希匹配已知恶意软件: ${desc}`,
            `SHA256: ${hash}\n文件路径: ${file}`,
            '立即隔离文件，启动事件响应'
          );
        }
      }
    }

    if (hashMatchCount === 0) {
      report.add(MODULE, 'IOC-HASH', '恶意文件哈希检测',
        SEVERITY.PASS, `已扫描 ${allFiles.length} 个文件，未匹配已知恶意哈希`);
    }
  }

  // 6.4 检查可疑进程
  const suspiciousProcs = safeExec(
    'ps aux 2>/dev/null | grep -E "(91\\.92\\.242|54\\.91\\.154|socifiapp|dyrtvwjfveyxjf)" | grep -v grep'
  );
  if (suspiciousProcs) {
    report.add(MODULE, 'IOC-PROC', '发现可疑进程',
      SEVERITY.CRITICAL,
      '检测到与已知恶意活动关联的进程',
      suspiciousProcs,
      '立即终止可疑进程并进行完整取证'
    );
  }

  // 6.5 检查 crontab 中的可疑条目
  const crontab = safeExec('crontab -l 2>/dev/null');
  if (crontab) {
    const suspiciousCron = crontab.split('\n').filter(line =>
      /curl|wget|base64|\/dev\/tcp|python.*-c|nc\s+-/i.test(line) && !line.startsWith('#')
    );
    if (suspiciousCron.length > 0) {
      report.add(MODULE, 'IOC-CRON', `crontab 中发现 ${suspiciousCron.length} 个可疑条目`,
        SEVERITY.HIGH,
        '定时任务中包含可疑命令',
        suspiciousCron.join('\n'),
        '检查并删除可疑的 crontab 条目'
      );
    }
  }
}

// ─────────────────────────────────────────────
// 7. 进程隔离与共享内存检测 (SYS-001, ECO-004, ECO-014)
// ─────────────────────────────────────────────
function auditProcessIsolation(report) {
  const MODULE = 'process-isolation';

  // 7.1 检查是否可以枚举加载的模块 (SYS-001)
  const loadedModules = Object.keys(require.cache);
  const sensitiveModules = loadedModules.filter(m =>
    /child_process|crypto|net|dgram|cluster|worker_threads/.test(m)
  );

  report.add(MODULE, 'SYS-001', `进程共享 ${loadedModules.length} 个已加载模块`,
    SEVERITY.HIGH,
    `当前进程可枚举所有已加载模块（共 ${loadedModules.length} 个），其中 ${sensitiveModules.length} 个为敏感系统模块`,
    sensitiveModules.length > 0 ? `敏感模块:\n${sensitiveModules.slice(0, 10).join('\n')}` : null,
    '实施进程隔离：使用 Docker/bwrap 沙箱为每个 Skill 创建独立执行环境'
  );

  // 7.2 检查是否可以 require 危险模块 (SYS-001, ECO-004)
  const dangerousModules = ['child_process', 'fs', 'net', 'dgram', 'http', 'https'];
  const accessible = [];
  for (const mod of dangerousModules) {
    try {
      require(mod);
      accessible.push(mod);
    } catch { /* 模块不可用 */ }
  }

  if (accessible.length > 0) {
    report.add(MODULE, 'SYS-001 / ECO-004', `${accessible.length} 个危险模块可直接 require`,
      SEVERITY.HIGH,
      `Skill 执行环境可直接加载危险 Node.js 模块`,
      `可用危险模块: ${accessible.join(', ')}`,
      '在 Skill 沙箱中限制 require() 可访问的模块，使用 seccomp-bpf 过滤系统调用'
    );
  }
}

// ─────────────────────────────────────────────
// 8. 文件系统敏感路径检测 (OC-004, OC-005)
// ─────────────────────────────────────────────
function auditSensitivePaths(report) {
  const MODULE = 'sensitive-paths';

  const SENSITIVE_PATHS = [
    { path: path.join(HOME, '.ssh', 'id_rsa'), desc: 'SSH 私钥', vulnId: 'OC-005' },
    { path: path.join(HOME, '.ssh', 'id_ed25519'), desc: 'SSH 私钥 (Ed25519)', vulnId: 'OC-005' },
    { path: path.join(HOME, '.aws', 'credentials'), desc: 'AWS 凭据', vulnId: 'OC-005' },
    { path: path.join(HOME, '.gnupg', 'secring.gpg'), desc: 'GPG 私钥环', vulnId: 'OC-005' },
    { path: '/etc/shadow', desc: '系统密码哈希', vulnId: 'OC-005' },
  ];

  // 检查这些敏感文件是否可从当前进程读取 (模拟 Skill 的权限)
  const readable = [];
  for (const { path: fp, desc, vulnId } of SENSITIVE_PATHS) {
    try {
      fs.accessSync(fp, fs.constants.R_OK);
      readable.push({ path: fp, desc, vulnId });
    } catch { /* 不可读，正常 */ }
  }

  if (readable.length > 0) {
    report.add(MODULE, 'OC-004 / OC-005', `${readable.length} 个敏感文件可从 Skill 进程读取`,
      SEVERITY.HIGH,
      '当前执行环境可读取系统敏感文件，恶意 Skill 可窃取这些凭据',
      readable.map(r => `[${r.vulnId}] ${r.path} — ${r.desc}`).join('\n'),
      '在沙箱配置中限制文件系统访问路径，将敏感文件加入 sandbox-paths 黑名单'
    );
  } else {
    report.add(MODULE, 'OC-005', '敏感文件访问检测',
      SEVERITY.PASS, `已检查 ${SENSITIVE_PATHS.length} 个敏感路径，均不可从当前进程读取`);
  }

  // 检查 OpenClaw 配置文件权限 (OC-004)
  const configDir = getConfigDir();
  if (configDir) {
    const configFiles = findFiles(configDir, /\.(json|yaml|yml|toml|env)$/);
    const widePerms = [];
    for (const file of configFiles) {
      try {
        const stat = fs.statSync(file);
        const perms = stat.mode & parseInt('777', 8);
        // 检查是否 other-readable
        if (perms & parseInt('004', 8)) {
          widePerms.push({ file, perms: '0' + perms.toString(8) });
        }
      } catch { /* */ }
    }

    if (widePerms.length > 0) {
      report.add(MODULE, 'OC-004', `${widePerms.length} 个配置文件权限过宽`,
        SEVERITY.MEDIUM,
        '配置文件可被其他用户读取',
        widePerms.map(w => `${w.file} (权限: ${w.perms})`).join('\n'),
        '执行 chmod 600 限制配置文件权限'
      );
    }
  }
}

// ─────────────────────────────────────────────
// 9. 网络监听端口检测
// ─────────────────────────────────────────────
function auditNetworkExposure(report) {
  const MODULE = 'network-exposure';

  // 检查 OpenClaw 相关端口是否对外开放
  const listeningPorts = safeExec('netstat -tlnp 2>/dev/null || ss -tlnp 2>/dev/null');
  if (!listeningPorts) return;

  const OPENCLAW_PORTS = [18789, 3000, 8080, 8443];
  const exposedPorts = [];

  for (const port of OPENCLAW_PORTS) {
    // 检查是否绑定到 0.0.0.0
    if (listeningPorts.includes(`0.0.0.0:${port}`) || listeningPorts.includes(`:::${port}`)) {
      exposedPorts.push(port);
    }
  }

  if (exposedPorts.length > 0) {
    report.add(MODULE, 'SYS-006', `${exposedPorts.length} 个端口绑定到所有接口`,
      SEVERITY.HIGH,
      `以下端口对所有网络接口开放: ${exposedPorts.join(', ')}`,
      null,
      '将服务绑定到 127.0.0.1，通过反向代理暴露必要端口'
    );
  }
}

// ─────────────────────────────────────────────
// 10. Bearer Token 时序侧信道检测 (ECO-022)
// ─────────────────────────────────────────────
function auditTimingSideChannel(report) {
  const MODULE = 'timing-analysis';

  // 检查配置中是否使用了安全的常量时间比较
  const configDir = getConfigDir();
  if (!configDir) return;

  const jsFiles = findFiles(configDir, /\.(js|ts)$/);
  let unsafeCompare = false;

  for (const file of jsFiles) {
    const content = safeReadText(file);
    if (!content) continue;

    // 检查是否使用 === 比较 token (而非 timingSafeEqual)
    if (/token\s*===\s*|===\s*token|\.token\s*===|password\s*===/i.test(content) &&
        !content.includes('timingSafeEqual')) {
      unsafeCompare = true;
      break;
    }
  }

  if (unsafeCompare) {
    report.add(MODULE, 'ECO-022', 'Token 比较存在时序侧信道风险',
      SEVERITY.MEDIUM,
      '检测到使用 === 进行 Token 比较，可能存在时序侧信道攻击',
      null,
      '使用 crypto.timingSafeEqual() 进行常量时间比较'
    );
  }
}

// ─────────────────────────────────────────────
// 主程序入口
// ─────────────────────────────────────────────
function main() {
  const args = process.argv.slice(2);
  const format = args.includes('--format') ? args[args.indexOf('--format') + 1] : 'console';
  const output = args.includes('--output') ? args[args.indexOf('--output') + 1] : null;
  const moduleArg = args.includes('--module') ? args[args.indexOf('--module') + 1] : null;
  const enabledModules = moduleArg ? moduleArg.split(',').map(m => m.trim()) : null;

  const report = new AuditReport();

  console.log('\n🔍 OpenClaw Security Audit Tool v1.0.0');
  console.log('━'.repeat(50));
  console.log(`📅 ${new Date().toISOString()}`);
  console.log(`💻 ${os.platform()} ${os.arch()} | Node ${process.version}`);
  console.log(`📂 配置目录: ${getConfigDir() || '未找到'}`);
  console.log('━'.repeat(50));

  const modules = [
    { name: 'env', label: '环境变量泄露检测', fn: auditEnvVars },
    { name: 'cred', label: '凭据存储安全检测', fn: auditCredentialStorage },
    { name: 'auth', label: '网关与认证配置检测', fn: auditGatewayAuth },
    { name: 'skills', label: '恶意 Skill 扫描', fn: auditInstalledSkills },
    { name: 'skillmd', label: 'SKILL.md 恶意内容检测', fn: auditSkillMdContent },
    { name: 'ioc', label: 'IOC 指标检测', fn: auditIOC },
    { name: 'isolation', label: '进程隔离验证', fn: auditProcessIsolation },
    { name: 'paths', label: '敏感路径检测', fn: auditSensitivePaths },
    { name: 'network', label: '网络暴露检测', fn: auditNetworkExposure },
    { name: 'timing', label: '时序侧信道检测', fn: auditTimingSideChannel },
  ];

  for (const mod of modules) {
    if (enabledModules && !enabledModules.includes(mod.name)) continue;
    console.log(`\n▶ [${mod.name}] ${mod.label}...`);
    try {
      mod.fn(report);
      console.log(`  ✅ 完成`);
    } catch (err) {
      console.log(`  ❌ 错误: ${err.message}`);
      report.add(mod.name, 'ERR', `模块执行错误: ${mod.label}`,
        SEVERITY.LOW, `执行过程中发生错误: ${err.message}`);
    }
  }

  // 输出报告
  if (format === 'json') {
    const jsonReport = JSON.stringify(report.toJson(), null, 2);
    if (output) {
      fs.writeFileSync(output, jsonReport);
      console.log(`\n📄 JSON 报告已保存: ${output}`);
    } else {
      console.log(jsonReport);
    }
  } else {
    report.printConsole();
  }

  // 如果指定了输出文件，同时保存 console 格式
  if (output && format !== 'json') {
    const jsonReport = JSON.stringify(report.toJson(), null, 2);
    fs.writeFileSync(output, jsonReport);
    console.log(`📄 报告已保存: ${output}`);
  }

  // 返回退出码：有严重问题时返回 1
  const summary = report.getSummary();
  if (summary.CRITICAL > 0) process.exit(2);
  if (summary.HIGH > 0) process.exit(1);
  process.exit(0);
}

main();
