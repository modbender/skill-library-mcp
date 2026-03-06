# 创建 GitHub 仓库指南

## 手动创建 GitHub 仓库

由于 GitHub API 速率限制，需要手动创建仓库并发布技能。

### 步骤 1: 创建 GitHub 仓库

1. 访问 https://github.com/new
2. 创建名为 `weather-openmeteo` 的仓库
3. 选择公开仓库
4. 添加 README.md
5. 选择 MIT 许可证

### 步骤 2: 上传文件

使用以下命令上传文件：

```bash
# 初始化 git 仓库
cd ~/.openclaw/workspace/skills/weather-openmeteo
git init
git add .
git commit -m "Initial commit: Weather Open-Meteo skill v1.0.0"

# 添加远程仓库（替换为你的仓库 URL）
git remote add origin https://github.com/yourusername/weather-openmeteo.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

### 步骤 3: 发布到 ClawHub

等待 GitHub API 速率限制重置后，使用：

```bash
clawhub publish ./skills/weather-openmeteo --slug weather-openmeteo --name "Weather Open-Meteo" --version 1.0.0 --tags "weather,openmeteo,powershell,chinese" --changelog "Initial release: Weather query skill optimized for PowerShell environments with Chinese support"
```

### 步骤 4: 验证发布

```bash
# 搜索技能
clawhub search "weather openmeteo"

# 安装技能
clawhub install weather-openmeteo
```

## 替代方案

如果不想创建 GitHub 仓库，可以：

1. 等待 GitHub API 速率限制重置（通常 1 小时后）
2. 使用 ClawHub 的网页界面手动上传
3. 联系 ClawHub 管理员寻求帮助

## 文件清单

确保包含以下文件：

- SKILL.md - 技能描述文件
- README.md - 项目概述
- USAGE.md - 使用指南
- QUICK-REF.md - 快速参考
- weather-en.ps1 - 英文版本脚本
- weather-cn.ps1 - 中文版本脚本
- test-skill.ps1 - 测试脚本
- demo-en.ps1 - 演示脚本

## 注意事项

- 确保所有文件都是 UTF-8 编码
- 检查文件路径是否正确
- 验证 SKILL.md 格式是否正确
- 确保没有包含敏感信息