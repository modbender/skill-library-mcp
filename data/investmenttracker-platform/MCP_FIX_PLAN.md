# InvestmentTracker MCP API 技能修改方案

## 问题诊断总结

### 核心问题
1. **协议不匹配**: InvestmentTracker 使用 MCP over SSE (Server-Sent Events)，而当前技能使用普通 HTTP/REST 客户端
2. **JSON解析错误**: `"Unterminated string in JSON at position 16738"` - SSE流被当作完整JSON解析
3. **API响应格式**: 需要专门的SSE客户端处理流式响应

### 技术分析
- **响应大小**: 至少16KB（错误位置16738）
- **协议要求**: `Accept: text/event-stream` 头部
- **请求格式**: JSON-RPC 2.0 over SSE

## 修改方案

### 方案一：完整SSE/MCP客户端实现（推荐）

#### 1. 创建新的MCP客户端类
```python
# mcp_client.py
import json
import asyncio
import aiohttp
from typing import AsyncGenerator, Dict, Any

class MCPClient:
    """MCP over SSE 客户端"""
    
    def __init__(self, url: str, auth_token: str):
        self.url = url
        self.auth_token = auth_token
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def connect(self) -> AsyncGenerator[Dict[str, Any], None]:
        """连接到MCP SSE服务器"""
        headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Accept': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url, headers=headers) as response:
                async for line in response.content:
                    if line:
                        event = self._parse_sse_line(line)
                        if event:
                            yield event
    
    async def send_request(self, method: str, params: Dict = None) -> Dict[str, Any]:
        """发送JSON-RPC请求"""
        request_id = f"req_{int(time.time())}"
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": request_id
        }
        
        headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Accept': 'text/event-stream',
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json=request, headers=headers) as response:
                # 处理SSE响应
                results = []
                async for line in response.content:
                    event = self._parse_sse_line(line)
                    if event and event.get('id') == request_id:
                        results.append(event)
                return results
    
    def _parse_sse_line(self, line: bytes) -> Optional[Dict[str, Any]]:
        """解析SSE事件行"""
        try:
            text = line.decode('utf-8').strip()
            if text.startswith('data: '):
                data = text[6:]  # 移除"data: "前缀
                if data:
                    return json.loads(data)
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None
        return None
```

#### 2. 更新技能主文件
```python
# InvestmentTracker技能主文件修改
from mcp_client import MCPClient

class InvestmentTrackerSkill:
    def __init__(self):
        self.client = MCPClient(
            url="https://investmenttracker-ingest-production.up.railway.app/mcp",
            auth_token="it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"
        )
    
    async def get_portfolio(self):
        """获取投资组合"""
        # 使用正确的MCP方法
        response = await self.client.send_request(
            method="resources/read",
            params={"uri": "investment://portfolio"}
        )
        return self._format_portfolio(response)
    
    async def get_transactions(self, limit: int = 50):
        """获取交易记录"""
        response = await self.client.send_request(
            method="resources/read",
            params={"uri": f"investment://transactions?limit={limit}"}
        )
        return self._format_transactions(response)
```

### 方案二：简化版SSE处理（快速修复）

#### 1. 修改现有fetch_data.py
```python
# 在现有fetch_data.py中添加SSE支持
import json
import requests
from typing import Generator, Dict, Any

class SimpleSSEClient:
    """简单的SSE客户端（同步版本）"""
    
    def __init__(self, url: str, auth_token: str):
        self.url = url
        self.headers = {
            'Authorization': f'Bearer {auth_token}',
            'Accept': 'text/event-stream',
            'Cache-Control': 'no-cache'
        }
    
    def stream_events(self) -> Generator[Dict[str, Any], None, None]:
        """流式读取SSE事件"""
        response = requests.get(self.url, headers=self.headers, stream=True)
        
        buffer = ""
        for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
            if chunk:
                buffer += chunk
                
                # 处理SSE事件（以\n\n分隔）
                while "\n\n" in buffer:
                    event_text, buffer = buffer.split("\n\n", 1)
                    
                    # 跳过空行和注释
                    if not event_text.strip() or event_text.startswith(":"):
                        continue
                    
                    # 解析事件
                    event = self._parse_event(event_text)
                    if event:
                        yield event
    
    def _parse_event(self, event_text: str) -> Optional[Dict[str, Any]]:
        """解析SSE事件文本"""
        lines = event_text.strip().split('\n')
        data_lines = []
        
        for line in lines:
            if line.startswith('data: '):
                data_lines.append(line[6:])
        
        if data_lines:
            try:
                # 合并多行数据
                data = '\n'.join(data_lines)
                return json.loads(data)
            except json.JSONDecodeError:
                return None
        
        return None
```

### 方案三：使用现有MCP库（最稳定）

#### 1. 安装MCP客户端库
```bash
# 方案A: 使用Node.js MCP SDK
npm install @modelcontextprotocol/sdk

# 方案B: 使用Python MCP客户端
pip install mcp-client
```

#### 2. 集成到技能中
```python
# 使用Python MCP客户端
from mcp import Client
import asyncio

async def main():
    client = Client(
        transport="sse",
        url="https://investmenttracker-ingest-production.up.railway.app/mcp",
        headers={
            "Authorization": "Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"
        }
    )
    
    await client.connect()
    
    # 列出可用工具
    tools = await client.list_tools()
    print("可用工具:", tools)
    
    # 调用工具
    result = await client.call_tool("get_portfolio", {})
    print("投资组合:", result)
```

## 具体修改步骤

### 第一步：测试API响应
```bash
# 1. 保存完整响应
curl -s \
  -H "Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes" \
  -H "Accept: text/event-stream" \
  "https://investmenttracker-ingest-production.up.railway.app/mcp" \
  > response_raw.txt

# 2. 分析响应格式
head -c 200 response_raw.txt
echo "..."
tail -c 200 response_raw.txt

# 3. 检查第16738个字符附近
sed -n '16700,16800p' response_raw.txt
```

### 第二步：选择实现方案
根据API响应格式选择：
- 如果响应是标准SSE格式 → 使用方案一或二
- 如果响应格式复杂 → 使用方案三（MCP库）
- 如果API有文档 → 按照文档实现

### 第三步：修改技能文件

#### 需要修改的文件：
1. **SKILL.md** - 更新使用说明
2. **config.json** - 添加SSE配置
3. **scripts/fetch_data.py** - 重写为SSE客户端
4. **新增 mcp_client.py** - MCP客户端实现
5. **新增 sse_utils.py** - SSE工具函数

#### 修改内容：
```python
# 在SKILL.md中添加
## MCP SSE 协议说明
- 使用 Server-Sent Events (SSE) 流式传输
- JSON-RPC 2.0 格式
- 需要专门的SSE客户端

# 在config.json中添加
{
  "mcp": {
    "protocol": "sse",
    "requires_sse_client": true,
    "event_stream_timeout": 30
  }
}
```

### 第四步：测试修改

#### 测试脚本：
```python
# test_mcp_fix.py
import asyncio
from mcp_client import MCPClient

async def test_fix():
    client = MCPClient(
        url="https://investmenttracker-ingest-production.up.railway.app/mcp",
        auth_token="it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"
    )
    
    print("测试连接...")
    async for event in client.connect():
        print(f"收到事件: {event}")
        break  # 只显示第一个事件
    
    print("测试请求...")
    response = await client.send_request("tools/list", {})
    print(f"工具列表: {response}")

if __name__ == "__main__":
    asyncio.run(test_fix())
```

## 错误处理改进

### 1. 流式JSON解析
```python
def parse_streaming_json(stream):
    """安全解析流式JSON"""
    decoder = json.JSONDecoder()
    buffer = ""
    
    for chunk in stream:
        buffer += chunk
        while buffer:
            try:
                obj, idx = decoder.raw_decode(buffer)
                yield obj
                buffer = buffer[idx:].lstrip()
            except json.JSONDecodeError as e:
                # 检查是否是"未终止字符串"错误
                if "Unterminated string" in str(e):
                    # 等待更多数据
                    break
                else:
                    # 其他JSON错误
                    raise
```

### 2. 连接重试机制
```python
class ResilientMCPClient:
    def __init__(self, max_retries=3, backoff_factor=2):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
    
    async def connect_with_retry(self):
        for attempt in range(self.max_retries):
            try:
                return await self._connect()
            except (TimeoutError, ConnectionError) as e:
                if attempt == self.max_retries - 1:
                    raise
                wait_time = self.backoff_factor ** attempt
                await asyncio.sleep(wait_time)
```

## 时间估计

| 任务 | 时间估计 | 优先级 |
|------|----------|--------|
| 分析API响应格式 | 1-2小时 | 高 |
| 实现SSE客户端 | 4-6小时 | 高 |
| 集成到现有技能 | 2-3小时 | 中 |
| 测试和调试 | 3-4小时 | 高 |
| 文档更新 | 1-2小时 | 低 |

**总计**: 11-17小时

## 风险评估

### 高风险：
1. API响应格式不符合标准SSE
2. 需要特定的MCP协议扩展
3. 认证或权限问题

### 缓解措施：
1. 先进行小规模测试
2. 准备备选方案（使用MCP库）
3. 联系API提供商获取支持

## 成功标准

1. ✅ 能够建立SSE连接
2. ✅ 能够发送JSON-RPC请求
3. ✅ 能够解析SSE事件流
4. ✅ 能够获取投资数据
5. ✅ 错误处理完善

## 备选方案

如果MCP API调试困难，考虑：
1. **使用模拟数据** - 创建本地模拟的InvestmentTracker
2. **集成其他投资API** - 使用Yahoo Finance、Alpha Vantage等
3. **简化功能** - 只实现核心的投资组合查看功能

---

*最后更新: 2026-02-16*
*状态: 等待实施*