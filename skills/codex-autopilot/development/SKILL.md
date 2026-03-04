---
name: 开发实现
description: 指导高质量的代码开发，遵循 SOLID 原则，规范的分支管理和提交流程，支持会话持久化与恢复
version: 1.5.0
updated: 2026-01-19
---

# 开发实现 Skill

> 写出可维护、可扩展、可测试的代码。

## 速查表

| 我想... | 跳转到 |
|---------|--------|
| 理解项目结构 | [项目理解](#阶段零项目理解) |
| 组件拆分原则 | [组件拆分](#03-组件拆分原则) |
| 复习 SOLID | [SOLID 原则](#21-solid-原则) |
| 查命名规范 | [命名规范](#22-命名规范) |
| AI 开发规范 | [AI 开发规范](#阶段三ai-开发规范) |
| 分支命名 | [分支管理](#阶段四分支管理) |
| 提交规范 | [Conventional Commits](#阶段五提交规范) |
| 密钥管理 | [密钥管理](#阶段六密钥管理) |
| 更新进度 | [进度追踪](#进度追踪) |
| 生成汇报 | [进度汇报模板](#进度汇报模板) |
| **修复Bug** | [Bug修复](#阶段十bug修复) |
| **文档管理** | [文档管理规范](#阶段十一-文档管理规范) |

**开发流程**: 项目理解 -> 开发前准备 -> 代码编写 -> 提交 -> 评审

---

## 关联 Skill

| Skill | 关系 | 说明 |
|-------|------|------|
| doc-writing | 前置 | 需求文档是开发的输入 |
| doc-review | 前置 | 文档评审通过后才开始开发 |
| code-review | 下一步 | 开发完成后进行代码评审 |

**工作流**: `requirement-discovery` -> `doc-writing` -> `doc-review` -> `development` -> `code-review`

---

## 使用场景

**新功能开发**:
- "帮我实现这个功能"
- "写一个 XXX 的代码"
- "开发 XXX 模块"
- "帮我理解这个项目结构"

**Bug修复** (触发阶段十):
- "帮我修复这个bug"
- "看看这个bug"
- "这个报错怎么解决"
- "这里有个问题"
- "debug一下"
- "排查一下这个问题"

---

## 开发流程

### 阶段零: 项目理解

> **开发前必做**: 先理解项目结构，再动手写代码

#### 0.1 项目结构扫描

在动手写代码前，必须先理解项目:

**检查清单**:
- [ ] 阅读项目 README
- [ ] 了解目录结构约定
- [ ] 查看现有组件/模块
- [ ] 理解命名规范
- [ ] 找到类似功能的参考代码

**触发方式**:
```
"帮我理解这个项目结构"
"扫描一下项目目录"
"这个项目的组件是怎么组织的"
```

#### 0.2 项目结构说明书模板

当用户说"帮我理解项目结构"时，输出以下格式:

```markdown
# 项目结构说明书

## 目录结构
[扫描并列出关键目录]

## 现有组件/模块
| 组件 | 位置 | 职责 |
|------|------|------|
| ... | ... | ... |

## 命名规范
- 文件命名: [如 PascalCase / kebab-case]
- 组件命名: [规范]
- 变量命名: [规范]

## 技术栈
- 框架: [如 React / Vue / Next.js]
- 状态管理: [如 Redux / Zustand]
- 样式方案: [如 CSS Modules / Tailwind]

## 新文件放置建议
- 页面组件放: [路径]
- 通用组件放: [路径]
- 工具函数放: [路径]
- API 调用放: [路径]
```

#### 0.3 组件拆分原则

| 原则 | 说明 | 示例 |
|------|------|------|
| **单一职责** | 一个组件只做一件事 | Button 只负责按钮样式和点击 |
| **合理粒度** | 不要太大也不要太碎 | 50-200 行为宜 |
| **可复用性** | 通用的提取为公共组件 | 放到 components/common |
| **内聚性** | 相关的放在一起 | 组件和它的样式、类型放一起 |
| **遵循约定** | 遵循项目现有结构 | 不要自创新目录 |

**组件拆分决策树**:
```
这段代码应该独立成组件吗?
|-- 会被多处使用? -> [OK] 提取为公共组件
|-- 超过 200 行? -> [OK] 考虑拆分
|-- 有独立的职责? -> [OK] 提取
|-- 只用一次且简单? -> [X] 暂不提取
|-- 拆分后更难理解? -> [X] 保持原状
```

#### 0.4 常见目录结构约定

**前端项目 (React/Vue/Next.js)**:
```
src/
|-- components/          # 通用组件
|   |-- common/          # 基础组件 (Button, Input, Modal)
|   |-- layout/          # 布局组件 (Header, Footer, Sidebar)
|   |-- business/        # 业务组件 (UserCard, OrderList)
|-- pages/               # 页面 (Next.js) 或 views/
|-- hooks/               # 自定义 hooks
|-- utils/               # 工具函数
|-- services/            # API 调用
|   |-- api/
|-- stores/              # 状态管理
|-- types/               # TypeScript 类型
|-- styles/              # 全局样式
```

**后端项目 (Node.js/Express)**:
```
src/
|-- controllers/         # 控制器 (处理请求)
|-- services/            # 业务逻辑
|-- models/              # 数据模型
|-- routes/              # 路由定义
|-- middlewares/         # 中间件
|-- utils/               # 工具函数
|-- config/              # 配置文件
|-- types/               # TypeScript 类型
```

**后端项目 (Python/FastAPI)**:
```
app/
|-- api/                 # API 路由
|   |-- v1/
|-- core/                # 核心配置
|-- models/              # 数据模型
|-- schemas/             # Pydantic schemas
|-- services/            # 业务逻辑
|-- utils/               # 工具函数
|-- main.py
```

#### 0.5 新文件位置决策

创建新文件前，问自己:

| 问题 | 决策 |
|------|------|
| 这是通用的还是特定业务的? | 通用 -> common/，业务 -> business/ |
| 只有当前页面用还是多处用? | 只当前用 -> 页面目录，多处用 -> components/ |
| 现有项目类似文件放在哪? | **遵循现有约定** |
| 是否需要新目录? | 谨慎创建，优先用现有目录 |

---

### 阶段一: 开发前准备

#### 1.1 确认清单
- [ ] 需求文档已评审通过?
- [ ] 技术方案已确认?
- [ ] 接口设计已明确?
- [ ] 验收标准清晰?
- [ ] 项目结构已理解?

#### 1.2 环境准备
- [ ] 开发环境就绪?
- [ ] 依赖安装完成?
- [ ] 数据库/服务可访问?

#### 1.3 任务拆分
- 每任务 1-4 小时
- 可独立测试
- 依赖关系明确

#### 1.4 开发工具（可选）

**端口管理** (多项目开发时推荐):
```bash
# 为当前项目分配端口
/port-allocator

# 查看所有端口分配
/port-allocator list
```

**Skill 权限配置** (避免重复确认命令):
```bash
# 一键授权 development skill 的常用命令
/skill-permissions allow development
```

> 工具来源: [guo-yu/skills](https://github.com/guo-yu/skills)

---

### 阶段二: 代码编写

#### 2.1 SOLID 原则

| 原则 | 说明 | 实践 |
|------|------|------|
| **S** 单一职责 | 一个类/函数只做一件事 | 函数 < 50 行考虑拆分 |
| **O** 开闭原则 | 对扩展开放，对修改关闭 | 使用接口和抽象 |
| **L** 里氏替换 | 子类可替换父类 | 继承不改变父类行为 |
| **I** 接口隔离 | 接口小而专 | 避免臃肿接口 |
| **D** 依赖倒置 | 依赖抽象非具体 | 使用依赖注入 |

#### 2.2 命名规范

| 类型 | 风格 | 示例 |
|------|------|------|
| 类/类型 | PascalCase | `UserService` |
| 函数/变量 | camelCase | `getUserById` |
| 常量 | UPPER_SNAKE | `MAX_RETRY` |
| 数据库表 | snake_case | `user_orders` |
| API 路径 | kebab-case | `/api/user-orders` |

#### 2.3 代码结构

```
函数设计:
- 短小 (< 30 行)
- 只做一件事
- 参数 <= 4 个
- 避免副作用
```

#### 2.4 注释规范

**需要注释**:
- [OK] 复杂业务逻辑
- [OK] 非显而易见的算法
- [OK] TODO / FIXME
- [OK] 公共 API 文档

**不需要**:
- [X] 显而易见的代码
- [X] 用注释解释糟糕命名

#### 2.5 错误处理

```javascript
// [OK] 好的错误处理
try {
  const user = await userService.getById(id);
  if (!user) throw new NotFoundError(`User: ${id}`);
  return user;
} catch (error) {
  logger.error('Failed to get user', { id, error });
  throw error;
}

// [X] 差的错误处理
try {
  return await userService.getById(id);
} catch (e) {
  console.log(e);  // 仅打印不处理
}
```

---

### 阶段三: AI 开发规范

#### 3.1 Prompt 管理

```javascript
// [OK] Prompt 版本管理
const PROMPTS = {
  CHAT_V1: `你是一个助手...`,
  CHAT_V2: `你是一个专业助手...`,  // 优化版
};

// 使用配置控制版本
const prompt = PROMPTS[config.chatPromptVersion];
```

#### 3.2 AI 调用最佳实践

```javascript
async function callAI(input) {
  // 1. 输入校验
  if (!input || input.length > MAX_INPUT_LENGTH) {
    throw new ValidationError('Invalid input');
  }
  
  // 2. 限流检查
  await rateLimiter.check(userId);
  
  // 3. 调用 AI
  try {
    const result = await aiService.chat({
      prompt: SYSTEM_PROMPT,
      message: sanitize(input),  // 防 Prompt 注入
      maxTokens: 1000,
      timeout: 30000,
    });
    
    // 4. 内容安全检查
    if (await contentFilter.isUnsafe(result)) {
      return { error: 'Content blocked' };
    }
    
    // 5. 记录用量
    await tokenUsage.record(userId, result.tokensUsed);
    
    return result;
  } catch (error) {
    // 6. 降级处理
    if (error.code === 'TIMEOUT' || error.code === 'SERVICE_UNAVAILABLE') {
      return fallbackResponse();
    }
    throw error;
  }
}
```

#### 3.3 Token 成本控制

```javascript
// 缓存相似请求
const cacheKey = hashInput(input);
const cached = await cache.get(cacheKey);
if (cached) return cached;

// 限制输出长度
const result = await ai.chat({ maxTokens: 500 });

// 用户配额
const usage = await getMonthlyUsage(userId);
if (usage > USER_MONTHLY_LIMIT) {
  throw new QuotaExceededError();
}
```

---

### 阶段四: 分支管理

#### 4.1 分支命名

| 类型 | 格式 | 示例 |
|------|------|------|
| 主分支 | `main` | `main` |
| 功能 | `feature/xxx` | `feature/user-login` |
| 修复 | `fix/xxx` | `fix/login-error` |
| 热修复 | `hotfix/xxx` | `hotfix/security` |

#### 4.2 工作流 (小团队)

```
main ------*------------*------
            \          /
develop -----*----*---*---*----
              \   |       
feature -------*--+       
```

1. 从 develop 创建功能分支
2. 开发完成提 PR
3. 合并回 develop
4. 定期发布到 main

---

### 阶段五: 提交规范

#### 5.1 Conventional Commits

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### 5.2 Type 类型

| Type | 说明 |
|------|------|
| `feat` | 新功能 |
| `fix` | 修复 |
| `docs` | 文档 |
| `style` | 格式 |
| `refactor` | 重构 |
| `perf` | 性能 |
| `test` | 测试 |
| `chore` | 构建/工具 |

#### 5.3 示例

```bash
# [OK] 好的提交
feat(user): add registration API

- Add POST /api/users
- Add email validation

Closes #123

# [X] 差的提交
fix bug
update
```

---

### 阶段六: 密钥管理

#### 6.1 规范

```bash
# [X] 永远不要
API_KEY="sk-xxx..."  # 硬编码在代码里
git add .env         # 提交密钥文件

# [OK] 正确做法
# 1. 使用环境变量
const apiKey = process.env.API_KEY;

# 2. .gitignore 添加
.env
.env.local
*.key

# 3. 使用密钥管理服务
# - AWS Secrets Manager
# - Vault
# - 1Password CLI
```

#### 6.2 .env 示例

```bash
# .env.example (提交这个)
API_KEY=your_api_key_here
DATABASE_URL=your_database_url

# .env (不提交)
API_KEY=sk-real-key-xxx
DATABASE_URL=postgres://...
```

---

### 阶段七: 调试技巧

#### 7.1 日志分级

```javascript
// 按重要性使用不同级别
logger.debug('详细调试信息');      // 开发环境
logger.info('重要业务信息');       // 正常流程
logger.warn('警告但不影响运行');   // 需关注
logger.error('错误需要处理', err); // 必须处理
```

#### 7.2 高效定位问题

```javascript
// 1. 添加请求 ID 追踪
const requestId = uuid();
logger.info('Request start', { requestId, path, params });

// 2. 关键步骤打点
logger.info('Step 1 complete', { requestId, duration: t1 });
logger.info('Step 2 complete', { requestId, duration: t2 });

// 3. 错误包含上下文
try {
  await process(data);
} catch (error) {
  logger.error('Process failed', { 
    requestId, 
    data, 
    error: error.message,
    stack: error.stack 
  });
}
```

---

### 阶段八: 测试要求

#### 8.1 测试金字塔

```
    /\     E2E (少)
   /  \    集成 (适量)
  /    \   单元 (大量)
 /______\
```

#### 8.2 覆盖率要求

| 类型 | 覆盖率 |
|------|--------|
| 核心逻辑 | > 80% |
| 工具函数 | > 90% |
| API | 关键路径 100% |

---

### 阶段九: 提交前自检

#### 代码检查
- [ ] 编译/运行正常
- [ ] 无 lint 错误
- [ ] 无调试代码 (console.log)
- [ ] 无硬编码密钥

#### 功能检查
- [ ] 功能正常工作
- [ ] 边界情况处理
- [ ] 错误情况处理

#### 测试检查
- [ ] 测试通过
- [ ] 新代码有测试
- [ ] 未破坏现有测试

#### 文档检查
- [ ] 必要注释已添加
- [ ] API 文档已更新

---

## 最佳实践

### 渐进式开发
1. Make it work (先跑起来)
2. Make it right (再写对)
3. Make it fast (最后优化)

### 代码审查友好
- 变更集中，不混杂
- PR 描述清晰
- 及时响应评审

---

## 进度追踪

开发过程中，需要持续更新任务进度。

### 使用场景

- "更新一下任务进度"
- "这个任务完成了"
- "生成进度汇报"
- "看看当前进度"

### 进度更新操作

当用户说"更新进度"时，执行以下步骤:

1. **确认任务清单位置** (通常在项目的 docs/ 或根目录)
2. **更新任务状态**
3. **更新进度统计**
4. **记录阻塞问题** (如有)

### 会话持久化（复杂任务）

> 基于 Manus 的 Context Engineering 理念：Context Window = RAM，Filesystem = Disk。

#### 核心理念

```
Context Window = RAM (易失性, 有限)
Filesystem = Disk (持久性, 无限)

→ 重要信息必须写入磁盘
```

#### 自动启用规则
- 硬触发（任一）：Bug修复/调试/排查；研究/对比/方案选型；跨 >=3 文件；外部系统变更（API/DB/第三方）
- 软触发：预计 >30 分钟；任务拆解 >=3 步；需要多轮沟通/确认
- 灰区判断：命中 2 项软触发 -> 直接启用；仅 1 项 -> 询问一次是否启用
- 动态升阶：出现错误/失败尝试，或多次查看/搜索仍未锁定方案 -> 立即启用
- 用户覆盖：用户明确表示"不需要会话记录" -> 跳过

#### 会话文件

| 文件 | 用途 | 更新时机 |
|------|------|---------|
| `task_plan.md` | 阶段、进度、决策 | 完成每个阶段后 |
| `findings.md` | 研究、发现 | 每次重要发现后 |
| `progress.md` | 会话日志、错误 | 整个会话过程中 |

默认项目根目录；如项目已有 `docs/_session/` 规范则使用之。

#### 自动化脚本

```bash
# 初始化三文件
./AIWorkFlowSkill/development/scripts/init-session.sh "任务名"

# 会话恢复（上下文清除后恢复未同步内容）
python3 ./AIWorkFlowSkill/development/scripts/session-catchup.py "$(pwd)"

# 检查任务完成度
./AIWorkFlowSkill/development/scripts/check-complete.sh
```

#### 3-Strike Error Protocol

```
尝试 1: 诊断 & 修复
  → 仔细阅读错误，识别根因，应用针对性修复

尝试 2: 替代方案
  → 同样错误? 尝试不同方法/工具/库
  → 永不重复完全相同的失败操作

尝试 3: 更广泛的反思
  → 质疑假设，搜索解决方案
  → 考虑更新计划

3 次失败后: 升级给用户
  → 解释尝试过什么，分享具体错误，请求指导
```

#### 5-Question Reboot Test

上下文恢复后，验证这 5 个问题能否回答：

| 问题 | 答案来源 |
|------|---------|
| 我在哪? | task_plan.md 中的当前阶段 |
| 我要去哪? | 剩余阶段 |
| 目标是什么? | 计划中的 Goal 声明 |
| 我学到了什么? | findings.md |
| 我做了什么? | progress.md |

#### 2-Action Rule

> 每 2 次查看/浏览/搜索操作后，**立即**将关键发现保存到 findings.md。

这防止视觉/多模态信息丢失。

模板与完整规则见 `AIWorkFlowSkill/development/references/session-management.md`。

### 任务状态标记

| 状态 | 标记 | 说明 |
|------|------|------|
| 待开始 | [ ] | 还没开始 |
| 进行中 | [~] | 正在做 |
| 已完成 | [x] | 做完了 |
| 暂停 | [!] | 有阻塞，暂时停止 |
| 取消 | [-] | 不做了 |

### 进度汇报模板

当用户说"生成进度汇报"时，输出以下格式:

```markdown
# 进度汇报

## 汇报信息
| 项目 | 内容 |
|------|------|
| 汇报日期 | YYYY-MM-DD |
| 汇报周期 | 本周 / 本日 |
| 汇报人 | - |

## 整体进度
| 指标 | 数值 |
|------|------|
| 总任务 | N |
| 已完成 | X (X%) |
| 进行中 | Y |
| 待开始 | Z |

## 本期完成
1. [任务1] - [简要说明]
2. [任务2] - [简要说明]

## 进行中
1. [任务3] - 预计完成时间: [日期]
2. [任务4] - 预计完成时间: [日期]

## 阻塞与风险
| 问题 | 影响 | 需要的支持 |
|------|------|-----------|
| [问题描述] | [影响范围] | [需要谁做什么] |

## 下周计划
1. [计划任务1]
2. [计划任务2]

## 备注
- [其他需要同步的信息]
```

### 快速进度更新

对于日常快速更新，可以使用简化格式:

```markdown
## 进度快报 YYYY-MM-DD

完成:
- [任务]

进行中:
- [任务] - 进度 X%

阻塞:
- [问题] - 需要 [支持]
```

---

## 阶段十: Bug修复

> 修复Bug不只是改代码，更要找到根因、追溯文档、防止再犯。

### 触发方式

当用户说以下任意一种时，进入Bug修复流程:

```
"帮我修复这个bug"
"看看这个bug"
"这个报错怎么解决"
"这里有个问题"
"debug一下"
"排查一下这个问题"
"这个功能不对"
"为什么这里报错"
```

### 会话持久化要求

Bug修复必须启用会话持久化，记录尝试与错误，避免重复失败。模板见 `AIWorkFlowSkill/development/references/session-management.md`。

### 10.1 Bug修复流程

```
Bug报告 -> 复现确认 -> 深层根因分析 -> 文档合规检查 -> 修复方案 -> 开发修复 -> 回归测试 -> 文档反馈
                         |                |
                    找到真正原因      检查是否违反文档
                                          |
                                    如有问题，反馈更新文档
```

### 10.2 深层根因分析

> 表面原因 != 根本原因。不要只修表面，要挖到底。

#### 5 Whys 分析法

持续问"为什么"直到找到根本原因:

```
问题: 用户登录失败
|-- Why 1: 为什么失败? -> Token验证不通过
|-- Why 2: 为什么Token不通过? -> Token已过期
|-- Why 3: 为什么过期? -> 刷新逻辑没执行
|-- Why 4: 为什么没执行? -> 条件判断错误
|-- Why 5: 为什么条件错误? -> 时区处理逻辑与文档不一致 <- 根因!
```

#### 根因分类

| 根因类型 | 说明 | 典型特征 | 后续行动 |
|---------|------|---------|---------|
| **代码bug** | 纯粹的代码逻辑错误 | 明确的代码问题 | 修复代码 |
| **文档未遵守** | 没按文档规范实现 | 代码与文档描述不一致 | 修复代码 + 加强review |
| **文档不清晰** | 文档写得模糊导致误解 | 实现理解有偏差 | 修复代码 + **更新文档** |
| **文档遗漏** | 文档没覆盖这个场景 | 边界情况未定义 | 修复代码 + **补充文档** |
| **设计缺陷** | 架构/设计层面有问题 | 重复类似问题 | 考虑重构 + 记录技术债 |
| **依赖问题** | 第三方/外部依赖导致 | 环境变化触发 | 适配修复 + 监控 |

#### 深层分析检查清单

- [ ] 这个bug是偶发还是必现?
- [ ] 这个bug是个例还是系统性问题?
- [ ] 类似的bug之前出现过吗?
- [ ] 根因是代码问题还是规范/文档问题?
- [ ] 其他地方有同样的隐患吗?

### 10.3 文档合规检查

> 很多Bug的本质是"没按文档做"。修复前先追溯文档。

#### 文档追溯步骤

```
1. 找到相关文档
   - PRD/需求文档
   - 技术方案
   - API设计文档
   - 相关README

2. 对比检查
   - 代码实现 vs 文档描述
   - 边界处理 vs 文档定义
   - 错误处理 vs 文档约定

3. 判定问题类型
   - 代码没按文档做 -> 修正代码
   - 文档描述不清 -> 修正代码 + 更新文档
   - 文档未覆盖 -> 修正代码 + 补充文档
```

#### 文档合规检查表

| 检查点 | 问题 | 结论 |
|--------|------|------|
| 需求文档 | 实现是否符合需求描述? | [OK]/[!]/[X] |
| 技术方案 | 是否按技术方案实现? | [OK]/[!]/[X] |
| API文档 | 接口行为是否符合文档? | [OK]/[!]/[X] |
| 边界定义 | 边界情况是否按文档处理? | [OK]/[!]/[X] |
| 错误处理 | 错误码/提示是否符合约定? | [OK]/[!]/[X] |

#### 常见"文档vs实现"问题

```javascript
// [X] 文档说返回数组，实际返回null
// 文档: 返回用户列表，无数据时返回空数组 []
function getUsers() {
  const users = db.query();
  if (!users.length) return null;  // 违反文档!
  return users;
}

// [OK] 按文档实现
function getUsers() {
  const users = db.query();
  return users || [];  // 符合文档: 返回空数组
}
```

### 10.4 最小改动原则

> 修Bug不是重构的借口。只改必须改的。

| 原则 | 说明 |
|------|------|
| **只改根因** | 只修复导致bug的代码 |
| **不顺便优化** | 看到"不完美"的代码忍住 |
| **不顺便重构** | 想重构另开分支 |
| **控制影响范围** | 改动越少，风险越小 |

#### 改动范围评估

```markdown
## Bug修复影响评估

### 根因定位
- 问题代码位置: [文件:行号]
- 根因描述: [描述]

### 修复方案
- 修改范围: [X个文件，Y行代码]
- 影响功能: [列出可能受影响的功能]

### 风险评估
- [ ] 修改是否最小化?
- [ ] 是否会影响其他功能?
- [ ] 是否需要数据迁移?
```

### 10.5 回归测试

> 修完bug，确保没有引入新问题。

#### 回归测试清单

| 检查项 | 状态 |
|--------|------|
| 原bug已修复 | [ ] |
| 相关功能正常 | [ ] |
| 边界情况测试 | [ ] |
| 未引入新问题 | [ ] |
| 类似场景检查 | [ ] |

#### 回归范围确定

```
修改代码 -> 直接影响的功能 -> 间接依赖的功能
    |            |               |
  必测        必测           抽测
```

### 10.6 文档反馈循环

> 如果根因涉及文档问题，必须更新文档，防止再犯。

#### 何时需要更新文档?

| 情况 | 是否更新文档 | 行动 |
|------|-------------|------|
| 代码bug，文档正确 | [X] 不需要 | 只修代码 |
| 文档描述不清晰 | [OK] 需要 | 修代码 + 澄清文档 |
| 文档遗漏场景 | [OK] 需要 | 修代码 + 补充文档 |
| 文档与实现都需改 | [OK] 需要 | 修代码 + 更新文档 |

#### 文档更新模板

```markdown
## 文档更新记录

### 更新原因
- 关联Bug: [Bug描述]
- 问题: [文档什么地方不清晰/遗漏]

### 更新内容
- 文档位置: [文档路径]
- 原内容: [原描述]
- 新内容: [新描述]

### 更新标记
[v1.x] 根据 Bug#XXX 补充/澄清
```

### 10.7 Bug修复分支与提交规范

#### 分支命名

```
fix/[issue-id]-[description]
例: fix/123-login-token-expire
hotfix/[issue-id]-[description]  # 紧急修复
例: hotfix/456-payment-crash
```

#### 提交规范

```
fix(scope): 简要描述

## 问题描述
[原bug是什么]

## 根因分析
[找到的根本原因]

## 修复方案
[如何修复的]

## 影响范围
[修改了哪些地方，影响哪些功能]

## 文档更新
- [x] 无需更新 / [ ] 已更新 [文档名]

Fixes #123
```

#### 提交示例

```
fix(auth): 修复登录时Token过期判断错误

## 问题描述
用户反馈登录后偶尔Token失效需要重新登录

## 根因分析
时区处理逻辑与文档不一致，导致UTC时间比较错误
- 根因类型: 文档未遵守
- 5 Whys: 时区 -> 比较逻辑 -> 没用UTC -> 与文档约定不符

## 修复方案
统一使用UTC时间戳进行Token过期判断

## 影响范围
- 修改文件: auth/token.js
- 影响功能: 登录、Token刷新

## 文档更新
- [x] 无需更新 (代码未遵守已有文档，非文档问题)

Fixes #123
```

### 10.8 Bug修复自检清单

提交修复前的最终检查:

#### 根因确认
- [ ] 找到了真正的根因，不是表面原因?
- [ ] 确认是代码问题还是文档问题?
- [ ] 类似问题在其他地方检查过了?

#### 修复质量
- [ ] 修复方案是最小改动?
- [ ] 代码符合现有规范 (SOLID、命名等)?
- [ ] 没有引入新的问题?

#### 回归测试
- [ ] 原bug已修复?
- [ ] 相关功能测试通过?
- [ ] 边界情况已覆盖?

#### 文档闭环
- [ ] 如需更新文档，已更新?
- [ ] 提交信息包含根因说明?

---

## 阶段十一: 文档管理规范

> Code Review 和 Bug Fix 产生的文档如何管理。

### 11.1 是否需要存档?

不是所有文档都需要存档。根据情况决定:

| 场景 | 是否存档 | 理由 |
|------|---------|------|
| 小修改的 code review | [X] 不存档 | 信息在 PR 评论里即可 |
| 重要功能的 code review | [OK] 存档 | 留作设计决策参考 |
| 简单 bug 修复 | [X] 不存档 | 信息在 commit message 里 |
| 复杂 bug / 线上问题 | [OK] 存档 | 防止再犯、知识沉淀 |
| 涉及架构决策 | [OK] 存档 | 重要决策要有记录 |

**快速判断**: 问自己"3个月后还需要查这个记录吗?" 如果是，存档。

### 11.2 文档存储位置

```
docs/
├── reviews/              # 代码评审记录
│   └── YYYY-MM-DD-[功能名].md
├── bug-fixes/            # Bug修复记录 (复杂问题)
│   └── YYYY-MM-DD-[问题描述].md
├── decisions/            # 技术决策记录 (ADR)
│   └── YYYY-MM-DD-[决策主题].md
└── ...
```

**或者使用项目已有结构**，遵循项目约定。

### 11.3 文件命名规范

| 类型 | 格式 | 示例 |
|------|------|------|
| Code Review | `review-YYYY-MM-DD-[功能名].md` | `review-2026-01-17-user-login.md` |
| Bug Fix | `bugfix-YYYY-MM-DD-[问题描述].md` | `bugfix-2026-01-17-token-expire.md` |
| 技术决策 | `adr-YYYY-MM-DD-[决策主题].md` | `adr-2026-01-17-auth-method.md` |

**命名原则**:
- 全小写
- 用短横线分隔
- 描述用2-4个单词

### 11.4 文档与代码关联

#### 在文档中引用代码

```markdown
## 关联信息
- PR: #123 或 [链接]
- Issue: #456 或 [链接]
- Commit: abc1234
- 相关文件: `src/auth/token.js`
```

#### 在 commit 中引用文档

```
fix(auth): 修复Token过期判断错误

详见: docs/bug-fixes/bugfix-2026-01-17-token-expire.md

Fixes #123
```

### 11.5 简化版模板

对于简单场景，使用简化版模板:

#### Code Review 简化版

```markdown
# Code Review: [功能名]

**结论**: [APPROVE] / [CHANGES] / [BLOCK]
**日期**: YYYY-MM-DD

## 主要问题
1. [问题1] - [建议]
2. [问题2] - [建议]

## 亮点
- [亮点]
```

#### Bug Fix 简化版

```markdown
# Bug Fix: [问题描述]

**日期**: YYYY-MM-DD
**关联**: Issue #XXX / PR #XXX

## 问题
[一句话描述问题]

## 根因
[一句话描述根因]

## 修复
[一句话描述修复方案]

## 影响
- 修改: [文件]
- 测试: [OK] 通过
```

### 11.6 文档生命周期

| 阶段 | 行动 |
|------|------|
| 创建 | 评审/修复完成时创建 |
| 更新 | 有后续讨论或变更时更新 |
| 归档 | 项目结束或功能下线时归档 |
| 清理 | 过时文档定期清理 (可选) |

### 11.7 何时使用哪个模板?

| 场景 | 使用模板 |
|------|---------|
| 日常小 PR | 不存档，评论即可 |
| 重要功能 PR | Code Review 简化版 |
| 复杂架构 PR | Code Review 完整版 |
| 简单 bug | 不存档，commit message 即可 |
| 复杂 / 线上 bug | Bug Fix 简化版 或 完整版 |

---

## 下一步

开发完成后使用 **code-review** skill:
> "帮我 review 这个代码"
