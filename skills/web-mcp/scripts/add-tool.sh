#!/bin/bash
# add-tool.sh - Aggiunge un nuovo tool WebMCP

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

TOOL_NAME="${1:-}"
TARGET_DIR="${2:-.}"

if [ -z "$TOOL_NAME" ]; then
  echo "Usage: add-tool.sh <tool-name> [target-dir]"
  echo ""
  echo "Example:"
  echo "  add-tool.sh searchProducts"
  exit 1
fi

TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"
TOOLS_DIR="$TARGET_DIR/tools"

echo "🔧 Creating tool: $TOOL_NAME"

mkdir -p "$TOOLS_DIR"

# Create tool file
cat > "$TOOLS_DIR/$TOOL_NAME.ts" << EOF
import { WebMCPTool, WebMCPContext } from '@/lib/webmcp';

export interface ${TOOL_NAME^}Params {
  // Define your parameters here
  query?: string;
}

export interface ${TOOL_NAME^}Result {
  // Define your return type here
  success: boolean;
  data?: unknown;
  error?: string;
}

export const ${TOOL_NAME}Tool: WebMCPTool<${TOOL_NAME^}Params, ${TOOL_NAME^}Result> = {
  name: '$TOOL_NAME',
  description: 'Description of what $TOOL_NAME does',
  parameters: {
    type: 'object',
    properties: {
      query: {
        type: 'string',
        description: 'Query parameter description'
      }
    }
  },
  
  async execute(params: ${TOOL_NAME^}Params, context: WebMCPContext): Promise<${TOOL_NAME^}Result> {
    try {
      // Implement your tool logic here
      console.log('Executing $TOOL_NAME with params:', params);
      
      return {
        success: true,
        data: null
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }
};

export default ${TOOL_NAME}Tool;
EOF

# Create test file
cat > "$TOOLS_DIR/$TOOL_NAME.test.ts" << EOF
import { ${TOOL_NAME}Tool } from './$TOOL_NAME';

describe('${TOOL_NAME}Tool', () => {
  it('should have correct name', () => {
    expect(${TOOL_NAME}Tool.name).toBe('$TOOL_NAME');
  });

  it('should execute successfully', async () => {
    const result = await ${TOOL_NAME}Tool.execute({ query: 'test' }, {} as any);
    expect(result.success).toBe(true);
  });
});
EOF

echo "✅ Tool created:"
echo "  - $TOOLS_DIR/$TOOL_NAME.ts"
echo "  - $TOOLS_DIR/$TOOL_NAME.test.ts"
echo ""
echo "Usage in your component:"
echo "  import { ${TOOL_NAME}Tool } from '@/tools/$TOOL_NAME';"
echo "  registerTool(${TOOL_NAME}Tool.name, ${TOOL_NAME}Tool.execute);"
