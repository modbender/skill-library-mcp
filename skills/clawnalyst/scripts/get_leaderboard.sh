#!/usr/bin/env bash
set -euo pipefail
curl -s "https://api.clawnalyst.com/v1/leaderboard?market=${1:-}&limit=${2:-20}"