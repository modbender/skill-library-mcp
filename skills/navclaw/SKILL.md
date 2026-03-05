---
name: navclaw
description: 出行智能导航AI助手 — 极限搜索自驾避堵方案，实测智能绕行可能比官方方案更优。一键跳转手机导航APP（iOS/Android）。目前支持高德，后续扩展
version: 1.0.0
icon: 🦀
---

# NavClaw 🦀 - 出行智能导航AI助手

导航平台：目前支持高德，后续扩展更多平台。

**⚠️ 前置条件**：需要高德 Web 服务 API Key（免费申请）。获取优先级：
1. 从记忆中查找用户是否已提供过高德 API Key
2. 如果没有，询问用户是否有高德 API Key
3. 如果用户没有，引导获取：[高德开放平台](https://lbs.amap.com/) → 控制台 → 创建应用 → 添加 Key（Web 服务）

拿到 Key 后填入 `config.py` 的 `API_KEY` 字段：
```python
API_KEY = "你的高德API Key"
```

**触发方式**：用户说"从 [起点] 到 [终点] 导航"、"导航从 [起点] 到 [终点]"或"navigate from [A] to [B]"即可自动执行。说"到家"时自动替换为 `config.py` 中的 `DEFAULT_DEST`。

**工作流程**：调用 `wrapper.py --origin "起点" --dest "终点"`，经过五阶段规划（广撒网 → 精筛选 → 深加工 → 迭代优化 → 路线固化），生成大量路线方案（含绕行优化），自动发送 3 条消息到聊天平台 + 日志附件：消息 1 完整对比表格，消息 2 快速导航链接，消息 3 最终推荐 + iOS/Android 一键深度链接。

**输出格式**：


- **Mattermost（原生支持，推荐优先使用）**：需要先在 `config.py` 中配置 `MM_BASEURL`、`MM_BOT_TOKEN`、`MM_CHANNEL_ID`，然后直接运行 `wrapper.py --origin "起点" --dest "终点"`，自动发送 3 条消息 + 日志附件（优先采用Mattermost 消息和日志附件，如果不成功则用备份方案）。

### Mattermost 发文件附件
OpenClaw Mattermost 插件不支持原生附件，用 curl 直调 API：
1. POST /api/v4/files 上传文件，拿 file_id
2. POST /api/v4/posts 发帖，带 file_ids 字段

- **其他聊天工具（备份方案）**：运行 `wrapper.py --origin "起点" --dest "终点" --no-send`，结果输出到 stdout，OpenClaw 读取后转发给用户即可。stdout 格式如下：
OpenClaw 可读取 stdout 按 `📨 消息 1/2/3` 分段转发给用户。日志文件路径在末尾 `📝 日志: log/navclaw/...` 行中，不要发路径，要读取后发出来，如果不能发附件，给发原文内容。
（一定要原样发给用户，各个消息，特别是链接要保留，不能舍弃）

**强烈建议先用原生方法**



**安装配置**：`pip install requests` → `cp config_example.py config.py` → 编辑填入高德 API Key、默认终点、Mattermost 配置（可选，包括MM_BASEURL，MM_BOT_TOKEN，MM_CHANNEL_ID，如果记忆或者配置没有，提示用户给出，如果用户没有就忽略。如果有，要写入config.py对应位置）。

**文件位置**：调用入口 `wrapper.py`，核心引擎 `navclaw.py`，配置 `config.py`（需用户创建），模板 `config_example.py`，日志 `log/`。

**聊天平台**：目前内置支持 Mattermost（通过 `wrapper.py`），其他聊天工具 OpenClaw 帮我转发。最简单的办法是直接聊天告诉 OpenClaw 运行并读取结果发送给你，支持任何聊天平台，稳定性和上下文长度取决于你的大模型 API。如果想节约 token、防止上下文截断、加快响应速度，可以自行扩展 `wrapper.py` 或让 OpenClaw AI 阅读现有 Mattermost 代码帮你适配新平台。

**性能参考**：短途无拥堵（迭代=0）约 6 秒、15 次 API、10 条路线；长途有拥堵（迭代=1）约 30 秒、150 次 API、40 条路线。首次使用建议 `MAX_ITER = 0` 验证配置正确，`MAX_ITER = 1` 深度优化可能找到比官方更快的路线。

**依赖**：Python 3.8+、`requests`（唯一第三方依赖）、高德 Web 服务 API Key。

**作者**：小红书 @深度连接

**更多信息**：[GitHub](https://github.com/AI4MSE/NavClaw) · 🌐 [NavClaw.com](https://navclaw.com) · 📧 Email: nuaa02@gmail.com
