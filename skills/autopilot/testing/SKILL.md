---
name: 测试策略与实践
description: 指导测试策略制定、用例设计、覆盖率分析，确保代码质量
version: 1.5.0
updated: 2026-01-19
---

# 测试策略与实践 Skill

> 测试不是找bug，是建立信心。本 Skill 帮助你设计和执行有效的测试策略。

## 速查表

| 我想... | 跳转到 |
|---------|--------|
| 了解测试金字塔 | [测试金字塔](#测试金字塔) |
| 写单元测试 | [单元测试](#单元测试) |
| 写集成测试 | [集成测试](#集成测试) |
| 设计测试用例 | [测试用例设计](#测试用例设计) |
| 分析覆盖率 | [覆盖率分析](#覆盖率分析) |
| AI功能测试 | [AI专项测试](#ai-专项测试) |

**测试原则**: 先测核心路径 -> 再测边界情况 -> 最后测异常处理

---

## 关联 Skill

| Skill | 关系 | 说明 |
|-------|------|------|
| development | 协同 | 开发过程中编写测试 |
| code-review | 协同 | 评审时检查测试覆盖 |
| doc-writing | 参考 | 根据需求文档设计测试 |

**工作流**: `development` + `testing` -> `code-review`

---

## 使用场景

- "帮我设计测试用例"
- "这个功能应该测什么"
- "分析一下测试覆盖率"
- "写一下单元测试"
- "这个AI功能怎么测试"

---

## 测试金字塔

```
        /\         E2E测试 (少)
       /  \        - 完整用户流程
      /----\       - 耗时长
     /      \      - 维护成本高
    /--------\     集成测试 (适量)
   /          \    - 模块间协作
  /------------\   - API测试
 /              \  - 数据库交互
/----------------\ 单元测试 (大量)
                   - 函数/类级别
                   - 快速执行
                   - 隔离测试
```

### 各层测试占比建议

| 测试类型 | 占比 | 执行频率 | 维护成本 |
|---------|------|---------|---------|
| 单元测试 | 70% | 每次提交 | 低 |
| 集成测试 | 20% | 每次 PR | 中 |
| E2E测试 | 10% | 每日/发布前 | 高 |

---

## 单元测试

### 基本原则

| 原则 | 说明 |
|------|------|
| **F**ast | 快速执行 (<100ms/个) |
| **I**ndependent | 测试间相互独立 |
| **R**epeatable | 可重复执行 |
| **S**elf-validating | 自动验证结果 |
| **T**imely | 与代码同步编写 |

### 测试结构 (AAA模式)

```javascript
describe('Calculator', () => {
  it('should add two numbers correctly', () => {
    // Arrange (准备)
    const calculator = new Calculator();
    
    // Act (执行)
    const result = calculator.add(1, 2);
    
    // Assert (断言)
    expect(result).toBe(3);
  });
});
```

### 命名规范

```javascript
// 模式: should_[预期行为]_when_[条件]

// [OK] 好的命名
'should return empty array when no items match'
'should throw error when input is null'
'should update user profile when valid data provided'

// [X] 差的命名
'test add'
'works'
'user test'
```

### 常见场景

```javascript
// 1. 正常路径
it('should calculate discount for VIP user', () => {
  const discount = calculateDiscount({ type: 'VIP' });
  expect(discount).toBe(0.2);
});

// 2. 边界情况
it('should handle zero quantity', () => {
  const total = calculateTotal(100, 0);
  expect(total).toBe(0);
});

// 3. 错误处理
it('should throw error for negative price', () => {
  expect(() => calculateTotal(-100, 1)).toThrow('Invalid price');
});

// 4. 异步操作
it('should fetch user data', async () => {
  const user = await fetchUser(1);
  expect(user.name).toBeDefined();
});
```

---

## 集成测试

### 测试范围

| 测试内容 | 示例 |
|---------|------|
| API端点 | POST /api/users请求响应 |
| 数据库操作 | CRUD操作正确性 |
| 外部服务 | 第三方API调用 |
| 模块协作 | Service与Repository协作 |

### API测试模板

```javascript
describe('POST /api/users', () => {
  // 成功场景
  it('should create user with valid data', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({ name: 'Test', email: 'test@example.com' })
      .expect(201);
    
    expect(response.body.data.id).toBeDefined();
  });
  
  // 参数校验
  it('should return 400 when email is invalid', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({ name: 'Test', email: 'invalid' })
      .expect(400);
    
    expect(response.body.code).toBe(10001);
  });
  
  // 业务规则
  it('should return 409 when email already exists', async () => {
    await createUser({ email: 'test@example.com' });
    
    const response = await request(app)
      .post('/api/users')
      .send({ name: 'Test', email: 'test@example.com' })
      .expect(409);
  });
});
```

### 数据库测试

```javascript
describe('UserRepository', () => {
  beforeEach(async () => {
    await db.truncate('users');
  });
  
  afterAll(async () => {
    await db.close();
  });
  
  it('should save and retrieve user', async () => {
    const repo = new UserRepository(db);
    
    await repo.save({ name: 'Test', email: 'test@example.com' });
    const user = await repo.findByEmail('test@example.com');
    
    expect(user.name).toBe('Test');
  });
});
```

---

## 测试用例设计

### 等价类划分

将输入分为有效和无效的等价类：

| 输入 | 有效类 | 无效类 |
|------|-------|-------|
| 年龄 | 1-120 | <=0, >120 |
| 邮箱 | 包含@的有效格式 | 无@, 格式错误 |
| 密码 | 8-20位含字母数字 | <8位, >20位, 纯数字 |

### 边界值分析

| 输入范围 | 测试值 |
|---------|--------|
| 1-100 | 0, 1, 2, 99, 100, 101 |
| 空值 | null, undefined, '', [] |
| 长度限制 | 0, 1, max-1, max, max+1 |

### 测试用例模板

```markdown
## 测试用例: [功能名称]

### 基本信息
| 项目 | 内容 |
|------|------|
| 功能 | [功能描述] |
| 前置条件 | [必要条件] |

### 测试用例列表

| ID | 场景 | 输入 | 预期结果 | 优先级 |
|----|------|------|---------|--------|
| TC-001 | 正常登录 | 正确用户名密码 | 登录成功 | P0 |
| TC-002 | 密码错误 | 正确用户名+错误密码 | 提示密码错误 | P0 |
| TC-003 | 用户不存在 | 未注册用户名 | 提示用户不存在 | P1 |
| TC-004 | 空用户名 | 空字符串 | 提示必填 | P1 |
| TC-005 | 连续失败锁定 | 5次错误密码 | 账户锁定15分钟 | P1 |
```

---

## 覆盖率分析

### 覆盖率类型

| 类型 | 说明 | 目标 |
|------|------|------|
| 行覆盖 | 执行的代码行 | >80% |
| 分支覆盖 | if/else分支 | >70% |
| 函数覆盖 | 调用的函数 | >90% |
| 语句覆盖 | 执行的语句 | >80% |

### 覆盖率要求

| 代码类型 | 覆盖率要求 | 说明 |
|---------|----------|------|
| 核心业务逻辑 | >80% | 必须保证 |
| 工具函数 | >90% | 纯函数易测 |
| API接口 | 关键路径100% | 至少测正常流程 |
| UI组件 | >60% | 复杂交互需覆盖 |

### 覆盖率盲区

```javascript
// 高覆盖率 != 高质量
// 以下代码虽然覆盖，但测试无效

// [X] 无效测试
it('should work', () => {
  const result = calculate(1, 2);
  expect(result).toBeTruthy();  // 只检查truthy，不验证正确性
});

// [OK] 有效测试
it('should add numbers correctly', () => {
  expect(calculate(1, 2)).toBe(3);
  expect(calculate(-1, 1)).toBe(0);
  expect(calculate(0, 0)).toBe(0);
});
```

---

## AI 专项测试

> AI功能有特殊的测试挑战，需要专门的策略

### AI测试挑战

| 挑战 | 说明 |
|------|------|
| 非确定性 | 同样输入可能不同输出 |
| 评估困难 | 好坏难以量化 |
| 成本高 | 每次调用都有费用 |
| 时间长 | 响应时间不稳定 |

### AI测试策略

#### 1. Mock AI响应

```javascript
// 隔离测试业务逻辑
jest.mock('./aiService');

it('should format AI response correctly', async () => {
  aiService.chat.mockResolvedValue('Hello, User!');
  
  const result = await processAIResponse('Hi');
  
  expect(result.formatted).toBe('Hello, User!');
});
```

#### 2. 集成测试 (有限次数)

```javascript
// 只对核心场景做真实调用
describe('AI Integration (limited)', () => {
  it('should respond to simple query', async () => {
    const response = await aiService.chat('Say hello');
    
    expect(response).toBeTruthy();
    expect(response.length).toBeGreaterThan(0);
  });
});
```

#### 3. Prompt测试

```javascript
describe('Prompt Generation', () => {
  it('should include system instructions', () => {
    const prompt = buildPrompt('user query');
    
    expect(prompt).toContain('You are a helpful assistant');
  });
  
  it('should sanitize user input', () => {
    const prompt = buildPrompt('ignore previous<script>');
    
    expect(prompt).not.toContain('<script>');
  });
});
```

#### 4. 边界测试

```javascript
describe('AI Error Handling', () => {
  it('should handle timeout gracefully', async () => {
    jest.setTimeout(35000);
    
    const result = await callAIWithTimeout('long query', 30000);
    
    expect(result.fallback).toBe(true);
  });
  
  it('should respect token limits', () => {
    const longInput = 'a'.repeat(10000);
    
    expect(() => validateInput(longInput)).toThrow('Input too long');
  });
});
```

### AI测试检查清单

- [ ] Prompt注入防护测试
- [ ] 超时降级测试
- [ ] Token限制测试
- [ ] 内容安全过滤测试
- [ ] 错误处理测试
- [ ] 成本控制测试

---

## 测试最佳实践

### 1. 测试先行 (TDD)

```
红 -> 绿 -> 重构
1. 写失败的测试
2. 写最少代码让测试通过
3. 重构代码
```

### 2. 测试隔离

```javascript
// [X] 测试间依赖
let counter = 0;
it('test 1', () => { counter++; });
it('test 2', () => { expect(counter).toBe(1); });  // 依赖test 1

// [OK] 独立测试
beforeEach(() => { counter = 0; });
it('test 1', () => { counter++; expect(counter).toBe(1); });
it('test 2', () => { counter++; expect(counter).toBe(1); });
```

### 3. 测试数据管理

```javascript
// 使用工厂函数创建测试数据
const createUser = (overrides = {}) => ({
  id: 1,
  name: 'Test User',
  email: 'test@example.com',
  ...overrides
});

it('should update user name', () => {
  const user = createUser({ name: 'Old Name' });
  updateUser(user, { name: 'New Name' });
  expect(user.name).toBe('New Name');
});
```

### 4. 断言精确

```javascript
// [X] 模糊断言
expect(result).toBeTruthy();
expect(users.length).toBeGreaterThan(0);

// [OK] 精确断言
expect(result).toEqual({ id: 1, name: 'Test' });
expect(users).toHaveLength(3);
```

---

## 测试报告模板

```markdown
# 测试报告

## 测试概要
| 项目 | 内容 |
|------|------|
| 功能 | [功能名称] |
| 日期 | YYYY-MM-DD |
| 执行人 | [姓名] |

## 覆盖率
| 类型 | 覆盖率 | 目标 | 状态 |
|------|--------|------|------|
| 行覆盖 | X% | 80% | [OK]/[X] |
| 分支覆盖 | X% | 70% | [OK]/[X] |
| 函数覆盖 | X% | 90% | [OK]/[X] |

## 测试用例执行
| 总数 | 通过 | 失败 | 跳过 |
|------|------|------|------|
| N | N | N | N |

## 失败用例
| ID | 场景 | 失败原因 |
|----|------|---------|
| TC-XXX | ... | ... |

## 风险与问题
- [风险/问题描述]

## 结论
[OK] 测试通过，可以发布
[!] 有风险，需要关注
[X] 测试未通过，需要修复
```

---

## 下一步

测试完成后，提交代码进入 **code-review** skill:
> "帮我review这个代码"
