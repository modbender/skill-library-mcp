#!/bin/bash
# CLI Scaffold Generator

NAME="${1:-my-cli}"
FRAMEWORK="${2:-commander}"
DESCRIPTION="${3:-A awesome CLI tool}"
AUTHOR="${4:-Developer}"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

if [ -z "$NAME" ]; then
    echo "Usage: cli-scaffold-generator <name> [framework] [description]"
    exit 1
fi

echo -e "${BLUE}🖥️ Generating CLI scaffold: $NAME${NC}"
echo "Framework: $FRAMEWORK"
echo ""

# Create directory structure
mkdir -p "$NAME"/{bin,lib,test}

# Generate package.json
cat > "$NAME/package.json" << JSON
{
  "name": "$NAME",
  "version": "1.0.0",
  "description": "$DESCRIPTION",
  "main": "bin/$NAME.js",
  "bin": {
    "$NAME": "bin/$NAME.js"
  },
  "scripts": {
    "test": "jest",
    "start": "node bin/$NAME.js"
  },
  "keywords": ["cli", "command-line", "$FRAMEWORK"],
  "author": "$AUTHOR",
  "license": "MIT",
  "dependencies": {
    "commander": "^11.0.0",
    "chalk": "^4.1.2"
  },
  "devDependencies": {
    "jest": "^29.0.0"
  }
}
JSON

# Generate main entry file
cat > "$NAME/bin/$NAME.js" << MAIN
#!/usr/bin/env node

const { Command } = require('commander');
const program = new Command());

program
  .name('$NAME')
  .description('$DESCRIPTION')
  .version('1.0.0');

// Default command
program
  .command('hello')
  .description('Say hello')
  .argument('<name>', 'Name to greet')
  .option('-l, --loud', 'Greet loudly')
  .action((name, options) => {
    const greeting = \`Hello, \${name}!\`;
    console.log(options.loud ? greeting.toUpperCase() : greeting);
  });

// Another example command
program
  .command('init')
  .description('Initialize the project')
  .option('-y, --yes', 'Skip prompts')
  .action((options) => {
    console.log('Initializing project...');
    if (options.yes) {
      console.log('Created config files!');
    } else {
      console.log('Run with --yes to skip prompts');
    }
  });

program.parse();
MAIN

# Generate README
cat > "$NAME/README.md" << README
# $NAME

$DESCRIPTION

## Installation

\`\`\`bash
npm install -g $NAME
\`\`\`

## Usage

\`\`\`bash
# Greet someone
$NAME hello World

# With loud mode
$NAME hello World --loud

# Initialize project
$NAME init
\`\`\`

## Development

\`\`\`bash
# Install dependencies
npm install

# Link locally
npm link

# Test
npm test
\`\`\`

## License

MIT
README

# Make executable
chmod +x "$NAME/bin/$NAME.js"

echo -e "${GREEN}✅ CLI scaffold generated!${NC}"
echo "📁 Location: ./$NAME"
echo ""
echo "Next steps:"
echo "1. cd $NAME"
echo "2. npm install"
echo "3. npm link"
echo "4. $NAME --help"
