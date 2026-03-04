#!/usr/bin/env node
const axios = require('axios');

const API_KEY = process.env.KIE_API_KEY;
const BASE_URL = 'https://api.kie.ai/api/v1';

const client = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Authorization': `Bearer ${API_KEY}`,
    'Content-Type': 'application/json'
  }
});

async function createVideoTask(prompt, options = {}) {
  const payload = {
    model: options.model || 'kling-2.6/text-to-video',
    input: {
      prompt: prompt,
      sound: options.sound || false,
      aspect_ratio: options.aspectRatio || '16:9',
      duration: String(options.duration || 5)
    }
  };

  if (options.callbackUrl) {
    payload.callBackUrl = options.callbackUrl;
  }

  try {
    const response = await client.post('/jobs/createTask', payload);
    return response.data;
  } catch (error) {
    console.error('Error creating task:', error.response?.data || error.message);
    throw error;
  }
}

async function getTaskStatus(taskId) {
  try {
    const response = await client.get(`/jobs/recordInfo?taskId=${taskId}`);
    return response.data;
  } catch (error) {
    console.error('Error getting task:', error.response?.data || error.message);
    throw error;
  }
}

async function getCredits() {
  try {
    const response = await client.get('/user/credits');
    return response.data;
  } catch (error) {
    console.error('Error getting credits:', error.response?.data || error.message);
    throw error;
  }
}

async function waitForCompletion(taskId, maxWaitMs = 300000, pollIntervalMs = 10000) {
  const startTime = Date.now();
  
  while (Date.now() - startTime < maxWaitMs) {
    const result = await getTaskStatus(taskId);
    const status = result.data?.state;
    
    if (status === 'completed' || status === 'success') {
      return result.data;
    }
    
    if (status === 'failed' || status === 'error') {
      throw new Error(`Task failed: ${result.data?.failMsg || 'Unknown error'}`);
    }
    
    console.log(`Status: ${status}... (${Math.round((Date.now() - startTime) / 1000)}s)`);
    await new Promise(resolve => setTimeout(resolve, pollIntervalMs));
  }
  
  throw new Error('Task timed out after 5 minutes');
}

async function generateVideo(prompt, options = {}) {
  console.log(`Creating video: "${prompt.substring(0, 50)}..."`);
  
  const result = await createVideoTask(prompt, options);
  
  if (result.code !== 200) {
    throw new Error(`API error: ${result.msg}`);
  }
  
  const taskId = result.data.taskId;
  console.log(`Task ID: ${taskId}`);
  
  if (options.wait !== false) {
    console.log('Waiting for completion (can take 1-5 min)...');
    const final = await waitForCompletion(taskId);
    return final;
  }
  
  return result.data;
}

// CLI interface
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  if (!API_KEY) {
    console.error('Error: KIE_API_KEY environment variable not set');
    process.exit(1);
  }
  
  switch (command) {
    case 'generate':
    case 'create': {
      const prompt = args.slice(1).join(' ');
      if (!prompt) {
        console.error('Usage: kling generate <prompt>');
        process.exit(1);
      }
      const result = await generateVideo(prompt);
      console.log(JSON.stringify(result, null, 2));
      break;
    }
    
    case 'status': {
      const taskId = args[1];
      if (!taskId) {
        console.error('Usage: kling status <task_id>');
        process.exit(1);
      }
      const result = await getTaskStatus(taskId);
      console.log(JSON.stringify(result.data, null, 2));
      break;
    }
    
    case 'quick': {
      const prompt = args.slice(1).join(' ');
      if (!prompt) {
        console.error('Usage: kling quick <prompt>');
        process.exit(1);
      }
      const result = await generateVideo(prompt, { wait: false });
      console.log(JSON.stringify(result, null, 2));
      break;
    }
    
    case 'credits': {
      const result = await getCredits();
      console.log(JSON.stringify(result.data, null, 2));
      break;
    }
    
    default:
      console.log(`Kling Video Generator (via Kie.ai)

Usage:
  kling generate <prompt>  - Generate video and wait for completion
  kling quick <prompt>     - Start generation, return task ID immediately
  kling status <task_id>   - Check task status
  kling credits            - Check credit balance

Examples:
  kling generate "A fitness coach celebrating with a client"
  kling quick "Professional gym environment with happy members"
  kling status a37ea5f5824fc8931966a87ee3bef36b
`);
  }
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
