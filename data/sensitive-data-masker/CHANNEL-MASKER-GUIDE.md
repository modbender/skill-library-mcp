# Channel 级敏感信息脱敏指南

在 Channel 消息接收时脱敏，维护 7 天临时映射表，本地可还原敏感数据。

---

## 🎯 核心思路

### 问题

- ❌ 直接发送敏感信息给 API 不安全
- ❌ 完全脱敏后本地无法使用敏感数据

### 解决方案

```
用户消息 → Channel 接收 → 脱敏 + 建立映射 → 脱敏消息给 API（安全）
                                    ↓
                            本地映射表（7 天）
                                    ↓
                         需要时还原敏感数据执行任务
```

---

## 📋 工作流程

### 1️⃣ 消息接收时脱敏

**用户发送**：
```
我的 password=MySecret123，帮我配置数据库
```

**Channel 接收后**：
```python
# 脱敏
masked_text = "[PASSWORD:f2ae1ea6d8ecb228]，帮我配置数据库"

# 建立映射
mapping = {
    "f2ae1ea6d8ecb228": {
        "original": "password=MySecret123",
        "expires_at": "2026-03-10"  # 7 天后过期
    }
}
```

**发送给 API**：
```
[PASSWORD:f2ae1ea6d8ecb228]，帮我配置数据库
```

---

### 2️⃣ 本地还原敏感数据

**任务执行前**：
```python
# 从映射表还原
original = mapping_store.get_original("f2ae1ea6d8ecb228")
# 返回："password=MySecret123"

# 还原消息
restored = "password=MySecret123，帮我配置数据库"
```

**执行任务**：
```bash
# 使用还原后的敏感数据
ssh root@host "echo 'password=MySecret123' > /etc/config"
```

---

## 🚀 快速开始

### 安装

技能已安装在：
```
/home/subline/.openclaw/workspace/skills/sensitive-data-masker/
```

### 测试

```bash
# 测试脱敏和还原
python3 sensitive-channel-masker.py test "我的 password=MySecret123"

# 输出
原始消息：我的 password=MySecret123
脱敏后：我的 [PASSWORD:f2ae1ea6d8ecb228]
还原后：我的 password=MySecret123
✅ 还原成功！
```

---

## 📊 查看映射表

### 统计信息

```bash
python3 sensitive-channel-masker.py stats
```

**输出**：
```
📊 敏感数据映射统计:
  总数：3
  TTL: 7 天
  即将过期（24h 内）: 0

  按类型:
    - password: 1
    - api_key: 1
    - db_connection: 1
```

### 映射表文件

**位置**: `~/.openclaw/data/sensitive-masker/sensitive-mapping.json`

**内容**：
```json
{
  "f2ae1ea6d8ecb228": {
    "original": "password=MySecret123",
    "data_type": "password",
    "created_at": "2026-03-03T16:17:49",
    "expires_at": "2026-03-10T16:17:49",
    "usage_count": 1
  }
}
```

---

## 🔧 配置选项

**文件**: `~/.openclaw/data/sensitive-masker/config.json`

```json
{
  "enabled": true,
  "ttl_days": 7,        // 映射表保留天数
  "auto_cleanup": true, // 自动清理过期数据
  "log_enabled": true   // 启用日志
}
```

### 修改 TTL

```bash
# 编辑配置文件
nano ~/.openclaw/data/sensitive-masker/config.json

# 改为 14 天
{
  "ttl_days": 14
}
```

---

## 🛠️ 命令参考

| 命令 | 说明 |
|------|------|
| `test <text>` | 测试脱敏和还原 |
| `stats` | 显示统计信息 |
| `cleanup` | 清理过期数据 |
| `clear` | 清空所有映射 |

### 示例

```bash
# 测试
python3 sensitive-channel-masker.py test "password=123"

# 查看统计
python3 sensitive-channel-masker.py stats

# 清理过期
python3 sensitive-channel-masker.py cleanup

# 清空所有（谨慎）
python3 sensitive-channel-masker.py clear
```

---

## 🔗 OpenClaw 集成

### 方式 1：Channel 插件钩子

在 Feishu Channel 插件中添加：

```python
from sensitive_channel_masker import on_channel_message

# 消息接收时调用
async def on_message(message):
    # 脱敏
    masked = on_channel_message(message)
    
    # 继续处理脱敏后的消息
    await process(masked)
```

### 方式 2：任务执行前还原

```python
from sensitive_channel_masker import before_task_execution

# 任务执行前调用
async def execute_task(context):
    # 还原敏感数据
    restored = before_task_execution(context)
    
    # 使用还原后的数据执行任务
    await run(restored)
```

---

## 📝 使用场景

### 场景 1：配置数据库

**用户**：
```
帮我配置数据库，连接字符串是 mongodb://user:pass@localhost:27017
```

**脱敏后发送给 API**：
```
帮我配置数据库，连接字符串是 [DB_CONNECTION:ad354bc50b8db850]
```

**本地还原并执行**：
```bash
# 还原
export DB_URL="mongodb://user:pass@localhost:27017"

# 配置
echo $DB_URL > /etc/db.conf
```

---

### 场景 2：部署服务

**用户**：
```
用 password=DeployPass123 这个密码部署服务
```

**脱敏后**：
```
用 [PASSWORD:f2ae1ea6d8ecb228] 这个密码部署服务
```

**本地还原**：
```bash
# 还原密码
DEPLOY_PASS="DeployPass123"

# 部署
./deploy.sh --password "$DEPLOY_PASS"
```

---

### 场景 3：API 调用

**用户**：
```
使用 sk-1234567890abcdefghijklmnop 调用 API
```

**脱敏后发送给大模型**：
```
使用 [API_KEY:967706960a0752e1] 调用 API
```

**大模型返回**：
```
已使用 [API_KEY:967706960a0752e1] 完成调用
```

**本地还原显示**：
```
已使用 sk-1234567890abcdefghijklmnop 完成调用
```

---

## 🔐 安全特性

### 1️⃣ 映射表保护

- ✅ 文件权限：600（仅所有者可读写）
- ✅ 存储位置：`~/.openclaw/data/`（本地）
- ✅ 自动过期：7 天后自动删除
- ✅ 使用计数：追踪访问次数

### 2️⃣ 脱敏标记

- ✅ 唯一标识符：16 位哈希
- ✅ 不可逆：无法从标记反推原始数据
- ✅ 类型标记：[PASSWORD:xxx]、[API_KEY:xxx]

### 3️⃣ 数据生命周期

```
创建 → 使用 → 过期 → 删除
       ↑
   7 天 TTL
```

---

## ⚠️ 注意事项

### 1️⃣ 映射表备份

```bash
# 定期备份
cp ~/.openclaw/data/sensitive-masker/sensitive-mapping.json \
   ~/backup/mapping-$(date +%Y%m%d).json
```

### 2️⃣ 清理策略

```bash
# 每天清理过期数据
0 2 * * * python3 sensitive-channel-masker.py cleanup
```

### 3️⃣ 安全警告

- ⚠️ 不要将映射表文件复制到不安全的机器
- ⚠️ 定期清理不再需要的敏感数据
- ⚠️ 映射表泄露 = 敏感数据泄露

---

## 📊 性能影响

| 操作 | 延迟 | 说明 |
|------|------|------|
| **脱敏** | < 1ms | 正则匹配 |
| **还原** | < 1ms | 哈希查找 |
| **存储** | < 5ms | JSON 写入 |
| **清理** | < 10ms | 过期检查 |

---

## 🎯 最佳实践

### 1️⃣ 配置建议

```json
{
  "ttl_days": 7,        // 根据业务需求调整
  "auto_cleanup": true, // 始终启用
  "log_enabled": true   // 生产环境启用
}
```

### 2️⃣ 监控

```bash
# 每天检查统计
python3 sensitive-channel-masker.py stats

# 监控即将过期的数据
# 如果很多，考虑延长 TTL
```

### 3️⃣ 审计

```bash
# 查看脱敏日志
cat ~/.openclaw/data/sensitive-masker/masker.log

# 检查敏感数据使用情况
# usage_count 字段显示使用次数
```

---

## 🔄 版本历史

### v1.0 (2026-03-03)
- 初始版本
- Channel 级脱敏
- 7 天临时映射表
- 自动过期清理
- 统计和监控

---

*最后更新：2026-03-03*
