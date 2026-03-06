# 创建 GitHub 仓库说明

由于 GitHub API 速率限制，需要手动创建仓库。

## 步骤

1. 访问 https://github.com/new
2. 创建名为 `weather-openmeteo` 的仓库
3. 选择公开仓库
4. 添加 README.md
5. 选择 MIT 许可证

## 上传文件

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

## 发布到 ClawHub

等待 GitHub API 速率限制重置后：

```bash
clawhub publish ./skills/weather-openmeteo --slug weather-openmeteo --name "Weather Open-Meteo" --version 1.0.0 --tags "weather,openmeteo,powershell,chinese" --changelog "Initial release"
```

## 验证发布

```bash
clawhub search "weather openmeteo"
clawhub install weather-openmeteo
```