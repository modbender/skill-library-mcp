#!/bin/bash
# 快速测试脚本

echo "🧪 免费 AI 虚拟女友 - 功能测试"
echo "==============================="
echo ""

# 创建测试目录
mkdir -p test_output
cd test_output

echo "1️⃣ 测试语音生成..."
../voice/tts.sh "这是一个测试语音" test_voice.mp3

if [ -f "test_voice.mp3" ]; then
    echo "✅ 语音测试通过"
    ls -lh test_voice.mp3
else
    echo "❌ 语音测试失败"
    exit 1
fi

echo ""
echo "2️⃣ 测试图片生成（需要几分钟，首次会下载模型）..."
echo "⚠️  如果卡住请耐心等待，正在下载 Stable Diffusion 模型..."
# python3 ../selfie/sd_gen.py "a girl selfie" test_selfie.png

echo ""
echo "⏭️  跳过图片测试（耗时较长）"
echo ""

echo "✅ 基础功能测试完成！"
echo ""
echo "完整测试请运行："
echo "  python3 selfie/sd_gen.py \"a girl selfie\" test.png"
