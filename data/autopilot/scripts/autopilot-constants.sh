#!/bin/bash
# autopilot-constants.sh — 脚本共享常量
#
# 允许通过环境变量覆盖，避免硬编码漂移。
AUTOPILOT_VERSION="0.5.0"

: "${LOW_CONTEXT_THRESHOLD:=25}"
: "${LOW_CONTEXT_CRITICAL_THRESHOLD:=15}"
: "${IDLE_THRESHOLD:=300}"
: "${IDLE_CONFIRM_PROBES:=3}"
: "${WORKING_INERTIA_SECONDS:=90}"
: "${CODEX_STATE_WORKING:=working}"
: "${CODEX_STATE_IDLE:=idle}"
: "${CODEX_STATE_IDLE_LOW_CONTEXT:=idle_low_context}"
: "${CODEX_STATE_PERMISSION:=permission}"
: "${CODEX_STATE_PERMISSION_WITH_REMEMBER:=permission_with_remember}"
: "${CODEX_STATE_SHELL:=shell}"
: "${CODEX_STATE_ABSENT:=absent}"
: "${MANUAL_BLOCK_REGEX:=BLOCKED[^│]*|manual[^│]*|人工[^│]*|需要证书[^│]*|证书[^│]*|签名[^│]*|certificate[^│]*|signing[^│]*|cert[^│]*}"
: "${NUDGE_MAX_RETRY:=5}"
: "${NUDGE_PAUSE_SECONDS:=1800}"
: "${LAYER2_FILE_PREVIEW_LIMIT:=20}"
: "${LAYER2_FALLBACK_COMMIT_WINDOW:=30}"
: "${TSC_TIMEOUT_SECONDS:=30}"
: "${REVIEW_OUTPUT_WAIT_SECONDS:=90}"
