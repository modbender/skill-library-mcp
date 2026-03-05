# 入门示例 1：你的第一个提示词

## 学习目标
学会使用 Prompt Master 创建一个简单的角色提示词

---

## 场景
你想创建一个英语学习伙伴，帮助你练习英语对话

---

## 步骤 1：使用模板库

### 你的请求
```
"我需要一个英语老师的角色提示词"
```

### Prompt Master 自动路由
→ 检测到关键词："英语老师"、"角色"
→ 调用能力：**模板库**

### 找到匹配模板
从 awesome-chatgpt-prompts 库中找到：

**Spoken English Teacher**
```
I want you to act as a spoken English teacher and improver.
I will speak to you in English and you will reply to me in English
to practice my spoken English. I want you to keep your reply neat,
limiting the reply to 100 words. I want you to strictly correct my
grammar mistakes, typos, and factual errors. I want you to ask me a
question in your reply. Now let's start practicing, you could ask me
a question first. Remember, I want you to strictly correct my grammar
mistakes, typos, and factual errors.
```

---

## 步骤 2：理解模板

### 模板分析
这个模板包含：
- ✅ **角色定义**：spoken English teacher（英语口语老师）
- ✅ **任务描述**：practice spoken English（练习口语）
- ✅ **约束条件**：
  - 回复简洁（100字以内）
  - 纠正语法、拼写、事实错误
  - 每次回复后提问，保持对话
- ✅ **启动指令**："Now let's start practicing"

### 模板质量
- 清晰度：✅ 优秀
- 具体性：✅ 优秀
- 结构性：✅ 良好
- 完整性：✅ 优秀
- 语气：✅ 适合
- 约束：✅ 明确

**评分**：5/6 - Good

---

## 步骤 3：定制模板（可选）

### 如果你想定制
可以调整某些部分：

**定制版**（添加级别和主题）：
```
I want you to act as a spoken English teacher and improver.
I will speak to you in English and you will reply to me in English
to practice my spoken English.

**My level**: [Beginner/Intermediate/Advanced]
**Topics I want to practice**: [daily conversation/business/tech]

I want you to:
1. Keep your reply neat, limiting to 100 words
2. Strictly correct my grammar mistakes, typos, and factual errors
3. Use simpler vocabulary if I'm a beginner
4. Ask me a question in your reply to keep the conversation going

Now let's start practicing. Ask me a question first.
```

**应用技术**：
- 角色扮演 ✅（已有）
- 约束条件 ✅（添加了级别和主题）
- 输出格式化 ✅（添加了编号）

---

## 步骤 4：测试使用

### 直接使用原模板
```
你：[直接粘贴模板]
AI：Hello! How are you doing today?
你：I is good.
AI：❌ Correction: "I am good." (not "I is")
    Now, tell me about your hobbies.
```

### 使用定制版
```
你：[粘贴定制版，填写级别和主题]
AI：Great! Let's practice your business English.
    First question: Tell me about your job.
```

---

## 学习要点

### ✅ 成功要素
1. **明确角色**："I want you to act as..."
2. **清晰任务**：practice spoken English
3. **具体约束**：100字、纠正错误、提问
4. **启动指令**："Now let's start..."

### 🎯 技术总结
这个模板使用了：
- **角色扮演技术**：定义老师角色
- **约束条件技术**：限制长度、要求纠错
- **任务分解技术**：分步骤练习

### 📚 相关学习
如果想深入学习：
- 学习系统 → "角色扮演技术"详解
- 优化器 → "如何改进角色提示词"
- 模板库 → "更多角色模板"

---

## 练习任务

### 任务 1：模板改写
将"英语老师"改写为"中文老师"

<details>
<summary>查看答案</summary>

```
I want you to act as a spoken Chinese teacher and improver.
I will speak to you in Chinese and you will reply to me in Chinese
to practice my spoken Chinese. I want you to keep your reply neat,
limiting the reply to 100 characters. I want you to strictly correct
my grammar mistakes, tones, and word usage errors. I want you to
ask me a question in your reply. Now let's start practicing, you
could ask me a question first.
```
</details>

---

### 任务 2：添加新约束
为英语老师添加一个新约束：只使用简单词汇

<details>
<summary>查看答案</summary>

```
在模板中添加：
"Use simple vocabulary and explain complex words when necessary."
```
</details>

---

### 任务 3：创建新角色
参考英语老师模板，创建一个"写作教练"角色

<details>
<summary>查看答案</summary>

```
I want you to act as a writing coach. I will provide you with my
writing and you will help me improve it. I want you to:

1. Correct my grammar, spelling, and punctuation mistakes
2. Suggest better word choices and sentence structures
3. Point out areas that are unclear or confusing
4. Keep your feedback constructive and encouraging

Limit your feedback to 200 words. Always end with a specific
suggestion for improvement.

Let's start. Send me your first writing sample.
```
</details>

---

## 下一步

恭喜你完成了第一个提示词！

**继续学习**：
- 📖 入门示例2：学习 Few-shot 技术
- 📚 技术详解：角色扮演、Few-shot
- 🎯 进阶示例：创建复杂工作流

**记住**：好提示词 = 明确角色 + 清晰任务 + 具体约束
