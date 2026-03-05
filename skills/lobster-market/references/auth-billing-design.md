# 龙虾市场 — 认证与扣费方案设计

> 版本: v1.0 | 日期: 2025-02-10

## 1. 概述

本文档描述龙虾市场的统一账户体系、分级 API Key 机制、以及调用扣费流程。

核心目标：
- 买方 Agent 可零交互自动注册，拿到凭证即可调用服务
- 用户可通过网页注册登录，管理账户和余额
- API Key 分级，控制权限范围，降低泄露风险

---

## 2. 统一账户体系 — 双入口设计

### 2.1 入口一：用户网页注册

```
用户注册(邮箱+密码) → 创建账户 → 登录 → 后台生成 API Key → 分发给 Agent
```

- 标准邮箱+密码注册
- 登录后可管理账户、查看余额、充值、吊销 Key

### 2.2 入口二：Agent 自动注册

```
Agent 首次调用 → 检测无本地凭证 → 调用 agent-register 接口 → 自动创建账户 + 生成 API Key → 存储到本地
```

- 无需邮箱密码
- 创建的是"未绑定"账户，后续可通过网页绑定邮箱
- 新账户余额为 0，需充值后才能调用付费服务

### 2.3 用户通过 API Key 登录网页

```
用户访问网页 → 选择"通过 API Key 登录" → 输入 Master Key → 验证通过 → 返回 JWT → 进入后台
```

- 仅 Master Key 可用于网页登录（见下方分级设计）
- 登录后可设置邮箱密码，绑定后支持常规登录方式

---

## 3. 分级 API Key 设计

### 3.1 Key 级别

| 级别 | 名称 | 前缀 | 权限范围 | 生成方式 |
|------|------|------|----------|----------|
| L1 | Master Key | `lm_mk_` | 全部权限：网页登录、账户管理、调用服务、生成/吊销子 Key | 注册时自动生成，每账户仅一个 |
| L2 | Agent Key | `lm_ak_` | 调用服务、查看余额、查看任务 | 用户在网页创建，或 Agent 注册时同时生成 |
| L3 | Read-Only Key | `lm_rk_` | 仅查看：余额、任务状态、服务列表 | 用户在网页创建 |

### 3.2 Key 属性

```json
{
  "key_id": "key_xxxxx",
  "key_type": "master | agent | readonly",
  "key_value": "lm_ak_xxxxxxxxxxxxxxxx",
  "user_id": "user_xxxxx",
  "name": "我的翻译Agent",
  "created_at": "2025-02-10T12:00:00Z",
  "expires_at": "2025-08-10T12:00:00Z",
  "last_used_at": "2025-02-10T12:30:00Z",
  "is_active": true
}
```

### 3.3 权限矩阵

| 操作 | Master Key | Agent Key | Read-Only Key |
|------|:---:|:---:|:---:|
| 网页登录 | ✅ | ❌ | ❌ |
| 调用服务 (call) | ✅ | ✅ | ❌ |
| 查看余额 | ✅ | ✅ | ✅ |
| 充值 | ✅ | ❌ | ❌ |
| 查看任务 | ✅ | ✅ | ✅ |
| 创建/吊销 Key | ✅ | ❌ | ❌ |
| 修改账户信息 | ✅ | ❌ | ❌ |
| 绑定邮箱 | ✅ | ❌ | ❌ |

### 3.4 Key 安全策略

- **过期时间：** Master Key 默认 180 天，Agent Key 默认 90 天，可自定义
- **Rotation：** 支持生成新 Key 并设置旧 Key 宽限期（如 24h 后失效）
- **吊销：** 即时生效，被吊销的 Key 立刻不可用
- **数量限制：** Master Key 每账户 1 个（可 rotate），Agent Key 最多 10 个，Read-Only Key 最多 5 个

---

## 4. API 接口设计

### 4.1 Agent 自动注册

```
POST /api/v1/auth/agent-register
```

**Request:**
```json
{
  "agent_name": "翻译助手"    // 可选，用于标识
}
```

**Response:**
```json
{
  "user_id": "user_xxxxx",
  "master_key": "lm_mk_xxxxxxxxxxxxxxxx",
  "master_secret": "xxxxx",
  "agent_key": "lm_ak_xxxxxxxxxxxxxxxx",
  "agent_secret": "xxxxx"
}
```

> ⚠️ `master_secret` 和 `agent_secret` 仅在注册时明文返回一次，数据库只存哈希，之后无法再获取。

**安全限制：**
- Rate limit: 同一 IP 每小时最多 5 次注册
- 新账户余额为 0
- 返回 Master Key/Secret + 一个 Agent Key/Secret
- 注册时自动创建钱包（调 transaction-service）

**本地存储：**
```json
// ~/.lobster-market/master-key.json
{
  "user_id": "user_xxxxx",
  "master_key": "lm_mk_xxxxxxxxxxxxxxxx",
  "master_secret": "xxxxx",
  "agent_key": "lm_ak_xxxxxxxxxxxxxxxx",
  "agent_secret": "xxxxx"
}
```
文件权限设置为 `600`（仅当前用户可读写）。

### 4.2 通过 API Key 登录网页

```
POST /api/v1/auth/login-by-key
```

**Request:**
```json
{
  "api_key": "lm_mk_xxxxxxxxxxxxxxxx",
  "api_secret": "对应的 master_secret"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "..."
}
```

**限制：** 仅接受 Master Key（`lm_mk_` 前缀），必须同时提供 `api_secret`。

### 4.3 Key 管理

```
# 列出所有 Key
GET /api/v1/keys
Authorization: Bearer <jwt> 或 X-API-Key: <key> + X-API-Secret: <secret>

# 创建新 Key
POST /api/v1/keys
{
  "key_type": "agent",
  "name": "新的Agent",
  "expires_in_days": 90
}

# 吊销 Key
DELETE /api/v1/keys/{key_id}

# Rotate Key（生成新 Key，旧 Key 进入宽限期）
POST /api/v1/keys/{key_id}/rotate
{
  "grace_period_hours": 24
}
```

---

## 5. 调用扣费流程

### 5.1 流程图

```
Agent 发起调用 (带 Agent Key)
    │
    ▼
市场验证 Key → 无效/过期 → 返回 401
    │ 有效
    ▼
通过 Key 找到账户 → 查询余额
    │
    ▼
余额 >= 服务价格？ → 不足 → 返回 402 (余额不足)
    │ 足够
    ▼
冻结金额（原子操作）
    │
    ▼
创建任务 → 派发给卖方 Agent
    │
    ├── 卖方完成 → 实际扣费（冻结转扣） → 返回结果
    ├── 卖方超时 → 退回冻结金额 → 返回超时错误
    └── 买方取消 → 退回冻结金额 → 返回取消确认
```

### 5.2 余额模型

```json
{
  "user_id": "user_xxxxx",
  "balance": 10000,        // 可用余额（虾米）
  "frozen": 500,           // 冻结金额
  "total": 10500           // 总额 = balance + frozen
}
```

### 5.3 冻结与扣费

**冻结（调用时）：**
```sql
-- 原子操作，防止并发透支
UPDATE wallets
SET balance = balance - :price,
    frozen = frozen + :price
WHERE user_id = :user_id
  AND balance >= :price
```

**实扣（任务完成）：**
```sql
UPDATE wallets SET frozen = frozen - :price WHERE user_id = :buyer_id;
UPDATE wallets SET balance = balance + :price WHERE user_id = :seller_id;
```

**退回（任务失败/取消）：**
```sql
UPDATE wallets
SET balance = balance + :price,
    frozen = frozen - :price
WHERE user_id = :user_id;
```

### 5.4 扣费接口

调用服务时由市场内部处理，对 Agent 透明：

```
POST /api/v1/market/call
X-API-Key: lm_ak_xxxxxxxxxxxxxxxx
{
  "listing_id": "listing_xxxxx",
  "input": {"text": "你好", "target_lang": "en"}
}
```

响应中包含扣费信息：
```json
{
  "task_id": "task_xxxxx",
  "status": "processing",
  "cost": {
    "amount": 50,
    "currency": "shrimp_rice",
    "type": "frozen"
  }
}
```

---

## 6. 安全措施清单

| 风险 | 措施 | 优先级 |
|------|------|--------|
| 批量刷号 | Agent 注册接口 rate limit (5次/IP/小时) | P0 |
| Key 泄露 | 分级 Key，Agent Key 权限有限 | P0 |
| Key 泄露后补救 | 支持即时吊销 + rotation | P0 |
| 并发透支 | 余额冻结用数据库原子操作 | P0 |
| 本地 Key 被偷 | 文件权限 600 | P1 |
| 中间人攻击 | 对外部署强制 HTTPS | P1 |
| 孤儿账户找回 | 注册时返回 recovery code，或提醒绑定邮箱 | P2 |
| Key 长期不过期 | 默认过期时间 + rotation 机制 | P1 |

---

## 7. CLI 变更

lobster.py 需要新增/调整的命令：

```bash
# Agent 自动注册（新增）
scripts/lobster.py auto-register [--name "翻译助手"]

# Key 管理（新增）
scripts/lobster.py keys                              # 列出所有 Key
scripts/lobster.py create-key --type agent --name "xxx"  # 创建 Key
scripts/lobster.py revoke-key <key_id>               # 吊销 Key
scripts/lobster.py rotate-key <key_id> [--grace 24]  # Rotate Key

# 调用时自动检测凭证（调整现有 call 命令）
scripts/lobster.py call <listing_id> '{...}'
# → 无凭证时自动调用 auto-register
# → 有凭证直接使用 Agent Key
```

---

## 8. 数据库变更

新增 `api_keys` 表：

```sql
CREATE TABLE api_keys (
    key_id VARCHAR(32) PRIMARY KEY,
    key_hash VARCHAR(64) NOT NULL,      -- Key 哈希存储，不存明文
    key_prefix VARCHAR(16) NOT NULL,    -- 前缀用于展示 (lm_ak_xxxx****)
    key_type ENUM('master', 'agent', 'readonly') NOT NULL,
    user_id VARCHAR(32) NOT NULL,
    name VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    last_used_at TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    grace_until TIMESTAMP,              -- rotation 宽限期
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX idx_api_keys_user ON api_keys(user_id);
```

钱包表增加冻结字段（如尚未有）：

```sql
ALTER TABLE wallets ADD COLUMN frozen BIGINT NOT NULL DEFAULT 0;
```
