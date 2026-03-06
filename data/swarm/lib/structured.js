/**
 * Structured Output Mode
 * Forces JSON schema output via Gemini's response_mime_type
 * Zero parse failures on structured extraction tasks
 * 
 * v1.3.7
 */

/**
 * Built-in schemas for common extraction patterns
 */
const SCHEMAS = {
  // Extract key entities from text
  entities: {
    type: 'object',
    properties: {
      entities: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            name: { type: 'string' },
            type: { type: 'string' },
            description: { type: 'string' },
          },
          required: ['name', 'type'],
        },
      },
    },
    required: ['entities'],
  },

  // Summarize with structured fields
  summary: {
    type: 'object',
    properties: {
      title: { type: 'string' },
      summary: { type: 'string' },
      keyPoints: {
        type: 'array',
        items: { type: 'string' },
      },
      sentiment: { type: 'string', enum: ['positive', 'negative', 'neutral', 'mixed'] },
      confidence: { type: 'number' },
    },
    required: ['title', 'summary', 'keyPoints'],
  },

  // Compare multiple items
  comparison: {
    type: 'object',
    properties: {
      items: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            name: { type: 'string' },
            pros: { type: 'array', items: { type: 'string' } },
            cons: { type: 'array', items: { type: 'string' } },
            score: { type: 'number' },
          },
          required: ['name', 'pros', 'cons'],
        },
      },
      winner: { type: 'string' },
      reasoning: { type: 'string' },
    },
    required: ['items', 'winner', 'reasoning'],
  },

  // Extract action items / tasks
  actions: {
    type: 'object',
    properties: {
      actions: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            action: { type: 'string' },
            priority: { type: 'string', enum: ['high', 'medium', 'low'] },
            owner: { type: 'string' },
            deadline: { type: 'string' },
          },
          required: ['action', 'priority'],
        },
      },
    },
    required: ['actions'],
  },

  // Classify/categorize input
  classification: {
    type: 'object',
    properties: {
      category: { type: 'string' },
      subcategory: { type: 'string' },
      confidence: { type: 'number' },
      reasoning: { type: 'string' },
      tags: { type: 'array', items: { type: 'string' } },
    },
    required: ['category', 'confidence'],
  },

  // Q&A extraction
  qa: {
    type: 'object',
    properties: {
      answer: { type: 'string' },
      confidence: { type: 'number' },
      sources: { type: 'array', items: { type: 'string' } },
      caveats: { type: 'array', items: { type: 'string' } },
    },
    required: ['answer', 'confidence'],
  },
};

/**
 * List available built-in schemas
 */
function listSchemas() {
  return Object.entries(SCHEMAS).map(([key, schema]) => ({
    key,
    fields: Object.keys(schema.properties),
    required: schema.required,
  }));
}

/**
 * Get a built-in schema by key
 */
function getSchema(key) {
  if (!SCHEMAS[key]) {
    throw new Error(`Unknown schema: ${key}. Available: ${Object.keys(SCHEMAS).join(', ')}`);
  }
  return SCHEMAS[key];
}

/**
 * Validate a JSON object against a schema (lightweight, no external deps)
 */
function validateAgainstSchema(data, schema) {
  const errors = [];

  if (schema.required) {
    for (const field of schema.required) {
      if (data[field] === undefined || data[field] === null) {
        errors.push(`Missing required field: ${field}`);
      }
    }
  }

  if (schema.properties) {
    for (const [key, prop] of Object.entries(schema.properties)) {
      if (data[key] !== undefined) {
        if (prop.type === 'array' && !Array.isArray(data[key])) {
          errors.push(`${key} should be array, got ${typeof data[key]}`);
        } else if (prop.type === 'number' && typeof data[key] !== 'number') {
          errors.push(`${key} should be number, got ${typeof data[key]}`);
        } else if (prop.type === 'string' && typeof data[key] !== 'string') {
          errors.push(`${key} should be string, got ${typeof data[key]}`);
        }
        if (prop.enum && !prop.enum.includes(data[key])) {
          errors.push(`${key} must be one of: ${prop.enum.join(', ')}`);
        }
      }
    }
  }

  return { valid: errors.length === 0, errors };
}

module.exports = { SCHEMAS, listSchemas, getSchema, validateAgainstSchema };
