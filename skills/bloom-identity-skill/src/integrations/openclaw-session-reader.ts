/**
 * OpenClaw Session Reader
 *
 * Reads conversation history from OpenClaw session JSONL files
 * and extracts topics, interests, and preferences for personality analysis.
 *
 * Session files location: ~/.openclaw/agents/main/sessions/
 * - sessions.json: metadata about active sessions
 * - {sessionId}.jsonl: conversation history (one JSON event per line)
 */

import fs from 'fs';
import path from 'path';
import os from 'os';
import { CATEGORY_KEYWORDS } from '../types/categories';

export interface SessionMessage {
  role: 'user' | 'assistant';
  text: string;
  timestamp: number;
}

export interface ConversationAnalysis {
  topics: string[];      // Main topics discussed (e.g., "AI tools", "DeFi", "productivity")
  interests: string[];   // Expressed interests (e.g., "machine learning", "crypto trading")
  preferences: string[]; // Stated preferences (e.g., "early stage", "open source")
  history: string[];     // Raw conversation snippets for context
  messageCount: number;  // Total messages analyzed
}

/**
 * OpenClaw Session Reader
 */
export class OpenClawSessionReader {
  private sessionDir: string;

  constructor() {
    // Default OpenClaw session directory
    this.sessionDir = path.join(os.homedir(), '.openclaw/agents/main/sessions');
  }

  /**
   * Read and analyze conversation history for a user
   */
  async readSessionHistory(userId: string): Promise<ConversationAnalysis> {
    console.log(`📖 Reading OpenClaw session for user: ${userId}`);

    try {
      // Step 1: Find active session ID
      const sessionId = await this.findActiveSession(userId);
      if (!sessionId) {
        console.log('⚠️  No active session found');
        return this.emptyAnalysis();
      }

      console.log(`✅ Found session: ${sessionId}`);

      // Step 2: Read session JSONL file
      const messages = await this.readSessionMessages(sessionId);
      console.log(`📨 Read ${messages.length} messages`);

      if (messages.length === 0) {
        return this.emptyAnalysis();
      }

      // Step 3: Analyze conversation to extract insights
      const analysis = await this.analyzeConversation(messages);
      console.log(`✅ Analysis complete: ${analysis.topics.length} topics, ${analysis.interests.length} interests`);

      return analysis;
    } catch (error) {
      console.error('❌ Error reading session:', error);
      return this.emptyAnalysis();
    }
  }

  /**
   * Find the active session ID for a user
   */
  private async findActiveSession(userId: string): Promise<string | null> {
    const sessionsMetaPath = path.join(this.sessionDir, 'sessions.json');

    if (!fs.existsSync(sessionsMetaPath)) {
      return null;
    }

    const sessionsMeta = JSON.parse(fs.readFileSync(sessionsMetaPath, 'utf-8'));

    // Look for session key: agent:main:{userId}
    const sessionKey = `agent:main:${userId}`;
    let sessionId = sessionsMeta[sessionKey]?.sessionId;
    if (!sessionId) {
      // Fallback to default main session
      sessionId = sessionsMeta['agent:main:main']?.sessionId;
    }

    return sessionId || null;
  }

  /**
   * Read all messages from a session JSONL file
   */
  private async readSessionMessages(sessionId: string): Promise<SessionMessage[]> {
    const sessionFile = path.join(this.sessionDir, `${sessionId}.jsonl`);

    if (!fs.existsSync(sessionFile)) {
      return [];
    }

    const lines = fs.readFileSync(sessionFile, 'utf-8').split('\n');
    const messages: SessionMessage[] = [];

    for (const line of lines) {
      if (!line.trim()) continue;

      try {
        const event = JSON.parse(line);

        // Extract message events
        if (event.type === 'message' && event.message) {
          const text = event.message.content
            ?.filter((c: any) => c.type === 'text')
            .map((c: any) => c.text)
            .join('\n');

          if (text) {
            messages.push({
              role: event.message.role,
              text,
              timestamp: event.message.timestamp || Date.now(),
            });
          }
        }
      } catch (error) {
        // Skip malformed lines
        console.warn('⚠️  Skipping malformed line:', error);
      }
    }

    return messages;
  }

  /**
   * Analyze conversation to extract topics, interests, and preferences
   */
  private async analyzeConversation(messages: SessionMessage[]): Promise<ConversationAnalysis> {
    // Combine all user messages (their input reveals interests)
    const userMessages = messages
      .filter(m => m.role === 'user')
      .map(m => m.text);

    // Also include assistant messages for context
    const allText = messages.map(m => m.text).join('\n').toLowerCase();

    // Extract topics (common themes)
    const topics = this.extractTopics(userMessages);

    // Extract interests (things they ask about or mention positively)
    const interests = this.extractInterests(userMessages);

    // Extract preferences (how they describe what they want)
    const preferences = this.extractPreferences(userMessages);

    // Get recent conversation snippets for context
    const recentMessages = messages.slice(-10).map(m => {
      const prefix = m.role === 'user' ? 'User:' : 'Assistant:';
      return `${prefix} ${m.text.slice(0, 200)}`;
    });

    return {
      topics,
      interests,
      preferences,
      history: recentMessages,
      messageCount: messages.length,
    };
  }

  /**
   * Extract main topics from conversation
   */
  private extractTopics(userMessages: string[]): string[] {
    const allText = userMessages.join(' ').toLowerCase();
    const topics: string[] = [];

    for (const [topic, keywords] of Object.entries(CATEGORY_KEYWORDS)) {
      const matches = keywords.filter(kw => allText.includes(kw)).length;
      if (matches >= 2) {
        topics.push(topic);
      }
    }

    return topics;
  }

  /**
   * Extract specific interests from user messages
   */
  private extractInterests(userMessages: string[]): string[] {
    const interests = new Set<string>();
    const allText = userMessages.join(' ').toLowerCase();

    // Interest patterns (what they're looking for or asking about)
    const interestKeywords = [
      'ai tools', 'machine learning', 'crypto', 'defi', 'nft',
      'productivity', 'automation', 'workflow', 'task management',
      'wellness', 'health', 'fitness', 'meditation',
      'education', 'learning', 'courses', 'tutorials',
      'web3', 'blockchain', 'smart contracts', 'dao',
      'design', 'ui/ux', 'creative', 'art',
      'marketing', 'growth', 'seo', 'content',
      'development', 'coding', 'programming',
      'investing', 'trading', 'finance',
    ];

    for (const keyword of interestKeywords) {
      if (allText.includes(keyword)) {
        // Capitalize properly
        interests.add(
          keyword.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
        );
      }
    }

    // Extract phrases after "interested in", "looking for", "need", "want"
    const interestPatterns = [
      /interested in ([a-z\s]+?)(?:\.|,|\n|$)/gi,
      /looking for ([a-z\s]+?)(?:\.|,|\n|$)/gi,
      /need ([a-z\s]+?)(?:\.|,|\n|$)/gi,
      /want ([a-z\s]+?)(?:\.|,|\n|$)/gi,
      /recommend ([a-z\s]+?)(?:\.|,|\n|$)/gi,
    ];

    for (const pattern of interestPatterns) {
      const matches = allText.matchAll(pattern);
      for (const match of matches) {
        const phrase = match[1].trim();
        if (phrase.length > 3 && phrase.length < 30) {
          interests.add(
            phrase.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
          );
        }
      }
    }

    return Array.from(interests).slice(0, 15);
  }

  /**
   * Extract stated preferences from conversation
   */
  private extractPreferences(userMessages: string[]): string[] {
    const preferences: string[] = [];
    const allText = userMessages.join(' ').toLowerCase();

    // Preference indicators
    const preferencePatterns = {
      'early stage': ['early stage', 'pre-launch', 'new project', 'just started'],
      'established': ['established', 'proven', 'mature', 'reliable'],
      'open source': ['open source', 'open-source', 'oss', 'github'],
      'user-friendly': ['user-friendly', 'easy to use', 'simple', 'intuitive'],
      'technical': ['technical', 'advanced', 'complex', 'detailed'],
      'community-driven': ['community', 'collaborative', 'social'],
      'data-driven': ['data-driven', 'analytics', 'metrics', 'statistics'],
      'innovative': ['innovative', 'cutting-edge', 'novel', 'breakthrough'],
      'affordable': ['affordable', 'cheap', 'free', 'budget'],
      'premium': ['premium', 'high-quality', 'professional', 'enterprise'],
    };

    for (const [preference, keywords] of Object.entries(preferencePatterns)) {
      if (keywords.some(kw => allText.includes(kw))) {
        preferences.push(preference);
      }
    }

    return preferences;
  }

  /**
   * Return empty analysis
   */
  private emptyAnalysis(): ConversationAnalysis {
    return {
      topics: [],
      interests: [],
      preferences: [],
      history: [],
      messageCount: 0,
    };
  }
}

/**
 * Create a session reader instance
 */
export function createSessionReader(): OpenClawSessionReader {
  return new OpenClawSessionReader();
}
