/**
 * ONNX MiniLM Embedding - Pure local, lightweight
 * ~20MB model, no external services
 */

const fs = require('fs').promises;
const path = require('path');
const os = require('os');
const { execSync } = require('child_process');

class ONNXEmbedding {
  constructor(config = {}) {
    this.modelName = config.modelName || 'all-MiniLM-L6-v2';
    this.cacheDir = config.cacheDir || path.join(os.homedir(), '.cache', 'elite-memory');
    this.modelPath = path.join(this.cacheDir, 'model.onnx');
    this.tokenizerPath = path.join(this.cacheDir, 'tokenizer.json');
    this.ort = null;
    this.tokenizer = null;
  }

  async init() {
    if (this.ort) return;

    // Ensure cache directory exists
    await fs.mkdir(this.cacheDir, { recursive: true });

    // Check if model exists, if not download
    await this.downloadModel();

    // Load ONNX Runtime - try multiple methods
    await this.loadONNX();
  }

  async downloadModel() {
    const modelExists = await this.fileExists(this.modelPath);
    const tokenizerExists = await this.fileExists(this.tokenizerPath);

    if (modelExists && tokenizerExists) {
      console.log('✅ ONNX MiniLM model already cached');
      return;
    }

    console.log('⬇️  Downloading ONNX MiniLM model (~20MB)...');
    
    // Use HF-Mirror for China access
    const baseUrl = 'https://hf-mirror.com/Xenova/all-MiniLM-L6-v2/resolve/main';
    
    try {
      // Download model
      if (!modelExists) {
        execSync(
          `curl -L --retry 3 --max-time 180 -o "${this.modelPath}" "${baseUrl}/onnx/model_quantized.onnx"`,
          { timeout: 200000, stdio: 'inherit' }
        );
      }

      // Download tokenizer
      if (!tokenizerExists) {
        execSync(
          `curl -L --retry 3 --max-time 60 -o "${this.tokenizerPath}" "${baseUrl}/tokenizer.json"`,
          { timeout: 80000, stdio: 'inherit' }
        );
      }

      console.log('✅ Model downloaded successfully');
    } catch (err) {
      console.error('❌ Failed to download model:', err.message);
      throw err;
    }
  }

  async loadONNX() {
    // Try to load onnxruntime-node
    try {
      this.ort = require('onnxruntime-node');
      console.log('✅ Using onnxruntime-node');
    } catch (e) {
      // Try alternative: use transformers.js
      try {
        const transformers = require('@xenova/transformers');
        this.pipeline = await transformers.pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2', {
          quantized: true,
          cache_dir: this.cacheDir
        });
        console.log('✅ Using transformers.js');
        return;
      } catch (e2) {
        console.error('❌ No ONNX runtime available');
        throw new Error('Please install: npm install onnxruntime-node OR npm install @xenova/transformers');
      }
    }

    // Load tokenizer
    const tokenizerData = await fs.readFile(this.tokenizerPath, 'utf-8');
    this.tokenizer = JSON.parse(tokenizerData);
  }

  async embed(text) {
    await this.init();

    if (this.pipeline) {
      // Use transformers.js
      const result = await this.pipeline(text, { 
        pooling: 'mean', 
        normalize: true 
      });
      return Array.from(result.data);
    }

    // Use ONNX Runtime directly
    return this.embedWithONNX(text);
  }

  async embedWithONNX(text) {
    // Simple tokenization (in production, use the actual tokenizer)
    const tokens = this.simpleTokenize(text);
    
    // Create input tensors
    const inputIds = new BigInt64Array(tokens.map(t => BigInt(t)));
    const attentionMask = new BigInt64Array(tokens.map(() => BigInt(1)));

    const session = await this.ort.InferenceSession.create(this.modelPath);
    
    const feeds = {
      input_ids: new this.ort.Tensor('int64', inputIds, [1, tokens.length]),
      attention_mask: new this.ort.Tensor('int64', attentionMask, [1, tokens.length])
    };

    const results = await session.run(feeds);
    const output = results.sentence_embedding || results.last_hidden_state;
    
    // Mean pooling and normalize
    return this.poolAndNormalize(output);
  }

  simpleTokenize(text) {
    // Simplified BPE tokenization
    // In production, use the actual tokenizer from the model
    const normalized = text.toLowerCase().trim();
    const tokens = [101]; // [CLS]
    
    const words = normalized.split(/\s+/);
    for (const word of words) {
      // Simple word hashing for demo
      tokens.push(...this.wordToTokens(word));
    }
    
    tokens.push(102); // [SEP]
    
    // Truncate to 128 tokens
    if (tokens.length > 128) {
      tokens.length = 127;
      tokens.push(102);
    }
    
    return tokens;
  }

  wordToTokens(word) {
    // Simplified - should use actual BPE
    const tokens = [];
    let i = 0;
    while (i < word.length) {
      // Simple character-based tokenization
      const char = word[i];
      const code = char.charCodeAt(0);
      // Map to vocabulary range (1000-30000)
      tokens.push(1000 + (code % 29000));
      i++;
    }
    return tokens.length > 0 ? tokens : [100]; // [UNK]
  }

  poolAndNormalize(output) {
    const data = output.data;
    const dims = output.dims;
    const seqLen = dims[1];
    const hiddenSize = dims[2] || 384;
    
    // Mean pooling
    const pooled = new Array(hiddenSize).fill(0);
    for (let i = 0; i < seqLen; i++) {
      for (let j = 0; j < hiddenSize; j++) {
        pooled[j] += data[i * hiddenSize + j];
      }
    }
    
    const mean = pooled.map(v => v / seqLen);
    
    // L2 normalize
    const norm = Math.sqrt(mean.reduce((sum, v) => sum + v * v, 0));
    if (norm > 0) {
      return mean.map(v => v / norm);
    }
    
    return mean;
  }

  async fileExists(filePath) {
    try {
      await fs.access(filePath);
      return true;
    } catch {
      return false;
    }
  }
}

module.exports = { ONNXEmbedding };
