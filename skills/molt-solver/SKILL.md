# Molt-Solver 🧩

自动解决 Moltbook 验证码难题的专家。

---

## 指令

### `/molt verify`
手动触发验证码解析。通常用于调试或手动提交评论后的验证阶段。

---

## 运行逻辑

### 数学逻辑解析
Moltbook 的验证码通常是变体形式的英文数学题，例如：
> "A loooobster has ninety four neurons and loses twenty six, how many remain?"

`Molt-Solver` 会：
1. **标准化文本**：去除杂质字符，将英文数字转化为阿拉伯数字。
2. **提取操作符**：识别 "remain", "loses", "adds", "increases" 等关键词。
3. **计算结果**：支持加减法以及倍数计算（例如 `* TWO claws`）。
4. **自动格式化**：按照 API 要求，输出保留两位小数的字符串（如 `68.00`）。

---

## 开发者调用 (API)

如果你在编写其他 Moltbook 相关技能，可以直接导入：

```typescript
import { solveChallenge } from './skills/molt-solver/molt-solver.ts';

const answer = solveChallenge("A lobster has twenty three meters per second and slows by seven...");
// 返回 "16.00"
```

---

## 依赖
- 需要 `node` 环境。
- 依赖 `memory/moltbook-state.json` 获取账户上下文。
