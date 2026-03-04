#!/usr/bin/env bash
# Salary Research — Search for salary data for a given role and location
# Usage: salary_research.sh "job title" "location"
#
# Outputs search queries for the agent to use with web_search/web_fetch tools.
# Sources: Glassdoor, LinkedIn Salary, levels.fyi, Payscale, Indeed

set -euo pipefail

ROLE="${1:?Usage: salary_research.sh \"job title\" \"location\"}"
LOCATION="${2:-}"

cat << EOF
{
  "role": "${ROLE}",
  "location": "${LOCATION}",
  "search_queries": [
    "${ROLE} salary ${LOCATION} glassdoor 2025 2026",
    "${ROLE} salary range ${LOCATION} linkedin",
    "${ROLE} compensation ${LOCATION} levels.fyi",
    "${ROLE} salary ${LOCATION} payscale",
    "${ROLE} salary netherlands europe indeed"
  ],
  "fetch_urls": [
    "https://www.glassdoor.com/Salaries/${ROLE// /-}-salary-SRCH_KO0,${#ROLE}.htm",
    "https://www.levels.fyi/t/${ROLE// /-}"
  ],
  "tips": [
    "Cross-reference at least 3 sources for accuracy",
    "Check if salary is gross or net, monthly or annual",
    "Factor in benefits: pension, holiday allowance (8% in NL), 13th month",
    "In the Netherlands, use the 'Loonwijzer' tool for local benchmarks",
    "Consider total compensation: base + bonus + equity + benefits"
  ]
}
EOF
