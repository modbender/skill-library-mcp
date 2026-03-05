from flask import Flask, render_template_string, request, jsonify, session, Response
import requests
import os
from dotenv import load_dotenv

# 加载 .env 配置
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
load_dotenv(dotenv_path=os.path.join(root_dir, "config", ".env"))

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB for image uploads

# --- 配置区 ---
PORT_AGENT = int(os.getenv("PORT_AGENT", "51200"))
LOCAL_AGENT_URL = f"http://127.0.0.1:{PORT_AGENT}/ask"
LOCAL_AGENT_STREAM_URL = f"http://127.0.0.1:{PORT_AGENT}/ask_stream"
LOCAL_AGENT_CANCEL_URL = f"http://127.0.0.1:{PORT_AGENT}/cancel"
LOCAL_LOGIN_URL = f"http://127.0.0.1:{PORT_AGENT}/login"
LOCAL_TOOLS_URL = f"http://127.0.0.1:{PORT_AGENT}/tools"
LOCAL_SESSIONS_URL = f"http://127.0.0.1:{PORT_AGENT}/sessions"
LOCAL_SESSION_HISTORY_URL = f"http://127.0.0.1:{PORT_AGENT}/session_history"
LOCAL_DELETE_SESSION_URL = f"http://127.0.0.1:{PORT_AGENT}/delete_session"
LOCAL_TTS_URL = f"http://127.0.0.1:{PORT_AGENT}/tts"
LOCAL_SESSION_STATUS_URL = f"http://127.0.0.1:{PORT_AGENT}/session_status"
# OpenAI 兼容端点
LOCAL_OPENAI_COMPLETIONS_URL = f"http://127.0.0.1:{PORT_AGENT}/v1/chat/completions"
INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN", "")

# OASIS Forum proxy
PORT_OASIS = int(os.getenv("PORT_OASIS", "51202"))
OASIS_BASE_URL = f"http://127.0.0.1:{PORT_OASIS}"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>Teamclaw | AI Agent</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">

    <!-- PWA / iOS Full-screen support -->
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Teamclaw">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="theme-color" content="#111827">
    <meta name="format-detection" content="telephone=no">
    <meta name="msapplication-tap-highlight" content="no">
    <meta name="msapplication-TileColor" content="#111827">
    <link rel="apple-touch-icon" href="https://img.icons8.com/fluency/180/robot-2.png">
    <link rel="apple-touch-icon" sizes="152x152" href="https://img.icons8.com/fluency/152/robot-2.png">
    <link rel="apple-touch-icon" sizes="180x180" href="https://img.icons8.com/fluency/180/robot-2.png">
    <link rel="apple-touch-icon" sizes="167x167" href="https://img.icons8.com/fluency/167/robot-2.png">
    <!-- iOS splash screens -->
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <link rel="manifest" href="/manifest.json">
    
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/marked/9.1.2/marked.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/github-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/highlight.min.js"></script>

    <style>
        /* === PWA Standalone Mode Fix === */
        :root {
            --app-height: 100vh;
            --header-height: 60px;
            --input-height: 70px;
            --safe-top: env(safe-area-inset-top, 0px);
            --safe-bottom: env(safe-area-inset-bottom, 0px);
        }
        
        /* PWA standalone mode: use dynamic viewport height */
        @supports (height: 100dvh) {
            :root { --app-height: 100dvh; }
        }
        
        /* === Native App Behavior (mobile only) === */
        html, body {
            overscroll-behavior: none;
        }
        @media (hover: none) and (pointer: coarse) {
            /* Mobile / touch devices only */
            html, body {
                -webkit-overflow-scrolling: touch;
                -webkit-user-select: none;
                user-select: none;
                -webkit-touch-callout: none;
                -webkit-tap-highlight-color: transparent;
                touch-action: manipulation;
                position: fixed;
                width: 100%;
                height: 100%;
                overflow: hidden;
            }
            /* Allow text selection only inside chat messages on mobile */
            .message-agent, .message-user, .markdown-body {
                -webkit-user-select: text;
                user-select: text;
            }
        }
        /* Safe area classes removed — no special notch/curved-screen handling */
        /* Splash screen */
        #app-splash {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(135deg, #111827 0%, #1e3a5f 100%);
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            z-index: 99999; transition: opacity 0.5s ease;
        }
        #app-splash.fade-out { opacity: 0; pointer-events: none; }
        #app-splash .splash-icon { width: 80px; height: 80px; border-radius: 20px; margin-bottom: 16px; animation: splash-bounce 1s ease infinite; }
        #app-splash .splash-title { color: white; font-size: 22px; font-weight: 700; letter-spacing: 1px; }
        #app-splash .splash-sub { color: rgba(255,255,255,0.5); font-size: 12px; margin-top: 8px; }
        @keyframes splash-bounce { 0%,100% { transform: scale(1); } 50% { transform: scale(1.08); } }
        /* Offline banner */
        #offline-banner {
            display: none; position: fixed; top: 0; left: 0; right: 0;
            background: #ef4444; color: white; text-align: center;
            padding: 6px 0; font-size: 13px; font-weight: 600; z-index: 99998;
            padding-top: 6px;
        }
        #offline-banner.show { display: block; animation: slideDown 0.3s ease; }
        @keyframes slideDown { from { transform: translateY(-100%); } to { transform: translateY(0); } }

        /* Fixed header height - input area auto-sizes */
        header { 
            flex-shrink: 0; 
            height: auto; 
            min-height: calc(var(--header-height, 60px) + var(--safe-top)); 
            padding-top: var(--safe-top);
            z-index: 50;
        }
        .p-2.sm\:p-4.border-t { 
            flex-shrink: 0; 
            min-height: calc(60px + var(--safe-bottom));
            padding-bottom: var(--safe-bottom);
        }

        .chat-container { flex: 1; min-height: 0; overflow-y: auto; }
        .markdown-body pre { background: #1e1e1e; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0; overflow-x: auto; }
        .markdown-body code { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 0.9em; }
        .message-user { border-radius: 1.25rem 1.25rem 0.2rem 1.25rem; max-width: min(85%, 800px); }
        .message-agent { border-radius: 1.25rem 1.25rem 1.25rem 0.2rem; max-width: min(85%, 800px); }
        /* 流式工具调用指示器 */
        .stream-tool-indicator {
            display: inline-flex; align-items: center; gap: 6px;
            background: #f0f7ff; border: 1px solid #d0e3f7; border-radius: 1rem;
            padding: 4px 14px; margin: 3px 0; font-size: 0.82rem; color: #3b6fa0;
            max-width: 85%;
        }
        .stream-tool-icon { font-size: 0.9rem; }
        .stream-tool-name { font-weight: 500; }
        .stream-tool-running { animation: toolPulse 1s ease-in-out infinite; }
        .stream-tool-done { color: #16a34a; }
        @keyframes toolPulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        /* 系统占用中按钮 */
        .busy-indicator-btn {
            display: inline-flex; align-items: center; gap: 6px;
            background: #f59e0b; color: white; border: none;
            padding: 8px 16px; border-radius: 0.75rem;
            font-weight: 700; font-size: 0.875rem;
            cursor: not-allowed; opacity: 0.9;
            box-shadow: 0 0 8px rgba(245,158,11,0.4);
            animation: busyGlow 2s ease-in-out infinite;
        }
        .busy-spinner {
            display: inline-block; width: 14px; height: 14px;
            border: 2px solid rgba(255,255,255,0.4); border-top-color: white;
            border-radius: 50%; animation: tts-spin 0.8s linear infinite;
        }
        @keyframes busyGlow {
            0%, 100% { box-shadow: 0 0 4px rgba(245,158,11,0.3); }
            50% { box-shadow: 0 0 14px rgba(245,158,11,0.6); }
        }
        /* 聊天区刷新小按钮 */
        .refresh-chat-btn {
            position: absolute; right: 12px; top: -38px; z-index: 10;
            width: 32px; height: 32px; border-radius: 50%;
            border: 1px solid #e5e7eb; background: white; color: #9ca3af;
            font-size: 14px; cursor: pointer; display: flex; align-items: center;
            justify-content: center; box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            transition: all 0.3s; opacity: 0.5;
        }
        .refresh-chat-btn:hover { background: #f3f4f6; opacity: 0.8; }
        .refresh-chat-btn.has-new {
            opacity: 1; background: #fef3c7; border-color: #f59e0b; color: #d97706;
            box-shadow: 0 0 8px rgba(245,158,11,0.4);
            animation: refreshGlow 2s ease-in-out infinite;
        }
        .refresh-chat-btn.has-new:hover { background: #fde68a; }
        @keyframes refreshGlow {
            0%, 100% { box-shadow: 0 0 4px rgba(245,158,11,0.3); }
            50% { box-shadow: 0 0 12px rgba(245,158,11,0.6); }
        }
        /* TTS 朗读按钮 */
        .tts-btn {
            display: inline-flex; align-items: center; gap: 4px;
            padding: 3px 10px; margin-top: 8px;
            background: #f3f4f6; border: 1px solid #e5e7eb; border-radius: 9999px;
            font-size: 12px; color: #6b7280; cursor: pointer; user-select: none;
            transition: all 0.2s ease;
        }
        .tts-btn:hover { background: #e5e7eb; color: #374151; }
        .tts-btn.playing { background: #dbeafe; color: #2563eb; border-color: #93c5fd; }
        .tts-btn.loading { opacity: 0.6; pointer-events: none; }
        .tts-btn svg { width: 14px; height: 14px; }
        .tts-btn .tts-spinner {
            width: 14px; height: 14px; border: 2px solid #93c5fd;
            border-top-color: transparent; border-radius: 50%;
            animation: tts-spin 0.8s linear infinite; display: none;
        }
        .tts-btn.loading .tts-spinner { display: inline-block; }
        .tts-btn.loading .tts-icon { display: none; }
        @keyframes tts-spin { to { transform: rotate(360deg); } }
        .dot { width: 6px; height: 6px; background: #3b82f6; border-radius: 50%; animation: pulse 1.5s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 0.3; transform: scale(0.8); } 50% { opacity: 1; transform: scale(1.2); } }
        /* Tool panel styles */
        .tool-panel { transition: max-height 0.3s ease, opacity 0.3s ease; overflow: hidden; }
        .tool-panel.collapsed { max-height: 0; opacity: 0; }
        .tool-panel.expanded { max-height: 300px; opacity: 1; overflow-y: auto; }
        .tool-tag { display: inline-flex; align-items: center; padding: 4px 10px; border-radius: 9999px; font-size: 12px; cursor: pointer; user-select: none; transition: all 0.25s ease; }
        .tool-tag.enabled { background: #eff6ff; color: #2563eb; border: 1px solid #bfdbfe; }
        .tool-tag.enabled:hover { background: #dbeafe; }
        .tool-tag.disabled { background: #f3f4f6; color: #9ca3af; border: 1px solid #e5e7eb; opacity: 0.65; }
        .tool-tag.disabled:hover { background: #e5e7eb; opacity: 0.8; }
        .tool-toggle-btn { cursor: pointer; user-select: none; transition: color 0.2s; }
        .tool-toggle-btn:hover { color: #2563eb; }
        .tool-toggle-icon { display: inline-block; transition: transform 0.3s ease; }
        .tool-toggle-icon.open { transform: rotate(180deg); }

        /* OASIS Panel Styles */
        .oasis-panel { width: 380px; min-width: 320px; transition: width 0.3s ease; }
        .oasis-panel.collapsed-panel { width: 48px; min-width: 48px; }
        .oasis-panel.collapsed-panel .oasis-content { display: none; }
        .oasis-panel.collapsed-panel .oasis-expand-btn { display: flex; }
        .oasis-expand-btn { display: none; writing-mode: vertical-lr; text-orientation: mixed; }
        .oasis-topic-item { transition: all 0.2s ease; cursor: pointer; }
        .oasis-topic-item:hover { background: #eff6ff; }
        .oasis-topic-item.active { background: #dbeafe; border-left: 3px solid #2563eb; }
        .oasis-post { animation: slideIn 0.3s ease; }
        @keyframes slideIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
        .oasis-vote-bar { height: 6px; border-radius: 3px; overflow: hidden; }
        .oasis-vote-up { background: #22c55e; }
        .oasis-vote-down { background: #ef4444; }
        .oasis-status-badge { font-size: 10px; padding: 2px 8px; border-radius: 9999px; font-weight: 600; }
        .oasis-status-pending { background: #fef3c7; color: #92400e; }
        .oasis-status-discussing { background: #dbeafe; color: #1e40af; animation: pulse-bg 2s infinite; }
        .oasis-status-concluded { background: #d1fae5; color: #065f46; }
        .oasis-action-btn { font-size: 12px; padding: 2px 4px; border-radius: 4px; border: none; cursor: pointer; opacity: 0; transition: opacity 0.2s; background: transparent; line-height: 1; }
        .oasis-topic-item:hover .oasis-action-btn { opacity: 0.7; }
        .oasis-action-btn:hover { opacity: 1 !important; }
        .oasis-btn-cancel:hover { background: #fef3c7; }
        .oasis-btn-delete:hover { background: #fee2e2; }
        .oasis-detail-action-btn { font-size: 11px; padding: 3px 8px; border-radius: 6px; border: 1px solid #e5e7eb; cursor: pointer; background: white; transition: all 0.15s; }
        .oasis-detail-action-btn:hover { background: #f3f4f6; }
        .oasis-detail-action-btn.cancel { color: #d97706; border-color: #fbbf24; }
        .oasis-detail-action-btn.cancel:hover { background: #fffbeb; }
        .oasis-detail-action-btn.delete { color: #dc2626; border-color: #fca5a5; }
        .oasis-detail-action-btn.delete:hover { background: #fef2f2; }
        .oasis-status-error { background: #fee2e2; color: #991b1b; }
        @keyframes pulse-bg { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
        .oasis-expert-avatar { width: 28px; height: 28px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold; color: white; flex-shrink: 0; }
        .expert-creative { background: linear-gradient(135deg, #f59e0b, #f97316); }
        .expert-critical { background: linear-gradient(135deg, #ef4444, #dc2626); }
        .expert-data { background: linear-gradient(135deg, #3b82f6, #2563eb); }
        .expert-synthesis { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }
        .expert-default { background: linear-gradient(135deg, #6b7280, #4b5563); }
        .oasis-discussion-box { height: calc(100vh - 340px); overflow-y: auto; }
        .oasis-conclusion-box { background: linear-gradient(135deg, #f0fdf4, #ecfdf5); border: 1px solid #86efac; border-radius: 12px; padding: 12px; }

        /* === Page Switch Tab === */
        .page-tab-bar {
            display: flex; background: #f9fafb; border-bottom: 1px solid #e5e7eb;
            flex-shrink: 0; z-index: 10;
        }
        .page-tab {
            flex: 1; padding: 10px 0; text-align: center; font-size: 13px; font-weight: 600;
            color: #6b7280; cursor: pointer; transition: all 0.2s; border-bottom: 2px solid transparent;
            user-select: none;
        }
        .page-tab:hover { color: #374151; background: #f3f4f6; }
        .page-tab.active { color: #2563eb; border-bottom-color: #2563eb; background: white; }

        /* === Group Chat Styles === */
        .group-page { display: none; flex-direction: column; height: 100%; overflow: hidden; }
        .group-page.active { display: flex; }
        .chat-page { display: flex; flex-direction: column; height: 100%; overflow: hidden; }
        .chat-page.hidden-page { display: none; }

        .group-list-sidebar {
            width: 240px; flex-shrink: 0; border-right: 1px solid #e5e7eb;
            display: flex; flex-direction: column; height: 100%; background: #fafbfc;
        }
        .group-item {
            padding: 10px 12px; cursor: pointer; transition: background 0.15s;
            border-bottom: 1px solid #f3f4f6; position: relative;
        }
        .group-item:hover { background: #f3f4f6; }
        .group-item.active { background: #eff6ff; border-left: 3px solid #2563eb; }
        .group-item .group-name { font-size: 13px; font-weight: 600; color: #374151; }
        .group-item .group-meta { font-size: 11px; color: #9ca3af; margin-top: 2px; }
        .group-item .group-delete-btn {
            display: none; position: absolute; right: 6px; top: 50%; transform: translateY(-50%);
            background: #fee2e2; color: #dc2626; border: none; border-radius: 4px;
            font-size: 11px; padding: 2px 6px; cursor: pointer;
        }
        .group-item:hover .group-delete-btn { display: block; }

        .group-chat-area {
            flex: 1; display: flex; flex-direction: column; min-width: 0;
        }
        .group-chat-header {
            padding: 12px 16px; border-bottom: 1px solid #e5e7eb; background: white;
            display: flex; align-items: center; justify-content: space-between; flex-shrink: 0;
        }
        .group-messages-box {
            flex: 1; overflow-y: auto; padding: 16px; space-y: 3; background: #f9fafb;
        }
        .group-msg {
            margin-bottom: 10px; animation: slideIn 0.2s ease;
        }
        .group-msg-sender {
            font-size: 11px; font-weight: 600; color: #6b7280; margin-bottom: 2px;
        }
        .group-msg-content {
            display: inline-block; padding: 8px 12px; border-radius: 12px;
            font-size: 13px; line-height: 1.5; max-width: 85%; word-break: break-word;
        }
        .group-msg-content.markdown-body { text-align: left; }
        .group-msg-content.markdown-body p { margin: 0 0 0.4em 0; }
        .group-msg-content.markdown-body p:last-child { margin-bottom: 0; }
        .group-msg-content.markdown-body pre { background: #1e1e1e; padding: 0.6rem; border-radius: 0.4rem; margin: 0.4rem 0; overflow-x: auto; }
        .group-msg-content.markdown-body code { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 0.85em; }
        .group-msg-content.markdown-body ul, .group-msg-content.markdown-body ol { margin: 0.3em 0; padding-left: 1.5em; }
        .group-msg.self .group-msg-content.markdown-body pre { background: #1e40af; }
        .group-msg.self .group-msg-content.markdown-body code { color: #e0e7ff; }
        .group-msg.self .group-msg-content { background: #2563eb; color: white; }
        .group-msg.other .group-msg-content { background: white; border: 1px solid #e5e7eb; color: #374151; }
        .group-msg.agent .group-msg-content { border-width: 1px; border-style: solid; }
        .group-msg.self { text-align: right; }
        .group-msg.agent { text-align: left; }
        .group-msg-time { font-size: 10px; color: #9ca3af; margin-top: 2px; }

        .group-input-area {
            padding: 12px 16px; border-top: 1px solid #e5e7eb; background: white; flex-shrink: 0;
            display: flex; align-items: end; gap: 8px;
        }
        .group-input-area textarea {
            flex: 1; resize: none; border: 1px solid #d1d5db; border-radius: 10px;
            padding: 8px 12px; font-size: 14px; max-height: 100px;
            outline: none; transition: border-color 0.2s;
        }
        .group-input-area textarea:focus { border-color: #2563eb; }

        /* Group member panel (right side) */
        .group-member-panel {
            width: 220px; flex-shrink: 0; border-left: 1px solid #e5e7eb;
            display: flex; flex-direction: column; background: white; overflow: hidden;
        }
        .group-member-panel .panel-header {
            padding: 12px; border-bottom: 1px solid #e5e7eb; font-size: 13px;
            font-weight: 600; color: #374151; background: #f9fafb;
        }
        .member-list { flex: 1; overflow-y: auto; padding: 8px; }
        .member-item {
            display: flex; align-items: center; justify-content: space-between;
            padding: 6px 8px; border-radius: 8px; margin-bottom: 4px; font-size: 12px;
        }
        .member-item .member-name { color: #374151; font-weight: 500; }
        .member-item .member-badge {
            font-size: 10px; padding: 1px 6px; border-radius: 9999px;
        }
        .member-item .badge-owner { background: #fef3c7; color: #92400e; }
        .member-item .badge-agent { background: #dbeafe; color: #1e40af; }

        .session-checkbox {
            display: flex; align-items: center; padding: 6px 8px; border-radius: 8px;
            cursor: pointer; transition: background 0.15s; font-size: 12px;
        }
        .session-checkbox:hover { background: #f3f4f6; }
        .session-checkbox input { margin-right: 8px; }
        .session-checkbox .session-label { color: #374151; flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

        .group-empty-state {
            flex: 1; display: flex; align-items: center; justify-content: center;
            flex-direction: column; color: #9ca3af;
        }
        .group-empty-state .empty-icon { font-size: 48px; margin-bottom: 12px; }
        .group-empty-state .empty-text { font-size: 14px; }

        /* @ Mention popup */
        .mention-popup {
            display: none; position: absolute; bottom: 100%; left: 0; right: 0;
            background: white; border: 1px solid #e5e7eb; border-radius: 12px;
            box-shadow: 0 -4px 16px rgba(0,0,0,0.1); max-height: 220px; overflow-y: auto;
            margin-bottom: 6px; z-index: 100; padding: 6px 0;
        }
        .mention-popup.show { display: block; }
        .mention-popup .mention-title {
            padding: 6px 14px; font-size: 11px; font-weight: 600; color: #9ca3af;
        }
        .mention-popup .mention-item {
            display: flex; align-items: center; padding: 8px 14px; cursor: pointer;
            transition: background 0.15s; gap: 8px; font-size: 13px;
        }
        .mention-popup .mention-item:hover { background: #f3f4f6; }
        .mention-popup .mention-item.selected { background: #eff6ff; }
        .mention-popup .mention-item .mention-check {
            width: 18px; height: 18px; border-radius: 4px; border: 2px solid #d1d5db;
            display: flex; align-items: center; justify-content: center; flex-shrink: 0;
            transition: all 0.15s; font-size: 11px; color: white;
        }
        .mention-popup .mention-item.selected .mention-check {
            background: #2563eb; border-color: #2563eb;
        }
        .mention-popup .mention-item .mention-name {
            flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: #374151;
        }
        .mention-popup .mention-confirm {
            margin: 6px 10px; padding: 6px; border: none; border-radius: 8px;
            background: #2563eb; color: white; font-size: 12px; font-weight: 600;
            cursor: pointer; width: calc(100% - 20px); transition: background 0.15s;
        }
        .mention-popup .mention-confirm:hover { background: #1d4ed8; }
        .mention-tag {
            display: inline-block; background: #dbeafe; color: #1e40af; border-radius: 4px;
            padding: 0 4px; font-size: 12px; font-weight: 500; margin-right: 2px;
        }
        .group-msg .mention-tag { background: rgba(37,99,235,0.15); color: #1e40af; font-weight: 600; }
        .group-msg.self .mention-tag { background: rgba(255,255,255,0.25); color: white; }

        @media (max-width: 768px) {
            .group-list-sidebar {
                width: 100% !important; border-right: none;
            }
            .group-chat-area { display: none !important; }
            .group-page.mobile-chat-open .group-list-sidebar { display: none !important; }
            .group-page.mobile-chat-open .group-chat-area { display: flex !important; }
            .group-member-panel {
                position: fixed; left: 0; top: 0; right: 0; bottom: 0;
                width: 100% !important; z-index: 250; box-shadow: 0 0 30px rgba(0,0,0,0.2);
            }
            .group-chat-header .group-back-btn { display: inline-flex !important; }
            .page-tab { font-size: 12px; padding: 8px 0; }
        }

        /* === Orchestration Page (Light Theme) === */
        .orch-page { display: none; flex-direction: column; height: 100%; overflow: hidden; }
        .orch-page.active { display: flex; }
        .orch-layout { display: flex; flex: 1; overflow: hidden; }
        .orch-sidebar {
            width: 200px; flex-shrink: 0; border-right: 1px solid #e5e7eb;
            display: flex; flex-direction: column; background: #fafbfc; overflow: hidden;
        }
        .orch-sidebar-header { padding: 10px 12px; border-bottom: 1px solid #e5e7eb; background: #f3f4f6; flex-shrink: 0; }
        .orch-expert-list { flex: 1; overflow-y: auto; padding: 4px 6px; }
        .orch-expert-card {
            display: flex; align-items: center; gap: 6px; padding: 6px 8px; margin-bottom: 3px;
            border-radius: 8px; background: white; border: 1px solid #e5e7eb;
            cursor: grab; transition: all 0.15s; font-size: 12px;
        }
        .orch-expert-card:hover { border-color: #2563eb; background: #eff6ff; }
        .orch-expert-card:active { cursor: grabbing; }
        .orch-expert-card .orch-emoji { font-size: 18px; }
        .orch-expert-card .orch-name { font-weight: 500; color: #374151; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .orch-expert-card .orch-tag { font-size: 10px; color: #9ca3af; }
        .orch-expert-card .orch-temp { font-size: 10px; color: #059669; background: #ecfdf5; padding: 1px 5px; border-radius: 4px; }
        .orch-manual-card {
            display: flex; align-items: center; gap: 6px; padding: 6px 8px; margin: 3px 6px 6px;
            border-radius: 8px; background: #faf5ff; border: 1px dashed #a855f7; cursor: grab; font-size: 12px;
        }
        .orch-manual-card:hover { background: #f3e8ff; }

        .orch-canvas-wrapper { flex: 1; display: flex; flex-direction: column; min-width: 0; }
        .orch-toolbar {
            display: flex; gap: 4px; padding: 6px 10px; background: #f9fafb; border-bottom: 1px solid #e5e7eb; flex-shrink: 0; flex-wrap: wrap;
        }
        .orch-btn {
            padding: 4px 10px; border: 1px solid #d1d5db; border-radius: 6px; background: white;
            color: #374151; cursor: pointer; font-size: 11px; transition: all 0.15s;
        }
        .orch-btn:hover { background: #f3f4f6; border-color: #2563eb; }
        .orch-btn-primary { background: #2563eb; color: white; border-color: #2563eb; }
        .orch-btn-primary:hover { background: #1d4ed8; }
        .orch-btn-danger { color: #dc2626; border-color: #fca5a5; }
        .orch-btn-danger:hover { background: #fef2f2; }

        .orch-canvas {
            flex: 1; position: relative; overflow: hidden;
            background-color: #fafbfc;
        }
        .orch-canvas-inner {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            transform-origin: 0 0;
            background: linear-gradient(#f1f5f9 1px, transparent 1px), linear-gradient(90deg, #f1f5f9 1px, transparent 1px);
            background-size: 24px 24px;
        }
        .orch-nav-controls {
            position: absolute; bottom: 12px; right: 12px; z-index: 100;
            display: flex; flex-direction: column; align-items: center; gap: 2px;
            background: rgba(255,255,255,0.95); border-radius: 10px; padding: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.13); font-size: 11px; color: #374151;
        }
        .orch-nav-controls .nav-row {
            display: flex; align-items: center; justify-content: center; gap: 2px;
        }
        .orch-nav-controls button {
            width: 26px; height: 26px; border: 1px solid #e5e7eb; border-radius: 6px;
            background: white; cursor: pointer; font-size: 13px; line-height: 1;
            display: flex; align-items: center; justify-content: center; color: #4b5563;
            transition: background 0.12s, border-color 0.12s;
        }
        .orch-nav-controls button:hover { background: #f3f4f6; border-color: #d1d5db; }
        .orch-nav-controls button:active { background: #e5e7eb; }
        .orch-nav-controls button.nav-center {
            width: 28px; height: 28px; font-size: 11px; font-weight: 600; color: #6b7280;
        }
        .orch-nav-controls .nav-zoom-row {
            display: flex; align-items: center; gap: 2px; margin-top: 2px;
            border-top: 1px solid #f0f0f0; padding-top: 4px;
        }
        .orch-nav-controls .nav-zoom-row button { width: 24px; height: 22px; font-size: 14px; }
        .orch-nav-controls .zoom-label {
            min-width: 34px; text-align: center; font-size: 10px; color: #9ca3af; user-select: none;
        }

        .orch-node {
            position: absolute; min-width: 110px; padding: 8px 10px;
            border-radius: 10px; background: white;
            border: 2px solid #d1d5db; cursor: move; user-select: none; z-index: 10;
            transition: box-shadow 0.15s, border-color 0.15s;
            display: flex; align-items: center; gap: 6px; font-size: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        }
        .orch-node:hover { border-color: #2563eb; box-shadow: 0 2px 8px rgba(37,99,235,0.15); }
        .orch-node.selected { border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37,99,235,0.2); }
        .orch-node.manual-type { background: #faf5ff; border-color: #a855f7; }
        .orch-node .orch-node-emoji { font-size: 18px; }
        .orch-node .orch-node-name { font-weight: 600; color: #374151; white-space: nowrap; }
        .orch-node .orch-node-tag { font-size: 10px; color: #9ca3af; }
        .orch-node .orch-node-del {
            position: absolute; top: -7px; right: -7px; width: 18px; height: 18px;
            border-radius: 50%; background: #ef4444; color: white; font-size: 11px;
            line-height: 18px; text-align: center; cursor: pointer; display: none; z-index: 20;
        }
        .orch-node:hover .orch-node-del { display: block; }
        .orch-node .orch-node-status {
            position: absolute; bottom: -4px; right: 6px; width: 8px; height: 8px;
            border-radius: 50%; border: 2px solid white;
        }
        .orch-node .orch-node-status.running { background: #22c55e; animation: orch-pulse 1.5s infinite; }
        .orch-node .orch-node-status.idle { background: #d1d5db; }
        @keyframes orch-pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }

        .orch-port {
            position: absolute; width: 10px; height: 10px; border-radius: 50%;
            background: #2563eb; border: 2px solid white; z-index: 15; cursor: crosshair;
        }
        .orch-port.port-out { right: -5px; top: 50%; transform: translateY(-50%); }
        .orch-port.port-in { left: -5px; top: 50%; transform: translateY(-50%); }
        .orch-port:hover { background: #3b82f6; transform: translateY(-50%) scale(1.3); }

        .orch-group {
            position: absolute; border-radius: 16px; border: 2px dashed; z-index: 2; min-width: 140px; min-height: 80px;
        }
        .orch-group.parallel { border-color: #22c55e80; background: #22c55e08; }
        .orch-group.all { border-color: #f59e0b80; background: #f59e0b08; }
        .orch-group .orch-group-label {
            position: absolute; top: -10px; left: 14px; padding: 1px 8px; border-radius: 8px;
            font-size: 10px; background: white; border: 1px solid;
        }
        .orch-group.parallel .orch-group-label { color: #16a34a; border-color: #22c55e80; }
        .orch-group.all .orch-group-label { color: #d97706; border-color: #f59e0b80; }
        .orch-group .orch-group-del {
            position: absolute; top: -7px; right: -7px; width: 18px; height: 18px;
            border-radius: 50%; background: #ef4444; color: white; font-size: 11px;
            line-height: 18px; text-align: center; cursor: pointer; display: none; z-index: 20;
        }
        .orch-group:hover .orch-group-del { display: block; }

        .orch-right-panel {
            width: 280px; flex-shrink: 0; border-left: 1px solid #e5e7eb;
            display: flex; flex-direction: column; background: white; overflow: hidden;
        }
        .orch-right-section { border-bottom: 1px solid #f3f4f6; }
        .orch-yaml-box {
            font-family: ui-monospace, SFMono-Regular, monospace; font-size: 11px;
            background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 6px;
            padding: 6px 8px; overflow-y: auto; white-space: pre-wrap; word-break: break-all; line-height: 1.4;
        }
        .orch-status-bar {
            padding: 4px 12px; background: #f9fafb; border-top: 1px solid #e5e7eb;
            font-size: 10px; color: #9ca3af; flex-shrink: 0;
        }

        .orch-sel-rect { position: absolute; border: 1px solid #2563eb; background: rgba(37,99,235,0.08); z-index: 5; pointer-events: none; }
        .orch-context-menu {
            position: fixed; background: white; border: 1px solid #e5e7eb; border-radius: 8px;
            padding: 4px; z-index: 1000; min-width: 150px; box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        }
        .orch-context-menu .orch-menu-item { padding: 6px 10px; cursor: pointer; border-radius: 4px; font-size: 12px; color: #374151; }
        .orch-context-menu .orch-menu-item:hover { background: #eff6ff; }
        .orch-context-menu .orch-menu-divider { height: 1px; background: #e5e7eb; margin: 3px 0; }
        .orch-toast {
            position: fixed; bottom: 60px; left: 50%; transform: translateX(-50%);
            padding: 8px 16px; background: #2563eb; color: white; border-radius: 8px;
            font-size: 12px; z-index: 3000; animation: slideIn 0.3s ease; box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }

        /* Session selector modal for orchestration */
        .orch-session-list { max-height: 280px; overflow-y: auto; margin: 8px 0; }
        .orch-session-item {
            display: flex; align-items: center; gap: 10px; padding: 10px 12px; margin-bottom: 4px;
            border: 1px solid #e5e7eb; border-radius: 8px; cursor: pointer; transition: all 0.2s;
            background: #fafafa;
        }
        .orch-session-item:hover { border-color: #2563eb; background: #eff6ff; }
        .orch-session-item.selected { border-color: #2563eb; background: #dbeafe; box-shadow: 0 0 0 2px rgba(37,99,235,0.2); }
        .orch-session-item .orch-session-title { font-size: 13px; font-weight: 500; color: #374151; flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .orch-session-item .orch-session-id { font-size: 10px; color: #9ca3af; font-family: monospace; }
        .orch-session-item .orch-session-icon { font-size: 18px; }
        .orch-session-new { display: flex; align-items: center; gap: 10px; padding: 10px 12px; margin-bottom: 4px; border: 2px dashed #d1d5db; border-radius: 8px; cursor: pointer; transition: all 0.2s; background: white; }
        .orch-session-new:hover { border-color: #2563eb; background: #eff6ff; }
        .orch-session-new.selected { border-color: #2563eb; background: #dbeafe; }
        .orch-goto-chat-btn {
            display: inline-flex; align-items: center; gap: 6px; margin-top: 8px; padding: 8px 16px;
            background: linear-gradient(135deg, #2563eb, #7c3aed); color: white; border: none;
            border-radius: 8px; font-size: 13px; font-weight: 500; cursor: pointer;
            transition: all 0.2s; box-shadow: 0 2px 8px rgba(37,99,235,0.3);
        }
        .orch-goto-chat-btn:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(37,99,235,0.4); }
        .orch-goto-chat-btn:active { transform: translateY(0); }

        .orch-modal-overlay {
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.3); z-index: 2000; display: flex; align-items: center; justify-content: center;
        }
        .orch-modal {
            background: white; border: 1px solid #e5e7eb; border-radius: 12px;
            padding: 20px; min-width: 360px; max-width: 460px; box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        }
        .orch-modal h3 { margin-bottom: 12px; color: #374151; font-size: 15px; }
        .orch-modal input, .orch-modal textarea {
            width: 100%; padding: 6px 10px; border: 1px solid #d1d5db; border-radius: 6px;
            font-size: 12px; margin-bottom: 8px; outline: none; transition: border-color 0.2s;
        }
        .orch-modal input:focus, .orch-modal textarea:focus { border-color: #2563eb; }
        .orch-modal textarea { height: 60px; resize: vertical; font-family: inherit; }
        .orch-modal .orch-modal-btns { display: flex; gap: 6px; justify-content: flex-end; }
        .orch-modal .orch-modal-btns button {
            padding: 6px 14px; border-radius: 6px; border: 1px solid #d1d5db;
            background: white; color: #374151; cursor: pointer; font-size: 12px;
        }
        .orch-modal .orch-modal-btns button.primary { background: #2563eb; color: white; border-color: #2563eb; }

        @media (max-width: 768px) {
            .orch-sidebar { display: none; }
            .orch-right-panel { width: 200px; }
        }

        .main-layout { display: flex; height: var(--app-height, 100vh); max-width: 100%; overflow: hidden; }
        .chat-main { flex: 1; min-width: 0; display: flex; flex-direction: column; height: var(--app-height, 100vh); overflow: hidden; }

        /* === Session sidebar === */
        .session-sidebar {
            width: 260px; flex-shrink: 0; display: flex; flex-direction: column;
            height: var(--app-height, 100vh); background: white; border-right: 1px solid #e5e7eb;
            overflow: hidden;
        }
        .session-item {
            padding: 8px 10px; border-radius: 8px; cursor: pointer; transition: background 0.15s;
            border: 1px solid transparent;
        }
        .session-item:hover { background: #f3f4f6; }
        .session-item.active { background: #eff6ff; border-color: #bfdbfe; }
        .session-item .session-title { font-size: 13px; font-weight: 500; color: #374151; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .session-item .session-meta { font-size: 11px; color: #9ca3af; margin-top: 2px; }
        .session-item .session-delete {
            display: none; position: absolute; right: 6px; top: 50%; transform: translateY(-50%);
            background: #fee2e2; color: #dc2626; border: none; border-radius: 4px;
            font-size: 11px; padding: 2px 6px; cursor: pointer; line-height: 1.2;
        }
        .session-item { position: relative; }
        .session-item:hover .session-delete { display: block; }
        .session-item .session-delete:hover { background: #fca5a5; }
        @keyframes session-glow-user {
            0%, 100% { box-shadow: 0 0 4px 1px rgba(59,130,246,0.3); }
            50% { box-shadow: 0 0 10px 3px rgba(59,130,246,0.5); }
        }
        @keyframes session-glow-system {
            0%, 100% { box-shadow: 0 0 4px 1px rgba(234,179,8,0.3); }
            50% { box-shadow: 0 0 10px 3px rgba(234,179,8,0.5); }
        }
        .session-item.busy-user {
            animation: session-glow-user 1.5s ease-in-out infinite;
            border-color: #93c5fd;
            background: rgba(59,130,246,0.08);
        }
        .session-item.busy-system {
            animation: session-glow-system 1.5s ease-in-out infinite;
            border-color: #fcd34d;
            background: rgba(234,179,8,0.10);
        }
        .session-busy-badge {
            display: inline-block; font-size: 10px; padding: 0 4px; border-radius: 3px;
            margin-left: 4px; vertical-align: middle; line-height: 1.4;
        }
        .session-busy-badge.user { background: #dbeafe; color: #2563eb; }
        .session-busy-badge.system { background: #fef3c7; color: #b45309; }

        /* === Mobile responsive === */
        @media (max-width: 768px) {
            .session-sidebar {
                position: fixed; left: 0; top: 0; z-index: 200; width: 75vw; max-width: 300px;
                box-shadow: 4px 0 20px rgba(0,0,0,0.15);
            }
            .session-overlay {
                position: fixed; inset: 0; background: rgba(0,0,0,0.3); z-index: 199;
            }
            .main-layout { flex-direction: column; height: var(--app-height, 100vh); overflow: hidden; }
            .chat-main { max-width: 100%; width: 100%; height: var(--app-height, 100vh); }
            /* Header: fixed at top - auto height for safe area */
            header { 
                flex-shrink: 0; 
                height: auto; 
                min-height: calc(var(--header-height, 60px) + var(--safe-top));
                padding-top: var(--safe-top);
                overflow: visible;
            }
            /* Chat container: scrollable middle area */
            .chat-container { flex: 1; min-height: 0; overflow-y: auto; -webkit-overflow-scrolling: touch; }
            /* Input area: fixed at bottom - auto height */
            .p-2.sm\:p-4.border-t { 
                flex-shrink: 0; 
                min-height: calc(60px + var(--safe-bottom));
                padding-bottom: var(--safe-bottom);
            }
            /* OASIS: overlay mode on mobile */
            .oasis-divider { display: none !important; }
            .oasis-panel {
                position: fixed !important; top: 0; left: 0; right: 0; bottom: 0;
                width: 100% !important; min-width: 100% !important;
                z-index: 50; display: none;
            }
            .oasis-panel.mobile-open { display: flex !important; }
            .oasis-panel.collapsed-panel { display: none !important; }
            .oasis-panel .oasis-expand-btn { display: none !important; }
            /* Mobile: hide UID & session, hide desktop buttons, show hamburger */
            #uid-display, #session-display { display: none !important; }
            .desktop-only-btn { display: none !important; }
            .mobile-menu-btn { display: inline-flex !important; }
            /* Header: stack items on narrow screens */
            .mobile-header-top { flex-wrap: wrap; gap: 6px; }
            .mobile-header-actions { flex-wrap: wrap; gap: 4px; justify-content: flex-end; }
            /* Reduce padding on mobile */
            #chat-box { padding: 12px !important; }
            .message-agent, .message-user { max-width: 92% !important; }
            /* Increase font size on mobile */
            .message-content, .message-agent, .message-user { font-size: 16px !important; }
            .message-content p, .message-content li { font-size: 16px !important; }
            #message-input, #message-input::placeholder { font-size: 16px !important; }
            .tool-tag { font-size: 14px !important; padding: 6px 12px !important; }
        }
        /* Hide mobile-only elements on desktop */
        @media (min-width: 769px) {
            .mobile-menu-wrapper { display: none !important; }
        }
        /* Mobile menu dropdown styles */
        .mobile-menu-btn { display: none; }
        .mobile-menu-dropdown {
            position: absolute; right: 0; top: 100%; margin-top: 6px;
            background: white; border: 1px solid #e5e7eb; border-radius: 10px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.12); z-index: 100;
            min-width: 140px; overflow: hidden;
        }
        .mobile-menu-item {
            display: block; width: 100%; text-align: left;
            padding: 10px 14px; font-size: 13px; color: #374151;
            border: none; background: none; cursor: pointer;
            transition: background 0.15s;
        }
        .mobile-menu-item:hover, .mobile-menu-item:active { background: #f3f4f6; }
        .mobile-menu-item + .mobile-menu-item { border-top: 1px solid #f3f4f6; }
        .oasis-divider { width: 1px; background: #e5e7eb; cursor: col-resize; flex-shrink: 0; }
        .oasis-divider:hover { background: #3b82f6; width: 3px; }

        /* Image upload styles */
        .image-preview-area { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 6px; }
        .image-preview-item { position: relative; width: 60px; height: 60px; border-radius: 8px; overflow: hidden; border: 1px solid #e5e7eb; }
        .image-preview-item img { width: 100%; height: 100%; object-fit: cover; }
        .image-preview-item .remove-btn { position: absolute; top: -2px; right: -2px; width: 18px; height: 18px; background: #ef4444; color: white; border: none; border-radius: 50%; font-size: 10px; cursor: pointer; display: flex; align-items: center; justify-content: center; line-height: 1; }
        .image-upload-btn { cursor: pointer; color: #6b7280; transition: color 0.2s; flex-shrink: 0; display: flex; align-items: center; justify-content: center; width: 42px; height: 42px; border-radius: 10px; border: 1px solid #e5e7eb; background: #f9fafb; }
        .image-upload-btn:hover { color: #2563eb; border-color: #bfdbfe; background: #eff6ff; }
        @media (max-width: 768px) { .image-upload-btn { width: 36px; height: 36px; } }
        /* File preview (text files) */
        .file-preview-item { position: relative; display: flex; align-items: center; gap: 4px; padding: 4px 8px; border-radius: 8px; border: 1px solid #e5e7eb; background: #f9fafb; font-size: 12px; color: #374151; max-width: 180px; }
        .file-preview-item .file-icon { font-size: 16px; flex-shrink: 0; }
        .file-preview-item .file-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .file-preview-item .remove-btn { width: 16px; height: 16px; background: #ef4444; color: white; border: none; border-radius: 50%; font-size: 9px; cursor: pointer; display: flex; align-items: center; justify-content: center; line-height: 1; flex-shrink: 0; }
        .chat-file-tag { display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; border-radius: 6px; background: rgba(255,255,255,0.15); font-size: 12px; margin-bottom: 4px; }
        /* Audio recording button */
        .audio-record-btn { cursor: pointer; color: #6b7280; transition: all 0.2s; flex-shrink: 0; display: flex; align-items: center; justify-content: center; width: 42px; height: 42px; border-radius: 10px; border: 1px solid #e5e7eb; background: #f9fafb; font-size: 18px; }
        .audio-record-btn:hover { color: #dc2626; border-color: #fecaca; background: #fef2f2; }
        .audio-record-btn.recording { color: #fff; background: #dc2626; border-color: #dc2626; animation: pulse-red 1.2s infinite; }
        @keyframes pulse-red { 0%,100% { box-shadow: 0 0 0 0 rgba(220,38,38,0.4); } 50% { box-shadow: 0 0 0 8px rgba(220,38,38,0); } }
        @media (max-width: 768px) { .audio-record-btn { width: 36px; height: 36px; font-size: 16px; } }
        /* Audio preview */
        .audio-preview-item { position: relative; display: flex; align-items: center; gap: 4px; padding: 4px 8px; border-radius: 8px; border: 1px solid #e5e7eb; background: #fef2f2; font-size: 12px; color: #374151; max-width: 200px; }
        .audio-preview-item .file-icon { font-size: 16px; flex-shrink: 0; }
        .audio-preview-item .file-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .audio-preview-item .remove-btn { width: 16px; height: 16px; background: #ef4444; color: white; border: none; border-radius: 50%; font-size: 9px; cursor: pointer; display: flex; align-items: center; justify-content: center; line-height: 1; flex-shrink: 0; }
        .chat-audio-tag { display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; border-radius: 6px; background: rgba(255,255,255,0.15); font-size: 12px; margin-bottom: 4px; }
        /* Inline image in chat messages */
        .chat-inline-image { max-width: 240px; max-height: 180px; border-radius: 8px; margin: 4px 0; cursor: pointer; }
        .chat-inline-image:hover { opacity: 0.9; }
    </style>
</head>
<body class="bg-gray-100 font-sans leading-normal tracking-normal">

    <!-- Splash Screen -->
    <div id="app-splash">
        <img class="splash-icon" src="https://img.icons8.com/fluency/180/robot-2.png" alt="">
        <div class="splash-title">Teamclaw</div>
        <div class="splash-sub">Xavier AI Agent</div>
    </div>

    <!-- Offline Banner -->
    <div id="offline-banner" data-i18n="offline_banner">⚠️ 网络已断开，请检查连接</div>

    <!-- ========== 登录页 ========== -->
    <div id="login-screen" class="min-h-screen flex items-center justify-center safe-top safe-bottom px-4" style="width:100%;height:100%;overflow:auto;">
        <div class="bg-white rounded-2xl shadow-2xl p-6 sm:p-8 w-full max-w-md border">
            <div class="flex items-center justify-center space-x-3 mb-6">
                <div class="bg-blue-600 p-3 rounded-xl text-white font-bold text-2xl">X</div>
                <h1 class="text-2xl font-bold text-gray-800" data-i18n="login_title">Teamclaw</h1>
            </div>
            <p class="text-center text-gray-500 text-sm mb-8" data-i18n="login_subtitle">请登录以开始对话</p>
            <div class="space-y-4">
                <input id="username-input" type="text" maxlength="32"
                    class="w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-center text-lg"
                    data-i18n-placeholder="username" placeholder="用户名" autofocus>
                <input id="password-input" type="password" maxlength="64"
                    class="w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-center text-lg"
                    data-i18n-placeholder="password" placeholder="密码">
                <div id="login-error" class="text-red-500 text-sm text-center hidden"></div>
                <button onclick="handleLogin()" id="login-btn"
                    class="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-xl font-bold text-lg transition-all shadow-lg"
                    data-i18n="login_btn">登录</button>
            </div>
            <p class="text-xs text-gray-400 text-center mt-6" data-i18n="login_footer">身份验证后方可使用，对话和文件按用户隔离</p>
        </div>
    </div>

    <!-- ========== 主布局（聊天 + OASIS）（初始隐藏） ========== -->
    <div id="chat-screen" class="main-layout safe-top safe-bottom safe-left safe-right" style="display:none;">

        <!-- ===== 历史会话侧边栏 ===== -->
        <div id="session-sidebar" class="session-sidebar" style="display:none;">
            <div class="p-3 border-b bg-gray-50 flex justify-between items-center flex-shrink-0">
                <span class="text-sm font-bold text-gray-700" data-i18n="history_title">🤖 Agents</span>
                <div class="flex items-center gap-2">
                    <button onclick="deleteAllSessions()" class="text-xs text-red-400 hover:text-red-600" data-i18n="delete_all">🗑️ 清空全部</button>
                    <button onclick="closeSessionSidebar()" class="text-gray-400 hover:text-gray-600 text-lg leading-none">&times;</button>
                </div>
            </div>
            <div id="session-list" class="flex-1 overflow-y-auto p-2 space-y-1">
                <div class="text-xs text-gray-400 text-center py-4" data-i18n="loading">加载中...</div>
            </div>
        </div>

        <!-- ===== 左侧：聊天区 ===== -->
        <div class="chat-main h-screen flex flex-col bg-white border-x border-gray-200 shadow-2xl">
            <!-- Page Switch Tab Bar -->
            <div class="page-tab-bar">
                <div class="page-tab active" id="tab-chat" onclick="switchPage('chat')" data-i18n="tab_chat">💬 对话</div>
                <div class="page-tab" id="tab-group" onclick="switchPage('group')" data-i18n="tab_group">👥 群聊</div>
                <div class="page-tab" id="tab-orchestrate" onclick="switchPage('orchestrate')">🎨 编排</div>
            </div>

            <!-- === Chat Page === -->
            <div id="page-chat" class="chat-page">
            <header class="p-3 sm:p-4 border-b bg-white flex justify-between items-start sm:items-center gap-2 flex-shrink-0">
                <div class="flex items-center space-x-2 sm:space-x-3 mobile-header-top flex-shrink-0">
                    <div class="bg-blue-600 p-1.5 sm:p-2 rounded-lg text-white font-bold text-lg sm:text-xl">X</div>
                    <div>
                        <h1 class="text-sm sm:text-lg font-bold text-gray-800 leading-tight">Teamclaw</h1>
                        <p class="text-[10px] sm:text-xs text-green-500 flex items-center" data-i18n="encrypted">● 已加密</p>
                    </div>
                </div>
                <div class="flex items-center space-x-1 sm:space-x-2 mobile-header-actions flex-shrink-0">
                    <div id="uid-display" class="text-xs sm:text-sm font-mono bg-gray-100 px-2 sm:px-3 py-1 rounded border truncate max-w-[80px] sm:max-w-none"></div>
                    <div id="session-display" class="text-[10px] sm:text-xs font-mono bg-blue-50 text-blue-600 px-1.5 sm:px-2 py-1 rounded border border-blue-200 cursor-default" data-i18n-title="current_session" title="当前对话号"></div>
                    <!-- History Button -->
                    <button onclick="toggleSessionSidebar()" class="desktop-only-btn text-[10px] sm:text-xs bg-gray-50 text-gray-600 hover:bg-gray-100 px-2 py-1 rounded border border-gray-200 transition-colors flex items-center justify-center" data-i18n-title="history_title" title="Agents">
                        <span class="hidden sm:inline" data-i18n="history">🤖Agents</span>
                        <span class="sm:hidden text-base leading-none">🤖</span>
                    </button>
                    <!-- New Session Button: Visible on all devices -->
                    <button onclick="handleNewSession()" class="text-[10px] sm:text-xs bg-green-50 text-green-600 hover:bg-green-100 px-2 py-1 rounded border border-green-200 transition-colors mr-1 flex items-center justify-center" data-i18n-title="new_session_confirm" title="开启新对话">
                        <span class="sm:hidden text-base font-bold leading-none">+</span>
                        <span class="hidden sm:inline" data-i18n="new_chat">+新</span>
                    </button>
                    <button onclick="toggleLanguage()" id="lang-toggle-btn" class="text-[10px] sm:text-xs bg-purple-50 text-purple-600 hover:bg-purple-100 px-2 py-1 rounded border border-purple-200 transition-colors" title="Switch Language">EN</button>
                    <button onclick="handleLogout()" class="desktop-only-btn text-[10px] sm:text-xs text-gray-400 hover:text-red-500 px-1.5 sm:px-2 py-1 rounded transition-colors" data-i18n="logout" data-i18n-title="logout" title="切换用户">退出</button>
                    <!-- Mobile: hamburger menu -->
                    <div class="mobile-menu-wrapper" style="position:relative;">
                        <button onclick="toggleMobileMenu()" class="mobile-menu-btn text-[10px] bg-gray-100 hover:bg-gray-200 px-2 py-1 rounded border border-gray-300 transition-colors" data-i18n-title="more_actions" title="更多操作">⋮</button>
                        <div id="mobile-menu-dropdown" class="mobile-menu-dropdown" style="display:none;">
                            <button onclick="toggleSessionSidebar(); closeMobileMenu();" class="mobile-menu-item" data-i18n="menu_history">🤖 Agents</button>
                            <button onclick="handleNewSession(); closeMobileMenu();" class="mobile-menu-item" data-i18n="menu_new">➕ 新对话</button>
                            <button onclick="toggleOasisMobile(); closeMobileMenu();" class="mobile-menu-item" data-i18n="menu_oasis">🏛️ TeamsWork</button>
                            <button onclick="handleLogout(); closeMobileMenu();" class="mobile-menu-item text-red-500" data-i18n="menu_logout">🚪 退出</button>
                        </div>
                    </div>
                </div>
            </header>

            <div id="chat-box" class="chat-container overflow-y-auto p-4 sm:p-6 space-y-4 sm:space-y-6 flex-grow bg-gray-50">
                <div class="flex justify-start">
                    <div class="message-agent bg-white border p-4 max-w-[85%] shadow-sm text-gray-700" data-i18n="welcome_message">
                        你好！我是 Xavier 智能助手。我已经准备好为你服务，请输入你的指令。
                    </div>
                </div>
            </div>

            <!-- 聊天区上方小刷新按钮 -->
            <div style="position:relative;">
                <button id="refresh-chat-btn" class="refresh-chat-btn" onclick="handleNewMsgRefresh()" title="刷新消息" data-i18n-title="refresh_chat">
                    🔄
                </button>
            </div>

            <div class="p-2 sm:p-4 border-t bg-white flex-shrink-0">
                <!-- Tool List Panel -->
                <div id="tool-panel-wrapper" class="mb-2" style="display:none;">
                    <div class="flex items-center justify-between mb-1">
                        <div class="tool-toggle-btn flex items-center space-x-1 text-sm text-gray-500 font-medium" onclick="toggleToolPanel()">
                            <span data-i18n="available_tools">🧰 可用工具</span>
                            <span id="tool-count" class="text-xs text-gray-400"></span>
                            <span id="tool-toggle-icon" class="tool-toggle-icon text-xs">▼</span>
                        </div>
                    </div>
                    <div id="tool-panel" class="tool-panel collapsed">
                        <div id="tool-list" class="flex flex-wrap gap-2 p-2 bg-gray-50 rounded-xl border border-gray-200">
                            <!-- tools will be injected here -->
                        </div>
                    </div>
                </div>
                <div id="image-preview-area" class="image-preview-area" style="display:none;"></div>
                <div id="file-preview-area" class="image-preview-area" style="display:none;"></div>
                <div id="audio-preview-area" class="image-preview-area" style="display:none;"></div>
                <div class="flex items-end space-x-2 sm:space-x-3">
                    <label class="image-upload-btn" title="上传图片/文件/音频">
                        📎
                        <input type="file" id="image-input" accept="image/*,.pdf,.txt,.md,.csv,.json,.xml,.yaml,.yml,.log,.py,.js,.ts,.html,.css,.java,.c,.cpp,.h,.go,.rs,.sh,.bat,.ini,.toml,.cfg,.conf,.sql,.r,.rb,.mp3,.wav,.ogg,.m4a,.webm,.flac,.aac,.avi,.mp4,.mkv,.mov" multiple style="display:none;" onchange="handleFileSelect(event)">
                    </label>
                    <button id="record-btn" class="audio-record-btn" data-i18n-title="recording_title" title="录音" onclick="toggleRecording()">🎤</button>
                    <div class="flex-grow">
                        <textarea id="user-input" rows="1" 
                            class="w-full p-2 sm:p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none transition-all text-sm sm:text-base"
                            data-i18n-placeholder="input_placeholder" placeholder="输入指令...（可粘贴图片/上传文件/录音）"></textarea>
                    </div>
                    <button onclick="handleSend()" id="send-btn"
                        class="bg-blue-600 hover:bg-blue-700 text-white px-4 sm:px-6 py-2 sm:py-3 rounded-xl transition-all font-bold shadow-lg h-[42px] sm:h-[50px] text-sm sm:text-base flex-shrink-0"
                        data-i18n="send_btn">发送
                    </button>
                    <button onclick="handleCancel()" id="cancel-btn"
                        class="bg-red-500 hover:bg-red-600 text-white px-4 sm:px-6 py-2 sm:py-3 rounded-xl transition-all font-bold shadow-lg h-[42px] sm:h-[50px] text-sm sm:text-base flex-shrink-0"
                        style="display:none;" data-i18n="cancel_btn">终止
                    </button>
                    <button id="busy-btn" disabled
                        class="busy-indicator-btn h-[42px] sm:h-[50px] text-sm sm:text-base flex-shrink-0"
                        style="display:none;" data-i18n="busy_btn">
                        <span class="busy-spinner"></span>系统占用中
                    </button>
                </div>
                <p class="text-[10px] text-center text-gray-400 mt-2 sm:mt-3 font-mono hidden sm:block" data-i18n="secure_footer">Secured by Nginx Reverse Proxy & SSH Tunnel</p>
            </div>
        </div>
        <!-- end of chat-page -->

        <!-- === Group Chat Page === -->
        <div id="page-group" class="group-page">
            <div style="display:flex; flex:1; overflow:hidden;">
                <!-- Group list sidebar -->
                <div class="group-list-sidebar">
                    <div class="p-3 border-b bg-gray-50 flex justify-between items-center flex-shrink-0">
                        <span class="text-sm font-bold text-gray-700" data-i18n="group_title">👥 群聊列表</span>
                        <div class="flex items-center gap-2">
                            <button onclick="toggleSessionSidebar()" class="text-[10px] bg-gray-50 text-gray-600 hover:bg-gray-100 px-2 py-1 rounded border border-gray-200" data-i18n-title="history_title" title="Agents">🤖</button>
                            <button onclick="showCreateGroupModal()" class="text-xs bg-blue-50 text-blue-600 hover:bg-blue-100 px-2 py-1 rounded border border-blue-200" data-i18n="group_new">+ 新建</button>
                        </div>
                    </div>
                    <div id="group-list" class="flex-1 overflow-y-auto">
                        <div class="group-empty-state" style="padding:40px 0;">
                            <div class="empty-icon">👥</div>
                            <div class="empty-text" data-i18n="group_no_groups">暂无群聊</div>
                        </div>
                    </div>
                </div>

                <!-- Group chat main area -->
                <div class="group-chat-area" id="group-chat-area">
                    <div class="group-empty-state" id="group-empty-placeholder">
                        <div class="empty-icon">💬</div>
                        <div class="empty-text" data-i18n="group_select_hint">选择或创建一个群聊</div>
                    </div>
                    <!-- Active group chat (hidden initially) -->
                    <div id="group-active-chat" style="display:none; flex-direction:column; height:100%;">
                        <div class="group-chat-header">
                            <div class="flex items-center gap-2">
                                <button onclick="groupBackToList()" class="group-back-btn text-xs text-gray-500 hover:text-gray-700 px-1" style="display:none;">← </button>
                                <span id="group-active-name" class="font-bold text-gray-800 text-sm"></span>
                                <span id="group-active-id" class="text-[10px] text-gray-400 ml-1"></span>
                            </div>
                            <div class="flex items-center gap-2">
                                <button id="group-mute-btn" onclick="toggleGroupMute()" class="text-xs px-2 py-1 rounded border font-bold" style="background:#fef2f2;color:#dc2626;border-color:#fecaca;" data-i18n="group_mute">🔇 急停</button>
                                <button onclick="toggleGroupMemberPanel()" class="text-xs bg-gray-50 hover:bg-gray-100 px-2 py-1 rounded border border-gray-200" data-i18n="group_members_btn">👤 成员</button>
                            </div>
                        </div>
                        <div id="group-messages-box" class="group-messages-box"></div>
                        <div class="group-input-area" style="position:relative;">
                            <div class="mention-popup" id="mention-popup">
                                <div class="mention-title">@ 选择要通知的 Agent</div>
                                <div id="mention-list"></div>
                                <button class="mention-confirm" onclick="confirmMention()">确认</button>
                            </div>
                            <textarea id="group-input" rows="1" placeholder="发送消息... 输入@选择Agent" data-i18n-placeholder="group_input_placeholder" onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();sendGroupMessage();}" oninput="onGroupInputChange(event)"></textarea>
                            <button onclick="sendGroupMessage()" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-xl font-bold text-sm flex-shrink-0" data-i18n="send_btn">发送</button>
                        </div>
                    </div>
                </div>

                <!-- Member panel (right side) -->
                <div class="group-member-panel" id="group-member-panel" style="display:none;">
                    <div class="panel-header flex justify-between items-center">
                        <span data-i18n="group_members">成员管理</span>
                        <button onclick="toggleGroupMemberPanel()" class="text-gray-400 hover:text-gray-600 text-sm">&times;</button>
                    </div>
                    <div class="p-2 border-b">
                        <div class="text-xs font-semibold text-gray-500 mb-2" data-i18n="group_current_members">当前成员</div>
                        <div id="group-current-members" class="member-list" style="max-height:200px;"></div>
                    </div>
                    <div class="p-2 flex-1 overflow-hidden flex flex-col">
                        <div class="text-xs font-semibold text-gray-500 mb-2" data-i18n="group_add_agents">添加 Agent Session</div>
                        <div id="group-available-sessions" class="flex-1 overflow-y-auto"></div>
                    </div>
                </div>
            </div>
        </div>
        <!-- end of group-page -->

        <!-- === Orchestration Page === -->
        <div id="page-orchestrate" class="orch-page">
            <div class="orch-layout">
                <!-- Left: Expert Pool -->
                <div class="orch-sidebar" style="overflow-y:auto;">
                    <div class="orch-sidebar-header">
                        <span class="text-sm font-bold text-gray-700">🧑‍💼 专家池</span>
                    </div>
                    <!-- Public experts -->
                    <div style="padding:2px 8px;font-size:10px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:0.5px;">📚 预设专家</div>
                    <div class="orch-expert-list" id="orch-expert-list-public"></div>
                    <!-- Custom experts -->
                    <div style="padding:2px 8px;font-size:10px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:0.5px;border-top:1px solid #e5e7eb;margin-top:4px;display:flex;align-items:center;justify-content:space-between;">
                        <span>🛠️ 自定义专家</span>
                        <button onclick="orchShowAddExpertModal()" style="font-size:14px;background:none;border:none;cursor:pointer;padding:0 2px;" title="添加自定义专家">➕</button>
                    </div>
                    <div class="orch-expert-list" id="orch-expert-list-custom"></div>
                    <!-- Session agents -->
                    <div style="padding:2px 8px;font-size:10px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:0.5px;border-top:1px solid #e5e7eb;margin-top:4px;display:flex;align-items:center;justify-content:space-between;">
                        <span>💬 Session Agent</span>
                        <button onclick="orchLoadSessionAgents()" style="font-size:11px;background:none;border:none;cursor:pointer;padding:0 2px;color:#2563eb;" title="刷新">🔄</button>
                    </div>
                    <div class="orch-expert-list" id="orch-expert-list-sessions"></div>
                    <!-- Manual injection -->
                    <div class="orch-manual-card" draggable="true" id="orch-manual-card">
                        <span style="font-size:18px;">📝</span>
                        <div><div class="text-xs font-semibold text-gray-700">手动注入</div><div class="text-[10px] text-purple-400">固定内容</div></div>
                    </div>
                    <div style="padding:6px 10px;font-size:10px;color:#9ca3af;border-top:1px solid #e5e7eb;">
                        <b>快捷操作：</b><br>• 拖入专家到画布<br>• 连接端口 = 工作流<br>• 选中 + Ctrl+G = 分组<br>• 双击侧栏快速添加
                    </div>
                </div>

                <!-- Center: Canvas -->
                <div class="orch-canvas-wrapper">
                    <!-- Toolbar -->
                    <div class="orch-toolbar">
                        <button onclick="orchAutoArrange()" class="orch-btn" title="自动排列">🔄 排列</button>
                        <button onclick="orchSaveLayout()" class="orch-btn" title="保存布局">💾 保存</button>
                        <button onclick="orchLoadLayout()" class="orch-btn" title="加载布局">📂 加载</button>
                        <button onclick="orchGenerateAgentYaml()" class="orch-btn orch-btn-primary" title="AI 生成 YAML">🤖 AI编排</button>
                        <button onclick="orchExportYaml()" class="orch-btn orch-btn-primary" title="复制 YAML">📋 导出</button>
                        <button onclick="orchRefreshSessions()" class="orch-btn" title="刷新 session 状态">🔄 状态</button>
                        <button onclick="orchClearCanvas()" class="orch-btn orch-btn-danger" title="清空画布">🗑️ 清空</button>
                    </div>
                    <div class="orch-canvas" id="orch-canvas-area">
                        <div class="orch-canvas-inner" id="orch-canvas-inner">
                            <svg id="orch-edge-svg" style="width:10000px;height:10000px;position:absolute;top:0;left:0;z-index:5;pointer-events:none;">
                                <defs><marker id="orch-arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#2563eb" /></marker></defs>
                            </svg>
                            <div id="orch-canvas-hint" style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;color:#9ca3af;pointer-events:none;z-index:1;">
                                <div style="font-size:40px;margin-bottom:8px;">🎯</div>
                                <div style="font-size:14px;font-weight:500;color:#6b7280;">拖入专家开始编排</div>
                                <div style="font-size:11px;margin-top:6px;color:#9ca3af;">拖入专家开始编排</div>
                            </div>
                        </div>
                        <div class="orch-nav-controls">
                            <div class="nav-row">
                                <button onclick="orchPanBy(0,-60)" title="上移">▲</button>
                            </div>
                            <div class="nav-row">
                                <button onclick="orchPanBy(-60,0)" title="左移">◀</button>
                                <button class="nav-center" onclick="orchResetView()" title="重置视图">⌂</button>
                                <button onclick="orchPanBy(60,0)" title="右移">▶</button>
                            </div>
                            <div class="nav-row">
                                <button onclick="orchPanBy(0,60)" title="下移">▼</button>
                            </div>
                            <div class="nav-zoom-row">
                                <button onclick="orchZoom(-0.1)" title="缩小">−</button>
                                <span id="orch-zoom-label" class="zoom-label">100%</span>
                                <button onclick="orchZoom(0.1)" title="放大">+</button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Right: Settings + YAML -->
                <div class="orch-right-panel">
                    <div class="orch-right-section">
                        <div class="text-xs font-bold text-gray-500 uppercase tracking-wide px-3 pt-3 pb-1">⚙️ 设置</div>
                        <div class="px-3 pb-2 space-y-1 text-xs text-gray-600 border-b border-gray-100">
                            <label class="flex items-center gap-2 cursor-pointer"><input type="checkbox" id="orch-repeat" checked class="accent-blue-600"> 每轮重复计划</label>
                            <label class="flex items-center gap-2">轮次: <input type="number" id="orch-rounds" value="5" min="1" max="20" class="w-12 px-1 py-0.5 border border-gray-300 rounded text-xs"></label>
                            <label class="flex items-center gap-2 cursor-pointer"><input type="checkbox" id="orch-bot-session" class="accent-blue-600"> 有状态模式</label>
                            <label class="flex items-center gap-2">聚类阈值: <input type="range" id="orch-threshold" min="50" max="400" value="150" class="flex-1 accent-blue-600"><span id="orch-threshold-val" class="text-[10px] text-gray-400">150</span></label>
                        </div>
                    </div>

                    <div class="orch-right-section">
                        <div class="text-xs font-bold text-gray-500 uppercase tracking-wide px-3 pt-2 pb-1">🤖 AI 生成</div>
                        <div id="orch-agent-status" class="mx-3 mb-1 px-2 py-1 rounded text-[10px] bg-gray-50 border border-gray-200 text-gray-400">
                            点击「🤖 AI编排」自动生成 YAML
                        </div>
                        <div class="px-3 pb-1">
                            <div class="text-[10px] text-gray-400 mb-1">📨 发送的 Prompt <button onclick="orchCopyPrompt()" class="text-[10px] text-blue-500 hover:underline float-right">复制</button></div>
                            <div class="orch-yaml-box text-[10px] text-amber-600" id="orch-prompt-content" style="max-height:100px;">点击 AI编排 后显示</div>
                        </div>
                        <div class="px-3 pb-1">
                            <div class="text-[10px] text-gray-400 mb-1">🤖 Agent YAML <button onclick="orchCopyAgentYaml()" class="text-[10px] text-blue-500 hover:underline float-right">复制</button></div>
                            <div class="orch-yaml-box text-[10px] text-green-600" id="orch-agent-yaml" style="max-height:140px;">等待 Agent 生成</div>
                        </div>
                    </div>

                    <div class="orch-right-section flex-1 flex flex-col min-h-0">
                        <div class="text-xs font-bold text-gray-500 uppercase tracking-wide px-3 pt-2 pb-1">📄 规则 YAML</div>
                        <div class="orch-yaml-box flex-1 mx-3 mb-2 text-xs text-green-700" id="orch-yaml-content">拖入专家后自动生成...</div>
                    </div>

                    <div class="orch-status-bar" id="orch-status-bar">节点: 0 | 连线: 0 | 分组: 0</div>
                </div>
            </div>
        </div>
        <!-- end of orchestrate-page -->
        </div>
        <!-- end of chat-main -->

        <!-- ===== 分割线 ===== -->
        <div class="oasis-divider" id="oasis-divider"></div>

        <!-- ===== 右侧：TeamsWork 讨论面板 ===== -->
        <div class="oasis-panel collapsed-panel bg-white border-l border-gray-200 flex flex-col h-screen" id="oasis-panel">
            <!-- Collapsed state expand button -->
            <div class="oasis-expand-btn items-center justify-center h-full text-gray-400 hover:text-blue-600 cursor-pointer text-sm font-bold" onclick="toggleOasisPanel()">
                🏛️ T E A M S
            </div>

            <!-- Panel content -->
            <div class="oasis-content flex flex-col h-full">
                <!-- Header -->
                <div class="p-3 border-b bg-gradient-to-r from-purple-50 to-blue-50 flex items-center justify-between flex-shrink-0">
                    <div class="flex items-center space-x-2">
                        <span class="text-lg">🏛️</span>
                        <div>
                            <h2 class="text-sm font-bold text-gray-800" data-i18n="oasis_title">TeamsWork 讨论论坛</h2>
                            <p class="text-[10px] text-gray-500" data-i18n="oasis_subtitle">多专家并行讨论系统</p>
                        </div>
                    </div>
                    <div class="flex items-center space-x-1">
                        <button onclick="refreshOasisTopics()" class="text-gray-400 hover:text-blue-600 p-1 rounded transition-colors" data-i18n-title="refresh" title="刷新">🔄</button>
                        <button onclick="toggleOasisPanel()" class="text-gray-400 hover:text-red-500 p-1 rounded transition-colors" data-i18n-title="collapse" title="收起">✕</button>
                    </div>
                </div>

                <!-- Topic list view -->
                <div id="oasis-topic-list-view" class="flex flex-col flex-1 overflow-hidden">
                    <div class="p-3 border-b flex-shrink-0">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-semibold text-gray-600" data-i18n="oasis_topics">📋 讨论话题</span>
                            <div class="flex items-center space-x-2">
                                <button onclick="deleteAllOasisTopics()" class="text-xs text-red-400 hover:text-red-600" data-i18n="delete_all">🗑️ 清空全部</button>
                                <span id="oasis-topic-count" class="text-[10px] text-gray-400"></span>
                            </div>
                        </div>
                    </div>
                    <div id="oasis-topic-list" class="flex-1 overflow-y-auto">
                        <div class="p-6 text-center text-gray-400 text-sm">
                            <div class="text-3xl mb-2">🏛️</div>
                            <p data-i18n="oasis_no_topics">暂无讨论话题</p>
                            <p class="text-xs mt-1" data-i18n="oasis_start_hint">在聊天中让 Agent 发起 TeamsWork 讨论</p>
                        </div>
                    </div>
                </div>

                <!-- Topic detail view (hidden by default) -->
                <div id="oasis-detail-view" class="flex flex-col flex-1 overflow-hidden" style="display:none;">
                    <!-- Detail header -->
                    <div class="p-3 border-b flex-shrink-0">
                        <div class="flex items-center justify-between">
                            <div class="flex items-center space-x-2">
                                <button onclick="showOasisTopicList()" class="text-gray-400 hover:text-blue-600 text-sm" data-i18n="oasis_back">← 返回</button>
                                <span id="oasis-detail-status" class="oasis-status-badge"></span>
                                <span id="oasis-detail-round" class="text-[10px] text-gray-400"></span>
                            </div>
                            <div id="oasis-detail-actions" class="flex items-center space-x-1">
                            </div>
                        </div>
                        <p id="oasis-detail-question" class="text-sm font-semibold text-gray-800 mt-1 line-clamp-2"></p>
                    </div>

                    <!-- Posts stream -->
                    <div id="oasis-posts-box" class="oasis-discussion-box flex-1 p-3 space-y-3 bg-gray-50">
                        <!-- Posts will be injected here -->
                    </div>

                    <!-- Conclusion area -->
                    <div id="oasis-conclusion-area" class="p-3 border-t flex-shrink-0" style="display:none;">
                        <div class="oasis-conclusion-box">
                            <div class="flex items-center space-x-1 mb-2">
                                <span class="text-sm">🏆</span>
                                <span class="text-xs font-bold text-green-800" data-i18n="oasis_conclusion">讨论结论</span>
                            </div>
                            <p id="oasis-conclusion-text" class="text-xs text-gray-700 leading-relaxed"></p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // ===== i18n 国际化配置 =====
        const i18n = {
            'zh-CN': {
                // 通用
                loading: '加载中...',
                error: '错误',
                success: '成功',
                cancel: '取消',
                confirm: '确认',
                close: '关闭',
                
                // 登录页
                login_title: 'Teamclaw',
                login_subtitle: '请登录以开始对话',
                username: '用户名',
                password: '密码',
                login_btn: '登录',
                login_verifying: '验证中...',
                login_error_invalid: '用户名只能包含字母、数字、下划线、短横线或中文',
                login_error_failed: '登录失败',
                login_error_network: '网络错误',
                login_footer: '身份验证后方可使用，对话和文件按用户隔离',
                
                // 头部
                encrypted: '● 已加密',
                history: '🤖Agents',
                new_chat: '+新',
                new_chat_mobile: '+',
                logout: '退出',
                current_session: '当前对话号',
                more_actions: '更多操作',
                
                // 移动端菜单
                menu_history: '🤖 Agents',
                menu_new: '➕ 新对话',
                menu_oasis: '🏛️ TeamsWork',
                menu_logout: '🚪 退出',
                
                // 聊天区域
                welcome_message: '你好！我是 Xavier 智能助手。我已经准备好为你服务，请输入你的指令。',
                new_session_message: '🆕 已开启新对话。我是 Xavier 智能助手，请输入你的指令。',
                input_placeholder: '输入指令...（可粘贴图片/上传文件/录音）',
                send_btn: '发送',
                cancel_btn: '终止',
                busy_btn: '系统占用中',
                new_system_msg: '有新的系统消息',
                click_refresh: '点击刷新',
                no_response: '（无响应）',
                thinking_stopped: '⚠️ 已终止思考',
                login_expired: '⚠️ 登录已过期，请重新登录',
                agent_error: '❌ 错误',
                
                // 工具面板
                available_tools: '🧰 可用工具',
                tool_calling: '（调用工具中...）',
                tool_return: '🔧 工具返回',
                
                // 文件上传
                max_images: '最多上传5张图片',
                max_files: '最多上传3个文件',
                max_audios: '最多上传2个音频',
                audio_too_large: '音频过大，上限 25MB',
                video_too_large: '视频过大，上限 50MB',
                pdf_too_large: 'PDF过大，上限 10MB',
                file_too_large: '文件过大，上限 512KB',
                unsupported_type: '不支持的文件类型',
                supported_types: '支持: txt, md, csv, json, py, js, pdf, mp3, wav, avi, mp4 等',
                
                // 录音
                recording_title: '录音',
                recording_stop: '点击停止录音',
                mic_permission_denied: '无法访问麦克风，请检查浏览器权限设置。',
                recording_too_long: '录音过长，上限 25MB',
                
                // 历史会话
                history_title: '🤖 Agents',
                history_loading: '加载中...',
                history_empty: '暂无历史对话',
                history_error: '加载失败',
                history_loading_msg: '加载历史消息...',
                history_no_msg: '（此对话暂无消息记录）',
                new_session_confirm: '开启新对话？当前对话的历史记录将保留，可通过切回对话号恢复。',
                messages_count: '条消息',
                session_id: '对话号',
                delete_session: '删除',
                delete_session_confirm: '确定删除此对话？删除后不可恢复。',
                delete_all_confirm: '确定删除所有对话记录？此操作不可恢复！',
                delete_success: '删除成功',
                delete_fail: '删除失败',
                delete_all: '🗑️ 清空全部',
                
                // TTS
                tts_read: '朗读',
                tts_stop: '停止',
                tts_loading: '加载中...',
                tts_request_failed: 'TTS 请求失败',
                code_omitted: '（代码省略）',
                image_placeholder: '(图片)',
                audio_placeholder: '(语音)',
                file_placeholder: '(文件)',
                
                // OASIS
                oasis_title: 'TeamsWork 讨论论坛',
                oasis_subtitle: '多专家并行讨论系统',
                oasis_topics: '📋 讨论话题',
                oasis_topics_count: '个话题',
                oasis_no_topics: '暂无讨论话题',
                oasis_start_hint: '在聊天中让 Agent 发起 TeamsWork 讨论',
                oasis_back: '← 返回',
                oasis_conclusion: '讨论结论',
                oasis_waiting: '等待专家发言...',
                oasis_status_pending: '等待中',
                oasis_status_discussing: '讨论中',
                oasis_status_concluded: '已完成',
                oasis_status_error: '出错',
                oasis_status_cancelled: '已终止',
                oasis_round: '轮',
                oasis_posts: '帖',
                oasis_expert_creative: '创意专家',
                oasis_expert_critical: '批判专家',
                oasis_expert_data: '数据分析师',
                oasis_expert_synthesis: '综合顾问',
                oasis_cancel: '终止讨论',
                oasis_cancel_confirm: '确定要强制终止此讨论？',
                oasis_cancel_success: '讨论已终止',
                oasis_delete: '删除记录',
                oasis_delete_confirm: '确定要永久删除此讨论记录？删除后不可恢复。',
                oasis_delete_success: '记录已删除',
                oasis_action_fail: '操作失败',
                
                // 页面切换
                tab_chat: '💬 对话',
                tab_group: '👥 群聊',
                
                // 群聊
                group_title: '👥 群聊列表',
                group_new: '+ 新建',
                group_no_groups: '暂无群聊',
                group_select_hint: '选择或创建一个群聊',
                group_members_btn: '👤 成员',
                group_mute: '🔇 急停',
                group_unmute: '🔊 恢复',
                group_members: '成员管理',
                group_current_members: '当前成员',
                group_add_agents: '添加 Agent Session',
                group_input_placeholder: '发送消息...',
                group_create_title: '创建群聊',
                group_name_placeholder: '群聊名称',
                group_no_sessions: '没有可用的 Agent Session',
                group_create_btn: '创建',
                group_delete_confirm: '确定删除此群聊？',
                group_owner: '群主',
                group_agent: 'Agent',
                group_msg_count: '条消息',
                group_member_count: '人',
                
                // 离线提示
                offline_banner: '⚠️ 网络已断开，请检查连接',
                
                // 其他
                splash_subtitle: 'Xavier AI Agent',
                secure_footer: 'Secured by Nginx Reverse Proxy & SSH Tunnel',
                refresh: '刷新',
                collapse: '收起',
            },
            'en': {
                // General
                loading: 'Loading...',
                error: 'Error',
                success: 'Success',
                cancel: 'Cancel',
                confirm: 'Confirm',
                close: 'Close',
                
                // Login
                login_title: 'Teamclaw',
                login_subtitle: 'Please login to start',
                username: 'Username',
                password: 'Password',
                login_btn: 'Login',
                login_verifying: 'Verifying...',
                login_error_invalid: 'Username can only contain letters, numbers, underscore, hyphen or Chinese',
                login_error_failed: 'Login failed',
                login_error_network: 'Network error',
                login_footer: 'Authentication required. Conversations and files are isolated by user',
                
                // Header
                encrypted: '● Encrypted',
                history: '🤖 Agents',
                new_chat: '+New',
                new_chat_mobile: '+',
                logout: 'Logout',
                current_session: 'Current session',
                more_actions: 'More actions',
                
                // Mobile menu
                menu_history: '🤖 Agents',
                menu_new: '➕ New Chat',
                menu_oasis: '🏛️ TeamsWork',
                menu_logout: '🚪 Logout',
                
                // Chat area
                welcome_message: 'Hello! I am Xavier AI Assistant. Ready to serve you. Please enter your instructions.',
                new_session_message: '🆕 New conversation started. I am Xavier AI Assistant. Please enter your instructions.',
                input_placeholder: 'Enter command... (paste images/upload files/record audio)',
                send_btn: 'Send',
                cancel_btn: 'Stop',
                busy_btn: 'System Busy',
                new_system_msg: 'New system message',
                click_refresh: 'Click to refresh',
                no_response: '(No response)',
                thinking_stopped: '⚠️ Thinking stopped',
                login_expired: '⚠️ Session expired, please login again',
                agent_error: '❌ Error',
                
                // Tool panel
                available_tools: '🧰 Available Tools',
                tool_calling: '(Calling tool...)',
                tool_return: '🔧 Tool Return',
                
                // File upload
                max_images: 'Maximum 5 images',
                max_files: 'Maximum 3 files',
                max_audios: 'Maximum 2 audio files',
                audio_too_large: 'Audio too large, limit 25MB',
                video_too_large: 'Video too large, limit 50MB',
                pdf_too_large: 'PDF too large, limit 10MB',
                file_too_large: 'File too large, limit 512KB',
                unsupported_type: 'Unsupported file type',
                supported_types: 'Supported: txt, md, csv, json, py, js, pdf, mp3, wav, avi, mp4, etc.',
                
                // Recording
                recording_title: 'Record',
                recording_stop: 'Click to stop recording',
                mic_permission_denied: 'Cannot access microphone. Please check browser permissions.',
                recording_too_long: 'Recording too long, limit 25MB',
                
                // History sessions
                history_title: '🤖 Agents',
                history_loading: 'Loading...',
                history_empty: 'No history',
                history_error: 'Failed to load',
                history_loading_msg: 'Loading messages...',
                history_no_msg: '(No messages in this conversation)',
                new_session_confirm: 'Start new conversation? Current history will be preserved.',
                messages_count: 'messages',
                session_id: 'Session',
                delete_session: 'Delete',
                delete_session_confirm: 'Delete this conversation? This cannot be undone.',
                delete_all_confirm: 'Delete ALL conversations? This cannot be undone!',
                delete_success: 'Deleted',
                delete_fail: 'Delete failed',
                delete_all: '🗑️ Clear All',
                
                // TTS
                tts_read: 'Read',
                tts_stop: 'Stop',
                tts_loading: 'Loading...',
                tts_request_failed: 'TTS request failed',
                code_omitted: '(code omitted)',
                image_placeholder: '(image)',
                audio_placeholder: '(audio)',
                file_placeholder: '(file)',
                
                // OASIS
                oasis_title: 'TeamsWork Discussion Forum',
                oasis_subtitle: 'Multi-Expert Parallel Discussion System',
                oasis_topics: '📋 Discussion Topics',
                oasis_topics_count: 'topics',
                oasis_no_topics: 'No discussion topics',
                oasis_start_hint: 'Ask Agent to start a TeamsWork discussion in chat',
                oasis_back: '← Back',
                oasis_conclusion: 'Conclusion',
                oasis_waiting: 'Waiting for experts...',
                oasis_status_pending: 'Pending',
                oasis_status_discussing: 'Discussing',
                oasis_status_concluded: 'Completed',
                oasis_status_error: 'Error',
                oasis_status_cancelled: 'Cancelled',
                oasis_round: 'rounds',
                oasis_posts: 'posts',
                oasis_expert_creative: 'Creative Expert',
                oasis_expert_critical: 'Critical Expert',
                oasis_expert_data: 'Data Analyst',
                oasis_expert_synthesis: 'Synthesis Advisor',
                oasis_cancel: 'Stop Discussion',
                oasis_cancel_confirm: 'Force stop this discussion?',
                oasis_cancel_success: 'Discussion stopped',
                oasis_delete: 'Delete',
                oasis_delete_confirm: 'Permanently delete this discussion? This cannot be undone.',
                oasis_delete_success: 'Record deleted',
                oasis_action_fail: 'Action failed',
                
                // Page switch
                tab_chat: '💬 Chat',
                tab_group: '👥 Groups',
                
                // Group chat
                group_title: '👥 Group Chats',
                group_new: '+ New',
                group_no_groups: 'No group chats',
                group_select_hint: 'Select or create a group chat',
                group_members_btn: '👤 Members',
                group_mute: '🔇 Stop',
                group_unmute: '🔊 Resume',
                group_members: 'Member Management',
                group_current_members: 'Current Members',
                group_add_agents: 'Add Agent Session',
                group_input_placeholder: 'Send a message...',
                group_create_title: 'Create Group Chat',
                group_name_placeholder: 'Group name',
                group_no_sessions: 'No available Agent Sessions',
                group_create_btn: 'Create',
                group_delete_confirm: 'Delete this group chat?',
                group_owner: 'Owner',
                group_agent: 'Agent',
                group_msg_count: 'messages',
                group_member_count: 'members',
                
                // Offline
                offline_banner: '⚠️ Network disconnected, please check connection',
                
                // Others
                splash_subtitle: 'Xavier AI Agent',
                secure_footer: 'Secured by Nginx Reverse Proxy & SSH Tunnel',
                refresh: 'Refresh',
                collapse: 'Collapse',
            }
        };
        
        // 当前语言
        let currentLang = localStorage.getItem('lang') || 'zh-CN';
        // 确保语言值有效
        if (!i18n[currentLang]) { currentLang = 'zh-CN'; localStorage.setItem('lang', 'zh-CN'); }
        
        // 获取翻译文本
        function t(key) {
            return (i18n[currentLang] && i18n[currentLang][key]) || i18n['zh-CN'][key] || key;
        }
        
        // 切换语言
        function toggleLanguage() {
            currentLang = currentLang === 'zh-CN' ? 'en' : 'zh-CN';
            localStorage.setItem('lang', currentLang);
            document.documentElement.lang = currentLang;
            applyTranslations();
        }
        
        // 应用翻译到页面
        function applyTranslations() {
            // 更新语言按钮显示
            const langBtn = document.getElementById('lang-toggle-btn');
            if (langBtn) {
                langBtn.textContent = currentLang === 'zh-CN' ? 'EN' : '中文';
            }
            
            // 更新 data-i18n 属性的元素
            document.querySelectorAll('[data-i18n]').forEach(el => {
                const key = el.getAttribute('data-i18n');
                if (el.tagName === 'INPUT' && el.hasAttribute('placeholder')) {
                    el.placeholder = t(key);
                } else if (el.tagName === 'TEXTAREA' && el.hasAttribute('placeholder')) {
                    el.placeholder = t(key);
                } else {
                    el.textContent = t(key);
                }
            });
            
            // 更新 data-i18n-placeholder 属性
            document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
                el.placeholder = t(el.getAttribute('data-i18n-placeholder'));
            });
            
            // 更新 title
            document.title = 'Teamclaw | AI Agent';
        }
        
        marked.setOptions({
            highlight: function(code, lang) {
                const language = hljs.getLanguage(lang) ? lang : 'plaintext';
                return hljs.highlight(code, { language }).value;
            },
            langPrefix: 'hljs language-'
        });

        let currentUserId = null;
        let currentSessionId = null;
        let currentAbortController = null;
        let cancelTargetSessionId = null;  // 终止按钮绑定的会话ID
        let pendingImages = []; // [{base64: "data:image/...", name: "file.jpg"}, ...]
        let pendingFiles = [];  // [{name: "data.csv", content: "...(text content)"}, ...]
        let pendingAudios = []; // [{base64: "data:audio/...", name: "recording.wav", format: "wav"}, ...]
        let isRecording = false;

        // OpenAI API 配置
        function getAuthToken() { return sessionStorage.getItem('authToken') || ''; }
        const TEXT_EXTENSIONS = new Set(['.txt','.md','.csv','.json','.xml','.yaml','.yml','.log','.py','.js','.ts','.html','.css','.java','.c','.cpp','.h','.go','.rs','.sh','.bat','.ini','.toml','.cfg','.conf','.sql','.r','.rb']);
        const AUDIO_EXTENSIONS = new Set(['.mp3','.wav','.ogg','.m4a','.webm','.flac','.aac']);
        const VIDEO_EXTENSIONS = new Set(['.avi','.mp4','.mkv','.mov']);
        const MAX_FILE_SIZE = 512 * 1024; // 512KB per text file
        const MAX_PDF_SIZE = 10 * 1024 * 1024; // 10MB per PDF
        const MAX_AUDIO_SIZE = 25 * 1024 * 1024; // 25MB per audio
        const MAX_VIDEO_SIZE = 50 * 1024 * 1024; // 50MB per video
        const MAX_IMAGE_SIZE = 10 * 1024 * 1024; // 压缩目标：10MB
        const MAX_IMAGE_DIMENSION = 2048; // 最大边长

        function compressImage(file) {
            return new Promise((resolve) => {
                const img = new Image();
                img.onload = () => {
                    let { width, height } = img;
                    if (width > MAX_IMAGE_DIMENSION || height > MAX_IMAGE_DIMENSION) {
                        const scale = MAX_IMAGE_DIMENSION / Math.max(width, height);
                        width = Math.round(width * scale);
                        height = Math.round(height * scale);
                    }
                    const canvas = document.createElement('canvas');
                    canvas.width = width;
                    canvas.height = height;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0, width, height);
                    let quality = 0.85;
                    let result = canvas.toDataURL('image/jpeg', quality);
                    while (result.length > MAX_IMAGE_SIZE * 1.37 && quality > 0.3) {
                        quality -= 0.1;
                        result = canvas.toDataURL('image/jpeg', quality);
                    }
                    resolve(result);
                };
                img.src = URL.createObjectURL(file);
            });
        }

        // ===== File Upload Logic (images + text files + PDF + audio) =====
        function handleFileSelect(event) {
            const files = event.target.files;
            if (!files.length) return;
            for (const file of files) {
                if (file.type.startsWith('image/')) {
                    if (pendingImages.length >= 5) { alert(t('max_images')); break; }
                    if (file.size <= MAX_IMAGE_SIZE) {
                        const reader = new FileReader();
                        reader.onload = (e) => {
                            pendingImages.push({ base64: e.target.result, name: file.name });
                            renderImagePreviews();
                        };
                        reader.readAsDataURL(file);
                    } else {
                        compressImage(file).then((compressed) => {
                            pendingImages.push({ base64: compressed, name: file.name });
                            renderImagePreviews();
                        });
                    }
                } else if (file.type.startsWith('audio/') || AUDIO_EXTENSIONS.has('.' + file.name.split('.').pop().toLowerCase())) {
                    if (file.size > MAX_AUDIO_SIZE) { alert(`${file.name}: ${t('audio_too_large')} (${(file.size/1024/1024).toFixed(1)}MB)`); continue; }
                    if (pendingAudios.length >= 2) { alert(t('max_audios')); break; }
                    const ext = file.name.split('.').pop().toLowerCase();
                    const fmt = ({'mp3':'mp3','wav':'wav','ogg':'ogg','m4a':'m4a','webm':'webm','flac':'flac','aac':'aac'})[ext] || 'mp3';
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        pendingAudios.push({ base64: e.target.result, name: file.name, format: fmt });
                        renderAudioPreviews();
                    };
                    reader.readAsDataURL(file);
                } else if (file.type.startsWith('video/') || VIDEO_EXTENSIONS.has('.' + file.name.split('.').pop().toLowerCase())) {
                    // 视频文件：以 dataURL 形式存入 pendingFiles，type='media'
                    if (file.size > MAX_VIDEO_SIZE) { alert(`${file.name}: ${t('video_too_large')} (${(file.size/1024/1024).toFixed(1)}MB)`); continue; }
                    if (pendingFiles.length >= 3) { alert(t('max_files')); break; }
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        pendingFiles.push({ name: file.name, content: e.target.result, type: 'media' });
                        renderFilePreviews();
                    };
                    reader.readAsDataURL(file);
                } else if (file.name.toLowerCase().endsWith('.pdf') || file.type === 'application/pdf') {
                    if (file.size > MAX_PDF_SIZE) { alert(`${file.name}: ${t('pdf_too_large')} (${(file.size/1024/1024).toFixed(1)}MB)`); continue; }
                    if (pendingFiles.length >= 3) { alert(t('max_files')); break; }
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        pendingFiles.push({ name: file.name, content: e.target.result, type: 'pdf' });
                        renderFilePreviews();
                    };
                    reader.readAsDataURL(file);
                } else {
                    const ext = '.' + file.name.split('.').pop().toLowerCase();
                    if (!TEXT_EXTENSIONS.has(ext)) { alert(`${t('unsupported_type')}: ${ext}\\n${t('supported_types')}`); continue; }
                    if (file.size > MAX_FILE_SIZE) { alert(`${file.name}: ${t('file_too_large')} (${(file.size/1024).toFixed(0)}KB)`); continue; }
                    if (pendingFiles.length >= 3) { alert(t('max_files')); break; }
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        pendingFiles.push({ name: file.name, content: e.target.result, type: 'text' });
                        renderFilePreviews();
                    };
                    reader.readAsText(file);
                }
            }
            event.target.value = '';
        }

        // ===== Audio Recording =====
        async function toggleRecording() {
            if (isRecording) {
                stopRecording();
            } else {
                await startRecording();
            }
        }

        // --- WAV 编码辅助函数 ---
        function encodeWAV(samples, sampleRate) {
            const buffer = new ArrayBuffer(44 + samples.length * 2);
            const view = new DataView(buffer);
            function writeString(offset, string) {
                for (let i = 0; i < string.length; i++) view.setUint8(offset + i, string.charCodeAt(i));
            }
            writeString(0, 'RIFF');
            view.setUint32(4, 36 + samples.length * 2, true);
            writeString(8, 'WAVE');
            writeString(12, 'fmt ');
            view.setUint32(16, 16, true);
            view.setUint16(20, 1, true); // PCM
            view.setUint16(22, 1, true); // mono
            view.setUint32(24, sampleRate, true);
            view.setUint32(28, sampleRate * 2, true);
            view.setUint16(32, 2, true);
            view.setUint16(34, 16, true);
            writeString(36, 'data');
            view.setUint32(40, samples.length * 2, true);
            for (let i = 0; i < samples.length; i++) {
                const s = Math.max(-1, Math.min(1, samples[i]));
                view.setInt16(44 + i * 2, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
            }
            return new Blob([buffer], { type: 'audio/wav' });
        }

        let audioContext = null;
        let audioSourceNode = null;
        let audioProcessorNode = null;
        let recordedSamples = [];

        async function startRecording() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
                audioSourceNode = audioContext.createMediaStreamSource(stream);
                audioProcessorNode = audioContext.createScriptProcessor(4096, 1, 1);
                recordedSamples = [];
                audioProcessorNode.onaudioprocess = (e) => {
                    const data = e.inputBuffer.getChannelData(0);
                    recordedSamples.push(new Float32Array(data));
                };
                audioSourceNode.connect(audioProcessorNode);
                audioProcessorNode.connect(audioContext.destination);
                isRecording = true;
                document.getElementById('record-btn').classList.add('recording');
                document.getElementById('record-btn').title = t('recording_stop');
            } catch (err) {
                alert(t('mic_permission_denied') + '\\n' + err.message);
            }
        }

        function stopRecording() {
            if (!audioContext) return;
            const stream = audioSourceNode.mediaStream;
            audioProcessorNode.disconnect();
            audioSourceNode.disconnect();
            stream.getTracks().forEach(t => t.stop());
            // 合并所有采样
            let totalLen = 0;
            for (const chunk of recordedSamples) totalLen += chunk.length;
            const merged = new Float32Array(totalLen);
            let offset = 0;
            for (const chunk of recordedSamples) { merged.set(chunk, offset); offset += chunk.length; }
            const sampleRate = audioContext.sampleRate;
            audioContext.close();
            audioContext = null;
            audioSourceNode = null;
            audioProcessorNode = null;
            recordedSamples = [];
            isRecording = false;
            document.getElementById('record-btn').classList.remove('recording');
            document.getElementById('record-btn').title = t('recording_title');
            const blob = encodeWAV(merged, sampleRate);
            if (blob.size > MAX_AUDIO_SIZE) { alert(t('recording_too_long')); return; }
            if (pendingAudios.length >= 2) { alert(t('max_audios')); return; }
            const reader = new FileReader();
            reader.onload = (e) => {
                const ts = new Date().toLocaleTimeString(currentLang === 'zh-CN' ? 'zh-CN' : 'en-US', {hour:'2-digit',minute:'2-digit',second:'2-digit'});
                const recName = currentLang === 'zh-CN' ? `录音_${ts}.wav` : `recording_${ts}.wav`;
                pendingAudios.push({ base64: e.target.result, name: recName, format: 'wav' });
                renderAudioPreviews();
            };
            reader.readAsDataURL(blob);
        }

        function removeAudio(index) {
            pendingAudios.splice(index, 1);
            renderAudioPreviews();
        }

        function renderAudioPreviews() {
            const area = document.getElementById('audio-preview-area');
            if (pendingAudios.length === 0) {
                area.style.display = 'none';
                area.innerHTML = '';
                return;
            }
            area.style.display = 'flex';
            area.innerHTML = pendingAudios.map((a, i) => `
                <div class="audio-preview-item">
                    <span class="file-icon">🎤</span>
                    <span class="file-name" title="${escapeHtml(a.name)}">${escapeHtml(a.name)}</span>
                    <button class="remove-btn" onclick="removeAudio(${i})">&times;</button>
                </div>
            `).join('');
        }

        function handlePasteImage(event) {
            const items = event.clipboardData?.items;
            if (!items) return;
            for (const item of items) {
                if (!item.type.startsWith('image/')) continue;
                event.preventDefault();
                if (pendingImages.length >= 5) { alert(t('max_images')); break; }
                const file = item.getAsFile();
                const reader = new FileReader();
                reader.onload = (e) => {
                    pendingImages.push({ base64: e.target.result, name: 'pasted_image.png' });
                    renderImagePreviews();
                };
                reader.readAsDataURL(file);
            }
        }

        function removeImage(index) {
            pendingImages.splice(index, 1);
            renderImagePreviews();
        }

        function removeFile(index) {
            pendingFiles.splice(index, 1);
            renderFilePreviews();
        }

        function renderImagePreviews() {
            const area = document.getElementById('image-preview-area');
            if (pendingImages.length === 0) {
                area.style.display = 'none';
                area.innerHTML = '';
                return;
            }
            area.style.display = 'flex';
            area.innerHTML = pendingImages.map((img, i) => `
                <div class="image-preview-item">
                    <img src="${img.base64}" alt="${img.name}">
                    <button class="remove-btn" onclick="removeImage(${i})">&times;</button>
                </div>
            `).join('');
        }

        function renderFilePreviews() {
            const area = document.getElementById('file-preview-area');
            if (pendingFiles.length === 0) {
                area.style.display = 'none';
                area.innerHTML = '';
                return;
            }
            area.style.display = 'flex';
            area.innerHTML = pendingFiles.map((f, i) => `
                <div class="file-preview-item">
                    <span class="file-icon">${f.type === 'media' ? '🎬' : '📄'}</span>
                    <span class="file-name" title="${escapeHtml(f.name)}">${escapeHtml(f.name)}</span>
                    <button class="remove-btn" onclick="removeFile(${i})">&times;</button>
                </div>
            `).join('');
        }

        // ===== Session (conversation) ID management =====
        function generateSessionId() {
            return Date.now().toString(36) + Math.random().toString(36).substr(2, 4);
        }

        function initSession() {
            let saved = sessionStorage.getItem('sessionId');
            if (!saved) {
                saved = generateSessionId();
                sessionStorage.setItem('sessionId', saved);
            }
            currentSessionId = saved;
            updateSessionDisplay();
        }

        function updateSessionDisplay() {
            const el = document.getElementById('session-display');
            if (el && currentSessionId) {
                el.textContent = '#' + currentSessionId.slice(-6);
                el.title = t('session_id') + ': ' + currentSessionId;
            }
        }

        function handleNewSession() {
            if (!confirm(t('new_session_confirm'))) return;
            currentSessionId = generateSessionId();
            sessionStorage.setItem('sessionId', currentSessionId);
            updateSessionDisplay();
            // Clear chat box for new conversation
            const chatBox = document.getElementById('chat-box');
            chatBox.innerHTML = `
                <div class="flex justify-start">
                    <div class="message-agent bg-white border p-4 max-w-[85%] shadow-sm text-gray-700">
                        ${t('new_session_message')}
                    </div>
                </div>`;
        }

        // ===== 历史会话侧边栏 =====
        let sessionSidebarOpen = false;
        let _historyPollingTimer = null;

        function startHistoryPolling() {
            stopHistoryPolling();
            _historyPollingTimer = setInterval(() => {
                if (sessionSidebarOpen) {
                    refreshHistoryList();
                } else {
                    // sidebar 未打开也刷新状态（发光效果），以便打开时立即可见
                    refreshSessionStatus();
                }
            }, 1000);
        }
        function stopHistoryPolling() {
            if (_historyPollingTimer) { clearInterval(_historyPollingTimer); _historyPollingTimer = null; }
        }

        function toggleSessionSidebar() {
            if (sessionSidebarOpen) { closeSessionSidebar(); } else { openSessionSidebar(); }
        }

        async function openSessionSidebar() {
            const sidebar = document.getElementById('session-sidebar');
            sidebar.style.display = 'flex';
            sessionSidebarOpen = true;
            // 移动端加遮罩
            if (window.innerWidth <= 768) {
                let overlay = document.getElementById('session-overlay');
                if (!overlay) {
                    overlay = document.createElement('div');
                    overlay.id = 'session-overlay';
                    overlay.className = 'session-overlay';
                    overlay.onclick = closeSessionSidebar;
                    sidebar.parentElement.appendChild(overlay);
                }
                overlay.style.display = 'block';
            }
            // 已有列表内容则增量刷新，否则全量加载
            const listEl = document.getElementById('session-list');
            if (listEl.querySelector('.session-item')) {
                refreshHistoryList();
            } else {
                await loadSessionList();
            }
        }

        function closeSessionSidebar() {
            document.getElementById('session-sidebar').style.display = 'none';
            const overlay = document.getElementById('session-overlay');
            if (overlay) overlay.style.display = 'none';
            sessionSidebarOpen = false;
        }

        async function loadSessionList() {
            const listEl = document.getElementById('session-list');
            if (!listEl.querySelector('.session-item')) {
                listEl.innerHTML = `<div class="text-xs text-gray-400 text-center py-4">${t('loading')}</div>`;
            }
            try {
                const resp = await fetch('/proxy_sessions');
                const data = await resp.json();
                if (!data.sessions || data.sessions.length === 0) {
                    listEl.innerHTML = `<div class="text-xs text-gray-400 text-center py-4">${t('history_empty')}</div>`;
                    return;
                }
                listEl.innerHTML = '';
                data.sessions.sort((a, b) => b.session_id.localeCompare(a.session_id));
                for (const s of data.sessions) {
                    const isActive = s.session_id === currentSessionId;
                    const div = document.createElement('div');
                    div.className = 'session-item' + (isActive ? ' active' : '');
                    div.dataset.sessionId = s.session_id;
                    div.innerHTML = `
                        <div class="session-title">${escapeHtml(s.title)}</div>
                        <div class="session-meta">#${s.session_id.slice(-6)} · ${s.message_count}${t('messages_count')}</div>
                        <button class="session-delete" onclick="event.stopPropagation(); deleteSession('${s.session_id}')">${t('delete_session')}</button>
                    `;
                    div.onclick = () => switchToSession(s.session_id);
                    listEl.appendChild(div);
                }
                refreshSessionStatus();
            } catch (e) {
                listEl.innerHTML = `<div class="text-xs text-red-400 text-center py-4">${t('history_error')}</div>`;
            }
        }

        // 增量刷新：不重建DOM，只更新标题/计数 + 状态发光
        async function refreshHistoryList() {
            try {
                const [sessResp, statusResp] = await Promise.all([
                    fetch('/proxy_sessions'),
                    fetch('/proxy_sessions_status')
                ]);
                const sessData = await sessResp.json();
                const statusData = statusResp.ok ? await statusResp.json() : {};
                const sessions = sessData.sessions || [];
                const listEl = document.getElementById('session-list');
                if (sessions.length === 0) {
                    listEl.innerHTML = `<div class="text-xs text-gray-400 text-center py-4">${t('history_empty')}</div>`;
                    return;
                }
                // 构建 session map
                const sessMap = {};
                for (const s of sessions) sessMap[s.session_id] = s;
                const statusMap = {};
                if (statusData.sessions) {
                    for (const s of statusData.sessions) statusMap[s.session_id] = s;
                }
                // 现有 DOM 的 session id 集合
                const existingEls = listEl.querySelectorAll('.session-item[data-session-id]');
                const existingIds = new Set();
                existingEls.forEach(el => existingIds.add(el.dataset.sessionId));
                const newIds = new Set(sessions.map(s => s.session_id));
                // 删除不存在的
                existingEls.forEach(el => {
                    if (!newIds.has(el.dataset.sessionId)) el.remove();
                });
                // 更新现有的 + 添加新的
                sessions.sort((a, b) => b.session_id.localeCompare(a.session_id));
                let prevEl = null;
                for (const s of sessions) {
                    let div = listEl.querySelector(`.session-item[data-session-id="${s.session_id}"]`);
                    if (div) {
                        // 更新标题和计数
                        const titleEl = div.querySelector('.session-title');
                        const newTitle = escapeHtml(s.title);
                        if (titleEl && titleEl.innerHTML !== newTitle) titleEl.innerHTML = newTitle;
                        const metaEl = div.querySelector('.session-meta');
                        if (metaEl) {
                            const badge = metaEl.querySelector('.session-busy-badge');
                            const newMeta = `#${s.session_id.slice(-6)} · ${s.message_count}${t('messages_count')}`;
                            // 只更新文本部分，保留badge
                            const textNode = metaEl.firstChild;
                            if (textNode && textNode.nodeType === 3) {
                                if (textNode.textContent.trim() !== newMeta.trim()) textNode.textContent = newMeta;
                            } else {
                                // 重建meta但保留badge
                                const savedBadge = badge;
                                metaEl.textContent = newMeta;
                                if (savedBadge) metaEl.appendChild(savedBadge);
                            }
                        }
                        // active 状态
                        div.classList.toggle('active', s.session_id === currentSessionId);
                    } else {
                        // 新增的 session
                        div = document.createElement('div');
                        div.className = 'session-item' + (s.session_id === currentSessionId ? ' active' : '');
                        div.dataset.sessionId = s.session_id;
                        div.innerHTML = `
                            <div class="session-title">${escapeHtml(s.title)}</div>
                            <div class="session-meta">#${s.session_id.slice(-6)} · ${s.message_count}${t('messages_count')}</div>
                            <button class="session-delete" onclick="event.stopPropagation(); deleteSession('${s.session_id}')">${t('delete_session')}</button>
                        `;
                        div.onclick = () => switchToSession(s.session_id);
                        if (prevEl && prevEl.nextSibling) {
                            listEl.insertBefore(div, prevEl.nextSibling);
                        } else if (!prevEl) {
                            listEl.prepend(div);
                        } else {
                            listEl.appendChild(div);
                        }
                    }
                    // 更新发光状态（不移除再添加class，避免动画重启）
                    const info = statusMap[s.session_id];
                    const wantUser = info && info.busy && info.source !== 'system';
                    const wantSystem = info && info.busy && info.source === 'system';
                    const hasUser = div.classList.contains('busy-user');
                    const hasSystem = div.classList.contains('busy-system');
                    if (wantUser && !hasUser) { div.classList.remove('busy-system'); div.classList.add('busy-user'); }
                    else if (wantSystem && !hasSystem) { div.classList.remove('busy-user'); div.classList.add('busy-system'); }
                    else if (!wantUser && !wantSystem) { div.classList.remove('busy-user', 'busy-system'); }
                    // badge
                    const existingBadge = div.querySelector('.session-busy-badge');
                    if (info && info.busy) {
                        const badgeCls = info.source === 'system' ? 'system' : 'user';
                        const badgeText = info.source === 'system' ? '⚙️' : '💬';
                        if (existingBadge) {
                            if (!existingBadge.classList.contains(badgeCls)) {
                                existingBadge.className = 'session-busy-badge ' + badgeCls;
                                existingBadge.textContent = badgeText;
                            }
                        } else {
                            const badge = document.createElement('span');
                            badge.className = 'session-busy-badge ' + badgeCls;
                            badge.textContent = badgeText;
                            div.querySelector('.session-meta')?.appendChild(badge);
                        }
                    } else if (existingBadge) {
                        existingBadge.remove();
                    }
                    prevEl = div;
                }
            } catch (e) { /* silent */ }
        }

        async function refreshSessionStatus() {
            try {
                const resp = await fetch('/proxy_sessions_status');
                if (!resp.ok) return;
                const data = await resp.json();
                if (!data.sessions) return;
                const statusMap = {};
                for (const s of data.sessions) statusMap[s.session_id] = s;
                document.querySelectorAll('.session-item[data-session-id]').forEach(el => {
                    const sid = el.dataset.sessionId;
                    const info = statusMap[sid];
                    el.classList.remove('busy-user', 'busy-system');
                    el.querySelector('.session-busy-badge')?.remove();
                    if (info && info.busy) {
                        const cls = info.source === 'system' ? 'busy-system' : 'busy-user';
                        el.classList.add(cls);
                        const badge = document.createElement('span');
                        badge.className = 'session-busy-badge ' + (info.source === 'system' ? 'system' : 'user');
                        badge.textContent = info.source === 'system' ? '⚙️' : '💬';
                        el.querySelector('.session-meta')?.appendChild(badge);
                    }
                });
            } catch (e) { /* silent */ }
        }

        async function deleteSession(sessionId) {
            if (!confirm(t('delete_session_confirm'))) return;
            try {
                const resp = await fetch('/proxy_delete_session', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ session_id: sessionId })
                });
                const data = await resp.json();
                if (resp.ok && data.status === 'success') {
                    // 如果删除的是当前会话，自动开一个新的
                    if (sessionId === currentSessionId) {
                        currentSessionId = generateSessionId();
                        sessionStorage.setItem('sessionId', currentSessionId);
                        updateSessionDisplay();
                        document.getElementById('chat-box').innerHTML = `
                            <div class="flex justify-start">
                                <div class="message-agent bg-white border p-4 max-w-[85%] shadow-sm text-gray-700">
                                    ${t('new_session_message')}
                                </div>
                            </div>`;
                    }
                    await loadSessionList();
                } else {
                    alert(t('delete_fail') + ': ' + (data.detail || data.error || ''));
                }
            } catch (e) {
                alert(t('delete_fail') + ': ' + e.message);
            }
        }

        async function deleteAllSessions() {
            if (!confirm(t('delete_all_confirm'))) return;
            try {
                const resp = await fetch('/proxy_delete_session', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ session_id: '' })
                });
                const data = await resp.json();
                if (resp.ok && data.status === 'success') {
                    currentSessionId = generateSessionId();
                    sessionStorage.setItem('sessionId', currentSessionId);
                    updateSessionDisplay();
                    document.getElementById('chat-box').innerHTML = `
                        <div class="flex justify-start">
                            <div class="message-agent bg-white border p-4 max-w-[85%] shadow-sm text-gray-700">
                                ${t('new_session_message')}
                            </div>
                        </div>`;
                    await loadSessionList();
                } else {
                    alert(t('delete_fail') + ': ' + (data.detail || data.error || ''));
                }
            } catch (e) {
                alert(t('delete_fail') + ': ' + e.message);
            }
        }

        async function switchToSession(sessionId, force = false) {
            if (!force && sessionId === currentSessionId) { closeSessionSidebar(); return; }
            hideNewMsgBanner();
            // 切换前先重置按钮到 idle 状态（避免旧 session 的 streaming/busy 状态残留）
            setStreamingUI(false);
            setSystemBusyUI(false);
            currentSessionId = sessionId;
            cancelTargetSessionId = null;  // 重置终止目标
            sessionStorage.setItem('sessionId', sessionId);
            updateSessionDisplay();
            closeSessionSidebar();

            // 加载该会话的历史消息
            const chatBox = document.getElementById('chat-box');
            chatBox.innerHTML = `<div class="text-xs text-gray-400 text-center py-4">${t('history_loading_msg')}</div>`;

            try {
                const resp = await fetch('/proxy_session_history', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ session_id: sessionId })
                });
                const data = await resp.json();
                chatBox.innerHTML = '';

                if (!data.messages || data.messages.length === 0) {
                    chatBox.innerHTML = `
                        <div class="flex justify-start">
                            <div class="message-agent bg-white border p-4 max-w-[85%] shadow-sm text-gray-700">
                                ${t('history_no_msg')}
                            </div>
                        </div>`;
                    return;
                }

                for (const msg of data.messages) {
                    if (msg.role === 'user') {
                        // 支持多模态历史消息（content 可能是 string 或 array）
                        let textContent = '';
                        let imagesHtml = '';
                        if (typeof msg.content === 'string') {
                            textContent = msg.content;
                        } else if (Array.isArray(msg.content)) {
                            for (const part of msg.content) {
                                if (part.type === 'text') textContent = part.text || '';
                                else if (part.type === 'image_url') {
                                    imagesHtml += `<img src="${part.image_url.url}" class="chat-inline-image">`;
                                }
                            }
                        }
                        chatBox.innerHTML += `
                            <div class="flex justify-end">
                                <div class="message-user bg-blue-600 text-white p-4 max-w-[85%] shadow-sm">
                                    ${imagesHtml}${imagesHtml ? '<div style="margin-top:6px">' : ''}${escapeHtml(textContent || '('+t('image_placeholder')+')')}${imagesHtml ? '</div>' : ''}
                                </div>
                            </div>`;
                    } else if (msg.role === 'tool') {
                        chatBox.innerHTML += `
                            <div class="flex justify-start">
                                <div class="bg-gray-100 border border-dashed border-gray-300 p-3 max-w-[85%] shadow-sm text-xs text-gray-500 rounded-lg">
                                    <div class="font-semibold text-gray-600 mb-1">🔧 ${t('tool_return')}: ${escapeHtml(msg.tool_name || '')}</div>
                                    <pre class="whitespace-pre-wrap break-words">${escapeHtml(msg.content.length > 500 ? msg.content.slice(0, 500) + '...' : msg.content)}</pre>
                                </div>
                            </div>`;
                    } else {
                        let toolCallsHtml = '';
                        if (msg.tool_calls && msg.tool_calls.length > 0) {
                            const callsList = msg.tool_calls.map(tc =>
                                `<span class="inline-block bg-blue-100 text-blue-700 text-xs px-2 py-0.5 rounded mr-1 mb-1">🔧 ${escapeHtml(tc.name)}</span>`
                            ).join('');
                            toolCallsHtml = `<div class="mb-2">${callsList}</div>`;
                        }
                        chatBox.innerHTML += `
                            <div class="flex justify-start">
                                <div class="message-agent bg-white border p-4 max-w-[85%] shadow-sm text-gray-700 markdown-body" data-tts-ready="1">
                                    ${toolCallsHtml}${msg.content ? marked.parse(msg.content) : '<span class="text-gray-400 text-xs">('+t('tool_calling')+')</span>'}
                                </div>
                            </div>`;
                    }
                }
                // 为历史 AI 消息添加朗读按钮
                chatBox.querySelectorAll('[data-tts-ready="1"]').forEach(div => {
                    div.removeAttribute('data-tts-ready');
                    const ttsBtn = createTtsButton(() => div.innerText || div.textContent || '');
                    div.appendChild(ttsBtn);
                });
                // 高亮代码块
                chatBox.querySelectorAll('pre code').forEach((block) => hljs.highlightElement(block));
                chatBox.scrollTop = chatBox.scrollHeight;
            } catch (e) {
                chatBox.innerHTML = `
                    <div class="text-xs text-red-400 text-center py-4">${t('history_error')}: ${e.message}</div>`;
            }

            // 切换 session 后立即检查一次 busy 状态
            try {
                const sr = await fetch('/proxy_session_status', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ session_id: sessionId })
                });
                const sd = await sr.json();
                if (sd.busy) {
                    setSystemBusyUI(true);
                } else {
                    setSystemBusyUI(false);
                }
            } catch(e) {}
        }

        // ===== 登录逻辑 =====
        async function handleLogin() {
            const nameInput = document.getElementById('username-input');
            const pwInput = document.getElementById('password-input');
            const errorDiv = document.getElementById('login-error');
            const loginBtn = document.getElementById('login-btn');
            const name = nameInput.value.trim();
            const password = pwInput.value;

            errorDiv.classList.add('hidden');

            if (!name) { nameInput.focus(); return; }
            if (!password) { pwInput.focus(); return; }

            if (!/^[a-zA-Z0-9_\\-\\u4e00-\\u9fa5]+$/.test(name)) {
                errorDiv.textContent = t('login_error_invalid');
                errorDiv.classList.remove('hidden');
                return;
            }

            loginBtn.disabled = true;
            loginBtn.textContent = t('login_verifying');

            try {
                const controller = new AbortController();
                const timeout = setTimeout(() => controller.abort(), 15000);
                const resp = await fetch("/proxy_login", {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: name, password: password }),
                    signal: controller.signal
                });
                clearTimeout(timeout);
                let data;
                try { data = await resp.json(); } catch (_) { data = { error: 'Invalid server response' }; }
                if (!resp.ok) {
                    errorDiv.textContent = data.detail || data.error || t('login_error_failed');
                    errorDiv.classList.remove('hidden');
                    return;
                }

                currentUserId = name;
                sessionStorage.setItem('userId', name);
                // 存储 OpenAI 格式的 Bearer token: user_id:password
                const authToken = name + ':' + password;
                sessionStorage.setItem('authToken', authToken);
                initSession();

                document.getElementById('uid-display').textContent = 'UID: ' + name;
                document.getElementById('login-screen').style.display = 'none';
                document.getElementById('chat-screen').style.display = 'flex';
                document.getElementById('user-input').focus();
                loadTools();
                refreshOasisTopics(); // Load OASIS topics after login
                startHistoryPolling();
            } catch (e) {
                if (e.name === 'AbortError') {
                    errorDiv.textContent = '连接超时，请确认后端服务已启动后重试';
                } else {
                    errorDiv.textContent = t('login_error_network') + ': ' + e.message;
                }
                errorDiv.classList.remove('hidden');
            } finally {
                loginBtn.disabled = false;
                loginBtn.textContent = t('login_btn');
            }
        }

        function handleLogout() {
            currentUserId = null;
            currentSessionId = null;
            stopHistoryPolling();
            sessionStorage.removeItem('userId');
            sessionStorage.removeItem('authToken');
            sessionStorage.removeItem('sessionId');
            fetch("/proxy_logout", { method: 'POST' });
            document.getElementById('chat-screen').style.display = 'none';
            document.getElementById('login-screen').style.display = 'flex';
            document.getElementById('username-input').value = '';
            document.getElementById('password-input').value = '';
            document.getElementById('login-error').classList.add('hidden');
            document.getElementById('username-input').focus();
            const chatBox = document.getElementById('chat-box');
            chatBox.innerHTML = `
                <div class="flex justify-start">
                    <div class="message-agent bg-white border p-4 max-w-[85%] shadow-sm text-gray-700">
                        ${t('welcome_message')}
                    </div>
                </div>`;
            // Stop OASIS polling
            stopOasisPolling();
        }

        // ===== Tool Panel 逻辑 =====
        let toolPanelOpen = false;
        let allTools = [];
        let enabledToolSet = new Set();

        function toggleToolPanel() {
            const panel = document.getElementById('tool-panel');
            const icon = document.getElementById('tool-toggle-icon');
            toolPanelOpen = !toolPanelOpen;
            if (toolPanelOpen) {
                panel.classList.remove('collapsed');
                panel.classList.add('expanded');
                icon.classList.add('open');
            } else {
                panel.classList.remove('expanded');
                panel.classList.add('collapsed');
                icon.classList.remove('open');
            }
        }

        function updateToolCount() {
            const toolCount = document.getElementById('tool-count');
            toolCount.textContent = '(' + enabledToolSet.size + '/' + allTools.length + ')';
        }

        function toggleTool(name, tagEl) {
            if (enabledToolSet.has(name)) {
                enabledToolSet.delete(name);
                tagEl.classList.remove('enabled');
                tagEl.classList.add('disabled');
            } else {
                enabledToolSet.add(name);
                tagEl.classList.remove('disabled');
                tagEl.classList.add('enabled');
            }
            updateToolCount();
        }

        function getEnabledTools() {
            if (enabledToolSet.size === allTools.length) return null;
            return Array.from(enabledToolSet);
        }

        async function loadTools() {
            try {
                const resp = await fetch('/proxy_tools');
                if (!resp.ok) return;
                const data = await resp.json();
                const tools = data.tools || [];
                const toolList = document.getElementById('tool-list');
                const wrapper = document.getElementById('tool-panel-wrapper');

                if (tools.length === 0) {
                    wrapper.style.display = 'none';
                    return;
                }

                allTools = tools;
                enabledToolSet = new Set(tools.map(t => t.name));
                toolList.innerHTML = '';
                tools.forEach(t => {
                    const tag = document.createElement('span');
                    tag.className = 'tool-tag enabled';
                    tag.title = t.description || '';
                    tag.textContent = t.name;
                    tag.onclick = () => toggleTool(t.name, tag);
                    toolList.appendChild(tag);
                });
                updateToolCount();
                wrapper.style.display = 'block';
            } catch (e) {
                console.warn('Failed to load tools:', e);
            }
        }

        // Session check
        (function checkSession() {
            // 初始化语言
            document.documentElement.lang = currentLang;
            applyTranslations();
            
            const saved = sessionStorage.getItem('userId');
            if (saved) {
                currentUserId = saved;
                initSession();
                document.getElementById('uid-display').textContent = 'UID: ' + saved;
                document.getElementById('login-screen').style.display = 'none';
                document.getElementById('chat-screen').style.display = 'flex';
                loadTools();
                refreshOasisTopics();
                startHistoryPolling();
            }
        })();

        // Login input handlers
        document.getElementById('username-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter') { e.preventDefault(); document.getElementById('password-input').focus(); }
        });
        document.getElementById('password-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter') { e.preventDefault(); handleLogin(); }
        });

        // ===== 聊天逻辑 =====
        const chatBox = document.getElementById('chat-box');
        const inputField = document.getElementById('user-input');
        const sendBtn = document.getElementById('send-btn');
        const cancelBtn = document.getElementById('cancel-btn');
        const busyBtn = document.getElementById('busy-btn');
        const refreshChatBtn = document.getElementById('refresh-chat-btn');
        let _hasUnreadSystemMsg = 0;  // 0=无未读, 1=有未读

        function showNewMsgBanner() {
            if (_hasUnreadSystemMsg) return;
            _hasUnreadSystemMsg = 1;
            refreshChatBtn.classList.add('has-new');
        }

        function hideNewMsgBanner() {
            _hasUnreadSystemMsg = 0;
            refreshChatBtn.classList.remove('has-new');
        }

        function handleNewMsgRefresh() {
            hideNewMsgBanner();
            switchToSession(currentSessionId, true);
        }

        // 按钮三态：idle(发送) / streaming(终止) / busy(系统占用中)
        function setStreamingUI(streaming) {
            if (streaming) {
                sendBtn.style.display = 'none';
                cancelBtn.style.display = 'inline-block';
                busyBtn.style.display = 'none';
                inputField.disabled = true;
                cancelTargetSessionId = currentSessionId;
            } else {
                sendBtn.style.display = 'inline-block';
                cancelBtn.style.display = 'none';
                busyBtn.style.display = 'none';
                sendBtn.disabled = false;
                inputField.disabled = false;
                cancelTargetSessionId = null;
            }
        }

        function setSystemBusyUI(busy) {
            if (busy) {
                sendBtn.style.display = 'none';
                cancelBtn.style.display = 'inline-block';
                busyBtn.style.display = 'none';
                inputField.disabled = true;
                cancelTargetSessionId = currentSessionId;
            } else {
                sendBtn.style.display = 'inline-block';
                cancelBtn.style.display = 'none';
                busyBtn.style.display = 'none';
                sendBtn.disabled = false;
                inputField.disabled = false;
                cancelTargetSessionId = null;
            }
        }

        async function handleCancel() {
            const targetSession = cancelTargetSessionId || currentSessionId;
            if (currentAbortController) {
                currentAbortController.abort();
                currentAbortController = null;
            }
            try {
                await fetch("/proxy_cancel", {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ session_id: targetSession })
                });
            } catch(e) { /* ignore */ }
            // 恢复 UI（无论是用户流式还是系统调用被终止）
            setStreamingUI(false);
            setSystemBusyUI(false);
        }

        // ===== TTS 朗读功能 =====
        let currentTtsAudio = null;
        let currentTtsBtn = null;

        function stripMarkdownForTTS(md) {
            // 移除代码块（含内容）
            let text = md.replace(/```[\\s\\S]*?```/g, '('+t('code_omitted')+')');
            // 移除行内代码
            text = text.replace(/`[^`]+`/g, '');
            // 移除图片
            text = text.replace(/!\\[.*?\\]\\(.*?\\)/g, '');
            // 移除链接，保留文字
            text = text.replace(/\\[([^\\]]+)\\]\\(.*?\\)/g, '$1');
            // 移除标题标记
            text = text.replace(/^#{1,6}\\s+/gm, '');
            // 移除粗体/斜体标记
            text = text.replace(/\\*{1,3}([^*]+)\\*{1,3}/g, '$1');
            // 移除工具调用提示行
            text = text.replace(/.*🔧.*调用工具.*\\n?/g, '');
            text = text.replace(/.*✅.*工具执行完成.*\\n?/g, '');
            // 清理多余空行
            text = text.replace(/\\n{3,}/g, '\\n\\n').trim();
            return text;
        }

        function stopTtsPlayback() {
            if (currentTtsAudio) {
                currentTtsAudio.pause();
                currentTtsAudio.src = '';
                currentTtsAudio = null;
            }
            if (currentTtsBtn) {
                currentTtsBtn.classList.remove('playing', 'loading');
                currentTtsBtn.querySelector('.tts-label').textContent = t('tts_read');
                currentTtsBtn = null;
            }
        }

        async function handleTTS(btn, text) {
            // 如果点击的是正在播放的按钮，则停止
            if (btn === currentTtsBtn && currentTtsAudio) {
                stopTtsPlayback();
                return;
            }
            // 停止上一个播放
            stopTtsPlayback();

            const cleanText = stripMarkdownForTTS(text);
            if (!cleanText) return;

            currentTtsBtn = btn;
            btn.classList.add('loading');
            btn.querySelector('.tts-label').textContent = t('tts_loading');

            try {
                const resp = await fetch('/proxy_tts', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: cleanText })
                });
                if (!resp.ok) throw new Error(t('tts_request_failed'));

                const blob = await resp.blob();
                const url = URL.createObjectURL(blob);
                const audio = new Audio(url);
                currentTtsAudio = audio;

                btn.classList.remove('loading');
                btn.classList.add('playing');
                btn.querySelector('.tts-label').textContent = t('tts_stop');

                audio.onended = () => {
                    URL.revokeObjectURL(url);
                    stopTtsPlayback();
                };
                audio.onerror = () => {
                    URL.revokeObjectURL(url);
                    stopTtsPlayback();
                };
                audio.play();
            } catch (e) {
                console.error('TTS error:', e);
                stopTtsPlayback();
            }
        }

        function createTtsButton(textRef) {
            const btn = document.createElement('div');
            btn.className = 'tts-btn';
            btn.innerHTML = `
                <span class="tts-spinner"></span>
                <svg class="tts-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                    <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                    <path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>
                </svg>
                <span class="tts-label">${t('tts_read')}</span>`;
            btn.onclick = () => handleTTS(btn, textRef());
            return btn;
        }

        function appendMessage(content, isUser = false, images = [], fileNames = [], audioNames = []) {
            const wrapper = document.createElement('div');
            wrapper.className = `flex ${isUser ? 'justify-end' : 'justify-start'} animate-in fade-in duration-300`;
            const div = document.createElement('div');
            div.className = `p-4 max-w-[85%] shadow-sm ${isUser ? 'bg-blue-600 text-white message-user' : 'bg-white border text-gray-800 message-agent'}`;
            if (isUser) {
                let extraHtml = '';
                if (images && images.length > 0) {
                    extraHtml += images.map(src => `<img src="${src}" class="chat-inline-image">`).join('');
                }
                if (fileNames && fileNames.length > 0) {
                    extraHtml += fileNames.map(n => `<div class="chat-file-tag">📄 ${escapeHtml(n)}</div>`).join('');
                }
                if (audioNames && audioNames.length > 0) {
                    extraHtml += audioNames.map(n => `<div class="chat-audio-tag">🎤 ${escapeHtml(n)}</div>`).join('');
                }
                if (extraHtml) {
                    div.innerHTML = extraHtml + '<div style="margin-top:6px">' + escapeHtml(content) + '</div>';
                } else {
                    div.innerText = content;
                }
            } else {
                div.className += " markdown-body";
                div.innerHTML = marked.parse(content);
                div.querySelectorAll('pre code').forEach((block) => hljs.highlightElement(block));
                // AI 消息添加朗读按钮（content 非空时）
                if (content) {
                    const ttsBtn = createTtsButton(() => div.innerText || div.textContent || '');
                    div.appendChild(ttsBtn);
                }
            }
            wrapper.appendChild(div);
            chatBox.appendChild(wrapper);
            chatBox.scrollTop = chatBox.scrollHeight;
            return div;
        }

        function showTyping() {
            const wrapper = document.createElement('div');
            wrapper.id = 'typing-indicator';
            wrapper.className = 'flex justify-start';
            wrapper.innerHTML = `
                <div class="message-agent bg-white border p-4 flex space-x-2 items-center shadow-sm">
                    <div class="dot"></div><div class="dot"></div><div class="dot"></div>
                </div>`;
            chatBox.appendChild(wrapper);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        async function handleSend() {
            const text = inputField.value.trim();
            if (!text && pendingImages.length === 0 && pendingFiles.length === 0 && pendingAudios.length === 0) return;
            if (sendBtn.disabled) return;

            // Stop recording if active
            if (isRecording) stopRecording();

            // Capture images, files, audios before clearing
            const imagesToSend = pendingImages.map(img => img.base64);
            const imagePreviewSrcs = [...imagesToSend];
            const filesToSend = pendingFiles.map(f => ({ name: f.name, content: f.content, type: f.type }));
            const fileNames = pendingFiles.map(f => f.name);
            const audiosToSend = pendingAudios.map(a => ({ base64: a.base64, name: a.name, format: a.format }));
            const audioNames = pendingAudios.map(a => a.name);

            const label = text || (imagePreviewSrcs.length ? '('+t('image_placeholder')+')' : audioNames.length ? '('+t('audio_placeholder')+')' : '('+t('file_placeholder')+')');
            appendMessage(label, true, imagePreviewSrcs, fileNames, audioNames);
            inputField.value = '';
            inputField.style.height = 'auto';
            pendingImages = [];
            pendingFiles = [];
            pendingAudios = [];
            renderImagePreviews();
            renderFilePreviews();
            renderAudioPreviews();
            sendBtn.disabled = true;
            showTyping();

            currentAbortController = new AbortController();
            setStreamingUI(true);

            let agentDiv = null;
            let fullText = '';

            try {
                // --- 构造 OpenAI 格式的 content parts ---
                const contentParts = [];
                if (text) {
                    contentParts.push({ type: 'text', text: text });
                }
                // 图片 → image_url
                for (const img of imagesToSend) {
                    contentParts.push({ type: 'image_url', image_url: { url: img } });
                }
                // 音频 → input_audio
                for (const audio of audiosToSend) {
                    contentParts.push({
                        type: 'input_audio',
                        input_audio: { data: audio.base64, format: audio.format || 'webm' }
                    });
                }
                // 文件 → file
                for (const f of filesToSend) {
                    const fileData = f.content.startsWith('data:') ? f.content : 'data:application/octet-stream;base64,' + f.content;
                    contentParts.push({
                        type: 'file',
                        file: { filename: f.name, file_data: fileData }
                    });
                }

                // 如果只有纯文本，content 用字符串；否则用 parts 数组
                let msgContent;
                if (contentParts.length === 1 && contentParts[0].type === 'text') {
                    msgContent = contentParts[0].text;
                } else if (contentParts.length > 0) {
                    msgContent = contentParts;
                } else {
                    msgContent = '(空消息)';
                }

                // --- 构造 OpenAI /v1/chat/completions 请求 ---
                const openaiPayload = {
                    model: 'mini-timebot',
                    messages: [{ role: 'user', content: msgContent }],
                    stream: true,
                    session_id: currentSessionId,
                    enabled_tools: getEnabledTools(),
                };

                const response = await fetch("/v1/chat/completions", {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + getAuthToken()
                    },
                    body: JSON.stringify(openaiPayload),
                    signal: currentAbortController.signal
                });

                const typingIndicator = document.getElementById('typing-indicator');
                if (typingIndicator) typingIndicator.remove();

                if (response.status === 401) {
                    appendMessage(t('login_expired'), false);
                    handleLogout();
                    return;
                }
                if (!response.ok) throw new Error("Agent error");

                agentDiv = appendMessage('', false);

                // --- 解析 OpenAI SSE 流式响应（支持分段渲染） ---
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';
                let allSegmentTexts = [];  // 记录所有段落的文本

                // 辅助函数：封存当前文本气泡，添加朗读按钮
                function sealCurrentBubble() {
                    if (fullText && agentDiv) {
                        agentDiv.innerHTML = marked.parse(fullText);
                        agentDiv.querySelectorAll('pre code').forEach(b => hljs.highlightElement(b));
                        const ttsBtn = createTtsButton(() => agentDiv.innerText || agentDiv.textContent || '');
                        agentDiv.appendChild(ttsBtn);
                        allSegmentTexts.push(fullText);
                    }
                }

                // 辅助函数：创建新的 AI 文本气泡
                function startNewBubble() {
                    fullText = '';
                    agentDiv = appendMessage('', false);
                }

                // 辅助函数：创建工具调用指示区
                function createToolIndicator(toolName, type) {
                    if (type === 'end') {
                        // 查找最后一个同名且仍在运行的 indicator 并更新
                        const allRunning = chatBox.querySelectorAll(`.stream-tool-indicator[data-tool-name="${CSS.escape(toolName)}"] .stream-tool-running`);
                        const last = allRunning.length ? allRunning[allRunning.length - 1] : null;
                        if (last) {
                            last.textContent = '✅';
                            last.classList.remove('stream-tool-running');
                            last.classList.add('stream-tool-done');
                        }
                        return;
                    }
                    const w = document.createElement('div');
                    w.className = 'flex justify-start animate-in fade-in duration-200';
                    const d = document.createElement('div');
                    d.className = 'stream-tool-indicator';
                    d.dataset.toolName = toolName;
                    d.innerHTML = `<span class="stream-tool-icon">🔧</span> <span class="stream-tool-name">${escapeHtml(toolName)}</span> <span class="stream-tool-status stream-tool-running">…</span>`;
                    w.appendChild(d);
                    chatBox.appendChild(w);
                    chatBox.scrollTop = chatBox.scrollHeight;
                }

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\\n');
                    buffer = lines.pop();

                    for (const line of lines) {
                        if (!line.startsWith('data: ')) continue;
                        const data = line.slice(6).trim();
                        if (data === '[DONE]') continue;

                        try {
                            const chunk = JSON.parse(data);
                            const delta = chunk.choices && chunk.choices[0] && chunk.choices[0].delta;
                            if (!delta) continue;

                            // --- 处理结构化 meta 事件 ---
                            if (delta.meta) {
                                const m = delta.meta;
                                if (m.type === 'tools_start') {
                                    // LLM 回复结束，即将调工具 → 封存当前气泡
                                    sealCurrentBubble();
                                } else if (m.type === 'tool_start') {
                                    createToolIndicator(m.name, 'start');
                                } else if (m.type === 'tool_end') {
                                    createToolIndicator(m.name, 'end');
                                } else if (m.type === 'tools_end') {
                                    // 所有工具执行完毕（可选：加分隔符）
                                } else if (m.type === 'ai_start') {
                                    // 新一轮 LLM 开始 → 创建新文本气泡
                                    startNewBubble();
                                }
                                continue;
                            }

                            // --- 处理文本内容 ---
                            if (delta.content) {
                                fullText += delta.content;
                                agentDiv.innerHTML = marked.parse(fullText);
                                agentDiv.querySelectorAll('pre code').forEach((block) => {
                                    if (!block.dataset.highlighted) {
                                        hljs.highlightElement(block);
                                        block.dataset.highlighted = 'true';
                                    }
                                });
                                chatBox.scrollTop = chatBox.scrollHeight;
                            }
                        } catch(e) {
                            // 跳过无法解析的 chunk
                        }
                    }
                }

                // 流式结束：封存最后一个气泡
                if (fullText) {
                    agentDiv.innerHTML = marked.parse(fullText);
                    agentDiv.querySelectorAll('pre code').forEach((block) => hljs.highlightElement(block));
                    const ttsBtn = createTtsButton(() => agentDiv.innerText || agentDiv.textContent || '');
                    agentDiv.appendChild(ttsBtn);
                    chatBox.scrollTop = chatBox.scrollHeight;
                }

                if (!fullText && allSegmentTexts.length === 0) {
                    agentDiv.innerHTML = `<span class="text-gray-400">${t('no_response')}</span>`;
                }

                // After agent response, refresh OASIS topics (in case a new discussion was started)
                setTimeout(() => refreshOasisTopics(), 1000);

            } catch (error) {
                const typingIndicator = document.getElementById('typing-indicator');
                if (typingIndicator) typingIndicator.remove();
                if (error.name === 'AbortError') {
                    if (agentDiv) {
                        fullText += '\\n\\n' + t('thinking_stopped');
                        agentDiv.innerHTML = marked.parse(fullText);
                    } else {
                        appendMessage(t('thinking_stopped'), false);
                    }
                } else {
                    appendMessage(t('agent_error') + ': ' + error.message, false);
                }
            } finally {
                currentAbortController = null;
                setStreamingUI(false);
                hideNewMsgBanner();
            }
        }

        inputField.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
        inputField.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
        });
        inputField.addEventListener('paste', handlePasteImage);

        // ================================================================
        // ===== OASIS 讨论面板逻辑 =====
        // ================================================================

        let oasisPanelOpen = false;
        let oasisCurrentTopicId = null;
        let oasisPollingTimer = null;
        let oasisStreamReader = null;

        // Expert avatar mapping
        const expertAvatars = {
            [t('oasis_expert_creative')]: { cls: 'expert-creative', icon: '💡' },
            [t('oasis_expert_critical')]: { cls: 'expert-critical', icon: '🔍' },
            [t('oasis_expert_data')]: { cls: 'expert-data', icon: '📊' },
            [t('oasis_expert_synthesis')]: { cls: 'expert-synthesis', icon: '🎯' },
        };

        function getExpertAvatar(name) {
            return expertAvatars[name] || { cls: 'expert-default', icon: '🤖' };
        }

        function getStatusBadge(status) {
            const map = {
                'pending': { cls: 'oasis-status-pending', text: t('oasis_status_pending') },
                'discussing': { cls: 'oasis-status-discussing', text: t('oasis_status_discussing') },
                'concluded': { cls: 'oasis-status-concluded', text: t('oasis_status_concluded') },
                'error': { cls: 'oasis-status-error', text: t('oasis_status_error') },
                'cancelled': { cls: 'oasis-status-error', text: t('oasis_status_cancelled') },
            };
            return map[status] || { cls: 'oasis-status-pending', text: status };
        }

        function formatTime(ts) {
            const d = new Date(ts * 1000);
            return d.toLocaleTimeString(currentLang === 'zh-CN' ? 'zh-CN' : 'en-US', { hour: '2-digit', minute: '2-digit' });
        }

        function toggleOasisPanel() {
            const panel = document.getElementById('oasis-panel');
            oasisPanelOpen = !oasisPanelOpen;
            if (oasisPanelOpen) {
                panel.classList.remove('collapsed-panel');
                panel.classList.remove('mobile-open');
                refreshOasisTopics();
            } else {
                panel.classList.add('collapsed-panel');
                panel.classList.remove('mobile-open');
                stopOasisPolling();
            }
        }

        function toggleOasisMobile() {
            const panel = document.getElementById('oasis-panel');
            if (panel.classList.contains('mobile-open')) {
                panel.classList.remove('mobile-open');
                stopOasisPolling();
            } else {
                panel.classList.remove('collapsed-panel');
                panel.classList.add('mobile-open');
                refreshOasisTopics();
            }
        }

        function toggleMobileMenu() {
            const dd = document.getElementById('mobile-menu-dropdown');
            if (dd.style.display === 'none') {
                dd.style.display = 'block';
                // close when tapping outside
                setTimeout(() => document.addEventListener('click', closeMobileMenuOutside, { once: true }), 0);
            } else {
                dd.style.display = 'none';
            }
        }
        function closeMobileMenu() {
            document.getElementById('mobile-menu-dropdown').style.display = 'none';
        }
        function closeMobileMenuOutside(e) {
            const wrapper = document.querySelector('.mobile-menu-wrapper');
            if (!wrapper.contains(e.target)) closeMobileMenu();
        }

        function stopOasisPolling() {
            if (oasisPollingTimer) {
                clearInterval(oasisPollingTimer);
                oasisPollingTimer = null;
            }
            if (oasisStreamReader) {
                oasisStreamReader.cancel();
                oasisStreamReader = null;
            }
        }

        async function refreshOasisTopics() {
            try {
                const resp = await fetch('/proxy_oasis/topics');
                console.log('[OASIS] Topics response status:', resp.status);
                if (!resp.ok) {
                    console.error('[OASIS] Failed to fetch topics:', resp.status);
                    return;
                }
                const topics = await resp.json();
                console.log('[OASIS] Topics data:', topics);
                renderTopicList(topics);
            } catch (e) {
                console.error('[OASIS] Failed to load topics:', e);
            }
        }

        function renderTopicList(topics) {
            const container = document.getElementById('oasis-topic-list');
            const countEl = document.getElementById('oasis-topic-count');
            countEl.textContent = topics.length + ' ' + t('oasis_topics_count');

            if (topics.length === 0) {
                container.innerHTML = `
                    <div class="p-6 text-center text-gray-400 text-sm">
                        <div class="text-3xl mb-2">🏛️</div>
                        <p>${t('oasis_no_topics')}</p>
                        <p class="text-xs mt-1">${t('oasis_start_hint')}</p>
                    </div>`;
                return;
            }

            // Sort: discussing first, then by created_at desc
            topics.sort((a, b) => {
                if (a.status === 'discussing' && b.status !== 'discussing') return -1;
                if (b.status === 'discussing' && a.status !== 'discussing') return 1;
                return (b.created_at || 0) - (a.created_at || 0);
            });

            container.innerHTML = topics.map(topic => {
                const badge = getStatusBadge(topic.status);
                const isActive = topic.topic_id === oasisCurrentTopicId;
                const isRunning = topic.status === 'discussing' || topic.status === 'pending';
                return `
                    <div class="oasis-topic-item p-3 border-b ${isActive ? 'active' : ''}" onclick="openOasisTopic('${topic.topic_id}')">
                        <div class="flex items-center justify-between mb-1">
                            <span class="oasis-status-badge ${badge.cls}">${badge.text}</span>
                            <div class="flex items-center space-x-1">
                                ${isRunning ? `<button onclick="event.stopPropagation(); cancelOasisTopic('${topic.topic_id}')" class="oasis-action-btn oasis-btn-cancel" title="${t('oasis_cancel')}">⏹</button>` : ''}
                                <button onclick="event.stopPropagation(); deleteOasisTopic('${topic.topic_id}')" class="oasis-action-btn oasis-btn-delete" title="${t('oasis_delete')}">🗑</button>
                                <span class="text-[10px] text-gray-400">${topic.created_at ? formatTime(topic.created_at) : ''}</span>
                            </div>
                        </div>
                        <p class="text-sm text-gray-800 font-medium line-clamp-2">${escapeHtml(topic.question)}</p>
                        <div class="flex items-center space-x-3 mt-1 text-[10px] text-gray-400">
                            <span>💬 ${topic.post_count || 0} ${t('oasis_posts')}</span>
                            <span>🔄 ${topic.current_round}/${topic.max_rounds} ${t('oasis_round')}</span>
                        </div>
                    </div>`;
            }).join('');
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        async function openOasisTopic(topicId) {
            oasisCurrentTopicId = topicId;
            stopOasisPolling();

            // Switch to detail view
            document.getElementById('oasis-topic-list-view').style.display = 'none';
            document.getElementById('oasis-detail-view').style.display = 'flex';

            // Load topic detail
            await loadTopicDetail(topicId);
        }

        function showOasisTopicList() {
            stopOasisPolling();
            oasisCurrentTopicId = null;
            document.getElementById('oasis-detail-view').style.display = 'none';
            document.getElementById('oasis-topic-list-view').style.display = 'flex';
            refreshOasisTopics();
        }

        async function loadTopicDetail(topicId) {
            try {
                const resp = await fetch(`/proxy_oasis/topics/${topicId}`);
                console.log('[OASIS] Detail response status:', resp.status);
                if (!resp.ok) {
                    console.error('[OASIS] Failed to fetch detail:', resp.status);
                    return;
                }
                const detail = await resp.json();
                console.log('[OASIS] Detail data:', detail);
                console.log('[OASIS] Posts count:', (detail.posts || []).length);
                renderTopicDetail(detail);

                // If still discussing, start polling for updates
                if (detail.status === 'discussing' || detail.status === 'pending') {
                    startDetailPolling(topicId);
                }
            } catch (e) {
                console.warn('Failed to load topic detail:', e);
            }
        }

        function renderTopicDetail(detail) {
            const badge = getStatusBadge(detail.status);
            document.getElementById('oasis-detail-status').className = 'oasis-status-badge ' + badge.cls;
            document.getElementById('oasis-detail-status').textContent = badge.text;
            const roundText = currentLang === 'zh-CN' ? `第 ${detail.current_round}/${detail.max_rounds} ${t('oasis_round')}` : `Round ${detail.current_round}/${detail.max_rounds}`;
            document.getElementById('oasis-detail-round').textContent = roundText;
            document.getElementById('oasis-detail-question').textContent = detail.question;

            // Render action buttons in detail header
            const actionsEl = document.getElementById('oasis-detail-actions');
            const isRunning = detail.status === 'discussing' || detail.status === 'pending';
            let btns = '';
            if (isRunning) {
                btns += `<button onclick="cancelOasisTopic('${detail.topic_id}')" class="oasis-detail-action-btn cancel">⏹ ${t('oasis_cancel')}</button>`;
            }
            btns += `<button onclick="deleteOasisTopic('${detail.topic_id}')" class="oasis-detail-action-btn delete">🗑 ${t('oasis_delete')}</button>`;
            actionsEl.innerHTML = btns;

            renderPosts(detail.posts || [], detail.timeline || [], detail.discussion !== false);

            // Show/hide conclusion (执行模式下不显示 conclusion)
            const conclusionArea = document.getElementById('oasis-conclusion-area');
            const isDiscussion = detail.discussion !== false;
            if (isDiscussion && detail.conclusion && detail.status === 'concluded') {
                document.getElementById('oasis-conclusion-text').textContent = detail.conclusion;
                conclusionArea.style.display = 'block';
            } else {
                conclusionArea.style.display = 'none';
            }
        }

        function fmtElapsed(sec) {
            if (sec === undefined || sec === null) return '';
            const s = Math.round(sec);
            if (s < 60) return 'T+' + s + 's';
            const m = Math.floor(s / 60);
            return 'T+' + m + 'm' + (s % 60) + 's';
        }

        function renderPosts(posts, timeline, isDiscussion) {
            const box = document.getElementById('oasis-posts-box');

            if (posts.length === 0 && (!timeline || timeline.length === 0)) {
                box.innerHTML = `
                    <div class="text-center text-gray-400 text-sm py-8">
                        <div class="text-2xl mb-2">💭</div>
                        <p>${t('oasis_waiting')}</p>
                    </div>`;
                return;
            }

            if (!isDiscussion) {
                // ── 执行模式：只展示 timeline 事件通知 ──
                if (!timeline || timeline.length === 0) {
                    box.innerHTML = `
                        <div class="text-center text-gray-400 text-sm py-8">
                            <div class="text-2xl mb-2">⏳</div>
                            <p>等待执行...</p>
                        </div>`;
                    return;
                }

                box.innerHTML = timeline.map(ev => {
                    const evIcons = {start:'🚀', round:'📢', agent_call:'⏳', agent_done:'✅', conclude:'🏁', manual_post:'📝'};
                    const icon = evIcons[ev.event] || '⏱';
                    let label = '';
                    if (ev.event === 'agent_call') {
                        label = ev.agent + ' 开始执行...';
                    } else if (ev.event === 'agent_done') {
                        label = ev.agent + ' 执行完成';
                    } else {
                        label = ev.agent ? ev.agent + (ev.detail ? ' · ' + ev.detail : '') : (ev.detail || ev.event);
                    }
                    return `
                        <div class="flex items-center space-x-2 py-1 px-2">
                            <span class="text-[10px] font-mono text-blue-500 whitespace-nowrap">${fmtElapsed(ev.elapsed)}</span>
                            <span class="text-xs text-gray-400">${icon} ${escapeHtml(label)}</span>
                        </div>`;
                }).join('');

                box.scrollTop = box.scrollHeight;
                return;
            }

            // ── 讨论模式：timeline 事件（绿色卡片）+ 帖子混排 ──
            const items = [];
            if (timeline) {
                for (const ev of timeline) {
                    // 讨论模式下不显示 agent_done
                    if (ev.event === 'agent_done') continue;
                    items.push({type: 'event', elapsed: ev.elapsed, data: ev});
                }
            }
            for (const p of posts) {
                items.push({type: 'post', elapsed: p.elapsed || 0, data: p});
            }
            items.sort((a, b) => a.elapsed - b.elapsed);

            box.innerHTML = items.map(item => {
                if (item.type === 'event') {
                    const ev = item.data;
                    const evIcons = {start:'🚀', round:'📢', agent_call:'⏳', conclude:'🏁', manual_post:'📝'};
                    const icon = evIcons[ev.event] || '⏱';
                    const label = ev.agent ? ev.agent + (ev.detail ? ' · ' + ev.detail : '') : (ev.detail || ev.event);
                    return `
                        <div class="oasis-post bg-green-50 rounded-xl p-3 border border-green-200 shadow-sm">
                            <div class="flex items-start space-x-2">
                                <div class="flex-1 min-w-0">
                                    <div class="flex items-center justify-between">
                                        <span class="text-xs font-semibold text-green-700">${icon} ${escapeHtml(label)}</span>
                                        <span class="text-[10px] font-mono text-green-500">${fmtElapsed(ev.elapsed)}</span>
                                    </div>
                                </div>
                            </div>
                        </div>`;
                }
                // Post
                const p = item.data;
                const avatar = getExpertAvatar(p.author);
                const isReply = p.reply_to !== null && p.reply_to !== undefined;
                const totalVotes = p.upvotes + p.downvotes;
                const upPct = totalVotes > 0 ? (p.upvotes / totalVotes * 100) : 50;

                return `
                    <div class="oasis-post bg-white rounded-xl p-3 border shadow-sm ${isReply ? 'ml-4 border-l-2 border-l-blue-300' : ''}">
                        <div class="flex items-start space-x-2">
                            <div class="oasis-expert-avatar ${avatar.cls}" title="${escapeHtml(p.author)}">${avatar.icon}</div>
                            <div class="flex-1 min-w-0">
                                <div class="flex items-center justify-between">
                                    <span class="text-xs font-semibold text-gray-700">${escapeHtml(p.author)}</span>
                                    <div class="flex items-center space-x-2 text-[10px] text-gray-400">
                                        <span class="font-mono text-blue-500">${fmtElapsed(p.elapsed)}</span>
                                        ${isReply ? '<span>↩️ #' + p.reply_to + '</span>' : ''}
                                        <span>#${p.id}</span>
                                    </div>
                                </div>
                                <p class="text-xs text-gray-600 mt-1 leading-relaxed">${escapeHtml(p.content)}</p>
                                <div class="flex items-center space-x-3 mt-2">
                                    <div class="flex items-center space-x-1">
                                        <span class="text-[10px]">👍 ${p.upvotes}</span>
                                        <span class="text-[10px]">👎 ${p.downvotes}</span>
                                    </div>
                                    ${totalVotes > 0 ? `
                                        <div class="flex-1 oasis-vote-bar flex">
                                            <div class="oasis-vote-up" style="width: ${upPct}%"></div>
                                            <div class="oasis-vote-down" style="width: ${100 - upPct}%"></div>
                                        </div>` : ''}
                                </div>
                            </div>
                        </div>
                    </div>`;
            }).join('');

            // Auto-scroll to bottom
            box.scrollTop = box.scrollHeight;
        }

        function startDetailPolling(topicId) {
            stopOasisPolling();
            let lastPostCount = 0;
            let lastTimelineCount = 0;
            let errorCount = 0;
            oasisPollingTimer = setInterval(async () => {
                if (oasisCurrentTopicId !== topicId) {
                    stopOasisPolling();
                    return;
                }
                try {
                    const resp = await fetch(`/proxy_oasis/topics/${topicId}`);
                    if (!resp.ok) {
                        errorCount++;
                        console.warn(`OASIS polling error: HTTP ${resp.status}`);
                        if (errorCount >= 5) {
                            console.error('OASIS polling failed 5 times, stopping');
                            stopOasisPolling();
                        }
                        return;
                    }
                    errorCount = 0;
                    const detail = await resp.json();
                    
                    // Re-render if posts or timeline changed
                    const currentPostCount = (detail.posts || []).length;
                    const currentTimelineCount = (detail.timeline || []).length;
                    if (currentPostCount !== lastPostCount || currentTimelineCount !== lastTimelineCount || detail.status !== 'discussing') {
                        renderTopicDetail(detail);
                        lastPostCount = currentPostCount;
                        lastTimelineCount = currentTimelineCount;
                    }

                    // Stop polling when discussion ends
                    if (detail.status === 'concluded' || detail.status === 'error') {
                        stopOasisPolling();
                        refreshOasisTopics();
                    }
                } catch (e) {
                    errorCount++;
                    console.warn('OASIS polling error:', e);
                }
            }, 1500); // Poll every 1.5 seconds for faster updates
        }

        async function cancelOasisTopic(topicId) {
            if (!confirm(t('oasis_cancel_confirm'))) return;
            try {
                const resp = await fetch(`/proxy_oasis/topics/${topicId}/cancel`, { method: 'POST' });
                const data = await resp.json();
                if (resp.ok) {
                    stopOasisPolling();
                    if (oasisCurrentTopicId === topicId) {
                        await loadTopicDetail(topicId);
                    }
                    refreshOasisTopics();
                } else {
                    alert(t('oasis_action_fail') + ': ' + (data.error || data.detail || data.message || ''));
                }
            } catch (e) {
                alert(t('oasis_action_fail') + ': ' + e.message);
            }
        }

        async function deleteOasisTopic(topicId) {
            if (!confirm(t('oasis_delete_confirm'))) return;
            try {
                const resp = await fetch(`/proxy_oasis/topics/${topicId}/purge`, { method: 'POST' });
                const data = await resp.json();
                if (resp.ok) {
                    stopOasisPolling();
                    if (oasisCurrentTopicId === topicId) {
                        showOasisTopicList();
                    } else {
                        refreshOasisTopics();
                    }
                } else {
                    alert(t('oasis_action_fail') + ': ' + (data.error || data.detail || data.message || ''));
                }
            } catch (e) {
                alert(t('oasis_action_fail') + ': ' + e.message);
            }
        }

        async function deleteAllOasisTopics() {
            const countEl = document.getElementById('oasis-topic-count');
            const count = parseInt(countEl.textContent) || 0;
            if (count === 0) {
                alert(t('oasis_no_topics') || '暂无讨论话题');
                return;
            }
            const confirmMsg = (currentLang === 'zh-CN')
                ? `确定要清空所有 ${count} 个讨论话题吗？此操作不可恢复！`
                : `Delete all ${count} topics? This cannot be undone!`;
            if (!confirm(confirmMsg)) return;

            try {
                const resp = await fetch('/proxy_oasis/topics', { method: 'DELETE' });
                const data = await resp.json();
                if (resp.ok) {
                    stopOasisPolling();
                    showOasisTopicList();
                    alert((currentLang === 'zh-CN' ? '已删除 ' : 'Deleted ') + data.deleted_count + (currentLang === 'zh-CN' ? ' 个话题' : ' topics'));
                } else {
                    alert(t('oasis_action_fail') + ': ' + (data.error || data.detail || data.message || ''));
                }
            } catch (e) {
                alert(t('oasis_action_fail') + ': ' + e.message);
            }
        }

        // Auto-refresh topic list periodically when panel is open
        setInterval(() => {
            if (oasisPanelOpen && !oasisCurrentTopicId && currentUserId) {
                refreshOasisTopics();
            }
        }, 10000); // Every 10 seconds

        // === System trigger polling: 检测后台系统触发产生的新消息 ===
        let _sessionStatusTimer = null;

        function startSessionStatusPolling() {
            stopSessionStatusPolling();
            _sessionStatusTimer = setInterval(async () => {
                if (!currentUserId || !currentSessionId) return;
                // 用户正在流式对话中，跳过轮询
                if (cancelBtn.style.display !== 'none') return;
                try {
                    const resp = await fetch('/proxy_session_status', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ session_id: currentSessionId })
                    });
                    const data = await resp.json();

                    // --- 系统占用状态 ---
                    if (data.busy) {
                        setSystemBusyUI(true);
                    } else if (busyBtn.style.display !== 'none') {
                        // busy → 不busy：恢复按钮，显示刷新横幅
                        setSystemBusyUI(false);
                        showNewMsgBanner();
                    }
                } catch(e) {
                    // 静默忽略
                }
            }, 5000); // 每 5 秒轮询一次
        }

        function stopSessionStatusPolling() {
            if (_sessionStatusTimer) {
                clearInterval(_sessionStatusTimer);
                _sessionStatusTimer = null;
            }
        }

        // 登录成功后启动轮询
        const _origLogin = typeof handleLogin === 'function' ? null : null;
        // 监听 chat-container 可见性来启动/停止轮询
        const _chatObserver = new MutationObserver(() => {
            const chatContainer = document.getElementById('chat-container');
            if (chatContainer && chatContainer.style.display !== 'none') {
                startSessionStatusPolling();
            } else {
                stopSessionStatusPolling();
            }
        });
        _chatObserver.observe(document.body, { childList: true, subtree: true, attributes: true });

        // ================================================================
        // ===== Group Chat (群聊) 逻辑 =====
        // ================================================================

        // Agent 颜色方案：根据名字 hash 分配一致的颜色
        const _agentColorPalette = [
            { bg: '#f0fdf4', border: '#bbf7d0', text: '#166534', sender: '#15803d', pre: '#1a2e1a', code: '#d1fae5' },
            { bg: '#eff6ff', border: '#bfdbfe', text: '#1e40af', sender: '#2563eb', pre: '#1e2a4a', code: '#dbeafe' },
            { bg: '#fdf4ff', border: '#e9d5ff', text: '#6b21a8', sender: '#7c3aed', pre: '#2d1a3e', code: '#ede9fe' },
            { bg: '#fff7ed', border: '#fed7aa', text: '#9a3412', sender: '#ea580c', pre: '#3b1a0a', code: '#ffedd5' },
            { bg: '#fef2f2', border: '#fecaca', text: '#991b1b', sender: '#dc2626', pre: '#3b1212', code: '#fee2e2' },
            { bg: '#f0fdfa', border: '#99f6e4', text: '#115e59', sender: '#0d9488', pre: '#0f2d2a', code: '#ccfbf1' },
            { bg: '#fefce8', border: '#fde68a', text: '#854d0e', sender: '#ca8a04', pre: '#2d2305', code: '#fef9c3' },
            { bg: '#fdf2f8', border: '#fbcfe8', text: '#9d174d', sender: '#db2777', pre: '#3b0d24', code: '#fce7f3' },
        ];
        const _agentColorCache = {};
        function getAgentColor(sender) {
            if (_agentColorCache[sender]) return _agentColorCache[sender];
            let hash = 0;
            for (let i = 0; i < sender.length; i++) {
                hash = ((hash << 5) - hash) + sender.charCodeAt(i);
                hash |= 0;
            }
            const color = _agentColorPalette[Math.abs(hash) % _agentColorPalette.length];
            _agentColorCache[sender] = color;
            return color;
        }
        function applyAgentColor(el, sender) {
            const c = getAgentColor(sender);
            const content = el.querySelector('.group-msg-content');
            const senderEl = el.querySelector('.group-msg-sender');
            if (content) {
                content.style.background = c.bg;
                content.style.borderColor = c.border;
                content.style.color = c.text;
            }
            if (senderEl) senderEl.style.color = c.sender;
            el.querySelectorAll('.group-msg-content pre').forEach(pre => { pre.style.background = c.pre; });
            el.querySelectorAll('.group-msg-content code').forEach(code => { code.style.color = c.code; });
        }

        let currentPage = 'chat'; // 'chat' or 'group'
        let currentGroupId = null;
        let groupPollingTimer = null;
        let groupLastMsgId = 0;
        let groupMuted = false;
        const groupSenderTitles = {};  // sender -> display title mapping

        function getGroupSenderTitle(sender) {
            let name = groupSenderTitles[sender] || sender;
            if (name.length > 7) name = name.slice(0, 7) + '…';
            return name;
        }

        // === @ Mention 功能 ===
        let mentionSelectedIds = [];  // 被 @ 选中的 agent session_id 列表
        let currentGroupMembers = []; // 当前群的 agent 成员缓存

        function onGroupInputChange(e) {
            const input = document.getElementById('group-input');
            const val = input.value;
            const cursorPos = input.selectionStart;
            // 检测光标前一个字符是否刚输入了 @
            if (cursorPos > 0 && val[cursorPos - 1] === '@') {
                showMentionPopup();
            }
        }

        function showMentionPopup() {
            const popup = document.getElementById('mention-popup');
            const listEl = document.getElementById('mention-list');
            // 从 groupSenderTitles 构建 agent 列表
            const agents = [];
            for (const [key, title] of Object.entries(groupSenderTitles)) {
                agents.push({ id: key, title: title });
            }
            if (agents.length === 0) {
                listEl.innerHTML = '<div style="padding:10px 14px;font-size:12px;color:#9ca3af;">群内暂无 Agent 成员</div>';
                popup.classList.add('show');
                return;
            }
            currentGroupMembers = agents;
            listEl.innerHTML = agents.map(a => {
                const sel = mentionSelectedIds.includes(a.id) ? ' selected' : '';
                const check = mentionSelectedIds.includes(a.id) ? '✓' : '';
                return `<div class="mention-item${sel}" data-id="${a.id}" onclick="toggleMentionItem(this, '${a.id}')">
                    <div class="mention-check">${check}</div>
                    <div class="mention-name" title="${a.title}">${a.title}</div>
                </div>`;
            }).join('');
            popup.classList.add('show');
        }

        function toggleMentionItem(el, agentId) {
            const idx = mentionSelectedIds.indexOf(agentId);
            if (idx >= 0) {
                mentionSelectedIds.splice(idx, 1);
                el.classList.remove('selected');
                el.querySelector('.mention-check').textContent = '';
            } else {
                mentionSelectedIds.push(agentId);
                el.classList.add('selected');
                el.querySelector('.mention-check').textContent = '✓';
            }
        }

        function confirmMention() {
            const popup = document.getElementById('mention-popup');
            popup.classList.remove('show');
            const input = document.getElementById('group-input');
            // 删掉输入框里刚输入的 @，替换为 @name 标签
            let val = input.value;
            // 找到最后一个 @ 的位置并替换
            const lastAt = val.lastIndexOf('@');
            if (lastAt >= 0) {
                const before = val.slice(0, lastAt);
                const after = val.slice(lastAt + 1);
                const tags = mentionSelectedIds.map(id => '@' + (groupSenderTitles[id] || id)).join(' ');
                input.value = before + tags + ' ' + after;
            }
            input.focus();
        }

        function hideMentionPopup() {
            document.getElementById('mention-popup').classList.remove('show');
        }

        // 点击输入区域外关闭弹层
        document.addEventListener('click', function(e) {
            const popup = document.getElementById('mention-popup');
            const inputArea = document.querySelector('.group-input-area');
            if (popup && inputArea && !inputArea.contains(e.target)) {
                popup.classList.remove('show');
            }
        });

        function switchPage(page) {
            currentPage = page;
            // Update tabs
            document.getElementById('tab-chat').classList.toggle('active', page === 'chat');
            document.getElementById('tab-group').classList.toggle('active', page === 'group');
            document.getElementById('tab-orchestrate').classList.toggle('active', page === 'orchestrate');
            // Show/hide pages
            const chatPage = document.getElementById('page-chat');
            const groupPage = document.getElementById('page-group');
            const orchPage = document.getElementById('page-orchestrate');
            if (page === 'chat') {
                chatPage.classList.remove('hidden-page');
                chatPage.style.display = 'flex';
                groupPage.classList.remove('active');
                groupPage.classList.remove('mobile-chat-open');
                if (orchPage) orchPage.classList.remove('active');
                stopGroupPolling();
                stopGroupListPolling();
            } else if (page === 'group') {
                chatPage.classList.add('hidden-page');
                chatPage.style.display = 'none';
                groupPage.classList.add('active');
                if (orchPage) orchPage.classList.remove('active');
                loadGroupList();
                startGroupListPolling();
                // 如果已有打开的群，恢复消息轮询
                if (currentGroupId) {
                    startGroupPolling(currentGroupId);
                }
            } else if (page === 'orchestrate') {
                chatPage.classList.add('hidden-page');
                chatPage.style.display = 'none';
                groupPage.classList.remove('active');
                groupPage.classList.remove('mobile-chat-open');
                if (orchPage) orchPage.classList.add('active');
                stopGroupPolling();
                stopGroupListPolling();
                if (!window._orchInitialized) { orchInit(); window._orchInitialized = true; }
            }
        }

        function stopGroupPolling() {
            if (groupPollingTimer) { clearInterval(groupPollingTimer); groupPollingTimer = null; }
        }

        let _groupListPollingTimer = null;
        function startGroupListPolling() {
            stopGroupListPolling();
            _groupListPollingTimer = setInterval(() => {
                if (currentPage === 'group' && currentUserId) {
                    loadGroupList();
                }
            }, 8000);
        }
        function stopGroupListPolling() {
            if (_groupListPollingTimer) { clearInterval(_groupListPollingTimer); _groupListPollingTimer = null; }
        }

        async function loadGroupList() {
            try {
                const resp = await fetch('/proxy_groups', {
                    headers: { 'Authorization': 'Bearer ' + getAuthToken() }
                });
                if (!resp.ok) return;
                const groups = await resp.json();
                renderGroupList(groups);
            } catch (e) {
                console.error('Failed to load groups:', e);
            }
        }

        function renderGroupList(groups) {
            const container = document.getElementById('group-list');
            if (!groups || groups.length === 0) {
                container.innerHTML = `
                    <div class="group-empty-state" style="padding:40px 0;">
                        <div class="empty-icon">👥</div>
                        <div class="empty-text">${t('group_no_groups')}</div>
                    </div>`;
                return;
            }
            container.innerHTML = groups.map(g => {
                const isActive = g.group_id === currentGroupId;
                return `
                    <div class="group-item ${isActive ? 'active' : ''}" onclick="openGroup('${g.group_id}')">
                        <div class="group-name">${escapeHtml(g.name)}</div>
                        <div class="group-meta">${g.member_count || 0} ${t('group_member_count')} · ${g.message_count || 0} ${t('group_msg_count')}</div>
                        <button class="group-delete-btn" onclick="event.stopPropagation(); deleteGroup('${g.group_id}')">${t('delete_session')}</button>
                    </div>`;
            }).join('');
        }

        async function openGroup(groupId) {
            currentGroupId = groupId;
            groupLastMsgId = 0;
            stopGroupPolling();

            // Mobile: switch to chat view
            document.getElementById('page-group').classList.add('mobile-chat-open');

            document.getElementById('group-empty-placeholder').style.display = 'none';
            const activeChat = document.getElementById('group-active-chat');
            activeChat.style.display = 'flex';

            // Load group detail
            try {
                const resp = await fetch(`/proxy_groups/${groupId}`, {
                    headers: { 'Authorization': 'Bearer ' + getAuthToken() }
                });
                if (!resp.ok) return;
                const detail = await resp.json();

                document.getElementById('group-active-name').textContent = detail.name;
                document.getElementById('group-active-id').textContent = '#' + groupId.slice(-8);

                // Build sender -> title mapping from members
                for (const key of Object.keys(groupSenderTitles)) delete groupSenderTitles[key];
                for (const m of (detail.members || [])) {
                    if (m.is_agent && m.title) {
                        const senderKey = m.user_id + '#' + m.session_id;
                        groupSenderTitles[senderKey] = m.title;
                    }
                }

                renderGroupMessages(detail.messages || []);
                renderGroupMembers(detail.members || []);

                // Track last message ID
                if (detail.messages && detail.messages.length > 0) {
                    groupLastMsgId = detail.messages[detail.messages.length - 1].id;
                }

                // Start polling for new messages
                startGroupPolling(groupId);

                // Load mute status
                await loadGroupMuteStatus(groupId);

                // Update group list selection
                loadGroupList();
            } catch (e) {
                console.error('Failed to open group:', e);
            }
        }

        function groupBackToList() {
            document.getElementById('page-group').classList.remove('mobile-chat-open');
            // Close member panel if open
            if (groupMemberPanelOpen) toggleGroupMemberPanel();
        }

        function renderGroupMessages(messages) {
            const box = document.getElementById('group-messages-box');
            if (messages.length === 0) {
                box.innerHTML = '<div style="text-align:center;color:#9ca3af;padding:40px 0;font-size:13px;">暂无消息</div>';
                return;
            }
            box.innerHTML = messages.map(m => {
                const isSelf = m.sender === currentUserId || m.sender === currentUserId;
                const isAgent = !isSelf && m.sender_session;
                const msgClass = isSelf ? 'self' : (isAgent ? 'agent' : 'other');
                const displayName = isAgent ? getGroupSenderTitle(m.sender) : m.sender;
                const timeStr = new Date(m.timestamp * 1000).toLocaleTimeString(currentLang === 'zh-CN' ? 'zh-CN' : 'en-US', {hour:'2-digit',minute:'2-digit'});
                return `
                    <div class="group-msg ${msgClass}" ${isAgent ? 'data-agent-sender="'+escapeHtml(m.sender)+'"' : ''}>
                        <div class="group-msg-sender">${escapeHtml(displayName)}</div>
                        <div class="group-msg-content markdown-body">${marked.parse(m.content || '')}</div>
                        <div class="group-msg-time">${timeStr}</div>
                    </div>`;
            }).join('');
            box.querySelectorAll('pre code').forEach((block) => hljs.highlightElement(block));
            box.querySelectorAll('.group-msg.agent[data-agent-sender]').forEach(el => applyAgentColor(el, el.dataset.agentSender));
            box.scrollTop = box.scrollHeight;
        }

        function appendGroupMessages(messages) {
            const box = document.getElementById('group-messages-box');
            // Remove "no messages" placeholder if present
            const placeholder = box.querySelector('div[style*="text-align:center"]');
            if (placeholder && messages.length > 0) placeholder.remove();

            for (const m of messages) {
                const isSelf = m.sender === currentUserId || m.sender === currentUserId;
                const isAgent = !isSelf && m.sender_session;
                const msgClass = isSelf ? 'self' : (isAgent ? 'agent' : 'other');
                const displayName = isAgent ? getGroupSenderTitle(m.sender) : m.sender;
                const timeStr = new Date(m.timestamp * 1000).toLocaleTimeString(currentLang === 'zh-CN' ? 'zh-CN' : 'en-US', {hour:'2-digit',minute:'2-digit'});
                const div = document.createElement('div');
                div.className = `group-msg ${msgClass}`;
                div.innerHTML = `
                    <div class="group-msg-sender">${escapeHtml(displayName)}</div>
                    <div class="group-msg-content markdown-body">${marked.parse(m.content || '')}</div>
                    <div class="group-msg-time">${timeStr}</div>`;
                div.querySelectorAll('pre code').forEach((block) => hljs.highlightElement(block));
                if (isAgent) applyAgentColor(div, m.sender);
                box.appendChild(div);
                if (m.id > groupLastMsgId) groupLastMsgId = m.id;
            }
            box.scrollTop = box.scrollHeight;
        }

        function startGroupPolling(groupId) {
            stopGroupPolling();
            groupPollingTimer = setInterval(async () => {
                if (currentGroupId !== groupId || currentPage !== 'group') {
                    stopGroupPolling();
                    return;
                }
                try {
                    const resp = await fetch(`/proxy_groups/${groupId}/messages?after_id=${groupLastMsgId}`, {
                        headers: { 'Authorization': 'Bearer ' + getAuthToken() }
                    });
                    if (!resp.ok) return;
                    const data = await resp.json();
                    if (data.messages && data.messages.length > 0) {
                        appendGroupMessages(data.messages);
                        // 有新消息时也刷新群列表（更新消息计数）
                        loadGroupList();
                    }
                } catch (e) {
                    // silent
                }
            }, 5000);
        }

        async function sendGroupMessage() {
            const input = document.getElementById('group-input');
            const text = input.value.trim();
            if (!text || !currentGroupId) return;

            // 收集 mentions：从 mentionSelectedIds 中取出被 @ 的 agent
            const mentions = mentionSelectedIds.length > 0 ? [...mentionSelectedIds] : null;
            // 发送后清空 mention 选中状态
            mentionSelectedIds = [];
            hideMentionPopup();
            input.value = '';

            try {
                const body = { content: text };
                if (mentions) body.mentions = mentions;
                const resp = await fetch(`/proxy_groups/${currentGroupId}/messages`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + getAuthToken()
                    },
                    body: JSON.stringify(body)
                });
                const result = await resp.json();
                const realId = result.id || (groupLastMsgId + 1);
                // Immediately show in UI with real server ID
                appendGroupMessages([{
                    id: realId,
                    sender: currentUserId,
                    content: text,
                    timestamp: Date.now() / 1000
                }]);
            } catch (e) {
                console.error('Failed to send group message:', e);
            }
        }

        function renderGroupMembers(members) {
            const container = document.getElementById('group-current-members');
            container.innerHTML = members.map(m => {
                const badge = m.is_agent
                    ? `<span class="member-badge badge-agent">${t('group_agent')}</span>`
                    : `<span class="member-badge badge-owner">${t('group_owner')}</span>`;
                let displayName = m.is_agent && m.title ? m.title : (m.user_id + (m.session_id !== 'default' ? '#' + m.session_id : ''));
                if (displayName.length > 7) displayName = displayName.slice(0, 7) + '…';
                return `
                    <div class="member-item">
                        <span class="member-name" title="${escapeHtml(m.user_id + '#' + m.session_id)}">${escapeHtml(displayName)}</span>
                        ${badge}
                    </div>`;
            }).join('');
        }

        let groupMemberPanelOpen = false;
        function toggleGroupMemberPanel() {
            groupMemberPanelOpen = !groupMemberPanelOpen;
            document.getElementById('group-member-panel').style.display = groupMemberPanelOpen ? 'flex' : 'none';
            if (groupMemberPanelOpen && currentGroupId) {
                loadAvailableSessions();
            }
        }

        async function loadAvailableSessions() {
            const container = document.getElementById('group-available-sessions');
            container.innerHTML = '<div class="text-xs text-gray-400 p-2">' + t('loading') + '</div>';
            try {
                const resp = await fetch(`/proxy_groups/${currentGroupId}/sessions`, {
                    headers: { 'Authorization': 'Bearer ' + getAuthToken() }
                });
                if (!resp.ok) return;
                const data = await resp.json();
                const sessions = data.sessions || [];

                // Get current members to mark them
                const detailResp = await fetch(`/proxy_groups/${currentGroupId}`, {
                    headers: { 'Authorization': 'Bearer ' + getAuthToken() }
                });
                const detail = await detailResp.json();
                const memberSet = new Set((detail.members || []).map(m => m.user_id + '#' + m.session_id));

                if (sessions.length === 0) {
                    container.innerHTML = '<div class="text-xs text-gray-400 p-2">' + t('group_no_sessions') + '</div>';
                    return;
                }

                container.innerHTML = sessions.map(s => {
                    const key = currentUserId + '#' + s.session_id;
                    const checked = memberSet.has(key) ? 'checked' : '';
                    const title = s.title || s.session_id;
                    return `
                        <label class="session-checkbox">
                            <input type="checkbox" ${checked} onchange="toggleGroupAgent('${s.session_id}', this.checked)">
                            <span class="session-label" title="${escapeHtml(title)}">${escapeHtml(title)}</span>
                        </label>`;
                }).join('');
            } catch (e) {
                container.innerHTML = '<div class="text-xs text-red-400 p-2">加载失败</div>';
            }
        }

        async function toggleGroupAgent(sessionId, add) {
            if (!currentGroupId) return;
            try {
                await fetch(`/proxy_groups/${currentGroupId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + getAuthToken()
                    },
                    body: JSON.stringify({
                        members: [{
                            user_id: currentUserId,
                            session_id: sessionId,
                            action: add ? 'add' : 'remove'
                        }]
                    })
                });
                // Refresh member list
                const resp = await fetch(`/proxy_groups/${currentGroupId}`, {
                    headers: { 'Authorization': 'Bearer ' + getAuthToken() }
                });
                const detail = await resp.json();
                renderGroupMembers(detail.members || []);
            } catch (e) {
                console.error('Failed to toggle group agent:', e);
            }
        }

        function showCreateGroupModal() {
            // 用自定义弹窗替代 prompt()，兼容移动端
            let overlay = document.getElementById('group-create-overlay');
            if (!overlay) {
                overlay = document.createElement('div');
                overlay.id = 'group-create-overlay';
                overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.4);z-index:300;display:flex;align-items:center;justify-content:center;';
                overlay.innerHTML = `
                    <div style="background:white;border-radius:12px;padding:20px;width:90%;max-width:320px;box-shadow:0 10px 40px rgba(0,0,0,0.2);">
                        <div style="font-size:14px;font-weight:600;color:#374151;margin-bottom:12px;" data-i18n="group_create_title">${t('group_create_title')}</div>
                        <input id="group-create-name-input" type="text" placeholder="${t('group_name_placeholder')}" data-i18n-placeholder="group_name_placeholder"
                            style="width:100%;box-sizing:border-box;padding:8px 12px;border:1px solid #d1d5db;border-radius:8px;font-size:14px;outline:none;" />
                        <div style="display:flex;gap:8px;margin-top:14px;justify-content:flex-end;">
                            <button onclick="closeCreateGroupModal()" style="padding:6px 16px;border-radius:8px;border:1px solid #d1d5db;background:white;font-size:13px;cursor:pointer;color:#6b7280;">取消</button>
                            <button onclick="submitCreateGroup()" style="padding:6px 16px;border-radius:8px;border:none;background:#2563eb;color:white;font-size:13px;font-weight:600;cursor:pointer;">${t('group_create_btn')}</button>
                        </div>
                    </div>`;
                document.body.appendChild(overlay);
                // Enter to submit
                document.getElementById('group-create-name-input').addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') { e.preventDefault(); submitCreateGroup(); }
                });
            } else {
                overlay.style.display = 'flex';
            }
            const input = document.getElementById('group-create-name-input');
            input.value = '';
            setTimeout(() => input.focus(), 100);
        }

        function closeCreateGroupModal() {
            const overlay = document.getElementById('group-create-overlay');
            if (overlay) overlay.style.display = 'none';
        }

        function submitCreateGroup() {
            const input = document.getElementById('group-create-name-input');
            const name = (input.value || '').trim();
            if (!name) return;
            closeCreateGroupModal();
            createGroup(name);
        }

        async function createGroup(name) {
            try {
                const resp = await fetch('/proxy_groups', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + getAuthToken()
                    },
                    body: JSON.stringify({ name: name, members: [] })
                });
                if (!resp.ok) { alert('创建失败'); return; }
                const data = await resp.json();
                await loadGroupList();
                openGroup(data.group_id);
            } catch (e) {
                alert('创建失败: ' + e.message);
            }
        }

        async function deleteGroup(groupId) {
            if (!confirm(t('group_delete_confirm'))) return;
            try {
                await fetch(`/proxy_groups/${groupId}`, {
                    method: 'DELETE',
                    headers: { 'Authorization': 'Bearer ' + getAuthToken() }
                });
                if (currentGroupId === groupId) {
                    currentGroupId = null;
                    document.getElementById('group-active-chat').style.display = 'none';
                    document.getElementById('group-empty-placeholder').style.display = 'flex';
                    document.getElementById('page-group').classList.remove('mobile-chat-open');
                    stopGroupPolling();
                }
                loadGroupList();
            } catch (e) {
                alert('删除失败: ' + e.message);
            }
        }

        function updateMuteButton() {
            const btn = document.getElementById('group-mute-btn');
            if (!btn) return;
            if (groupMuted) {
                btn.textContent = t('group_unmute');
                btn.style.background = '#f0fdf4';
                btn.style.color = '#16a34a';
                btn.style.borderColor = '#bbf7d0';
            } else {
                btn.textContent = t('group_mute');
                btn.style.background = '#fef2f2';
                btn.style.color = '#dc2626';
                btn.style.borderColor = '#fecaca';
            }
        }

        async function loadGroupMuteStatus(groupId) {
            try {
                const resp = await fetch(`/proxy_groups/${groupId}/mute_status`, {
                    headers: { 'Authorization': 'Bearer ' + getAuthToken() }
                });
                if (resp.ok) {
                    const data = await resp.json();
                    groupMuted = data.muted;
                    updateMuteButton();
                }
            } catch (e) { console.error('Failed to load mute status:', e); }
        }

        async function toggleGroupMute() {
            if (!currentGroupId) return;
            const action = groupMuted ? 'unmute' : 'mute';
            try {
                const resp = await fetch(`/proxy_groups/${currentGroupId}/${action}`, {
                    method: 'POST',
                    headers: { 'Authorization': 'Bearer ' + getAuthToken() }
                });
                if (resp.ok) {
                    groupMuted = !groupMuted;
                    updateMuteButton();
                }
            } catch (e) { console.error('Failed to toggle mute:', e); }
        }
    </script>

    <script>
    // === Native App Enhancements ===

    // 1. Splash screen dismiss
    window.addEventListener('load', () => {
        setTimeout(() => {
            const splash = document.getElementById('app-splash');
            if (splash) {
                splash.classList.add('fade-out');
                setTimeout(() => splash.remove(), 600);
            }
        }, 800);
    });

    // 2. Prevent pull-to-refresh and overscroll bounce
    document.addEventListener('touchmove', function(e) {
        // Allow scrolling inside scrollable containers
        let el = e.target;
        while (el && el !== document.body) {
            const style = window.getComputedStyle(el);
            if ((style.overflowY === 'auto' || style.overflowY === 'scroll') && el.scrollHeight > el.clientHeight) {
                return; // Allow scroll inside this element
            }
            el = el.parentElement;
        }
        e.preventDefault();
    }, { passive: false });

    // 3. Prevent double-tap zoom
    let lastTouchEnd = 0;
    document.addEventListener('touchend', function(e) {
        const now = Date.now();
        if (now - lastTouchEnd <= 300) {
            e.preventDefault();
        }
        lastTouchEnd = now;
    }, false);

    // 4. Prevent pinch zoom
    document.addEventListener('gesturestart', function(e) {
        e.preventDefault();
    });
    document.addEventListener('gesturechange', function(e) {
        e.preventDefault();
    });

    // 5. Prevent context menu on long press - mobile only (except in chat messages)
    const isTouchDevice = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);
    if (isTouchDevice) {
        document.addEventListener('contextmenu', function(e) {
            const allowed = e.target.closest('.message-agent, .message-user, .markdown-body, textarea, input');
            if (!allowed) {
                e.preventDefault();
            }
        });
    }

    // 6. Online/Offline detection
    function updateOnlineStatus() {
        const banner = document.getElementById('offline-banner');
        if (navigator.onLine) {
            banner.classList.remove('show');
        } else {
            banner.classList.add('show');
        }
    }
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);

    // 7. Register Service Worker for PWA caching
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js').catch(() => {});
    }

    // 8. iOS standalone: handle navigation to stay in-app
    if (window.navigator.standalone) {
        document.addEventListener('click', function(e) {
            const a = e.target.closest('a');
            if (a && a.href && !a.target && a.hostname === location.hostname) {
                e.preventDefault();
                location.href = a.href;
            }
        });
    }

    // 9. Keyboard handling for mobile/PWA - comprehensive solution
    if (isTouchDevice && window.visualViewport) {
        const chatMain = document.querySelector('.chat-main');
        const chatContainer = document.querySelector('.chat-container');
        const header = document.querySelector('header');
        const inputArea = document.querySelector('.border-t.p-2');
        
        // PWA Standalone mode detection
        const isPWA = window.matchMedia('(display-mode: standalone)').matches || 
                      window.navigator.standalone === true;
        
        let lastHeight = window.visualViewport.height;
        
        function handleViewportChange() {
            const vh = window.visualViewport.height;
            const windowHeight = window.innerHeight;
            const keyboardHeight = windowHeight - vh;
            
            // Detect if keyboard is open (more than 100px difference)
            const keyboardOpen = keyboardHeight > 100;
            
            if (isPWA || keyboardOpen) {
                // PWA mode or keyboard open: adjust heights
                const availableHeight = vh;
                
                // Update CSS variable for app height
                document.documentElement.style.setProperty('--app-height', availableHeight + 'px');
                
                // Chat main takes full available height
                if (chatMain) {
                    chatMain.style.height = availableHeight + 'px';
                    chatMain.style.maxHeight = availableHeight + 'px';
                }
                
                // Ensure flex behavior
                if (header) header.style.flexShrink = '0';
                if (inputArea) inputArea.style.flexShrink = '0';
                
                // Chat container gets remaining space via flex
                if (chatContainer) {
                    chatContainer.style.flex = '1';
                    chatContainer.style.minHeight = '0';
                }
            } else {
                // Normal mode: reset to CSS defaults
                document.documentElement.style.removeProperty('--app-height');
                
                if (chatMain) {
                    chatMain.style.height = '';
                    chatMain.style.maxHeight = '';
                }
                
                if (header) header.style.flexShrink = '';
                if (inputArea) inputArea.style.flexShrink = '';
                
                if (chatContainer) {
                    chatContainer.style.flex = '';
                    chatContainer.style.minHeight = '';
                }
            }
            
            lastHeight = vh;
        }
        
        // Debounced resize handler
        let resizeTimeout;
        function debouncedHandleViewportChange() {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(handleViewportChange, 50);
        }
        
        // Initial call
        handleViewportChange();
        
        // Listen for viewport changes
        window.visualViewport.addEventListener('resize', debouncedHandleViewportChange);
        window.visualViewport.addEventListener('scroll', handleViewportChange);
        
        // Also listen for window resize (orientation change)
        window.addEventListener('resize', debouncedHandleViewportChange);
        window.addEventListener('orientationchange', () => {
            setTimeout(handleViewportChange, 100);
        });
    }
    
    // Input focus: scroll into view on mobile
    const inputEl = document.getElementById('user-input');
    if (inputEl && isTouchDevice) {
        inputEl.addEventListener('focus', () => {
            setTimeout(() => {
                // Scroll input into view
                inputEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                // Also trigger viewport check
                if (window.visualViewport) {
                    window.dispatchEvent(new Event('resize'));
                }
            }, 100);
        });
        
        // On blur: reset after keyboard closes
        inputEl.addEventListener('blur', () => {
            setTimeout(() => {
                if (window.visualViewport) {
                    window.dispatchEvent(new Event('resize'));
                }
            }, 200);
        });
    }
    </script>

    <!-- ===== Orchestration Page JavaScript ===== -->
    <script>
    // ── Orchestration State ──
    const orch = {
        experts: [],
        nodes: [],
        edges: [],
        groups: [],
        selectedNodes: new Set(),
        nid: 1, eid: 1, gid: 1,
        dragging: null,
        connecting: null,
        selecting: null,
        contextMenu: null,
        sessionStatuses: {},
        // Zoom & pan state
        zoom: 1,
        panX: 0,
        panY: 0,
    };

    // ── Zoom / Pan helpers ──
    function orchApplyTransform() {
        const inner = document.getElementById('orch-canvas-inner');
        if (inner) inner.style.transform = `translate(${orch.panX}px, ${orch.panY}px) scale(${orch.zoom})`;
        document.getElementById('orch-zoom-label').textContent = Math.round(orch.zoom * 100) + '%';
    }
    function orchZoom(delta) {
        orch.zoom = Math.min(3, Math.max(0.15, orch.zoom + delta));
        orchApplyTransform();
    }
    function orchPanBy(dx, dy) {
        orch.panX += dx; orch.panY += dy;
        orchApplyTransform();
    }
    function orchResetView() {
        orch.zoom = 1; orch.panX = 0; orch.panY = 0;
        orchApplyTransform();
    }
    /** Convert page-level clientX/Y to canvas-inner coordinates (accounting for zoom+pan) */
    function orchClientToCanvas(clientX, clientY) {
        const area = document.getElementById('orch-canvas-area');
        const rect = area.getBoundingClientRect();
        return {
            x: (clientX - rect.left - orch.panX) / orch.zoom,
            y: (clientY - rect.top  - orch.panY) / orch.zoom,
        };
    }

    function orchInit() {
        orchLoadExperts();
        orchLoadSessionAgents();
        orchSetupCanvas();
        orchSetupSettings();
        // Bind manual injection card events (dragstart + dblclick)
        const mc = document.getElementById('orch-manual-card');
        if (mc) {
            mc.addEventListener('dragstart', e => {
                e.dataTransfer.setData('application/json', JSON.stringify({type:'manual', name:'手动注入', tag:'manual', emoji:'📝', temperature:0}));
                e.dataTransfer.effectAllowed = 'copy';
            });
            mc.addEventListener('dblclick', () => orchAddNodeCenter({type:'manual', name:'手动注入', tag:'manual', emoji:'📝', temperature:0}));
        }
    }

    // ── Load experts (public + custom) ──
    async function orchLoadExperts() {
        try {
            const r = await fetch('/proxy_visual/experts');
            orch.experts = await r.json();
        } catch(e) { console.error('Load experts failed:', e); }
        orchRenderExpertSidebar();
    }

    function orchRenderExpertSidebar() {
        const pubList = document.getElementById('orch-expert-list-public');
        const custList = document.getElementById('orch-expert-list-custom');
        pubList.innerHTML = '';
        custList.innerHTML = '';

        orch.experts.forEach(exp => {
            const card = document.createElement('div');
            card.className = 'orch-expert-card';
            card.draggable = true;
            const isCustom = exp.source === 'custom';
            card.innerHTML = `<span class="orch-emoji">${exp.emoji}</span><div style="min-width:0;flex:1;"><div class="orch-name">${escapeHtml(exp.name)}</div><div class="orch-tag">${escapeHtml(exp.tag)}</div></div><span class="orch-temp">${exp.temperature||''}</span>${isCustom ? '<button class="orch-expert-del-btn" title="删除" style="font-size:10px;background:none;border:none;cursor:pointer;color:#dc2626;padding:0 2px;margin-left:2px;">✕</button>' : ''}`;
            card.addEventListener('dragstart', e => {
                e.dataTransfer.setData('application/json', JSON.stringify({type:'expert', ...exp}));
                e.dataTransfer.effectAllowed = 'copy';
            });
            card.addEventListener('dblclick', () => orchAddNodeCenter({type:'expert', ...exp}));
            if (isCustom) {
                card.querySelector('.orch-expert-del-btn').addEventListener('click', async (ev) => {
                    ev.stopPropagation();
                    if (!confirm('删除自定义专家 "' + exp.name + '"？')) return;
                    try {
                        await fetch('/proxy_visual/experts/custom/' + encodeURIComponent(exp.tag), { method: 'DELETE' });
                        orchToast('已删除: ' + exp.name);
                        orchLoadExperts();
                    } catch(e) { orchToast('删除失败'); }
                });
                custList.appendChild(card);
            } else {
                pubList.appendChild(card);
            }
        });

        if (!custList.children.length) {
            custList.innerHTML = '<div style="padding:6px 10px;font-size:10px;color:#d1d5db;text-align:center;">暂无自定义专家</div>';
        }
    }

    // ── Load session agents ──
    async function orchLoadSessionAgents() {
        const list = document.getElementById('orch-expert-list-sessions');
        list.innerHTML = '<div style="padding:6px 10px;font-size:10px;color:#9ca3af;text-align:center;">⏳ 加载中...</div>';
        try {
            const resp = await fetch('/proxy_sessions');
            const data = await resp.json();
            list.innerHTML = '';
            if (!data.sessions || data.sessions.length === 0) {
                list.innerHTML = '<div style="padding:6px 10px;font-size:10px;color:#d1d5db;text-align:center;">暂无 Session</div>';
                return;
            }
            data.sessions.sort((a, b) => b.session_id.localeCompare(a.session_id));
            for (const s of data.sessions) {
                const card = document.createElement('div');
                card.className = 'orch-expert-card';
                card.draggable = true;
                const title = s.title || 'Untitled';
                card.innerHTML = `<span class="orch-emoji">🤖</span><div style="min-width:0;flex:1;"><div class="orch-name">${escapeHtml(title)}</div><div class="orch-tag" style="color:#6366f1;font-family:monospace;">#${s.session_id.slice(-8)}</div></div><span class="orch-temp" style="font-size:9px;color:#9ca3af;">${s.message_count||0}msg</span>`;
                const sessionData = {type:'session_agent', name: title, tag: 'session', emoji:'🤖', temperature: 0.7, session_id: s.session_id};
                card.addEventListener('dragstart', e => {
                    e.dataTransfer.setData('application/json', JSON.stringify(sessionData));
                    e.dataTransfer.effectAllowed = 'copy';
                });
                card.addEventListener('dblclick', () => orchAddNodeCenter(sessionData));
                list.appendChild(card);
            }
        } catch(e) {
            list.innerHTML = '<div style="padding:6px 10px;font-size:10px;color:#dc2626;text-align:center;">❌ 加载失败</div>';
        }
    }

    // ── Add custom expert modal ──
    function orchShowAddExpertModal() {
        const overlay = document.createElement('div');
        overlay.className = 'orch-modal-overlay';
        overlay.id = 'orch-add-expert-overlay';
        overlay.innerHTML = `
            <div class="orch-modal" style="min-width:380px;max-width:460px;">
                <h3>🛠️ 添加自定义专家</h3>
                <div style="display:flex;flex-direction:column;gap:8px;margin:10px 0;">
                    <label style="font-size:11px;font-weight:600;color:#374151;">名称 <input id="orch-ce-name" type="text" placeholder="如：金融分析师" style="width:100%;padding:6px 8px;border:1px solid #d1d5db;border-radius:6px;font-size:12px;margin-top:2px;"></label>
                    <label style="font-size:11px;font-weight:600;color:#374151;">Tag (英文) <input id="orch-ce-tag" type="text" placeholder="如：finance" style="width:100%;padding:6px 8px;border:1px solid #d1d5db;border-radius:6px;font-size:12px;margin-top:2px;"></label>
                    <label style="font-size:11px;font-weight:600;color:#374151;">Temperature <input id="orch-ce-temp" type="number" value="0.7" min="0" max="2" step="0.1" style="width:80px;padding:6px 8px;border:1px solid #d1d5db;border-radius:6px;font-size:12px;margin-top:2px;"></label>
                    <label style="font-size:11px;font-weight:600;color:#374151;">Persona (角色描述)
                        <textarea id="orch-ce-persona" rows="4" placeholder="描述这位专家的角色、专长和行为风格..." style="width:100%;padding:6px 8px;border:1px solid #d1d5db;border-radius:6px;font-size:12px;margin-top:2px;resize:vertical;"></textarea>
                    </label>
                </div>
                <div class="orch-modal-btns">
                    <button id="orch-ce-cancel" style="padding:6px 14px;border-radius:6px;border:1px solid #d1d5db;background:white;color:#374151;cursor:pointer;font-size:12px;">取消</button>
                    <button id="orch-ce-save" style="padding:6px 14px;border-radius:6px;border:none;background:#2563eb;color:white;cursor:pointer;font-size:12px;">保存</button>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);
        overlay.querySelector('#orch-ce-cancel').addEventListener('click', () => overlay.remove());
        overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });
        overlay.querySelector('#orch-ce-save').addEventListener('click', async () => {
            const name = document.getElementById('orch-ce-name').value.trim();
            const tag = document.getElementById('orch-ce-tag').value.trim();
            const temperature = parseFloat(document.getElementById('orch-ce-temp').value) || 0.7;
            const persona = document.getElementById('orch-ce-persona').value.trim();
            if (!name || !tag || !persona) { orchToast('请填写完整信息'); return; }
            try {
                const r = await fetch('/proxy_visual/experts/custom', {
                    method: 'POST', headers: {'Content-Type':'application/json'},
                    body: JSON.stringify({name, tag, temperature, persona}),
                });
                const res = await r.json();
                if (r.ok) {
                    orchToast('自定义专家已添加: ' + name);
                    overlay.remove();
                    orchLoadExperts();
                } else {
                    orchToast('失败: ' + (res.detail || res.error || '未知错误'));
                }
            } catch(e) { orchToast('网络错误'); }
        });
    }

    function orchRenderSidebar() {
        orchRenderExpertSidebar();
        // Manual card
        const mc = document.getElementById('orch-manual-card');
        mc.addEventListener('dragstart', e => {
            e.dataTransfer.setData('application/json', JSON.stringify({type:'manual', name:'手动注入', tag:'manual', emoji:'📝', temperature:0}));
            e.dataTransfer.effectAllowed = 'copy';
        });
        mc.addEventListener('dblclick', () => orchAddNodeCenter({type:'manual', name:'手动注入', tag:'manual', emoji:'📝', temperature:0}));
    }

    // ── Settings ──
    function orchSetupSettings() {
        document.getElementById('orch-threshold').addEventListener('input', e => {
            document.getElementById('orch-threshold-val').textContent = e.target.value;
        });
    }
    function orchGetSettings() {
        return {
            repeat: document.getElementById('orch-repeat').checked,
            max_rounds: parseInt(document.getElementById('orch-rounds').value) || 5,
            use_bot_session: document.getElementById('orch-bot-session').checked,
            cluster_threshold: parseInt(document.getElementById('orch-threshold').value) || 150,
        };
    }

    // ── Node Management ──
    function orchNextInstance(data) {
        // Compute next instance number for this agent identity
        const key = data.type === 'session_agent' ? ('sa:' + (data.session_id||'')) : ('ex:' + (data.tag||'custom'));
        let maxInst = 0;
        orch.nodes.forEach(n => {
            const nk = n.type === 'session_agent' ? ('sa:' + (n.session_id||'')) : ('ex:' + (n.tag||'custom'));
            if (nk === key && n.instance > maxInst) maxInst = n.instance;
        });
        return maxInst + 1;
    }

    function orchAddNode(data, x, y) {
        const id = 'on' + orch.nid++;
        const inst = data.instance || orchNextInstance(data);
        const node = { id, name: data.name, tag: data.tag||'custom', emoji: data.emoji||'⭐', x: Math.round(x), y: Math.round(y), type: data.type||'expert', temperature: data.temperature||0.5, author: data.author||'主持人', content: data.content||'', session_id: data.session_id||'', source: data.source||'', instance: inst };
        orch.nodes.push(node);
        orchRenderNode(node);
        orchUpdateYaml();
        orchUpdateStatus();
        document.getElementById('orch-canvas-hint').style.display = 'none';
        return node;
    }

    function orchAddNodeCenter(data) {
        const area = document.getElementById('orch-canvas-area');
        const cx = (area.offsetWidth / 2 - orch.panX) / orch.zoom - 60;
        const cy = (area.offsetHeight / 2 - orch.panY) / orch.zoom - 20;
        const n = orch.nodes.length;
        const angle = n * 137.5 * Math.PI / 180;
        const radius = 80 * Math.sqrt(n) * 0.5;
        return orchAddNode(data, cx + radius * Math.cos(angle), cy + radius * Math.sin(angle));
    }

    function orchRenderNode(node) {
        const area = document.getElementById('orch-canvas-inner');
        const el = document.createElement('div');
        const isSession = node.type === 'session_agent';
        el.className = 'orch-node' + (node.type === 'manual' ? ' manual-type' : '') + (isSession ? ' session-type' : '');
        el.id = 'onode-' + node.id;
        el.style.left = node.x + 'px';
        el.style.top = node.y + 'px';
        if (isSession) el.style.borderColor = '#6366f1';

        const status = orch.sessionStatuses[node.tag] || orch.sessionStatuses[node.name] || 'idle';
        const instBadge = `<span style="display:inline-block;background:#2563eb;color:#fff;font-size:9px;font-weight:700;border-radius:50%;min-width:16px;height:16px;line-height:16px;text-align:center;margin-left:3px;flex-shrink:0;">${node.instance||1}</span>`;
        const tagLine = isSession ? `<div class="orch-node-tag" style="color:#6366f1;font-family:monospace;">#${(node.session_id||'').slice(-8)}</div>` : `<div class="orch-node-tag">${escapeHtml(node.tag)}</div>`;
        el.innerHTML = `
            <span class="orch-node-emoji">${node.emoji}</span>
            <div style="min-width:0;flex:1;"><div class="orch-node-name" style="display:flex;align-items:center;">${escapeHtml(node.name)}${instBadge}</div>${tagLine}</div>
            <div class="orch-node-del" title="移除">×</div>
            <div class="orch-port port-in" data-node="${node.id}" data-dir="in"></div>
            <div class="orch-port port-out" data-node="${node.id}" data-dir="out"></div>
            <div class="orch-node-status ${status}"></div>
        `;

        el.querySelector('.orch-node-del').addEventListener('click', e => { e.stopPropagation(); orchRemoveNode(node.id); });

        el.addEventListener('mousedown', e => {
            if (e.target.classList.contains('orch-port') || e.target.classList.contains('orch-node-del')) return;
            e.stopPropagation();
            if (!e.shiftKey && !orch.selectedNodes.has(node.id)) orchClearSelection();
            orchSelectNode(node.id);
            const cp = orchClientToCanvas(e.clientX, e.clientY);
            orch.dragging = { nodeId: node.id, offX: cp.x - node.x, offY: cp.y - node.y, multi: orch.selectedNodes.size > 1, starts: {} };
            if (orch.selectedNodes.size > 1) {
                orch.selectedNodes.forEach(nid => { const n = orch.nodes.find(nn=>nn.id===nid); if(n) orch.dragging.starts[nid]={x:n.x,y:n.y}; });
            }
        });

        el.querySelectorAll('.orch-port').forEach(port => {
            port.addEventListener('mousedown', e => {
                e.stopPropagation();
                if (port.dataset.dir === 'out') {
                    const portRect = port.getBoundingClientRect();
                    const cp = orchClientToCanvas(portRect.left + 5, portRect.top + 5);
                    orch.connecting = { sourceId: node.id, sx: cp.x, sy: cp.y };
                }
            });
            port.addEventListener('mouseup', e => {
                e.stopPropagation();
                if (orch.connecting && port.dataset.dir === 'in' && port.dataset.node !== orch.connecting.sourceId) {
                    orchAddEdge(orch.connecting.sourceId, node.id);
                }
                orch.connecting = null;
                orchRemoveTempLine();
            });
        });

        el.addEventListener('contextmenu', e => {
            e.preventDefault(); e.stopPropagation();
            if (!orch.selectedNodes.has(node.id)) { orchClearSelection(); orchSelectNode(node.id); }
            orchShowContextMenu(e.clientX, e.clientY, node);
        });
        el.addEventListener('dblclick', () => { if (node.type === 'manual') orchShowManualModal(node); });
        area.appendChild(el);
    }

    function orchRemoveNode(id) {
        orch.nodes = orch.nodes.filter(n => n.id !== id);
        orch.edges = orch.edges.filter(e => e.source !== id && e.target !== id);
        orch.selectedNodes.delete(id);
        orch.groups.forEach(g => { g.nodeIds = g.nodeIds.filter(nid => nid !== id); });
        const el = document.getElementById('onode-' + id);
        if (el) el.remove();
        orchRenderEdges();
        orchUpdateYaml();
        orchUpdateStatus();
        if (orch.nodes.length === 0) document.getElementById('orch-canvas-hint').style.display = '';
    }

    function orchSelectNode(id) { orch.selectedNodes.add(id); const el=document.getElementById('onode-'+id); if(el) el.classList.add('selected'); }
    function orchClearSelection() { orch.selectedNodes.forEach(id => { const el=document.getElementById('onode-'+id); if(el) el.classList.remove('selected'); }); orch.selectedNodes.clear(); }

    // ── Edge Management ──
    function orchAddEdge(src, tgt) {
        if (orch.edges.some(e => e.source === src && e.target === tgt)) return;
        orch.edges.push({ id: 'oe' + orch.eid++, source: src, target: tgt });
        orchRenderEdges();
        orchUpdateYaml();
    }

    function orchRenderEdges() {
        const svg = document.getElementById('orch-edge-svg');
        const defs = svg.querySelector('defs');
        svg.innerHTML = '';
        svg.appendChild(defs);
        orch.edges.forEach(edge => {
            const sn = orch.nodes.find(n => n.id === edge.source);
            const tn = orch.nodes.find(n => n.id === edge.target);
            if (!sn || !tn) return;
            const se = document.getElementById('onode-' + edge.source);
            const te = document.getElementById('onode-' + edge.target);
            if (!se || !te) return;
            const x1 = sn.x + se.offsetWidth, y1 = sn.y + se.offsetHeight/2;
            const x2 = tn.x, y2 = tn.y + te.offsetHeight/2;
            const cpx = (x1+x2)/2;
            const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            path.setAttribute('d', `M${x1},${y1} C${cpx},${y1} ${cpx},${y2} ${x2},${y2}`);
            path.setAttribute('stroke', '#2563eb');
            path.setAttribute('stroke-width', '2');
            path.setAttribute('fill', 'none');
            path.setAttribute('marker-end', 'url(#orch-arrowhead)');
            path.style.cursor = 'pointer';
            path.style.pointerEvents = 'all';
            path.addEventListener('click', e => { e.stopPropagation(); orch.edges = orch.edges.filter(ee=>ee.id!==edge.id); orchRenderEdges(); orchUpdateYaml(); });
            path.addEventListener('mouseenter', () => { path.setAttribute('stroke','#ef4444'); path.setAttribute('stroke-width','3'); });
            path.addEventListener('mouseleave', () => { path.setAttribute('stroke','#2563eb'); path.setAttribute('stroke-width','2'); });
            svg.appendChild(path);
        });
    }

    function orchRemoveTempLine() { const svg=document.getElementById('orch-edge-svg'); const t=svg.querySelector('.temp-line'); if(t)t.remove(); }
    function orchDrawTempLine(x1,y1,x2,y2) {
        const svg=document.getElementById('orch-edge-svg'); orchRemoveTempLine();
        const line=document.createElementNS('http://www.w3.org/2000/svg','line');
        line.classList.add('temp-line');
        line.setAttribute('x1',x1); line.setAttribute('y1',y1); line.setAttribute('x2',x2); line.setAttribute('y2',y2);
        line.setAttribute('stroke','#2563eb80'); line.setAttribute('stroke-width','2'); line.setAttribute('stroke-dasharray','5,5');
        line.style.pointerEvents = 'none';
        svg.appendChild(line);
    }

    // ── Group Management ──
    function orchCreateGroup(type) {
        if (orch.selectedNodes.size < 2 && type !== 'all') { orchToast('请先选中至少2个节点'); return; }
        const members = [...orch.selectedNodes];
        const nodes = members.map(id => orch.nodes.find(n=>n.id===id)).filter(Boolean);
        const pad = 30;
        const x = Math.min(...nodes.map(n=>n.x)) - pad;
        const y = Math.min(...nodes.map(n=>n.y)) - pad;
        const w = Math.max(...nodes.map(n=>n.x+120)) - x + pad;
        const h = Math.max(...nodes.map(n=>n.y+50)) - y + pad;
        const id = 'og' + orch.gid++;
        const labelMap = {parallel:'🔀 并行', all:'👥 全员'};
        const group = { id, name: labelMap[type]||type, type, x, y, w, h, nodeIds: members };
        orch.groups.push(group);
        orchRenderGroup(group);
        orchUpdateYaml();
    }

    function orchRenderGroup(group) {
        const area = document.getElementById('orch-canvas-inner');
        const el = document.createElement('div');
        el.className = 'orch-group ' + group.type;
        el.id = 'ogroup-' + group.id;
        el.style.cssText = `left:${group.x}px;top:${group.y}px;width:${group.w}px;height:${group.h}px;`;
        el.innerHTML = `<span class="orch-group-label">${group.name}</span><div class="orch-group-del" title="解散">×</div>`;
        el.querySelector('.orch-group-del').addEventListener('click', e => {
            e.stopPropagation();
            orch.groups = orch.groups.filter(g=>g.id!==group.id);
            el.remove();
            orchUpdateYaml();
        });
        area.appendChild(el);
    }

    function orchUpdateGroupBounds(group) {
        const members = orch.nodes.filter(n => group.nodeIds.includes(n.id));
        if (!members.length) return;
        const pad = 30;
        group.x = Math.min(...members.map(n=>n.x)) - pad;
        group.y = Math.min(...members.map(n=>n.y)) - pad;
        group.w = Math.max(...members.map(n=>n.x+120)) - group.x + pad;
        group.h = Math.max(...members.map(n=>n.y+50)) - group.y + pad;
        const el = document.getElementById('ogroup-' + group.id);
        if (el) { el.style.left=group.x+'px'; el.style.top=group.y+'px'; el.style.width=group.w+'px'; el.style.height=group.h+'px'; }
    }

    // ── Canvas Events ──
    function orchSetupCanvas() {
        const canvas = document.getElementById('orch-canvas-area');

        // ── Drag-and-drop from sidebar ──
        canvas.addEventListener('dragover', e => { e.preventDefault(); e.dataTransfer.dropEffect = 'copy'; });
        canvas.addEventListener('drop', e => {
            e.preventDefault();
            try {
                const data = JSON.parse(e.dataTransfer.getData('application/json'));
                const cp = orchClientToCanvas(e.clientX, e.clientY);
                orchAddNode(data, cp.x - 55, cp.y - 20);
            } catch(err) {}
        });

        // ── Mousedown: selection rect ──
        canvas.addEventListener('mousedown', e => {
            const inner = document.getElementById('orch-canvas-inner');
            if (e.target === canvas || e.target === inner || e.target.id === 'orch-canvas-hint') {
                orchClearSelection();
                const cp = orchClientToCanvas(e.clientX, e.clientY);
                orch.selecting = { sx: cp.x, sy: cp.y };
            }
        });

        // ── Mousemove: drag nodes / connect / select ──
        canvas.addEventListener('mousemove', e => {
            if (orch.dragging) {
                const d = orch.dragging;
                const cp = orchClientToCanvas(e.clientX, e.clientY);
                if (d.multi) {
                    const dx = cp.x - d.offX - d.starts[d.nodeId].x;
                    const dy = cp.y - d.offY - d.starts[d.nodeId].y;
                    orch.selectedNodes.forEach(nid => {
                        const n = orch.nodes.find(nn=>nn.id===nid);
                        if (n && d.starts[nid]) { n.x = d.starts[nid].x + dx; n.y = d.starts[nid].y + dy; const el=document.getElementById('onode-'+nid); if(el){el.style.left=n.x+'px';el.style.top=n.y+'px';} }
                    });
                } else {
                    const n = orch.nodes.find(nn=>nn.id===d.nodeId);
                    if (n) { n.x = cp.x - d.offX; n.y = cp.y - d.offY; const el=document.getElementById('onode-'+n.id); if(el){el.style.left=n.x+'px';el.style.top=n.y+'px';} }
                }
                orchRenderEdges();
                orch.groups.forEach(g => orchUpdateGroupBounds(g));
            } else if (orch.connecting) {
                const cp = orchClientToCanvas(e.clientX, e.clientY);
                orchDrawTempLine(orch.connecting.sx, orch.connecting.sy, cp.x, cp.y);
            } else if (orch.selecting) {
                const s = orch.selecting;
                const cp = orchClientToCanvas(e.clientX, e.clientY);
                let existing = document.querySelector('.orch-sel-rect');
                const inner = document.getElementById('orch-canvas-inner');
                if (!existing) { existing = document.createElement('div'); existing.className='orch-sel-rect'; inner.appendChild(existing); }
                const x = Math.min(s.sx, cp.x), y = Math.min(s.sy, cp.y);
                const w = Math.abs(cp.x - s.sx), h = Math.abs(cp.y - s.sy);
                existing.style.cssText = `left:${x}px;top:${y}px;width:${w}px;height:${h}px;`;
            }
        });

        // ── Mouseup ──
        canvas.addEventListener('mouseup', e => {
            if (orch.dragging) { orch.dragging = null; orchUpdateYaml(); }
            if (orch.connecting) { orch.connecting = null; orchRemoveTempLine(); }
            if (orch.selecting) {
                const s = orch.selecting;
                const cp = orchClientToCanvas(e.clientX, e.clientY);
                const x1 = Math.min(s.sx, cp.x), y1 = Math.min(s.sy, cp.y);
                const x2 = Math.max(s.sx, cp.x), y2 = Math.max(s.sy, cp.y);
                if (Math.abs(x2-x1) > 10 && Math.abs(y2-y1) > 10) {
                    orch.nodes.forEach(n => { if (n.x > x1 && n.x < x2 && n.y > y1 && n.y < y2) orchSelectNode(n.id); });
                }
                orch.selecting = null;
                document.querySelectorAll('.orch-sel-rect').forEach(el => el.remove());
            }
        });

        // ── Context menu ──
        canvas.addEventListener('contextmenu', e => {
            e.preventDefault();
            orchShowContextMenu(e.clientX, e.clientY);
        });

        // ── Keyboard shortcuts ──
        document.addEventListener('keydown', e => {
            if (currentPage !== 'orchestrate') return;
            if (e.key === 'Delete' || e.key === 'Backspace') {
                if (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'TEXTAREA') return;
                orch.selectedNodes.forEach(id => orchRemoveNode(id));
            }
            if ((e.ctrlKey || e.metaKey) && e.key === 'g') {
                e.preventDefault();
                if (orch.selectedNodes.size >= 2) orchCreateGroup('parallel');
            }
            if ((e.ctrlKey || e.metaKey) && e.key === 'a' && currentPage === 'orchestrate') {
                e.preventDefault();
                orch.nodes.forEach(n => orchSelectNode(n.id));
            }
            if (e.key === 'Escape') { orchClearSelection(); orchHideContextMenu(); }
        });
        document.addEventListener('keyup', e => {});
    }

    function orchShowContextMenu(x, y, targetNode) {
        orchHideContextMenu();
        const menu = document.createElement('div');
        menu.className = 'orch-context-menu';
        menu.id = 'orch-ctx-menu';
        menu.style.left = x + 'px';
        menu.style.top = y + 'px';

        const hasSelection = orch.selectedNodes.size > 0;
        const items = [];

        // ── Node-specific: duplicate / set instance ──
        if (targetNode) {
            items.push({label: '📋 复用此专家 (同序号)', action: () => {
                orchAddNode({...targetNode, instance: targetNode.instance}, targetNode.x + 40, targetNode.y + 40);
            }});
            items.push({label: '➕ 新建实例 (新序号)', action: () => {
                orchAddNode({...targetNode, instance: undefined}, targetNode.x + 40, targetNode.y + 40);
            }});
            items.push({divider: true});
        }

        if (hasSelection && orch.selectedNodes.size >= 2) {
            items.push({label: '🔀 创建并行分组', action: () => orchCreateGroup('parallel')});
            items.push({label: '👥 创建全员分组', action: () => orchCreateGroup('all')});
            items.push({divider: true});
        }
        if (hasSelection) {
            items.push({label: '🗑️ 删除选中', action: () => { orch.selectedNodes.forEach(id => orchRemoveNode(id)); }});
        }
        items.push({label: '🔄 刷新 YAML', action: () => orchUpdateYaml()});
        items.push({label: '🗑️ 清空画布', action: () => orchClearCanvas()});

        items.forEach(item => {
            if (item.divider) { const d = document.createElement('div'); d.className='orch-menu-divider'; menu.appendChild(d); return; }
            const d = document.createElement('div');
            d.className = 'orch-menu-item';
            d.textContent = item.label;
            d.addEventListener('click', () => { item.action(); orchHideContextMenu(); });
            menu.appendChild(d);
        });

        document.body.appendChild(menu);
        document.addEventListener('click', orchHideContextMenu, {once: true});
    }
    function orchHideContextMenu() { const m = document.getElementById('orch-ctx-menu'); if(m) m.remove(); }

    // ── Manual Edit Modal ──
    function orchShowManualModal(node) {
        const overlay = document.createElement('div');
        overlay.className = 'orch-modal-overlay';
        overlay.id = 'orch-manual-modal';
        overlay.innerHTML = `<div class="orch-modal">
            <h3>📝 编辑手动注入内容</h3>
            <input type="text" id="orch-man-author" value="${node.author||'主持人'}" placeholder="作者">
            <textarea id="orch-man-content" placeholder="注入内容...">${node.content||''}</textarea>
            <div class="orch-modal-btns">
                <button onclick="document.getElementById('orch-manual-modal').remove()">取消</button>
                <button class="primary" onclick="orchSaveManual('${node.id}')">保存</button>
            </div>
        </div>`;
        document.body.appendChild(overlay);
        overlay.addEventListener('click', e => { if (e.target === overlay) overlay.remove(); });
    }
    function orchSaveManual(nodeId) {
        const node = orch.nodes.find(n=>n.id===nodeId);
        if (node) {
            node.author = document.getElementById('orch-man-author').value;
            node.content = document.getElementById('orch-man-content').value;
        }
        document.getElementById('orch-manual-modal')?.remove();
        orchUpdateYaml();
    }

    // ── Layout Data ──
    function orchGetLayoutData() {
        return {
            nodes: orch.nodes.map(n => ({...n})),
            edges: orch.edges.map(e => ({...e})),
            groups: orch.groups.map(g => ({...g})),
            settings: orchGetSettings(),
            view: { zoom: orch.zoom, panX: orch.panX, panY: orch.panY },
        };
    }

    // ── YAML Generation (Rule-based) ──
    async function orchUpdateYaml() {
        orchUpdateStatus();
        const data = orchGetLayoutData();
        if (orch.nodes.length === 0) {
            document.getElementById('orch-yaml-content').textContent = '拖入专家后自动生成...';
            return;
        }
        try {
            const r = await fetch('/proxy_visual/generate-yaml', {
                method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data),
            });
            const res = await r.json();
            document.getElementById('orch-yaml-content').textContent = res.yaml || '# Error: ' + (res.error || 'Unknown');
        } catch(e) {
            document.getElementById('orch-yaml-content').textContent = '# Error: ' + e.message;
        }
    }

    // ── AI Generate YAML (with session selection) ──
    let orchTargetSessionId = null;

    async function orchGenerateAgentYaml() {
        if (orch.nodes.length === 0) { orchToast('请先添加专家节点'); return; }
        orchShowSessionSelectModal();
    }

    async function orchShowSessionSelectModal() {
        const overlay = document.createElement('div');
        overlay.className = 'orch-modal-overlay';
        overlay.id = 'orch-session-select-overlay';

        overlay.innerHTML = `
            <div class="orch-modal" style="min-width:400px;max-width:500px;">
                <h3>🎯 选择目标 Agent Session</h3>
                <p style="font-size:12px;color:#6b7280;margin-bottom:10px;">选择一个已有的对话 Session，或新建一个，生成完成后可跳转继续对话。</p>
                <div class="orch-session-list" id="orch-session-select-list">
                    <div style="text-align:center;padding:20px;color:#9ca3af;font-size:12px;">⏳ 加载中...</div>
                </div>
                <div class="orch-modal-btns">
                    <button id="orch-session-cancel-btn" style="padding:6px 14px;border-radius:6px;border:1px solid #d1d5db;background:white;color:#374151;cursor:pointer;font-size:12px;">取消</button>
                    <button id="orch-session-confirm-btn" disabled style="padding:6px 14px;border-radius:6px;border:none;background:#2563eb;color:white;cursor:pointer;font-size:12px;opacity:0.5;">确认并生成</button>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);

        let selectedSid = null;

        overlay.querySelector('#orch-session-cancel-btn').addEventListener('click', () => overlay.remove());
        overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });

        const listEl = overlay.querySelector('#orch-session-select-list');
        try {
            const resp = await fetch('/proxy_sessions');
            const data = await resp.json();
            listEl.innerHTML = '';

            const newSessionId = Date.now().toString(36) + Math.random().toString(36).substr(2, 4);
            const newItem = document.createElement('div');
            newItem.className = 'orch-session-new';
            newItem.innerHTML = `<span style="font-size:18px;">🆕</span><div style="flex:1;"><div style="font-size:13px;font-weight:500;color:#2563eb;">新建对话</div><div style="font-size:10px;color:#9ca3af;font-family:monospace;">#${newSessionId.slice(-6)}</div></div>`;
            newItem.addEventListener('click', () => {
                listEl.querySelectorAll('.orch-session-item,.orch-session-new').forEach(el => el.classList.remove('selected'));
                newItem.classList.add('selected');
                selectedSid = newSessionId;
                const btn = overlay.querySelector('#orch-session-confirm-btn');
                btn.disabled = false; btn.style.opacity = '1';
            });
            listEl.appendChild(newItem);

            if (data.sessions && data.sessions.length > 0) {
                data.sessions.sort((a, b) => b.session_id.localeCompare(a.session_id));
                for (const s of data.sessions) {
                    const item = document.createElement('div');
                    item.className = 'orch-session-item';
                    item.innerHTML = `<span class="orch-session-icon">💬</span><div style="flex:1;min-width:0;"><div class="orch-session-title">${escapeHtml(s.title || 'Untitled')}</div><div class="orch-session-id">#${s.session_id.slice(-6)} · ${s.message_count || 0} 条消息</div></div>`;
                    item.addEventListener('click', () => {
                        listEl.querySelectorAll('.orch-session-item,.orch-session-new').forEach(el => el.classList.remove('selected'));
                        item.classList.add('selected');
                        selectedSid = s.session_id;
                        const btn = overlay.querySelector('#orch-session-confirm-btn');
                        btn.disabled = false; btn.style.opacity = '1';
                    });
                    listEl.appendChild(item);
                }
            }
        } catch(e) {
            listEl.innerHTML = '<div style="text-align:center;padding:20px;color:#dc2626;font-size:12px;">❌ 加载 Session 列表失败</div>';
        }

        overlay.querySelector('#orch-session-confirm-btn').addEventListener('click', () => {
            if (!selectedSid) return;
            orchTargetSessionId = selectedSid;
            overlay.remove();
            orchDoGenerateAgentYaml();
        });
    }

    async function orchDoGenerateAgentYaml() {
        const data = orchGetLayoutData();
        // Attach the user-selected target session_id
        data.target_session_id = orchTargetSessionId || null;

        const statusEl = document.getElementById('orch-agent-status');
        const promptEl = document.getElementById('orch-prompt-content');
        const yamlEl = document.getElementById('orch-agent-yaml');
        statusEl.textContent = '🔄 正在与 Agent 通信 (Session: #' + (orchTargetSessionId||'').slice(-6) + ')...';
        statusEl.style.cssText = 'color:#2563eb;background:#eff6ff;border-color:#bfdbfe;';
        promptEl.textContent = '⏳ 生成中...';
        yamlEl.textContent = '⏳ 等待 Agent 返回...';

        const oldBtn = document.getElementById('orch-goto-chat-container');
        if (oldBtn) oldBtn.remove();

        try {
            const r = await fetch('/proxy_visual/agent-generate-yaml', {
                method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data),
            });
            const res = await r.json();
            if (res.prompt) promptEl.textContent = res.prompt;
            if (res.error) {
                yamlEl.textContent = '# ⚠️ ' + res.error;
                statusEl.textContent = '⚠️ ' + (res.error.includes('401') ? '认证失败' : 'Agent 不可用');
                statusEl.style.cssText = 'color:#dc2626;background:#fef2f2;border-color:#fca5a5;';
                orchToast('Agent 不可用');
                return;
            }
            if (res.agent_yaml) {
                yamlEl.textContent = res.agent_yaml;
                if (res.validation?.valid) {
                    let statusMsg = `✅ 有效 YAML — ${res.validation.steps} 步骤 [${res.validation.step_types.join(', ')}]`;
                    if (res.saved_file && !res.saved_file.startsWith('save_error')) {
                        statusMsg += ` | 💾 已保存: ${res.saved_file}`;
                    }
                    statusEl.textContent = statusMsg;
                    statusEl.style.cssText = 'color:#16a34a;background:#f0fdf4;border-color:#86efac;';
                    orchToast(res.saved_file ? 'YAML 已生成并保存! ✅' : 'Agent 生成了有效的 YAML! ✅');
                } else {
                    statusEl.textContent = `⚠️ YAML 校验问题: ${res.validation?.error||''}`;
                    statusEl.style.cssText = 'color:#d97706;background:#fffbeb;border-color:#fbbf24;';
                }
                orchShowGotoChatButton();
            }
        } catch(e) {
            promptEl.textContent = '# 通信失败: ' + e.message;
            statusEl.textContent = '❌ 连接错误';
            statusEl.style.cssText = 'color:#dc2626;background:#fef2f2;border-color:#fca5a5;';
        }
    }

    function orchShowGotoChatButton() {
        const old = document.getElementById('orch-goto-chat-container');
        if (old) old.remove();

        if (!orchTargetSessionId) return;

        const container = document.createElement('div');
        container.id = 'orch-goto-chat-container';
        container.style.cssText = 'padding: 8px 12px; text-align: center;';

        const sessionLabel = '#' + orchTargetSessionId.slice(-6);
        container.innerHTML = `
            <button class="orch-goto-chat-btn" onclick="orchGotoChat()">
                💬 跳转到对话 ${escapeHtml(sessionLabel)} 继续聊天
            </button>
        `;

        const statusEl = document.getElementById('orch-agent-status');
        if (statusEl && statusEl.parentNode) {
            statusEl.parentNode.insertBefore(container, statusEl.nextSibling);
        }
    }

    async function orchGotoChat() {
        if (!orchTargetSessionId) { orchToast('没有选中的 Session'); return; }

        const prevSessionId = currentSessionId;
        if (currentSessionId === orchTargetSessionId) {
            currentSessionId = '__temp_orch__';
        }

        switchPage('chat');
        await switchToSession(orchTargetSessionId);

        orchToast('已跳转到对话 #' + orchTargetSessionId.slice(-6));
    }

    // ── Session Status ──
    async function orchRefreshSessions() {
        try {
            const r = await fetch('/proxy_visual/sessions-status');
            const sessions = await r.json();
            orch.sessionStatuses = {};
            if (Array.isArray(sessions)) {
                sessions.forEach(s => {
                    const sid = s.session_id || s.id || '';
                    const isRunning = s.is_running || s.status === 'running' || false;
                    orch.sessionStatuses[sid] = isRunning ? 'running' : 'idle';
                });
            }
            orch.nodes.forEach(n => {
                const el = document.getElementById('onode-' + n.id);
                if (!el) return;
                const dot = el.querySelector('.orch-node-status');
                if (!dot) return;
                const isRunning = Object.entries(orch.sessionStatuses).some(([sid, st]) =>
                    st === 'running' && (sid.includes(n.name) || sid.includes(n.tag))
                );
                dot.className = 'orch-node-status ' + (isRunning ? 'running' : 'idle');
            });
            orchToast('Session 状态已更新');
        } catch(e) {
            orchToast('获取状态失败');
        }
    }

    // ── Actions ──
    function orchClearCanvas() {
        orch.nodes = []; orch.edges = []; orch.groups = []; orch.selectedNodes.clear();
        orch.zoom = 1; orch.panX = 0; orch.panY = 0; orchApplyTransform();
        const area = document.getElementById('orch-canvas-inner');
        area.querySelectorAll('.orch-node,.orch-group').forEach(el => el.remove());
        orchRenderEdges();
        orchUpdateYaml();
        document.getElementById('orch-canvas-hint').style.display = '';
    }

    function orchAutoArrange() {
        const n = orch.nodes.length;
        if (n === 0) return;
        orch.zoom = 1; orch.panX = 0; orch.panY = 0; orchApplyTransform();
        const area = document.getElementById('orch-canvas-area');
        const cw = area.offsetWidth, ch = area.offsetHeight;
        const cols = Math.ceil(Math.sqrt(n));
        const gapX = Math.min(180, (cw - 60) / cols);
        const gapY = Math.min(90, (ch - 60) / Math.ceil(n / cols));
        orch.nodes.forEach((node, i) => {
            const col = i % cols, row = Math.floor(i / cols);
            node.x = 40 + col * gapX;
            node.y = 40 + row * gapY;
            const el = document.getElementById('onode-' + node.id);
            if (el) { el.style.left = node.x + 'px'; el.style.top = node.y + 'px'; }
        });
        orchRenderEdges();
        orch.groups.forEach(g => orchUpdateGroupBounds(g));
        orchUpdateYaml();
        orchToast('已自动排列');
    }

    async function orchSaveLayout() {
        const name = prompt('布局名称:', 'my-layout');
        if (!name) return;
        const data = orchGetLayoutData();
        data.name = name;
        try {
            await fetch('/proxy_visual/save-layout', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(data) });
            orchToast('已保存: ' + name);
        } catch(e) { orchToast('保存失败'); }
    }

    async function orchLoadLayout() {
        try {
            const r = await fetch('/proxy_visual/load-layouts');
            const layouts = await r.json();
            if (!layouts.length) { orchToast('没有已保存的布局'); return; }

            // Build visual selection modal
            const overlay = document.createElement('div');
            overlay.className = 'orch-modal-overlay';
            overlay.id = 'orch-load-layout-overlay';
            overlay.innerHTML = `
                <div class="orch-modal" style="min-width:360px;max-width:460px;">
                    <h3>📂 选择布局</h3>
                    <div class="orch-session-list" id="orch-layout-select-list" style="max-height:300px;overflow-y:auto;"></div>
                    <div class="orch-modal-btns">
                        <button id="orch-layout-cancel-btn" style="padding:6px 14px;border-radius:6px;border:1px solid #d1d5db;background:white;color:#374151;cursor:pointer;font-size:12px;">取消</button>
                        <button id="orch-layout-del-btn" style="padding:6px 14px;border-radius:6px;border:1px solid #fca5a5;background:#fef2f2;color:#dc2626;cursor:pointer;font-size:12px;display:none;">🗑️ 删除</button>
                        <button id="orch-layout-confirm-btn" disabled style="padding:6px 14px;border-radius:6px;border:none;background:#2563eb;color:white;cursor:pointer;font-size:12px;opacity:0.5;">加载</button>
                    </div>
                </div>
            `;
            document.body.appendChild(overlay);

            let selectedName = null;
            overlay.querySelector('#orch-layout-cancel-btn').addEventListener('click', () => overlay.remove());
            overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });

            const listEl = overlay.querySelector('#orch-layout-select-list');
            for (const name of layouts) {
                const item = document.createElement('div');
                item.className = 'orch-session-item';
                item.innerHTML = `<span class="orch-session-icon">📋</span><div style="flex:1;min-width:0;"><div class="orch-session-title">${escapeHtml(name)}</div></div>`;
                item.addEventListener('click', () => {
                    listEl.querySelectorAll('.orch-session-item').forEach(el => el.classList.remove('selected'));
                    item.classList.add('selected');
                    selectedName = name;
                    const btn = overlay.querySelector('#orch-layout-confirm-btn');
                    btn.disabled = false; btn.style.opacity = '1';
                    overlay.querySelector('#orch-layout-del-btn').style.display = '';
                });
                listEl.appendChild(item);
            }

            overlay.querySelector('#orch-layout-del-btn').addEventListener('click', async () => {
                if (!selectedName || !confirm('确定删除布局 "' + selectedName + '"？')) return;
                try {
                    await fetch('/proxy_visual/delete-layout/' + encodeURIComponent(selectedName), { method: 'DELETE' });
                    orchToast('已删除: ' + selectedName);
                    overlay.remove();
                    orchLoadLayout();
                } catch(e) { orchToast('删除失败'); }
            });

            overlay.querySelector('#orch-layout-confirm-btn').addEventListener('click', async () => {
                if (!selectedName) return;
                overlay.remove();
                await orchDoLoadLayout(selectedName);
            });
        } catch(e) { orchToast('加载失败'); }
    }

    async function orchDoLoadLayout(name) {
        try {
            const r2 = await fetch('/proxy_visual/load-layout/' + encodeURIComponent(name));
            const data = await r2.json();
            if (data.error) { orchToast(data.error); return; }
            orchClearCanvas();

            // Restore settings
            if (data.settings) {
                document.getElementById('orch-repeat').checked = data.settings.repeat !== false;
                document.getElementById('orch-rounds').value = data.settings.max_rounds || 5;
                document.getElementById('orch-bot-session').checked = data.settings.use_bot_session || false;
                if (data.settings.cluster_threshold) {
                    document.getElementById('orch-threshold').value = data.settings.cluster_threshold;
                    document.getElementById('orch-threshold-val').textContent = data.settings.cluster_threshold;
                }
            }

            // Restore view (zoom/pan)
            if (data.view) {
                orch.zoom = data.view.zoom || 1;
                orch.panX = data.view.panX || 0;
                orch.panY = data.view.panY || 0;
                orchApplyTransform();
            }

            // Build id mapping: restore nodes with ORIGINAL ids preserved
            const idMap = {};
            (data.nodes||[]).forEach(n => {
                const origId = n.id;
                const newNode = orchAddNode(n, n.x, n.y);
                idMap[origId] = newNode.id;
            });

            // Restore edges using mapped ids
            (data.edges||[]).forEach(e => {
                const src = idMap[e.source];
                const tgt = idMap[e.target];
                if (src && tgt) orchAddEdge(src, tgt);
            });

            // Restore groups with mapped node ids
            (data.groups||[]).forEach(g => {
                const mappedGroup = {...g, nodeIds: (g.nodeIds||[]).map(nid => idMap[nid]).filter(Boolean)};
                if (mappedGroup.nodeIds.length > 0) {
                    orch.groups.push(mappedGroup);
                    orchRenderGroup(mappedGroup);
                }
            });

            orchRenderEdges();
            orchUpdateYaml();
            orchToast('已加载: ' + name);
        } catch(e) { orchToast('加载失败: ' + e.message); }
    }

    function orchExportYaml() {
        const yaml = document.getElementById('orch-yaml-content').textContent;
        if (!yaml || yaml.startsWith('拖入')) { orchToast('请先生成 YAML'); return; }
        navigator.clipboard.writeText(yaml).then(() => orchToast('YAML 已复制!')).catch(() => {
            const ta = document.createElement('textarea'); ta.value = yaml; document.body.appendChild(ta); ta.select(); document.execCommand('copy'); document.body.removeChild(ta); orchToast('YAML 已复制!');
        });
    }
    function orchCopyPrompt() {
        const text = document.getElementById('orch-prompt-content').textContent;
        navigator.clipboard.writeText(text).catch(() => {}); orchToast('Prompt 已复制');
    }
    function orchCopyAgentYaml() {
        const text = document.getElementById('orch-agent-yaml').textContent;
        navigator.clipboard.writeText(text).catch(() => {}); orchToast('Agent YAML 已复制');
    }

    function orchUpdateStatus() {
        document.getElementById('orch-status-bar').textContent = `节点: ${orch.nodes.length} | 连线: ${orch.edges.length} | 分组: ${orch.groups.length}`;
    }

    function orchToast(msg) {
        const existing = document.querySelector('.orch-toast');
        if (existing) existing.remove();
        const t = document.createElement('div');
        t.className = 'orch-toast';
        t.textContent = msg;
        document.body.appendChild(t);
        setTimeout(() => t.remove(), 2500);
    }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/manifest.json")
def manifest():
    """Serve PWA manifest for iOS/Android Add-to-Home-Screen support."""
    manifest_data = {
        "name": "Teamclaw",
        "short_name": "Teamclaw",
        "description": "Xavier AI Agent - Intelligent Control Assistant",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "orientation": "portrait",
        "background_color": "#111827",
        "theme_color": "#111827",
        "lang": "zh-CN",
        "categories": ["productivity", "utilities"],
        "icons": [
            {
                "src": "https://img.icons8.com/fluency/192/robot-2.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable"
            },
            {
                "src": "https://img.icons8.com/fluency/512/robot-2.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable"
            }
        ]
    }
    return app.response_class(
        response=__import__("json").dumps(manifest_data),
        mimetype="application/manifest+json"
    )


@app.route("/sw.js")
def service_worker():
    """Serve Service Worker for PWA offline support and caching."""
    sw_code = """
// Teamclaw Service Worker v3
const CACHE_NAME = 'teamclaw-v3';
const PRECACHE_URLS = ['/'];

self.addEventListener('install', event => {
    self.skipWaiting();
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(PRECACHE_URLS))
    );
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
        ).then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', event => {
    // CRITICAL: Only handle GET requests. Non-GET (POST, PUT, DELETE) must pass through directly.
    if (event.request.method !== 'GET') return;

    // API GET requests also pass through without SW interference
    const url = event.request.url;
    if (url.includes('/proxy_') || url.includes('/ask') || url.includes('/v1/') || url.includes('/api/')) return;

    // Cache-first for static GET assets only
    event.respondWith(
        caches.match(event.request).then(cached => {
            const fetched = fetch(event.request).then(response => {
                if (response.ok) {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
                }
                return response;
            }).catch(() => cached);
            return cached || fetched;
        })
    );
});
"""
    return app.response_class(
        response=sw_code,
        mimetype="application/javascript",
        headers={"Service-Worker-Allowed": "/"}
    )


@app.route("/v1/chat/completions", methods=["POST", "OPTIONS"])
def proxy_openai_completions():
    """OpenAI 兼容端点透传：前端直接发 OpenAI 格式，原样转发到后端"""
    if request.method == "OPTIONS":
        # CORS preflight
        resp = Response("", status=204)
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return resp

    # 直接透传请求体和 Authorization header 到后端
    auth_header = request.headers.get("Authorization", "")
    try:
        r = requests.post(
            LOCAL_OPENAI_COMPLETIONS_URL,
            json=request.get_json(silent=True),
            headers={
                "Authorization": auth_header,
                "Content-Type": "application/json",
            },
            stream=True,
            timeout=120,
        )
        if r.status_code != 200:
            return Response(r.content, status=r.status_code, content_type=r.headers.get("content-type", "application/json"))

        # 判断是否是流式响应
        content_type = r.headers.get("content-type", "")
        if "text/event-stream" in content_type:
            def generate():
                for chunk in r.iter_content(chunk_size=None):
                    if chunk:
                        yield chunk
            return Response(
                generate(),
                mimetype="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                },
            )
        else:
            return Response(r.content, status=r.status_code, content_type=content_type)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/v1/models", methods=["GET"])
def proxy_openai_models():
    """透传 /v1/models"""
    try:
        r = requests.get(f"http://127.0.0.1:{PORT_AGENT}/v1/models", timeout=10)
        return Response(r.content, status=r.status_code, content_type=r.headers.get("content-type", "application/json"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_login", methods=["POST"])
def proxy_login():
    """代理登录请求到后端 Agent"""
    user_id = request.json.get("user_id", "")
    password = request.json.get("password", "")

    try:
        r = requests.post(LOCAL_LOGIN_URL, json={"user_id": user_id, "password": password}, timeout=10)
        if r.status_code == 200:
            # 登录成功，在 Flask session 中记录
            session["user_id"] = user_id
            session["password"] = password  # 需要传给后端每次验证
            return jsonify(r.json())
        else:
            return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/proxy_ask", methods=["POST"])
def proxy_ask():
    """[已弃用] 非流式代理，请改用 /v1/chat/completions (stream=false)"""
    user_id = session.get("user_id")
    password = session.get("password")
    if not user_id or not password:
        return jsonify({"error": "未登录"}), 401

    user_content = request.json.get("content")
    images = request.json.get("images")

    # 构造 content parts
    content_parts = []
    if user_content:
        content_parts.append({"type": "text", "text": user_content})
    if images:
        for img_data in images:
            content_parts.append({"type": "image_url", "image_url": {"url": img_data}})

    if len(content_parts) == 1 and content_parts[0]["type"] == "text":
        msg_content = content_parts[0]["text"]
    elif content_parts:
        msg_content = content_parts
    else:
        msg_content = "(空消息)"

    openai_payload = {
        "model": "mini-timebot",
        "messages": [{"role": "user", "content": msg_content}],
        "stream": False,
        "user": user_id,
        "password": password,
    }

    try:
        r = requests.post(
            LOCAL_OPENAI_COMPLETIONS_URL,
            json=openai_payload,
            headers={"Authorization": f"Bearer {user_id}:{password}"},
            timeout=120,
        )
        if r.status_code == 401:
            session.clear()
            return jsonify(r.json()), 401
        resp = r.json()
        # 从 OpenAI 格式提取 content 转为原格式
        content = resp.get("choices", [{}])[0].get("message", {}).get("content", "")
        return jsonify({"status": "success", "response": content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/proxy_ask_stream", methods=["POST"])
def proxy_ask_stream():
    """[已弃用] 流式代理，请改用 /v1/chat/completions (stream=true)"""
    user_id = session.get("user_id")
    password = session.get("password")
    if not user_id or not password:
        return jsonify({"error": "未登录"}), 401

    data = request.get_json(silent=True)
    if data is None:
        content_len = request.content_length or 0
        print(f"[proxy_ask_stream] ⚠️ JSON 解析失败, content_length={content_len}, content_type={request.content_type}")
        return jsonify({"error": f"请求体解析失败 (大小: {content_len/1024/1024:.1f}MB)"}), 400

    user_content = data.get("content")
    enabled_tools = data.get("enabled_tools")  # None or list
    session_id = data.get("session_id", "default")
    images = data.get("images")  # None or list of base64 strings
    files = data.get("files")    # None or list of {name, content}
    audios = data.get("audios")  # None or list of {base64, name, format}
    print(f"[proxy_ask_stream] 收到请求: text={bool(user_content)}, images={len(images) if images else 0}, files={len(files) if files else 0}, audios={len(audios) if audios else 0}")

    # 构造 OpenAI 格式的 messages content parts
    content_parts = []
    if user_content:
        content_parts.append({"type": "text", "text": user_content})

    # 图片 → image_url parts
    if images:
        for img_data in images:
            content_parts.append({"type": "image_url", "image_url": {"url": img_data}})

    # 音频 → input_audio parts
    if audios:
        for audio in audios:
            content_parts.append({
                "type": "input_audio",
                "input_audio": {
                    "data": audio.get("base64", ""),
                    "format": audio.get("format", "webm"),
                },
            })

    # 文件 → file parts
    if files:
        for f in files:
            fname = f.get("name", "file")
            fcontent = f.get("content", "")
            ftype = f.get("type", "text")
            file_data_uri = fcontent if fcontent.startswith("data:") else f"data:application/octet-stream;base64,{fcontent}"
            content_parts.append({
                "type": "file",
                "file": {"filename": fname, "file_data": file_data_uri},
            })

    # 如果只有纯文本，content 直接用字符串
    if len(content_parts) == 1 and content_parts[0]["type"] == "text":
        msg_content = content_parts[0]["text"]
    elif content_parts:
        msg_content = content_parts
    else:
        msg_content = "(空消息)"

    # 构造 OpenAI 格式请求
    openai_payload = {
        "model": "mini-timebot",
        "messages": [{"role": "user", "content": msg_content}],
        "stream": True,
        "user": user_id,
        "password": password,
        "session_id": session_id,
        "enabled_tools": enabled_tools,
    }

    try:
        r = requests.post(
            LOCAL_OPENAI_COMPLETIONS_URL,
            json=openai_payload,
            headers={"Authorization": f"Bearer {user_id}:{password}"},
            stream=True,
            timeout=120,
        )
        if r.status_code == 401:
            session.clear()
            return jsonify({"error": "认证失败"}), 401
        if r.status_code != 200:
            return jsonify({"error": f"Agent 返回 {r.status_code}"}), r.status_code

        def generate():
            """将 OpenAI SSE 格式转为前端期望的简单 SSE 格式"""
            import json as _json
            for line in r.iter_lines(decode_unicode=True):
                if not line:
                    continue
                if line.startswith("data: [DONE]"):
                    yield "data: [DONE]\n\n"
                    continue
                if line.startswith("data: "):
                    try:
                        chunk = _json.loads(line[6:])
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            # 转换为前端期望的简单 SSE 格式
                            text = content.replace("\\", "\\\\").replace("\n", "\\n")
                            yield f"data: {text}\n\n"
                    except _json.JSONDecodeError:
                        # 透传无法解析的行
                        yield line + "\n\n"

        return Response(
            generate(),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/proxy_cancel", methods=["POST"])
def proxy_cancel():
    """代理取消请求到后端 Agent"""
    user_id = session.get("user_id")
    password = session.get("password")
    if not user_id or not password:
        return jsonify({"error": "未登录"}), 401
    session_id = request.json.get("session_id", "default") if request.is_json else "default"
    try:
        r = requests.post(LOCAL_AGENT_CANCEL_URL, json={"user_id": user_id, "password": password, "session_id": session_id}, timeout=5)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/proxy_tts", methods=["POST"])
def proxy_tts():
    """代理 TTS 请求到后端 Agent，返回 mp3 音频流"""
    user_id = session.get("user_id")
    password = session.get("password")
    if not user_id or not password:
        return jsonify({"error": "未登录"}), 401

    text = request.json.get("text", "")
    voice = request.json.get("voice")
    if not text.strip():
        return jsonify({"error": "文本不能为空"}), 400

    try:
        payload = {"user_id": user_id, "password": password, "text": text}
        if voice:
            payload["voice"] = voice
        r = requests.post(LOCAL_TTS_URL, json=payload, timeout=60)
        if r.status_code != 200:
            return jsonify({"error": f"TTS 服务错误: {r.status_code}"}), r.status_code

        return Response(
            r.content,
            mimetype="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=tts_output.mp3"},
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/proxy_tools")
def proxy_tools():
    """代理获取工具列表请求到后端 Agent"""
    try:
        r = requests.get(LOCAL_TOOLS_URL, headers={"X-Internal-Token": INTERNAL_TOKEN}, timeout=10)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e), "tools": []}), 500

@app.route("/proxy_logout", methods=["POST"])
def proxy_logout():
    session.clear()
    return jsonify({"status": "success"})


@app.route("/proxy_sessions")
def proxy_sessions():
    """代理获取用户会话列表"""
    user_id = session.get("user_id")
    password = session.get("password")
    if not user_id or not password:
        return jsonify({"error": "未登录"}), 401
    try:
        r = requests.post(LOCAL_SESSIONS_URL, json={"user_id": user_id, "password": password}, timeout=15)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_sessions_status")
def proxy_sessions_status():
    """代理获取用户所有 session 的忙碌状态"""
    user_id = session.get("user_id")
    password = session.get("password")
    if not user_id or not password:
        return jsonify({"error": "未登录"}), 401
    try:
        r = requests.post(
            f"http://127.0.0.1:{PORT_AGENT}/sessions_status",
            json={"user_id": user_id, "password": password},
            timeout=5,
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_session_history", methods=["POST"])
def proxy_session_history():
    """代理获取指定会话的历史消息"""
    user_id = session.get("user_id")
    password = session.get("password")
    if not user_id or not password:
        return jsonify({"error": "未登录"}), 401
    sid = request.json.get("session_id", "")
    try:
        r = requests.post(LOCAL_SESSION_HISTORY_URL, json={
            "user_id": user_id, "password": password, "session_id": sid
        }, timeout=15)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_session_status", methods=["POST"])
def proxy_session_status():
    """代理检查会话是否有系统触发的新消息"""
    user_id = session.get("user_id")
    password = session.get("password")
    if not user_id or not password:
        return jsonify({"has_new_messages": False}), 200
    sid = request.json.get("session_id", "") if request.is_json else ""
    try:
        r = requests.post(LOCAL_SESSION_STATUS_URL, json={
            "user_id": user_id, "password": password, "session_id": sid
        }, timeout=5)
        return jsonify(r.json()), r.status_code
    except Exception:
        return jsonify({"has_new_messages": False}), 200


@app.route("/proxy_delete_session", methods=["POST"])
def proxy_delete_session():
    """代理删除会话请求到后端 Agent"""
    user_id = session.get("user_id")
    password = session.get("password")
    if not user_id or not password:
        return jsonify({"error": "未登录"}), 401
    sid = request.json.get("session_id", "") if request.is_json else ""
    try:
        r = requests.post(LOCAL_DELETE_SESSION_URL, json={
            "user_id": user_id, "password": password, "session_id": sid
        }, timeout=15)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===== Group Chat Proxy Routes =====

def _group_auth_headers():
    """构造群聊API的Authorization header"""
    user_id = session.get("user_id")
    password = session.get("password")
    if not user_id or not password:
        return None, None
    return user_id, {"Authorization": f"Bearer {user_id}:{password}"}


@app.route("/proxy_groups", methods=["GET"])
def proxy_list_groups():
    """代理列出用户群聊"""
    uid, headers = _group_auth_headers()
    if not uid:
        return jsonify([]), 200
    try:
        r = requests.get(f"http://127.0.0.1:{PORT_AGENT}/groups", headers=headers, timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_groups", methods=["POST"])
def proxy_create_group():
    """代理创建群聊"""
    uid, headers = _group_auth_headers()
    if not uid:
        return jsonify({"error": "未登录"}), 401
    try:
        headers["Content-Type"] = "application/json"
        r = requests.post(f"http://127.0.0.1:{PORT_AGENT}/groups", json=request.get_json(silent=True), headers=headers, timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_groups/<group_id>", methods=["GET"])
def proxy_get_group(group_id):
    """代理获取群聊详情"""
    uid, headers = _group_auth_headers()
    if not uid:
        return jsonify({"error": "未登录"}), 401
    try:
        r = requests.get(f"http://127.0.0.1:{PORT_AGENT}/groups/{group_id}", headers=headers, timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_groups/<group_id>", methods=["PUT"])
def proxy_update_group(group_id):
    """代理更新群聊"""
    uid, headers = _group_auth_headers()
    if not uid:
        return jsonify({"error": "未登录"}), 401
    try:
        headers["Content-Type"] = "application/json"
        r = requests.put(f"http://127.0.0.1:{PORT_AGENT}/groups/{group_id}", json=request.get_json(silent=True), headers=headers, timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_groups/<group_id>", methods=["DELETE"])
def proxy_delete_group(group_id):
    """代理删除群聊"""
    uid, headers = _group_auth_headers()
    if not uid:
        return jsonify({"error": "未登录"}), 401
    try:
        r = requests.delete(f"http://127.0.0.1:{PORT_AGENT}/groups/{group_id}", headers=headers, timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_groups/<group_id>/messages", methods=["GET"])
def proxy_group_messages(group_id):
    """代理获取群聊消息（支持增量 after_id）"""
    uid, headers = _group_auth_headers()
    if not uid:
        return jsonify({"messages": []}), 200
    try:
        after_id = request.args.get("after_id", "0")
        r = requests.get(
            f"http://127.0.0.1:{PORT_AGENT}/groups/{group_id}/messages",
            params={"after_id": after_id},
            headers=headers, timeout=10,
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_groups/<group_id>/messages", methods=["POST"])
def proxy_post_group_message(group_id):
    """代理发送群聊消息"""
    uid, headers = _group_auth_headers()
    if not uid:
        return jsonify({"error": "未登录"}), 401
    try:
        headers["Content-Type"] = "application/json"
        r = requests.post(
            f"http://127.0.0.1:{PORT_AGENT}/groups/{group_id}/messages",
            json=request.get_json(silent=True),
            headers=headers, timeout=10,
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_groups/<group_id>/mute", methods=["POST"])
def proxy_mute_group(group_id):
    """代理静音群聊"""
    uid, headers = _group_auth_headers()
    if not uid:
        return jsonify({"error": "未登录"}), 401
    try:
        r = requests.post(
            f"http://127.0.0.1:{PORT_AGENT}/groups/{group_id}/mute",
            headers=headers, timeout=10,
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_groups/<group_id>/unmute", methods=["POST"])
def proxy_unmute_group(group_id):
    """代理取消静音群聊"""
    uid, headers = _group_auth_headers()
    if not uid:
        return jsonify({"error": "未登录"}), 401
    try:
        r = requests.post(
            f"http://127.0.0.1:{PORT_AGENT}/groups/{group_id}/unmute",
            headers=headers, timeout=10,
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_groups/<group_id>/mute_status", methods=["GET"])
def proxy_group_mute_status(group_id):
    """代理查询群聊静音状态"""
    uid, headers = _group_auth_headers()
    if not uid:
        return jsonify({"muted": False}), 200
    try:
        r = requests.get(
            f"http://127.0.0.1:{PORT_AGENT}/groups/{group_id}/mute_status",
            headers=headers, timeout=10,
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_groups/<group_id>/sessions", methods=["GET"])
def proxy_group_sessions(group_id):
    """代理获取可加入群聊的sessions"""
    uid, headers = _group_auth_headers()
    if not uid:
        return jsonify({"sessions": []}), 200
    try:
        r = requests.get(
            f"http://127.0.0.1:{PORT_AGENT}/groups/{group_id}/sessions",
            headers=headers, timeout=15,
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"sessions": [], "error": str(e)}), 500


# ===== OASIS Proxy Routes =====

@app.route("/proxy_oasis/topics")
def proxy_oasis_topics():
    """Proxy: list OASIS discussion topics for the logged-in user."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify([]), 200
    try:
        print(f"[OASIS Proxy] Fetching topics from {OASIS_BASE_URL}/topics for user={user_id}")
        r = requests.get(f"{OASIS_BASE_URL}/topics", params={"user_id": user_id}, timeout=10)
        print(f"[OASIS Proxy] Response status: {r.status_code}, count: {len(r.json()) if r.text else 0}")
        return jsonify(r.json()), r.status_code
    except Exception as e:
        print(f"[OASIS Proxy] Error fetching topics: {e}")
        return jsonify([]), 200  # Return empty list on error


@app.route("/proxy_oasis/topics/<topic_id>")
def proxy_oasis_topic_detail(topic_id):
    """Proxy: get full detail of a specific OASIS discussion."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "未登录"}), 401
    try:
        url = f"{OASIS_BASE_URL}/topics/{topic_id}"
        print(f"[OASIS Proxy] Fetching topic detail from {url} for user={user_id}")
        r = requests.get(url, params={"user_id": user_id}, timeout=10)
        print(f"[OASIS Proxy] Detail response status: {r.status_code}")
        return jsonify(r.json()), r.status_code
    except Exception as e:
        print(f"[OASIS Proxy] Error fetching topic detail: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_oasis/topics/<topic_id>/stream")
def proxy_oasis_topic_stream(topic_id):
    """Proxy: SSE stream for real-time OASIS discussion updates."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "未登录"}), 401
    try:
        r = requests.get(
            f"{OASIS_BASE_URL}/topics/{topic_id}/stream",
            params={"user_id": user_id},
            stream=True, timeout=300,
        )
        if r.status_code != 200:
            return jsonify({"error": f"OASIS returned {r.status_code}"}), r.status_code

        def generate():
            for line in r.iter_lines(decode_unicode=True):
                if line:
                    yield line + "\n\n"

        return Response(
            generate(),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_oasis/experts")
def proxy_oasis_experts():
    """Proxy: list all OASIS expert agents."""
    user_id = session.get("user_id", "")
    try:
        r = requests.get(f"{OASIS_BASE_URL}/experts", params={"user_id": user_id}, timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_oasis/topics/<topic_id>/cancel", methods=["POST"])
def proxy_oasis_cancel_topic(topic_id):
    """Proxy: force-cancel a running OASIS discussion."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "未登录"}), 401
    try:
        r = requests.delete(f"{OASIS_BASE_URL}/topics/{topic_id}", params={"user_id": user_id}, timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_oasis/topics/<topic_id>/purge", methods=["POST"])
def proxy_oasis_purge_topic(topic_id):
    """Proxy: permanently delete an OASIS discussion record."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "未登录"}), 401
    try:
        r = requests.post(f"{OASIS_BASE_URL}/topics/{topic_id}/purge", params={"user_id": user_id}, timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_oasis/topics", methods=["DELETE"])
def proxy_oasis_purge_all_topics():
    """Proxy: delete all OASIS topics for the current user."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "未登录"}), 401
    try:
        r = requests.delete(f"{OASIS_BASE_URL}/topics", params={"user_id": user_id}, timeout=30)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ──────────────────────────────────────────────────────────────
# Visual Orchestration – proxy endpoints
# ──────────────────────────────────────────────────────────────
import sys as _sys, math as _math, re as _re, yaml as _yaml

# Import expert pool & conversion helpers from visual/main.py
_VISUAL_DIR = os.path.join(root_dir, "visual")
if _VISUAL_DIR not in _sys.path:
    _sys.path.insert(0, _VISUAL_DIR)

try:
    from main import (
        DEFAULT_EXPERTS as _VIS_EXPERTS,
        TAG_EMOJI as _VIS_TAG_EMOJI,
        layout_to_yaml as _vis_layout_to_yaml,
        _build_llm_prompt as _vis_build_llm_prompt,
        _extract_yaml_from_response as _vis_extract_yaml,
        _validate_generated_yaml as _vis_validate_yaml,
    )
except Exception:
    # Fallback: define minimal versions if visual module unavailable
    _VIS_EXPERTS = []
    _VIS_TAG_EMOJI = {}
    _vis_layout_to_yaml = None
    _vis_build_llm_prompt = None
    _vis_extract_yaml = None
    _vis_validate_yaml = None


@app.route("/proxy_visual/experts", methods=["GET"])
def proxy_visual_experts():
    """Return available expert pool for orchestration canvas (public + user custom)."""
    user_id = session.get("user_id", "")
    # Fetch full expert list from OASIS server (public + user custom)
    all_experts = []
    try:
        r = requests.get(f"{OASIS_BASE_URL}/experts", params={"user_id": user_id}, timeout=5)
        if r.ok:
            all_experts = r.json().get("experts", [])
    except Exception:
        pass

    # Fallback to static list if OASIS unavailable
    if not all_experts:
        all_experts = [{**e, "source": "public"} for e in _VIS_EXPERTS]

    result = []
    for e in all_experts:
        emoji = _VIS_TAG_EMOJI.get(e.get("tag", ""), "⭐")
        if e.get("source") == "custom":
            emoji = "🛠️"
        result.append({**e, "emoji": emoji})
    return jsonify(result)


@app.route("/proxy_visual/experts/custom", methods=["POST"])
def proxy_visual_add_custom_expert():
    """Add a custom expert via OASIS server."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "未登录"}), 401
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400
    try:
        r = requests.post(
            f"{OASIS_BASE_URL}/experts/user",
            json={"user_id": user_id, **data},
            timeout=10,
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_visual/experts/custom/<tag>", methods=["DELETE"])
def proxy_visual_delete_custom_expert(tag):
    """Delete a custom expert via OASIS server."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "未登录"}), 401
    try:
        r = requests.delete(
            f"{OASIS_BASE_URL}/experts/user/{tag}",
            params={"user_id": user_id},
            timeout=10,
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_visual/generate-yaml", methods=["POST"])
def proxy_visual_generate_yaml():
    """Convert canvas layout to OASIS YAML (rule-based)."""
    data = request.get_json()
    if not data or not _vis_layout_to_yaml:
        return jsonify({"error": "No data or visual module unavailable"}), 400
    try:
        yaml_out = _vis_layout_to_yaml(data)
        return jsonify({"yaml": yaml_out})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_visual/agent-generate-yaml", methods=["POST"])
def proxy_visual_agent_generate_yaml():
    """Build prompt + send to main agent using session credentials → get YAML."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400

    user_id = session.get("user_id")
    password = session.get("password")
    if not user_id or not password:
        return jsonify({"error": "Not logged in"}), 401

    try:
        prompt = _vis_build_llm_prompt(data) if _vis_build_llm_prompt else "Error: visual module unavailable"

        # Call main agent with user credentials
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {user_id}:{password}",
        }
        payload = {
            "model": "mini-timebot",
            "messages": [
                {"role": "system", "content": (
                    "You are a YAML schedule generator for the OASIS expert orchestration engine. "
                    "Output ONLY valid YAML, no markdown fences, no explanations, no commentary. "
                    "The YAML must start with 'version: 1' and contain a 'plan:' section."
                )},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "session_id": data.get("target_session_id") or "visual_orchestrator",
            "temperature": 0.3,
        }
        resp = requests.post(LOCAL_OPENAI_COMPLETIONS_URL, json=payload, headers=headers, timeout=60)
        if resp.status_code != 200:
            return jsonify({"prompt": prompt, "error": f"Agent returned HTTP {resp.status_code}: {resp.text[:500]}", "agent_yaml": None})

        result = resp.json()
        agent_reply = ""
        try:
            agent_reply = result["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            agent_reply = str(result)

        agent_yaml = _vis_extract_yaml(agent_reply) if _vis_extract_yaml else agent_reply
        validation = _vis_validate_yaml(agent_yaml) if _vis_validate_yaml else {"valid": False, "error": "validator unavailable"}

        # Auto-save valid YAML to user's oasis/yaml directory
        saved_path = None
        if validation.get("valid"):
            try:
                import time as _time
                yaml_dir = os.path.join(root_dir, "data", "user_files", user_id, "oasis", "yaml")
                os.makedirs(yaml_dir, exist_ok=True)
                fname = data.get("save_name") or f"orch_{_time.strftime('%Y%m%d_%H%M%S')}"
                if not fname.endswith((".yaml", ".yml")):
                    fname += ".yaml"
                fpath = os.path.join(yaml_dir, fname)
                with open(fpath, "w", encoding="utf-8") as _yf:
                    _yf.write(f"# Auto-generated from visual orchestrator\n{agent_yaml}")
                saved_path = fname
            except Exception as save_err:
                saved_path = f"save_error: {save_err}"

        return jsonify({"prompt": prompt, "agent_yaml": agent_yaml, "agent_reply_raw": agent_reply, "validation": validation, "saved_file": saved_path})

    except requests.exceptions.ConnectionError:
        prompt = _vis_build_llm_prompt(data) if _vis_build_llm_prompt else ""
        return jsonify({"prompt": prompt, "error": "Cannot connect to main agent. Is mainagent.py running?", "agent_yaml": None})
    except requests.exceptions.Timeout:
        prompt = _vis_build_llm_prompt(data) if _vis_build_llm_prompt else ""
        return jsonify({"prompt": prompt, "error": "Agent request timed out (60s).", "agent_yaml": None})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy_visual/save-layout", methods=["POST"])
def proxy_visual_save_layout():
    """Save canvas layout JSON for the current user."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400
    save_dir = os.path.join(root_dir, "data", "visual_layouts", user_id)
    os.makedirs(save_dir, exist_ok=True)
    name = data.get("name", "untitled")
    safe = "".join(c for c in name if c.isalnum() or c in "-_ ").strip() or "untitled"
    import json as _json
    with open(os.path.join(save_dir, f"{safe}.json"), "w", encoding="utf-8") as f:
        _json.dump(data, f, ensure_ascii=False, indent=2)
    return jsonify({"saved": True})


@app.route("/proxy_visual/load-layouts", methods=["GET"])
def proxy_visual_load_layouts():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify([])
    save_dir = os.path.join(root_dir, "data", "visual_layouts", user_id)
    if not os.path.isdir(save_dir):
        return jsonify([])
    return jsonify([f[:-5] for f in os.listdir(save_dir) if f.endswith(".json")])


@app.route("/proxy_visual/load-layout/<name>", methods=["GET"])
def proxy_visual_load_layout(name):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401
    safe = "".join(c for c in name if c.isalnum() or c in "-_ ").strip()
    path = os.path.join(root_dir, "data", "visual_layouts", user_id, f"{safe}.json")
    if not os.path.isfile(path):
        return jsonify({"error": "Not found"}), 404
    import json as _json
    with open(path, "r", encoding="utf-8") as f:
        return jsonify(_json.load(f))


@app.route("/proxy_visual/delete-layout/<name>", methods=["DELETE"])
def proxy_visual_delete_layout(name):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401
    safe = "".join(c for c in name if c.isalnum() or c in "-_ ").strip()
    path = os.path.join(root_dir, "data", "visual_layouts", user_id, f"{safe}.json")
    if os.path.isfile(path):
        os.remove(path)
        return jsonify({"deleted": True})
    return jsonify({"error": "Not found"}), 404


@app.route("/proxy_visual/sessions-status", methods=["GET"])
def proxy_visual_sessions_status():
    """Return all sessions with their running status for the canvas display."""
    user_id = session.get("user_id")
    password = session.get("password")
    if not user_id or not password:
        return jsonify([])
    try:
        r = requests.post(LOCAL_SESSIONS_URL, json={"user_id": user_id, "password": password}, timeout=10)
        if r.status_code != 200:
            return jsonify([])
        sessions_data = r.json()
        return jsonify(sessions_data if isinstance(sessions_data, list) else [])
    except Exception:
        return jsonify([])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT_FRONTEND", "51209")), debug=False, threaded=True)
