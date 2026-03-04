#!/bin/bash

# Tech Blog Generator
# Usage: tech-blog-generator "Title" "Description" [--tags tag1,tag2]

set -e

TITLE="${1:-}"
DESCRIPTION="${2:-}"
TAGS="${3:-}"
LEVEL="${4:-Intermediate}"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Convert title to slug
to_slug() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd '[:alnum:]-'
}

# Current date
CURRENT_DATE=$(date +"%Y-%m-%d")

# Check if title is provided
if [ -z "$TITLE" ]; then
    echo -e "${YELLOW}Usage: tech-blog-generator \"Article Title\" \"Description\" [--tags tag1,tag2]${NC}"
    exit 1
fi

if [ -z "$DESCRIPTION" ]; then
    DESCRIPTION="A comprehensive guide on this topic"
fi

SLUG=$(to_slug "$TITLE")

# Generate blog post
cat << EOF
# $TITLE

> $DESCRIPTION

**Published:** $CURRENT_DATE  
**Level:** $LEVEL  
$TAGS_TAG_LINE

---

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Getting Started](#getting-started)
4. [Main Content](#main-content)
5. [Code Examples](#code-examples)
6. [Best Practices](#best-practices)
7. [Conclusion](#conclusion)
8. [References](#references)

---

## Introduction

$DESCRIPTION

In this article, we'll explore the key concepts and practical applications. By the end, you'll have a solid understanding of the topic.

---

## Prerequisites

Before we begin, make sure you have:

- Basic understanding of the subject
- Required tools installed
- Access to necessary resources

---

## Getting Started

Let's start by setting up our environment.

\`\`\`bash
# Install dependencies
npm install

# Run the project
npm start
\`\`\`

---

## Main Content

### What is this about?

This section covers the core concepts...

### Key Concepts

1. **First Concept** - Explanation...
2. **Second Concept** - Explanation...
3. **Third Concept** - Explanation...

### How it works

The implementation follows these steps:

1. Step one
2. Step two
3. Step three

---

## Code Examples

### Example 1: Basic Usage

\`\`\`javascript
// Your code here
function example() {
  console.log('Hello, World!');
}
\`\`\`

### Example 2: Advanced Usage

\`\`\`javascript
// Advanced example
async function advanced() {
  const result = await fetch('/api/data');
  return result.json();
}
\`\`\`

---

## Best Practices

- ✅ Do this
- ✅ Do that
- ❌ Avoid this
- ❌ Don't do that

---

## Conclusion

In this article, we've covered:

- The fundamentals
- Practical applications
- Best practices

Continue learning and experimenting!

---

## References

- [Resource 1](link)
- [Resource 2](link)
- [Resource 3](link)

---

*Generated with Tech Blog Generator*
EOF

# Generate tags line if provided
if [ -n "$TAGS" ]; then
    TAGS_TAG_LINE="**Tags:** $(echo "$TAGS" | tr ',' ' ')"
else
    TAGS_TAG_LINE=""
fi

echo ""
echo -e "${GREEN}✅ Blog post generated!${NC}"
echo "Title: $TITLE"
echo "Slug: $SLUG"
