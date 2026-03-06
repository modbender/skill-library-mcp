# Autopilot 系统 PRD

## 第一批修复 ✅
- ✅ M-1 Layer2 review clean 误判
- ✅ M-2 发送失败仍进冷却
- ✅ M-5 Layer2 trigger 非 idle 被消费
- ✅ M-6 .last-review-commit 无条件推进
- ✅ M-9 PROJECTS 硬编码两处

## 第二批修复 ✅
- ✅ M-3 两套状态机统一
- ✅ M-4 指令生效闭环
- ✅ M-7 status.json 自动更新
- ✅ M-8 互斥锁

## 第三批修复
- ✅ M-10 低 context 阈值不一致 (15 vs 25)
- ✅ M-11 Layer2 文件列表上限 10 个
- ✅ M-12 tsc --noEmit 无 timeout
- ✅ M-13 review 历史按日期覆盖
- ✅ M-14 watchdog 仅 set -u，关键命令失败继续
- ✅ M-15 md5 管道优先级
- ✅ M-16 tmux paste-buffer 竞态

## idle 检测升级
- ✅ IDLE_THRESHOLD 120→300s
- ✅ 连续 3 次确认机制（IDLE_CONFIRM_PROBES=3）
- ✅ Working 惯性 90s（WORKING_INERTIA=90）
- ✅ codex-status.sh 正则补全（Thinking 等误判）

## PRD 引擎
- ✅ prd-items.yaml 结构化格式（支持多版本、bugfix type）
- ✅ prd-verify.sh 自动验收引擎（checker 插件化）
- ✅ prd-progress.json 机器可读状态
- ✅ prd-todo.md 自动生成（从 progress.json）
- ✅ commit 后自动匹配 PRD item 并跑 checker
- ✅ review P0/P1 自动转 prd-items.yaml bugfix item
- ✅ 接入 watchdog 触发 + status-sync 推进
- ✅ nudge 带具体失败原因（而非泛泛"继续推进"）

## compact_prompt 升级
- ✅ 加入 prd-todo.md 引用（compact 后不丢任务上下文）

## CONVENTIONS.md 规则
- ✅ Codex 完成任务后必须更新 prd-todo.md 标记 ✅

## 全面 review
- ✅ 双路 review (Claude + Codex) 直到 P0/P1 = 0
