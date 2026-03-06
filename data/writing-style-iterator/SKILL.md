---
name: writing-style-iterator
description: |
  个性化写作风格记忆系统。在帮用户写作时，加载用户的写作风格
  按用户偏好生成内容，并从用户的修改中自动提取风格规则，不断学习用户的写作风格，越用越好用。
  当用户的请求涉及写作、改写、润色等文字创作场景时自动激活。
---

# Writing Style Iterator — 写作风格记忆系统

你具备写作风格记忆能力。通过 Writing Style Iterator，你能记住用户的写作风格偏好，并随着每次交互变得更懂用户。

## 数据位置

`~/.writing-style-iterator/` 是一个 git 仓库，存放：
- `style.md` — 用户的风格规则文件
- `drafts/` — 草稿快照（用于 diff 和回滚）

首次使用前，如果目录不存在，先初始化：
```bash
mkdir -p ~/.writing-style-iterator/drafts && git -C ~/.writing-style-iterator init && touch ~/.writing-style-iterator/style.md && git -C ~/.writing-style-iterator add . && git -C ~/.writing-style-iterator commit -m "init"
```

## 核心工作流

### 首次生成
```
1. 用户发起写作请求
       ↓
2. 加载style：cat ~/.writing-style-iterator/style.md
       ↓
3. 按 style.md 中的规则生成/修改内容
       ↓
4. 保存草稿（写入用户文件 + 记录快照 + commit）
```

### 迭代修改（核心循环）
```
5. 用户在编辑器中修改（你不参与这一步）
       ↓
6. 用户回来找你（可能带反馈，也可能什么都不说）
       ↓
7. 获取 diff，分析用户改了什么
       ↓
8. 提取风格规则 → 写入 style.md → 通知用户
       ↓
9. 判断是否需要更新内容：
       └─ 新规则明显影响其他部分 → 主动修改并保存
       └─ 用户口头要求了修改 → 照做
       └─ 没什么要改的 → 不必产出新内容
       ↓
      回到步骤 5，直到用户满意
```

## 何时激活

当用户的请求涉及以下任何场景时，加载 style.md 并进入 Writing Style Iterator 工作流：
- 写文章、博客、评论、文案
- 改写、润色、调整语气
- 翻译并调整风格
- 任何「帮我写/改」类请求

## 操作方法

不需要专门的 CLI 工具。所有操作都是文件操作 + git，用 `&&` 链接保证原子性。

### 加载style
```bash
cat ~/.writing-style-iterator/style.md
```

### 保存草稿
```bash
# 将内容写入用户文件，同时记录快照（用绝对路径做目录结构，避免同名冲突）
# 例：/Users/sjm/blog/article.md → ~/.writing-style-iterator/drafts/Users/sjm/blog/article.md
mkdir -p ~/.writing-style-iterator/drafts/$(dirname <用户文件的绝对路径>) && cp <用户文件> ~/.writing-style-iterator/drafts/<用户文件的绝对路径> && git -C ~/.writing-style-iterator add . && git -C ~/.writing-style-iterator commit -m "draft: <文件名>"
```
**每次生成/修改内容都必须做这一步**，否则后续 diff 无法工作。

### 获取用户修改
```bash
diff ~/.writing-style-iterator/drafts/<用户文件的绝对路径> <用户文件>
```
输出用户自上次保存以来的所有变更。

### 更新style
```bash
# 将新内容写入 style.md 并 commit
cat > ~/.writing-style-iterator/style.md << 'EOF'
(更新后的 style.md 完整内容)
EOF
git -C ~/.writing-style-iterator add style.md && git -C ~/.writing-style-iterator commit -m "style: <修改摘要>"
```

### 回滚草稿（AI 改坏了用户文件时）
```bash
git -C ~/.writing-style-iterator checkout HEAD~1 -- drafts/<用户文件的绝对路径> && cp ~/.writing-style-iterator/drafts/<用户文件的绝对路径> <用户文件>
```

### 回滚 style.md
```bash
git -C ~/.writing-style-iterator checkout HEAD~1 -- style.md
```

### 查看版本历史
```bash
git -C ~/.writing-style-iterator log --oneline
```

## 规则提取

### 核心原则：记录+可能的泛化

记录，不强行泛化 你大概总结出规律了可以泛化一下 style.md

### 不同粒度的修改 → 不同类型的记录

| 用户做了什么 | 写入  style.md 的什么位置 |
|---|---|
| 改了一个词/短语 | 忌口清单 → 替换条目 |
| 删掉了某种句式 | 忌口清单 → 禁用结构 |
| 重写了一整段 | 参考示例 → before/after 对比 |
| 加了批注说"太官方了" | 核心原则 → 补充语气要求 |

### 输入来源

1. **diff**：用户对草稿的修改
2. **行内批注**：用户可能在文件里加了标记。没有固定格式——`<!-- 太官方了 -->`、`(这句不好)`、甚至就一个 `?`，你都应该能识别出来
3. **口头反馈**：用户直接和你说的话

### 流程

1. 看 diff + 批注 + 口头反馈
2. 按修改粒度决定写入 style.md 的位置
3. 直接写入 style.md 并 commit
4. 通知用户你做了什么：
   ```
   已更新style：
   。。。
   如需撤回，告诉我即可。
   ```

**不要问 Y/N。** 直接做，然后通知。不满意就回滚。

## 内容更新策略

revise 不一定产出更新后的内容。你需要自己判断：

- **用户改过的部分**：保留，不覆盖
- **用户口头要求了修改**：照做
- **新规则明显影响其他部分**：主动应用
- **没什么要改的**：不需要产出新内容，只更新 style.md 就行

核心目标是**节省用户能量**。能自动做的就自动做。

## 重要原则

1. **节省用户能量，减少交互摩擦**：最高原则。规则直接写入不用问，做完通知就行。
2. **忠实记录，不强行泛化**：用户的修改是什么就记什么。模式是长期积累自然涌现的。
3. **用户不满意可以撤回**：style.md 和草稿都有完整版本历史，随时回滚。
4. **diff 是事实**：diff 告诉你用户实际做了什么，比你的猜测更可靠。
5. **用户的意图高于一切**：用户怎么说就怎么做，Writing Style Iterator 的工作流是辅助而非限制。
