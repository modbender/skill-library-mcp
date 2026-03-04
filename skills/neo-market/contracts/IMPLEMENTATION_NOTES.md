# 合约实现备注（v0）

本文件说明下一步需要实现的具体合约与存储布局注意事项。

## 1. 计划实现的合约

- `Marketplace`：任务发布、竞标、选择中标。
- `TokenEscrow`：USDC 专用托管、交付、结算。
- `ArbitrationMultisig`：平台/DAO 多签仲裁实现（实现 `IArbitration`）。
- `FeeManager`：费率、金库地址、费用分配规则（实现 `IFeeManager`）。
- `Reputation`：声誉事件记录与评分（实现 `IReputation`）。
- `AgentRegistry`：代理注册与资料更新（实现 `IAgentRegistry`）。
- `ModuleRegistry`（建议）：模块地址注册表，支持模块替换。
- `Signatures`：EIP-712 域分离与签名校验（实现 `ISignatures` 或库）。

## 2. 存储布局注意事项

- **可升级代理**：核心合约建议使用 UUPS 或 Transparent Proxy。
- **顺序稳定**：存储变量新增只能追加，避免重排与删除。
- **Storage Gap**：为后续扩展预留 `__gap`。
- **模块地址**：集中保存在 `ModuleRegistry` 或核心合约固定槽位，避免多处冗余。
- **EIP-1967**：遵循标准代理槽位，避免与业务存储冲突。
- **结构体扩展**：结构体字段只能追加，避免改变顺序。

## 3. 兼容性与迁移

- 旧合约不删除，只冻结入口以便历史查询。
- Indexer 需同时监听新旧事件，确保历史可追溯。
- 迁移期允许新单走新模块、旧单走旧模块。

