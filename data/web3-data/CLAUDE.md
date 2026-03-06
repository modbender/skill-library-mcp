# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

web3-data-skill — A Claude Code skill for exploring Web3 on-chain data using Chainbase APIs.

## Structure

```
├── SKILL.md                    # Skill 定义：路由逻辑、工作流、Chain ID 映射
├── scripts/
│   └── chainbase.sh            # Chainbase API 调用封装脚本（支持 SQL 异步轮询）
└── references/
    └── api-endpoints.md        # 完整 API 端点参考文档（38 个端点）
```

## Key Conventions

- API 调用统一通过 `scripts/chainbase.sh` 封装脚本执行
- 默认使用 `demo` API Key，可通过环境变量 `CHAINBASE_API_KEY` 覆盖
- 默认链为 Ethereum (chain_id=1)，除非用户指定其他链
- SQL API 为异步模式，脚本会自动轮询结果

## Testing

```bash
# 测试 Web3 API
scripts/chainbase.sh /v1/token/top-holders chain_id=1 contract_address=0xdAC17F958D2ee523a2206206994597C13D831ec7 limit=3

# 测试地址标签
scripts/chainbase.sh /v1/address/labels chain_id=1 address=0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045

# 测试 SQL API
scripts/chainbase.sh /query/execute --sql="SELECT * FROM ethereum.blocks LIMIT 1"
```
