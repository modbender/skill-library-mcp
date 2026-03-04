# 安装指南

## 📦 安装方法

### 方法1：通过ClawdHub安装（推荐）

```bash
# 安装最新版本
clawdhub install claw-security-scanner

# 安装特定版本
clawdhub install claw-security-scanner@1.0.0
```

### 方法2：手动安装

```bash
# 克隆仓库
git clone https://github.com/openclaw-skills/claw-security-scanner.git

# 复制到OpenClaw技能目录
cp -r claw-security-scanner ~/.openclaw/skills/

# 或使用符号链接
ln -s $(pwd)/claw-security-scanner ~/.openclaw/skills/
```

### 方法3：Python包安装

```bash
# 从PyPI安装（如果可用）
pip install claw-security-scanner

# 从GitHub安装
pip install git+https://github.com/openclaw-skills/claw-security-scanner.git
```

## ⚙️ 配置

### OpenClaw集成配置

在 `~/.openclaw/config.json` 中添加以下配置：

```json
{
  "skills": {
    "claw-security-scanner": {
      "enabled": true,
      "config": {
        "autoScan": true,
        "scanOnInstall": true,
        "scanOnUpdate": true,
        "severityThreshold": "medium",
        "reportFormat": "detailed",
        "notifyOnRisk": true,
        "backupBeforeFix": true,
        "excludePatterns": [
          "node_modules",
          ".git",
          "__pycache__",
          "*.log",
          "*.tmp"
        ]
      }
    }
  }
}
```

### 环境变量配置

```bash
# 基本配置
export SECURITY_SCANNER_AUTO_SCAN=true
export SECURITY_SCANNER_SEVERITY_THRESHOLD=medium
export SECURITY_SCANNER_REPORT_FORMAT=console

# 高级配置
export SECURITY_SCANNER_NOTIFY_ON_RISK=true
export SECURITY_SCANNER_BACKUP_BEFORE_FIX=true
export SECURITY_SCANNER_EXCLUDE_PATTERNS="node_modules,.git"

# 性能配置
export SECURITY_SCANNER_MAX_MEMORY=1024
export SECURITY_SCANNER_MAX_THREADS=4
export SECURITY_SCANNER_TIMEOUT=300
```

### 配置文件优先级

配置按以下优先级应用（从高到低）：
1. 命令行参数
2. 环境变量
3. OpenClaw配置文件
4. 默认值

## 🔧 验证安装

### 验证命令行工具

```bash
# 检查是否安装成功
security-scan --version

# 或使用Python模块
python -m security_scanner --version

# 或直接运行
python ~/.openclaw/skills/security-scanner/claw_security_scanner.py --version
```

### 测试扫描功能

```bash
# 测试扫描当前目录
security-scan .

# 测试扫描示例技能
security-scan ~/.openclaw/skills/claw-security-scanner

# 测试不同输出格式
security-scan . --format json
security-scan . --format markdown
```

## 🚀 快速配置

### 一键配置脚本

创建 `setup_security_scanner.sh`：

```bash
#!/bin/bash

echo "🔒 设置 Claw Security Scanner"

# 安装
clawdhub install claw-security-scanner || {
    echo "❌ ClawdHub安装失败，尝试手动安装..."
    git clone https://github.com/openclaw-skills/claw-security-scanner.git
    cp -r claw-security-scanner ~/.openclaw/skills/
}

# 创建配置目录
mkdir -p ~/.openclaw/config

# 添加配置
cat > ~/.openclaw/config/security-scanner.json << EOF
{
  "autoScan": true,
  "scanOnInstall": true,
  "scanOnUpdate": true,
  "severityThreshold": "medium",
  "reportFormat": "detailed"
}
EOF

# 测试安装
echo "🧪 测试安装..."
security-scan --version && echo "✅ 安装成功" || echo "❌ 安装失败"

echo "🎉 配置完成！"
```

运行：
```bash
chmod +x setup_security_scanner.sh
./setup_security_scanner.sh
```

## 🔄 更新与维护

### 更新到最新版本

```bash
# 通过ClawdHub更新
clawdhub update claw-security-scanner

# 或手动更新
cd ~/.openclaw/skills/security-scanner
git pull origin main
```

### 卸载

```bash
# 通过ClawdHub卸载
clawdhub uninstall claw-security-scanner

# 或手动卸载
rm -rf ~/.openclaw/skills/security-scanner

# 清理配置
rm -f ~/.openclaw/config/security-scanner.json
```

## 🐳 Docker支持

### Docker镜像使用

```bash
# 拉取镜像
docker pull clawsecurity/scanner:latest

# 运行扫描
docker run -v $(pwd):/skill clawsecurity/scanner security-scan /skill

# 交互式使用
docker run -it -v $(pwd):/skill clawsecurity/scanner bash
```

### Docker Compose配置

创建 `docker-compose.yml`：

```yaml
version: '3.8'
services:
  security-scanner:
    image: clawsecurity/scanner:latest
    volumes:
      - ./skills:/skills
      - ./reports:/reports
    environment:
      - SECURITY_SCANNER_AUTO_SCAN=true
      - SECURITY_SCANNER_SEVERITY=high
    command: security-scan /skills --format json --output /reports/scan.json
```

运行：
```bash
docker-compose up
```

## ☁️ 云环境部署

### AWS Lambda函数

创建 `lambda_function.py`：

```python
import json
from claw_security_scanner import SecurityScanner

def lambda_handler(event, context):
    scanner = SecurityScanner()
    
    # 从S3获取技能文件
    skill_path = '/tmp/skill'
    # ... 下载代码到 skill_path ...
    
    # 运行扫描
    result = scanner.scan_skill(skill_path)
    
    # 返回结果
    return {
        'statusCode': 200,
        'body': json.dumps(result.to_dict())
    }
```

### GitHub Actions集成

创建 `.github/workflows/security-scan.yml`：

```yaml
name: Security Scan
on: [push, pull_request]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install Security Scanner
        run: |
          pip install git+https://github.com/openclaw-skills/claw-security-scanner.git
      
      - name: Run Security Scan
        run: |
          security-scan . --format json --output security-report.json
      
      - name: Upload Security Report
        uses: actions/upload-artifact@v3
        with:
          name: security-report
          path: security-report.json
```

## 📱 移动设备支持

### Termux（Android）

```bash
# 安装依赖
pkg install python git

# 安装扫描器
pip install git+https://github.com/openclaw-skills/claw-security-scanner.git

# 运行扫描
security-scan /path/to/skill
```

### iOS（通过iSH）

```bash
# 安装Python
apk add python3 py3-pip git

# 安装扫描器
pip3 install git+https://github.com/openclaw-skills/claw-security-scanner.git

# 运行扫描
security-scan /path/to/skill
```

## 🔐 安全注意事项

### 权限管理

```bash
# 以非特权用户运行
sudo -u nobody security-scan /path/to/skill

# 限制文件访问
security-scan --chroot /safe/path /path/to/skill

# 使用容器隔离
docker run --read-only -v $(pwd):/skill:ro clawsecurity/scanner security-scan /skill
```

### 网络隔离

```bash
# 离线模式
security-scan --offline /path/to/skill

# 禁用网络
security-scan --no-network /path/to/skill

# 使用代理
export HTTP_PROXY=http://proxy:8080
export HTTPS_PROXY=http://proxy:8080
security-scan /path/to/skill
```

## 🛠️ 故障排除

### 常见安装问题

#### 问题1：命令未找到
```bash
# 检查PATH
echo $PATH

# 添加OpenClaw技能目录到PATH
export PATH="$HOME/.openclaw/skills/security-scanner:$PATH"

# 或创建符号链接
ln -s ~/.openclaw/skills/security-scanner/security-scan /usr/local/bin/
```

#### 问题2：Python依赖错误
```bash
# 安装依赖
pip install -r requirements.txt

# 或使用系统包管理器
# Ubuntu/Debian
sudo apt-get install python3-pip python3-dev

# CentOS/RHEL
sudo yum install python3-pip python3-devel

# macOS
brew install python
```

#### 问题3：权限错误
```bash
# 修复权限
chmod +x ~/.openclaw/skills/security-scanner/claw_security_scanner.py
chmod +x ~/.openclaw/skills/security-scanner/security-scan

# 或使用sudo
sudo security-scan /path/to/skill
```

### 获取帮助

```bash
# 查看帮助
security-scan --help
security-scan -h

# 查看详细文档
man security-scan  # 如果安装了手册页

# 调试模式
security-scan --debug --verbose /path/to/skill

# 查看日志
tail -f ~/.openclaw/logs/security-scanner.log
```

## 📞 支持

如果遇到问题，请：

1. 查看 [FAQ文档](FAQ.md)
2. 检查 [GitHub Issues](https://github.com/openclaw-skills/claw-security-scanner/issues)
3. 在 [Moltbook社区](https://moltbook.com/u/TestClaw_001) 提问
4. 发送邮件到 support@claw-security-scanner.com

---

**安装完成！现在开始保护你的OpenClaw技能吧** 🔒