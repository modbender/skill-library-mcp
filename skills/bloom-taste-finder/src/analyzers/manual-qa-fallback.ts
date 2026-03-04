/**
 * Manual Q&A Fallback
 *
 * When user denies data access or insufficient data is available,
 * ask 3 simple questions to determine personality type
 */

import { PersonalityType } from '../types/personality';

export interface ManualAnswer {
  question: string;
  answer: string;
}

export interface ManualQAResult {
  personalityType: PersonalityType;
  tagline: string;
  description: string;
  mainCategories: string[];
  subCategories: string[];
  confidence: number;
}

/**
 * 4 gentle questions to determine personality
 */
export const MANUAL_QUESTIONS = [
  {
    id: 'focus',
    question: "What's been taking most of your attention lately?",
    options: [
      { value: 'Exploring or building new AI tools', personality: PersonalityType.THE_INNOVATOR, weight: 10 },
      { value: 'Diving into crypto / Web3 ideas', personality: PersonalityType.THE_VISIONARY, weight: 10 },
      { value: 'Streamlining workflows and execution', personality: PersonalityType.THE_OPTIMIZER, weight: 10 },
      { value: 'Learning deeply and building a knowledge base', personality: PersonalityType.THE_EXPLORER, weight: 10 },
      { value: 'Health, mindset, or life balance', personality: PersonalityType.THE_CULTIVATOR, weight: 10 },
    ],
  },
  {
    id: 'pull',
    question: 'What kind of content naturally pulls you in?',
    options: [
      { value: 'Fresh AI/tool demos', personality: PersonalityType.THE_INNOVATOR, weight: 8 },
      { value: 'Crypto/Web3 narratives and trends', personality: PersonalityType.THE_VISIONARY, weight: 8 },
      { value: 'Productivity systems and workflows', personality: PersonalityType.THE_OPTIMIZER, weight: 8 },
      { value: 'Deep dives, research, or courses', personality: PersonalityType.THE_EXPLORER, weight: 8 },
      { value: 'Mental health, wellness, or lifestyle', personality: PersonalityType.THE_CULTIVATOR, weight: 8 },
    ],
  },
  {
    id: 'support',
    question: 'When you support an early-stage project, which role feels most like you?',
    options: [
      { value: 'The first to try new tech', personality: PersonalityType.THE_INNOVATOR, weight: 7 },
      { value: 'Believing early and amplifying the story', personality: PersonalityType.THE_VISIONARY, weight: 7 },
      { value: 'Making it smoother and more efficient', personality: PersonalityType.THE_OPTIMIZER, weight: 7 },
      { value: 'Offering research, insight, or strategy', personality: PersonalityType.THE_EXPLORER, weight: 7 },
      { value: 'Caring about human impact and wellbeing', personality: PersonalityType.THE_CULTIVATOR, weight: 7 },
    ],
  },
  {
    id: 'category',
    question: 'If you had to pick one theme to go deep on first, what would it be?',
    options: [
      { value: 'AI Tools / New Tech', personality: PersonalityType.THE_INNOVATOR, weight: 9 },
      { value: 'Crypto / Web3', personality: PersonalityType.THE_VISIONARY, weight: 9 },
      { value: 'Productivity / Automation', personality: PersonalityType.THE_OPTIMIZER, weight: 9 },
      { value: 'Learning / Education', personality: PersonalityType.THE_EXPLORER, weight: 9 },
      { value: 'Wellness / Mental Health', personality: PersonalityType.THE_CULTIVATOR, weight: 9 },
    ],
  },
];

export class ManualQAFallback {
  /**
   * Analyze answers to determine personality type
   */
  async analyze(answers: ManualAnswer[]): Promise<ManualQAResult> {
    console.log('🤔 Analyzing manual Q&A responses...');

    // Score each personality type
    const scores: Record<PersonalityType, number> = {
      [PersonalityType.THE_VISIONARY]: 0,
      [PersonalityType.THE_EXPLORER]: 0,
      [PersonalityType.THE_CULTIVATOR]: 0,
      [PersonalityType.THE_OPTIMIZER]: 0,
      [PersonalityType.THE_INNOVATOR]: 0,
    };

    // Calculate scores based on answers
    for (const answer of answers) {
      const question = MANUAL_QUESTIONS.find(q => q.question === answer.question);
      if (!question) continue;

      const option = question.options.find(opt => opt.value === answer.answer);
      if (!option) continue;

      scores[option.personality] += option.weight;
    }

    // Determine dominant personality
    let maxScore = -1;
    let dominantType = PersonalityType.THE_INNOVATOR; // Default

    for (const [type, score] of Object.entries(scores)) {
      if (score > maxScore) {
        maxScore = score;
        dominantType = type as PersonalityType;
      }
    }

    // Generate result
    const result = this.generateResult(dominantType, answers);

    console.log(`✅ Determined personality: ${dominantType} (confidence: ${result.confidence}%)`);

    return result;
  }

  /**
   * Generate complete result based on personality type
   */
  private generateResult(
    personalityType: PersonalityType,
    answers: ManualAnswer[]
  ): ManualQAResult {
    const configs = {
      [PersonalityType.THE_VISIONARY]: {
        tagline: 'See beyond the hype',
        description: 'An early believer in paradigm-shifting technologies. Champions Web3 and decentralized innovation.',
        mainCategories: ['Crypto', 'DeFi', 'Web3', 'Blockchain'],
        subCategories: ['DeFi', 'DAOs', 'NFTs', 'Layer 2'],
      },
      [PersonalityType.THE_EXPLORER]: {
        tagline: 'Never stop discovering',
        description: 'A curious mind with insatiable appetite for learning. Supports projects that expand human knowledge.',
        mainCategories: ['Education', 'Learning', 'Knowledge', 'Research'],
        subCategories: ['Online Courses', 'EdTech', 'Books', 'Science'],
      },
      [PersonalityType.THE_CULTIVATOR]: {
        tagline: 'Growth starts within',
        description: 'A wellness advocate who believes in holistic growth. Champions mental, physical, and emotional health.',
        mainCategories: ['Wellness', 'Mental Health', 'Fitness', 'Mindfulness'],
        subCategories: ['Meditation', 'Yoga', 'Nutrition', 'Sleep'],
      },
      [PersonalityType.THE_OPTIMIZER]: {
        tagline: 'Always leveling up',
        description: 'An efficiency enthusiast who loves tools that maximize productivity. Always seeking to work smarter.',
        mainCategories: ['Productivity', 'Tools', 'Efficiency', 'Automation'],
        subCategories: ['Task Management', 'Note-taking', 'Workflow', 'Time Tracking'],
      },
      [PersonalityType.THE_INNOVATOR]: {
        tagline: 'First to back new tech',
        description: 'A technology pioneer who jumps on cutting-edge AI tools. Funds the next generation of breakthroughs.',
        mainCategories: ['AI Tools', 'Technology', 'Innovation', 'Machine Learning'],
        subCategories: ['AI Assistants', 'Content Creation', 'Code Tools', 'LLMs'],
      },
    };

    const config = configs[personalityType];

    return {
      personalityType,
      tagline: config.tagline,
      description: config.description,
      mainCategories: config.mainCategories,
      subCategories: config.subCategories,
      confidence: 60, // Manual Q&A has lower confidence than data analysis
    };
  }

  /**
   * Format questions for display to user
   */
  formatQuestionsForUser(): string {
    let message = '🤔 Let me ask you a few quick questions to understand your interests:\n\n';

    MANUAL_QUESTIONS.forEach((q, index) => {
      message += `**Question ${index + 1}**: ${q.question}\n`;
      q.options.forEach((opt, optIndex) => {
        message += `${optIndex + 1}. ${opt.value}\n`;
      });
      message += '\n';
    });

    return message;
  }

  /**
   * Parse user's text responses
   */
  parseTextResponses(responses: string[]): ManualAnswer[] {
    const answers: ManualAnswer[] = [];

    responses.forEach((response, index) => {
      if (index < MANUAL_QUESTIONS.length) {
        const question = MANUAL_QUESTIONS[index];

        // Try to match response to an option
        const matchedOption = question.options.find(opt =>
          response.toLowerCase().includes(opt.value.toLowerCase().slice(0, 5))
        );

        answers.push({
          question: question.question,
          answer: matchedOption?.value || response,
        });
      }
    });

    return answers;
  }
}
