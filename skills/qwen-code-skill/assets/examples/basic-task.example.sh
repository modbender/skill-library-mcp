#!/bin/bash
# Qwen Code 基本任务执行示例
# 使用前请确保已安装 Qwen Code CLI 并完成认证

set -e

echo "=== Qwen Code 基本任务示例 ==="

# 示例 1: 创建简单项目
echo "示例 1: 创建 Flask API 项目"
qwen -p "创建一个简单的 Flask API，包含 /health 和 /api/users 端点"

# 示例 2: 代码解释
echo "示例 2: 解释代码"
qwen -p "解释这段代码的功能和实现思路" << 'EOF'
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
EOF

# 示例 3: 代码重构
echo "示例 3: 代码重构"
qwen -p "重构这个函数，提高可读性和性能" << 'EOF'
function processData(d) {
    let r = [];
    for(let i=0; i<d.length; i++) {
        if(d[i].active) {
            r.push(d[i].value * 2);
        }
    }
    return r;
}
EOF

# 示例 4: 生成单元测试
echo "示例 4: 生成单元测试"
qwen -p "为这个函数生成 Jest 单元测试" << 'EOF'
export function add(a, b) {
    return a + b;
}
EOF

# 示例 5: 代码审查
echo "示例 5: 代码审查"
qwen -p "审查这段代码，指出潜在问题和改进建议" << 'EOF'
async function fetchData(url) {
    const response = await fetch(url);
    const data = await response.json();
    return data;
}
EOF

echo "=== 示例执行完成 ==="
