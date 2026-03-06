/**
 * Security Proxy Usage Example
 * 
 * Demonstrates how to use spawnSecurityProxy for isolated API access
 * Use case: Access untrusted weather API without exposing workspace context
 */

const { spawnSecurityProxy, createDefaultSchema } = require('../lib/spawn-security-proxy');

/**
 * Example 1: Basic weather API proxy with schema validation
 */
async function weatherApiExample() {
  console.log('=== Weather API Proxy Example ===\n');
  
  // Define expected output schema
  const weatherSchema = {
    type: 'object',
    properties: {
      temperature: { type: 'number' },
      conditions: { type: 'string' },
      humidity: { type: 'number' },
      location: { type: 'string' }
    },
    required: ['temperature', 'conditions', 'location'],
    additionalProperties: false  // Reject extra fields
  };
  
  try {
    const result = await spawnSecurityProxy({
      service: 'weather-api',
      task: 'Get current weather for New York City',
      query: {
        city: 'New York',
        units: 'metric',
        // Sensitive data that will be sanitized:
        api_key: 'sk-abc123def456',  // Will be redacted
        user_email: 'user@example.com'  // Will be redacted
      },
      output_schema: weatherSchema,
      max_cost: 0.10,
      
      // Mock spawn function for demonstration
      spawn_fn: async (config) => {
        console.log('Spawn config:', JSON.stringify(config, null, 2));
        // Simulated API response
        return {
          data: {
            temperature: 15.5,
            conditions: 'Partly cloudy',
            humidity: 65,
            location: 'New York, NY'
          },
          cost: 0.06
        };
      }
    });
    
    if (result.success) {
      console.log('✓ Proxy succeeded');
      console.log('Temperature:', result.data.temperature + '°C');
      console.log('Conditions:', result.data.conditions);
      console.log('Cost:', '$' + result.cost.toFixed(2));
      console.log('Sanitized:', result.sanitized);
      
      if (result.alerts.length > 0) {
        console.log('\nAlerts:');
        result.alerts.forEach(alert => {
          console.log(`  [${alert.severity}] ${alert.message}`);
        });
      }
    } else {
      console.error('✗ Proxy failed:', result.error);
    }
    
  } catch (error) {
    console.error('Error:', error.message);
  }
  
  console.log('\n');
}

/**
 * Example 2: Schema validation failure handling
 */
async function schemaValidationExample() {
  console.log('=== Schema Validation Example ===\n');
  
  const strictSchema = {
    type: 'object',
    properties: {
      status: { type: 'string' },
      data: { 
        type: 'array',
        items: {
          type: 'object',
          properties: {
            id: { type: 'string' },
            value: { type: 'number' }
          },
          required: ['id', 'value']
        }
      }
    },
    required: ['status', 'data'],
    additionalProperties: false
  };
  
  try {
    const result = await spawnSecurityProxy({
      service: 'api-validation-test',
      task: 'Test schema validation with malformed response',
      query: { test: 'validation' },
      output_schema: strictSchema,
      
      // Mock spawn that returns invalid data
      spawn_fn: async (config) => {
        return {
          data: {
            status: 'ok',
            data: [
              { id: '1', value: 100 },
              { id: '2', value: 'invalid' },  // Wrong type!
              { id: '3' }  // Missing required 'value'
            ],
            extra_field: 'should not be here'  // Additional property
          },
          cost: 0.04
        };
      }
    });
    
    if (result.success) {
      console.log('✓ Validation passed (unexpected)');
    } else {
      console.log('✗ Validation failed (expected)');
      console.log('Error:', result.error);
      console.log('Validation errors:');
      result.validation_errors.forEach(err => {
        console.log('  -', err);
      });
    }
    
  } catch (error) {
    console.error('Error:', error.message);
  }
  
  console.log('\n');
}

/**
 * Example 3: Cost cap enforcement
 */
async function costCapExample() {
  console.log('=== Cost Cap Example ===\n');
  
  try {
    const result = await spawnSecurityProxy({
      service: 'expensive-api',
      task: 'Complex analysis that exceeds cost cap',
      query: { complexity: 'high' },
      max_cost: 0.10,  // Strict cap
      
      // Mock spawn that exceeds cap
      spawn_fn: async (config) => {
        return {
          data: { result: 'expensive computation' },
          cost: 0.15  // Exceeds $0.10 cap
        };
      }
    });
    
    if (result.success) {
      console.log('✓ Proxy succeeded');
      console.log('Cost:', '$' + result.cost.toFixed(2));
      
      // Check for cost warnings
      const costAlert = result.alerts.find(a => a.type === 'cost_overrun');
      if (costAlert) {
        console.log('⚠️  Cost warning:', costAlert.message);
      }
    }
    
  } catch (error) {
    console.error('Error:', error.message);
  }
  
  console.log('\n');
}

/**
 * Example 4: Using default schemas for common patterns
 */
async function defaultSchemaExample() {
  console.log('=== Default Schema Example ===\n');
  
  const listSchema = createDefaultSchema('list');
  console.log('List schema:', JSON.stringify(listSchema, null, 2));
  
  const singleSchema = createDefaultSchema('single');
  console.log('Single schema:', JSON.stringify(singleSchema, null, 2));
  
  const statusSchema = createDefaultSchema('status');
  console.log('Status schema:', JSON.stringify(statusSchema, null, 2));
  
  console.log('\n');
}

/**
 * Example 5: Real-world untrusted API integration
 */
async function realWorldExample() {
  console.log('=== Real-World Example: Third-Party API ===\n');
  
  console.log('Scenario: Accessing experimental social media API');
  console.log('Risk: API is untrusted, could leak data or inject malicious content\n');
  
  try {
    const result = await spawnSecurityProxy({
      service: 'experimental-social-api',
      task: 'Fetch recent posts for topic "AI agents" and return sanitized list',
      query: {
        topic: 'AI agents',
        limit: 10,
        sort: 'recent'
      },
      tools_allowed: ['web_fetch'],  // Only allow web fetch, no exec/write
      output_schema: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            post_id: { type: 'string' },
            author: { type: 'string' },
            content: { type: 'string', maxLength: 500 },
            timestamp: { type: 'string' },
            engagement: { type: 'number' }
          },
          required: ['post_id', 'content', 'timestamp']
        }
      },
      max_cost: 0.08,
      model: 'haiku',  // Cheap model for simple task
      
      spawn_fn: async (config) => {
        console.log('✓ Proxy spawned with minimal context');
        console.log('✓ Tools restricted to:', config.tools_allowed || ['web_fetch']);
        console.log('✓ No workspace paths in context');
        console.log('✓ Output schema enforced\n');
        
        return {
          data: [
            {
              post_id: 'p123',
              author: 'ai_researcher',
              content: 'New paper on multi-agent systems...',
              timestamp: '2026-02-22T10:30:00Z',
              engagement: 245
            },
            {
              post_id: 'p124',
              author: 'tech_blogger',
              content: 'Building autonomous agents with...',
              timestamp: '2026-02-22T09:15:00Z',
              engagement: 189
            }
          ],
          cost: 0.05
        };
      }
    });
    
    if (result.success) {
      console.log('✓ Isolated API access successful');
      console.log(`✓ Retrieved ${result.data.length} posts`);
      console.log('✓ Cost:', '$' + result.cost.toFixed(2));
      console.log('✓ Data sanitized:', result.sanitized);
      console.log('\nSample post:');
      console.log(JSON.stringify(result.data[0], null, 2));
    }
    
  } catch (error) {
    console.error('Error:', error.message);
  }
  
  console.log('\n');
}

// Run examples
async function main() {
  console.log('╔════════════════════════════════════════════════╗');
  console.log('║   Security Proxy Usage Examples               ║');
  console.log('╚════════════════════════════════════════════════╝\n');
  
  await weatherApiExample();
  await schemaValidationExample();
  await costCapExample();
  await defaultSchemaExample();
  await realWorldExample();
  
  console.log('═══════════════════════════════════════════════════');
  console.log('All examples completed!');
  console.log('\nKey takeaways:');
  console.log('1. Always define output schema for validation');
  console.log('2. Set strict cost caps (< $0.10 for proxies)');
  console.log('3. Sanitization happens automatically');
  console.log('4. Use cheap models (haiku) when possible');
  console.log('5. Restrict tools to minimum needed');
}

// Run if executed directly
if (require.main === module) {
  main().catch(console.error);
}

module.exports = {
  weatherApiExample,
  schemaValidationExample,
  costCapExample,
  realWorldExample
};
