#!/bin/bash
# Qwen Code 代码审查示例
# 使用前请确保已安装 Qwen Code CLI 并完成认证

set -e

echo "=== Qwen Code 代码审查示例 ==="

# 创建示例代码文件
cat > /tmp/sample_code.py << 'EOF'
import requests

def fetch_user_data(user_id):
    url = f"http://api.example.com/users/{user_id}"
    response = requests.get(url)
    return response.json()

def process_users(user_ids):
    results = []
    for id in user_ids:
        data = fetch_user_data(id)
        results.append(data)
    return results

# 使用示例
users = process_users([1, 2, 3, 4, 5])
print(users)
EOF

echo "示例代码已创建：/tmp/sample_code.py"
echo ""

# 审查示例 1: 基础审查
echo "=== 审查 1: 基础代码审查 ==="
qwen -p "审查这个 Python 文件，指出代码质量问题、安全漏洞和改进建议" /tmp/sample_code.py

# 审查示例 2: 安全性审查
echo ""
echo "=== 审查 2: 安全性专项审查 ==="
qwen -p "从安全角度审查这段代码，重点关注：1) 输入验证 2) 错误处理 3) 敏感信息泄露" /tmp/sample_code.py

# 审查示例 3: 性能审查
echo ""
echo "=== 审查 3: 性能专项审查 ==="
qwen -p "分析这段代码的性能问题，并提供优化建议" /tmp/sample_code.py

# 审查示例 4: 生成修复建议
echo ""
echo "=== 审查 4: 生成修复代码 ==="
qwen -p "根据上述问题，生成修复后的完整代码版本" /tmp/sample_code.py

# 清理
rm /tmp/sample_code.py

echo ""
echo "=== 代码审查示例完成 ==="
