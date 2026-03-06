#!/bin/bash
# Obsidian CLI wrapper - 确保 PATH 正确
export PATH="$PATH:/Applications/Obsidian.app/Contents/MacOS"
exec obsidian "$@"
