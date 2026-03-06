#!/bin/bash
# Router Skill 测试脚本
# 用途：快速验证所有功能

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║          OpenClaw Router Skill v3.0 测试套件              ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 测试 1: 模块导入
echo "测试 1: 模块导入..."
python3 -c "
from src.detector import EnvironmentDetector
from src.recommender import ConfigRecommender
from src.router import ModelRouter
from src.config_manager import ConfigManager
print('✅ 所有模块导入成功')
" || { echo "❌ 模块导入失败"; exit 1; }
echo ""

# 测试 2: 环境检测
echo "测试 2: 环境检测..."
python3 << 'PYTHON_EOF'
from src.detector import EnvironmentDetector
detector = EnvironmentDetector()
results = detector.run_full_detection()

print(f"   Ollama: {'✅ 已安装' if results['ollama']['installed'] else '❌ 未安装'}")
print(f"   阿里云：{'✅ 已配置' if results['dashscope']['configured'] else '❌ 未配置'}")
print(f"   OpenAI: {'✅ 已配置' if results['openai']['configured'] else '❌ 未配置'}")
print(f"   Anthropic: {'✅ 已配置' if results['anthropic']['configured'] else '❌ 未配置'}")
print(f"   系统：{results['system']['memory_gb']}GB 内存，{results['system']['cpu_cores']} 核心")
PYTHON_EOF
echo ""

# 测试 3: 配置推荐
echo "测试 3: 配置推荐..."
python3 << 'PYTHON_EOF'
from src.detector import EnvironmentDetector
from src.recommender import ConfigRecommender

detector = EnvironmentDetector()
results = detector.run_full_detection()
recommender = ConfigRecommender()
config = recommender.generate_recommendation(results)

if config.get('primary_model'):
    print(f"   ✅ 主路由：{config['primary_model']['id']}")
if config.get('verifier_model'):
    print(f"   ✅ 验证器：{config['verifier_model']['id']}")
if config.get('expert_model'):
    print(f"   ✅ 专家：{config['expert_model']['id']}")
print(f"   ✅ 阈值：{config['thresholds']['mode']}")
print(f"   ✅ 预算：¥{config['budget_suggestion']['monthly']}/月")
PYTHON_EOF
echo ""

# 测试 4: 路由选择
echo "测试 4: 路由选择..."
python3 << 'PYTHON_EOF'
from src.router import ModelRouter

# 模拟配置
config = {
    "primary_model": {"id": "qwen2.5:14b", "location": "local", "cost_per_1k": 0},
    "verifier_model": {"id": "dashscope/qwen3.5-plus", "location": "cloud", "cost_per_1k": 0.002},
    "expert_model": {"id": "dashscope/qwen3-max", "location": "cloud", "cost_per_1k": 0.04},
    "thresholds": {"auto_pass": 3.5, "verify_min": 3.0, "verify_max": 3.5, "escalate_below": 3.0}
}

router = ModelRouter(config)

# 测试不同得分
test_scores = [5.0, 4.0, 3.2, 2.5, 1.0]
for score in test_scores:
    result = router.select_model(score)
    print(f"   {score}分 → {result['model']['id'] if result.get('model') else 'N/A'}")
PYTHON_EOF
echo ""

# 测试 5: 配置保存
echo "测试 5: 配置保存..."
python3 << 'PYTHON_EOF'
from src.config_manager import ConfigManager
import tempfile
import os

# 创建临时配置
config = {
    "version": "3.0.0",
    "models": {
        "primary": {"id": "qwen2.5:14b", "location": "local"}
    },
    "thresholds": {"auto_pass": 3.5}
}

# 测试保存和加载
with tempfile.TemporaryDirectory() as tmpdir:
    config_file = os.path.join(tmpdir, "test_config.yaml")
    cm = ConfigManager(config_file)
    
    if cm.save_config(config):
        print("   ✅ 配置保存成功")
    else:
        print("   ❌ 配置保存失败")
        exit(1)
    
    loaded = cm.load_config()
    if loaded and loaded.get("version") == "3.0.0":
        print("   ✅ 配置加载成功")
    else:
        print("   ❌ 配置加载失败")
        exit(1)
    
    validation = cm.validate_config()
    if validation["valid"]:
        print("   ✅ 配置验证通过")
    else:
        print(f"   ❌ 配置验证失败：{validation['errors']}")
        exit(1)
PYTHON_EOF
echo ""

# 总结
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                    测试完成！                            ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "所有测试通过！Router Skill 已准备就绪。"
echo ""
