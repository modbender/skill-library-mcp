# InvestmentTracker MCP API 问题分析报告

## 🔍 问题发现

### 测试结果
- **API URL**: `https://investmenttracker-ingest-production.up.railway.app/mcp`
- **HTTP状态码**: `500` (服务器内部错误)
- **响应内容**: 空
- **测试时间**: 2026-02-16 23:10 UTC

### 关键发现
1. **连接正常** - 可以建立TCP/TLS连接
2. **认证通过** - 服务器接受请求（返回500而不是401/403）
3. **服务器错误** - HTTP 500表示服务器端处理出错

## 🐛 可能的问题原因

### 1. **MCP服务器配置问题**
```json
// 当前请求格式
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "params": {},
  "id": 1
}
```

**可能问题**:
- MCP服务器期望不同的JSON-RPC格式
- 缺少必需的参数
- 方法名称不正确

### 2. **认证头问题**
```bash
-H 'X-API-Key: it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes'
```

**可能问题**:
- 需要不同的认证头名称（如 `Authorization: Bearer`）
- API密钥格式不正确
- 密钥已过期或无效

### 3. **Content-Type/Accept头问题**
```bash
-H 'Content-Type: application/json'
-H 'Accept: application/json'
```

**可能问题**:
- 需要 `text/event-stream` 而不是 `application/json`
- 需要不同的Content-Type

### 4. **服务器端代码错误**
- MCP服务器处理逻辑有bug
- 数据库连接失败
- 依赖服务不可用

## 🔧 调试建议

### 第一步：检查服务器日志
```bash
# 查看Railway服务器日志
railway logs
```

### 第二步：验证API密钥格式
尝试不同的认证头格式：
```bash
# 方案1: Bearer Token格式
-H 'Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes'

# 方案2: 基本认证
-H 'Authorization: Basic BASE64_ENCODED_KEY'

# 方案3: 自定义头
-H 'X-API-Token: it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes'
```

### 第三步：测试不同的Content-Type
```bash
# 方案1: SSE模式
-H 'Accept: text/event-stream'

# 方案2: 纯文本
-H 'Accept: text/plain'

# 方案3: 所有类型
-H 'Accept: */*'
```

### 第四步：简化请求
```bash
# 最小化请求
curl -v -X POST 'https://investmenttracker-ingest-production.up.railway.app/mcp' \
  -H 'Content-Type: application/json' \
  -d '{}'
```

## 🚀 修复方案

### 方案A：检查MCP服务器实现
1. **查看服务器代码** - 确认JSON-RPC处理逻辑
2. **检查路由配置** - 确认 `/mcp` 端点正确配置
3. **验证工具注册** - 确认工具已正确注册到MCP服务器

### 方案B：调整客户端请求
```python
# 调整后的MCP客户端请求
request = {
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": str(int(time.time() * 1000))  # 字符串ID
}

headers = {
    "Authorization": f"Bearer {api_key}",  # 使用Bearer格式
    "Content-Type": "application/json",
    "Accept": "text/event-stream, application/json"  # 支持多种类型
}
```

### 方案C：添加调试信息
在MCP服务器中添加详细日志：
```javascript
// 示例：Express.js中间件
app.use('/mcp', (req, res, next) => {
  console.log('MCP Request:', {
    method: req.method,
    headers: req.headers,
    body: req.body,
    url: req.url
  });
  next();
});
```

## 📋 测试用例

### 测试1：基础连接测试
```bash
# 只测试连接，不发送数据
curl -v 'https://investmenttracker-ingest-production.up.railway.app/'
```

### 测试2：健康检查端点
```bash
# 检查是否有健康检查端点
curl -v 'https://investmenttracker-ingest-production.up.railway.app/health'
curl -v 'https://investmenttracker-ingest-production.up.railway.app/status'
```

### 测试3：不同HTTP方法
```bash
# 尝试GET请求
curl -v -X GET 'https://investmenttracker-ingest-production.up.railway.app/mcp'

# 尝试OPTIONS请求（查看支持的CORS）
curl -v -X OPTIONS 'https://investmenttracker-ingest-production.up.railway.app/mcp'
```

## 🔍 需要的信息

为了进一步诊断，需要以下信息：

### 1. **服务器端信息**
- MCP服务器的技术栈（Node.js/Python/其他）
- 使用的MCP库/框架
- 服务器日志内容

### 2. **API文档**
- 正确的请求格式
- 认证方式
- 支持的Content-Type
- 可用的工具列表

### 3. **部署信息**
- Railway部署配置
- 环境变量设置
- 依赖服务状态

## 🎯 下一步行动

### 立即行动
1. **检查服务器日志** - 查看500错误的详细原因
2. **验证API密钥** - 确认密钥格式正确
3. **测试简化请求** - 排除复杂参数问题

### 短期修复
1. **修复服务器bug** - 根据日志修复代码
2. **更新客户端** - 调整请求格式
3. **添加健康检查** - 便于监控

### 长期改进
1. **完善错误处理** - 提供有意义的错误信息
2. **添加API文档** - 明确使用方式
3. **实现监控** - 实时监控API状态

## 📊 当前影响

### 对用户的影响
- ✅ 技能功能完整（使用模拟数据）
- ⚠️ 无法获取实时数据
- 🔄 投资分析基于模拟数据

### 对开发的影响
- 🔧 需要修复MCP服务器
- 📝 需要更新API文档
- 🧪 需要添加更多测试

## 💡 临时解决方案

### 在修复期间
1. **继续使用模拟数据** - 保持功能可用
2. **添加数据源标识** - 明确显示"模拟数据"
3. **提供手动更新** - 允许用户手动输入真实数据

### 数据同步方案
```python
class HybridDataManager:
    """混合数据管理器"""
    
    def get_positions(self):
        # 1. 尝试从API获取
        api_data = self._fetch_from_api()
        if api_data:
            return {"source": "api", "data": api_data}
        
        # 2. 尝试从本地缓存获取
        cached_data = self._load_from_cache()
        if cached_data:
            return {"source": "cache", "data": cached_data}
        
        # 3. 使用模拟数据
        return {"source": "simulated", "data": self._generate_simulated_data()}
```

## 📞 联系支持

### 需要协助
1. **服务器访问权限** - 查看日志和配置
2. **API文档** - 了解正确的使用方式
3. **测试环境** - 在非生产环境测试

### 预计时间
- **初步诊断**: 1-2小时
- **问题修复**: 4-8小时
- **全面测试**: 2-4小时

---

**总结：MCP服务器返回HTTP 500错误，需要检查服务器端代码和配置。建议先查看服务器日志，确认具体的错误原因。**