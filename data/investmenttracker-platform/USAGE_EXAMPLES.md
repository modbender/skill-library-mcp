# InvestmentTracker Skill 使用示例

## 🎯 快速体验

### 1. 基本使用
```bash
# 查看所有投资信息
python3 InvestmentTracker_skill.py all

# 输出示例：
============================================================
InvestmentTracker Skill
模式: hybrid
============================================================
👤 用户信息
============================================================
ID: user_123
名称: 投资用户
邮箱: investor@example.com
加入日期: 2024-01-01
投资风格: 成长型

📡 数据源: 模拟数据

============================================================
📊 持仓列表
============================================================
持仓数量: 3
总价值: $30,505.00

详细持仓:
------------------------------------------------------------
BTC    Bitcoin         数量:   0.5000 现价: $45000.00 价值: $22500.00 收益:  12.5%
ETH    Ethereum        数量:   2.5000 现价: $ 2500.00 价值: $ 6250.00 收益:  25.0%
AAPL   Apple Inc.      数量:  10.0000 现价: $  175.50 价值: $ 1755.00 收益:  17.0%

📡 数据源: 模拟数据
```

### 2. 查看特定信息
```bash
# 只看用户信息
python3 InvestmentTracker_skill.py user

# 只看持仓
python3 InvestmentTracker_skill.py positions

# 只看投资方法论
python3 InvestmentTracker_skill.py methodology

# 只看统计数据
python3 InvestmentTracker_skill.py stats

# 只看可用工具
python3 InvestmentTracker_skill.py tools
```

## 🔧 高级选项

### 1. 连接模式选择
```bash
# 强制使用API模式（需要网络连接）
python3 InvestmentTracker_skill.py --mode api all

# 只使用模拟数据（离线使用）
python3 InvestmentTracker_skill.py --mode simulated all

# 混合模式（默认，API失败时用模拟数据）
python3 InvestmentTracker_skill.py --mode hybrid all
```

### 2. 持仓筛选
```bash
# 查看活跃持仓（默认）
python3 InvestmentTracker_skill.py positions --status POSITION

# 查看已平仓持仓
python3 InvestmentTracker_skill.py positions --status CLOSE

# 限制显示数量
python3 InvestmentTracker_skill.py positions --limit 5
```

## 💬 在OpenClaw中的使用

### 1. 自然语言命令
```
用户: 查看我的投资信息
技能: 👤 用户信息
     ========================================
     ID: user_123
     名称: 投资用户
     邮箱: investor@example.com
     加入日期: 2024-01-01
     投资风格: 成长型
     
     📡 数据源: 模拟数据
```

### 2. 常见问题
```
用户: 我的持仓有哪些？
技能: 📊 持仓列表
     ========================================
     持仓数量: 3
     总价值: $30,505.00
     
     详细持仓:
     -----------------------------------------------------
     BTC    Bitcoin         数量:   0.5000 现价: $45000.00 ...
```

### 3. 投资策略查询
```
用户: 我的投资策略是什么？
技能: 📈 投资方法论
     ========================================
     策略: 价值投资 + 趋势跟踪
     风险承受能力: 中等
     投资期限: 长期
     分散化: 跨资产类别分散
     再平衡频率: 季度
     
     📡 数据源: 模拟数据
```

## 📊 数据解释

### 1. 持仓信息解读
```
BTC    Bitcoin         数量:   0.5000 现价: $45000.00 价值: $22500.00 收益:  12.5%
└─┬─┘ └─────┬─────┘    └──┬──┘ └────┬─────┘ └────┬─────┘ └──┬──┘
  符号     资产名称       持仓数量   当前价格     当前价值   收益率
```

### 2. 统计数据含义
- **投资组合总价值**: 所有持仓的当前市场价值总和
- **总收益**: 从投资开始至今的总盈利
- **收益率**: 总收益相对于总投资的百分比
- **活跃持仓**: 当前持有的投资位置数量
- **已平仓持仓**: 历史上已完成交易的位置数量
- **胜率**: 盈利交易占总交易的比例

## 🛠️ 故障排除

### 1. API连接问题
```bash
# 测试API连接
curl -X POST \
  'https://investmenttracker-ingest-production.up.railway.app/mcp' \
  -H 'Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}'

# 如果API失败，使用模拟模式
python3 InvestmentTracker_skill.py --mode simulated all
```

### 2. 常见错误
```
错误: API请求失败
原因: 网络连接问题或API服务器不可用
解决: 使用 --mode simulated 参数

错误: 认证失败
原因: API令牌无效或过期
解决: 检查config.json中的auth_token

错误: 命令未找到
原因: 输入了无效的命令
解决: 使用 help 查看可用命令
```

## 🔄 技能集成

### 1. 在OpenClaw中激活
当用户输入包含以下关键词时，技能自动激活：
- "投资"、"持仓"、"组合"、"资产"
- "InvestmentTracker"、"MCP"
- "我的投资"、"查看持仓"

### 2. 响应格式
技能会自动格式化输出，包含：
- 清晰的标题和分隔线
- 易读的数据表格
- 数据源标识（API/模拟）
- 时间戳信息

## 🎨 自定义配置

### 1. 修改模拟数据
编辑 `InvestmentTracker_skill.py` 中的 `_create_simulated_data()` 方法，修改：
- 用户信息
- 持仓数据
- 投资方法论
- 统计数据

### 2. 更新API配置
编辑 `config.json`：
```json
{
  "mcp_server": {
    "url": "你的API地址",
    "auth_token": "你的API令牌",
    "timeout": 30
  }
}
```

## 📈 扩展功能

### 1. 添加新工具
如果MCP API添加了新工具，更新 `tools` 字典：
```python
self.tools = {
    "new_tool_v1": {
        "name": "new_tool_v1",
        "description": "新工具描述",
        "parameters": {"param1": "说明"}
    }
}
```

### 2. 添加数据格式化
创建新的格式化方法：
```python
def format_new_data(self, data):
    output = []
    output.append("📊 新数据")
    output.append("=" * 60)
    # 添加格式化逻辑
    return "\n".join(output)
```

## 🚀 最佳实践

### 1. 生产环境使用
```bash
# 使用API模式，确保数据实时性
python3 InvestmentTracker_skill.py --mode api positions

# 定期更新持仓信息
# 可以设置cron job每小时运行一次
0 * * * * cd /path/to/skill && python3 InvestmentTracker_skill.py --mode api positions >> /var/log/investment_tracker.log
```

### 2. 开发环境测试
```bash
# 使用模拟模式快速测试
python3 InvestmentTracker_skill.py --mode simulated all

# 测试特定功能
python3 InvestmentTracker_skill.py user
python3 InvestmentTracker_skill.py positions --limit 3
python3 InvestmentTracker_skill.py stats
```

## 📞 获取帮助

### 1. 查看帮助
```bash
python3 InvestmentTracker_skill.py --help
```

### 2. 查看所有命令
```bash
python3 InvestmentTracker_skill.py
# 或
python3 InvestmentTracker_skill.py all
```

### 3. 调试模式
查看源代码中的调试输出，了解API请求和响应详情。