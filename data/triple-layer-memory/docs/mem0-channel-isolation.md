# Mem0 频道级命名空间隔离配置

## 概述

为了实现频道级记忆隔离，需要修改 Mem0 插件的 userId 生成逻辑：
- boss 频道：使用主 userId，可以访问全量记忆
- 子频道：使用 `userId::channelKey`，只能访问本频道记忆

## 配置步骤

### 1. 编辑 Mem0 插件

文件位置：`~/.openclaw/extensions/openclaw-mem0/index.ts`

找到 userId 生成逻辑，修改为：

```typescript
// 原代码
const userId = config.userId || "default";

// 修改为
const channelKey = context.channelKey || "boss";
const userId = channelKey === "boss" 
  ? (config.userId || "default")
  : `${config.userId || "default"}::${channelKey}`;
```

### 2. 重启 OpenClaw Gateway

```bash
openclaw gateway restart
```

### 3. 验证

在不同频道测试记忆写入和检索：

```bash
# 在 boss 频道
memory_store("这是 boss 频道的记忆")

# 在子频道（如 ca）
memory_store("这是 ca 频道的记忆")

# 在 boss 频道搜索
memory_search("记忆")  # 应该能搜到两条

# 在 ca 频道搜索
memory_search("记忆")  # 只能搜到 ca 频道的记忆
```

## 文件层隔离

文件层的频道隔离通过元数据 `channel` 字段实现：

```markdown
<!-- meta: importance=7 access=0 created=2026-03-04 last_accessed=2026-03-04 channel=ca -->
```

检索时使用 `scripts/channel_memory.py` 过滤：

```python
from channel_memory import filter_by_channel

entries = read_all_memories()
ca_entries = filter_by_channel(entries, "ca")
```

## 权限边界

- **boss 频道**：全量记忆检索权限
- **子频道**：只能读取本频道记忆
- **跨频道操作**：必须通过 `scripts/channel_guard.py` 鉴权

## 故障排查

### 子频道能看到其他频道的记忆

检查：
1. Mem0 插件的 userId 是否正确生成（应该是 `userId::channelKey`）
2. 文件层的 `channel` 元数据是否正确
3. 检索时是否使用了 `filter_by_channel`

### boss 频道看不到子频道的记忆

检查：
1. boss 频道的 userId 是否是主 userId（不带 `::channelKey`）
2. 检索逻辑是否正确（boss 应该能访问所有频道）

### 记忆写入时没有 channel 字段

检查：
1. `scripts/auto_memory_write.py` 是否传入了 `channel` 参数
2. 元数据模板是否包含 `channel` 字段
