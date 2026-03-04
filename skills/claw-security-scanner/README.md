# Claw Security Scanner 🔒

**OpenClaw技能安全扫描器 - 保护你的AI助手免受恶意技能侵害**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OpenClaw Compatible](https://img.shields.io/badge/OpenClaw-1.0%2B-green.svg)](https://openclaw.ai)

## 🚨 为什么需要技能安全扫描？

### 背景故事
2026年2月，Moltbook社区发现了一个严重的安全问题：
- 一个伪装成天气技能的凭据窃取者在ClawdHub上被发现
- 它读取用户的 `.env` 文件并将机密发送到远程服务器
- 这个事件获得了4151个点赞，成为社区最关注的话题

**问题**：OpenClaw技能生态系统缺乏安全检查机制，用户容易受到恶意代码侵害。

**解决方案**：Claw Security Scanner - 自动扫描技能文件，检测安全威胁。

## ✨ 核心功能

### 🔍 **凭据泄露检测**
- 检测硬编码的API密钥、密码、访问令牌
- 发现数据库连接字符串、SSH私钥
- 识别AWS、JWT等敏感凭证

### 🦠 **恶意代码检测**
- 识别远程代码执行漏洞
- 检测可疑的文件系统操作
- 发现挖矿脚本、键盘记录器
- 标记可疑的网络请求

### 📦 **依赖安全检查**
- 检查已知漏洞的依赖包
- 验证版本固定安全性
- 分析依赖树风险

### ⚙️ **配置安全评估**
- 扫描.env文件中的硬编码值
- 检查YAML/JSON配置中的敏感信息
- 评估权限设置安全性

### 📊 **风险评估与报告**
- 五级风险评估（严重/高/中/低/信息）
- 多种报告格式（控制台/JSON/Markdown）
- 详细的修复建议

## 🚀 快速开始

### 安装
```bash
# 通过ClawdHub安装（推荐）
clawdhub install claw-security-scanner

# 或手动安装
git clone https://github.com/openclaw-skills/claw-security-scanner.git
cp -r claw-security-scanner ~/.openclaw/skills/
```

### 基本使用
```bash
# 扫描单个技能
security-scan /path/to/skill

# 扫描当前目录
security-scan .

# 生成JSON报告
security-scan /path/to/skill --format json --output report.json

# 详细输出
security-scan /path/to/skill --verbose
```

### Python API
```python
from claw_security_scanner import SecurityScanner

# 创建扫描器
scanner = SecurityScanner()

# 扫描技能
result = scanner.scan_skill("/path/to/skill")

# 生成报告
report = scanner.generate_report(result, format="json")
print(report)

# 检查风险等级
if result.has_critical_or_high():
    print("⚠️  发现严重或高风险问题！")
```

## 📋 使用示例

### 示例1：扫描已安装的技能
```bash
# 扫描Claw Memory Guardian
security-scan ~/.openclaw/skills/claw-memory-guardian

# 扫描Claw Ethics Checker  
security-scan ~/.openclaw/skills/claw-ethics-checker
```

### 示例2：集成到工作流
```bash
# 在CI/CD中自动扫描
security-scan ./my-skill --format json --fail-on critical,high

# 扫描结果作为JSON输出
report=$(security-scan ./my-skill --format json)

# 解析结果
critical_count=$(echo $report | jq '.risk_statistics.critical')
if [ $critical_count -gt 0 ]; then
    echo "发现严重安全问题，停止构建"
    exit 1
fi
```

### 示例3：定期安全检查
```bash
#!/bin/bash
# 安全扫描脚本

SKILLS_DIR="$HOME/.openclaw/skills"
LOG_FILE="$HOME/security-scan.log"

echo "=== 安全扫描报告 $(date) ===" >> $LOG_FILE

for skill in $SKILLS_DIR/*/; do
    skill_name=$(basename $skill)
    echo "扫描: $skill_name" >> $LOG_FILE
    security-scan $skill --format markdown >> $LOG_FILE
    echo "---" >> $LOG_FILE
done
```

## 🛡️ 检测能力详解

### 凭据泄露检测
- **API密钥**: `api_key`, `secret_key`, `access_token`
- **密码**: `password`, `passwd`, `pwd`
- **连接字符串**: `mysql://`, `postgresql://`
- **加密密钥**: SSH私钥、JWT令牌
- **云服务凭证**: AWS、Google Cloud、Azure

### 恶意代码模式
- **代码执行**: `eval()`, `exec()`, `__import__()`
- **系统操作**: `rm -rf`, 文件系统遍历
- **网络活动**: 可疑的webhook、数据外泄
- **挖矿代码**: cryptocurrency、mining相关关键词

### 依赖安全检查
- **漏洞数据库**: 集成已知CVE信息
- **版本分析**: 检查过时版本、漏洞版本
- **许可证检查**: 检测不兼容的许可证

### 配置安全检查
- **环境变量**: 硬编码的敏感值
- **配置文件**: YAML/JSON中的密码、令牌
- **权限设置**: 过度文件系统权限

## 📈 报告系统

### 控制台报告
```
============================================================
Claw Security Scanner 报告
============================================================
技能: test-skill
路径: /path/to/skill
扫描时间: 1.23秒
文件统计: 15/20 个文件已扫描

风险统计:
  CRITICAL  : 2
  HIGH      : 3
  MEDIUM    : 5
  LOW       : 2
  INFO      : 1

⚠️  严重/高风险问题 (5个):
  ● 检测到潜在的凭据泄露: API_KEY
      文件: config.py
      行号: 3
      建议: 移除硬编码的凭据，使用环境变量
...
```

### JSON报告
```json
{
  "skill_name": "test-skill",
  "skill_path": "/path/to/skill",
  "total_files": 20,
  "scanned_files": 15,
  "findings": [
    {
      "id": "cred_abc123",
      "category": "credentials",
      "risk_level": "critical",
      "file_path": "config.py",
      "line_number": 3,
      "description": "检测到潜在的凭据泄露: API_KEY",
      "evidence": "API_KEY = \"sk_test_123...\"",
      "recommendation": "移除硬编码的凭据...",
      "detector_name": "credential_detector",
      "fix_available": true,
      "auto_fixable": false
    }
  ],
  "risk_statistics": {
    "critical": 2,
    "high": 3,
    "medium": 5,
    "low": 2,
    "info": 1
  },
  "has_critical_or_high": true
}
```

### Markdown报告
适用于文档、issue跟踪、团队分享。

## ⚙️ 配置选项

### OpenClaw配置
在 `~/.openclaw/config.json` 中添加：
```json
{
  "securityScanner": {
    "autoScan": true,
    "scanOnInstall": true,
    "scanOnUpdate": true,
    "severityThreshold": "medium",
    "reportFormat": "detailed",
    "notifyOnRisk": true,
    "backupBeforeFix": true,
    "excludePatterns": ["node_modules", ".git", "__pycache__"]
  }
}
```

### 环境变量
```bash
export SECURITY_SCANNER_AUTO_SCAN=true
export SECURITY_SCANNER_SEVERITY=high
export SECURITY_SCANNER_FORMAT=json
```

## 🏗️ 架构设计

### 模块化检测器
```
security-scanner/
├── core/                    # 核心扫描引擎
│   ├── static_analyzer/    # 静态代码分析
│   ├── dependency_checker/ # 依赖安全检查
│   ├── credential_scanner/ # 凭据泄露检测
│   └── risk_assessor/      # 风险评估
├── detectors/              # 检测规则库
│   ├── python_detectors/   # Python代码检测
│   ├── javascript_detectors/ # JS代码检测
│   └── config_detectors/   # 配置文件检测
├── reporting/              # 报告系统
└── cli/                    # 命令行界面
```

### 扩展检测器
```python
from claw_security_scanner import BaseDetector

class CustomDetector(BaseDetector):
    def __init__(self):
        super().__init__("custom_detector", "自定义检测器")
    
    def detect(self, file_path: str, content: str):
        # 实现自定义检测逻辑
        findings = []
        # ... 检测代码 ...
        return findings
```

## 🔧 故障排除

### 常见问题
1. **扫描速度慢**
   ```bash
   security-scan --exclude node_modules --fast-mode
   ```

2. **内存不足**
   ```bash
   security-scan --max-memory 512
   ```

3. **误报处理**
   ```bash
   security-scan --ignore-false-positives
   ```

4. **网络依赖**
   ```bash
   security-scan --offline
   ```

### 调试模式
```bash
# 启用详细日志
security-scan --verbose --debug

# 查看检测器状态
security-scan --list-detectors

# 测试特定检测器
security-scan --test-detector credential_detector
```

## 📚 学习资源

### 相关链接
- [Moltbook原帖](https://moltbook.com/p/...) - 引起关注的供应链攻击讨论
- [OpenClaw文档](https://docs.openclaw.ai) - OpenClaw官方文档
- [ClawdHub](https://clawdhub.com) - 技能市场

### 安全最佳实践
1. **永不硬编码凭据** - 使用环境变量或安全存储
2. **定期更新依赖** - 保持依赖包最新安全版本
3. **最小权限原则** - 只授予必要的权限
4. **代码审查** - 重要的技能要进行人工审查
5. **安全扫描** - 集成到开发工作流中

## 🤝 贡献指南

我们欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md)。

### 开发设置
```bash
# 克隆仓库
git clone https://github.com/openclaw-skills/claw-security-scanner.git
cd claw-security-scanner

# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
python test_security_scanner.py

# 运行代码检查
flake8 .
pytest
```

### 添加新检测器
1. 在 `detectors/` 目录创建新的检测器类
2. 实现 `BaseDetector` 接口
3. 编写单元测试
4. 更新文档

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- **Moltbook社区** - 提出了这个重要的安全问题
- **OpenClaw团队** - 创造了优秀的AI助手平台
- **所有贡献者** - 帮助我们改进这个工具

## 📞 支持与反馈

- **问题反馈**: [GitHub Issues](https://github.com/openclaw-skills/claw-security-scanner/issues)
- **安全报告**: security@claw-security-scanner.com
- **社区讨论**: Moltbook @TestClaw_001

---

**记住：安全不是功能，而是基础** 🔒

*使用 Claw Security Scanner，让你的OpenClaw技能更安全*