#!/usr/bin/env node
/**
 * Stirling-PDF CLI Wrapper
 * Usage: node pdf.js <operation> <input> [options]
 * 
 * Required environment variables:
 *   STIRLING_PDF_URL - Your Stirling-PDF instance URL
 *   STIRLING_API_KEY - API key (if authentication is enabled)
 */

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

// Config from environment only (no file fallback)
const BASE_URL = process.env.STIRLING_PDF_URL || 'http://localhost:8080';
const API_KEY = process.env.STIRLING_API_KEY || '';

const operations = {
  merge: {
    endpoint: '/api/v1/general/merge-pdfs',
    description: 'Merge multiple PDFs into one',
    multipleFiles: true
  },
  split: {
    endpoint: '/api/v1/general/split-pages',
    description: 'Split PDF into individual pages',
    multipleFiles: false
  },
  compress: {
    endpoint: '/api/v1/misc/compress-pdf',
    description: 'Reduce PDF file size',
    multipleFiles: false
  },
  ocr: {
    endpoint: '/api/v1/misc/ocr-pdf',
    description: 'Add OCR layer to scanned PDF',
    multipleFiles: false
  },
  'pdf-to-image': {
    endpoint: '/api/v1/convert/pdf/img',
    description: 'Convert PDF to images',
    multipleFiles: false
  },
  'image-to-pdf': {
    endpoint: '/api/v1/convert/img/pdf',
    description: 'Convert images to PDF',
    multipleFiles: true
  },
  'add-watermark': {
    endpoint: '/api/v1/security/add-watermark',
    description: 'Add watermark to PDF',
    multipleFiles: false,
    extraParams: ['watermarkText', 'fontSize', 'opacity', 'rotation']
  },
  'add-password': {
    endpoint: '/api/v1/security/add-password',
    description: 'Password protect PDF',
    multipleFiles: false,
    extraParams: ['password']
  },
  'remove-password': {
    endpoint: '/api/v1/security/remove-password',
    description: 'Remove password from PDF',
    multipleFiles: false,
    extraParams: ['password']
  },
  'pdf-to-word': {
    endpoint: '/api/v1/convert/pdf/word',
    description: 'Convert PDF to Word',
    multipleFiles: false
  },
  'word-to-pdf': {
    endpoint: '/api/v1/convert/file/pdf',
    description: 'Convert Word/Office to PDF',
    multipleFiles: false
  },
  'extract-text': {
    endpoint: '/api/v1/convert/pdf/text',
    description: 'Extract text from PDF',
    multipleFiles: false
  },
  info: {
    endpoint: '/api/v1/analysis/basic-info',
    description: 'Get PDF metadata/info',
    multipleFiles: false
  },
  'pdf-to-html': {
    endpoint: '/api/v1/convert/pdf/html',
    description: 'Convert PDF to HTML',
    multipleFiles: false
  },
  'html-to-pdf': {
    endpoint: '/api/v1/convert/html/pdf',
    description: 'Convert HTML to PDF',
    multipleFiles: false
  },
  'pdf-to-pdfa': {
    endpoint: '/api/v1/convert/pdf/pdfa',
    description: 'Convert PDF to PDF/A (archive)',
    multipleFiles: false
  },
  'add-stamp': {
    endpoint: '/api/v1/misc/add-stamp',
    description: 'Add stamp to PDF',
    multipleFiles: false
  },
  'rotate': {
    endpoint: '/api/v1/general/rotate-pdf',
    description: 'Rotate PDF pages',
    multipleFiles: false
  },
  'repair': {
    endpoint: '/api/v1/misc/repair',
    description: 'Repair corrupted PDF',
    multipleFiles: false
  },
  'sanitize': {
    endpoint: '/api/v1/security/sanitize-pdf',
    description: 'Sanitize PDF (remove metadata/scripts)',
    multipleFiles: false
  },
  'redact': {
    endpoint: '/api/v1/security/redact',
    description: 'Redact sensitive content',
    multipleFiles: false
  }
};

function printHelp() {
  console.log('Stirling-PDF CLI Wrapper\n');
  console.log('Usage: node pdf.js <operation> <input> [options]\n');
  console.log('Environment Variables:');
  console.log('  STIRLING_PDF_URL   - Your instance URL (default: http://localhost:8080)');
  console.log('  STIRLING_API_KEY   - API key if auth is enabled\n');
  console.log('Operations:');
  console.log('  merge           - Merge multiple PDFs');
  console.log('  split           - Split PDF into pages');
  console.log('  compress        - Reduce file size');
  console.log('  ocr             - Make scanned PDF searchable');
  console.log('  pdf-to-image    - Convert PDF to images');
  console.log('  image-to-pdf    - Convert images to PDF');
  console.log('  pdf-to-word     - Convert PDF to Word');
  console.log('  word-to-pdf     - Convert Word/Office to PDF');
  console.log('  pdf-to-html     - Convert PDF to HTML');
  console.log('  html-to-pdf     - Convert HTML to PDF');
  console.log('  pdf-to-pdfa     - Convert to PDF/A (archive)');
  console.log('  extract-text    - Extract text from PDF');
  console.log('  add-watermark   - Add watermark (-t "text")');
  console.log('  add-stamp       - Add stamp');
  console.log('  add-password    - Password protect (-p "pwd")');
  console.log('  remove-password - Remove password (-p "pwd")');
  console.log('  rotate          - Rotate pages');
  console.log('  repair          - Repair corrupted PDF');
  console.log('  sanitize        - Remove metadata/scripts');
  console.log('  redact          - Redact sensitive content');
  console.log('  info            - Get PDF metadata');
  console.log('\nOptions:');
  console.log('  -o, --output <file>   Output file path');
  console.log('  -p, --password <pwd>  Password');
  console.log('  -t, --text <text>     Watermark text');
  console.log('  --help                Show this help');
}

function parseArgs(args) {
  const result = {
    operation: null,
    files: [],
    output: null,
    extra: {}
  };

  let i = 0;
  while (i < args.length) {
    const arg = args[i];
    if (arg === '-o' || arg === '--output') {
      result.output = args[++i];
    } else if (arg === '-p' || arg === '--password') {
      result.extra.password = args[++i];
    } else if (arg === '-t' || arg === '--text') {
      result.extra.watermarkText = args[++i];
    } else if (arg === '--help' || arg === '-h') {
      printHelp();
      process.exit(0);
    } else if (!arg.startsWith('-')) {
      if (!result.operation) {
        result.operation = arg;
      } else {
        result.files.push(arg);
      }
    }
    i++;
  }

  return result;
}

function runCurl(op, files, output, extra = {}) {
  return new Promise((resolve, reject) => {
    const args = ['-s', '-X', 'POST', `${BASE_URL}${op.endpoint}`];
    
    // Add headers
    args.push('-H', 'Content-Type: multipart/form-data');
    if (API_KEY) {
      args.push('-H', `X-API-KEY: ${API_KEY}`);
    }

    // Add file inputs
    for (const file of files) {
      const absPath = path.resolve(file);
      if (!fs.existsSync(absPath)) {
        reject(new Error(`File not found: ${file}`));
        return;
      }
      args.push('-F', `fileInput=@${absPath}`);
    }

    // Add extra parameters
    for (const [key, value] of Object.entries(extra)) {
      if (value !== undefined && value !== null) {
        args.push('-F', `${key}=${value}`);
      }
    }

    // Default extra params for specific operations
    if (op.endpoint.includes('ocr')) {
      args.push('-F', 'languages=eng');
    }
    if (op.endpoint.includes('add-watermark')) {
      if (!extra.watermarkText) {
        reject(new Error('Watermark text required. Use -t "your text"'));
        return;
      }
      if (!extra.fontSize) args.push('-F', 'fontSize=30');
      if (!extra.opacity) args.push('-F', 'opacity=0.5');
      if (!extra.rotation) args.push('-F', 'rotation=45');
    }

    // Output
    if (output) {
      args.push('-o', path.resolve(output));
    }

    const curl = spawn('curl', args);
    
    let stderr = '';
    curl.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    curl.on('close', (code) => {
      if (code === 0) {
        if (output) {
          console.log(`✅ Output saved to: ${output}`);
        }
        resolve();
      } else {
        reject(new Error(`curl exited with code ${code}: ${stderr}`));
      }
    });

    curl.on('error', (err) => {
      reject(err);
    });

    // Pipe stdout to process stdout for non-file output
    if (!output) {
      curl.stdout.pipe(process.stdout);
    }
  });
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    printHelp();
    process.exit(0);
  }

  const parsed = parseArgs(args);

  if (!parsed.operation) {
    console.error('Error: No operation specified');
    printHelp();
    process.exit(1);
  }

  const op = operations[parsed.operation];
  if (!op) {
    console.error(`Error: Unknown operation "${parsed.operation}"`);
    console.log('Run with --help for available operations');
    process.exit(1);
  }

  if (parsed.files.length === 0) {
    console.error('Error: No input files specified');
    process.exit(1);
  }

  try {
    await runCurl(op, parsed.files, parsed.output, parsed.extra);
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

main();
