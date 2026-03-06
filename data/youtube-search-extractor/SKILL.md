---
name: YouTube Search Extractor
description: YouTube搜索结果视频链接提取器 - 可以搜索特定关键词并提取视频链接
read_when:
  - 需要从YouTube搜索结果中提取视频链接
  - 需要批量获取特定关键词的视频内容
  - 需要自动化处理YouTube搜索和链接提取
metadata: {"clawdbot":{"emoji":"🎥","requires":{"bins":["node","npm"]}}}
allowed-tools: Bash(youtube-search-extractor:*)
---

# YouTube Search Extractor - YouTube搜索结果视频链接提取器

## 功能概述

这是一个用于从YouTube搜索结果中自动提取视频链接的技能。它可以：

1. 使用`agent-browser`工具自动执行YouTube搜索
2. 从搜索结果HTML页面中提取视频链接
3. 过滤和去重视频链接
4. 生成格式化的链接列表

## 安装依赖

### 安装agent-browser（npm方式推荐）

```bash
npm install -g agent-browser
agent-browser install
agent-browser install --with-deps
```

### 从源代码安装

```bash
git clone https://github.com/vercel-labs/agent-browser
cd agent-browser
pnpm install
pnpm build
agent-browser install
```

## 使用方法

### 基本搜索和提取

```bash
# 搜索关键词并保存链接到文件
npm run search -- "关键词" "输出文件名"
```

### 示例：搜索Hydrasynth实战应用视频

```bash
npm run search -- "hydrasynth 实战应用" hydrasynth_links
```

### 直接使用脚本

```bash
cd /Users/happy/.openclaw/workspace/skills/youtube-search-extractor
python3 youtube_search_extractor.py "关键词" "输出文件名"
```

## 文件结构

### 核心文件

- **`youtube_search_extractor.py`** - 主要的搜索和提取脚本
- **`SKILL.md`** - 技能文档
- **`package.json`** - npm项目配置
- **`.clawhub/`** - ClawHub配置目录

### 输出文件

- **`<output_file>.html`** - YouTube搜索结果的HTML页面
- **`<output_file>_links.txt`** - 提取的视频链接列表

## 技术特点

### 🚀 自动化流程
- 使用`agent-browser`进行浏览器自动化
- 模拟真实用户搜索行为
- 智能等待页面加载完成

### 🔍 精准提取
- 使用正则表达式匹配视频链接模式
- 处理相对链接到绝对链接的转换
- 自动去重和链接清理

### 📋 格式化输出
- 清晰的编号列表
- 完整的YouTube URL格式
- 包含搜索时间戳

### ⚡ 高性能
- 并行处理搜索和提取
- 优化的链接匹配算法
- 容错机制保障稳定运行

## 支持的搜索关键词格式

- 英文关键词：`"Hydrasynth practical applications"`
- 中文关键词：`"hydrasynth 实战应用"`
- 混合关键词：`"OpenClaw tutorial 教程"`
- 多关键词搜索：使用空格分隔

## 使用示例

### 1. 搜索OpenClaw相关视频

```bash
npm run search -- "OpenClaw tutorial" openclaw_links
```

### 2. 搜索Hydrasynth实战应用视频

```bash
python3 youtube_search_extractor.py "hydrasynth 实战应用" hydrasynth_links
```

### 3. 搜索特定主题的视频

```bash
cd /Users/happy/.openclaw/workspace/skills/youtube-search-extractor
python3 youtube_search_extractor.py "AI音乐创作" ai_music_links
```

## 配置选项

### 脚本参数

```bash
python3 youtube_search_extractor.py [关键词] [输出文件名] [可选参数]

可选参数：
  --headless          # 无头浏览器模式（默认：启用）
  --wait-time <秒数>   # 页面加载等待时间（默认：5秒）
  --max-links <数量>   # 最大链接数（默认：50个）
  --proxy <地址>       # 使用代理服务器
```

### 配置文件

创建`youtube_search_config.json`配置文件：

```json
{
  "browser": {
    "headless": true,
    "wait_time": 5,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
  },
  "extractor": {
    "max_links": 50,
    "filter_relevance": true
  }
}
```

## 故障排除

### 常见问题

1. **安装依赖失败**
   ```bash
   npm install -g agent-browser --force
   ```

2. **浏览器启动失败**
   ```bash
   agent-browser install --with-deps
   ```

3. **网络连接问题**
   ```bash
   # 使用代理
   python3 youtube_search_extractor.py "关键词" "输出文件名" --proxy "http://localhost:8080"
   ```

### 调试模式

```bash
# 启用详细输出
python3 youtube_search_extractor.py "关键词" "输出文件名" --debug
```

## 扩展功能

### 添加新的搜索模板

在`search_templates`目录中添加搜索模板：

```json
{
  "name": "Hydrasynth Search",
  "keywords": ["hydrasynth", "Hydrasynth", "hydra synth"],
  "description": "搜索Hydrasynth合成器相关的内容",
  "filters": ["hydrasynth"]
}
```

### 自定义提取规则

修改`youtube_search_extractor.py`中的链接匹配模式：

```python
def extract_video_links(html_content):
    patterns = [
        r'href=["\'](/watch\?v=[\w-]+[^"\']*)["\']',
        r'href=["\'](https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+[^"\']*)["\']',
        r'href=["\'](https?://(?:www\.)?youtu\.be/[\w-]+[^"\']*)["\']'
    ]
    # 其他提取逻辑...
```

## 注意事项

### 合法使用
- 请遵守YouTube的服务条款
- 合理使用API，避免过度请求
- 尊重版权，仅供个人学习使用

### 性能优化
- 避免在短时间内进行大量搜索
- 使用适当的等待时间避免被封禁
- 考虑使用代理池分散请求

### 安全注意
- 不在代码中硬编码个人信息
- 定期更新依赖库
- 监控网络连接安全性

## 许可证

本技能采用MIT许可证，可自由使用、修改和分发。
