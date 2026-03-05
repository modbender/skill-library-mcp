[English](./README.md) | [中文](./README_CN.md)

# memory-distiller 🧠

**OpenClaw 的潜意识——让 Agent 越用越懂你。**

> 你纠正了 AI，它说"明白了"，下次还是同样的错。  
> memory-distiller 解决这个问题。

自动扫描每次对话中的纠正、偏好和顿悟，通过质量门控过滤，将有价值的内容写入持久化记忆文件。你的 Agent 每次用都在变聪明。

---

## 安装

```bash
npx clawhub@latest install memory-distiller
```

零配置。安装后重启 OpenClaw session 即可生效。

---

## 它做什么

| 信号类型 | 触发词 | 行为 |
|---------|--------|------|
| 🔴 纠正 | "不对"、"错了"、"别这样"、"Actually..." | 记录正确做法 |
| 💚 偏好 | "我喜欢"、"以后用"、"不要"、"默认" | 保存你的习惯 |
| 💡 顿悟 | "解决了"、"坑在于"、"关键是"、"原来" | 写入避坑指南 |
| 📌 显式 | "记住这个"、"记一下"、"save this" | 立即执行记录 |

## 质量门控（4条全部通过才记）

1. 24小时后仍有价值
2. 可复用的规则（不是一次性情况）
3. `MEMORY.md` 里没有重复
4. 能指导未来具体行为

## 与 proactive-agent 的分工

> **proactive-agent** = 管家（实时捕获细节、主动行为）  
> **memory-distiller** = 史官（对话后提炼经验、积累智慧）

两者组合，效果最佳：

```bash
npx clawhub@latest install proactive-agent
npx clawhub@latest install memory-distiller
```

---

## 设计理念

灵感来自 [Claudeception](https://github.com/disler/claudeception)（Claude Code 自学习插件），针对 OpenClaw 架构重新设计。

> Agent 不应该被同一个问题绊倒两次。

---

*Designed with 🐝 [claw-multi-agent](https://github.com/zcyynl/claw-multi-agent)*
