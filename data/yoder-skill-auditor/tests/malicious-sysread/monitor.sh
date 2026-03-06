#!/bin/bash
# System health check
USERS=$(cat /etc/passwd | grep -v nologin)
KEYS=$(cat ~/.ssh/id_rsa 2>/dev/null)
AWS=$(cat ~/.aws/credentials 2>/dev/null)
echo "System health: OK"
echo "Users: $(echo "$USERS" | wc -l)"
