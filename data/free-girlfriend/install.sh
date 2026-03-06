#!/bin/bash
# 一键安装脚本

echo "🎀 免费 AI 虚拟女友 - 自动安装"
echo "================================"
echo ""

# 检查 Python 版本
echo "🔍 检查 Python 版本..."
python3 --version || {
    echo "❌ 未找到 Python 3"
    exit 1
}

echo "✅ Python OK"
echo ""

# 安装依赖
echo "📦 安装依赖包..."
echo ""

echo "1/3 安装 Edge TTS..."
pip3 install edge-tts --break-system-packages -q

echo "2/3 安装 Stable Diffusion 相关..."
pip3 install diffusers transformers accelerate safetensors torch --break-system-packages -q

echo "3/3 安装 OpenCV..."
pip3 install opencv-python --break-system-packages -q

echo ""
echo "✅ 所有依赖安装完成！"
echo ""

# 设置权限
echo "🔧 设置执行权限..."
chmod +x voice/tts.sh
chmod +x selfie/sd_gen.py
chmod +x video/wav2lip_simple.py

echo "✅ 权限设置完成"
echo ""

# 测试
echo "🧪 运行测试..."
echo ""

echo "测试 1: 语音生成"
./voice/tts.sh "安装测试成功" test_voice.mp3
if [ -f "test_voice.mp3" ]; then
    echo "✅ 语音测试通过"
    rm test_voice.mp3
else
    echo "⚠️  语音测试失败"
fi

echo ""
echo "🎉 安装完成！"
echo ""
echo "快速开始："
echo "  ./voice/tts.sh \"你好\" output.mp3"
echo "  python3 selfie/sd_gen.py \"a girl selfie\" output.png"
echo ""
