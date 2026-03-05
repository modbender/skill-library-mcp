#!/bin/bash
# Voice Chat Bridge - 初始化脚本

echo "🎙️  Voice Chat Bridge 初始化..."

# 创建目录
mkdir -p ~/.openclaw/workspace/voice_output
touch ~/.openclaw/workspace/voice_output/.gitkeep

# 创建配置文件
CONFIG_FILE="~/.openclaw/workspace/voice_config.json"

if [ ! -f "$CONFIG_FILE" ]; then
cat > ~/.openclaw/workspace/voice_config.json << 'EOF'
{
  "domain": "https://your-domain.com",
  "local_port": 8765,
  "voice": "zh-CN-XiaoxiaoNeural",
  "transcribe_tool": "hear",
  "output_format": "mp3"
}
EOF
    echo "✅ 配置文件已创建: ~/.openclaw/workspace/voice_config.json"
    echo "⚠️  请编辑配置文件，填入你的域名"
else
    echo "ℹ️  配置文件已存在"
fi

# 检查依赖
echo ""
echo "🔍 检查依赖..."

# 检查 ffmpeg
if command -v ffmpeg >/dev/null 2>&1; then
    echo "✅ ffmpeg 已安装"
else
    echo "❌ ffmpeg 未安装，请运行: brew install ffmpeg"
fi

# 检查 edge-tts
if command -v edge-tts >/dev/null 2>&1 || [ -f "/Library/Frameworks/Python.framework/Versions/3.13/bin/edge-tts" ]; then
    echo "✅ edge-tts 已安装"
else
    echo "❌ edge-tts 未安装，请运行: pip3 install edge-tts"
fi

# 检查 hear
if [ -f "$HOME/.local/bin/hear" ]; then
    echo "✅ hear 已安装"
else
    echo "⚠️  hear 未安装（可选），语音转文字将需要其他方案"
fi

echo ""
echo "🚀 初始化完成！"
echo ""
echo "下一步:"
echo "1. 编辑 ~/.openclaw/workspace/voice_config.json，填入你的域名"
echo "2. 启动语音服务器: python3 scripts/voice_server.py"
echo "3. 启动 Cloudflare Tunnel"
echo ""
