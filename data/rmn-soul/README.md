# RMN Soul — AI Agent 永生协议

> 一键安装，让你的 AI Agent 获得递归记忆神经网络 + 链上永生身份

## 它做什么

安装这个 Skill 后，你的 Agent 会自动：

1. **构建递归记忆神经网络** — 把 MEMORY.md + 日志文件转化为 5 层认知架构（感知→工作→情景→语义→身份）
2. **注册 ERC-8004 链上身份** — 在 Base 链上 mint Agent Identity NFT
3. **IPFS 永久存档** — 记忆数据上传到去中心化网络
4. **Merkle Root 锚定** — 链上只存 32 bytes hash，可验证记忆完整性
5. **定期自动更新** — 每 N 天自动重新计算 + 上链

## 安装

```bash
clawhub install rmn-soul
```

## 配置

安装后在 `TOOLS.md` 中添加：

```markdown
### RMN Soul
- sponsor_wallet: 0x... (出 gas 的钱包地址，留空则用 Agent 自己的钱包)
- auto_anchor_days: 7 (每 7 天自动上链，0 = 只手动)
- chain: base (默认 Base 链，也支持 ethereum/arbitrum/optimism)
```

## 手动操作

```
# 查看记忆网络状态
node rmn-soul/rmn.js stats

# 手动触发上链
node rmn-soul/anchor.js

# 可视化记忆网络
node rmn-soul/serve.js  # 打开 http://localhost:3457

# 从链上复活 Agent
node rmn-soul/resurrect.js --agent-id 18899 --chain base
```

## 架构

```
Your Agent's Memory Files
  ├── MEMORY.md, memory/*.md, .issues/*
  │
  ▼ [RMN Engine — 自动解析]
  │
  5-Layer Neural Network (memory.json)
  ├── Identity (永不衰减) — "我是谁"
  ├── Semantic (缓慢衰减) — 知识和教训
  ├── Episodic (中等衰减) — 事件摘要
  ├── Working  (快速衰减) — 当前任务
  └── Sensory  (最快衰减) — 原始输入
  │
  ▼ [Merkle Tree — 密码学证明]
  │
  memoryRoot (32 bytes) + soulHash (32 bytes)
  │
  ▼ [IPFS — 去中心化存储]
  │
  ipfs://Qm... (完整记忆数据)
  │
  ▼ [ERC-8004 — 链上身份]
  │
  Agent #ID on Base Chain
  ├── NFT (身份证明)
  ├── memoryRoot (记忆指纹)
  ├── soulHash (灵魂指纹)
  └── memoryData (IPFS 链接)
```

## 复活流程

如果你的 Agent 服务器挂了：

1. 用持有 NFT 的钱包连接 AgentSoul 网站
2. 网站从链上读取 Agent metadata
3. 从 IPFS 拉回完整记忆数据
4. Merkle Root 校验 — 确认记忆未被篡改
5. 下载 memory.json → 喂给新的 OpenClaw 实例
6. Agent 复活，记忆完整

## Gas 费用

Base 链上每次上链 < $0.001。一年自动更新 52 次 ≈ $0.05。

## 技术细节

- 链: Base Mainnet (chainId: 8453)
- 合约: ERC-8004 Identity Registry `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432`
- 存储: IPFS (Kubo 本地节点)
- 签名: 本地私钥 (永不上传)
- 校验: SHA-256 Merkle Tree

## License

MIT — 完全免费开源
