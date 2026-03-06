#!/bin/bash
# 初始化 planning 三文件
# 用法: ./init-session.sh [任务名]

set -e

TASK_NAME="${1:-task}"
DATE=$(date +%Y-%m-%d)

echo "初始化 planning 文件: $TASK_NAME"
echo "日期: $DATE"
echo ""

# 创建 task_plan.md
if [ ! -f "task_plan.md" ]; then
    cat > task_plan.md << 'EOF'
# Task Plan: [任务名称]

## Goal
[一句话描述最终目标]

## Current Phase
Phase 1

## Phases

### Phase 1: 需求理解
- [ ] 理解用户意图
- [ ] 识别约束条件
- [ ] 记录到 findings.md
- **Status:** in_progress

### Phase 2: 方案设计
- [ ] 确定实现方案
- [ ] 创建项目结构
- **Status:** pending

### Phase 3: 开发实现
- [ ] 执行计划
- [ ] 先写文件再执行
- **Status:** pending

### Phase 4: 测试验证
- [ ] 验证需求满足
- [ ] 记录测试结果
- **Status:** pending

### Phase 5: 交付
- [ ] 审查输出
- [ ] 交付用户
- **Status:** pending

## Decisions Made
| Decision | Rationale |
|----------|-----------|

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
EOF
    echo "[OK] 创建 task_plan.md"
else
    echo "[!] task_plan.md 已存在，跳过"
fi

# 创建 findings.md
if [ ! -f "findings.md" ]; then
    cat > findings.md << 'EOF'
# Findings

## 需求发现
-

## 研究发现
-

## 技术决策
| Decision | Rationale |
|----------|-----------|

## 遇到的问题
| Issue | Resolution |
|-------|------------|

## 参考资源
-
EOF
    echo "[OK] 创建 findings.md"
else
    echo "[!] findings.md 已存在，跳过"
fi

# 创建 progress.md
if [ ! -f "progress.md" ]; then
    cat > progress.md << EOF
# Progress Log

## Session: $DATE

### Current Status
- **Phase:** 1 - 需求理解
- **Started:** $DATE

### Actions Taken
-

### Test Results
| Test | Expected | Actual | Status |
|------|----------|--------|--------|

### Errors
| Error | Attempt | Result | Next |
|-------|---------|--------|------|
EOF
    echo "[OK] 创建 progress.md"
else
    echo "[!] progress.md 已存在，跳过"
fi

echo ""
echo "Planning 文件初始化完成!"
echo "文件: task_plan.md, findings.md, progress.md"
echo ""
echo "下一步:"
echo "  1. 编辑 task_plan.md 填写任务目标"
echo "  2. 开始执行 Phase 1"
