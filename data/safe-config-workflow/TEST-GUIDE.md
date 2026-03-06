# Config Manager Skill 测试指南

## 测试目标

验证配置修改标准化流程的有效性，确保：
1. doctor --fix 能正确检测并修复配置错误
2. 热重载机制正常工作
3. Gateway 状态验证可靠
4. 排障流程在失败时可用

## 测试环境准备

```bash
# 1. 备份当前配置（安全起见）
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.test.backup

# 2. 确认 Gateway 当前状态正常
openclaw gateway status
# 预期：Runtime: running, RPC probe: ok
```

## 测试用例

### 测试 1：安全配置修改（无错误）

**目的：** 验证热重载正常工作

**步骤：**
```bash
# 1. 修改一个安全的配置项（比如添加注释或调整格式）
nano ~/.openclaw/openclaw.json

# 2. 运行 doctor 检查
openclaw doctor --fix

# 3. 等待热重载
sleep 3

# 4. 验证 Gateway 状态
openclaw gateway status
```

**预期结果：**
- doctor 输出：无问题
- Gateway 状态：running

---

### 测试 2：故意制造配置错误

**目的：** 验证 doctor --fix 能检测并修复错误

**步骤：**
```bash
# 1. 故意添加一个无效配置项
nano ~/.openclaw/openclaw.json
# 添加：
# "channels": {
#   "telegram": {
#     "streaming": "invalid_value_test"
#   }
# }

# 2. 运行 doctor 检查
openclaw doctor --fix

# 3. 查看 doctor 输出
# 应该显示修复了什么

# 4. 对比备份
diff ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak

# 5. 验证 Gateway 状态
openclaw gateway status
```

**预期结果：**
- doctor 输出：修复了 channels.telegram.streaming 字段
- diff 显示：从 "invalid_value_test" 改回 "off"（或删除）
- Gateway 状态：running

---

### 测试 3：关键配置错误（Gateway 启动失败）

**⚠️ 警告：这会导致 Gateway 暂时无法运行，仅用于测试排障流程！**

**目的：** 验证 Gateway 失败后诊断命令仍可用，排障流程有效

**步骤：**
```bash
# 1. 备份当前配置
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.critical.backup

# 2. 故意修改关键配置（比如改端口为已占用的）
nano ~/.openclaw/openclaw.json
# 修改：
# "gateway": {
#   "port": 18789  # 改成已占用的端口，或者改一个无效值
# }

# 3. 运行 doctor 检查
openclaw doctor --fix
# 可能检测不出端口冲突

# 4. 强制 Gateway 重新加载（或重启）
openclaw gateway restart

# 5. 验证 Gateway 状态（应该失败）
openclaw gateway status
# 预期：Runtime: not running 或 RPC probe: failed

# 6. 查看日志
openclaw logs --follow
# 应该显示具体错误原因

# 7. 手动修复配置
nano ~/.openclaw/openclaw.json
# 改回正确的端口

# 8. 再次启动
openclaw gateway restart

# 9. 再次验证
openclaw gateway status
# 预期：Runtime: running, RPC probe: ok
```

**预期结果：**
- Gateway 启动失败后，诊断命令（doctor、logs、status）仍可用
- 日志显示具体错误原因
- 手动修复后 Gateway 恢复正常

---

### 测试 4：反馈策略验证

**目的：** 验证两种反馈策略（小问题自己学，重要问题反馈用户）

**步骤：**
```bash
# 1. 小问题测试（拼写错误）
# 修改一个明显的拼写错误，看是否自动修复并记录

# 2. 重要配置测试（影响功能）
# 修改渠道配置，看是否反馈用户并说明影响
```

**预期结果：**
- 小问题：自动修复，记录到 MEMORY.md，不麻烦用户
- 重要问题：反馈用户，说明影响，记录到 MEMORY.md

---

## 测试结果记录

### 测试日期

YYYY-MM-DD

### 测试者

主人 / AI 助手

### 测试用例结果

| 测试用例 | 预期结果 | 实际结果 | 状态 |
|---|---|---|---|
| 测试 1：安全配置修改 | Gateway 正常运行 | | ⬜ 通过 / ⬜ 失败 |
| 测试 2：doctor --fix 修复 | 正确检测并修复 | | ⬜ 通过 / ⬜ 失败 |
| 测试 3：排障流程 | 诊断命令可用，可恢复 | | ⬜ 通过 / ⬜ 失败 |
| 测试 4：反馈策略 | 小问题自学，重要反馈 | | ⬜ 通过 / ⬜ 失败 |

### 发现的问题

- 

### 改进建议

- 

---

## 恢复测试环境

测试完成后，恢复原始配置：

```bash
# 恢复配置
cp ~/.openclaw/openclaw.json.test.backup ~/.openclaw/openclaw.json

# 重启 Gateway
openclaw gateway restart

# 验证状态
openclaw gateway status
```

---

## 注意事项

1. **测试前务必备份配置** — 避免数据丢失
2. **测试 3 会导致 Gateway 暂时不可用** — 选择合适时间测试
3. **记录测试结果** — 用于改进流程
4. **测试后恢复环境** — 不影响正常使用
