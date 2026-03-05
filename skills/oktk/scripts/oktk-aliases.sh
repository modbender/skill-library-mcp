#!/bin/bash
# oktk-aliases.sh - Auto-filter common CLI outputs through oktk
# Source this file in your .zshrc or .bashrc:
#   source ~/.openclaw/workspace/skills/oktk/scripts/oktk-aliases.sh
#
# By Buba Draugelis 🇱🇹
# https://github.com/satnamra/openclaw-workspace

# Check if oktk is installed
if ! command -v oktk &> /dev/null; then
    echo "[oktk] Warning: oktk not found. Install with: npm link ~/.openclaw/workspace/skills/oktk"
    return 1
fi

# ═══════════════════════════════════════════════════════════════
# Git Commands (60-90% token reduction)
# ═══════════════════════════════════════════════════════════════
alias gst='git status | oktk git status'
alias glog='git log --oneline -20 | oktk git log'
alias gdiff='git diff | oktk git diff'
alias gbr='git branch -a | oktk git branch'
alias gsh='git show | oktk git show'
alias gstash='git stash list | oktk git stash'
alias gbl='git blame | oktk git blame'

# Full git wrapper function
gitk() {
    git "$@" 2>&1 | oktk "git $*"
}

# ═══════════════════════════════════════════════════════════════
# Docker Commands (50-80% token reduction)
# ═══════════════════════════════════════════════════════════════
alias dps='docker ps | oktk docker ps'
alias dpsa='docker ps -a | oktk docker ps'
alias dimages='docker images | oktk docker images'
alias dlogs='docker logs 2>&1 | oktk docker logs'
alias dstats='docker stats --no-stream | oktk docker stats'
alias dcompose='docker-compose ps | oktk docker-compose'

# Full docker wrapper function
dk() {
    docker "$@" 2>&1 | oktk "docker $*"
}

dkc() {
    docker-compose "$@" 2>&1 | oktk "docker-compose $*"
}

# ═══════════════════════════════════════════════════════════════
# Kubectl Commands (60-85% token reduction)
# ═══════════════════════════════════════════════════════════════
alias kpods='kubectl get pods | oktk kubectl get pods'
alias ksvc='kubectl get svc | oktk kubectl get svc'
alias kdeploy='kubectl get deployments | oktk kubectl get deployments'
alias knodes='kubectl get nodes | oktk kubectl get nodes'
alias klogs='kubectl logs 2>&1 | oktk kubectl logs'
alias kdesc='kubectl describe 2>&1 | oktk kubectl describe'
alias kevents='kubectl get events | oktk kubectl get events'

# Full kubectl wrapper function
kk() {
    kubectl "$@" 2>&1 | oktk "kubectl $*"
}

# ═══════════════════════════════════════════════════════════════
# NPM/Yarn Commands (40-70% token reduction)
# ═══════════════════════════════════════════════════════════════
alias ntest='npm test 2>&1 | oktk npm test'
alias nbuild='npm run build 2>&1 | oktk npm build'
alias ninstall='npm install 2>&1 | oktk npm install'
alias nlist='npm list 2>&1 | oktk npm list'
alias noutdated='npm outdated 2>&1 | oktk npm outdated'

# ═══════════════════════════════════════════════════════════════
# System Commands
# ═══════════════════════════════════════════════════════════════
alias psg='ps aux | grep | oktk ps'
alias lsa='ls -la | oktk'
alias dfh='df -h | oktk'
alias duh='du -h | oktk'
alias netstat_listen='netstat -an | grep LISTEN | oktk'

# ═══════════════════════════════════════════════════════════════
# Universal wrapper - pipe any command through oktk
# ═══════════════════════════════════════════════════════════════
# Usage: ok <command>
# Example: ok git status
# Example: ok docker ps -a
ok() {
    "$@" 2>&1 | oktk "$*"
}

# ═══════════════════════════════════════════════════════════════
# Stats helper
# ═══════════════════════════════════════════════════════════════
alias oktk-stats='oktk --stats'

echo "[oktk] 🚀 Token optimizer aliases loaded!"
echo "[oktk] Use 'ok <command>' to filter any output, or use aliases like gst, dps, kpods"
echo "[oktk] Check stats: oktk --stats"
