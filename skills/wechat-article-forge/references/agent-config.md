# 智能体配置指南 — Orchestrator Agent Configuration

本文档定义调用 wechat-article-writer 技能的**编排智能体（Orchestrator Agent）**的最佳配置。安装技能后，按此指南配置智能体，实现最大自动化 + 关键人工审核。

---

## 一、核心原则

- **能自动跑的步骤不问人**（调研、初稿、评审、排版、后处理）
- **必须停下来等人的步骤明确标注**（文字预览审核、插图确认、发布确认）
- **语音消息是主要反馈方式** — 智能体必须能处理语音转文字并据此行动
- **状态持久化** — 所有进度写入 `pipeline-state.json`，不依赖会话记忆

---

## 二、Gateway 配置

```yaml
# openclaw config 关键字段
session:
  idleMinutes: 10080        # 7天空闲才重置（文章流程可能跨多天）
  
defaultModel: anthropic/claude-sonnet-4-5   # 日常对话和评审用Sonnet（省钱）
```

**模型策略：**
| 任务 | 模型 | 原因 |
|------|------|------|
| 日常对话、评审 | Sonnet (默认) | 成本低，评审质量够用 |
| 初稿写作、改稿 | Opus (子代理指定) | 创作质量显著更高 |
| 插图生成 | OpenRouter gpt-5-image-mini | article-illustrator 默认 |

---

## 三、AGENTS.md 追加规则

将以下内容追加到编排智能体的 `AGENTS.md`：

```markdown
## 微信公众号文章写作规则

### 自动执行（不问人）
- 选题调研（web_search）
- 撰写大纲
- 生成初稿（spawn Writer 子代理，用 Opus 模型）
- 评审打分（spawn Reviewer 子代理，用 Sonnet 模型）
- 自动修改循环（最多2轮）
- wenyan 排版 + HTML 后处理
- 启动预览服务器

### 必须等人确认
- **文字预览**（步骤9）：发预览链接后等用户反馈，不要自行继续
- **插图生成**（步骤10）：用户明确说"可以了"/"好了"/"生成图片"才执行
- **发布**（步骤13）：始终保存为草稿，用户手动发布

### 用户反馈处理
- 用户可能通过**语音消息**给反馈 — 直接根据转录文字行动
- 用户说"改一下XX" → 直接改，不要确认
- 用户说"不好"/"重写" → 回到步骤4重写
- 用户说"可以了" → 进入下一步
- 用户沉默超过30分钟 → 发一条提醒，不要反复催

### 成本控制
- 插图是最贵的步骤（~$0.50/篇），放在最后
- 不要在被拒绝的草稿上生成插图
- article-illustrator 原样使用，不修改提示词或添加风格前缀

### Pipeline 状态
- 每个主要步骤完成后更新 pipeline-state.json
- 会话重启后先读 pipeline-state.json 恢复进度
- 不要依赖会话记忆来跟踪进度
```

---

## 四、HEARTBEAT.md 追加规则

```markdown
## 文章 Pipeline 检查
每次心跳检查 ~/.wechat-article-writer/drafts/*/pipeline-state.json
- 如果有 phase 不是 "done" 且不是等待人工的阶段 → 继续执行
- 如果 phase 是 "previewing_text" 或 "illustrating" → 不要自动继续，等用户
- 如果 pipeline 超过 24 小时没更新 → 提醒用户
```

---

## 五、SOUL.md 建议追加

```markdown
## 文章写作人格
写文章时切换到"编辑"模式：
- 对文字质量极其严格，不放过任何教材腔/翻译腔/鸡汤腔
- 但对用户反馈高度响应 — 用户说改就改，不要辩解
- 主动提供改进建议，但不强制执行
- 如果用户的意见和评审冲突，以用户意见为准
```

---

## 六、技能依赖清单

安装 wechat-article-writer 前，确保以下技能已安装：

```bash
# 必须
openclaw skill install article-illustrator   # 插图生成
openclaw skill install wechat-publisher      # wenyan-cli 排版

# 推荐
openclaw skill install openai-whisper-api    # 语音转文字（处理用户语音反馈）
```

---

## 七、环境变量

```bash
OPENROUTER_API_KEY=sk-...   # 必须：article-illustrator 图片生成
```

---

## 八、Chrome 浏览器配置（发布用）

```bash
# 启动 Chrome，开启远程调试
DISPLAY=:1 google-chrome-stable \
  --remote-debugging-port=18800 \
  --user-data-dir=/tmp/openclaw-browser2 \
  --no-first-run --disable-default-apps &

# 用户需手动扫码登录 mp.weixin.qq.com
# token 从 URL 中提取，保存到 config.json
```

---

## 九、完整安装检查清单

| # | 检查项 | 命令 |
|---|--------|------|
| 1 | article-illustrator 已安装 | `ls ~/.openclaw/skills/article-illustrator/` |
| 2 | wechat-publisher 已安装 | `which wenyan` |
| 3 | OPENROUTER_API_KEY 已设置 | `echo $OPENROUTER_API_KEY` |
| 4 | Chrome 远程调试可用 | `curl -s http://localhost:18800/json/version` |
| 5 | WeChat 已登录 | 浏览器中访问 mp.weixin.qq.com 检查 |
| 6 | session idle >= 7天 | 检查 OpenClaw gateway 配置 |
| 7 | 默认模型 Sonnet | `openclaw status` |
| 8 | 语音转文字可用 | openai-whisper-api 技能已安装 |

---

## 十、Cron 错误监控

**Cron job 失败是静默的** — 不会主动通知任何人。必须通过以下方式监控：

1. **HEARTBEAT.md 中添加 cron 健康检查**（setup.sh 已自动添加）
2. **Discord delivery target 必须使用 `channel:` 前缀**（e.g. `channel:1234567890`），否则报 "Ambiguous Discord recipient" 并静默失败
3. 如果 `consecutiveErrors >= 2`，禁用该 job 并通知用户

## 十一、常见问题

**Q: 文章流程跑到一半，会话被重置了怎么办？**
A: pipeline-state.json 保存了完整状态。新会话启动后，心跳检查会发现未完成的 pipeline 并恢复。

**Q: 评审分数始终达不到9.5怎么办？**
A: 自动轮次最多2轮，之后转人工。用户的判断优先于自动评分。不要死磕分数。

**Q: 插图风格不满意怎么办？**
A: 重新生成（~$0.50）。但不要修改 article-illustrator 的调用方式，只改内容描述。

**Q: wenyan 输出乱码？**
A: wenyan 输出缺少 `<meta charset="utf-8">`，步骤8会自动注入。如果直接打开 raw.html 会乱码，这是正常的。
