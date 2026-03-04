# McDonald's Order Skill (麦当劳点餐助手)

## ⚠️ SECURITY WARNING

**This skill requires sensitive permissions:**
- 🔑 **API Token** (MCD_TOKEN) - Access to your McDonald's account
- 💻 **Shell Access** (execute_bash) - Can run system commands

**Before installation:**
1. ✅ Review the source code in SKILL.md
2. ✅ Read [SECURITY.md](SECURITY.md) for detailed security considerations
3. ✅ Only install from trusted sources (official Anthropic repository)
4. ✅ Verify all curl commands only target `mcp.mcd.cn`

**Risk**: If this skill is from an untrusted source, it could potentially exfiltrate your API token or execute malicious commands.

**Recommendation**: Only proceed if you trust the skill origin and have reviewed the code.

---

## 📦 技能信息

- **名称**: mcdonald-order
- **版本**: 2.0.0
- **作者**: Kiro Skill Creator
- **分类**: 生活服务 / 美食外卖
- **标签**: 麦当劳、优惠券、外卖、营养查询

## 🎯 功能特性

### 核心功能
1. **优惠券管理** - 查询、领取、查看已有优惠券
2. **外卖点餐** - 完整的下单流程（地址→菜单→价格→下单）
3. **营养查询** - 160+餐品的详细营养数据，支持热量控制套餐搭配
4. **活动日历** - 查看麦当劳促销活动
5. **订单追踪** - 查询订单状态和配送进度

### 技能亮点
- ✅ **实战验证**: 已通过真实API测试，成功完成领券、点餐、查询等操作
- ✅ **营养专业**: 提供完整营养成分表（热量、蛋白质、脂肪、碳水），支持减肥套餐推荐
- ✅ **流程完整**: 严格遵循下单流程，避免常见错误（如跳过地址查询）
- ✅ **价格准确**: 自动转换价格单位（分→元），显示完整费用明细
- ✅ **优惠智能**: 自动匹配门店可用优惠券

## 📊 评估结果

### 测试通过率
- **使用技能**: 93.3% (14/15)
- **不使用技能**: 26.7% (4/15)
- **提升幅度**: +66.6%

### 测试场景
1. ✅ 优惠券领取流程 - 100% 通过
2. ✅ 外卖下单流程 - 100% 通过
3. ✅ 营养搭配查询 - 80% 通过（已优化）

## 🚀 安装使用

### ⚠️ 安全须知

**重要**: 此技能需要访问您的麦当劳账户，请注意：

1. **凭证保护**
   - `MCD_TOKEN` 是您的 API 凭证，请妥善保管
   - 不要在公共场合分享或展示 Token
   - 定期更换 Token 以提高安全性

2. **操作确认**
   - 技能会在以下操作前**要求您确认**：
     - ✅ 领取优惠券
     - ✅ 创建订单
     - ✅ 使用优惠券
   - 价格计算后必须等待您确认才会下单

3. **自主使用限制**
   - 不建议在无人监督的自动化场景中使用
   - 建议每次使用时人工审核关键操作

### 前置要求
1. 访问 https://mcp.mcd.cn 注册并获取 API Token
2. 设置环境变量：
   ```bash
   # 必需：API 认证 Token
   export MCD_TOKEN="your_token_here"
   
   # 可选：自定义 MCP 服务地址（默认：https://mcp.mcd.cn）
   export MCD_MCP_URL="https://mcp.mcd.cn"
   ```

### 安装方法
```bash
# 解压技能包
tar -xzf mcdonald-order-skill.tar.gz -C ~/.kiro/skills/

# 或直接从仓库安装
kiro-cli skill install mcdonald-order
```

### 使用示例

**查询优惠券**
```
用户: 今天麦当劳有什么优惠券？
助手: [自动调用 available-coupons 查询并展示]
```

**点外卖**
```
用户: 我想点麦乐送
助手: [引导完成：地址选择 → 菜单浏览 → 价格计算 → 确认下单]
```

**营养查询**
```
用户: 我在减肥，想吃点低热量的
助手: [展示营养数据表格，推荐低热量套餐组合]
```

## 📝 技能结构

```
mcdonald-order/
├── SKILL.md           # 主技能文件（包含完整工作流和工具说明）
└── evals/
    └── evals.json     # 测试用例（3个核心场景）
```

## 🔧 技术细节

### 安全机制

**用户确认流程**：
```
1. 查询操作（只读）→ 无需确认
   - available-coupons
   - query-my-coupons
   - query-meals
   - list-nutrition-foods
   - query-order

2. 写入操作（修改数据）→ 必须确认
   - auto-bind-coupons → 询问 "需要帮你一键领取吗？"
   - calculate-price → 显示价格，询问 "确认下单吗？"
   - create-order → 仅在用户明确确认后执行
```

**Token 保护**：
- Token 仅用于 Authorization header
- 不会在输出中显示或记录
- 错误信息不包含 Token 内容

### API 调用方式
通过 MCP (Model Context Protocol) 调用麦当劳中国服务：
```bash
curl -s -X POST "https://mcp.mcd.cn" \
  -H "Authorization: Bearer ${MCD_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"TOOL_NAME","arguments":{...}},"id":1}'
```

### 关键工作流

**外卖下单流程**（必须按顺序）：
1. `delivery-query-addresses` - 获取地址和门店信息
2. `query-meals` - 查询菜单
3. `calculate-price` - 计算价格（等待用户确认）
4. `create-order` - 创建订单

**常见陷阱**：
- ❌ 跳过地址查询直接查菜单
- ❌ 价格单位混淆（API返回分，需转换为元）
- ❌ 未等用户确认就下单

## 📈 优化历程

### Iteration 1 → 2 改进
1. **营养信息增强** - 添加完整营养成分表格示例
2. **描述优化** - 更"pushy"的触发描述，提高准确率
3. **工作流明确** - 强调步骤依赖关系和"为什么"
4. **实战验证** - 通过真实API测试验证所有功能

## 🎓 学习价值

这个技能展示了：
- ✅ 如何设计多步骤工作流
- ✅ 如何处理API依赖关系
- ✅ 如何格式化和展示结构化数据
- ✅ 如何通过评估迭代改进技能

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

- 技能问题: 提交 GitHub Issue
- MCP Token: https://mcp.mcd.cn
- 麦当劳客服: 400-851-7517

---

**注意**: 此技能仅用于学习和个人使用，请遵守麦当劳服务条款。
