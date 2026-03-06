#!/usr/bin/env node
/**
 * MCP Workflow Server
 * 
 * Implements Model Context Protocol for workflow automation.
 * Provides prompts, resources, and tools for orchestrating multi-step workflows.
 * 
 * Inspired by Jason Zhou's MCP patterns
 */

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const {
  CallToolRequestSchema,
  ListResourcesRequestSchema,
  ListResourceTemplatesRequestSchema,
  ListToolsRequestSchema,
  ReadResourceRequestSchema,
  ListPromptsRequestSchema,
  GetPromptRequestSchema,
} = require('@modelcontextprotocol/sdk/types.js');

const fs = require('fs');
const path = require('path');

// Configuration
const CONFIG = {
  templatesDir: path.join(__dirname, 'templates'),
  workflowsDir: process.env.WORKFLOWS_DIR || './workflows',
  memoryFile: path.join(__dirname, '.mcp-memory.json'),
};

// In-memory storage
let memoryStore = {};

// Load memory if exists
function loadMemory() {
  try {
    if (fs.existsSync(CONFIG.memoryFile)) {
      memoryStore = JSON.parse(fs.readFileSync(CONFIG.memoryFile, 'utf8'));
    }
  } catch (e) {
    console.error('Error loading memory:', e.message);
  }
}

// Save memory
function saveMemory() {
  try {
    fs.writeFileSync(CONFIG.memoryFile, JSON.stringify(memoryStore, null, 2));
  } catch (e) {
    console.error('Error saving memory:', e.message);
  }
}

// Load memory on startup
loadMemory();

// Create server
const server = new Server(
  {
    name: 'mcp-workflow-server',
    version: '1.0.0',
  },
  {
    capabilities: {
      resources: {},
      tools: {},
      prompts: {},
    },
  }
);

/**
 * RESOURCES
 */

// List available resources
server.setRequestHandler(ListResourcesRequestSchema, async () => {
  const resources = [];
  
  // Add memory resources
  for (const key of Object.keys(memoryStore)) {
    resources.push({
      uri: `memory://${key}`,
      mimeType: 'application/json',
      name: `Memory: ${key}`,
      description: `Stored memory value for key: ${key}`,
    });
  }
  
  // Add template resources
  try {
    const templates = fs.readdirSync(CONFIG.templatesDir)
      .filter(f => f.endsWith('.json'));
    for (const template of templates) {
      const name = path.basename(template, '.json');
      resources.push({
        uri: `template://${name}`,
        mimeType: 'application/json',
        name: `Template: ${name}`,
        description: `Workflow template: ${name}`,
      });
    }
  } catch (e) {
    // Templates dir might not exist
  }
  
  return { resources };
});

// Resource templates
server.setRequestHandler(ListResourceTemplatesRequestSchema, async () => {
  return {
    resourceTemplates: [
      {
        uriTemplate: 'file://{path}',
        name: 'File System',
        mimeType: 'text/plain',
        description: 'Access files by path',
      },
      {
        uriTemplate: 'memory://{key}',
        name: 'Memory Store',
        mimeType: 'application/json',
        description: 'Access stored memory values',
      },
      {
        uriTemplate: 'template://{name}',
        name: 'Workflow Template',
        mimeType: 'application/json',
        description: 'Access workflow templates',
      },
      {
        uriTemplate: 'config://{section}',
        name: 'Configuration',
        mimeType: 'application/json',
        description: 'Access configuration sections',
      },
    ],
  };
});

// Read resource
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const uri = request.params.uri;
  
  // Memory resource
  if (uri.startsWith('memory://')) {
    const key = uri.replace('memory://', '');
    if (memoryStore[key] !== undefined) {
      return {
        contents: [
          {
            uri,
            mimeType: 'application/json',
            text: JSON.stringify(memoryStore[key], null, 2),
          },
        ],
      };
    }
    throw new Error(`Memory key not found: ${key}`);
  }
  
  // Template resource
  if (uri.startsWith('template://')) {
    const name = uri.replace('template://', '');
    const templatePath = path.join(CONFIG.templatesDir, `${name}.json`);
    if (fs.existsSync(templatePath)) {
      return {
        contents: [
          {
            uri,
            mimeType: 'application/json',
            text: fs.readFileSync(templatePath, 'utf8'),
          },
        ],
      };
    }
    throw new Error(`Template not found: ${name}`);
  }
  
  // File resource
  if (uri.startsWith('file://')) {
    const filePath = uri.replace('file://', '');
    if (fs.existsSync(filePath)) {
      const content = fs.readFileSync(filePath, 'utf8');
      return {
        contents: [
          {
            uri,
            mimeType: 'text/plain',
            text: content,
          },
        ],
      };
    }
    throw new Error(`File not found: ${filePath}`);
  }
  
  throw new Error(`Unsupported resource URI: ${uri}`);
});

/**
 * TOOLS
 */

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'workflow.run',
        description: 'Execute a workflow by name with optional input',
        inputSchema: {
          type: 'object',
          properties: {
            name: {
              type: 'string',
              description: 'Name of the workflow to run',
            },
            input: {
              type: 'object',
              description: 'Input parameters for the workflow',
            },
          },
          required: ['name'],
        },
      },
      {
        name: 'workflow.list',
        description: 'List all available workflows',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
      {
        name: 'workflow.validate',
        description: 'Validate a workflow JSON structure',
        inputSchema: {
          type: 'object',
          properties: {
            workflow: {
              type: 'object',
              description: 'Workflow object to validate',
            },
          },
          required: ['workflow'],
        },
      },
      {
        name: 'memory.set',
        description: 'Store a value in memory',
        inputSchema: {
          type: 'object',
          properties: {
            key: {
              type: 'string',
              description: 'Memory key',
            },
            value: {
              type: 'any',
              description: 'Value to store',
            },
          },
          required: ['key', 'value'],
        },
      },
      {
        name: 'memory.get',
        description: 'Retrieve a value from memory',
        inputSchema: {
          type: 'object',
          properties: {
            key: {
              type: 'string',
              description: 'Memory key',
            },
          },
          required: ['key'],
        },
      },
      {
        name: 'memory.delete',
        description: 'Delete a value from memory',
        inputSchema: {
          type: 'object',
          properties: {
            key: {
              type: 'string',
              description: 'Memory key',
            },
          },
          required: ['key'],
        },
      },
      {
        name: 'prompt.render',
        description: 'Render a prompt template with variables',
        inputSchema: {
          type: 'object',
          properties: {
            template: {
              type: 'string',
              description: 'Prompt template with {variables}',
            },
            variables: {
              type: 'object',
              description: 'Variables to substitute',
            },
          },
          required: ['template'],
        },
      },
      {
        name: 'chain.execute',
        description: 'Execute a prompt chain (plan → generate → execute)',
        inputSchema: {
          type: 'object',
          properties: {
            steps: {
              type: 'array',
              description: 'Array of chain steps',
              items: {
                type: 'object',
                properties: {
                  name: { type: 'string' },
                  prompt: { type: 'string' },
                  input: { type: 'object' },
                },
              },
            },
            context: {
              type: 'object',
              description: 'Shared context across steps',
            },
          },
          required: ['steps'],
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  
  switch (name) {
    case 'workflow.run': {
      const workflowName = args.name;
      const input = args.input || {};
      
      // Load workflow template
      const templatePath = path.join(CONFIG.templatesDir, `${workflowName}.json`);
      if (!fs.existsSync(templatePath)) {
        throw new Error(`Workflow template not found: ${workflowName}`);
      }
      
      const workflow = JSON.parse(fs.readFileSync(templatePath, 'utf8'));
      
      // Execute workflow steps
      const results = [];
      let context = { ...input };
      
      for (const step of workflow.steps || []) {
        const result = await executeStep(step, context);
        results.push({ step: step.name, result });
        context = { ...context, ...result };
      }
      
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              workflow: workflowName,
              results,
              finalContext: context,
            }, null, 2),
          },
        ],
      };
    }
    
    case 'workflow.list': {
      try {
        const templates = fs.readdirSync(CONFIG.templatesDir)
          .filter(f => f.endsWith('.json'))
          .map(f => path.basename(f, '.json'));
        
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({ workflows: templates }, null, 2),
            },
          ],
        };
      } catch (e) {
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({ workflows: [], error: e.message }, null, 2),
            },
          ],
        };
      }
    }
    
    case 'workflow.validate': {
      const workflow = args.workflow;
      const errors = validateWorkflow(workflow);
      
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              valid: errors.length === 0,
              errors,
            }, null, 2),
          },
        ],
      };
    }
    
    case 'memory.set': {
      memoryStore[args.key] = args.value;
      saveMemory();
      return {
        content: [
          {
            type: 'text',
            text: `Memory set: ${args.key}`,
          },
        ],
      };
    }
    
    case 'memory.get': {
      const value = memoryStore[args.key];
      return {
        content: [
          {
            type: 'text',
            text: value !== undefined 
              ? JSON.stringify(value, null, 2)
              : `Memory key not found: ${args.key}`,
          },
        ],
      };
    }
    
    case 'memory.delete': {
      delete memoryStore[args.key];
      saveMemory();
      return {
        content: [
          {
            type: 'text',
            text: `Memory deleted: ${args.key}`,
          },
        ],
      };
    }
    
    case 'prompt.render': {
      let rendered = args.template;
      const vars = args.variables || {};
      
      for (const [key, value] of Object.entries(vars)) {
        rendered = rendered.replace(new RegExp(`{${key}}`, 'g'), String(value));
      }
      
      return {
        content: [
          {
            type: 'text',
            text: rendered,
          },
        ],
      };
    }
    
    case 'chain.execute': {
      const steps = args.steps || [];
      let context = args.context || {};
      const results = [];
      
      for (const step of steps) {
        // Merge step input with context
        const input = { ...context, ...(step.input || {}) };
        
        // Simulate step execution (in real impl, would call LLM)
        const result = {
          step: step.name,
          input,
          output: `Executed: ${step.name}`,
          timestamp: new Date().toISOString(),
        };
        
        results.push(result);
        context = { ...context, ...result };
      }
      
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({ results, finalContext: context }, null, 2),
          },
        ],
      };
    }
    
    default:
      throw new Error(`Unknown tool: ${name}`);
  }
});

/**
 * PROMPTS
 */

// List available prompts
server.setRequestHandler(ListPromptsRequestSchema, async () => {
  return {
    prompts: [
      {
        name: 'chain:plan',
        description: 'Planning step in a workflow chain',
        arguments: [
          {
            name: 'goal',
            description: 'What to plan for',
            required: true,
          },
          {
            name: 'constraints',
            description: 'Any constraints to consider',
            required: false,
          },
        ],
      },
      {
        name: 'chain:generate',
        description: 'Generation step in a workflow chain',
        arguments: [
          {
            name: 'task',
            description: 'What to generate',
            required: true,
          },
          {
            name: 'context',
            description: 'Context from previous steps',
            required: false,
          },
        ],
      },
      {
        name: 'chain:review',
        description: 'Review step in a workflow chain',
        arguments: [
          {
            name: 'content',
            description: 'Content to review',
            required: true,
          },
          {
            name: 'criteria',
            description: 'Review criteria',
            required: false,
          },
        ],
      },
      {
        name: 'workflow:meal-plan',
        description: 'Generate a meal plan',
        arguments: [
          {
            name: 'diet',
            description: 'Dietary preferences',
            required: false,
          },
          {
            name: 'days',
            description: 'Number of days',
            required: true,
          },
        ],
      },
      {
        name: 'workflow:code-review',
        description: 'Review code changes',
        arguments: [
          {
            name: 'code',
            description: 'Code to review',
            required: true,
          },
          {
            name: 'language',
            description: 'Programming language',
            required: false,
          },
        ],
      },
    ],
  };
});

// Get prompt
server.setRequestHandler(GetPromptRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  
  const prompts = {
    'chain:plan': {
      description: 'Planning step',
      messages: [
        {
          role: 'user',
          content: {
            type: 'text',
            text: `Create a detailed plan for: ${args?.goal || 'the task'}
${args?.constraints ? `\nConstraints: ${args.constraints}` : ''}

Break this down into clear, actionable steps.`,
          },
        },
      ],
    },
    'chain:generate': {
      description: 'Generation step',
      messages: [
        {
          role: 'user',
          content: {
            type: 'text',
            text: `Generate ${args?.task || 'content'} based on the following context:
${args?.context ? `\nContext:\n${args.context}` : ''}

Provide a complete, well-structured output.`,
          },
        },
      ],
    },
    'chain:review': {
      description: 'Review step',
      messages: [
        {
          role: 'user',
          content: {
            type: 'text',
            text: `Review the following content:
${args?.content || ''}

${args?.criteria ? `Review Criteria:\n${args.criteria}` : 'Provide constructive feedback and suggestions for improvement.'}`,
          },
        },
      ],
    },
    'workflow:meal-plan': {
      description: 'Meal planning workflow',
      messages: [
        {
          role: 'user',
          content: {
            type: 'text',
            text: `Create a ${args?.days || 7}-day meal plan${args?.diet ? ` for a ${args.diet} diet` : ''}.

Include:
- Breakfast, lunch, dinner for each day
- Shopping list organized by category
- Nutritional highlights

Format as a structured meal plan.`,
          },
        },
      ],
    },
    'workflow:code-review': {
      description: 'Code review workflow',
      messages: [
        {
          role: 'user',
          content: {
            type: 'text',
            text: `Review the following ${args?.language || ''} code:

\`\`\`
${args?.code || ''}
\`\`\`

Check for:
1. Bugs and logic errors
2. Code style and best practices
3. Performance issues
4. Security concerns
5. Documentation completeness

Provide specific, actionable feedback.`,
          },
        },
      ],
    },
  };
  
  const prompt = prompts[name];
  if (!prompt) {
    throw new Error(`Prompt not found: ${name}`);
  }
  
  return prompt;
});

// Helper functions
function validateWorkflow(workflow) {
  const errors = [];
  
  if (!workflow.name) {
    errors.push('Workflow must have a name');
  }
  
  if (!workflow.steps || !Array.isArray(workflow.steps)) {
    errors.push('Workflow must have a steps array');
  } else {
    for (let i = 0; i < workflow.steps.length; i++) {
      const step = workflow.steps[i];
      if (!step.name) {
        errors.push(`Step ${i} must have a name`);
      }
      if (!step.type) {
        errors.push(`Step ${step.name || i} must have a type`);
      }
    }
  }
  
  return errors;
}

async function executeStep(step, context) {
  // In a real implementation, this would execute the step
  // For now, return a mock result
  return {
    stepName: step.name,
    stepType: step.type,
    executed: true,
    timestamp: new Date().toISOString(),
    context,
  };
}

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('MCP Workflow Server running on stdio');
}

main().catch(console.error);
