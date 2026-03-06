#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IMA Skill - AI 搜索与知识库助手 (Network Injection + DOM Extraction)
"""

import urllib.request
import json
import sys
import time
import subprocess
import os
import argparse
import urllib.parse
import select
import io
import re

# 强制 stdout 使用 UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    import websocket
except ImportError:
    print("Error: websocket-client module not found.", file=sys.stderr)
    sys.exit(1)

# 配置加载路径
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

# 默认配置
CDP_HOST = "127.0.0.1"
CDP_PORT = 8315
POSSIBLE_PATHS = [
    "/Applications/ima.copilot.app/Contents/MacOS/ima.copilot",
    os.path.expanduser("~/Applications/ima.copilot.app/Contents/MacOS/ima.copilot")
]
APP_PATH = None
for p in POSSIBLE_PATHS:
    if os.path.exists(p):
        APP_PATH = p
        break

def get_knowledge_id():
    """从配置文件获取知识库 ID"""
    # 优先检查环境变量
    env_id = os.environ.get("IMA_KNOWLEDGE_ID")
    if env_id: return env_id
    
    # 检查 Skill 目录下的配置
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config.get("knowledge_id")
        except Exception as e:
            print(f"Warning: Failed to load config: {e}", file=sys.stderr)
            
    return None

def is_port_open(host, port):
    try:
        url = f"http://{host}:{port}/json/version"
        with urllib.request.urlopen(url, timeout=1) as response:
            return response.status == 200
    except:
        return False

def launch_app():
    if not APP_PATH:
        print("Error: App not found", file=sys.stderr)
        sys.exit(1)
    subprocess.Popen([APP_PATH, f"--remote-debugging-port={CDP_PORT}", "--remote-allow-origins=*"], 
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(15):
        time.sleep(1)
        if is_port_open(CDP_HOST, CDP_PORT): return True
    return False

def create_new_tab():
    url = f"http://{CDP_HOST}:{CDP_PORT}/json/new"
    try:
        req = urllib.request.Request(url, method='PUT')
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error creating tab: {e}", file=sys.stderr)
        sys.exit(1)

def run_search(query, knowledge_mode=False, autoclose=False):
    if not is_port_open(CDP_HOST, CDP_PORT):
        print("Starting ima...", file=sys.stderr)
        launch_app()
    
    tab = create_new_tab()
    ws_url = tab['webSocketDebuggerUrl']
    ws = websocket.create_connection(ws_url)
    
    kid = None
    if knowledge_mode:
        kid = get_knowledge_id()
        if not kid:
            print(f"Error: Knowledge ID missing. Please configure {CONFIG_FILE}", file=sys.stderr)
            ws.close()
            return

    # 1. 开启 Network 拦截 (最稳健的注入方式)
    ws.send(json.dumps({"id": 1, "method": "Network.enable"}))
    if knowledge_mode:
        print(f"Injecting Knowledge ID: {kid[:4]}***", file=sys.stderr)
        ws.send(json.dumps({
            "id": 2, 
            "method": "Network.setRequestInterception", 
            "params": {"patterns": [{"urlPattern": "*cgi-bin/assistant/qa*"}]}
        }))
    
    # 2. 导航
    target_url = f"https://ima.qq.com/ai-search?query={urllib.parse.quote(query)}"
    print(f"Navigating to: {target_url}", file=sys.stderr)
    ws.send(json.dumps({"id": 3, "method": "Page.navigate", "params": {"url": target_url}}))
    
    target_request_id = None
    request_hijacked = False
    
    start_time = time.time()
    # 增加超时，防止长文本生成超时
    while time.time() - start_time < 90:
        try:
            r, _, _ = select.select([ws.sock], [], [], 0.1)
            if not r: continue
            
            msg = ws.recv()
            data = json.loads(msg)
            method = data.get("method")
            params = data.get("params", {})
            
            # === 注入逻辑 (Network) ===
            if method == "Network.requestIntercepted":
                req_id = params["interceptionId"]
                post_data = params["request"].get("postData")
                
                try:
                    if post_data and knowledge_mode:
                        body = json.loads(post_data)
                        # 注入知识库参数
                        body["command_info"] = {
                            "type": 14,
                            "knowledge_qa_info": {"knowledge_ids": [kid]}
                        }
                        # 这里 Network.continueInterceptedRequest 直接接受字符串，不需要 base64
                        new_body_str = json.dumps(body)
                        
                        ws.send(json.dumps({
                            "id": 10,
                            "method": "Network.continueInterceptedRequest",
                            "params": {
                                "interceptionId": req_id,
                                "postData": new_body_str 
                            }
                        }))
                        request_hijacked = True
                        print("Injection successful.", file=sys.stderr)
                    else:
                        ws.send(json.dumps({"id": 11, "method": "Network.continueInterceptedRequest", "params": {"interceptionId": req_id}}))
                except:
                    ws.send(json.dumps({"id": 12, "method": "Network.continueInterceptedRequest", "params": {"interceptionId": req_id}}))

            # === 结果监听逻辑 ===
            # 锁定目标 RequestID
            elif method == "Network.responseReceived":
                if "cgi-bin/assistant/qa" in params["response"]["url"]:
                    target_request_id = params["requestId"]

            # 流传输结束：这是抓取的最佳时机
            elif method == "Network.loadingFinished":
                if target_request_id and params["requestId"] == target_request_id:
                    print("Stream finished. Waiting 5s for DOM render...", file=sys.stderr)
                    time.sleep(5) # 给 React 渲染留时间
                    
                    # 使用 DOM 抓取 (完美编码)
                    dom_script = """
                    (function() {
                        function getDeepText(root) {
                            if (!root) return "";
                            if (root.nodeType === 1) {
                                const style = window.getComputedStyle(root);
                                if (style.display === 'none' || style.visibility === 'hidden') return "";
                                if (root.tagName === 'SCRIPT' || root.tagName === 'STYLE') return "";
                            }
                            let text = "";
                            if (root.shadowRoot) text += getDeepText(root.shadowRoot);
                            if (root.childNodes) {
                                root.childNodes.forEach(node => {
                                    if (node.nodeType === 3) text += node.nodeValue;
                                    else if (node.nodeType === 1) {
                                        text += getDeepText(node);
                                        const d = window.getComputedStyle(node).display;
                                        if (d === 'block' || d === 'flex') text += "\\n";
                                    }
                                });
                            }
                            return text;
                        }
                        return getDeepText(document.body);
                    })()
                    """
                    ws.send(json.dumps({
                        "id": 88,
                        "method": "Runtime.evaluate",
                        "params": {"expression": dom_script, "returnByValue": True}
                    }))

            # 处理 DOM 结果
            elif data.get("id") == 88:
                if "result" in data and "result" in data["result"]:
                    dom_text = data["result"]["result"].get("value", "")
                    # 简单过滤 loading 状态
                    if len(dom_text) > 100:
                        final_text = re.sub(r'\\n\\s*\\n', '\\n\\n', dom_text.strip())
                        print("\n=== IMA RESULT ===")
                        print(final_text[:3000])
                        break
                    else:
                        print("Content too short, waiting...", file=sys.stderr)
                        # 如果内容太短，可能是渲染还没完，稍微再试一次
                        time.sleep(2)
                        ws.send(json.dumps({
                            "id": 88,
                            "method": "Runtime.evaluate",
                            "params": {"expression": dom_script, "returnByValue": True}
                        }))

        except Exception as e:
            pass
            
    # 如果注入成功了，关闭拦截，防止影响后续页面交互
    if request_hijacked:
        ws.send(json.dumps({"id": 20, "method": "Network.disable"}))
        
    ws.close()
    if autoclose: close_app()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="搜索查询")
    parser.add_argument("--autoclose", type=str, default="false")
    args = parser.parse_args()
    
    clean = args.query
    use_k = False
    if "@个人知识库" in args.query or "@knowledge" in args.query:
        use_k = True
        clean = args.query.replace("@个人知识库", "").replace("@knowledge", "").strip()
        
    run_search(clean, use_k, args.autoclose.lower()=="true")
