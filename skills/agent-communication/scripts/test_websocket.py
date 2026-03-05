#!/usr/bin/env python3
"""WebSocket通信完整测试"""

import asyncio
import json
import time
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/agent-communication/scripts')

try:
    import websockets
except ImportError:
    print("安装websockets: pip install websockets")
    sys.exit(1)

SERVER = "ws://localhost:8765"

async def test_agent(agent_id: str, messages_received: list):
    """测试Agent连接"""
    latency_results = []
    
    async with websockets.connect(SERVER) as ws:
        # 注册
        await ws.send(json.dumps({"type": "register", "agent_id": agent_id}))
        response = await ws.recv()
        print(f"[{agent_id}] 注册成功")
        
        # 测试发送消息
        start_time = time.time()
        await ws.send(json.dumps({
            "type": "send",
            "from": agent_id,
            "to": "main",
            "message": f"{agent_id}的测试消息",
            "priority": "normal"
        }))
        response = await ws.recv()
        latency = (time.time() - start_time) * 1000
        latency_results.append(latency)
        print(f"[{agent_id}] 发送延迟: {latency:.2f}ms")
        
        # 监听消息
        try:
            while True:
                msg = await asyncio.wait_for(ws.recv(), timeout=2)
                data = json.loads(msg)
                if data.get("type") == "message":
                    messages_received.append({
                        "agent": agent_id,
                        "from": data.get("from"),
                        "message": data.get("message"),
                        "latency": latency
                    })
                    print(f"[{agent_id}] 收到消息: {data.get('from')} -> {data.get('message')}")
        except asyncio.TimeoutError:
            pass
        
        return latency_results

async def main():
    print("=== WebSocket通信测试 ===\n")
    
    messages = []
    
    # 并行测试PM、Dev、Test
    print("测试1: 多Agent连接和消息发送")
    print("-" * 40)
    
    results = await asyncio.gather(
        test_agent("pm", messages),
        test_agent("dev", messages),
        test_agent("test", messages)
    )
    
    # 统计延迟
    all_latencies = [l for r in results for l in r]
    avg_latency = sum(all_latencies) / len(all_latencies) if all_latencies else 0
    
    print("\n" + "=" * 40)
    print("测试结果:")
    print(f"  - 参与Agent: 3 (pm, dev, test)")
    print(f"  - 消息发送: {len(all_latencies)} 条")
    print(f"  - 平均延迟: {avg_latency:.2f}ms")
    print(f"  - 最大延迟: {max(all_latencies):.2f}ms" if all_latencies else "")
    print(f"  - 最小延迟: {min(all_latencies):.2f}ms" if all_latencies else "")
    
    if avg_latency < 50:
        print(f"  - 性能评估: ✅ 优秀 (<50ms)")
    elif avg_latency < 100:
        print(f"  - 性能评估: ✅ 良好 (<100ms)")
    else:
        print(f"  - 性能评估: ⚠️ 需优化")
    
    print("\n" + "=" * 40)
    print("✅ 测试完成!")

if __name__ == "__main__":
    asyncio.run(main())