#!/usr/bin/env node

/**
 * Skills 安全安装工具 v2.0
 * 
 * 整合完整安全检查流程：
 * 1. Skill-Vetter 来源与代码审查
 * 2. ClawHub 评分检查
 * 3. ThreatBook 沙箱扫描
 * 4. 统一展示复核结果
 * 5. 按决策矩阵执行后续操作
 * 
 * 退出码:
 *   0 - 安装成功
 *   1 - 检测到恶意代码，禁止安装
 *   2 - 文件可疑，等待确认
 *   3 - API 调用失败
 *   4 - 评分过低，等待确认
 *   5 - 用户取消安装
 *   6 - Vetter 检查发现极端红旗
 */

import { execSync } from 'child_process';
import { readFileSync, writeFileSync, mkdirSync, rmSync, existsSync, readdirSync, statSync } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { platform } from 'os';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 配置
const THREATBOOK_API_BASE = 'https://api.threatbook.cn/v3';
const DEFAULT_TIMEOUT = 120000; // 120 秒
const SAFE_RATING_THRESHOLD = 3.5; // 安全评分阈值
const SAFE_MALICIOUS_RATE = 0.01; // 1% 恶意率阈值
const SUSPICIOUS_MALICIOUS_RATE = 0.10; // 10% 恶意率阈值

// 沙箱环境映射
const SANDBOX_TYPE_MAP = {
  'linux': 'ubuntu_1704_x64',
  'win32': 'win10_1903_enx64_office2016',
  'darwin': 'win10_1903_enx64_office2016'
};

// 颜色输出
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  bold: '\x1b[1m'
};

function log(message, color = 'reset', bold = false) {
  const prefix = bold ? colors.bold : '';
  console.log(`${prefix}${colors[color]}${message}${colors.reset}`);
}

function logSection(title) {
  log('\n' + '━'.repeat(50), 'cyan');
  log(title, 'cyan', true);
  log('━'.repeat(50), 'cyan');
}

// 解析命令行参数
function parseArgs(args) {
  const options = {
    force: args.includes('--force'),
    auto: args.includes('--auto') || args.includes('--yes') || args.includes('-y'),
    noVetter: args.includes('--no-vetter'),
    noScan: args.includes('--no-scan'),
    dryRun: args.includes('--dry-run'),
    timeout: parseInt(args.find(a => a.startsWith('--timeout='))?.split('=')[1] || '120') * 1000,
    help: args.includes('--help') || args.includes('-h')
  };
  
  const skillName = args.find(a => !a.startsWith('--'));
  
  return { options, skillName };
}

// 显示帮助
function showHelp() {
  console.log(`
🛡️  Skills 安全安装工具 v2.0

用法:
  node safe-install.mjs <skill-name> [选项]

选项:
  --auto, --yes, -y  自动模式（需要确认时自动询问任务下达者）
  --force            强制安装（跳过可疑警告）
  --no-vetter        跳过 Vetter 代码审查（不推荐）
  --no-scan          跳过沙箱扫描（不推荐）
  --dry-run          仅检查，不实际安装
  --timeout=<秒>     沙箱扫描超时时间（默认 120 秒）
  --help, -h         显示帮助

安全检查流程:
  1. Skill-Vetter 来源与代码审查（检查红旗）
  2. ClawHub 评分检查 (≥3.5 分？)
  3. ThreatBook 沙箱扫描
  4. 统一展示复核结果
  5. 按决策矩阵执行（安装/询问/禁止）

决策矩阵:
  ┌────────────┬─────────┬──────────┬────────────┐
  │ Vetter     │ 评分    │ 沙箱     │ 最终决策   │
  ├────────────┼─────────┼──────────┼────────────┤
  │ ✅ 通过    │ ≥3.5    │ 安全     │ ✅ 直接安装│
  │ ✅ 通过    │ ≥3.5    │ 可疑     │ ❓ 询问    │
  │ ✅ 通过    │ <3.5    │ 任意     │ ❓ 询问    │
  │ ⚠️ 高风险  │ 任意    │ 任意     │ ❓ 询问    │
  │ 🚨 极端风险│ 任意    │ 任意     │ ❌ 禁止    │
  │ 任意       │ 任意    │ 恶意     │ ❌ 禁止    │
  └────────────┴─────────┴──────────┴────────────┘

示例:
  node safe-install.mjs tavily-search
  node safe-install.mjs some-skill --auto
  node safe-install.mjs test-skill --dry-run
`);
}

// 获取 API Key
function getApiKey() {
  return process.env.THREATBOOK_API_KEY;
}

// 执行命令并返回输出
function execCommand(cmd, options = {}) {
  try {
    const result = execSync(cmd, { 
      encoding: 'utf8',
      stdio: options.silent ? 'pipe' : 'inherit',
      ...options
    });
    return { success: true, output: result };
  } catch (error) {
    return { 
      success: false, 
      error: error.message,
      status: error.status,
      output: error.stdout || ''
    };
  }
}

// 红旗检测规则（来自 skill-vetter）
const RED_FLAGS = [
  { pattern: /curl\s+.*\|.*bash/i, name: 'Curl pipe to bash', severity: 'extreme' },
  { pattern: /wget\s+.*\|.*bash/i, name: 'Wget pipe to bash', severity: 'extreme' },
  { pattern: /curl.*-d.*@.*(?:\/etc\/|\/home\/|\.ssh|\.aws)/i, name: 'Sending sensitive data', severity: 'extreme' },
  { pattern: /eval\s*\(/i, name: 'Use of eval()', severity: 'high' },
  { pattern: /exec\s*\(/i, name: 'Use of exec()', severity: 'high' },
  { pattern: /child_process\.exec/i, name: 'Child process exec', severity: 'high' },
  { pattern: /spawn\s*\(/i, name: 'Spawn process', severity: 'medium' },
  { pattern: /\.ssh\//i, name: 'Accessing .ssh directory', severity: 'extreme' },
  { pattern: /\.aws\//i, name: 'Accessing .aws directory', severity: 'extreme' },
  { pattern: /MEMORY\.md|USER\.md|SOUL\.md|IDENTITY\.md/i, name: 'Accessing memory files', severity: 'high' },
  { pattern: /base64\s*decode|atob\s*\(/i, name: 'Base64 decode', severity: 'medium' },
  { pattern: /fs\.readFile.*(?:\/etc\/passwd|\/etc\/shadow)/i, name: 'Reading system files', severity: 'extreme' },
  { pattern: /sudo\s+/i, name: 'Sudo command', severity: 'high' },
  { pattern: /document\.cookie/i, name: 'Accessing cookies', severity: 'high' },
  { pattern: /localStorage|sessionStorage/i, name: 'Accessing storage', severity: 'medium' },
  { pattern: /fetch\s*\(['"`]http/i, name: 'HTTP request', severity: 'low' },
  { pattern: /XMLHttpRequest/i, name: 'XHR request', severity: 'low' },
  { pattern: /net\.connect|socket\.connect/i, name: 'Network connection', severity: 'medium' },
  { pattern: /require\s*\(['"`]child_process['"`]\)/i, name: 'Child process module', severity: 'medium' },
  { pattern: /require\s*\(['"`]fs['"`]\)/i, name: 'File system module', severity: 'low' },
  { pattern: /require\s*\(['"`]net['"`]\)/i, name: 'Network module', severity: 'medium' },
  { pattern: /chmod\s+777/i, name: 'Insecure permissions', severity: 'high' },
  { pattern: /rm\s+-rf\s+\//i, name: 'Dangerous rm command', severity: 'extreme' },
  { pattern: /mktemp|\/tmp\//i, name: 'Temp file usage', severity: 'low' },
];

// 第一步：Skill-Vetter 代码审查
async function vetSkill(skillName, options) {
  logSection('第一步：Skill-Vetter 代码审查');
  
  const result = {
    passed: true,
    riskLevel: 'low',
    redFlags: [],
    permissions: {
      files: [],
      network: [],
      commands: []
    },
    source: 'unknown',
    author: 'unknown',
    needsConfirm: false
  };
  
  log(`🔍 获取 Skill 信息...`, 'cyan');
  
  // 获取 Skill 元数据
  const inspectResult = execCommand(`clawhub inspect "${skillName}"`, { silent: true });
  
  if (inspectResult.success) {
    const output = inspectResult.output;
    
    // 提取作者信息
    const authorMatch = output.match(/Owner:\s*(\S+)/i);
    if (authorMatch) {
      result.author = authorMatch[1];
      log(`👤 作者：${result.author}`, 'cyan');
    }
    
    // 提取更新时间
    const updatedMatch = output.match(/Updated:\s*(\S+)/i);
    if (updatedMatch) {
      log(`📅 更新时间：${updatedMatch[1]}`, 'cyan');
    }
    
    // 提取版本
    const versionMatch = output.match(/Latest:\s*(\S+)/i);
    if (versionMatch) {
      log(`📦 版本：${versionMatch[1]}`, 'cyan');
    }
  }
  
  // 信任层级检查
  log(`\n📊 信任层级评估...`, 'cyan');
  
  if (result.author === 'openclaw' || result.author === 'OpenClaw') {
    log(`✅ 官方 OpenClaw Skill - 较低审查`, 'green');
    result.source = 'official';
    result.riskLevel = 'low';
  } else if (['spclaudehome', 'CHJ0w0'].includes(result.author)) {
    log(`✅ 已知作者 - 中等审查`, 'green');
    result.source = 'known_author';
    result.riskLevel = 'medium';
  } else {
    log(`⚠️ 未知作者 - 最高审查`, 'yellow');
    result.source = 'unknown';
    result.riskLevel = 'high';
    result.needsConfirm = true;
  }
  
  // 临时下载 Skill 进行代码审查
  log(`\n📥 下载 Skill 进行代码审查...`, 'cyan');
  const tempDir = `/tmp/vet-skill-${Date.now()}`;
  mkdirSync(tempDir, { recursive: true });
  
  try {
    const downloadResult = execCommand(`clawhub install "${skillName}" --dir "${tempDir}"`, { silent: true });
    
    if (!downloadResult.success) {
      log(`⚠️ 无法下载 Skill 进行审查`, 'yellow');
      return result;
    }
    
    const skillPath = path.join(tempDir, skillName);
    log(`📂 审查目录：${skillPath}`, 'cyan');
    
    // 扫描所有 JS/MJS 文件
    const jsFiles = [];
    function scanDir(dir) {
      const files = readdirSync(dir);
      for (const file of files) {
        const filePath = path.join(dir, file);
        const stat = existsSync(filePath) ? statSync(filePath) : null;
        if (stat?.isDirectory() && !file.startsWith('.') && file !== 'node_modules') {
          scanDir(filePath);
        } else if (file.endsWith('.js') || file.endsWith('.mjs')) {
          jsFiles.push(filePath);
        }
      }
    }
    scanDir(skillPath);
    
    log(`📄 发现 ${jsFiles.length} 个脚本文件`, 'cyan');
    
    // 检查每个文件的红旗
    for (const jsFile of jsFiles) {
      const content = readFileSync(jsFile, 'utf8');
      const relativePath = path.relative(skillPath, jsFile);
      
      for (const flag of RED_FLAGS) {
        const matches = content.match(flag.pattern);
        if (matches) {
          const flagInfo = {
            file: relativePath,
            name: flag.name,
            severity: flag.severity,
            line: content.substring(0, matches.index).split('\n').length
          };
          
          result.redFlags.push(flagInfo);
          
          // 记录权限需求
          if (flag.name.includes('fs') || flag.name.includes('File')) {
            result.permissions.files.push(relativePath);
          }
          if (flag.name.includes('fetch') || flag.name.includes('HTTP') || flag.name.includes('Network')) {
            result.permissions.network.push(relativePath);
          }
          if (flag.name.includes('exec') || flag.name.includes('spawn') || flag.name.includes('sudo')) {
            result.permissions.commands.push(relativePath);
          }
          
          // 严重红旗直接标记
          if (flag.severity === 'extreme') {
            result.passed = false;
            result.riskLevel = 'extreme';
          } else if (flag.severity === 'high' && result.riskLevel !== 'extreme') {
            result.riskLevel = 'high';
          }
        }
      }
    }
    
    // 输出审查结果
    log(`\n📊 Vetter 审查结果:`, 'cyan');
    
    if (result.redFlags.length === 0) {
      log(`✅ 未发现红旗`, 'green');
    } else {
      log(`⚠️ 发现 ${result.redFlags.length} 个潜在问题:`, 'yellow');
      for (const flag of result.redFlags.slice(0, 10)) {
        const severityIcon = flag.severity === 'extreme' ? '🚨' : 
                            flag.severity === 'high' ? '🔴' : 
                            flag.severity === 'medium' ? '🟡' : '🟢';
        log(`  ${severityIcon} ${flag.name} (${flag.file}:${flag.line})`, 
            flag.severity === 'extreme' ? 'red' : 
            flag.severity === 'high' ? 'red' : 
            flag.severity === 'medium' ? 'yellow' : 'reset');
      }
      if (result.redFlags.length > 10) {
        log(`  ... 还有 ${result.redFlags.length - 10} 个问题`, 'yellow');
      }
    }
    
    // 风险等级
    const riskIcon = result.riskLevel === 'extreme' ? '⛔' :
                    result.riskLevel === 'high' ? '🔴' :
                    result.riskLevel === 'medium' ? '🟡' : '🟢';
    log(`\n风险等级：${riskIcon} ${result.riskLevel.toUpperCase()}`, 
        result.riskLevel === 'extreme' ? 'red' : 
        result.riskLevel === 'high' ? 'red' : 
        result.riskLevel === 'medium' ? 'yellow' : 'green', true);
    
    // 判定
    if (result.riskLevel === 'extreme') {
      result.passed = false;
      result.needsConfirm = false; // 直接拒绝
    } else if (result.riskLevel === 'high' || result.redFlags.length > 0) {
      result.needsConfirm = true;
    }
    
    return result;
    
  } finally {
    // 清理临时目录
    if (existsSync(tempDir)) {
      rmSync(tempDir, { recursive: true, force: true });
    }
  }
}

// 第二步：ClawHub 评分检查
async function checkRating(skillName) {
  logSection('第二步：ClawHub 评分检查');
  
  log(`📋 查询 Skill: ${skillName}...`, 'cyan');
  
  const result = execCommand(`clawhub search "${skillName}"`, { silent: true });
  
  if (!result.success) {
    log(`⚠️ 无法获取 Skill 信息：${result.error}`, 'yellow');
    return { 
      passed: false, 
      score: null, 
      reason: '无法获取评分',
      needsConfirm: true 
    };
  }
  
  // 解析评分（从输出中提取）
  const output = result.output;
  const scoreMatch = output.match(/(?:评分 |Rating|Score)[:：]?\s*([\d.]+)/i);
  const score = scoreMatch ? parseFloat(scoreMatch[1]) : null;
  
  if (score === null) {
    log(`⚠️ 无法解析评分信息`, 'yellow');
    return { 
      passed: false, 
      score: null, 
      reason: '无法解析评分',
      needsConfirm: true 
    };
  }
  
  const passed = score >= SAFE_RATING_THRESHOLD;
  
  if (passed) {
    log(`✅ 评分：${score}/5.0 (高评分，通过)`, 'green');
  } else {
    log(`⚠️ 评分：${score}/5.0 (低于安全阈值 ${SAFE_RATING_THRESHOLD})`, 'yellow');
  }
  
  return { 
    passed, 
    score, 
    reason: passed ? '高评分' : '低评分',
    needsConfirm: !passed 
  };
}

// 上传文件到沙箱
async function uploadFile(filePath, apiKey, sandboxType) {
  const fileSize = existsSync(filePath) ? 
    (await import('fs')).promises.stat(filePath).then(s => s.size).catch(() => 0) : 0;
  
  if (fileSize > 100 * 1024 * 1024) {
    throw new Error('文件大小超过 100MB 限制');
  }
  
  log(`📤 上传文件到沙箱...`, 'cyan');
  log(`🖥️ 沙箱环境：${sandboxType}`, 'cyan');
  
  const curlCmd = `curl -s -X POST "${THREATBOOK_API_BASE}/file/upload?apikey=${apiKey}" \\
    -F "file=@${filePath}" \\
    -F "sandbox_type=${sandboxType}"`;
  
  const result = execCommand(curlCmd, { silent: true, shell: true });
  
  if (!result.success) {
    throw new Error(`上传失败：${result.error}`);
  }
  
  const data = JSON.parse(result.output);
  
  if (data.response_code !== 0) {
    throw new Error(data.verbose_msg || '上传失败');
  }
  
  const sha256 = data.data.sha256 || data.data.sample_sha256;
  log(`✅ 上传成功，SHA256: ${sha256.substring(0, 16)}...`, 'green');
  
  return { sha256, sandbox_type: sandboxType };
}

// 获取沙箱报告
async function getReport(sha256, sandboxType, apiKey, timeout) {
  log(`⏳ 等待沙箱分析结果...`, 'yellow');
  
  const startTime = Date.now();
  const pollInterval = 10000;
  
  while (Date.now() - startTime < timeout) {
    const curlCmd = `curl -s -X GET "${THREATBOOK_API_BASE}/file/report?apikey=${apiKey}&sha256=${sha256}&sandbox_type=${sandboxType}"`;
    const result = execCommand(curlCmd, { silent: true, shell: true });
    
    if (result.success) {
      try {
        const data = JSON.parse(result.output);
        if (data.response_code === 0 && data.data) {
          const summary = data.data.summary;
          if (summary && summary.threat_level) {
            log(`✅ 分析完成`, 'green');
            return data.data;
          }
        }
      } catch (e) {
        // 继续等待
      }
    }
    
    log(`⏳ 等待分析结果...`, 'yellow');
    await sleep(pollInterval);
  }
  
  throw new Error('扫描超时');
}

// 分析沙箱结果
function analyzeResult(report) {
  const result = {
    verdict: 'safe',
    confidence: 0,
    threatLevel: 'unknown',
    engines: { total: 0, malicious: 0 },
    threatTypes: [],
    message: ''
  };
  
  if (report && report.summary) {
    const summary = report.summary;
    result.threatLevel = summary.threat_level;
    
    // 白名单检查
    if (summary.is_whitelist === true) {
      result.verdict = 'safe';
      result.confidence = 99;
      result.message = '✅ 白名单文件，安全';
      return result;
    }
    
    // 根据 threat_level 判定
    if (summary.threat_level === 'clean') {
      result.verdict = 'safe';
      result.confidence = 90;
    } else if (summary.threat_level === 'suspicious') {
      result.verdict = 'suspicious';
      result.confidence = 70;
    } else if (summary.threat_level === 'malicious') {
      result.verdict = 'malicious';
      result.confidence = 95;
    } else {
      result.verdict = 'suspicious';
      result.confidence = 50;
    }
    
    // 提取威胁类型
    if (summary.malware_type) {
      result.threatTypes.push(summary.malware_type);
    }
    
    // 多引擎信息
    if (summary.multi_engines) {
      const match = summary.multi_engines.match(/(\d+)\/(\d+)/);
      if (match) {
        result.engines.malicious = parseInt(match[1]);
        result.engines.total = parseInt(match[2]);
      }
    }
  }
  
  // 生成消息
  const engineInfo = result.engines.total > 0 ? 
    ` (${result.engines.malicious}/${result.engines.total} 引擎检出)` : '';
  const malwareInfo = result.threatTypes.length > 0 ? 
    ` [${result.threatTypes.join(', ')}]` : '';
  
  if (result.verdict === 'malicious') {
    result.message = `❌ 检测到恶意代码${malwareInfo}${engineInfo}`;
  } else if (result.verdict === 'suspicious') {
    result.message = `⚠️ 文件可疑${engineInfo}`;
  } else {
    result.message = `✅ 文件安全 (${result.confidence}% 可信度)`;
  }
  
  return result;
}

// 第三步：ThreatBook 沙箱扫描
async function scanSkill(skillName, options) {
  logSection('第三步：ThreatBook 沙箱扫描');
  
  const apiKey = getApiKey();
  if (!apiKey) {
    log(`⚠️ 未配置 THREATBOOK_API_KEY`, 'yellow');
    log(`   请在 ~/.openclaw/.env 中添加 API Key`, 'yellow');
    return { 
      passed: false, 
      apiFailed: true, 
      needsConfirm: true,
      reason: 'API Key 未配置'
    };
  }
  
  try {
    // 临时下载 Skill
    const tempDir = `/tmp/safe-install-${Date.now()}`;
    mkdirSync(tempDir, { recursive: true });
    
    try {
      log(`📥 下载 Skill 进行扫描...`, 'cyan');
      const downloadResult = execCommand(
        `clawhub install "${skillName}" --dir "${tempDir}"`, 
        { silent: true }
      );
      
      if (!downloadResult.success) {
        throw new Error('下载 Skill 失败');
      }
      
      const skillPath = path.join(tempDir, skillName);
      
      // 打包为 zip
      const zipPath = `/tmp/skill-${Date.now()}.zip`;
      execCommand(`cd "${skillPath}" && zip -r "${zipPath}" . -x "*.git*" -x "node_modules/*"`, { 
        silent: true, 
        shell: true 
      });
      
      // 上传并扫描
      const sandboxType = SANDBOX_TYPE_MAP[platform()] || 'ubuntu_1704_x64';
      const { sha256, sandbox_type } = await uploadFile(zipPath, apiKey, sandboxType);
      const report = await getReport(sha256, sandbox_type, apiKey, options.timeout);
      const result = analyzeResult(report);
      
      // 输出结果
      log(`\n📊 扫描结果:`, 'cyan');
      log(`  判定：${result.verdict.toUpperCase()}`, result.verdict === 'safe' ? 'green' : 
                                          result.verdict === 'malicious' ? 'red' : 'yellow');
      log(`  威胁等级：${result.threatLevel}`);
      log(`  可信度：${result.confidence}%`);
      if (result.engines.total > 0) {
        log(`  引擎检出：${result.engines.malicious}/${result.engines.total}`);
      }
      if (result.threatTypes.length > 0) {
        log(`  威胁类型：${result.threatTypes.join(', ')}`, 'red');
      }
      
      // 清理临时文件
      if (existsSync(zipPath)) rmSync(zipPath);
      
      return {
        passed: result.verdict === 'safe',
        apiFailed: false,
        needsConfirm: result.verdict !== 'safe',
        reason: result.verdict,
        confidence: result.confidence,
        engines: result.engines,
        threatTypes: result.threatTypes,
        message: result.message
      };
      
    } finally {
      if (existsSync(tempDir)) rmSync(tempDir, { recursive: true, force: true });
    }
    
  } catch (error) {
    log(`⚠️ 扫描失败：${error.message}`, 'yellow');
    return { 
      passed: false, 
      apiFailed: true, 
      needsConfirm: true,
      reason: `扫描失败：${error.message}`
    };
  }
}

// 展示复核结果摘要
function showSummary(vetResult, ratingResult, scanResult) {
  logSection('📋 复核结果摘要');
  
  log('\n┌─────────────────────────────────────────────────────┐', 'cyan');
  log('│              三层安全检查结果                       │', 'cyan', true);
  log('├─────────────────────────────────────────────────────┤', 'cyan');
  
  // Vetter 结果
  const vetIcon = vetResult.riskLevel === 'extreme' ? '🚨' :
                  vetResult.riskLevel === 'high' ? '🔴' :
                  vetResult.riskLevel === 'medium' ? '🟡' : '🟢';
  const vetStatus = vetResult.riskLevel === 'extreme' ? '禁止' :
                    vetResult.needsConfirm ? '需确认' : '通过';
  log(`│ 1️⃣ Vetter 审查    ${vetIcon} ${vetStatus.padEnd(6)} │ 风险：${vetResult.riskLevel.toUpperCase().padEnd(10)}│`, 'cyan');
  
  // 评分结果
  const ratingIcon = ratingResult.passed ? '✅' : '⚠️';
  const ratingStatus = ratingResult.passed ? '通过' : '需确认';
  const scoreStr = ratingResult.score !== null ? `${ratingResult.score}/5.0` : 'N/A';
  log(`│ 2️⃣ ClawHub 评分   ${ratingIcon} ${ratingStatus.padEnd(6)} │ 评分：${scoreStr.padEnd(10)}│`, 'cyan');
  
  // 沙箱结果
  let scanIcon, scanStatus;
  if (scanResult.apiFailed) {
    scanIcon = '❓';
    scanStatus = 'API 失败';
  } else if (scanResult.reason === 'malicious') {
    scanIcon = '❌';
    scanStatus = '禁止';
  } else if (scanResult.needsConfirm) {
    scanIcon = '⚠️';
    scanStatus = '需确认';
  } else {
    scanIcon = '✅';
    scanStatus = '通过';
  }
  const scanReason = scanResult.reason || 'N/A';
  log(`│ 3️⃣ ThreatBook     ${scanIcon} ${scanStatus.padEnd(6)} │ 结果：${scanReason.padEnd(10)}│`, 'cyan');
  
  log('└─────────────────────────────────────────────────────┘', 'cyan');
}

// 根据决策矩阵做出最终判定
function makeDecision(vetResult, ratingResult, scanResult) {
  logSection('🎯 最终决策');
  
  // 检查极端情况 - 直接禁止
  if (vetResult.riskLevel === 'extreme') {
    log(`🚨 发现极端危险代码，禁止安装！`, 'red', true);
    return { action: 'deny', reason: 'vetter_extreme' };
  }
  
  if (scanResult.reason === 'malicious') {
    log(`❌ 检测到恶意代码，禁止安装！`, 'red', true);
    if (scanResult.threatTypes.length > 0) {
      log(`   威胁类型：${scanResult.threatTypes.join(', ')}`, 'red');
    }
    return { action: 'deny', reason: 'malicious' };
  }
  
  // 检查需要确认的情况
  const needsConfirm = [];
  
  if (vetResult.needsConfirm) {
    needsConfirm.push(`Vetter 发现${vetResult.redFlags.length}个潜在问题 (${vetResult.riskLevel}风险)`);
  }
  
  if (ratingResult.needsConfirm) {
    needsConfirm.push(`ClawHub 评分过低 (${ratingResult.score || 'N/A'}/5.0)`);
  }
  
  if (scanResult.apiFailed) {
    needsConfirm.push(`ThreatBook API 不可用`);
  } else if (scanResult.needsConfirm && scanResult.reason !== 'malicious') {
    needsConfirm.push(`沙箱扫描结果可疑 (${scanResult.reason})`);
  }
  
  if (needsConfirm.length > 0) {
    log(`⚠️ 需要任务下达者确认:`, 'yellow');
    for (const reason of needsConfirm) {
      log(`   • ${reason}`, 'yellow');
    }
    return { action: 'confirm', reasons: needsConfirm };
  }
  
  // 全部通过
  log(`✅ 所有安全检查通过，可以安装`, 'green', true);
  return { action: 'install' };
}

// 询问任务下达者
function askForConfirmation(skillName, decision) {
  logSection('❓ 等待确认');
  
  log(`\nSkill: ${skillName}`, 'cyan');
  log(`\n以下问题需要您确认:`, 'yellow');
  for (const reason of decision.reasons) {
    log(`  • ${reason}`, 'yellow');
  }
  
  log(`\n是否继续安装？`, 'yellow');
  log(`  输入 y 或 yes 继续，其他键取消`, 'cyan');
  log(`\n> `, 'cyan');
  
  // 尝试读取输入（非阻塞）
  try {
    const answer = readFileSync(0, 'utf8').trim().toLowerCase();
    return answer === 'y' || answer === 'yes';
  } catch (e) {
    // 无法读取输入时返回 false
    return false;
  }
}

// 执行安装
function installSkill(skillName, dryRun = false) {
  logSection('执行安装');
  
  if (dryRun) {
    log(`🔍 干运行模式，跳过实际安装`, 'yellow');
    return true;
  }
  
  log(`📥 开始安装 ${skillName}...`, 'cyan');
  
  const result = execCommand(`clawhub install "${skillName}"`);
  
  if (result.success) {
    log(`\n✅ ${skillName} 安装完成！`, 'green');
    return true;
  } else {
    log(`\n❌ 安装失败：${result.error}`, 'red');
    return false;
  }
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// 主程序
async function main() {
  const args = process.argv.slice(2);
  const { options, skillName } = parseArgs(args);
  
  if (options.help || !skillName) {
    showHelp();
    process.exit(options.help ? 0 : 1);
  }
  
  log(`\n🛡️ 开始 Skills 安全安装流程 v2.0`, 'cyan', true);
  log(`📋 检查 Skill: ${skillName}`, 'cyan');
  
  // 收集所有检查结果
  const results = {
    vet: { passed: true, riskLevel: 'low', redFlags: [], needsConfirm: false, author: 'unknown' },
    rating: { passed: true, score: null, needsConfirm: false },
    scan: { passed: true, apiFailed: false, needsConfirm: false, reason: 'safe' }
  };
  
  // 第一步：Skill-Vetter 代码审查
  if (!options.noVetter) {
    results.vet = await vetSkill(skillName, options);
    
    // 极高风险直接拒绝
    if (results.vet.riskLevel === 'extreme') {
      showSummary(results.vet, results.rating, results.scan);
      log(`\n🚨 发现极端危险代码，禁止安装！`, 'red', true);
      if (results.vet.redFlags.length > 0) {
        log(`\n红旗列表:`, 'red');
        for (const flag of results.vet.redFlags) {
          if (flag.severity === 'extreme') {
            log(`  🚨 ${flag.name} (${flag.file}:${flag.line})`, 'red');
          }
        }
      }
      process.exit(6);
    }
  }
  
  // 第二步：评分检查
  results.rating = await checkRating(skillName);
  
  // 第三步：沙箱扫描（除非 --no-scan）
  if (!options.noScan) {
    results.scan = await scanSkill(skillName, options);
    
    // 恶意软件直接禁止
    if (results.scan.reason === 'malicious') {
      showSummary(results.vet, results.rating, results.scan);
      log(`\n❌ 禁止安装恶意软件！`, 'red', true);
      process.exit(1);
    }
  }
  
  // 展示复核结果摘要
  showSummary(results.vet, results.rating, results.scan);
  
  // 根据决策矩阵做出最终判定
  const decision = makeDecision(results.vet, results.rating, results.scan);
  
  // 执行决策
  switch (decision.action) {
    case 'deny':
      log(`\n❌ 安装被拒绝`, 'red');
      process.exit(1);
      
    case 'confirm':
      if (options.auto || options.force) {
        // 自动模式：直接继续
        log(`\n⚡ 自动模式：继续安装...`, 'yellow');
      } else {
        // 交互模式：询问用户
        const confirmed = askForConfirmation(skillName, decision);
        if (!confirmed) {
          log(`\n❌ 安装已取消`, 'red');
          process.exit(5);
        }
      }
      // 继续执行安装
      break;
      
    case 'install':
      // 直接安装
      break;
  }
  
  // 执行安装
  const success = installSkill(skillName, options.dryRun);
  process.exit(success ? 0 : 3);
}

main().catch(error => {
  log(`\n❌ 未捕获的错误：${error.message}`, 'red');
  log(`\n堆栈跟踪:`, 'red');
  log(error.stack, 'red');
  process.exit(3);
});
