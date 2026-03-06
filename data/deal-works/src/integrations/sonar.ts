/**
 * Perplexity Sonar API Integration
 *
 * Provides real-time web search and research capabilities for:
 * - Bourse: Market intelligence, competitor analysis, pricing research
 * - Cadre: Agent research, skill discovery, best practices
 *
 * Sonar API is OpenAI-compatible and stable (independent of Perplexity Computer)
 */

import { z } from "zod";

// Configuration
const SONAR_API_BASE = "https://api.perplexity.ai";

export interface SonarConfig {
  apiKey: string;
  model?: SonarModel;
  timeout?: number;
}

export type SonarModel =
  | "sonar"           // Standard search - fast, cost-effective
  | "sonar-pro"       // Advanced reasoning with search
  | "sonar-reasoning-pro"  // Complex analytical tasks
  | "sonar-deep-research"; // Comprehensive research (higher cost)

export interface SonarSearchResult {
  answer: string;
  citations: Array<{
    url: string;
    title?: string;
    snippet?: string;
  }>;
  model: string;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

export interface SonarError {
  code: string;
  message: string;
  retryable: boolean;
}

// Input validation
const SonarQuerySchema = z.object({
  query: z.string().min(1).max(2000),
  model: z.enum(["sonar", "sonar-pro", "sonar-reasoning-pro", "sonar-deep-research"]).optional(),
  systemPrompt: z.string().max(4000).optional(),
  maxTokens: z.number().min(1).max(4096).optional(),
  temperature: z.number().min(0).max(2).optional(),
  returnCitations: z.boolean().optional(),
  searchDomainFilter: z.array(z.string()).optional(),
  searchRecencyFilter: z.enum(["day", "week", "month", "year"]).optional(),
});

export type SonarQuery = z.infer<typeof SonarQuerySchema>;

/**
 * Sonar API Client
 */
export class SonarClient {
  private readonly apiKey: string;
  private readonly defaultModel: SonarModel;
  private readonly timeout: number;

  constructor(config: SonarConfig) {
    this.apiKey = config.apiKey;
    this.defaultModel = config.model ?? "sonar";
    this.timeout = config.timeout ?? 30000;
  }

  /**
   * Perform a web search with AI-powered answer synthesis
   */
  async search(query: SonarQuery): Promise<SonarSearchResult | SonarError> {
    const validated = SonarQuerySchema.parse(query);

    const messages = [
      ...(validated.systemPrompt
        ? [{ role: "system" as const, content: validated.systemPrompt }]
        : []),
      { role: "user" as const, content: validated.query },
    ];

    const body = {
      model: validated.model ?? this.defaultModel,
      messages,
      max_tokens: validated.maxTokens,
      temperature: validated.temperature ?? 0.2,
      return_citations: validated.returnCitations ?? true,
      search_domain_filter: validated.searchDomainFilter,
      search_recency_filter: validated.searchRecencyFilter,
    };

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);

      const response = await fetch(`${SONAR_API_BASE}/chat/completions`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${this.apiKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text();
        return {
          code: `HTTP_${response.status}`,
          message: errorText || response.statusText,
          retryable: response.status >= 500 || response.status === 429,
        };
      }

      const data = await response.json();

      return {
        answer: data.choices?.[0]?.message?.content ?? "",
        citations: data.citations ?? [],
        model: data.model,
        usage: data.usage,
      };
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      return {
        code: "NETWORK_ERROR",
        message,
        retryable: true,
      };
    }
  }

  /**
   * Market intelligence search for Bourse
   * Enriches marketplace listings with real-time market data
   */
  async marketIntelligence(params: {
    topic: string;
    industry?: string;
    competitors?: string[];
  }): Promise<SonarSearchResult | SonarError> {
    const systemPrompt = `You are a market research analyst. Provide concise, data-driven insights about:
- Market size and growth trends
- Key players and competitors
- Pricing benchmarks
- Recent developments and news

Focus on actionable intelligence. Cite specific sources.`;

    const query = params.competitors?.length
      ? `${params.topic} in ${params.industry ?? "technology"} industry. Compare with: ${params.competitors.join(", ")}`
      : `${params.topic} market analysis ${params.industry ?? ""}`;

    return this.search({
      query,
      model: "sonar-pro",
      systemPrompt,
      searchRecencyFilter: "month",
    });
  }

  /**
   * Agent research for Cadre
   * Discovers best practices and existing solutions for agent deployment
   */
  async agentResearch(params: {
    task: string;
    domain?: string;
    requirements?: string[];
  }): Promise<SonarSearchResult | SonarError> {
    const systemPrompt = `You are an AI agent architect. Research and recommend:
- Existing solutions and frameworks
- Best practices for the task
- Potential pitfalls and how to avoid them
- Cost and performance considerations

Be specific about implementation details.`;

    const reqString = params.requirements?.length
      ? ` Requirements: ${params.requirements.join(", ")}`
      : "";

    return this.search({
      query: `AI agent for ${params.task} ${params.domain ?? ""} automation${reqString}`,
      model: "sonar-reasoning-pro",
      systemPrompt,
    });
  }

  /**
   * Deep research for comprehensive analysis
   * Use sparingly - higher token cost
   */
  async deepResearch(params: {
    topic: string;
    context?: string;
    questions?: string[];
  }): Promise<SonarSearchResult | SonarError> {
    const questionsText = params.questions?.length
      ? `\n\nSpecific questions to address:\n${params.questions.map((q, i) => `${i + 1}. ${q}`).join("\n")}`
      : "";

    return this.search({
      query: `${params.topic}${params.context ? ` Context: ${params.context}` : ""}${questionsText}`,
      model: "sonar-deep-research",
      maxTokens: 4096,
    });
  }
}

/**
 * Create a Sonar client instance
 */
export function createSonarClient(config?: Partial<SonarConfig>): SonarClient {
  const apiKey = config?.apiKey ?? process.env.PERPLEXITY_API_KEY;

  if (!apiKey) {
    throw new Error("PERPLEXITY_API_KEY not set");
  }

  return new SonarClient({
    apiKey,
    model: config?.model,
    timeout: config?.timeout,
  });
}

/**
 * Check if result is an error
 */
export function isSonarError(result: SonarSearchResult | SonarError): result is SonarError {
  return "code" in result && "retryable" in result;
}
