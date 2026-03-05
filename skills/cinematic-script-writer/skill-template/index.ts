/**
 * Skill Template
 * 
 * This is the main entry point for your skill.
 * Export functions that the agent can call as tools.
 */

// Types for skill context and configuration
interface SkillContext {
  userId: string;
  sessionId: string;
  memory: MemoryStore;
  logger: Logger;
}

interface SkillConfig {
  greetingPrefix?: string;
  enableLogging?: boolean;
}

interface MemoryStore {
  get(key: string): Promise<any>;
  set(key: string, value: any): Promise<void>;
  delete(key: string): Promise<void>;
}

interface Logger {
  debug(msg: string): void;
  info(msg: string): void;
  warn(msg: string): void;
  error(msg: string): void;
}

// Skill class - main implementation
export class SkillTemplate {
  private config: SkillConfig;
  private context: SkillContext;

  constructor(config: SkillConfig, context: SkillContext) {
    this.config = config;
    this.context = context;
  }

  /**
   * Greet the user
   * This is a simple example tool
   */
  async greet(name: string): Promise<string> {
    const prefix = this.config.greetingPrefix || "Hello";
    const message = `${prefix}, ${name}! 👋`;
    
    if (this.config.enableLogging) {
      this.context.logger.debug(`Greeting user: ${name}`);
    }

    // Store greeting in memory
    await this.context.memory.set(`lastGreeting:${this.context.userId}`, {
      name,
      timestamp: new Date().toISOString()
    });

    return message;
  }

  /**
   * Perform a calculation
   * Example of a tool that does something useful
   */
  async calculate(expression: string): Promise<{ result: number; expression: string }> {
    if (this.config.enableLogging) {
      this.context.logger.debug(`Calculating: ${expression}`);
    }

    // Simple calculation - in production, use a proper math parser
    try {
      // WARNING: eval is dangerous, use a safe math parser in production
      // This is just for demonstration
      const result = Function('"use strict"; return (' + expression + ')')();
      
      return {
        result,
        expression
      };
    } catch (error) {
      throw new Error(`Invalid expression: ${expression}`);
    }
  }

  /**
   * Get last greeting from memory
   */
  async getLastGreeting(): Promise<any> {
    return await this.context.memory.get(`lastGreeting:${this.context.userId}`);
  }
}

// Factory function - the agent calls this to create your skill instance
export default function createSkill(config: SkillConfig, context: SkillContext) {
  return new SkillTemplate(config, context);
}

// Export types for TypeScript users
export type { SkillConfig, SkillContext };
