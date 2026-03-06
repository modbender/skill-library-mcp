#!/bin/bash
# Crea workflows MCP (Model Context Protocol)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
TEMPLATE_DIR="$SKILL_DIR/templates/workflow"

# Colori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Parse arguments
PROJECT_NAME=""
TEMPLATE="automation"

while [[ $# -gt 0 ]]; do
    case $1 in
        --template)
            TEMPLATE="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: ailabs create workflow <name> --template <automation|integration|pipeline>"
            exit 0
            ;;
        *)
            if [[ -z "$PROJECT_NAME" ]]; then
                PROJECT_NAME="$1"
            fi
            shift
            ;;
    esac
done

if [[ -z "$PROJECT_NAME" ]]; then
    log_error "Nome progetto richiesto"
    exit 1
fi

if [[ ! "$TEMPLATE" =~ ^(automation|integration|pipeline)$ ]]; then
    log_error "Template non valido. Usa: automation, integration, pipeline"
    exit 1
fi

log_info "Creazione Workflow: $PROJECT_NAME (template: $TEMPLATE)"

# Crea directory progetto
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# Inizializza progetto Node.js
log_info "Inizializzazione progetto..."
npm init -y

# Installa dipendenze MCP
log_info "Installazione dipendenze MCP..."
npm install @modelcontextprotocol/sdk zod
npm install -D typescript @types/node ts-node nodemon

# Installa dipendenze aggiuntive
npm install node-cron express
npm install -D @types/express @types/node-cron

# Setup TypeScript
log_info "Setup TypeScript..."
npx tsc --init --outDir ./dist --rootDir ./src --esModuleInterop --strict

# Crea struttura
mkdir -p src/{workflows,servers,tools,resources,utils}

# Crea tsconfig.json
cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "lib": ["ES2022"],
    "moduleResolution": "Node16",
    "rootDir": "./src",
    "outDir": "./dist",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
EOF

# Crea package.json scripts
cat > package.json << 'EOF'
{
  "name": "mcp-workflow",
  "version": "1.0.0",
  "description": "MCP Workflow Server",
  "main": "dist/index.js",
  "type": "module",
  "scripts": {
    "build": "tsc",
    "dev": "nodemon --exec ts-node --esm src/index.ts",
    "start": "node dist/index.js",
    "workflow": "node dist/workflows/runner.js"
  },
  "keywords": ["mcp", "workflow", "automation"],
  "author": "",
  "license": "MIT"
}
EOF

# Crea server MCP base
cat > src/index.ts << 'EOF'
#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
} from '@modelcontextprotocol/sdk/types.js'
import { z } from 'zod'
import { WorkflowEngine } from './workflows/engine.js'

// Workflow Engine
const engine = new WorkflowEngine()

// MCP Server
const server = new Server(
  {
    name: 'mcp-workflow-server',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
      resources: {},
    },
  }
)

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'execute_workflow',
        description: 'Execute a workflow by name',
        inputSchema: {
          type: 'object',
          properties: {
            workflowName: {
              type: 'string',
              description: 'Name of the workflow to execute',
            },
            params: {
              type: 'object',
              description: 'Parameters for the workflow',
            },
          },
          required: ['workflowName'],
        },
      },
      {
        name: 'list_workflows',
        description: 'List all available workflows',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
      {
        name: 'schedule_workflow',
        description: 'Schedule a workflow to run at a specific time',
        inputSchema: {
          type: 'object',
          properties: {
            workflowName: {
              type: 'string',
              description: 'Name of the workflow',
            },
            cron: {
              type: 'string',
              description: 'Cron expression',
            },
            params: {
              type: 'object',
              description: 'Parameters for the workflow',
            },
          },
          required: ['workflowName', 'cron'],
        },
      },
    ],
  }
})

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params

  switch (name) {
    case 'execute_workflow':
      const result = await engine.execute(args.workflowName, args.params)
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(result, null, 2),
          },
        ],
      }

    case 'list_workflows':
      const workflows = engine.listWorkflows()
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(workflows, null, 2),
          },
        ],
      }

    case 'schedule_workflow':
      engine.schedule(args.workflowName, args.cron, args.params)
      return {
        content: [
          {
            type: 'text',
            text: `Workflow '${args.workflowName}' scheduled with cron: ${args.cron}`,
          },
        ],
      }

    default:
      throw new Error(`Unknown tool: ${name}`)
  }
})

// List resources
server.setRequestHandler(ListResourcesRequestSchema, async () => {
  return {
    resources: [
      {
        uri: 'workflows://list',
        name: 'Available Workflows',
        mimeType: 'application/json',
        description: 'List of all registered workflows',
      },
      {
        uri: 'workflows://logs',
        name: 'Workflow Logs',
        mimeType: 'application/json',
        description: 'Recent workflow execution logs',
      },
    ],
  }
})

// Read resources
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const { uri } = request.params

  switch (uri) {
    case 'workflows://list':
      return {
        contents: [
          {
            uri,
            mimeType: 'application/json',
            text: JSON.stringify(engine.listWorkflows(), null, 2),
          },
        ],
      }

    case 'workflows://logs':
      return {
        contents: [
          {
            uri,
            mimeType: 'application/json',
            text: JSON.stringify(engine.getLogs(), null, 2),
          },
        ],
      }

    default:
      throw new Error(`Unknown resource: ${uri}`)
  }
})

// Start server
async function main() {
  const transport = new StdioServerTransport()
  await server.connect(transport)
  console.error('MCP Workflow Server running on stdio')
}

main().catch(console.error)
EOF

# Crea workflow engine
cat > src/workflows/engine.ts << 'EOF'
import { Workflow, WorkflowStep, WorkflowContext } from './types.js'
import { scheduledJobs } from './scheduler.js'

export class WorkflowEngine {
  private workflows: Map<string, Workflow> = new Map()
  private logs: Array<{ timestamp: Date; workflow: string; result: any }> = []

  constructor() {
    this.registerDefaultWorkflows()
  }

  register(name: string, workflow: Workflow) {
    this.workflows.set(name, workflow)
  }

  listWorkflows() {
    return Array.from(this.workflows.entries()).map(([name, workflow]) => ({
      name,
      description: workflow.description,
      steps: workflow.steps.length,
    }))
  }

  async execute(name: string, params?: Record<string, any>): Promise<any> {
    const workflow = this.workflows.get(name)
    if (!workflow) {
      throw new Error(`Workflow '${name}' not found`)
    }

    const context: WorkflowContext = {
      params: params || {},
      data: {},
      results: [],
    }

    console.error(`Executing workflow: ${name}`)

    for (const step of workflow.steps) {
      try {
        console.error(`  Step: ${step.name}`)
        const result = await step.execute(context)
        context.results.push({ step: step.name, result })
        context.data[step.name] = result

        if (step.onSuccess) {
          await step.onSuccess(context, result)
        }
      } catch (error) {
        console.error(`  Error in step ${step.name}:`, error)
        if (step.onError) {
          await step.onError(context, error as Error)
        }
        throw error
      }
    }

    this.logs.push({
      timestamp: new Date(),
      workflow: name,
      result: context.results,
    })

    return context.results
  }

  schedule(name: string, cron: string, params?: Record<string, any>) {
    const workflow = this.workflows.get(name)
    if (!workflow) {
      throw new Error(`Workflow '${name}' not found`)
    }

    scheduledJobs.push({
      workflow: name,
      cron,
      params,
      createdAt: new Date(),
    })

    console.error(`Scheduled workflow '${name}' with cron: ${cron}`)
  }

  getLogs() {
    return this.logs.slice(-50)
  }

  private registerDefaultWorkflows() {
    // Register sample workflows
    const { dataProcessingWorkflow } = await import('./templates.js')
    this.register('data-processing', dataProcessingWorkflow)
  }
}
EOF

# Crea workflow types
cat > src/workflows/types.ts << 'EOF'
export interface WorkflowContext {
  params: Record<string, any>
  data: Record<string, any>
  results: Array<{ step: string; result: any }>
}

export interface WorkflowStep {
  name: string
  description?: string
  execute: (context: WorkflowContext) => Promise<any>
  onSuccess?: (context: WorkflowContext, result: any) => Promise<void>
  onError?: (context: WorkflowContext, error: Error) => Promise<void>
}

export interface Workflow {
  name: string
  description: string
  steps: WorkflowStep[]
  version?: string
}

export interface ScheduledJob {
  workflow: string
  cron: string
  params?: Record<string, any>
  createdAt: Date
}
EOF

# Crea scheduler
cat > src/workflows/scheduler.ts << 'EOF'
import { ScheduledJob } from './types.js'

export const scheduledJobs: ScheduledJob[] = []

export class WorkflowScheduler {
  private jobs: Map<string, any> = new Map()

  schedule(job: ScheduledJob, executeFn: () => Promise<void>) {
    // Implementation would use node-cron
    console.error(`Scheduling ${job.workflow} with cron: ${job.cron}`)
  }

  cancel(workflowName: string) {
    const job = this.jobs.get(workflowName)
    if (job) {
      // job.stop()
      this.jobs.delete(workflowName)
    }
  }

  list() {
    return Array.from(this.jobs.keys())
  }
}
EOF

# Crea workflow templates
cat > src/workflows/templates.ts << 'EOF'
import { Workflow, WorkflowStep } from './types.js'

// Sample Data Processing Workflow
export const dataProcessingWorkflow: Workflow = {
  name: 'data-processing',
  description: 'Process and transform data through multiple steps',
  version: '1.0.0',
  steps: [
    {
      name: 'fetch-data',
      description: 'Fetch data from source',
      execute: async (context) => {
        const source = context.params.source || 'default'
        console.error(`Fetching data from: ${source}`)
        return { source, items: [] }
      },
    },
    {
      name: 'validate',
      description: 'Validate data integrity',
      execute: async (context) => {
        const data = context.data['fetch-data']
        console.error('Validating data...')
        return { valid: true, count: data.items?.length || 0 }
      },
    },
    {
      name: 'transform',
      description: 'Transform data format',
      execute: async (context) => {
        console.error('Transforming data...')
        return { transformed: true, timestamp: new Date().toISOString() }
      },
    },
    {
      name: 'save',
      description: 'Save processed data',
      execute: async (context) => {
        const destination = context.params.destination || 'output'
        console.error(`Saving to: ${destination}`)
        return { saved: true, destination }
      },
    },
  ],
}

// API Integration Workflow
export const apiIntegrationWorkflow: Workflow = {
  name: 'api-integration',
  description: 'Integrate with external APIs',
  version: '1.0.0',
  steps: [
    {
      name: 'authenticate',
      description: 'Authenticate with API',
      execute: async (context) => {
        const apiKey = context.params.apiKey
        console.error('Authenticating...')
        return { authenticated: true, token: 'xxx' }
      },
    },
    {
      name: 'fetch',
      description: 'Fetch data from API',
      execute: async (context) => {
        const endpoint = context.params.endpoint
        console.error(`Fetching from: ${endpoint}`)
        return { data: [] }
      },
    },
    {
      name: 'sync',
      description: 'Sync with local database',
      execute: async (context) => {
        console.error('Syncing data...')
        return { synced: 0 }
      },
    },
  ],
}

// Notification Workflow
export const notificationWorkflow: Workflow = {
  name: 'notification',
  description: 'Send notifications through multiple channels',
  version: '1.0.0',
  steps: [
    {
      name: 'prepare',
      description: 'Prepare notification content',
      execute: async (context) => {
        const { message, channels } = context.params
        return { message, channels: channels || ['email'] }
      },
    },
    {
      name: 'send',
      description: 'Send to all channels',
      execute: async (context) => {
        const prep = context.data['prepare']
        const results = []
        for (const channel of prep.channels) {
          console.error(`Sending via ${channel}...`)
          results.push({ channel, sent: true })
        }
        return { results }
      },
    },
  ],
}
EOF

# Crea workflow runner CLI
cat > src/workflows/runner.ts << 'EOF'
#!/usr/bin/env node
import { WorkflowEngine } from './engine.js'
import { dataProcessingWorkflow, apiIntegrationWorkflow, notificationWorkflow } from './templates.js'

const engine = new WorkflowEngine()

// Register workflows
engine.register('data-processing', dataProcessingWorkflow)
engine.register('api-integration', apiIntegrationWorkflow)
engine.register('notification', notificationWorkflow)

// CLI
const command = process.argv[2]
const workflowName = process.argv[3]

async function main() {
  switch (command) {
    case 'list':
      console.log(JSON.stringify(engine.listWorkflows(), null, 2))
      break

    case 'run':
      if (!workflowName) {
        console.error('Usage: npm run workflow -- run <workflow-name>')
        process.exit(1)
      }
      try {
        const result = await engine.execute(workflowName)
        console.log(JSON.stringify(result, null, 2))
      } catch (error) {
        console.error('Error:', error)
        process.exit(1)
      }
      break

    case 'logs':
      console.log(JSON.stringify(engine.getLogs(), null, 2))
      break

    default:
      console.log('Usage:')
      console.log('  npm run workflow -- list')
      console.log('  npm run workflow -- run <workflow-name>')
      console.log('  npm run workflow -- logs')
  }
}

main()
EOF

# Crea webhook handler
cat > src/servers/webhook.ts << 'EOF'
import express from 'express'
import { WorkflowEngine } from '../workflows/engine.js'

const app = express()
app.use(express.json())

const engine = new WorkflowEngine()

// Webhook endpoint
app.post('/webhook/:workflow', async (req, res) => {
  const { workflow } = req.params
  const { event, data } = req.body

  try {
    const result = await engine.execute(workflow, { event, ...data })
    res.json({ success: true, result })
  } catch (error) {
    res.status(500).json({ success: false, error: (error as Error).message })
  }
})

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', workflows: engine.listWorkflows() })
})

const PORT = process.env.PORT || 3001
app.listen(PORT, () => {
  console.error(`Webhook server running on port ${PORT}`)
})
EOF

# Crea .env.example
cat > .env.example << 'EOF'
# MCP Server Configuration
PORT=3001
NODE_ENV=development

# API Keys for integrations
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Webhook secrets
WEBHOOK_SECRET=

# Database (optional)
DATABASE_URL=
EOF

# Crea README
cat > README.md << EOF
# $PROJECT_NAME

Workflow MCP Server creato con AI Labs Builder

## Features

- MCP (Model Context Protocol) compliant server
- Workflow engine con step-by-step execution
- Scheduled workflows con cron expressions
- Webhook triggers
- Resource templates
- Cross-server coordination ready

## Struttura

\`\`\`
src/
├── index.ts              # MCP Server entry point
├── workflows/
│   ├── engine.ts         # Workflow execution engine
│   ├── types.ts          # TypeScript types
│   ├── scheduler.ts      # Cron scheduling
│   ├── templates.ts      # Sample workflows
│   └── runner.ts         # CLI runner
├── servers/
│   └── webhook.ts        # Webhook HTTP server
└── utils/                # Utilities
\`\`\`

## Comandi

\`\`\`bash
# Install dependencies
npm install

# Build
npm run build

# Run MCP Server
npm start

# Run CLI
npm run workflow -- list
npm run workflow -- run data-processing
npm run workflow -- logs

# Dev mode
npm run dev
\`\`\`

## Workflow Template

\`\`\`typescript
import { Workflow } from './workflows/types.js'

const myWorkflow: Workflow = {
  name: 'my-workflow',
  description: 'My custom workflow',
  steps: [
    {
      name: 'step-1',
      execute: async (context) => {
        // Your logic here
        return { success: true }
      },
    },
  ],
}
\`\`\`

## MCP Tools

- \`execute_workflow\` - Esegue un workflow
- \`list_workflows\` - Lista workflow disponibili
- \`schedule_workflow\` - Schedula un workflow

## MCP Resources

- \`workflows://list\` - Lista workflow
- \`workflows://logs\` - Execution logs
EOF

log_success "Workflow MCP creato con successo!"
log_info "Template: $TEMPLATE"
log_info "Per iniziare:"
echo "  cd $PROJECT_NAME"
echo "  npm install"
echo "  npm run build"
echo "  npm start"
echo ""
log_info "Comandi CLI:"
echo "  npm run workflow -- list"
echo "  npm run workflow -- run data-processing"
