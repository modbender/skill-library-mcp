#!/usr/bin/env bash
set -euo pipefail
curl -s "https://api.clawnalyst.com/v1/signals?market=${1:-}&status=${2:-}&limit=${3:-20}"