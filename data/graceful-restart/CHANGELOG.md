# Changelog - graceful-restart

## English

### v1.0.3 (2026-02-22)

#### 🔧 Fix
- Add more metadata fields: runtime, permissions, capabilities, requiredEnvironment

---

### v1.0.4 (2026-02-22)

#### 🔧 Fix
- Add more metadata fields: runtime, permissions, capabilities, requiredEnvironment

---

### v1.0.3 (2026-02-22)

#### 🔧 Fix
- Add more metadata fields: runtime, permissions, capabilities, requiredEnvironment

---

### v1.0.2 (2026-02-22)

#### 🔧 Fix
- Fix SKILL.md: default delay 30s → 10s (matches code)
- Add `requiredBinaries` field to metadata

---

### v1.0.1 (2026-02-22)

#### 🔒 Security Fix
- Use `execFile` with argument arrays to prevent command injection
- Add input validation for `--task` parameter
- Declare `openclaw CLI` dependency in metadata

---

### v1.0.0 (2026-02-22)

#### 🎉 Initial Release
- **Problem:** Gateway restart loses session context
- **Solution:** Auto-restart with self-wakeup using cron + system-event
- **Default delay:** 10 seconds

---

## 中文

### v1.0.2 (2026-02-22)

#### 🔧 修复
- 修复 SKILL.md：默认延迟 30 秒改为 10 秒（与代码一致）
- 添加 `requiredBinaries` 字段到 metadata

---

### v1.0.1 (2026-02-22)

#### 🔒 安全修复
- 使用 `execFile` + 参数数组防止命令注入
- 添加 `--task` 参数输入验证
- 在 metadata 中声明 `openclaw CLI` 依赖

---

### v1.0.0 (2026-02-22)

#### 🎉 初始版本
- **问题**：Gateway 重启后会丢失会话上下文
- **方案**：使用 cron + system-event 实现重启后自唤醒
- **默认延迟**：10 秒
