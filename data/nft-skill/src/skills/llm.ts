/**
 * LLM Provider Skill
 * Supports OpenRouter (free), Groq (free), and Ollama (local)
 */
import axios from 'axios';

type Provider = 'openrouter' | 'groq' | 'ollama';

interface LLMConfig {
  provider: Provider;
  model: string;
  apiKey?: string;
  baseUrl?: string;
}

function getConfig(): LLMConfig {
  const provider = (process.env.LLM_PROVIDER as Provider) || 'openrouter';
  
  switch (provider) {
    case 'groq':
      return {
        provider: 'groq',
        model: process.env.LLM_MODEL || 'llama-3.1-8b-instant',
        apiKey: process.env.GROQ_API_KEY
      };
    case 'ollama':
      return {
        provider: 'ollama',
        model: process.env.LLM_MODEL || 'llama3.2',
        baseUrl: process.env.OLLAMA_BASE_URL || 'http://localhost:11434'
      };
    default:
      return {
        provider: 'openrouter',
        model: process.env.LLM_MODEL || 'meta-llama/llama-3.2-3b-instruct:free',
        apiKey: process.env.OPENROUTER_API_KEY
      };
  }
}

export async function generateArtConcept(theme: string, generation: number): Promise<string> {
  const config = getConfig();
  const prompt = `Generate a creative art concept for an NFT. Theme: "${theme}". Generation level: ${generation}.
Keep it under 100 words. Describe visual elements, colors, and mood. Be poetic but specific.`;

  const response = await callLLM(prompt, config);
  return response || `Abstract interpretation of ${theme} featuring flowing shapes and vibrant colors`;
}

export async function generateTweetText(context: string, metadata: Record<string, any>): Promise<string> {
  const config = getConfig();
  const prompt = `Write an engaging tweet about ${context}.
Context: ${JSON.stringify(metadata)}
Max 250 chars. Include emojis. Be artistic and slightly mysterious.`;

  const response = await callLLM(prompt, config);
  return response || `New art created: ${metadata.message || 'Check it out'} 🎨`;
}

async function callLLM(prompt: string, config: LLMConfig): Promise<string | null> {
  try {
    if (config.provider === 'ollama') {
      const res = await axios.post(`${config.baseUrl}/api/generate`, {
        model: config.model,
        prompt: prompt,
        stream: false
      });
      return res.data.response?.trim();
    }
    
    if (config.provider === 'groq') {
      const res = await axios.post('https://api.groq.com/openai/v1/chat/completions', {
        model: config.model,
        messages: [{ role: 'user', content: prompt }],
        temperature: 0.7
      }, {
        headers: { Authorization: `Bearer ${config.apiKey}` }
      });
      return res.data.choices[0]?.message?.content?.trim();
    }
    
    // OpenRouter (default)
    const res = await axios.post('https://openrouter.ai/api/v1/chat/completions', {
      model: config.model,
      messages: [{ role: 'user', content: prompt }]
    }, {
      headers: {
        Authorization: `Bearer ${config.apiKey}`,
        'HTTP-Referer': 'https://github.com/ai-artist-agent',
        'X-Title': 'AI Artist Agent'
      }
    });
    return res.data.choices[0]?.message?.content?.trim();
    
  } catch (error: any) {
    console.error(`[LLM] ${config.provider} error:`, error.message);
    return null;
  }
}
