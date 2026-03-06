#!/bin/bash

# GitHub README Generator
# Usage: github-readme-generator "Project Name" "Description" [--template modern] [--lang en]

set -e

NAME="${1:-}"
DESCRIPTION="${2:-}"
TEMPLATE="${3:-modern}"
LANG="${4:-en}"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Templates
MODERN_TEMPLATE() {
    cat << 'EOF'
# {NAME}

{DESCRIPTION}

![License](https://img.shields.io/github/license/{NAME_KEBAB})
![Stars](https://img.shields.io/github/stars/{NAME_KEBAB})
![Forks](https://img.shields.io/github/forks/{NAME_KEBAB})
![Issues](https://img.shields.io/github/issues/{NAME_KEBAB})

## Features

- ✨ Feature 1
- 🚀 Feature 2
- 🔒 Feature 3
- 📦 Easy to use

## Installation

\`\`\`bash
npm install {NAME_KEBAB}
\`\`\`

## Usage

\`\`\`javascript
const {NAME_CAMEL} = require('{NAME_KEBAB}');

// Example usage
async function main() {
  const result = await {NAME_CAMEL}.doSomething();
  console.log(result);
}

main();
\`\`\`

## API

| Method | Description | Returns |
|--------|-------------|---------|
| \`doSomething()\` | Does something | \`Promise<Result>\` |

## Contributing

1. Fork the repository
2. Create your feature branch (\`git checkout -b feature/amazing-feature\`)
3. Commit your changes (\`git commit -m 'Add some amazing feature'\`)
4. Push to the branch (\`git push origin feature/amazing-feature\`)
5. Open a Pull Request

## License

MIT License - see the [LICENSE](LICENSE) file for details.

## Author

{ AUTHOR_NAME }
EOF
}

MINIMAL_TEMPLATE() {
    cat << 'EOF'
# {NAME}

{DESCRIPTION}

## Install

\`\`\`
npm install {NAME_KEBAB}
\`\`\`

## Usage

\`\`\`js
const pkg = require('{NAME_KEBAB}');
\`\`\`

## License

MIT
EOF
}

CLI_TEMPLATE() {
    cat << 'EOF'
# {NAME}

{DESCRIPTION}

[![npm version](https://img.shields.io/npm/v/{NAME_KEBAB}.svg)](https://www.npmjs.com/package/{NAME_KEBAB})
[![License](https://img.shields.io/npm/l/{NAME_KEBAB}.svg)](https://opensource.org/licenses/MIT)

## Install

\`\`\`bash
npm install -g {NAME_KEBAB}
\`\`\`

## Usage

\`\`\`bash
{NAME_KEBAB} --help
{NAME_KEBAB} command --option
\`\`\`

## Commands

| Command | Description |
|---------|-------------|
| \`init\` | Initialize project |
| \`build\` | Build for production |
| \`deploy\` | Deploy to server |

## License

MIT
EOF
}

# Convert name to different cases
to_kebab() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd '[:alnum:]-'
}

to_camel() {
    echo "$1" | sed 's/[-_ ]//g' | sed 's/^\(.\)/\U\1/'
}

# Check if name is provided
if [ -z "$NAME" ]; then
    echo -e "${RED}Error: Project name is required${NC}"
    echo "Usage: github-readme-generator \"Project Name\" \"Description\""
    exit 1
fi

if [ -z "$DESCRIPTION" ]; then
    echo -e "${YELLOW}Warning: No description provided${NC}"
    DESCRIPTION="A brief description of your awesome project"
fi

NAME_KEBAB=$(to_kebab "$NAME")
NAME_CAMEL=$(to_camel "$NAME")
AUTHOR_NAME="${AUTHOR_NAME:-Your Name}"

# Get git config if available
if [ -d ".git" ]; then
    GIT_NAME=$(git config user.name 2>/dev/null || echo "")
    if [ -n "$GIT_NAME" ]; then
        AUTHOR_NAME="$GIT_NAME"
    fi
fi

# Generate based on template
case "$TEMPLATE" in
    minimal)
        TEMPLATE_CONTENT=$(MINIMAL_TEMPLATE)
        ;;
    cli)
        TEMPLATE_CONTENT=$(CLI_TEMPLATE)
        ;;
    modern|*)
        TEMPLATE_CONTENT=$(MODERN_TEMPLATE)
        ;;
esac

# Replace placeholders
CONTENT=$(echo "$TEMPLATE_CONTENT" | sed "s/{NAME}/$NAME/g")
CONTENT=$(echo "$CONTENT" | sed "s/{NAME_KEBAB}/$NAME_KEBAB/g")
CONTENT=$(echo "$CONTENT" | sed "s/{NAME_CAMEL}/$NAME_CAMEL/g")
CONTENT=$(echo "$CONTENT" | sed "s/{DESCRIPTION}/$DESCRIPTION/g")
CONTENT=$(echo "$CONTENT" | sed "s/{AUTHOR_NAME}/$AUTHOR_NAME/g")

# Output
echo "$CONTENT" > README.md

echo -e "${GREEN}✅ README.md generated successfully!${NC}"
echo "Project: $NAME"
echo "Template: $TEMPLATE"
