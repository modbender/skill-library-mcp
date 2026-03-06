/**
 * Observer — Extract structured facts from conversations via LLM.
 * Supports OpenAI, Anthropic, Gemini. Fails gracefully.
 */

export type ObservationKind = 'world' | 'biographical' | 'opinion' | 'observation';

export interface Observation {
  kind: ObservationKind;
  timestamp: Date;
  entities: string[];
  content: string;
  source: string;
  priority: 'high' | 'medium' | 'low';
  confidence?: number;
}

export interface ObserverConfig {
  provider: 'openai' | 'anthropic' | 'gemini';
  model?: string;
  apiKey?: string;
}

export interface Message {
  role: string;
  content: string;
  timestamp?: Date;
}

const EXTRACTION_PROMPT = `Extract structured facts from this conversation.
For each fact, output one line:
KIND|PRIORITY|ENTITIES|CONTENT

KIND: W (world fact), B (biographical), O (opinion), S (observation)
PRIORITY: H (high), M (medium), L (low)
ENTITIES: comma-separated @mentions
CONTENT: the fact itself

Example:
W|H|@Alice,@Bob|Alice and Bob are siblings
O|M|@Alice|Alice prefers TypeScript over Python (confidence: 0.8)

Conversation:
`;

export class ObserverAgent {
  private config: ObserverConfig;

  constructor(config: ObserverConfig) {
    this.config = config;
  }

  /** Sanitize message content — strip control chars, Unicode tags, ZW chars, cap length.
   *  Defends against invisible prompt injection (wunderwuzzi23/embracethered). */
  private sanitize(text: string, maxLen = 8000): string {
    return text
      .replace(/[\x00-\x08\x0B\x0C\x0E-\x1F]/g, '')           // C0 control chars
      .replace(/[\u200B-\u200F\u2060-\u206F\uFEFF]/g, '')       // zero-width & format chars
      .replace(/[\u202A-\u202E]/g, '')                           // bidi embeddings/overrides (Trojan Source)
      .replace(/[\u2066-\u2069]/g, '')                           // bidi isolates
      .replace(/\u061C/g, '')                                    // Arabic Letter Mark
      .replace(/\u00AD/g, '')                                    // Soft Hyphen
      .replace(/[\uDB40][\uDC00-\uDC7F]/g, '')                  // Unicode Tags U+E0000-E007F (surrogate pairs)
      .replace(/[\uFE00-\uFE0F]/g, '')                           // Variation Selectors 1-16
      .replace(/[\uDB40][\uDD00-\uDDEF]/g, '')                  // Variation Selectors 17-256
      .slice(0, maxLen);
  }

  async extract(messages: Message[], source = 'conversation'): Promise<Observation[]> {
    const sanitized = messages.map(m => `${m.role}: ${this.sanitize(m.content)}`).join('\n');
    const prompt = EXTRACTION_PROMPT + sanitized;

    let response: string;
    try {
      response = await this.callLLM(prompt);
    } catch (err) {
      console.warn('[memory] LLM extraction failed:', (err as Error).message);
      return [];
    }

    return this.parseResponse(response, source);
  }

  private async callLLM(prompt: string): Promise<string> {
    const key = this.config.apiKey || process.env.OPENAI_API_KEY || process.env.ANTHROPIC_API_KEY || '';

    if (this.config.provider === 'openai') {
      const res = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${key}` },
        body: JSON.stringify({
          model: this.config.model || 'gpt-4o-mini',
          messages: [{ role: 'user', content: prompt }],
          max_tokens: 2000,
        }),
      });
      const data = await res.json() as any;
      return data.choices?.[0]?.message?.content || '';
    }

    if (this.config.provider === 'anthropic') {
      const res = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': key,
          'anthropic-version': '2023-06-01',
        },
        body: JSON.stringify({
          model: this.config.model || 'claude-3-5-haiku-20241022',
          max_tokens: 2000,
          messages: [{ role: 'user', content: prompt }],
        }),
      });
      const data = await res.json() as any;
      return data.content?.[0]?.text || '';
    }

    // Gemini — key in header, not URL (avoids log exposure)
    const res = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/${this.config.model || 'gemini-2.0-flash'}:generateContent`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-goog-api-key': key },
        body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }] }),
      }
    );
    const data = await res.json() as any;
    return data.candidates?.[0]?.content?.parts?.[0]?.text || '';
  }

  private parseResponse(text: string, source: string): Observation[] {
    const kindMap: Record<string, ObservationKind> = { W: 'world', B: 'biographical', O: 'opinion', S: 'observation' };
    const prioMap: Record<string, 'high' | 'medium' | 'low'> = { H: 'high', M: 'medium', L: 'low' };
    const obs: Observation[] = [];

    for (const line of text.split('\n')) {
      const parts = line.split('|').map(s => s.trim());
      if (parts.length < 4) continue;

      const kind = kindMap[parts[0]];
      const priority = prioMap[parts[1]];
      if (!kind || !priority) continue;

      const entities = parts[2].split(',').map(e => e.trim().replace(/^@/, '')).filter(Boolean);
      const content = parts.slice(3).join('|');

      const confMatch = content.match(/confidence:\s*([\d.]+)/i);

      obs.push({
        kind,
        timestamp: new Date(),
        entities,
        content: content.replace(/\(confidence:.*?\)/i, '').trim(),
        source,
        priority,
        confidence: confMatch ? parseFloat(confMatch[1]) : undefined,
      });
    }

    return obs;
  }
}
