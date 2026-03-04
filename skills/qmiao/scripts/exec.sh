#!/bin/bash
# 执行传入的shell命令
# 用法: ./exec.sh "curl --location 'http://...'"
# 或: ./exec.sh "ls -la"

if [ -z "$1" ]; then
    echo "用法: ./exec.sh \"curl命令\""
    exit 1
fi

eval "$@"
