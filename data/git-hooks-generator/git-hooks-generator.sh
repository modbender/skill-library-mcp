#!/bin/bash
mkdir -p .git/hooks

cat > .git/hooks/pre-commit << 'HOOK'
#!/bin/sh
echo "Running pre-commit checks..."
npm run lint
npm test
HOOK

chmod +x .git/hooks/pre-commit
echo "✅ Git hooks generated!"
