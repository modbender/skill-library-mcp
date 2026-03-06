#!/bin/bash
# Authentication script for Jira and Confluence

# Usage:
# source auth.sh
# to set environment variables before running commands

# Check if tokens are provided
if [[ -z "${JIRA_API_TOKEN}" || -z "${CONFLUENCE_API_TOKEN}" ]]; then
  echo "Error: JIRA_API_TOKEN or CONFLUENCE_API_TOKEN environment variables are not set."
  echo "You can set them via export or CLI arguments."
  exit 1
fi

# Export tokens for API usage
if [[ -z "${JIRA_API_TOKEN}" ]]; then
  export JIRA_API_TOKEN="${JIRA_API_TOKEN:-""}
fi

if [[ -z "${CONFLUENCE_API_TOKEN}" ]]; then
  export CONFLUENCE_API_TOKEN="${CONFLUENCE_API_TOKEN:-""}
fi
