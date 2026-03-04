# 代码评审参考

> 本目录包含代码评审的检查清单和常见问题参考

## 评审检查清单

### 核心维度 (快速评审)

1. **功能正确性**
   - [ ] 需求符合?
   - [ ] 逻辑正确?
   - [ ] 边界处理?
   - [ ] 错误处理?

2. **代码质量**
   - [ ] SOLID原则?
   - [ ] 命名清晰?
   - [ ] 无重复代码?
   - [ ] 嵌套不深?

3. **安全性**
   - [ ] 无SQL注入?
   - [ ] 无XSS?
   - [ ] 无敏感信息泄露?
   - [ ] 权限控制正确?

4. **性能**
   - [ ] 无N+1查询?
   - [ ] 无内存泄漏?
   - [ ] 有分页?
   - [ ] 避免重复计算?

5. **AI专项**
   - [ ] Prompt注入防护?
   - [ ] Token限制?
   - [ ] 超时降级?
   - [ ] 成本控制?

---

## 常见代码问题

### 安全问题

```javascript
// [X] SQL注入
const query = `SELECT * FROM users WHERE id = ${userId}`;

// [OK] 参数化查询
const query = 'SELECT * FROM users WHERE id = ?';
```

### 性能问题

```javascript
// [X] N+1查询
for (const user of users) {
  const orders = await Order.findByUserId(user.id);
}

// [OK] 批量查询
const users = await User.findAll({ include: [Order] });
```

### 代码质量

```javascript
// [X] 嵌套太深
if (user) {
  if (user.isActive) {
    if (user.hasPermission) {
      // ...
    }
  }
}

// [OK] 早返回
if (!user) return;
if (!user.isActive) return;
if (!user.hasPermission) return;
// ...
```

---

## 参考资源

- [会话持久化规范](../development/references/session-management.md)
