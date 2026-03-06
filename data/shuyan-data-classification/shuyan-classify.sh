#!/bin/bash
# 数安云智数据分类分级同步接口
# 用法: shuyan-classify.sh <command> [args...]

API_KEY="${SHUYAN_API_KEY:-sk-secret-key}"
API_URL="${SHUYAN_API_URL:-http://localhost:8080}"
ENDPOINT="/api/llm_infer_zh_and_cls_and_type_v2_batchdata_sync"

case "$1" in
  classify)
    shift
    if [ $# -lt 2 ]; then
      echo "用法: shuyan-classify.sh classify <colNameCh> <colNameComment> [colNameEn] [projectName]"
      exit 1
    fi
    colNameCh="$1"
    colNameComment="$2"
    colNameEn="${3:-}"
    projectName="${4:-default}"
    
    DATA=$(cat <<EOF
[
  {
    "colNameCh": "$colNameCh",
    "colNameComment": "$colNameComment",
    "colNameEn": "$colNameEn",
    "projectName": "$projectName",
    "standardCode": "llm_infer_zh_and_cls_and_type_v2_test",
    "sensitivityLevelRedisKey": "fenji_standard"
  }
]
EOF
)
    curl -s -X POST "${API_URL}${ENDPOINT}" \
      -H "Authorization: Bearer ${API_KEY}" \
      -H "Content-Type: application/json" \
      -d "$DATA"
    ;;
    
  classify-batch)
    shift
    if [ $# -lt 1 ]; then
      echo "用法: shuyan-classify.sh classify-batch <json_file>"
      exit 1
    fi
    JSON_FILE="$1"
    if [ ! -f "$JSON_FILE" ]; then
      echo "错误: 文件不存在: $JSON_FILE"
      exit 1
    fi
    curl -s -X POST "${API_URL}${ENDPOINT}" \
      -H "Authorization: Bearer ${API_KEY}" \
      -H "Content-Type: application/json" \
      -d @"$JSON_FILE"
    ;;
    
  test)
    curl -s -X POST "${API_URL}${ENDPOINT}" \
      -H "Authorization: Bearer ${API_KEY}" \
      -H "Content-Type: application/json" \
      -d '[
        {
          "colNameCh": "测试字段",
          "colNameComment": "测试用字段",
          "colNameEn": "test_field",
          "projectName": "测试系统",
          "standardCode": "llm_infer_zh_and_cls_and_type_v2_test",
          "sensitivityLevelRedisKey": "fenji_standard"
        }
      ]'
    ;;
    
  health)
    curl -s -o /dev/null -w "%{http_code}" "${API_URL}/health" 2>/dev/null || echo "API不可用"
    ;;
    
  help|--help|-h)
    echo "数安云智数据分类分级同步接口"
    echo ""
    echo "用法: shuyan-classify.sh <command> [args...]"
    echo ""
    echo "命令:"
    echo "  classify <字段中文名> <字段含义> [英文名] [项目名]  - 单字段分类"
    echo "  classify-batch <json_file>                              - 批量分类"
    echo "  test                                                 - 测试连接"
    echo "  health                                               - 健康检查"
    echo ""
    echo "环境变量:"
    echo "  SHUYAN_API_KEY   - API认证密钥 (默认: sk-secret-key)"
    echo "  SHUYAN_API_URL  - API地址 (默认: http://localhost:8080)"
    echo ""
    ;;
    
  *)
    echo "未知命令: $1"
    echo "使用 shuyan-classify.sh help 查看帮助"
    exit 1
    ;;
esac
