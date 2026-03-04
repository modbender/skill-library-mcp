# bilibili-analytics 安装指南

## 安装方法

### 方法1：解压 .skill 文件

```bash
# 1. 下载 bilibili-analytics.skill 文件

# 2. 解压到 skills 目录
cd ~/.openclaw/workspace/skills
unzip /path/to/bilibili-analytics.skill

# 3. 赋予脚本执行权限
chmod +x bilibili-analytics/scripts/*.sh
chmod +x bilibili-analytics/scripts/*.py

# 4. 安装 Python 依赖（可选）
pip install -r bilibili-analytics/requirements.txt 2>/dev/null || true
```

### 方法2：手动复制

```bash
# 复制整个目录
cp -r /path/to/bilibili-analytics ~/.openclaw/workspace/skills/
```

### 方法3：通过 Git

```bash
# 克隆到 skills 目录
cd ~/.openclaw/workspace/skills
git clone https://your-repo/bilibili-analytics.git
```

## 验证安装

```bash
# 检查文件
ls -la ~/.openclaw/workspace/skills/bilibili-analytics/

# 应该看到：
# SKILL.md
# scripts/scrape_videos.sh
# scripts/analyze_data.py
# references/usage-examples.md
```

## 使用方法

### 1. 直接使用脚本

```bash
# 抓取数据
cd ~/.openclaw/workspace/skills/bilibili-analytics
./scripts/scrape_videos.sh "关键词" 5

# 分析数据
python3 scripts/analyze_data.py bilibili_data_*.json
```

### 2. 通过 OpenClaw AI 使用

用户请求示例：
- "帮我搜索B站上关于'原神'的视频"
- "分析B站'AI绘画'话题的热度"

AI 会自动：
1. 读取 SKILL.md
2. 执行抓取脚本
3. 运行分析脚本
4. 生成统计报告

## 依赖要求

- **agent-browser**: 用于浏览器自动化
- **Python 3.6+**: 用于数据分析
- **Bash**: 用于抓取脚本

安装 agent-browser:
```bash
npm install -g agent-browser
agent-browser install
```

## 常见问题

### Q: agent-browser 安装失败？
A: 运行 `agent-browser install --with-deps` 安装系统依赖

### Q: Python 脚本报错？
A: 检查 Python 版本：`python3 --version`，需要 3.6+

### Q: 抓取数据为空？
A: 检查网络连接和页面加载时间，可能需要增加 `--timeout` 参数
