# 代码风格指南

## TypeScript 风格

### 类型定义

- 使用强类型，避免 `any` 类型
- 为复杂类型创建接口或类型别名
- 使用泛型提高代码复用性

### 命名规范

- **接口**：PascalCase，如 `UserInterface`
- **类**：PascalCase，如 `UserService`
- **函数**：camelCase，如 `getUser`
- **变量**：camelCase，如 `userName`
- **常量**：UPPER_CASE，如 `MAX_RETRY_COUNT`
- **私有成员**：下划线前缀，如 `_privateMethod`

### 代码格式

- 缩进：2 个空格
- 行宽：120 字符
- 大括号：与语句同一行
- 分号：必须使用
- 引号：单引号

### 导入顺序

1. 内置模块
2. 第三方模块
3. 本地模块

## ESLint 规则

项目使用以下 ESLint 规则：

- `@typescript-eslint/no-explicit-any`：禁止使用 `any` 类型
- `@typescript-eslint/explicit-function-return-type`：显式函数返回类型
- `@typescript-eslint/no-unused-vars`：禁止未使用的变量
- `no-console`：生产环境禁止使用 console
- `no-debugger`：禁止使用 debugger

## Prettier 配置

项目使用以下 Prettier 配置：

- 缩进：2 个空格
- 行宽：120 字符
- 单引号：true
- 分号：true
- 尾随逗号：es5
- 箭头函数括号：avoid

## 代码注释

### 函数注释

```typescript
/**
 * 获取用户信息
 * @param userId 用户ID
 * @returns 用户信息
 */
async function getUser(userId: string): Promise<User> {
  // 实现
}
```

### 类注释

```typescript
/**
 * 用户服务类
 * 处理用户相关的业务逻辑
 */
class UserService {
  // 实现
}
```

### 模块注释

```typescript
/**
 * 用户模块
 * 包含用户相关的控制器、服务和模型
 */
```

## 最佳实践

1. **可读性**：优先考虑代码可读性
2. **简洁性**：保持代码简洁明了
3. **一致性**：遵循项目的代码风格
4. **可维护性**：编写易于维护的代码
5. **性能**：考虑代码性能影响