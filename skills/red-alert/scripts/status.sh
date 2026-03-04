#!/bin/bash
# Quick status check for RedAlert API
curl -s -H "Accept: application/json" "https://redalert.orielhaim.com/api/status" | python3 -m json.tool
