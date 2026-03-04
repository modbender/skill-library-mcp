#!/bin/bash
# Interactive script to create master resume

set -e

echo "📝 Let's create your master resume!"
echo ""

# Create directory
mkdir -p CV_Master

# Basic Info
echo "=== Basic Information ==="
read -p "Full Name: " name
read -p "Professional Title (e.g., 'Data Analyst'): " title
read -p "Email: " email
read -p "Phone: " phone
read -p "LinkedIn URL: " linkedin
read -p "Portfolio/Website (optional): " portfolio

echo ""
echo "=== Professional Summary ==="
echo "Describe yourself in 2-3 sentences. Include:"
echo "- Your current role/expertise"
echo "- What makes you unique"
echo "- Your career focus"
echo "(Press Enter twice when done)"
summary=""
while IFS= read -r line; do
    [ -z "$line" ] && break
    summary="$summary $line"
done

echo ""
echo "=== Core Competencies ==="
echo "Enter your top 5-8 skills (one per line, empty line to finish):"
skills=()
while IFS= read -r skill; do
    [ -z "$skill" ] && break
    skills+=("$skill")
done

echo ""
echo "=== Professional Experience ==="
echo "We'll add 2-3 most relevant roles."
experiences=()
for i in 1 2 3; do
    echo ""
    echo "--- Role $i ---"
    read -p "Company (or press Enter to skip): " company
    [ -z "$company" ] && break
    read -p "Job Title: " job_title
    read -p "Dates (e.g., '2022 - Present'): " dates
    read -p "Location: " location
    
    echo "Enter 3-4 bullet points (one per line, empty line to finish):"
    bullets=()
    while IFS= read -r bullet; do
        [ -z "$bullet" ] && break
        bullets+=("$bullet")
    done
    
    experiences+=("$company|$job_title|$dates|$location|${bullets[*]}")
done

echo ""
echo "=== Education ==="
read -p "Degree (e.g., 'Bachelor of Science in Computer Science'): " degree
read -p "Institution: " institution
read -p "Dates: " edu_dates

echo ""
echo "=== Languages ==="
echo "Enter languages and proficiency (e.g., 'English (Native)', one per line):"
languages=()
while IFS= read -r lang; do
    [ -z "$lang" ] && break
    languages+=("$lang")
done

# Generate markdown file
cat > CV_Master/master_resume.md << EOF
# $name

## Contact Information
- **Email:** $email
- **Phone:** $phone
- **LinkedIn:** $linkedin
${portfolio:+- **Portfolio:** $portfolio}

## Professional Summary

$summary

## Core Competencies

$(for skill in "${skills[@]}"; do echo "- $skill"; done)

## Professional Experience

$(for exp in "${experiences[@]}"; do
    IFS='|' read -r comp title dates location bullets <<< "$exp"
    echo "### $comp | $title"
    echo "*$dates | $location*"
    echo ""
    for bullet in $bullets; do
        echo "- $bullet"
    done
    echo ""
done)

## Education

### $degree
*$institution | $edu_dates*

## Languages

$(for lang in "${languages[@]}"; do echo "- $lang"; done)
EOF

echo ""
echo "✅ Master resume created at: CV_Master/master_resume.md"
echo ""
echo "You can edit this file anytime to update your information."