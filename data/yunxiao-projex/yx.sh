#!/bin/bash
# 云效项目协作工具快捷脚本

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"

# 只加载明确的变量名，避免导出无关的 secrets
if [ -f "$ENV_FILE" ]; then
  while IFS='=' read -r key value; do
    # 跳过注释和空行
    if [[ ! "$key" =~ ^# ]] && [[ -n "$key" ]]; then
      # 只导出我们需要的变量
      case "$key" in
        YUNXIAO_ACCESS_TOKEN|YUNXIAO_ORGANIZATION_ID)
          export "$key=$value"
          ;;
      esac
    fi
  done < "$ENV_FILE"
fi

# 运行 Node.js 脚本
node "$SCRIPT_DIR/yunxiao-projex.js" "$@"
