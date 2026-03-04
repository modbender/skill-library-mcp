"""
QST Memory Web UI

Flask Web 界面。

功能：
- 記憶列表管理
- 對話上下文查看
- 統計儀表板
- 檢索測試
"""

from flask import Flask, render_template, request, jsonify
from typing import Dict, List, Any
import json
import os
from datetime import datetime

# ===== Flask App =====
app = Flask(__name__)

# ===== 配置 =====
app.config['SECRET_KEY'] = 'qst-memory-secret-key'


# ===== API 路由 =====

@app.route('/')
def index():
    """主頁面"""
    return render_template('index.html')


@app.route('/api/memories')
def api_memories():
    """獲取記憶列表"""
    try:
        from qst_memory import QSTMemory
        memory = QSTMemory()
        stats = memory.get_stats()
        
        memories = []
        for mid, mem in memory.core.memories.items():
            memories.append({
                "id": mid,
                "content": mem.content[:100],
                "coherence": mem.coherence,
                "dsi_level": mem.dsi_level,
                "timestamp": mem.timestamp.isoformat()
            })
        
        return jsonify({
            "success": True,
            "memories": memories,
            "stats": stats
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


@app.route('/api/retrieve', methods=['POST'])
def api_retrieve():
    """檢索 API"""
    try:
        data = request.json
        query = data.get('query', '')
        top_k = data.get('top_k', 5)
        
        from qst_memory import QSTMemory
        memory = QSTMemory()
        results = memory.retrieve(query, top_k=top_k)
        
        return jsonify({
            "success": True,
            "results": [
                {
                    "content": r.memory.content,
                    "score": r.total_score,
                    "coherence": r.memory.coherence,
                    "dsi_level": r.memory.dsi_level
                }
                for r in results
            ]
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


@app.route('/api/store', methods=['POST'])
def api_store():
    """存儲 API"""
    try:
        data = request.json
        content = data.get('content', '')
        context = data.get('context', None)
        
        from qst_memory import QSTMemory
        memory = QSTMemory()
        memory_id = memory.store(content, context)
        
        return jsonify({
            "success": True,
            "memory_id": memory_id
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


@app.route('/api/context')
def api_context():
    """獲取上下文"""
    try:
        from qst_memory import QSTMemory
        memory = QSTMemory()
        context = memory.get_context()
        
        return jsonify({
            "success": True,
            "context": context
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


@app.route('/api/stats')
def api_stats():
    """獲取統計"""
    try:
        from qst_memory import QSTMemory
        memory = QSTMemory()
        stats = memory.get_stats()
        
        return jsonify({
            "success": True,
            "stats": stats
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


@app.route('/api/clear', methods=['POST'])
def api_clear():
    """清空記憶"""
    try:
        from qst_memory import QSTMemory
        memory = QSTMemory()
        memory.clear()
        
        return jsonify({
            "success": True
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


# ===== 便捷啟動函數 =====
def run_server(host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
    """
    啟動 Web 服務器
    
    Args:
        host: 監聽地址
        port: 端口
        debug: 調試模式
    """
    # 確保 templates 目錄存在
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    app.run(host=host, port=port, debug=debug)


def create_demo_templates():
    """創建演示模板"""
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # index.html
    html = '''<!DOCTYPE html>
<html lang="zh-HK">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QST Memory System</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        header {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        h1 { font-size: 2em; margin-bottom: 10px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .card {
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 20px;
        }
        .card h2 { border-bottom: 2px solid #667eea; padding-bottom: 10px; margin-bottom: 15px; }
        input, textarea, button {
            width: 100%;
            padding: 10px;
            margin-bottom: 10px;
            border: none;
            border-radius: 5px;
        }
        input, textarea { background: rgba(255,255,255,0.9); color: #333; }
        button {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            cursor: pointer;
            font-weight: bold;
        }
        button:hover { opacity: 0.9; }
        .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
        .stat-item { 
            background: rgba(102,126,234,0.3); 
            padding: 15px; 
            border-radius: 8px; 
            text-align: center;
        }
        .stat-value { font-size: 2em; font-weight: bold; }
        .memory-list { max-height: 400px; overflow-y: auto; }
        .memory-item {
            background: rgba(255,255,255,0.05);
            padding: 10px;
            margin-bottom: 8px;
            border-radius: 5px;
            border-left: 3px solid #667eea;
        }
        .memory-meta { font-size: 0.8em; color: #aaa; }
        .result-item {
            background: rgba(102,126,234,0.2);
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
        }
        .context-box {
            background: rgba(0,0,0,0.3);
            padding: 15px;
            border-radius: 8px;
            white-space: pre-wrap;
            max-height: 300px;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🧠 QST Memory System</h1>
            <p>基於 QST Matrix 的高效記憶存取系統</p>
        </header>
        
        <div class="grid">
            <div class="card">
                <h2>📊 統計</h2>
                <div class="stats" id="stats"></div>
            </div>
            
            <div class="card">
                <h2>🔍 檢索</h2>
                <input type="text" id="query" placeholder="輸入查詢...">
                <button onclick="search()">檢索</button>
                <div id="results"></div>
            </div>
        </div>
        
        <div class="grid" style="margin-top: 20px;">
            <div class="card">
                <h2>💬 上下文</h2>
                <div class="context-box" id="context"></div>
                <button onclick="refreshContext()" style="margin-top:10px;">刷新</button>
            </div>
            
            <div class="card">
                <h2>📝 存儲記憶</h2>
                <textarea id="content" placeholder="輸入記憶內容..." rows="3"></textarea>
                <input type="text" id="contextLabel" placeholder="上下文標籤 (可選)">
                <button onclick="store()">存儲</button>
            </div>
        </div>
        
        <div class="card" style="margin-top: 20px;">
            <h2>🗂️ 所有記憶</h2>
            <button onclick="refreshMemories()">刷新列表</button>
            <div class="memory-list" id="memoryList"></div>
            <button onclick="clearAll()" style="margin-top:10px; background: linear-gradient(90deg, #e74c3c 0%, #c0392b 100%);">清空所有</button>
        </div>
    </div>
    
    <script>
        async function api(url, method='GET', data=null) {
            const options = { method };
            if (data) {
                options.headers = {'Content-Type': 'application/json'};
                options.body = JSON.stringify(data);
            }
            const res = await fetch(url, options);
            return res.json();
        }
        
        async function loadStats() {
            const data = await api('/api/stats');
            if (data.success) {
                const s = data.stats;
                document.getElementById('stats').innerHTML = \`
                    <div class="stat-item"><div class="stat-value">\${s.total_stores}</div><div>存儲次數</div></div>
                    <div class="stat-item"><div class="stat-value">\${s.total_retrievals}</div><div>檢索次數</div></div>
                    <div class="stat-item"><div class="stat-value">\${s.short_term_turns || 0}</div><div>短記憶</div></div>
                    <div class="stat-item"><div class="stat-value">\${s.long_term_memories || 0}</div><div>長記憶</div></div>
                \`;
            }
        }
        
        async function refreshMemories() {
            const data = await api('/api/memories');
            if (data.success) {
                document.getElementById('memoryList').innerHTML = data.memories.map(m => \`
                    <div class="memory-item">
                        <div>\${m.content}</div>
                        <div class="memory-meta">
                            σ=\${m.coherence.toFixed(2)} | DSI=\${m.dsi_level} | \${m.timestamp.slice(0,19)}
                        </div>
                    </div>
                \`).join('');
            }
        }
        
        async function refreshContext() {
            const data = await api('/api/context');
            if (data.success) {
                document.getElementById('context').textContent = data.context || '(無上下文)';
            }
        }
        
        async function search() {
            const query = document.getElementById('query').value;
            if (!query) return;
            
            const data = await api('/api/retrieve', 'POST', { query, top_k: 5 });
            if (data.success) {
                document.getElementById('results').innerHTML = data.results.map((r, i) => \`
                    <div class="result-item">
                        <strong>[\${(r.score*100).toFixed(1)}%]</strong> \${r.content}
                    </div>
                \`).join('') || '<p>無結果</p>';
            }
        }
        
        async function store() {
            const content = document.getElementById('content').value;
            const context = document.getElementById('contextLabel').value;
            if (!content) return;
            
            const data = await api('/api/store', 'POST', { content, context });
            if (data.success) {
                document.getElementById('content').value = '';
                refreshMemories();
                loadStats();
            }
        }
        
        async function clearAll() {
            if (confirm('確定清空所有記憶？')) {
                await api('/api/clear', 'POST');
                refreshMemories();
                loadStats();
            }
        }
        
        loadStats();
        refreshMemories();
        refreshContext();
        
        setInterval(loadStats, 5000);
    </script>
</body>
</html>'''
    
    with open(os.path.join(templates_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)


# ===== 主程序 =====
if __name__ == '__main__':
    create_demo_templates()
    run_server(host='0.0.0.0', port=5000, debug=True)
