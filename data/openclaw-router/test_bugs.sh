#!/bin/bash
# Router Skill - 完整 Bug 测试脚本
# 版本：3.0.0

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║       OpenClaw Router Skill v3.0 - 完整 Bug 测试          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

TESTS_PASSED=0
TESTS_FAILED=0

# 测试函数
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -n "测试：$test_name ... "
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo "✅ 通过"
        ((TESTS_PASSED++))
    else
        echo "❌ 失败"
        ((TESTS_FAILED++))
    fi
}

# Bug 测试 1: 模块导入
echo "══════════════════════════════════════════════════════════"
echo "Bug 测试组 1: 模块导入"
echo "══════════════════════════════════════════════════════════"
run_test "src 模块导入" "python3 -c 'from src import *'"
run_test "detector 导入" "python3 -c 'from src.detector import EnvironmentDetector'"
run_test "recommender 导入" "python3 -c 'from src.recommender import ConfigRecommender'"
run_test "router 导入" "python3 -c 'from src.router import ModelRouter'"
run_test "config_manager 导入" "python3 -c 'from src.config_manager import ConfigManager'"
run_test "i18n 导入" "python3 -c 'from src.i18n import I18n'"
echo ""

# Bug 测试 2: 环境检测
echo "══════════════════════════════════════════════════════════"
echo "Bug 测试组 2: 环境检测"
echo "══════════════════════════════════════════════════════════"
run_test "Ollama 检测" "python3 -c 'from src.detector import EnvironmentDetector; d = EnvironmentDetector(); r = d.detect_ollama(); assert \"installed\" in r'"
run_test "DashScope 检测" "python3 -c 'from src.detector import EnvironmentDetector; d = EnvironmentDetector(); r = d.detect_dashscope(); assert \"configured\" in r'"
run_test "OpenAI 检测" "python3 -c 'from src.detector import EnvironmentDetector; d = EnvironmentDetector(); r = d.detect_openai(); assert \"configured\" in r'"
run_test "系统资源检测" "python3 -c 'from src.detector import EnvironmentDetector; d = EnvironmentDetector(); r = d.detect_system(); assert \"memory_gb\" in r'"
echo ""

# Bug 测试 3: 配置推荐
echo "══════════════════════════════════════════════════════════"
echo "Bug 测试组 3: 配置推荐"
echo "══════════════════════════════════════════════════════════"
run_test "纯本地推荐" "python3 -c 'from src.recommender import ConfigRecommender; r = ConfigRecommender(); c = r.generate_recommendation({\"ollama\": {\"installed\": True, \"models\": [\"qwen2.5:14b\"]}, \"dashscope\": {\"configured\": False}, \"openai\": {\"configured\": False}, \"anthropic\": {\"configured\": False}, \"system\": {}}); assert c[\"primary_model\"][\"location\"] == \"local\"'"
run_test "混合部署推荐" "python3 -c 'from src.recommender import ConfigRecommender; r = ConfigRecommender(); c = r.generate_recommendation({\"ollama\": {\"installed\": True, \"models\": [\"qwen2.5:14b\"]}, \"dashscope\": {\"configured\": True}, \"openai\": {\"configured\": False}, \"anthropic\": {\"configured\": False}, \"system\": {}}); assert c[\"primary_model\"][\"location\"] == \"local\"'"
run_test "纯云端推荐" "python3 -c 'from src.recommender import ConfigRecommender; r = ConfigRecommender(); c = r.generate_recommendation({\"ollama\": {\"installed\": False, \"models\": []}, \"dashscope\": {\"configured\": True}, \"openai\": {\"configured\": False}, \"anthropic\": {\"configured\": False}, \"system\": {}}); assert c[\"primary_model\"][\"location\"] == \"cloud\"'"
echo ""

# Bug 测试 4: 模型路由
echo "══════════════════════════════════════════════════════════"
echo "Bug 测试组 4: 模型路由"
echo "══════════════════════════════════════════════════════════"
run_test "高分路由 (5.0)" "python3 -c 'from src.router import ModelRouter; r = ModelRouter({\"primary_model\": {\"id\": \"test\"}, \"thresholds\": {\"auto_pass\": 3.5}}); result = r.select_model(5.0); assert result[\"selected\"]'"
run_test "边界路由 (3.2)" "python3 -c 'from src.router import ModelRouter; r = ModelRouter({\"primary_model\": {\"id\": \"test\"}, \"verifier_model\": {\"id\": \"test\"}, \"thresholds\": {\"auto_pass\": 3.5, \"verify_min\": 3.0, \"verify_max\": 3.5}}); result = r.select_model(3.2); assert result[\"requires_verification\"]'"
run_test "低分路由 (2.0)" "python3 -c 'from src.router import ModelRouter; r = ModelRouter({\"primary_model\": {\"id\": \"test\"}, \"expert_model\": {\"id\": \"test\"}, \"thresholds\": {\"escalate_below\": 3.0}}); result = r.select_model(2.0); assert result[\"selected\"]'"
run_test "标签路由 [BEST]" "python3 -c 'from src.router import ModelRouter; r = ModelRouter({\"expert_model\": {\"id\": \"test\"}}); result = r.select_model(4.0, user_tags=[\"[BEST]\"]); assert result[\"selected\"]'"
echo ""

# Bug 测试 5: 配置管理
echo "══════════════════════════════════════════════════════════"
echo "Bug 测试组 5: 配置管理"
echo "══════════════════════════════════════════════════════════"
run_test "配置保存" "python3 -c 'from src.config_manager import ConfigManager; import tempfile; import os; cm = ConfigManager(tempfile.mktemp()); c = {\"version\": \"3.0.0\"}; assert cm.save_config(c)'"
run_test "配置加载" "python3 -c 'from src.config_manager import ConfigManager; import tempfile; cm = ConfigManager(tempfile.mktemp()); cm.save_config({\"version\": \"3.0.0\"}); c = cm.load_config(); assert c[\"version\"] == \"3.0.0\"'"
run_test "配置验证" "python3 -c 'from src.config_manager import ConfigManager; cm = ConfigManager(); v = cm.validate_config({}); assert \"valid\" in v'"
run_test "阈值获取" "python3 -c 'from src.config_manager import ConfigManager; cm = ConfigManager(); t = cm.get_threshold(\"auto_pass\"); assert isinstance(t, float)'"
echo ""

# Bug 测试 6: 国际化
echo "══════════════════════════════════════════════════════════"
echo "Bug 测试组 6: 国际化 (i18n)"
echo "══════════════════════════════════════════════════════════"
run_test "英文加载" "python3 -c 'from src.i18n import I18n; i = I18n(\"en\"); assert i.get(\"welcome\") == \"Welcome to Router Skill\"'"
run_test "中文加载" "python3 -c 'from src.i18n import I18n; i = I18n(\"zh\"); assert \"欢迎\" in i.get(\"welcome\")'"
run_test "参数格式化" "python3 -c 'from src.i18n import I18n; i = I18n(\"zh\"); t = i.get(\"ollama_installed\", count=5); assert \"5\" in t'"
run_test "语言切换" "python3 -c 'from src.i18n import I18n; i = I18n(); i.set_language(\"en\"); assert i.language == \"en\"'"
run_test "自动检测" "python3 -c 'from src.i18n import I18n; i = I18n(); assert i.language in [\"en\", \"zh\"]'"
echo ""

# Bug 测试 7: 边界情况
echo "══════════════════════════════════════════════════════════"
echo "Bug 测试组 7: 边界情况"
echo "══════════════════════════════════════════════════════════"
run_test "无模型推荐" "python3 -c 'from src.recommender import ConfigRecommender; r = ConfigRecommender(); c = r.generate_recommendation({\"ollama\": {\"installed\": False, \"models\": []}, \"dashscope\": {\"configured\": False}, \"openai\": {\"configured\": False}, \"anthropic\": {\"configured\": False}, \"system\": {}}); assert c.get(\"primary_model\") is None'"
run_test "负分路由" "python3 -c 'from src.router import ModelRouter; r = ModelRouter({\"expert_model\": {\"id\": \"test\"}}); result = r.select_model(-1.0); assert result[\"selected\"]'"
run_test "超高分路由" "python3 -c 'from src.router import ModelRouter; r = ModelRouter({\"primary_model\": {\"id\": \"test\"}}); result = r.select_model(10.0); assert result[\"selected\"]'"
run_test "空配置验证" "python3 -c 'from src.config_manager import ConfigManager; cm = ConfigManager(); v = cm.validate_config(None); assert not v[\"valid\"]'"
echo ""

# 总结
echo "══════════════════════════════════════════════════════════"
echo "测试结果总结"
echo "══════════════════════════════════════════════════════════"
echo ""
echo "通过：$TESTS_PASSED"
echo "失败：$TESTS_FAILED"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║              ✅ 所有测试通过！无 Bug 发现！                ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    exit 0
else
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║              ⚠️  发现 $TESTS_FAILED 个失败测试！                    ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    exit 1
fi
