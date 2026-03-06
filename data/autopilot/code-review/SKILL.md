---
name: 代码评审
description: 系统性地进行代码评审，检查代码质量、安全性、性能和可维护性
version: 1.5.0
updated: 2026-01-19
---

# 代码评审 Skill

> 代码评审不是找茬，是知识共享和质量保障。

## 速查表

| 评审维度 | 核心检查 |
|---------|---------|
| 功能正确 [!] | 需求符合? 边界处理? 错误处理? |
| 代码质量 [!] | SOLID? 命名? 嵌套深度? |
| 安全性 [!] | SQL注入? XSS? 权限? 敏感信息? |
| 性能 [!] | N+1查询? 内存泄漏? 分页? |
| AI专项 [!] | Prompt注入? Token浪费? 降级? |
| 项目结构 | 文件位置? 组件拆分? 命名一致? |

**快速评审**: 只查 [!] 标记的 5 个核心维度
**评审结论**: [APPROVE] / [CHANGES] / [BLOCK]

---

## 关联 Skill

| Skill | 关系 | 说明 |
|-------|------|------|
| doc-writing | 前置 | 评审时对照需求文档 |
| doc-review | 前置 | 确保需求已评审通过 |
| development | 上一步 | 评审开发完成的代码 |

**工作流**: `requirement-discovery` -> `doc-writing` -> `doc-review` -> `development` -> `code-review`

---

## 使用场景

- "帮我 review 这个代码"
- "检查这个 PR"
- "看看这个实现有没有问题"

---

## 复杂评审的会话记录（可选）

当评审范围较大或涉及多处上下文时，可启用会话记录，避免遗漏与重复。
参考模板: `AIWorkFlowSkill/development/references/session-management.md`

---

## 评审模式

| 模式 | 场景 | 维度 | 时间 |
|------|------|------|------|
| **完整评审** | 核心功能 | 全部 9 个 | 30-60分钟 |
| **快速评审** [!] | 紧急修复 | 5 个核心 | 10-15分钟 |

---

## 评审维度

### 核心维度 (快速评审必查) [!]

#### 1. 功能正确性 [!]

| 检查点 | 常见问题 |
|--------|---------|
| 需求符合? | 遗漏功能 |
| 逻辑正确? | 逻辑漏洞 |
| 边界处理? | 空值、极值未处理 |
| 错误处理? | 异常被忽略 |

```javascript
// [X] 没有处理空值
function getName(user) {
  return user.name.toUpperCase();
}

// [OK] 正确处理
function getName(user) {
  if (!user?.name) return '';
  return user.name.toUpperCase();
}
```

#### 2. 代码质量 [!]

| 检查点 | 常见问题 |
|--------|---------|
| SOLID? | 职责不单一 |
| 命名? | 命名不清晰 |
| 重复? | 代码冗余 |
| 复杂度? | 嵌套太深 |

```javascript
// [X] 嵌套太深
if (user) {
  if (user.isActive) {
    if (user.hasPermission) {
      // do something
    }
  }
}

// [OK] 早返回
if (!user) return;
if (!user.isActive) return;
if (!user.hasPermission) return;
// do something
```

#### 3. 安全性 [!]

| 检查点 | 常见问题 |
|--------|---------|
| SQL 注入? | 拼接 SQL |
| XSS? | 未转义输入 |
| 敏感信息? | 日志泄露密码 |
| 权限? | 越权访问 |

```javascript
// [X] SQL 注入
const query = `SELECT * FROM users WHERE id = ${userId}`;

// [OK] 参数化
const query = 'SELECT * FROM users WHERE id = ?';
db.query(query, [userId]);
```

**危险命令阻止列表** (代码/脚本中禁止出现):

| 类型 | 阻止的命令 | 原因 |
|------|-----------|------|
| 文件操作 | `rm -rf *`, `rm *` | 递归删除，数据丢失风险 |
| 权限提升 | `sudo *`, `chmod 777 *` | 越权操作 |
| 进程操作 | `kill -9 *`, `pkill *` | 影响系统稳定性 |
| 远程执行 | `curl * \| bash`, `wget * \| sh` | 远程代码执行风险 |
| 动态执行 | `eval *`, `exec *` | 代码注入风险 |
| Git 危险操作 | `git push --force *`, `git reset --hard *` | 数据丢失风险 |

> 来源: [guo-yu/skills/skill-permissions](https://github.com/guo-yu/skills)

#### 4. 性能 [!]

| 检查点 | 常见问题 |
|--------|---------|
| N+1 查询? | 循环中查数据库 |
| 内存泄漏? | 未释放资源 |
| 重复计算? | 可缓存的计算 |
| 分页? | 大数据量无分页 |

```javascript
// [X] N+1 查询
for (const user of users) {
  const orders = await Order.findByUserId(user.id);
}

// [OK] 批量查询
const users = await User.findAll({
  include: [{ model: Order }]
});
```

#### 5. AI 代码专项 [!] (AI功能必查)

| 检查点 | 常见问题 |
|--------|---------|
| Prompt 注入? | 用户输入未过滤 |
| Token 浪费? | 无缓存、无限制 |
| 超时处理? | AI 卡死无降级 |
| 成本控制? | 无用户配额 |
| 内容安全? | 无内容审核 |

```javascript
// [X] Prompt 注入风险
const prompt = `分析: ${userInput}`;  // userInput 可能包含恶意指令

// [OK] 输入清理
const sanitizedInput = sanitize(userInput);
const prompt = `分析以下用户提供的文本:\n"""${sanitizedInput}"""`;

// [X] 无降级
const result = await ai.chat(input);

// [OK] 有降级
try {
  const result = await ai.chat(input, { timeout: 30000 });
  return result;
} catch (error) {
  if (error.code === 'TIMEOUT') {
    return fallbackResponse();
  }
  throw error;
}
```

### 扩展维度 (完整评审)

#### 6. 可维护性

| 检查点 | 常见问题 |
|--------|---------|
| 魔法数字? | 硬编码数值 |
| 注释? | 复杂逻辑无说明 |
| 配置分离? | 配置硬编码 |

```javascript
// [X] 魔法数字
if (user.type === 1) {
  discount = 0.2;
}

// [OK] 使用常量
const USER_TYPE = { VIP: 1 };
const VIP_DISCOUNT = 0.2;
if (user.type === USER_TYPE.VIP) {
  discount = VIP_DISCOUNT;
}
```

#### 7. 测试覆盖

| 检查点 | 常见问题 |
|--------|---------|
| 测试存在? | 新代码无测试 |
| 覆盖充分? | 只测正常路径 |
| 测试质量? | 只检查 truthy |

```javascript
// [X] 无效测试
expect(result).toBeTruthy();

// [OK] 有效测试
expect(calculate(1, 2)).toBe(3);
expect(calculate(-1, 1)).toBe(0);
```

#### 8. 兼容性

| 检查点 | 常见问题 |
|--------|---------|
| 向后兼容? | API 破坏性变更 |
| 数据迁移? | 无迁移脚本 |
| 现有功能? | 影响其他模块 |

#### 9. 文档规范

| 检查点 | 常见问题 |
|--------|---------|
| 代码规范? | 风格不一致 |
| 提交规范? | commit 不规范 |
| API 文档? | 新接口未文档化 |

#### 10. 项目结构

| 检查点 | 常见问题 |
|--------|---------|
| 文件位置? | 新文件放错目录 |
| 组件拆分? | 组件过大或过碎 |
| 命名一致? | 不遵循项目命名规范 |
| 复用性? | 重复代码未提取 |
| 目录约定? | 自创目录破坏结构 |

```
# 常见问题示例

[X] 把通用组件放在页面目录
   pages/home/Button.tsx  # 应该放 components/common/

[X] 组件文件超过 500 行
   -> 考虑拆分为更小的组件

[X] 命名风格不一致
   UserCard.tsx / order-list.tsx / productItem.tsx
   -> 统一使用 PascalCase 或 kebab-case

[X] 重复代码
   多个文件有相同的工具函数
   -> 提取到 utils/
```

---

## 评审输出格式

```markdown
# 代码评审报告

## 评审信息
| 项目 | 内容 |
|------|------|
| PR/代码 | [标题] |
| 模式 | 完整/快速 |
| 结论 | [APPROVE] / [CHANGES] / [BLOCK] |

## 维度汇总
| 维度 | 状态 | 问题 |
|------|------|------|
| 功能正确 [!] | [OK]/[!]/[X] | N |
| 代码质量 [!] | [OK]/[!]/[X] | N |
| 安全性 [!] | [OK]/[!]/[X] | N |
| 性能 [!] | [OK]/[!]/[X] | N |
| AI专项 [!] | [OK]/[!]/[X]/N/A | N |

## [BLOCK] 必须修改
1. **[问题]**
   - 位置: `file.js:L10`
   - 问题: [问题描述]
   - 建议: [建议]
   ```javascript
   // 示例代码
   ```

## [WARN] 建议优化
1. **[问题]** - [建议]

## [GOOD] 亮点
- [亮点]

## [?] 疑问
- [需作者解释]
```

---

## 评审结论

| 结论 | 条件 | 行动 |
|------|------|------|
| [APPROVE] | 无阻塞问题 | 直接合并 |
| [CHANGES] | 有问题但不严重 | 修改后合并 |
| [BLOCK] | 严重问题/安全漏洞 | 修改后重新评审 |

---

## 评审原则

### 1. 尊重
- 对事不对人
- 建设性语言
- 假设作者善意

### 2. 具体
- 指出具体位置
- 提供改进建议
- 用代码示例

### 3. 及时
- 及时响应
- 小 PR 优先
- 不拖延

### 4. 学习
- 双向学习
- 表扬亮点
- 虚心请教

---

## 评审语言

```
[X] 把这个改成 xxx
[OK] 考虑是否可以用 xxx? 这样可以...

[X] 这里应该用常量
[OK] 建议提取为常量 `VIP_DISCOUNT`，便于复用和维护

[X] 这个写法有问题
[OK] 这里可能有 null 风险，建议用 `user?.name`
```

---

## 快速评审

时间紧迫时只查 5 个核心维度: 功能正确、代码质量、安全性、性能、AI专项

```markdown
# 快速评审结果
[APPROVE]/[CHANGES]/[BLOCK] [结论]

## 关键问题
1. [问题]

## 下一步
- [行动]
```

---

## 代码修改规范

| 原则 | 说明 |
|------|------|
| **评审输出报告** | 只输出问题和建议，不要重写整个代码文件 |
| **增量修改** | 只修改需要改的部分，使用编辑工具 |
| **测试验证** | 修改后确保测试通过再提交 |

---

## 文档存档决策

评审完成后，决定是否需要存档评审报告:

| 场景 | 是否存档 | 说明 |
|------|---------|------|
| 日常小 PR | [X] 不存档 | 评论在 PR 里即可 |
| 重要功能 | [OK] 存档 | 留作设计决策参考 |
| 涉及架构决策 | [OK] 存档 | 重要决策要有记录 |
| 多轮讨论 | [OK] 存档 | 记录讨论过程和结论 |

**存档位置**: `docs/reviews/review-YYYY-MM-DD-[功能名].md`

**详细规范**: 见 development skill 的 "阶段十一: 文档管理规范"

---

## 完成后

代码评审通过、合并后，一个完整的开发周期结束。

如需开始下一个功能，回到 **requirement-discovery** skill:
> "帮我调研一下这个需求"
