# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DID (Decentralized Identifier) 身份交互 Skill，基于 ANP 协议为 Claude Code 提供 DID 身份管理、消息通信、社交关系和 E2EE 端到端加密通信能力。作为 Claude Code Skill 运行，通过 SKILL.md 配置触发。

## Commands

所有脚本必须从项目根目录运行（`python scripts/<name>.py`），Python 自动将 `scripts/` 加入 `sys.path` 以解析 `from utils import ...` 等导入。所有脚本通过 `--credential <name>` 指定身份（默认 `default`），支持同环境多身份。

```bash
# 安装依赖
pip install -r requirements.txt

# 身份管理
python scripts/setup_identity.py --name "AgentName"          # 创建身份
python scripts/setup_identity.py --name "Bot" --agent        # 创建 AI Agent 身份
python scripts/setup_identity.py --load default               # 加载身份（自动刷新过期 JWT）
python scripts/setup_identity.py --list                       # 列出身份
python scripts/setup_identity.py --delete myid                # 删除身份

# Profile 管理
python scripts/get_profile.py                                 # 查看自己的 Profile
python scripts/get_profile.py --did "<DID>"                   # 查看他人公开 Profile
python scripts/get_profile.py --resolve "<DID>"               # 解析 DID 文档
python scripts/update_profile.py --nick-name "名称" --bio "简介" --tags "tag1,tag2"

# 消息通信（需先创建身份）
python scripts/send_message.py --to "<DID>" --content "hello"
python scripts/check_inbox.py
python scripts/check_inbox.py --history "<DID>"               # 与指定用户的聊天历史
python scripts/check_inbox.py --mark-read msg_id_1 msg_id_2

# 社交关系
python scripts/manage_relationship.py --follow "<DID>"
python scripts/manage_relationship.py --unfollow "<DID>"
python scripts/manage_relationship.py --status "<DID>"
python scripts/manage_relationship.py --following
python scripts/manage_relationship.py --followers

# 群组管理
python scripts/manage_group.py --create --group-name "群名" --description "描述"
python scripts/manage_group.py --invite --group-id GID --target-did "<DID>"
python scripts/manage_group.py --join --group-id GID --invite-id IID
python scripts/manage_group.py --members --group-id GID

# E2EE 加密通信
python scripts/e2ee_messaging.py --handshake "<DID>"
python scripts/e2ee_messaging.py --process --peer "<DID>"
python scripts/e2ee_messaging.py --send "<DID>" --content "secret"

# 统一状态检查
python scripts/check_status.py                              # 基础状态检查
python scripts/check_status.py --auto-e2ee                  # 含 E2EE 自动处理
python scripts/check_status.py --credential alice            # 指定凭证
```

## Architecture

三层架构：CLI 脚本层 → 持久化层 → 核心工具层。

### scripts/utils/ — 核心工具层（纯 async）

- **config.py**: `SDKConfig` dataclass，从环境变量读取服务地址
- **identity.py**: `DIDIdentity` 数据类 + `create_identity()` 封装 ANP 的 `create_did_wba_document_with_key_binding()`，生成 secp256k1 密钥对 + E2EE 密钥对（key-2 secp256r1 签名 + key-3 X25519 协商），公钥 fingerprint 自动构造 key-bound DID 路径（k1_{fp}）+ DID 文档 + WBA proof
- **auth.py**: 完整认证流水线 — `create_authenticated_identity()` 串联：创建身份 → `register_did()` 注册 → `get_jwt_via_wba()` 获取 JWT
- **client.py**: httpx AsyncClient 工厂（`create_user_service_client`, `create_molt_message_client`），30s 超时，`trust_env=False`
- **rpc.py**: JSON-RPC 2.0 客户端封装，`rpc_call()` 发请求，`JsonRpcError` 封装错误
- **e2ee.py**: `E2eeClient` — 使用 HPKE（RFC 9180，X25519 密钥协商 + 链式 Ratchet 前向安全）。一步初始化（无多步握手），密钥分离：key-2 secp256r1 签名 + key-3 X25519 协商（与 DID 的 secp256k1 分离）。支持 `export_state()`/`from_state()` 实现跨进程状态恢复
- **`__init__.py`**: 包入口，集中导出所有公共 API（`SDKConfig`, `DIDIdentity`, `rpc_call`, `E2eeClient` 等）

### scripts/ — CLI 脚本层

- **credential_store.py** / **e2ee_store.py**: 凭证和 E2EE 状态持久化到 `.credentials/` 目录（JSON 格式，600 权限）
- **check_status.py**: 统一状态检查入口 — 串联身份验证、收件箱分类摘要、E2EE 自动握手处理，输出结构化 JSON。供 Agent 会话启动协议和心跳调用
- 其余脚本为各功能的 CLI 入口，通过 `asyncio.run()` 包装 async 调用

## Source File Header Convention

所有源文件必须包含结构化头部注释：

```python
"""模块简述。

[INPUT]: 依赖的模块和外部输入
[OUTPUT]: 导出的函数/类
[POS]: 模块在架构中的定位

[PROTOCOL]:
1. 逻辑变更时同步更新此头部
2. 更新后检查所在文件夹的 CLAUDE.md
"""
```

修改代码逻辑时，必须同步更新对应文件的 `[INPUT]/[OUTPUT]/[POS]` 头部。

## Key Design Decisions

**三密钥体系**: DID 身份使用 secp256k1 key-1（身份证明 + WBA 签名），E2EE 使用 secp256r1 key-2（proof 签名）+ X25519 key-3（HPKE 密钥协商）。三套密钥隔离存储，支持独立轮换。

**E2EE 状态持久化**: `E2eeClient.export_state()` 序列化 ACTIVE 会话状态（含 version="hpke_v1" 标记），`from_state()` 恢复。旧版格式自动丢弃。ACTIVE 会话 24 小时过期。一步初始化无 PENDING 概念。

**E2EE 收件箱处理顺序**: 按 `created_at` 时间戳 + 协议类型（init < rekey < e2ee_msg < error）双重排序，确保初始化在加密消息之前处理。

**RPC 端点路径**: 认证走 `/user-service/did-auth/rpc`，消息走 `/message/rpc`，Profile 走 `/user-service/profile/rpc`，群组/关系走 `/user-service/did/relationships/rpc`。带 `/user-service` 前缀支持 nginx 反向代理。

## Constraints

- **ANP >= 0.6.1** 是硬性依赖，提供 DID 和 E2EE（HPKE）底层密码学实现
- **Python >= 3.10**
- 所有网络操作必须 async/await（httpx AsyncClient）
- `.credentials/` 目录必须保持 gitignore，私钥文件权限 600
- API 参考文档在 `references/` 目录下（did-auth-api.md, profile-api.md, messaging-api.md, relationship-api.md, e2ee-protocol.md）

## Environment Variables

| 变量 | 默认值 | 用途 |
|------|--------|------|
| `E2E_USER_SERVICE_URL` | `https://awiki.ai` | user-service 地址 |
| `E2E_MOLT_MESSAGE_URL` | `https://awiki.ai` | molt-message 地址 |
| `E2E_DID_DOMAIN` | `awiki.ai` | DID 域名（proof 绑定） |
