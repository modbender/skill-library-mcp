#!/bin/bash
# GitCode API 辅助脚本
# 用于 CANN 代码审查技能

# 配置
API_TOKEN="5_EtXLq3jGyQvb6tWwrN3byz"
API_BASE="https://api.gitcode.com/api/v5"

# 通用请求函数
api_request() {
    local method=$1
    local endpoint=$2
    local data=$3
    
    if [ -z "$data" ]; then
        curl -s -X "$method" \
            -H "Authorization: Bearer $API_TOKEN" \
            "${API_BASE}${endpoint}"
    else
        curl -s -X "$method" \
            -H "Authorization: Bearer $API_TOKEN" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "${API_BASE}${endpoint}"
    fi
}

# 获取 PR 信息
get_pr() {
    local owner=$1
    local repo=$2
    local pr_number=$3
    
    api_request "GET" "/repos/${owner}/${repo}/pulls/${pr_number}"
}

# 获取 PR 文件变更
get_pr_files() {
    local owner=$1
    local repo=$2
    local pr_number=$3
    
    api_request "GET" "/repos/${owner}/${repo}/pulls/${pr_number}/files"
}

# 发布 PR 评论
post_pr_comment() {
    local owner=$1
    local repo=$2
    local pr_number=$3
    local body=$4
    
    # 转义 JSON 字符串
    local escaped_body=$(echo "$body" | python3 -c "import sys, json; print(json.dumps(sys.stdin.read()))")
    
    api_request "POST" "/repos/${owner}/${repo}/pulls/${pr_number}/comments" "{\"body\":${escaped_body}}"
}

# 获取开放的 PR 列表
get_open_prs() {
    local owner=$1
    local repo=$2
    
    api_request "GET" "/repos/${owner}/${repo}/pulls?state=opened"
}

# 使用示例
if [ "$1" = "get-pr" ]; then
    get_pr "$2" "$3" "$4"
elif [ "$1" = "get-files" ]; then
    get_pr_files "$2" "$3" "$4"
elif [ "$1" = "post-comment" ]; then
    post_pr_comment "$2" "$3" "$4" "$5"
elif [ "$1" = "list-prs" ]; then
    get_open_prs "$2" "$3"
else
    echo "用法:"
    echo "  $0 get-pr <owner> <repo> <pr_number>"
    echo "  $0 get-files <owner> <repo> <pr_number>"
    echo "  $0 post-comment <owner> <repo> <pr_number> <comment>"
    echo "  $0 list-prs <owner> <repo>"
    echo ""
    echo "示例:"
    echo "  $0 get-pr cann runtime 628"
    echo "  $0 get-files cann runtime 628"
    echo "  $0 post-comment cann runtime 628 'LGTM! 代码质量良好。'"
    echo "  $0 list-prs cann runtime"
fi
