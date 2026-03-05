const axios = require('axios');

async function runMoA(prompt) {
  const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY;
  if (!OPENROUTER_API_KEY) {
    console.error("Need OPENROUTER_API_KEY");
    process.exit(1);
  }
  
  const BASE_URL = "https://openrouter.ai/api/v1/chat/completions";

  // Correct model IDs
  const proposerModels = [
    "moonshotai/kimi-k2.5",       // Kimi 2.5
    "minimax/minimax-m2.5",       // MiniMax 2.5
    "z-ai/glm-5"                  // GLM 5
  ];

  const aggregatorModel = "moonshotai/kimi-k2.5";

  console.log(`[MoA-Paid] Querying 3 models: Kimi 2.5, MiniMax 2.5, GLM 5...`);
  console.log(`[MoA-Paid] Prompt: "${prompt.substring(0, 80)}..."\n`);

  const fetchResponse = async (model) => {
    const startTime = Date.now();
    try {
      const response = await axios.post(BASE_URL, {
        model: model,
        messages: [{ role: "user", content: prompt }],
        max_tokens: 1200
      }, {
        headers: {
          "Authorization": `Bearer ${OPENROUTER_API_KEY}`,
          "HTTP-Referer": "https://github.com/openclaw/openclaw",
          "Content-Type": "application/json"
        },
        timeout: 180000
      });
      const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
      console.log(`✓ ${model} responded (${elapsed}s)`);
      return { model, content: response.data.choices[0].message.content };
    } catch (error) {
      console.log(`✗ ${model}: ${error.response?.data?.error?.message || error.message}`);
      return { model, content: `Error: ${error.message}` };
    }
  };

  const results = await Promise.all(proposerModels.map(fetchResponse));
  const successCount = results.filter(r => !r.content.startsWith('Error')).length;
  console.log(`\n[MoA-Paid] Got ${successCount}/3 responses. Synthesizing with Kimi 2.5...\n`);

  const synthesisPrompt = `
You are an expert Aggregator synthesizing insights from multiple AI models.

ORIGINAL QUESTION:
"${prompt}"

RESPONSES FROM 3 MODELS:

${results.map(r => `--- ${r.model} ---\n${r.content}`).join('\n\n')}

INSTRUCTIONS:
1. Identify the most valuable and unique insights from each response
2. Resolve contradictions by prioritizing logical consistency and practical feasibility
3. Synthesize into a single, definitive answer that captures the best of all three
4. Structure your answer clearly with specific recommendations
5. If a model failed, ignore it
`;

  try {
    const finalResponse = await axios.post(BASE_URL, {
      model: aggregatorModel,
      messages: [{ role: "user", content: synthesisPrompt }],
      max_tokens: 2500
    }, {
      headers: {
        "Authorization": `Bearer ${OPENROUTER_API_KEY}`,
        "Content-Type": "application/json"
      },
      timeout: 180000
    });
    return finalResponse.data.choices[0].message.content;
  } catch (error) {
    return `Synthesis Error: ${error.response?.data?.error?.message || error.message}`;
  }
}

const prompt = `What web2 services (particularly SaaS companies) would be significantly better (faster and cheaper) if rebuilt using a combination of Arweave and Filecoin for decentralized storage?

Focus on:
1. Services with LARGE Total Addressable Market (TAM)
2. Services that are relatively EASY to build
3. Concrete examples of why decentralized storage makes them faster OR cheaper
4. Be specific about which aspects use Arweave (permanent storage) vs Filecoin (retrievable storage)

Give me 3-5 specific SaaS categories with business model insights.`;

runMoA(prompt).then(result => {
  console.log('='.repeat(60));
  console.log('MoA SYNTHESIS (Kimi 2.5 + MiniMax 2.5 + GLM 5)');
  console.log('='.repeat(60) + '\n');
  console.log(result);
});
