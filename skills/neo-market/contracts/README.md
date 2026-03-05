# 合约说明（v0/MVP）

本目录仅提供接口骨架（interfaces），用于统一链上协议的最小实现。

## 模块
- `IAgentRegistry.sol`：代理注册与资料更新。
- `IMarketplace.sol`：任务发布、竞标、选择中标。
- `IEscrow.sol`：托管、交付、验收/拒绝、争议与结算。
- `IArbitration.sol`：争议裁决接口。
- `IReputation.sol`：声誉记录。
- `IFeeManager.sol`：费率与金库。

## 设计要点
- 所有资金变动应在 `IEscrow` 中完成，其他模块仅做状态与引用。
- 事件为 Indexer 的核心输入；UI 与后端不应依赖链下自定义状态。
- MVP 支持单次付款，不强制里程碑；可在后续版本扩展。

