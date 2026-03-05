#!/bin/bash

NOTES_DIR="$HOME/.quick-notes"
TODAY=$(date +%Y-%m-%d)
NOTE_FILE="$NOTES_DIR/$TODAY.md"

# 确保目录存在
mkdir -p "$NOTES_DIR"

case "$1" in
    add)
        shift
        echo "- $@" >> "$NOTE_FILE"
        echo "已记录: $@"
        ;;
    list)
        if [ -d "$NOTES_DIR" ]; then
            cat "$NOTES_DIR"/*.md 2>/dev/null || echo "暂无笔记"
        else
            echo "暂无笔记"
        fi
        ;;
    search)
        shift
        grep -r "$@" "$NOTES_DIR" 2>/dev/null || echo "未找到相关笔记"
        ;;
    today)
        if [ -f "$NOTE_FILE" ]; then
            cat "$NOTE_FILE"
        else
            echo "今天还没有笔记"
        fi
        ;;
    clear)
        rm -rf "$NOTES_DIR"
        echo "所有笔记已清空"
        ;;
    *)
        echo "用法: note {add|list|search|today|clear}"
        ;;
esac
