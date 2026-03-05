---
name: tweet-thread-generator
description: 将技术文章、博客转换为吸引人的 Twitter/X 推文线程，支持多语言，自动添加话题标签。
metadata: {"clawdbot":{"emoji":"🐦","requires":{},"primaryEnv":""}}
---

# Tweet Thread Generator

将技术内容转换为吸引人的 Twitter/X 推文线程。

## 功能

- 📝 自动生成推文线程
- 🏷️ 自动添加热门话题标签
- ✂️ 智能分段
- 🌐 多语言支持
- 📊 字符数自动优化
- 🎯 吸引人的开场白建议

## 使用方法

### 从文本生成

```bash
# 基本用法
tweet-thread-generator "你的技术文章内容"

# 指定主题
tweet-thread-generator "文章内容" --topic "AI"

# 输出格式
tweet-thread-generator "内容" --format thread
```

### 从文件生成

```bash
# 从 Markdown 文件
tweet-thread-generator file.md

# 从 URL
tweet-thread-generator url "https://example.com/article"
```

### 交互模式

```bash
# 启动交互式生成
tweet-thread-generator interactive

# 或简写
tweet-thread-generator -i
```

## 输出示例

```
🧵 关于如何写出更好的代码的 10 个技巧

(1/n)

写代码不仅是完成任务，更是创造艺术品。

以下是我从多年编程经验中总结的 10 条建议👇

(2/n)

1. 先思考，再编码
花时间理解问题再动手，能省下后面几倍的重写时间。

#CodingTips #Programming

(3/n)

2. 命名要有意义
...

---
📝 共 8 条推文
🔥 预计曝光: 10K+
⏱️ 预计发布时间: 5 分钟
```

## 选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--topic` | 主题标签 | 自动检测 |
| `--length` | 线程长度 | auto |
| `--tone` | 语气 (funny/serious/educational) | educational |
| `--format` | 输出格式 (thread/list) | thread |
| `--lang` | 语言 | en |

## 配置

### 默认设置

```bash
# 设置默认主题
tweet-thread-generator config --default-topic "Tech"

# 设置默认语气
tweet-thread-generator config --tone educational

# 设置输出格式
tweet-thread-generator config --format thread
```

### 预设开场白

编辑 `~/.tweet-generator/hooks.txt` 添加自定义开场白：

```
🔥 你绝对想不到...
💡 5 年程序员的经验分享
🧵 一个让你效率翻倍的方法
```

## 使用场景

- 📢 推广技术博客
- 📢 产品发布公告
- 📢 分享学习心得
- 📢 行业见解
- 📢 教程和技巧

## 变现思路

1. **Twitter API 服务** - 提供批量生成和管理
2. **付费模板** - 专业推文模板
3. **代运营服务** - 为企业运营 Twitter
4. **培训课程** - Twitter 增长黑客课程
5. **联盟营销** - 推荐工具和产品

## 安装

```bash
# 无需额外依赖
```

## 示例

### 技术教程

```bash
tweet-thread-generator "如何学习 React" --topic "React" --tone educational
```

### 工具推荐

```bash
tweet-thread-generator "5 个提升效率的开发工具" --topic "DevTools"
```

### 行业观点

```bash
tweet-thread-generator "AI 不会取代程序员，但..." --topic "AI" --tone serious
```
