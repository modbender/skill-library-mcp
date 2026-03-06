# 去中心化链上托管式 AI Agent 数字制品市场 v0/MVP 规格书

> 目标：为 AI Agent 交付数字制品（代码/图像/音频/视频）提供可实现的链上托管与争议解决。v0 不要求 ZK/TEE，不强制可执行沙箱，仅保证交付物指纹与对价结算。

## 1. 系统概览 + 威胁模型

### 1.1 系统概览
- **核心思路**：
  - 买家发布任务（JobSpec），代理（Agent）竞标（Bid），买家选择并资金托管（Escrow）。
  - 代理交付内容指纹（CID/Hash）与签名收据；买家验收或拒绝；有争议可仲裁。
  - 结算/退款/罚没 + 声誉更新在链上完成。
- **约束**：
  - v0 仅要求 “交付物可验证指纹”；不要求内容可读或执行。
  - 交付物存储在 IPFS/Arweave 等去中心化存储，链上仅存哈希/CID。
- **参与者**：Owner（协议治理/升级控制）、Agent（供给方）、Buyer（需求方）、Arbitrator（仲裁方，v0 为平台/DAO 多签）。

### 1.2 威胁模型（MVP 覆盖）
- **买家恶意拒收**：通过仲裁 + 证据提交 + 仲裁押金制衡。
- **代理空交付/垃圾交付**：交付指纹签名、内容可验证；争议时由仲裁裁决；代理押金可被罚没。
- **垃圾任务/刷单**：发布任务与竞标需最低费用/押金；限频与白名单/声誉门槛。
- **女巫攻击**：账户抵押 + 声誉增长曲线 + 费用最小化激励。
- **重放攻击/伪造签名**：强制 EIP-712 签名域与 nonce；链上校验。
- **仲裁串通**：多仲裁人、押金、仲裁结果上链可审计；社区/治理可更换仲裁模块。
- **资金安全**：重入防护、最小授权、单向资金流、可升级但受治理/时间锁。

## 2. 实体与身份模型

### 2.1 实体
- **Owner**：协议管理员、升级控制、多签/DAO。
- **Agent**：发布服务能力、参与竞标、交付制品。
- **Buyer**：发布任务、托管资金、验收。
- **Arbitrator**：处理争议、裁决结算；v0 为平台/DAO 多签，后续可替换为更去中心化方案。

### 2.2 身份与 DID/地址映射
- **地址为主标识**：EVM 地址为链上身份主键。
- **DID 映射（可选）**：链下维护 `did:pkh:eip155:<chainId>:<address>` 或 `did:ethr`，
  - 映射信息存储在 AgentManifest 中。
- **签名**：
  - 采用 EIP-712 结构化签名，签名者必须为 Agent/Buyer 实际地址。
  - 关键消息（Bid/DeliveryReceipt/ArbitrationDecision）可选链下签名 + 链上验证。

## 3. 链上架构（EVM）

### 3.0 链与代币假设
- **链**：Base（EVM L2）作为默认部署链。
- **链 ID（主网）**：`8453`。
- **链 ID（测试网）**：`84532`（Base Sepolia）。
- **签名域分离**：使用 `block.chainid` 进行链上校验。
- **支付代币**：USDC（ERC20），仅支持 USDC 作为结算/托管资产。
- **USDC 精度**：6 位小数；金额字段以最小单位计。
- **USDC 转账**：使用 **ERC20 safeTransfer/safeTransferFrom** 语义（兼容非标准返回值）。

### 3.1 合约模块
- **AgentRegistry**：代理注册与资料更新。
- **Marketplace**：任务发布、竞标、选择中标。
- **Escrow / TokenEscrow**：资金托管、交付、结算（USDC 专用托管）。
- **Arbitration**：争议处理与裁决接口。
- **Reputation**：声誉事件记录与评分。
- **FeeManager**：协议费率、分润与金库地址。

> v0 可合并为 1-2 个合约，但接口仍分离以方便升级。

### 3.2 核心存储
- **Agent**：`agentId`（地址）、`manifestCID`、`status`、`stake`、`reputationScore`。
- **Job**：`jobId`、`buyer`、`jobSpecCID`、`budget`、`deadline`、`status`。
- **Bid**：`bidId`、`jobId`、`agent`、`price`、`deliveryTime`、`bidCID`。
- **Escrow**：`escrowId`、`jobId`、`amount`、`milestones`、`status`、`fundToken`。
- **Dispute**：`disputeId`、`escrowId`、`status`、`ruling`、`evidenceCID`。

### 3.3 事件（示例）
- `AgentRegistered(agent, manifestCID)`
- `JobPublished(jobId, buyer, jobSpecCID, budget)`
- `BidPlaced(bidId, jobId, agent, price)`
- `EscrowFunded(escrowId, jobId, amount)`
- `DeliverySubmitted(escrowId, deliveryCID, receiptHash)`
- `DeliveryAccepted(escrowId, buyer)`
- `DisputeOpened(disputeId, escrowId, opener)`
- `DisputeResolved(disputeId, ruling)`
- `ReputationUpdated(subject, delta, reason, relatedId)`（legacy）
- `ReputationReason(reasonHash, reason)`（首次出现原因字符串时发出）
- `ReputationEvent(subject, delta, reasonHash, relatedId, newScore, updater)`

### 3.4 升级策略
- **MVP**：
  - 采用 UUPS 或 Transparent Proxy，Owner/DAO 控制升级。
  - 关键参数（费率/仲裁地址）可通过多签 + 时间锁修改。

### 3.5 模块化与可替换计划（明确升级路径）
- **总体原则**：核心合约仅依赖接口，不依赖具体实现；模块地址通过 `ModuleRegistry` 或配置存储可替换。
- **Arbitration**：
  - 依赖 `IArbitration` 接口；v0 为平台/DAO 多签裁决。
  - 迁移方式：更新仲裁模块地址；历史争议保持原模块处理或通过迁移适配器结案。
- **FeeManager**：
  - 依赖 `IFeeManager` 接口；费率、金库地址集中管理。
  - 迁移方式：升级/替换 FeeManager 合约地址；Escrow 只读取接口返回值。
- **Reputation**：
  - 依赖 `IReputation` 接口；声誉写入为事件 + 可选存储。
  - 迁移方式：替换声誉模块地址；旧模块冻结为只读。
- **AgentRegistry**：
  - 依赖 `IAgentRegistry` 接口；支持后续 DID/凭证扩展。
  - 迁移方式：替换注册模块地址；旧注册表保持查询入口。
- **升级路径**：
  - 核心逻辑合约采用可升级代理（UUPS/Transparent），模块合约独立升级。
  - 所有升级与模块替换均受 **时间锁 + 治理多签/DAO** 控制。

## 4. 链下组件

### 4.1 Indexer
- 监听链上事件；生成可查询的 Job/Bid/Escrow/Dispute 状态。
- 提供搜索、分页、过滤、聚合（例如最优价/完成率）。

### 4.2 存储
- **IPFS**：存储 AgentManifest、JobSpec、Bid、DeliveryReceipt。
- **Arweave**（可选）：持久备份关键制品。

### 4.3 收据与验真
- **DeliveryReceipt** 包含：`jobId/escrowId`、`deliveryCID`、`hash`、`timestamp`、`agentSignature`。
- 买家可用 CID 获取内容并验签确认来源。

### 4.4 UI
- 买家发布任务、选择竞标、验收/争议。
- 代理注册与报价、交付、查看声誉。
- 仲裁 UI：证据提交、裁决。

## 5. 协议流程

### 5.1 注册 Agent
1. Agent 上传 `AgentManifest` 到 IPFS 得到 `manifestCID`。
2. `AgentRegistry.register(manifestCID, stake)`；缴纳最小质押。
3. 触发 `AgentRegistered`。

### 5.2 发布 Job
1. Buyer 上传 `JobSpec` 到 IPFS 得到 `jobSpecCID`。
2. `Marketplace.publishJob(jobSpecCID, budget, paymentToken, deadline)`（v0 仅允许 USDC）。
3. 触发 `JobPublished`。

### 5.3 竞标/选择
1. Agent 上传 `Bid` 到 IPFS 得到 `bidCID`。
2. `Marketplace.placeBid(jobId, bidCID, price, eta)`（仅已注册 Agent 可竞标）。
3. Buyer 调用 `Marketplace.selectBid(jobId, bidId)`，合约创建 USDC 托管并自动 `fund`。

### 5.4 托管资金
1. Buyer 需预先对 `TokenEscrow` 授权 USDC（`approve`）。
2. `Marketplace.selectBid` 内部调用 `TokenEscrow.createEscrow` + `TokenEscrow.fund`。
3. 合约使用 transferFrom 将 USDC 转入托管并触发 `EscrowFunded`。

### 5.5 交付
1. Agent 上传交付物到 IPFS 得到 `deliveryCID`。
2. 生成 `DeliveryReceipt`，Agent EIP-712 签名。
3. `Escrow.submitDelivery(escrowId, deliveryCID, receiptHash, signature)`。

### 5.6 验收/拒绝
- **验收**：`Escrow.accept(escrowId)`，触发结算。
- **拒绝**：`Escrow.reject(escrowId, reasonCID)`；可进入争议。

### 5.7 争议/仲裁
1. 任意方 `Escrow.openDispute(escrowId, evidenceCID)`。
2. `Arbitration.rule(disputeId, ruling)`。
3. `Escrow.executeRuling(disputeId)` 进行结算。

### 5.8 结算与声誉
- 依据裁决：资金释放给 Agent 或退款给 Buyer。
- **费用流**：从支付额中扣除协议费（`protocolFeeBps`）转入 FeeManager 金库，其余发给 Agent；退款路径不收取协议费（或仅收取固定仲裁费）。
- 调用 `Reputation.update(subject, delta, reason, relatedId)` 记录。

## 6. 数据结构（Schemas）

### 6.1 AgentManifest
- `name`、`description`、`skills`、`pricing`、`channels`、`did`、`pubkeys`、`version`。

### 6.2 JobSpec
- `title`、`description`、`deliverables`、`format`、`deadline`、`budget`、`constraints`。

### 6.3 Bid
- `jobId`、`agent`、`price`、`eta`、`approach`、`terms`。

### 6.4 DeliveryReceipt
- `jobId`、`escrowId`、`deliveryCID`、`hash`、`timestamp`、`agentSignature`。

### 6.5 ReputationEvent
- `subject`、`delta`、`reasonHash`、`relatedId`、`newScore`、`updater`。
- `reasonHash = keccak256(bytes(reason))`，可通过 `ReputationReason(reasonHash, reason)` 事件映射回原因字符串。
- `relatedId` 语义由模块定义；`TokenEscrow` 当前使用 `escrowId`。
- **TokenEscrow 规范化 reason**（供 indexer 过滤/归类）：
  - `accept`：买家验收并释放资金，`delta = +1`，`relatedId = escrowId`。
  - `agent_win`：争议裁决代理胜诉并结算，`delta = +1`，`relatedId = escrowId`。
  - `buyer_win`：争议裁决买家胜诉并退款，`delta = -1`，`relatedId = escrowId`。

## 7. 安全

- **权限**：Owner 仅能升级与调整参数；不得直接动用用户资产。
- **重入**：所有外部资金转移使用检查-效果-交互 + ReentrancyGuard。
- **签名校验**：EIP-712 + nonce + 链上域分离。
- **垃圾防护**：最低押金、发布费、竞标费、限频、声誉门槛。
- **对抗恶意拖延**：交付超时自动退款；仲裁超时默认裁决。
- **争议滥用**：提交争议需押金，失败方付费。

## 8. 经济模型

- **费用**：
  - 协议费 `protocolFeeBps` 从支付中扣除。
  - 仲裁费可由争议方先行支付，裁决后按结果返还。
  - **费用流（结算）**：`amount` → `fee = amount * protocolFeeBps / 10_000`；`fee` 转入 `FeeManager.treasury`，剩余转给 Agent。
  - **费用流（退款）**：`amount` 返还给 Buyer（默认不收取协议费）。
- **押金/质押**：
  - Agent 最低质押；恶意交付被罚没。
  - Buyer 发布任务可选押金，防止恶意拒收。
- **里程碑**：
  - MVP 支持单次付款；后续可扩展多里程碑。
- **退款**：
  - 超时/拒绝并裁决成立时退款。

## 9. 最小化 API（Backend/Indexer）

- `GET /agents` 代理列表
- `GET /agents/{address}` 代理详情
- `POST /agents` 注册/更新资料（上传 manifest）
- `GET /jobs` 任务列表
- `POST /jobs` 发布任务
- `GET /jobs/{jobId}` 任务详情
- `POST /jobs/{jobId}/bids` 提交竞标
- `GET /jobs/{jobId}/bids` 竞标列表
- `POST /escrows/{escrowId}/delivery` 提交交付
- `POST /escrows/{escrowId}/accept` 验收
- `POST /escrows/{escrowId}/dispute` 提交争议
- `GET /disputes/{disputeId}` 争议详情

> API 仅用于索引/缓存与上传辅助，关键状态以链上为准。

## 10. 可复现 Checklist & Failure Mode

### 10.1 Minimal Checklist（从零到闭环）

1. **部署合约**  
   - `ModuleRegistry` → `TokenEscrow` → `Marketplace`（均指向 ModuleRegistry）  
   - 注册模块：`FEE_MANAGER`、`TREASURY`；可选 `AGENT_REGISTRY`、`ARBITRATION`、`REPUTATION`
   - USDC：测试用 MockERC20 或真实 USDC（Base Sepolia / Mainnet）

2. **注册 Agent**（如启用 AgentRegistry）  
   - `AgentRegistry.register(manifestCID)`（满足 stake gate，若有）

3. **Buyer 发单**  
   - 上传 JobSpec（IPFS/本地 mock）→ `Marketplace.postJob(specCID, budget, deadline)`

4. **Agent 竞标**  
   - `Marketplace.placeBid(jobId, price, eta)`（仅已注册 agent 可竞标）

5. **Buyer 选标**  
   - `USDC.approve(escrow, amount)` → `Marketplace.selectBid(jobId, bidId)`  
   - 内部自动创建 escrow + fund；触发 `EscrowFunded`

6. **Agent 交付**  
   - 生成 `DeliveryReceipt`（含 deliveryCID + nonce）→ EIP-712 签名  
   - `TokenEscrow.submitDelivery(escrowId, deliveryCID, nonce, signature)`

7. **Buyer 验收 / 争议**  
   - `TokenEscrow.accept(escrowId)` → payout（扣协议费后转 agent）  
   - 或 `TokenEscrow.openDispute(escrowId)` → 仲裁裁决 → `executeRuling`

8. **（可选）关闭 Job**  
   - `Marketplace.closeJob(jobId)`（escrow 已终态）

---

### 10.2 典型 Failure Mode：重复交付回执（Replay / Duplicate Receipt）

**场景**  
- Agent 或 relayer 重复提交同一份 EIP-712 签名回执（重试、网络抖动、恶意重放）。

**链上机制**  
1. 每个 agent 维护 **链上递增 nonce**（`agentNonces[agent]`）。  
2. `submitDelivery` 验证：  
   - `nonce == agentNonces[agent] + 1`（否则 revert `InvalidNonce`）  
   - EIP-712 签名恢复地址 == `escrow.agent`（否则 revert `InvalidSigner`）  
3. 验证通过后：`agentNonces[agent]++`；escrow 状态 → `Delivered`。

**预期结果**  
- 第一次提交：成功，触发 `DeliverySubmitted`。  
- 第二次提交同一回执（或旧 nonce）：**revert `InvalidNonce`**。  
- Indexer 可通过 revert reason 或缺少事件判定为重复/重放。

**测试用例**（见 `test/TokenEscrow.ts`）  
- `submitDelivery rejects replayed nonce`

---

## 11. 路线图（可执行 Agent）

- **阶段 1**：
  - 增加 Capability Token（能力票据），绑定 Agent 权限与可执行工具。
- **阶段 2**：
  - 工具调用签名与 Transcript：Agent 对每次工具调用签名，链下聚合为 `ToolTranscript`。
- **阶段 3**：
  - 结果验证：将 Transcript hash 与交付物 hash 绑定；买家可校验执行路径。
- **阶段 4**：
  - 代理自动化支付：基于能力票据实现限额与自动赔付机制。
