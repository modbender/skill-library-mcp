#!/usr/bin/env python3
"""
浏览器内浮窗脚本
用于在当前浏览的网页旁边弹出浮窗进行交互
"""
import os
import sys
import json
import argparse
import subprocess

# JavaScript 代码用于在页面中注入浮窗
MODAL_HTML = '''
<div id="openclaw-modal-overlay" style="
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 999999;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    animation: openclaw-fade-in 0.2s ease-out;
">
    <div style="
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 16px;
        padding: 24px;
        min-width: 320px;
        max-width: 480px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        animation: openclaw-slide-up 0.3s ease-out;
    ">
        <div id="openclaw-modal-title" style="
            font-size: 18px;
            font-weight: 600;
            color: #1a1a1a;
            margin-bottom: 12px;
        "></div>
        <div id="openclaw-modal-content" style="
            font-size: 14px;
            color: #666;
            margin-bottom: 20px;
            line-height: 1.6;
        "></div>
        <div id="openclaw-modal-input-container" style="display:none; margin-bottom: 20px;">
            <input id="openclaw-modal-input" type="text" style="
                width: 100%;
                padding: 12px 16px;
                border: 1px solid #ddd;
                border-radius: 8px;
                font-size: 14px;
                outline: none;
                transition: border-color 0.2s;
            " onfocus="this.style.borderColor='#007aff'" onblur="this.style.borderColor='#ddd'">
        </div>
        <div id="openclaw-modal-buttons" style="
            display: flex;
            gap: 12px;
            justify-content: flex-end;
        ">
            <button id="openclaw-modal-cancel" style="
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                background: #f5f5f5;
                color: #666;
                transition: background 0.2s;
            ">取消</button>
            <button id="openclaw-modal-confirm" style="
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                background: linear-gradient(135deg, #007aff, #5856d6);
                color: white;
                transition: transform 0.1s, box-shadow 0.2s;
            ">确认</button>
        </div>
    </div>
    <style>
        @keyframes openclaw-fade-in {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        @keyframes openclaw-slide-up {
            from { transform: translateY(20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
    </style>
</div>
'''

def create_modal_js(type_name, title, message, default_value="", options=""):
    """创建注入页面的 JavaScript 代码"""
    
    # 转义 JavaScript 字符串
    title_js = title.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
    message_js = message.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
    default_js = default_value.replace("\\", "\\\\").replace("'", "\\'")
    
    if type_name == "confirm":
        input_display = "none"
        button_display = "flex"
    elif type_name == "input":
        input_display = "block"
        button_display = "flex"
    else:  # select
        input_display = "none"
        button_display = "flex"
    
    js_code = f'''
    (function() {{
        // 移除已存在的浮窗
        var existing = document.getElementById('openclaw-modal-overlay');
        if (existing) {{
            existing.remove();
        }}
        
        // 创建浮窗 HTML
        var container = document.createElement('div');
        container.innerHTML = `{MODAL_HTML}`;
        var modal = container.firstElementChild;
        
        // 设置内容
        modal.querySelector('#openclaw-modal-title').textContent = '{title_js}';
        modal.querySelector('#openclaw-modal-content').innerHTML = '{message_js}'.replace(/\\n/g, '<br>');
        
        // 设置输入框
        var inputContainer = modal.querySelector('#openclaw-modal-input-container');
        var input = modal.querySelector('#openclaw-modal-input');
        inputContainer.style.display = '{input_display}';
        input.value = '{default_js}';
        
        // 绑定按钮事件
        var cancelBtn = modal.querySelector('#openclaw-modal-cancel');
        var confirmBtn = modal.querySelector('#openclaw-modal-confirm');
        
        var resolve = null;
        var promise = new Promise(function(res) {{ resolve = res; }});
        
        cancelBtn.onclick = function() {{
            modal.remove();
            resolve({{ result: 'cancel' }});
        }};
        
        confirmBtn.onclick = function() {{
            var value = input.value;
            modal.remove();
            resolve({{ result: 'confirmed', value: value }});
        }};
        
        // ESC 键关闭
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape') {{
                modal.remove();
                resolve({{ result: 'cancel' }});
            }}
            if (e.key === 'Enter' && '{type_name}' === 'input') {{
                confirmBtn.click();
            }}
        }});
        
        // 点击遮罩关闭
        modal.onclick = function(e) {{
            if (e.target === modal) {{
                modal.remove();
                resolve({{ result: 'cancel' }});
            }}
        }};
        
        // 添加到页面
        document.body.appendChild(modal);
        
        // 如果有输入框，自动聚焦
        if ('{type_name}' === 'input') {{
            setTimeout(function() {{ input.focus(); }}, 100);
        }}
        
        // 返回 Promise
        window.openclaw_modal_result = promise;
    }})();
    '''
    
    return js_code

def main():
    parser = argparse.ArgumentParser(description='浏览器内浮窗')
    parser.add_argument('--action', required=True, choices=['show', 'hide', 'result'],
                        help='操作类型')
    parser.add_argument('--type', default='confirm', choices=['confirm', 'input', 'select'],
                        help='浮窗类型')
    parser.add_argument('--title', default='确认', help='浮窗标题')
    parser.add_argument('--message', default='', help='浮窗内容')
    parser.add_argument('--default', default='', help='默认值')
    parser.add_argument('--options', default='', help='选项')
    parser.add_argument('--timeout', type=int, default=60, help='超时时间')
    parser.add_argument('--json', action='store_true', help='输出JSON')
    
    args = parser.parse_args()
    
    if args.action == 'show':
        js_code = create_modal_js(args.type, args.title, args.message, args.default, args.options)
        
        # 使用 AppleScript 在 Safari/Chrome 中执行 JS
        # 这里先创建一个简化版本，使用 Python 回调方式
        print(json.dumps({
            "action": "show",
            "js_code": js_code,
            "message": "请在浏览器中手动执行浮窗注入"
        }, ensure_ascii=False))
        
    elif args.action == 'hide':
        js_code = '''
        (function() {
            var modal = document.getElementById('openclaw-modal-overlay');
            if (modal) modal.remove();
        })();
        '''
        print(json.dumps({"action": "hide", "js_code": js_code}, ensure_ascii=False))
        
    elif args.action == 'result':
        # 实际上这个需要通过其他方式获取结果
        # 暂时返回占位信息
        print(json.dumps({"result": "pending"}, ensure_ascii=False))

if __name__ == "__main__":
    main()
