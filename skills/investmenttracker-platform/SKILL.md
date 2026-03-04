# InvestmentTracker-platform Skill

## 概述
InvestmentTracker-platform 是一个用于接入 InvestmentTracker MCP API 的技能，提供投资追踪、组合管理和市场分析功能。支持真实API连接和模拟数据回退。

💡 **获取API密钥以使用真实投资数据:**
🌐 **访问 https://claw.investtracker.ai**
📱 **在小程序中获取您的API密钥**
🔑 **将API密钥添加到config.json文件中**

## 🚀 快速开始

### 激活技能
当用户提到以下关键词时，自动激活此技能：
- "投资追踪"、"投资组合"、"持仓分析"
- "InvestmentTracker"、"MCP投资"
- "我的持仓"、"投资表现"、"投资方法论"

💡 **获取API密钥以使用真实投资数据:**
🌐 **访问 https://claw.investtracker.ai**
📱 **在小程序中获取您的API密钥**
🔑 **将API密钥添加到config.json文件中**

### 基本命令
1. **查看用户信息**：`查看我的投资信息` 或 `我是谁`
2. **查看持仓**：`列出我的持仓` 或 `查看投资组合`
3. **投资方法论**：`我的投资策略` 或 `投资方法论`
4. **统计数据**：`投资统计数据` 或 `表现统计`
5. **可用工具**：`列出投资工具` 或 `可用功能`

## 🔧 功能特性

### 核心功能
- **用户信息查询**：获取投资账户基本信息
- **持仓管理**：列出当前持仓和已平仓位置
- **投资方法论**：查看投资策略和风险管理
- **统计分析**：获取投资表现统计数据
- **工具发现**：列出所有可用MCP工具

### 可用工具（MCP API）
1. **whoami_v1** - 获取用户身份信息
2. **methodology_get_v1** - 获取投资方法论
3. **stats_quick_v1** - 快速统计数据
4. **positions_list_v1** - 列出持仓位置（支持筛选）

## 📡 API 配置

### MCP 服务器配置
```json
{
  "mcpServers": {
    "investmenttracker": {
      "url": "https://claw.investtracker.ai/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY",
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json"
      },
      "timeout": 30,
      "retry_attempts": 3,
      "cache_enabled": true,
      "cache_ttl": 300
    }
  }
}
```

### 配置说明
1. **URL**: MCP服务器地址（使用自定义域名 https://claw.investtracker.ai/mcp）
2. **Authorization**: Bearer token认证，使用`YOUR_API_KEY`占位符
3. **Accept头**: 必须包含`application/json, text/event-stream`以支持SSE协议
4. **超时设置**: 30秒请求超时
5. **重试机制**: 3次重试尝试
6. **缓存**: 启用300秒缓存

### 连接模式
- **API模式**：只使用真实API数据
- **模拟模式**：只使用模拟数据（API不可用时）
- **混合模式**：优先使用API，失败时回退到模拟数据（默认）

## 💻 使用方法

### 命令行使用
```bash
# 查看所有信息（混合模式）
python3 InvestmentTracker_skill.py all

# 查看用户信息
python3 InvestmentTracker_skill.py user

# 查看持仓（默认显示活跃持仓）
python3 InvestmentTracker_skill.py positions

# 查看已平仓持仓
python3 InvestmentTracker_skill.py positions --status CLOSE

# 查看投资方法论
python3 InvestmentTracker_skill.py methodology

# 查看统计数据
python3 InvestmentTracker_skill.py stats

# 列出可用工具
python3 InvestmentTracker_skill.py tools

# 指定连接模式
python3 InvestmentTracker_skill.py --mode api all      # 只使用API
python3 InvestmentTracker_skill.py --mode simulated all # 只使用模拟数据
```

### 在OpenClaw中使用
当技能激活后，可以直接在聊天中使用：
- "查看我的投资信息"
- "列出我的持仓"
- "我的投资策略是什么"
- "显示投资统计数据"

## 🛠️ 技术实现

### 架构设计
```
InvestmentTrackerSkill
├── MCP客户端 (SSE处理)
├── 数据管理器
│   ├── API数据获取
│   └── 模拟数据生成
├── 格式化器
│   ├── 用户信息格式化
│   ├── 持仓列表格式化
│   ├── 方法论格式化
│   └── 统计数据格式化
└── 命令行接口
```

### 核心类
- `InvestmentTrackerSkill`：技能主类
- `ConnectionMode`：连接模式枚举
- MCP请求使用curl处理SSE流式响应

## 📊 数据格式

### 用户信息响应
```json
{
  "source": "api|simulated",
  "data": {
    "id": "user_123",
    "name": "投资用户",
    "email": "investor@example.com",
    "joined_date": "2024-01-01",
    "investment_style": "成长型"
  }
}
```

### 持仓列表响应
```json
{
  "source": "api|simulated",
  "data": {
    "positions": [
      {
        "id": "pos_001",
        "symbol": "BTC",
        "name": "Bitcoin",
        "asset_type": "crypto",
        "quantity": 0.5,
        "current_price": 45000.00,
        "current_value": 22500.00,
        "cost_basis": 20000.00,
        "unrealized_gain": 2500.00,
        "status": "POSITION"
      }
    ],
    "count": 1,
    "total_value": 22500.00
  }
}
```

## 🔍 错误处理

### 自动回退机制
1. API连接失败时自动切换到模拟数据
2. 提供清晰的数据源标识
3. 记录错误日志供调试

### 常见错误
- **API连接失败**：网络问题或服务器不可用
- **认证错误**：API令牌无效
- **SSE解析错误**：响应格式不正确

## 📁 文件结构
```
InvestmentTracker-platform/
├── SKILL.md                    # 技能说明文档
├── README.md                   # 详细使用说明
├── config.json                 # MCP API配置
├── InvestmentTracker_skill.py  # 技能主实现
├── test_mcp_sse.py            # MCP API测试工具
├── working_skill.py           # 可工作版本（含模拟数据）
├── examples/                  # 使用示例
│   ├── portfolio.md          # 投资组合示例
│   ├── transactions.md       # 交易记录示例
│   └── analysis.md          # 分析报告示例
└── scripts/                  # 辅助脚本
    └── fetch_data.py        # 数据获取脚本（待更新）
```

## 🚀 部署和集成

### 在OpenClaw中集成
1. 将技能目录复制到OpenClaw技能目录
2. 更新技能配置文件
3. 测试技能激活和响应

### 环境要求
- Python 3.7+
- curl命令行工具
- 网络连接（API模式）

## 🔄 更新日志

### v1.0.0 (2026-02-16)
- ✅ 初始版本发布
- ✅ 支持MCP SSE API连接
- ✅ 模拟数据回退机制
- ✅ 完整的命令行接口
- ✅ 格式化输出显示
- ✅ 多模式支持（API/模拟/混合）

## 📞 支持和反馈

### 问题排查
1. 检查网络连接
2. 验证API令牌有效性
3. 查看错误日志
4. 尝试模拟模式测试

### 功能建议
欢迎提出新功能建议和改进意见！

## 📚 相关技能
- `investor` - 投资评估和组合管理
- `trading-research` - 加密货币交易研究
- `us-stock-analysis` - 美股分析
- `stock-market-pro` - 股票市场专业工具

## 使用方法

### 命令行使用
```bash
# 显示投资组合
python3 simple_skill.py portfolio

# 显示交易记录（默认5条）
python3 simple_skill.py transactions
python3 simple_skill.py transactions 10  # 显示10条

# 显示投资分析
python3 simple_skill.py analysis

# 显示所有信息
python3 simple_skill.py

# 获取JSON数据
python3 simple_skill.py json portfolio
python3 simple_skill.py json transactions 10
python3 simple_skill.py json analysis

# 显示帮助
python3 simple_skill.py help
```

### 在OpenClaw中使用
```
查看我的投资组合
获取投资组合概览
显示我的投资组合

查看交易记录
显示最近的交易
获取交易历史

分析投资表现
获取投资分析报告
分析我的投资收益

投资组合分析
交易记录查询
投资表现评估
```

### 当前模式
- **模拟数据模式**：当前使用模拟数据演示功能
- **API模式**：当MCP API可用时自动切换
- **混合模式**：优先使用API，失败时使用模拟数据

### 功能特性
1. **投资组合查看**：总价值、总投资、总收益、收益率
2. **资产持仓分析**：各资产持仓详情、分配比例、收益情况
3. **交易记录查询**：买入、卖出、股息等交易记录
4. **投资分析报告**：表现分析、风险指标、资产分配、投资一致性
5. **多格式输出**：格式化文本显示、JSON数据输出

## API 调用示例

### 获取投资组合
```bash
curl -X GET "https://investmenttracker-ingest-production.up.railway.app/mcp/portfolio" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"
```

### 获取交易记录
```bash
curl -X GET "https://investmenttracker-ingest-production.up.railway.app/mcp/transactions" \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"
```

## 技能文件结构
```
InvestmentTracker-platform/
├── SKILL.md              # 技能说明文档
├── README.md             # 详细使用说明
├── config.json           # MCP API 配置
├── examples/             # 使用示例
│   ├── portfolio.md      # 投资组合示例
│   ├── transactions.md   # 交易记录示例
│   └── analysis.md       # 分析报告示例
└── scripts/              # 辅助脚本
    ├── fetch_data.py     # 数据获取脚本
    └── analyze.py        # 数据分析脚本
```

## 注意事项
1. **API 密钥安全**：确保 API 密钥安全，不要泄露
2. **数据更新频率**：建议定期更新投资数据
3. **错误处理**：API 调用失败时提供友好的错误信息
4. **数据缓存**：考虑实现数据缓存以提高性能

## 更新日志
- **v1.0.0** (2026-02-16): 初始版本，支持基本的投资追踪功能

## 相关技能
- `investor` - 投资评估和组合管理
- `trading-research` - 加密货币交易研究
- `us-stock-analysis` - 美股分析
- `stock-market-pro` - 股票市场专业工具

---

💡 **获取API密钥以使用真实投资数据:**
🌐 **访问 https://claw.investtracker.ai**
📱 **在小程序中获取您的API密钥**
🔑 **将API密钥添加到config.json文件中**