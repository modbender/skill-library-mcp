#!/usr/bin/env node

/**
 * CivitAI Image Generation Script
 * 
 * Generates AI artwork using CivitAI's official JavaScript SDK
 * Usage: node get_illust.js [options]
 */

const fs = require('fs');
const path = require('path');

// Check if civitai package is available
let Civitai, Scheduler;
try {
  const civitai = require('civitai');
  Civitai = civitai.Civitai;
  Scheduler = civitai.Scheduler;
} catch (e) {
  console.error('Error: civitai package is not installed.');
  console.error('Please run: npm install civitai');
  process.exit(1);
}

// Parse command line arguments
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    prompt: '',
    negative: 'bad quality,worst quality,worst detail,sketch,censor',
    width: 832,
    height: 1216,
    seed: null,
    steps: 20,
    cfgScale: 5,
    model: 'urn:air:sdxl:checkpoint:civitai:827184@2514310',
    output: './output.png',
    sampler: 'Euler a',
    clipSkip: 2,
    loras: [], // Array of {urn, strength} for LoRA networks
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    const nextArg = args[i + 1];

    switch (arg) {
      case '--prompt':
        options.prompt = nextArg;
        i++;
        break;
      case '--negative':
        options.negative = nextArg;
        i++;
        break;
      case '--width':
        options.width = parseInt(nextArg, 10);
        i++;
        break;
      case '--height':
        options.height = parseInt(nextArg, 10);
        i++;
        break;
      case '--seed':
        options.seed = parseInt(nextArg, 10);
        i++;
        break;
      case '--steps':
        options.steps = parseInt(nextArg, 10);
        i++;
        break;
      case '--cfg-scale':
        options.cfgScale = parseFloat(nextArg);
        i++;
        break;
      case '--model':
        options.model = nextArg;
        i++;
        break;
      case '--output':
        options.output = nextArg;
        i++;
        break;
      case '--sampler':
        options.sampler = nextArg;
        i++;
        break;
      case '--clip-skip':
        options.clipSkip = parseInt(nextArg, 10);
        i++;
        break;
      case '--lora':
        // Format: "urn:air:sdxl:lora:civitai:XXX@YYY,strength" or just "urn,strength"
        const loraArg = nextArg;
        const parts = loraArg.split(',');
        const loraUrn = parts[0];
        const strength = parts[1] ? parseFloat(parts[1]) : 1.0;
        options.loras.push({ urn: loraUrn, strength });
        i++;
        break;
      case '--help':
      case '-h':
        showHelp();
        process.exit(0);
        break;
    }
  }

  return options;
}

function showHelp() {
  console.log(`
Usage: node get_illust.js [options]

Options:
  --prompt <text>      Main generation prompt (required)
                       (自动添加前缀: masterpiece,best quality,amazing quality,)
  --negative <text>    Negative prompt (default: "bad quality,worst quality,worst detail,sketch,censor")
  --width <number>     Image width (default: 832)
  --height <number>    Image height (default: 1216)
  --seed <number>      Random seed (default: random)
  --steps <number>     Sampling steps (default: 20)
  --cfg-scale <number> CFG scale (default: 5)
  --model <hash/name>  Model identifier (default: "urn:air:sdxl:checkpoint:civitai:827184@2514310")
  --sampler <name>     Sampler algorithm (default: "Euler a")
  --clip-skip <number> CLIP skip layers (default: 2)
  --output <path>      Output file path (default: "./output.png")
  --lora <urn,strength> Add LoRA network (can specify multiple times)
                       Format: "urn:air:sdxl:lora:civitai:XXX@YYY,strength"
                       Example: --lora "urn:air:sdxl:lora:civitai:162141@182559,0.8"
  --help, -h           Show this help message

Examples:
  基础生成 (使用默认SDXL模型和高质量前缀):
    node get_illust.js --prompt "1girl, red hair, blue eyes, maid outfit" --output maid.png

  高级设置:
    node get_illust.js \\
      --prompt "1girl, long silver hair, magical girl, cityscape at night" \\
      --negative "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, bad feet" \\
      --width 1024 \\
      --height 1536 \\
      --steps 28 \\
      --cfg-scale 6 \\
      --seed 42 \\
      --output magical_girl.png

  使用 LoRA:
    node get_illust.js \\
      --prompt "1girl, red hair, blue eyes, maid outfit, smile" \\
      --lora "urn:air:sdxl:lora:civitai:162141@182559,0.8" \\
      --output maid_with_lora.png

  使用多个 LoRA:
    node get_illust.js \\
      --prompt "1girl, cat ears, cute smile, IncrsAhri, multiple tails" \\
      --lora "urn:air:sd1:lora:civitai:162141@182559,1.0" \\
      --lora "urn:air:sd1:lora:civitai:176425@198856,0.6" \\
      --output multi_lora.png
`);
}

// Map sampler name to Scheduler enum
function getScheduler(samplerName) {
  const schedulerMap = {
    'Euler a': 'EULER_A',
    'Euler': 'EULER',
    'LMS': 'LMS',
    'Heun': 'HEUN',
    'DPM2': 'DPM2',
    'DPM2 a': 'DPM2_A',
    'DPM++ 2S a': 'DPM2_SA',
    'DPM++ 2M': 'DPM2_M',
    'DPM++ SDE': 'DPM_SDE',
    'DPM fast': 'DPM_FAST',
    'DPM adaptive': 'DPM_ADAPTIVE',
    'LMS Karras': 'LMS_KARRAS',
    'DPM2 Karras': 'DPM2_KARRAS',
    'DPM2 a Karras': 'DPM2_A_KARRAS',
    'DPM++ 2S a Karras': 'DPM2_SA_KARRAS',
    'DPM++ 2M Karras': 'DPM2_M_KARRAS',
    'DPM++ SDE Karras': 'DPM_SDE_KARRAS',
    'DDIM': 'DDIM',
    'PLMS': 'PLMS',
    'UniPC': 'UNIPC',
    'LCM': 'LCM',
    'DDPM': 'DDPM',
    'DEIS': 'DEIS',
  };
  
  return schedulerMap[samplerName] || 'EULER_A';
}

async function downloadImage(url, outputPath) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to download image: ${response.status} ${response.statusText}`);
  }
  
  const buffer = await response.arrayBuffer();
  fs.writeFileSync(outputPath, Buffer.from(buffer));
}

async function main() {
  const options = parseArgs();

  // Validate required parameters for new generation
  if (!options.prompt) {
    console.error('Error: --prompt is required');
    console.error('Use --help for usage information');
    process.exit(1);
  }

  // Check for API token
  const apiToken = process.env.CIVITAI_API_TOKEN;
  if (!apiToken) {
    console.error('Error: CIVITAI_API_TOKEN environment variable is not set');
    console.error('Please set your CivitAI API token:');
    console.error('  export CIVITAI_API_TOKEN="your_token_here"');
    process.exit(1);
  }

  // Initialize CivitAI client
  const civitai = new Civitai({
    auth: apiToken,
  });

  console.log('Generating image with the following settings:');
  console.log(`  Prompt: ${options.prompt}`);
  console.log(`  Negative: ${options.negative}`);
  console.log(`  Size: ${options.width}x${options.height}`);
  console.log(`  Steps: ${options.steps}`);
  console.log(`  CFG Scale: ${options.cfgScale}`);
  if (options.seed) console.log(`  Seed: ${options.seed}`);
  console.log(`  Model: ${options.model}`);
  console.log(`  Sampler: ${options.sampler}`);
  console.log(`  CLIP Skip: ${options.clipSkip}`);
  if (options.loras.length > 0) {
    console.log(`  LoRAs:`);
    options.loras.forEach((lora, idx) => {
      console.log(`    [${idx + 1}] ${lora.urn} (strength: ${lora.strength})`);
    });
  }
  console.log('');

  try {
    // Add default quality tags to prompt if not already present
    const qualityPrefix = 'masterpiece,best quality,amazing quality,';
    let prompt = options.prompt;
    if (!prompt.includes('masterpiece') && !prompt.includes('best quality')) {
      prompt = qualityPrefix + prompt;
    }

    // Map sampler to Scheduler
    const scheduler = getScheduler(options.sampler);

    // Build input for SDK
    const input = {
      model: options.model,
      params: {
        prompt: prompt,
        negativePrompt: options.negative,
        scheduler: Scheduler[scheduler] || Scheduler.EulerA,
        steps: options.steps,
        cfgScale: options.cfgScale,
        width: options.width,
        height: options.height,
        seed: options.seed || undefined,
        clipSkip: options.clipSkip,
      }
    };

    // Add LoRAs if specified
    if (options.loras.length > 0) {
      input.additionalNetworks = {};
      options.loras.forEach(lora => {
        input.additionalNetworks[lora.urn] = {
          strength: lora.strength,
        };
      });
    }

    console.log('Submitting generation job...');
    
    // Use SDK to generate image - always wait for completion (default behavior)
    const response = await civitai.image.fromText(input, true);
    
    // Long polling completed - response has the result
    console.log('');
    console.log('✓ Image generated successfully!');
    console.log(`Job ID: ${response.jobs?.[0]?.jobId || 'N/A'}`);
    console.log(`Cost: ${response.jobs?.[0]?.cost || 'N/A'}`);
    
    // Get the result from the response
    const jobResult = response.jobs?.[0]?.result;
    let result = null;
    
    if (Array.isArray(jobResult) && jobResult.length > 0) {
      result = jobResult[0];
    } else if (jobResult) {
      result = jobResult;
    }
    
    if (result?.blobUrl) {
      console.log(`Image URL: ${result.blobUrl}`);
      console.log('');
      
      // Download the image
      const outputPath = path.resolve(options.output);
      console.log(`Downloading image to: ${outputPath}`);
      await downloadImage(result.blobUrl, outputPath);
      console.log('Image saved successfully!');
      console.log(`\nOutput: ${outputPath}`);
    } else {
      console.log('No image URL in response.');
      console.log('Full response:', JSON.stringify(response, null, 2));
    }

  } catch (error) {
    console.error('Error generating image:', error.message);
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
    }
    process.exit(1);
  }
}

// Run main function
main().catch((error) => {
  console.error('Unexpected error:', error);
  process.exit(1);
});
