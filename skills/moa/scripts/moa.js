const axios = require('axios');

async function handle({ prompt, tier = 'paid' }) {
  // 1. Configuration
  const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY;
  if (!OPENROUTER_API_KEY) {
    return "Error: OPENROUTER_API_KEY environment variable not set";
  }
  
  const BASE_URL = "https://openrouter.ai/api/v1/chat/completions";

  // Model tiers
  const MODELS = {
    paid: {
      proposers: [
        "moonshotai/kimi-k2.5",      // Kimi 2.5 (~23s)
        "z-ai/glm-5",                 // GLM 5 (~36s)
        "minimax/minimax-m2.5"        // MiniMax 2.5 (~64s)
      ],
      aggregator: "moonshotai/kimi-k2.5",
      maxTokens: 1200,
      aggregatorMaxTokens: 2500
    },
    free: {
      proposers: [
        "meta-llama/llama-3.3-70b-instruct:free",
        "google/gemini-2.0-flash-exp:free",
        "mistralai/mistral-small-24b-instruct-2501:free",
        "nvidia/llama-3.1-nemotron-70b-instruct:free",
        "qwen/qwen-2.5-72b-instruct:free"
      ],
      aggregator: "meta-llama/llama-3.3-70b-instruct:free",
      maxTokens: 500,
      aggregatorMaxTokens: 1500
    }
  };

  const config = MODELS[tier] || MODELS.paid;
  const { proposers, aggregator, maxTokens, aggregatorMaxTokens } = config;

  console.log(`[MoA] Tier: ${tier.toUpperCase()} | Models: ${proposers.length}`);
  console.log(`[MoA] Prompt: "${prompt.substring(0, 60)}..."\n`);

  // 2. Fetch responses from all models in parallel
  const fetchResponse = async (model) => {
    const startTime = Date.now();
    try {
      const response = await axios.post(BASE_URL, {
        model: model,
        messages: [{ role: "user", content: prompt }],
        max_tokens: maxTokens
      }, {
        headers: {
          "Authorization": `Bearer ${OPENROUTER_API_KEY}`,
          "HTTP-Referer": "https://github.com/openclaw/openclaw",
          "Content-Type": "application/json"
        },
        timeout: 180000
      });
      const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
      const modelName = model.split('/')[1];
      console.log(`✓ ${modelName} responded (${elapsed}s)`);
      return { model, content: response.data.choices[0].message.content };
    } catch (error) {
      const modelName = model.split('/')[1];
      console.log(`✗ ${modelName}: ${error.response?.data?.error?.message || error.message}`);
      return { model, content: `Error: ${error.message}` };
    }
  };

  const results = await Promise.all(proposers.map(fetchResponse));
  const successCount = results.filter(r => !r.content.startsWith('Error')).length;
  
  console.log(`\n[MoA] Got ${successCount}/${proposers.length} responses. Synthesizing...\n`);

  // 3. Construct the Synthesis Prompt
  const synthesisPrompt = `
You are an expert Aggregator synthesizing insights from multiple AI models.

ORIGINAL QUESTION:
"${prompt}"

RESPONSES FROM ${successCount} MODELS:

${results.filter(r => !r.content.startsWith('Error')).map(r => `--- ${r.model} ---\n${r.content}`).join('\n\n')}

INSTRUCTIONS:
1. Identify the most valuable and unique insights from each response.
2. Resolve any contradictions by prioritizing logical consistency and practical feasibility.
3. Synthesize into a single, definitive answer that captures the best of all responses.
4. Structure your answer clearly with specific recommendations.
5. If a model provided weak or irrelevant content, deprioritize it.
`;

  // 4. Send to Aggregator for the final output
  try {
    const finalResponse = await axios.post(BASE_URL, {
      model: aggregator,
      messages: [{ role: "user", content: synthesisPrompt }],
      max_tokens: aggregatorMaxTokens
    }, {
      headers: {
        "Authorization": `Bearer ${OPENROUTER_API_KEY}`,
        "Content-Type": "application/json"
      },
      timeout: 180000
    });
    return finalResponse.data.choices[0].message.content;
  } catch (error) {
    return `MoA Synthesis Error: ${error.response?.data?.error?.message || error.message}`;
  }
}

// CLI support
if (require.main === module) {
  const args = process.argv.slice(2);
  
  // Check for --free flag
  let tier = 'paid';
  const freeIndex = args.indexOf('--free');
  if (freeIndex !== -1) {
    tier = 'free';
    args.splice(freeIndex, 1);
  }
  
  const prompt = args.join(' ');
  if (!prompt) {
    console.error('Usage: node moa.js "Your question here" [--free]');
    console.error('  Default: Uses paid models (Kimi 2.5, GLM 5, MiniMax 2.5)');
    console.error('  --free:  Uses free models (Llama, Gemini, Mistral, etc.)');
    process.exit(1);
  }
  
  handle({ prompt, tier }).then(result => {
    console.log('='.repeat(60));
    console.log(`MoA SYNTHESIS (${tier.toUpperCase()} TIER)`);
    console.log('='.repeat(60) + '\n');
    console.log(result);
  });
}

module.exports = { handle };
