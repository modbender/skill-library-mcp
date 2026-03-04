#!/usr/bin/env node
/**
 * Ragflow CLI
 * Universal command-line client for Ragflow API
 */

const fs = require('fs');
const path = require('path');
const ragflow = require('../lib/api.js');

// ANSI colors
const c = {
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  cyan: '\x1b[36m',
  dim: '\x1b[2m',
  reset: '\x1b[0m',
};

function log(msg, color = 'reset') {
  console.log(`${c[color]}${msg}${c.reset}`);
}

function error(msg) {
  console.error(`${c.red}Error: ${msg}${c.reset}`);
  process.exit(1);
}

function printUsage() {
  console.log(`
${c.cyan}Ragflow CLI${c.reset} - Universal Ragflow API client

${c.yellow}Usage:${c.reset}
  node ragflow.js <command> [options]

${c.yellow}Commands:${c.reset}
  datasets                List all datasets
  create-dataset          Create a new dataset
  delete-dataset          Delete a dataset
  documents               List documents in a dataset
  upload                  Upload a document to a dataset
  parse                   Trigger parsing for documents
  chat                    Run a RAG query against a dataset

${c.yellow}Options:${c.reset}
  --name <name>           Dataset name (for create-dataset)
  --dataset <id>          Dataset ID
  --file <path>           File path (for upload)
  --query <text>          Query text (for chat)
  --top-k <n>             Number of chunks to retrieve (default: 10)
  --doc-ids <ids>         Comma-separated document IDs (for parse)

${c.yellow}Examples:${c.reset}
  node ragflow.js datasets
  node ragflow.js create-dataset --name "My Knowledge Base"
  node ragflow.js upload --dataset DATASET_ID --file article.pdf
  node ragflow.js parse --dataset DATASET_ID --doc-ids DOC_ID1,DOC_ID2
  node ragflow.js chat --dataset DATASET_ID --query "What is stroke?"
`);
}

function parseArgs(args) {
  const result = { _: [] };
  let current = null;
  
  for (const arg of args) {
    if (arg.startsWith('--')) {
      current = arg.slice(2);
      result[current] = true;
    } else if (current) {
      result[current] = arg;
      current = null;
    } else {
      result._.push(arg);
    }
  }
  
  return result;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const command = args._[0];
  
  if (!command || command === 'help' || command === '--help') {
    printUsage();
    process.exit(0);
  }
  
  try {
    switch (command) {
      case 'datasets':
      case 'list':
        await cmdDatasets();
        break;
        
      case 'create-dataset':
        if (!args.name) error('--name required');
        await cmdCreateDataset(args.name);
        break;
        
      case 'delete-dataset':
        if (!args.dataset) error('--dataset required');
        await cmdDeleteDataset(args.dataset);
        break;
        
      case 'documents':
      case 'docs':
        if (!args.dataset) error('--dataset required');
        await cmdDocuments(args.dataset);
        break;
        
      case 'upload':
        if (!args.dataset) error('--dataset required');
        if (!args.file) error('--file required');
        await cmdUpload(args.dataset, args.file);
        break;
        
      case 'parse':
        if (!args.dataset) error('--dataset required');
        if (!args['doc-ids']) error('--doc-ids required');
        await cmdParse(args.dataset, args['doc-ids'].split(','));
        break;
        
      case 'chat':
      case 'query':
        if (!args.dataset) error('--dataset required');
        if (!args.query) error('--query required');
        await cmdChat(args.dataset, args.query, args['top-k']);
        break;
        
      default:
        error(`Unknown command: ${command}`);
    }
  } catch (e) {
    error(e.message);
  }
}

async function cmdDatasets() {
  const result = await ragflow.listDatasets();
  const datasets = result.data || [];
  
  if (datasets.length === 0) {
    log('No datasets found', 'yellow');
    return;
  }
  
  log(`\n${c.green}Datasets (${datasets.length}):${c.reset}\n`);
  for (const ds of datasets) {
    console.log(`  ${c.cyan}${ds.id}${c.reset}  ${ds.name}`);
    console.log(`    ${c.dim}Chunks: ${ds.chunk_count || 0} | Docs: ${ds.document_count || 0}${c.reset}`);
  }
  console.log();
}

async function cmdCreateDataset(name) {
  const result = await ragflow.createDataset(name);
  log(`Created dataset: ${result.data?.id || result.id}`, 'green');
}

async function cmdDeleteDataset(datasetId) {
  await ragflow.deleteDataset(datasetId);
  log(`Deleted dataset: ${datasetId}`, 'green');
}

async function cmdDocuments(datasetId) {
  const result = await ragflow.listDocuments(datasetId);
  const docs = result.data || [];
  
  if (docs.length === 0) {
    log('No documents in dataset', 'yellow');
    return;
  }
  
  log(`\n${c.green}Documents (${docs.length}):${c.reset}\n`);
  for (const doc of docs) {
    console.log(`  ${c.cyan}${doc.id}${c.reset}  ${doc.name}`);
    console.log(`    ${c.dim}Status: ${doc.status || 'unknown'} | Chunks: ${doc.chunk_count || 0}${c.reset}`);
  }
  console.log();
}

async function cmdUpload(datasetId, filePath) {
  if (!fs.existsSync(filePath)) {
    error(`File not found: ${filePath}`);
  }
  
  log(`Uploading ${path.basename(filePath)}...`, 'cyan');
  const result = await ragflow.uploadDocument(datasetId, filePath);
  const docId = result.data?.[0]?.id;
  log(`Uploaded: ${docId}`, 'green');
}

async function cmdParse(datasetId, docIds) {
  log(`Triggering parsing for ${docIds.length} document(s)...`, 'cyan');
  await ragflow.triggerParsing(datasetId, docIds);
  log('Parsing started', 'green');
}

async function cmdChat(datasetId, query, topK = 10) {
  log(`\n${c.cyan}Query:${c.reset} ${query}\n`, 'cyan');
  
  const result = await ragflow.chat(datasetId, query, { top_k: parseInt(topK) });
  
  if (result.data) {
    // Show answer if available
    if (result.data.answer) {
      log(result.data.answer, 'green');
    }
    
    // Show sources
    const chunks = result.data.chunks || result.data || [];
    if (Array.isArray(chunks) && chunks.length > 0) {
      console.log(`\n${c.dim}--- Sources (${chunks.length}) ---${c.reset}`);
      for (const chunk of chunks.slice(0, 5)) {
        console.log(`\n${c.yellow}[${chunk.document_name || 'unknown'}]${c.reset}`);
        const content = chunk.content || chunk.text || '';
        console.log(content.substring(0, 300) + (content.length > 300 ? '...' : ''));
      }
    }
  }
  console.log();
}

main();
