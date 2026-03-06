// lib/llm.js – OpenRouter API abstraction
// All model calls go through here. Zero local models.
const { getConfig } = require('./db');

async function chat({ role, messages, json = false, maxTokens = 2000 }) {
  const config = getConfig();
  const modelConfig = config.models[role];
  if (!modelConfig) throw new Error(`Unknown model role: ${role}`);

  const model = modelConfig.model;
  const apiKey = config.openrouter.apiKey;
  const baseUrl = config.openrouter.baseUrl;

  if (!apiKey || apiKey.includes('YOUR_KEY') || apiKey.includes('DEIN_KEY') || apiKey.length < 20) {
    throw new Error('OpenRouter API key not configured. Edit config.json.');
  }

  const body = {
    model,
    messages,
    max_tokens: maxTokens,
    temperature: role === 'initiative' ? 0.7 : 0.3,
  };

  if (json) {
    body.response_format = { type: 'json_object' };
  }

  let lastError = null;
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const res = await fetch(`${baseUrl}/chat/completions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
          'HTTP-Referer': 'https://github.com/Emphaiser/secondmind',
          'X-Title': 'SecondMind Skill'
        },
        body: JSON.stringify(body)
      });

      if (!res.ok) {
        const errText = await res.text();
        // Rate limit → wait and retry
        if (res.status === 429) {
          const wait = (attempt + 1) * 5000;
          console.log(`[LLM] Rate limited, waiting ${wait/1000}s...`);
          await sleep(wait);
          continue;
        }
        throw new Error(`OpenRouter ${res.status}: ${errText}`);
      }

      const data = await res.json();
      const content = data.choices?.[0]?.message?.content;
      if (!content) throw new Error('Empty response from OpenRouter');

      // Log usage for cost tracking
      if (data.usage) {
        const usage = data.usage;
        console.log(`[LLM] ${role} (${model}): ${usage.prompt_tokens}in/${usage.completion_tokens}out`);
      }

      return content;
    } catch (err) {
      lastError = err;
      if (attempt < 2) {
        console.log(`[LLM] Attempt ${attempt + 1} failed: ${err.message}. Retrying...`);
        await sleep(2000 * (attempt + 1));
      }
    }
  }
  throw lastError;
}

// Convenience: Chat expecting JSON response, parse it (with repair fallback)
async function chatJSON({ role, messages, maxTokens = 2000 }) {
  const content = await chat({ role, messages, json: true, maxTokens });
  try {
    const cleaned = content.replace(/^```json?\s*/i, '').replace(/\s*```$/i, '').trim();
    return JSON.parse(cleaned);
  } catch (firstErr) {
    // Repair attempt: ask the cheapest model to fix the JSON
    console.warn('[LLM] JSON parse failed, attempting repair...');
    try {
      const repaired = await chat({
        role: 'extraction', // cheapest model
        messages: [{ role: 'user', content: `Fix this broken JSON. Return ONLY valid JSON, nothing else:\n${content.slice(0, 3000)}` }],
        json: true,
        maxTokens: maxTokens
      });
      const cleanRepair = repaired.replace(/^```json?\s*/i, '').replace(/\s*```$/i, '').trim();
      return JSON.parse(cleanRepair);
    } catch {
      console.error('[LLM] JSON repair also failed:', content.slice(0, 200));
      throw new Error(`JSON parse error: ${firstErr.message}`);
    }
  }
}

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

module.exports = { chat, chatJSON };
