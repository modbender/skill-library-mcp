/**
 * ContextCompressor - Usage Examples
 *
 * This file demonstrates various ways to use the ContextCompressor
 * for reducing context size while maintaining quality.
 */

import { ContextCompressor, createCompressor } from './compressor.js';

// ============================================================================
// Example 1: Basic Usage - Hybrid Strategy (Recommended)
// ============================================================================

async function example1_BasicUsage() {
  console.log('========================================');
  console.log('Example 1: Basic Usage - Hybrid Strategy');
  console.log('========================================\n');

  const compressor = new ContextCompressor();

  const context = `User: Hi, I'm working on a React project.
Assistant: Great! How can I help with your React project?
User: I need to optimize my component rendering.
Assistant: You can use React.memo to prevent unnecessary re-renders.
User: How do I use React.memo?
Assistant: Wrap your component with React.memo like this:

\`\`\`javascript
const MyComponent = React.memo(({ data }) => {
  return <div>{data}</div>;
});
\`\`\`

User: Thanks! That's helpful.
Assistant: You're welcome!`;

  const result = await compressor.compress(context, 'hybrid');

  console.log('Original Context:');
  console.log(result.original);
  console.log('\nCompressed Context:');
  console.log(result.compressed);
  console.log('\nMetrics:');
  console.log(`- Original tokens: ${result.metrics.originalTokens}`);
  console.log(`- Compressed tokens: ${result.metrics.compressedTokens}`);
  console.log(`- Compression ratio: ${(result.metrics.compressionRatio * 100).toFixed(1)}%`);
  console.log(`- Quality score: ${result.metrics.qualityScore.toFixed(3)}`);
  console.log(`- Time taken: ${result.metrics.compressionTime}ms\n`);
}

// ============================================================================
// Example 2: Deduplication Strategy
// ============================================================================

async function example2_Deduplication() {
  console.log('========================================');
  console.log('Example 2: Deduplication Strategy');
  console.log('========================================\n');

  const compressor = new ContextCompressor();

  const context = `The user prefers TypeScript over JavaScript.
TypeScript provides better type safety.
The user mentioned they prefer TypeScript.
Type safety is important in large projects.
The user likes TypeScript for large projects.`;

  const result = await compressor.compress(context, 'deduplication');

  console.log('Original Context:');
  console.log(result.original);
  console.log('\nDeduplicated Context:');
  console.log(result.compressed);
  console.log('\nMetrics:');
  console.log(`- Compression ratio: ${(result.metrics.compressionRatio * 100).toFixed(1)}%`);
  console.log(`- Quality score: ${result.metrics.qualityScore.toFixed(3)}\n`);
}

// ============================================================================
// Example 3: Pruning Strategy - Remove Low-Value Content
// ============================================================================

async function example3_Pruning() {
  console.log('========================================');
  console.log('Example 3: Pruning Strategy');
  console.log('========================================\n');

  const compressor = new ContextCompressor();

  const context = `Hello! How are you today?
The project uses a microservices architecture.
Thanks for your help!
Each service communicates via REST APIs.
Okay, sure.
The database is PostgreSQL with Redis caching.
Can you help me with something?`;

  const result = await compressor.compress(context, 'pruning');

  console.log('Original Context:');
  console.log(result.original);
  console.log('\nPruned Context (low-value phrases removed):');
  console.log(result.compressed);
  console.log('\nMetrics:');
  console.log(`- Compression ratio: ${(result.metrics.compressionRatio * 100).toFixed(1)}%\n`);
}

// ============================================================================
// Example 4: Summarization Strategy - Condense Verbose Content
// ============================================================================

async function example4_Summarization() {
  console.log('========================================');
  console.log('Example 4: Summarization Strategy');
  console.log('========================================\n');

  const compressor = new ContextCompressor();

  const context = `The application is built using React for the frontend.
React is a popular JavaScript library.
We chose React because of its component-based architecture.
Components can be reused across the application.
The state management is handled by Redux.
Redux provides predictable state updates.
We use Redux Toolkit for better developer experience.
The backend is built with Node.js and Express.
Express is a minimal web framework for Node.js.
We chose Express for its simplicity and flexibility.`;

  const result = await compressor.compress(context, 'summarization', {
    targetCompressionRatio: 0.5 // 50% compression
  });

  console.log('Original Context:');
  console.log(result.original);
  console.log('\nSummarized Context:');
  console.log(result.compressed);
  console.log('\nMetrics:');
  console.log(`- Compression ratio: ${(result.metrics.compressionRatio * 100).toFixed(1)}%`);
  console.log(`- Quality score: ${result.metrics.qualityScore.toFixed(3)}\n`);
}

// ============================================================================
// Example 5: Template Removal - Remove Boilerplate
// ============================================================================

async function example5_TemplateRemoval() {
  console.log('========================================');
  console.log('Example 5: Template Removal');
  console.log('========================================\n');

  const compressor = new ContextCompressor();

  const context = `---
Copyright (c) 2024 OpenClaw
Licensed under MIT License
---

This is the main documentation for the API.
The API provides endpoints for user management.

---
Generated by OpenClaw Documentation Generator
Auto-generated on 2024-02-12
---

Key endpoints:
- POST /api/users - Create user
- GET /api/users/:id - Get user`;

  const result = await compressor.compress(context, 'template');

  console.log('Original Context:');
  console.log(result.original);
  console.log('\nCleaned Context (templates removed):');
  console.log(result.compressed);
  console.log('\nMetrics:');
  console.log(`- Compression ratio: ${(result.metrics.compressionRatio * 100).toFixed(1)}%\n`);
}

// ============================================================================
// Example 6: Custom Options
// ============================================================================

async function example6_CustomOptions() {
  console.log('========================================');
  console.log('Example 6: Custom Options');
  console.log('========================================\n');

  // Create compressor with custom options
  const compressor = new ContextCompressor(null, {
    targetCompressionRatio: 0.6,    // Target 60% compression
    similarityThreshold: 0.85,       // Lower threshold = more aggressive dedup
    preserveCodeBlocks: true,        // Always preserve code blocks
    preserveImportantSections: true  // Keep sections marked as important
  });

  const context = `User: I prefer TypeScript.
The quick brown fox jumps over the lazy dog.
User: I like TypeScript.
The quick brown fox is very fast.

\`\`\`typescript
function greet(name: string): string {
  return \`Hello, \${name}!\`;
}
\`\`\`

Important: Always validate user input.
The lazy dog is sleeping peacefully.`;

  const result = await compressor.compress(context, 'hybrid');

  console.log('Compressed Context:');
  console.log(result.compressed);
  console.log('\nMetrics:');
  console.log(`- Target compression: 60%`);
  console.log(`- Achieved compression: ${(result.metrics.compressionRatio * 100).toFixed(1)}%`);
  console.log(`- Quality score: ${result.metrics.qualityScore.toFixed(3)}\n`);
}

// ============================================================================
// Example 7: Structured Object Input
// ============================================================================

async function example7_StructuredInput() {
  console.log('========================================');
  console.log('Example 7: Structured Object Input');
  console.log('========================================\n');

  const compressor = new ContextCompressor();

  const contextObject = {
    userProfile: {
      name: 'John Doe',
      preferences: ['TypeScript', 'React', 'Node.js'],
      experience: 'Senior Developer'
    },
    conversationHistory: [
      'User: I prefer TypeScript',
      'Assistant: TypeScript is great!',
      'User: I prefer TypeScript',
      'Assistant: You mentioned that earlier'
    ],
    systemInfo: {
      platform: 'Windows',
      version: '1.0.0'
    }
  };

  const result = await compressor.compress(contextObject, 'hybrid');

  console.log('Original object tokens:', result.metrics.originalTokens);
  console.log('Compressed tokens:', result.metrics.compressedTokens);
  console.log('Compression ratio:', `${(result.metrics.compressionRatio * 100).toFixed(1)}%\n`);
}

// ============================================================================
// Example 8: Token Estimation (No Compression)
// ============================================================================

async function example8_TokenEstimation() {
  console.log('========================================');
  console.log('Example 8: Token Estimation');
  console.log('========================================\n');

  const compressor = new ContextCompressor();

  const examples = [
    'Hello world',
    'The quick brown fox jumps over the lazy dog',
    'import { ContextCompressor } from "./compressor.js";\nconst comp = new ContextCompressor();'
  ];

  for (const text of examples) {
    const tokens = compressor.estimateTokens(text);
    console.log(`Text: "${text.substring(0, 50)}${text.length > 50 ? '...' : ''}"`);
    console.log(`Estimated tokens: ${tokens}\n`);
  }
}

// ============================================================================
// Example 9: Quality Scoring
// ============================================================================

async function example9_QualityScoring() {
  console.log('========================================');
  console.log('Example 9: Quality Scoring');
  console.log('========================================\n');

  const compressor = new ContextCompressor();

  const original = `John works at OpenAI as a Senior Engineer.
He specializes in natural language processing.
His favorite programming language is Python.
He has published 5 research papers on AI.`;

  // Good compression - keeps key information
  const goodCompression = `John works at OpenAI as Senior Engineer specializing in NLP.
Favorite language: Python. Published 5 AI research papers.`;

  // Poor compression - loses too much information
  const poorCompression = `John works at OpenAI.`;

  const goodScore = compressor.calculateQualityScore(original, goodCompression);
  const poorScore = compressor.calculateQualityScore(original, poorCompression);

  console.log('Original:', original);
  console.log('\nGood Compression:', goodCompression);
  console.log('Quality Score:', goodScore.toFixed(3));
  console.log('\nPoor Compression:', poorCompression);
  console.log('Quality Score:', poorScore.toFixed(3));
  console.log('\nInterpretation:');
  console.log('- Scores range from 0.0 (poor) to 1.0 (perfect)');
  console.log('- Higher scores indicate better information retention\n');
}

// ============================================================================
// Example 10: Factory Function
// ============================================================================

async function example10_FactoryFunction() {
  console.log('========================================');
  console.log('Example 10: Factory Function');
  console.log('========================================\n');

  // Using factory function with custom options
  const compressor = createCompressor(null, {
    targetCompressionRatio: 0.5,
    similarityThreshold: 0.9
  });

  const context = 'Hello! How are you today?';
  const result = await compressor.compress(context);

  console.log('Created compressor using factory function');
  console.log('Compression strategy:', result.strategy);
  console.log('Successfully compressed context\n');
}

// ============================================================================
// Run All Examples
// ============================================================================

async function runAllExamples() {
  await example1_BasicUsage();
  await example2_Deduplication();
  await example3_Pruning();
  await example4_Summarization();
  await example5_TemplateRemoval();
  await example6_CustomOptions();
  await example7_StructuredInput();
  await example8_TokenEstimation();
  await example9_QualityScoring();
  await example10_FactoryFunction();

  console.log('========================================');
  console.log('All examples completed!');
  console.log('========================================');
}

// Run examples if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  runAllExamples().catch(console.error);
}

export {
  example1_BasicUsage,
  example2_Deduplication,
  example3_Pruning,
  example4_Summarization,
  example5_TemplateRemoval,
  example6_CustomOptions,
  example7_StructuredInput,
  example8_TokenEstimation,
  example9_QualityScoring,
  example10_FactoryFunction
};
