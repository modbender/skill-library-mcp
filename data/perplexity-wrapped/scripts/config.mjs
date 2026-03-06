#!/usr/bin/env node
/**
 * Resolves the Perplexity API key from environment.
 * Set via OpenClaw config: skills.entries.perplexity_wrapped.apiKey
 */

export const apiKey = process.env.PERPLEXITY_API_KEY || null;
