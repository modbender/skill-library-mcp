#!/bin/bash
# Strip ANSI escape codes from stdin
# Usage: echo "colored text" | ./strip-ansi.sh
sed 's/\x1b\[[0-9;]*[a-zA-Z]//g; s/\x1b\][^\x07]*\x07//g; s/\x1b(B//g; s/\r//g'
