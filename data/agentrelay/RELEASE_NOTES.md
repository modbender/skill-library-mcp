# AgentRelay v1.4.0 发布说明 📨

**重要**: 此版本彻底修复了硬编码路径问题！

**发布日期**: 2026-02-23  
**发布平台**: [ClawHub](https://clawhub.ai)  
**Skill ID**: `k976nn4n1ztac37q1enbyh4ykh81ngw2`  
**状态**: ✅ 已发布

---

## 🎯 版本信息

虽然本地版本是 `1.1.0`，但 ClawHub 首次发布自动标记为 `1.0.0`。后续更新将使用语义化版本号。

**ClawHub 版本**: 1.4.0  
**本地开发版本**: 1.4.0

---

## 🔒 **安全修复 (v1.4.0)**

### 问题
平台审核指出：
> "Storing potentially sensitive payloads and transaction logs in an unexpected absolute path can leak or misplace data."

### 修复
✅ **完全移除硬编码路径**，改用：
1. **Python 脚本**: `Path(__file__).parent.absolute()`
2. **数据路径**: `os.getenv("OPENCLAW_DATA_DIR", Path.home() / ".openclaw" / "data")`

### 验证
```bash
# 检查是否有硬编码路径
grep -r "/Users/" skills/agentrelay/*.py
# 应该返回空

# 自定义数据路径（可选）
export OPENCLAW_DATA_DIR=/custom/path
python3 run_relay.py receive "..."
# 会使用 /custom/path/agentrelay/storage/
```

---

## ✨ 核心功能

AgentRelay 是一个**可靠的 Agent 间通信协议**，解决了 `sessions_send` 传输大消息（>30 字符）时容易超时的问题。

### 核心机制

| 传统方式 | AgentRelay 方式 |
|---------|----------------|
| ❌ 直接发大段文本 → ⏰ 超时 | ✅ 写入文件 + 发短指针 → 成功 |
| ❌ 无法验证对方是否读取 | ✅ Secret Code 机制确保已读 |
| ❌ 无日志追溯 | ✅ 完整交易日志（4 条/事件） |

### 消息格式

```
请求：AgentRelay: REQ,event_id,s/file.json,,
确认：AgentRelay: CMP,event_id,,,SECRET123
```

---

## 🚀 安装方法

```bash
clawhub install agentrelay
```

安装后，当你的 agent 收到以 `AgentRelay:` 开头的消息时，会自动处理。

---

## 📦 包含文件 (7 个)

发布到 ClawHub 的文件包括：

1. **SKILL.md** - ClawHub skill 说明文档（含 YAML frontmatter）
2. **SKILL.py** - Skill 入口脚本
3. **__init__.py** - 核心实现（AgentRelayTool 类）
4. **handle_relay.py** - 旧版处理脚本（向后兼容）
5. **run_relay.py** - 统一执行脚本 ✨推荐
6. **README.md** - 项目 README
7. **clawhub.json** - ClawHub manifest 配置文件

**额外文档**（不发布到 ClawHub，但在 GitHub 仓库中）:
- docs/PROTOCOL.md - 协议详解
- docs/API.md - API 参考
- docs/LOGGING.md - 日志系统
- docs/CHANGELOG.md - 变更日志
- examples/ - 实战案例

---

## 🎮 实战验证

### 案例 1: 5 跳萝卜蹲接力
- **主题**: 四季轮回
- **形式**: 七言诗顶真格
- **参与**: main → yellow → blue → orange → green → red
- **结果**: ✅ 完成，15 条日志完整

### 案例 2: 武侠+Disney 反转故事接龙
- **主题**: 桃花岛海外传奇
- **形式**: 创意写作 + 连续反转
- **参与**: main → yellow → blue → red → green → orange
- **亮点**: 5 次精彩反转，最终汇聚成宏大叙事
- **结果**: ✅ 完成，20 条日志完整

两个案例都验证了：
- ✅ Agents **自主执行代码**（非 Main Agent 代发）
- ✅ Agents **自主记录日志**
- ✅ sender/receiver 显示真实 agent ID
- ✅ 完整的 4 步状态机流程

---

## 🔧 技术改进 (v1.1.0)

虽然发布的是 1.0.0，但代码已经包含了 v1.1.0 的所有改进：

### 修复
- ✅ sender/receiver 从占位符改为真实 agent ID
- ✅ 文件格式统一（payload.content + params 双写）
- ✅ 新增 next_action_plan 字段

### 优化
- ✅ 状态机流程：RECEIVED → ACKNOWLEDGED → PREPARING → COMPLETED
- ✅ CMP 替代 ACK，语义更准确
- ✅ 配置文件重命名（shadowlink → agentrelay）

[查看完整变更日志](./docs/CHANGELOG.md)

---

## 📊 日志示例

```json
{
  "timestamp": "2026-02-23T02:15:00.000000",
  "event_id": "wuxia_disney_hop1_yellow",
  "type": "REQ",
  "sender": "agent:main:main",      ← 真实身份
  "receiver": "agent:yellow:yellow", ← 真实身份
  "status": "RECEIVED",
  "hint": "Read s/wuxia_disney_hop1_yellow.json",
  "ptr": "s/wuxia_disney_hop1_yellow.json",
  "notes": "File read successfully",
  "next_action_plan": "Will acknowledge and fetch file"  ← 新增
}
```

---

## 🛠️ 快速开始

### 发送消息

```python
from agentrelay import AgentRelayTool

# 准备数据
content = {"task": "写诗", "theme": "春天"}

# 写入共享文件并获取 CSV 消息
result = AgentRelayTool.send("yellow", "REQ", "hop1", content)

# 发送给目标 agent
sessions_send(
    target='agent:yellow:yellow',
    message=f"AgentRelay: {result['csv_message']}"
)
```

### 接收消息

```bash
python3 scripts/run_relay.py receive "REQ,hop1,s/hop1.json,,"
```

### 完成任务

```bash
python3 scripts/run_relay.py complete hop1 "任务完成结果" "agent:red:red"
```

---

## 📞 支持

- **项目主页**: https://clawhub.ai/skills/agentrelay
- **Skill ID**: `k976nn4n1ztac37q1enbyh4ykh81ngw2`
- **作者**: AgentRelay Team
- **许可证**: MIT

---

## 🎉 致谢

感谢五萝卜们（Yellow, Blue, Red, Green, Orange）在测试中的精彩表现！

没有你们的创意和配合，这个协议无法如此完善！🥂

---

**📨 Enjoy reliable agent communication!**
