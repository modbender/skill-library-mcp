# WeChat Auto Publisher 使用教程

## 快速开始

### 第一步：配置 API 密钥

在技能包目录创建 `.env` 文件：

```env
# 百炼 API（用于文章生成）
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxx

# 公众号配置（可选，发布功能需要）
WECHAT_APP_ID=wx1234567890
WECHAT_APP_SECRET=abcdef123456
```

**获取百炼 API Key：**
1. 访问 https://bailian.console.aliyun.com/
2. 开通百炼服务
3. 创建 API Key

### 第二步：测试运行

```bash
cd ~/.openclaw/workspace/ai-company/products/wechat-auto-publisher-skill/scripts
node index.js monitor
```

看到热点列表即表示正常工作。

### 第三步：生成第一篇文章

```bash
node index.js generate 1
```

检查 `drafts/` 目录下的 Markdown 文件。

---

## 详细使用指南

### 1. 热点监控

#### 手动监控
```bash
node index.js monitor
```

#### 监控结果
```
========== 热点监控开始 ==========
时间：2026/3/2 20:00:00
模式：真实数据源
================================

[数据源] 获取微博热搜...
[数据源] 获取知乎热榜...
[数据源] 获取 GitHub Trending...
[数据源] 获取 Hacker News...

共获取 85 条热点
筛选后剩余 23 个相关话题

=== 推荐选题 TOP 10 ===
1. [github] openai/gpt-5 (热度：95)
2. [hackernews] New AI breakthrough (热度：92)
...
```

#### 数据保存位置
- 最新数据：`data/latest_topics.json`
- 历史记录：`data/topics_2026-03-02T12-00-00.json`

### 2. 文章生成

#### 基础用法
```bash
# 生成 1 篇文章
node index.js generate 1

# 生成 3 篇文章
node index.js generate 3
```

#### 生成流程
```
[1/2] 生成文章...
[LLM] 调用百炼 API...
[LLM] 生成完成，共 1523 字

[2/2] 生成备选标题...

========== 文章生成完成 (8.5s) ==========
草稿已保存：2026-03-02T12-05-30_AI大模型新突破.md
```

#### 草稿格式
```markdown
---
title: AI 这波操作，有点东西
altTitles:
  - OpenAI 又整活了
  - 大模型格局要变
topic: OpenAI 发布新模型
source: hackernews
hotValue: 92
createdAt: 2026-03-02T12:05:30Z
status: draft
---

# AI 这波操作，有点东西

最近科技圈又炸了...

---

【备选标题】
1. AI 这波操作，有点东西
2. OpenAI 又整活了
3. 大模型格局要变
```

### 3. 完整流程

```bash
# 监控 + 生成一体化
node index.js full
```

等价于：
1. 先运行 `monitor`
2. 再运行 `generate`

---

## 高级配置

### 修改监控关键词

编辑 `config.js`：

```javascript
topics: {
  keywords: [
    'AI', '人工智能', '大模型', 'GPT',
    '科技', '互联网', '数码',
    // 添加你的关键词
    '区块链', 'Web3', '元宇宙'
  ],
  excludeKeywords: [
    '娱乐', '明星', '八卦'
  ],
  minHotValue: 50
}
```

### 修改文章风格

编辑 `style-guide.md`：

```markdown
## 核心原则
- 不说教，不引导，不规整
- 犀利，有态度，善用对比反讽
- 开头要有吸引力，结尾要留白
```

### 修改文章长度

编辑 `config.js`：

```javascript
content: {
  targetLength: 2000,  // 改为 2000 字
  style: '专业但不失幽默'
}
```

---

## 定时任务设置

### Windows 任务计划程序

1. 按 `Win + R`，输入 `taskschd.msc`
2. 创建基本任务
3. 触发器：每天 9:00 和 18:00
4. 操作：启动程序
   - 程序：`node.exe`
   - 参数：`index.js full`
   - 起始位置：脚本目录

### Linux Cron

```bash
# 编辑 crontab
crontab -e

# 添加任务（每天 9:00 和 18:00）
0 9,18 * * * cd /path/to/scripts && node index.js full
```

---

## 常见问题

### Q: 热点获取失败怎么办？

A: 检查网络连接，部分数据源可能需要代理。程序会自动使用备用数据。

### Q: 文章生成太慢？

A: AI 生成需要时间，一篇 1500 字文章约 8-15 秒。可以减少 `maxTokens` 加快速度。

### Q: 生成的内容质量不高？

A: 
1. 检查 `style-guide.md` 是否符合预期
2. 调整 `temperature` 参数（0.5-0.8）
3. 在 `config.js` 中修改 prompt

### Q: 如何发布到公众号？

A: 
1. 配置 `.env` 中的公众号密钥
2. 设置 `autoPublish: true`
3. 或手动复制草稿内容到公众号后台

---

## 最佳实践

1. **人工审核** - 测试阶段建议关闭自动发布
2. **每日限量** - 建议每天不超过 3 篇，避免被限流
3. **内容抽查** - 定期检查生成质量，优化 prompt
4. **热点时效** - 热点监控频率建议 4-6 小时一次
5. **风格统一** - 保持写作风格一致，建立品牌调性

---

## 技术支持

遇到问题可以：
1. 检查 `logs/` 目录下的日志文件
2. 查看 `data/` 目录下的数据文件
3. 运行 `node test.js` 进行诊断测试

---

## 更新日志

### V1.0 (2026-03-02)
- ✅ 热点监控（6 个平台）
- ✅ AI 文章生成
- ✅ 草稿管理
- ✅ 配置化设计
- ⏳ 自动发布（待实现）