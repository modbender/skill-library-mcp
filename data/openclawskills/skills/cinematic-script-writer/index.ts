/**
 * Cinematic Script Writer Skill
 * 
 * Creates professional cinematic scripts for comic videos with:
 * - Context management (characters, era, settings)
 * - Story idea generation
 * - Full script with cinematography details
 * - Image/Video generation prompts
 * - YouTube metadata generation
 */

import { v4 as uuidv4 } from 'uuid';
import { CinematographyAPI } from './cinematography-api';
import { promptBuilder, BuiltPrompts, PromptBuildOptions } from './prompt-builder';
import { 
  consistencyManager,
  CharacterReferenceSheet,
  VoiceProfile,
  EnvironmentStyleGuide,
  ValidationResult 
} from './consistency-system';

// ============================================================================
// Types & Interfaces
// ============================================================================

interface SkillConfig {
  llmProvider?: 'openai' | 'anthropic' | 'local';
  apiKey?: string;
  model?: string;
  defaultVideoDuration?: number;
  cameraStyle?: 'cinematic' | 'documentary' | 'anime' | 'comic-book' | 'minimalist';
}

interface SkillContext {
  userId: string;
  memory: MemoryStore;
  logger: Logger;
  llm?: LLMClient;
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

interface LLMClient {
  complete(prompt: string, options?: any): Promise<string>;
}

// Story Context Types
interface StoryContext {
  id: string;
  name: string;
  description: string;
  createdAt: string;
  updatedAt: string;
  characters: Character[];
  period: string;
  era: string;
  location: string;
  videoType: 'short' | 'series' | 'movie' | 'comic-strip';
  tone: 'comedy' | 'drama' | 'action' | 'horror' | 'romance' | 'mixed';
  targetAudience: string;
  visualStyle: string;
  additionalNotes?: string;
}

interface Character {
  id: string;
  name: string;
  description: string;
  personality: string;
  appearance: string;
  role: 'protagonist' | 'antagonist' | 'supporting' | 'cameo';
  backstory?: string;
  specialTraits?: string[];
}

// Story & Script Types
interface StoryIdea {
  id: string;
  title: string;
  summary: string;
  genre: string;
  estimatedDuration: number;
  keyMoments: string[];
  hook: string;
  twist?: string;
}

interface CinematicScript {
  id: string;
  contextId: string;
  storyIdeaId: string;
  title: string;
  createdAt: string;
  hook: HookScript;
  scenes: Scene[];
  bRoll: BRoll[];
  soundDesign: SoundDesign;
  productionNotes: string;
}

interface HookScript {
  text: string;
  duration: number;
  visualDescription: string;
  impact: string;
}

interface Scene {
  number: number;
  title: string;
  duration: number;
  location: string;
  timeOfDay: string;
  synopsis: string;
  shots: Shot[];
  dialogues: Dialogue[];
  transitions: string;
}

interface Shot {
  shotNumber: number;
  type: ShotType;
  cameraAngle: CameraAngle;
  cameraMovement: CameraMovement;
  duration: number;
  description: string;
  impact: string;
  imagePrompt: string;
  videoPrompt: string;
}

type ShotType = 'wide' | 'medium' | 'close-up' | 'extreme-close-up' | 'over-shoulder' | 'POV' | 'aerial' | 'establishing';
type CameraAngle = 'eye-level' | 'low-angle' | 'high-angle' | 'dutch-angle' | 'overhead' | 'bird-eye' | 'worm-eye';
type CameraMovement = 'static' | 'pan' | 'tilt' | 'dolly' | 'truck' | 'crane' | 'handheld' | 'steadicam' | 'zoom' | 'rack-focus';

interface Dialogue {
  character: string;
  text: string;
  tone: string;
  delivery: string;
  isPunchline?: boolean;
}

interface BRoll {
  timestamp: string;
  description: string;
  purpose: string;
  imagePrompt: string;
  videoPrompt: string;
}

interface SoundDesign {
  ambient: string[];
  sfx: SFX[];
  music: MusicCue[];
}

interface SFX {
  timestamp: string;
  sound: string;
  description: string;
  intensity: 'subtle' | 'moderate' | 'intense';
}

interface MusicCue {
  timestamp: string;
  type: 'intro' | 'background' | 'transition' | 'climax' | 'outro';
  genre: string;
  mood: string;
  tempo: string;
  instrumentation: string[];
}

// YouTube Metadata
interface YouTubeMetadata {
  title: string;
  description: string;
  tags: string[];
  thumbnailIdea: string;
  category: string;
}

// ============================================================================
// Camera & Cinematography Knowledge Base
// ============================================================================

const CAMERA_TECHNIQUES = {
  angles: {
    'eye-level': {
      description: 'Camera at subject eye level - neutral, natural perspective',
      emotionalImpact: 'Creates connection, equality, neutrality',
      bestFor: 'Dialogue, emotional moments, establishing character presence'
    },
    'low-angle': {
      description: 'Camera below subject looking up',
      emotionalImpact: 'Power, dominance, heroism, intimidation',
      bestFor: 'Revealing villains, heroic moments, making subject imposing'
    },
    'high-angle': {
      description: 'Camera above subject looking down',
      emotionalImpact: 'Vulnerability, weakness, inferiority, overview',
      bestFor: 'Showing subject small/helpless, establishing location'
    },
    'dutch-angle': {
      description: 'Tilted camera, horizon not level',
      emotionalImpact: 'Unease, disorientation, tension, psychological distress',
      bestFor: 'Chaos, dreams, insanity, danger moments'
    },
    'overhead': {
      description: 'Directly above subject (god view)',
      emotionalImpact: 'Omniscience, detachment, pattern recognition',
      bestFor: 'Action sequences, revealing layouts, artistic composition'
    },
    'bird-eye': {
      description: 'Extreme high angle from above',
      emotionalImpact: 'Subject is insignificant, lost, or part of larger system',
      bestFor: 'Epic scale, isolation, maze-like situations'
    },
    'worm-eye': {
      description: 'Extreme low angle from ground',
      emotionalImpact: 'Overwhelming presence, massive scale, awe',
      bestFor: 'Monuments, giants, towering structures, power'
    }
  },
  
  movements: {
    'static': 'Fixed position - stability, observation, contemplation',
    'pan': 'Horizontal rotation - revealing space, following action',
    'tilt': 'Vertical rotation - revealing height, following vertical action',
    'dolly': 'Camera on wheels forward/back - immersion, intimacy, or withdrawal',
    'truck': 'Side-to-side movement - following parallel action',
    'crane': 'Sweeping vertical arcs - epic scale, transitions, dramatic reveals',
    'handheld': 'Shaky natural movement - documentary feel, urgency, realism',
    'steadicam': 'Smooth floating movement - following through space, dreams',
    'zoom': 'Changing focal length - sudden focus, surprise, dramatic emphasis',
    'rack-focus': 'Shifting focus between planes - revealing connections, choices'
  },

  shots: {
    'establishing': 'Wide shot of location - sets scene, geography, time',
    'wide': 'Full subject + surroundings - context, environment, scale',
    'medium': 'Subject waist up - dialogue, interaction, body language',
    'close-up': 'Subject head/shoulders - emotion, reaction, intimacy',
    'extreme-close-up': 'Detail only (eyes, hands) - intense emotion, symbolism',
    'over-shoulder': 'Looking past one subject to another - conversation, perspective',
    'POV': 'Character point of view - immersion, subjectivity',
    'aerial': 'From above - scale, geography, patterns'
  }
};

// ============================================================================
// Main Skill Class
// ============================================================================

export class CinematicScriptWriter {
  private config: SkillConfig;
  private context: SkillContext;

  constructor(config: SkillConfig, context: SkillContext) {
    this.config = config;
    this.context = context;
  }

  private getStorageKey(type: string, id?: string): string {
    const base = `cinematic-writer:${this.context.userId}`;
    return id ? `${base}:${type}:${id}` : `${base}:${type}`;
  }

  // ========================================================================
  // Context Management
  // ========================================================================

  /**
   * Create a new story context
   */
  async createContext(
    name: string,
    description: string,
    characters: Omit<Character, 'id'>[],
    period: string,
    era: string,
    location: string,
    videoType: StoryContext['videoType'],
    tone: StoryContext['tone'],
    targetAudience: string,
    visualStyle: string,
    additionalNotes?: string
  ): Promise<StoryContext> {
    this.context.logger.info(`Creating context: ${name}`);

    const context: StoryContext = {
      id: uuidv4(),
      name,
      description,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      characters: characters.map(c => ({ ...c, id: uuidv4() })),
      period,
      era,
      location,
      videoType,
      tone,
      targetAudience,
      visualStyle,
      additionalNotes
    };

    // Save context
    await this.context.memory.set(
      this.getStorageKey('context', context.id),
      context
    );

    // Update context list
    const contexts = await this.listContexts();
    contexts.push({ id: context.id, name: context.name, createdAt: context.createdAt });
    await this.context.memory.set(
      this.getStorageKey('contexts-list'),
      contexts
    );

    this.context.logger.info(`Context created: ${context.id}`);
    return context;
  }

  /**
   * List all saved contexts
   */
  async listContexts(): Promise<{ id: string; name: string; createdAt: string }[]> {
    const list = await this.context.memory.get(this.getStorageKey('contexts-list'));
    return list || [];
  }

  /**
   * List contexts with full details
   */
  async listContextsDetailed(): Promise<StoryContext[]> {
    const list = await this.listContexts();
    const contexts: StoryContext[] = [];
    
    for (const item of list) {
      const context = await this.getContext(item.id);
      if (context) contexts.push(context);
    }
    
    return contexts;
  }

  /**
   * Get a specific context by ID
   */
  async getContext(contextId: string): Promise<StoryContext | null> {
    return await this.context.memory.get(this.getStorageKey('context', contextId));
  }

  /**
   * Delete a context
   */
  async deleteContext(contextId: string): Promise<boolean> {
    await this.context.memory.delete(this.getStorageKey('context', contextId));
    
    const contexts = await this.listContexts();
    const updated = contexts.filter(c => c.id !== contextId);
    await this.context.memory.set(this.getStorageKey('contexts-list'), updated);
    
    return true;
  }

  // ========================================================================
  // Story Idea Generation
  // ========================================================================

  /**
   * Generate story ideas based on a context
   */
  async generateStoryIdeas(
    contextId: string,
    count: number = 3,
    theme?: string
  ): Promise<StoryIdea[]> {
    const storyContext = await this.getContext(contextId);
    if (!storyContext) {
      throw new Error(`Context not found: ${contextId}`);
    }

    this.context.logger.info(`Generating ${count} story ideas for context: ${storyContext.name}`);

    // Build prompt for LLM
    const prompt = this.buildStoryIdeasPrompt(storyContext, count, theme);
    
    // Generate using LLM or fallback to template
    let ideas: StoryIdea[] = [];
    
    if (this.context.llm) {
      try {
        const response = await this.context.llm.complete(prompt, {
          temperature: 0.8,
          maxTokens: 2000
        });
        ideas = this.parseStoryIdeas(response);
      } catch (error) {
        this.context.logger.warn(`LLM failed, using template: ${error}`);
        ideas = this.generateTemplateStoryIdeas(storyContext, count, theme);
      }
    } else {
      ideas = this.generateTemplateStoryIdeas(storyContext, count, theme);
    }

    // Save ideas
    await this.context.memory.set(
      this.getStorageKey('ideas', contextId),
      ideas
    );

    return ideas;
  }

  private buildStoryIdeasPrompt(context: StoryContext, count: number, theme?: string): string {
    const characters = context.characters.map(c => 
      `- ${c.name}: ${c.description}. Personality: ${c.personality}. Role: ${c.role}. ${c.backstory ? `Backstory: ${c.backstory}` : ''}`
    ).join('\n');

    return `Generate ${count} story ideas for a ${context.videoType} video with the following context:

CONTEXT:
- Name: ${context.name}
- Description: ${context.description}
- Period: ${context.period}
- Era: ${context.era}
- Location: ${context.location}
- Tone: ${context.tone}
- Target Audience: ${context.targetAudience}
- Visual Style: ${context.visualStyle}
${theme ? `- Theme: ${theme}` : ''}
${context.additionalNotes ? `- Additional Notes: ${context.additionalNotes}` : ''}

CHARACTERS:
${characters}

For each story idea, provide:
1. Title (catchy, memorable)
2. Summary (2-3 sentences)
3. Genre
4. Estimated duration (in seconds)
5. Key moments (3-5 bullet points)
6. Hook (what grabs attention in first 3 seconds)
7. Twist/climax (optional)

Make ideas engaging, original, and suitable for the ${context.tone} tone. Consider the curse/blessing dynamic if present in characters.

Format as JSON array:
[
  {
    "title": "...",
    "summary": "...",
    "genre": "...",
    "estimatedDuration": 60,
    "keyMoments": ["...", "..."],
    "hook": "...",
    "twist": "..."
  }
]`;
  }

  private parseStoryIdeas(response: string): StoryIdea[] {
    try {
      // Extract JSON from response
      const jsonMatch = response.match(/\[[\s\S]*\]/);
      if (jsonMatch) {
        const parsed = JSON.parse(jsonMatch[0]);
        return parsed.map((idea: any, index: number) => ({
          id: uuidv4(),
          ...idea
        }));
      }
    } catch (error) {
      this.context.logger.error(`Failed to parse story ideas: ${error}`);
    }
    return [];
  }

  private generateTemplateStoryIdeas(context: StoryContext, count: number, theme?: string): StoryIdea[] {
    // Template-based generation when LLM unavailable
    const ideas: StoryIdea[] = [];
    const protagonist = context.characters.find(c => c.role === 'protagonist') || context.characters[0];
    
    const templates = [
      {
        title: `${protagonist?.name}'s Unexpected Blessing`,
        genre: 'Comedy-Drama',
        summary: `When ${protagonist?.name} tries to cause trouble, the curse transforms every misdeed into an act of kindness, leading to hilarious consequences.`,
        keyMoments: ['Attempted mischief backfires', 'Villains confused by kindness', 'Unexpected hero moment', 'Learning to embrace the curse']
      },
      {
        title: 'The Cursed Hero',
        genre: 'Action-Comedy',
        summary: `${protagonist?.name} must save the day, but every villainous move he plans turns heroic. Can he defeat the enemy while being good?`,
        keyMoments: ['Villain threatens village', 'Plans go wrong but right', 'Epic battle of confusion', 'Victory through accidental heroism']
      },
      {
        title: 'A Day in the Life',
        genre: 'Slice of Life Comedy',
        summary: `Follow ${protagonist?.name} through a normal day where simple tasks become adventures thanks to the unpredictable curse.`,
        keyMoments: ['Morning routine chaos', 'Helping strangers accidentally', 'Dinner disaster turns feast', 'Finding joy in the curse']
      }
    ];

    for (let i = 0; i < Math.min(count, templates.length); i++) {
      ideas.push({
        id: uuidv4(),
        ...templates[i],
        estimatedDuration: this.config.defaultVideoDuration || 60,
        hook: `What happens when a ${protagonist?.name} tries to be bad but can only do good?`,
        twist: `The curse was actually a blessing in disguise all along`
      });
    }

    return ideas;
  }

  // ========================================================================
  // Cinematic Script Generation
  // ========================================================================

  /**
   * Create full cinematic script from story idea
   */
  async createCinematicScript(
    contextId: string,
    storyIdeaId: string,
    storyIdea: StoryIdea
  ): Promise<CinematicScript> {
    const storyContext = await this.getContext(contextId);
    if (!storyContext) {
      throw new Error(`Context not found: ${contextId}`);
    }

    this.context.logger.info(`Creating cinematic script: ${storyIdea.title}`);

    // Generate script components
    const hook = await this.generateHook(storyContext, storyIdea);
    const scenes = await this.generateScenes(storyContext, storyIdea);
    const bRoll = await this.generateBRoll(storyContext, storyIdea, scenes);
    const soundDesign = await this.generateSoundDesign(storyContext, storyIdea, scenes);

    const script: CinematicScript = {
      id: uuidv4(),
      contextId,
      storyIdeaId,
      title: storyIdea.title,
      createdAt: new Date().toISOString(),
      hook,
      scenes,
      bRoll,
      soundDesign,
      productionNotes: this.generateProductionNotes(storyContext, storyIdea)
    };

    // Save script
    await this.context.memory.set(
      this.getStorageKey('script', script.id),
      script
    );

    return script;
  }

  private async generateHook(
    context: StoryContext,
    idea: StoryIdea
  ): Promise<HookScript> {
    const protagonist = context.characters.find(c => c.role === 'protagonist');
    
    return {
      text: idea.hook,
      duration: 3,
      visualDescription: `Quick cut sequence: ${protagonist?.name} attempting something mischievous, but it transforms into something good. Confused expression. Fast-paced, high energy.`,
      impact: 'Creates immediate curiosity and sets up the comedic premise'
    };
  }

  private async generateScenes(
    context: StoryContext,
    idea: StoryIdea
  ): Promise<Scene[]> {
    const scenes: Scene[] = [];
    const sceneCount = 3; // Standard short video structure
    
    // Scene 1: Setup
    scenes.push({
      number: 1,
      title: 'The Setup',
      duration: 15,
      location: context.location,
      timeOfDay: 'Day',
      synopsis: 'Introduce protagonist and the curse dynamics',
      shots: [
        {
          shotNumber: 1,
          type: 'establishing',
          cameraAngle: 'high-angle',
          cameraMovement: 'static',
          duration: 3,
          description: `Wide shot of ${context.location}, establishing the setting`,
          impact: 'Sets the scene and era',
          imagePrompt: `Epic wide establishing shot of ancient ${context.location}, ${context.visualStyle} style, ${context.era} architecture, golden hour lighting, cinematic composition, highly detailed, 8k`,
          videoPrompt: `Wide establishing shot of ancient ${context.location}, gentle camera drift, golden hour lighting, atmospheric dust particles, cinematic, 4k quality`
        },
        {
          shotNumber: 2,
          type: 'medium',
          cameraAngle: 'eye-level',
          cameraMovement: 'dolly',
          duration: 4,
          description: 'Protagonist enters, showing personality through walk and expression',
          impact: 'Character introduction',
          imagePrompt: `Medium shot of ${context.characters[0]?.name}, ${context.characters[0]?.appearance}, walking confidently, ${context.visualStyle} art style, expressive character design, ${context.period} clothing, dynamic lighting`,
          videoPrompt: `Smooth dolly shot following ${context.characters[0]?.name} walking, slight handheld feel, natural movement, cinematic depth of field`
        },
        {
          shotNumber: 3,
          type: 'close-up',
          cameraAngle: 'low-angle',
          cameraMovement: 'static',
          duration: 3,
          description: 'Protagonist plans something mischievous, evil grin',
          impact: 'Sets up conflict/humor',
          imagePrompt: `Close-up low-angle shot of ${context.characters[0]?.name} with mischievous expression, dramatic underlighting, ${context.visualStyle}, expressive face, cinematic shadows`,
          videoPrompt: `Static close-up, subtle expression change from evil grin to confusion, rack focus to background where something good happens instead`
        },
        {
          shotNumber: 4,
          type: 'wide',
          cameraAngle: 'eye-level',
          cameraMovement: 'zoom',
          duration: 5,
          description: 'The curse activates - intended mischief transforms into something good',
          impact: 'Main comedic moment, establishes premise',
          imagePrompt: `Wide shot showing ${context.characters[0]?.name} accidental good deed, surprised reactions from bystanders, ${context.visualStyle}, dynamic composition, ${context.period} setting`,
          videoPrompt: `Slow zoom out revealing the transformed situation, comedic timing, reactions from crowd, bright optimistic lighting`
        }
      ],
      dialogues: [
        {
          character: context.characters[0]?.name || 'Protagonist',
          text: "Today, I shall create chaos!",
          tone: 'determined',
          delivery: 'confident, evil laugh',
          isPunchline: false
        },
        {
          character: context.characters[0]?.name || 'Protagonist',
          text: "Wait... why is everyone smiling?",
          tone: 'confused',
          delivery: 'bewildered, high pitch',
          isPunchline: true
        }
      ],
      transitions: 'Fade to Scene 2 with sound effect of magical sparkles'
    });

    // Scene 2: Rising Action
    scenes.push({
      number: 2,
      title: 'The Conflict',
      duration: 25,
      location: `${context.location} - Marketplace`,
      timeOfDay: 'Day',
      synopsis: 'Protagonist tries again, things get more complicated',
      shots: [
        {
          shotNumber: 1,
          type: 'medium',
          cameraAngle: 'dutch-angle',
          cameraMovement: 'handheld',
          duration: 5,
          description: 'Protagonist sneaking, exaggerated stealth moves',
          impact: 'Comedic tension',
          imagePrompt: `Dutch angle medium shot, ${context.characters[0]?.name} sneaking comically, ${context.visualStyle}, dynamic pose, ${context.period} marketplace background, dramatic tilted composition`,
          videoPrompt: `Handheld camera following sneaking character, slight wobble for comedy, quick pans to show environment`
        },
        {
          shotNumber: 2,
          type: 'over-shoulder',
          cameraAngle: 'eye-level',
          cameraMovement: 'rack-focus',
          duration: 4,
          description: 'POV of target, then rack focus to show transformation happening',
          impact: 'Shows cause and effect',
          imagePrompt: `Over-shoulder shot, shallow depth of field, ${context.visualStyle}, one character in foreground blurred, magical transformation in background, ${context.period} aesthetic`,
          videoPrompt: `Rack focus from foreground to background, smooth focus pull, magical particle effects, dramatic lighting change`
        },
        {
          shotNumber: 3,
          type: 'extreme-close-up',
          cameraAngle: 'eye-level',
          cameraMovement: 'static',
          duration: 2,
          description: 'Eyes widening in disbelief',
          impact: 'Emotional beat',
          imagePrompt: `Extreme close-up of eyes, wide with disbelief, ${context.visualStyle}, detailed iris, dramatic lighting, expressive`,
          videoPrompt: `Static extreme close-up, eyes widen slowly, reflection of the chaos/goodness in pupils, subtle zoom in`
        },
        {
          shotNumber: 4,
          type: 'wide',
          cameraAngle: 'high-angle',
          cameraMovement: 'crane',
          duration: 6,
          description: 'Epic reveal of the transformed situation from above',
          impact: 'Scale and irony',
          imagePrompt: `High-angle crane shot, ${context.visualStyle}, ${context.period} marketplace scene, beautiful composition, vibrant colors, character tiny in frame, ${context.era} architecture`,
          videoPrompt: `Sweeping crane shot from high angle, smooth arc motion, revealing the full scene, majestic music moment`
        },
        {
          shotNumber: 5,
          type: 'medium',
          cameraAngle: 'low-angle',
          cameraMovement: 'dolly',
          duration: 4,
          description: 'People celebrating, treating protagonist as hero',
          impact: 'Comedic irony',
          imagePrompt: `Low-angle shot of crowd celebrating ${context.characters[0]?.name}, ${context.visualStyle}, joyful expressions, ${context.period} clothing, dynamic upward perspective`,
          videoPrompt: `Slow dolly forward through celebrating crowd, confetti or petals falling, sun flare, triumphant feel`
        },
        {
          shotNumber: 6,
          type: 'close-up',
          cameraAngle: 'eye-level',
          cameraMovement: 'static',
          duration: 4,
          description: 'Protagonist face palm, exasperated but secretly pleased',
          impact: 'Character moment',
          imagePrompt: `Close-up of ${context.characters[0]?.name} facepalming, exasperated expression, ${context.visualStyle}, soft lighting, relatable emotion`,
          videoPrompt: `Static close-up, hold on facepalm, then slowly reveal small smile peeking through fingers`
        }
      ],
      dialogues: [
        {
          character: 'Villager',
          text: "Our hero! You saved the market!",
          tone: 'grateful',
          delivery: 'cheering, enthusiastic'
        },
        {
          character: context.characters[0]?.name || 'Protagonist',
          text: "I was trying to steal the apples!",
          tone: 'frustrated',
          delivery: 'muttering under breath'
        },
        {
          character: context.characters[0]?.name || 'Protagonist',
          text: "...But yes, you're welcome.",
          tone: 'resigned',
          delivery: 'small smile',
          isPunchline: true
        }
      ],
      transitions: 'Dissolve with magical sound to Scene 3'
    });

    // Scene 3: Climax and Resolution
    scenes.push({
      number: 3,
      title: 'The Resolution',
      duration: 20,
      location: `${context.location} - Sunset Viewpoint`,
      timeOfDay: 'Sunset',
      synopsis: 'Protagonist accepts their fate, finds happiness in being good',
      shots: [
        {
          shotNumber: 1,
          type: 'wide',
          cameraAngle: 'eye-level',
          cameraMovement: 'static',
          duration: 4,
          description: 'Beautiful sunset establishing shot',
          impact: 'Mood transition',
          imagePrompt: `Wide shot of ${context.location} at sunset, orange and purple sky, ${context.visualStyle}, silhouette of landscape, peaceful atmosphere, ${context.era} architecture, cinematic composition`,
          videoPrompt: `Static wide shot, time-lapse clouds, sun setting slowly, birds flying, peaceful ambient movement`
        },
        {
          shotNumber: 2,
          type: 'medium',
          cameraAngle: 'eye-level',
          cameraMovement: 'pan',
          duration: 5,
          description: 'Protagonist sitting, then stands up with new determination',
          impact: 'Character growth',
          imagePrompt: `Medium shot ${context.characters[0]?.name} silhouette against sunset, ${context.visualStyle}, contemplative pose, warm lighting, ${context.period} clothing silhouette`,
          videoPrompt: `Slow pan right to left, character rises from sitting to standing, golden hour backlight, lens flare`
        },
        {
          shotNumber: 3,
          type: 'close-up',
          cameraAngle: 'eye-level',
          cameraMovement: 'dolly',
          duration: 4,
          description: 'Determined smile, acceptance of the curse',
          impact: 'Emotional resolution',
          imagePrompt: `Close-up of ${context.characters[0]?.name} genuine smile, warm sunset lighting, ${context.visualStyle}, hopeful expression, soft focus background`,
          videoPrompt: `Slow dolly in on smile, golden hour lighting, eyes sparkle with acceptance, rack focus to sunset behind`
        },
        {
          shotNumber: 4,
          type: 'aerial',
          cameraAngle: 'bird-eye',
          cameraMovement: 'crane',
          duration: 4,
          description: 'Epic final shot, protagonist walking into the sunset, ready for next adventure',
          impact: 'Epic ending, sequel setup',
          imagePrompt: `Bird eye aerial shot, ${context.characters[0]?.name} walking path, sunset colors, ${context.visualStyle}, long shadow, ${context.location} vista, cinematic wide angle`,
          videoPrompt: `Slow crane up and rotate, character becomes small in epic landscape, sun setting, triumphant music swell, fade to black`
        }
      ],
      dialogues: [
        {
          character: context.characters[0]?.name || 'Protagonist',
          text: "Maybe... being good isn't so bad.",
          tone: 'reflective',
          delivery: 'warm, genuine'
        },
        {
          character: context.characters[0]?.name || 'Protagonist',
          text: "But tomorrow, I'm definitely going to try being evil again!",
          tone: 'playful',
          delivery: 'wink to camera',
          isPunchline: true
        }
      ],
      transitions: 'Fade to black with upbeat music'
    });

    return scenes;
  }

  private async generateBRoll(
    context: StoryContext,
    idea: StoryIdea,
    scenes: Scene[]
  ): Promise<BRoll[]> {
    return [
      {
        timestamp: '0:05',
        description: 'Butterflies fluttering from flowers',
        purpose: 'Transition shot, magical moment',
        imagePrompt: `Close-up of colorful butterflies on flowers, macro photography style, ${context.visualStyle}, shallow depth of field, magical lighting, ${context.period} aesthetic`,
        videoPrompt: `Macro shot, butterflies taking flight in slow motion, gentle breeze moving flowers, magical particle effects, 60fps`
      },
      {
        timestamp: '0:25',
        description: 'Ancient temple bells ringing',
        purpose: 'Cultural atmosphere',
        imagePrompt: `Ancient temple bells, ${context.era} architecture, ${context.visualStyle}, golden lighting, intricate details, peaceful atmosphere`,
        videoPrompt: `Slow motion bells swaying, gentle ringing, sun flares, atmospheric dust motes, meditative pace`
      },
      {
        timestamp: '0:45',
        description: 'Children playing in background',
        purpose: 'Life goes on, community',
        imagePrompt: `Children playing in ${context.period} setting, ${context.visualStyle}, joyful expressions, warm colors, ${context.location} background`,
        videoPrompt: `Background plate of children playing, soft focus, laughter sounds, sunlight filtering through, 30fps natural motion`
      }
    ];
  }

  private async generateSoundDesign(
    context: StoryContext,
    idea: StoryIdea,
    scenes: Scene[]
  ): Promise<SoundDesign> {
    return {
      ambient: [
        `${context.location} marketplace ambience`,
        'Birds chirping, distant temple bells',
        'Wind through trees, sunset crickets'
      ],
      sfx: [
        { timestamp: '0:03', sound: 'Magical sparkle', description: 'Curse activating', intensity: 'moderate' },
        { timestamp: '0:18', sound: 'Crowd gasp then cheer', description: 'Public reaction', intensity: 'intense' },
        { timestamp: '0:35', sound: 'Comedic slide whistle', description: 'Punchline emphasis', intensity: 'subtle' },
        { timestamp: '0:55', sound: 'Triumphant horn', description: 'Resolution moment', intensity: 'moderate' }
      ],
      music: [
        {
          timestamp: '0:00',
          type: 'intro',
          genre: 'orchestral-fusion',
          mood: 'playful-mysterious',
          tempo: 'medium',
          instrumentation: ['sitar', 'tabla', 'strings', 'light percussion']
        },
        {
          timestamp: '0:15',
          type: 'background',
          genre: 'comedy',
          mood: 'light-fun',
          tempo: 'upbeat',
          instrumentation: ['bansuri', 'rhythm section', 'whimsical strings']
        },
        {
          timestamp: '0:40',
          type: 'transition',
          genre: 'emotional',
          mood: 'warm-reflective',
          tempo: 'slow',
          instrumentation: ['santoor', 'soft strings', 'ambient pads']
        },
        {
          timestamp: '0:58',
          type: 'outro',
          genre: 'triumphant',
          mood: 'hopeful-energetic',
          tempo: 'medium-fast',
          instrumentation: ['full orchestra', 'traditional drums', 'victory brass']
        }
      ]
    };
  }

  private generateProductionNotes(context: StoryContext, idea: StoryIdea): string {
    return `
PRODUCTION NOTES:
================

1. COLOR GRADING:
   - Scene 1: Warm golden tones, slightly saturated
   - Scene 2: Vibrant marketplace colors
   - Scene 3: Orange/purple sunset palette

2. EDITING STYLE:
   - Quick cuts for comedy timing
   - Hold on reaction shots for 2+ seconds
   - Smooth transitions for emotional beats

3. VFX REQUIREMENTS:
   - Magical sparkles when curse activates
   - Subtle glow on transformed objects
   - Particle effects for epic moments

4. CHARACTER ANIMATION:
   - Exaggerated expressions for comedy
   - Subtle squash and stretch
   - Strong silhouettes in action poses

5. REFERENCE FILMS:
   - Kung Fu Panda (color palette)
   - Spider-Verse (visual style)
   - Ramayana: The Legend of Prince Rama (cultural aesthetic)

Total Estimated Duration: ${idea.estimatedDuration} seconds
Target Resolution: 1080p (4K preferred for cropping)
Frame Rate: 24fps (cinematic) or 30fps (standard)
    `.trim();
  }

  // ========================================================================
  // YouTube Metadata Generation
  // ========================================================================

  /**
   * Generate YouTube title, description, and tags
   */
  async generateYouTubeMetadata(scriptId: string): Promise<YouTubeMetadata> {
    const script = await this.context.memory.get(this.getStorageKey('script', scriptId));
    if (!script) {
      throw new Error(`Script not found: ${scriptId}`);
    }

    const storyContext = await this.getContext(script.contextId);
    
    this.context.logger.info(`Generating YouTube metadata for: ${script.title}`);

    // Generate using LLM or templates
    let metadata: YouTubeMetadata;

    if (this.context.llm) {
      try {
        metadata = await this.generateMetadataWithLLM(script, storyContext);
      } catch (error) {
        metadata = this.generateMetadataTemplate(script, storyContext);
      }
    } else {
      metadata = this.generateMetadataTemplate(script, storyContext);
    }

    // Save metadata
    await this.context.memory.set(
      this.getStorageKey('metadata', scriptId),
      metadata
    );

    return metadata;
  }

  private async generateMetadataWithLLM(
    script: CinematicScript,
    context: StoryContext | null
  ): Promise<YouTubeMetadata> {
    const prompt = `Generate YouTube metadata for this video:

Title: ${script.title}
Genre: ${context?.tone || 'Comedy'}
Target: ${context?.targetAudience || 'General'}
Period: ${context?.era || 'Ancient'} ${context?.period || 'Mythological'}

Create:
1. Catchy YouTube title (under 60 characters, include hook words)
2. Engaging description (200-300 words, include timestamps, credits, links)
3. 15-20 SEO tags (comma-separated, mix of broad and specific)

Format as JSON:
{
  "title": "...",
  "description": "...",
  "tags": ["..."],
  "thumbnailIdea": "...",
  "category": "..."
}`;

    const response = await this.context.llm!.complete(prompt, {
      temperature: 0.7,
      maxTokens: 1500
    });

    const jsonMatch = response.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      const parsed = JSON.parse(jsonMatch[0]);
      return {
        ...parsed,
        tags: Array.isArray(parsed.tags) ? parsed.tags : parsed.tags.split(',').map((t: string) => t.trim())
      };
    }

    throw new Error('Failed to parse LLM response');
  }

  private generateMetadataTemplate(
    script: CinematicScript,
    context: StoryContext | null
  ): YouTubeMetadata {
    const protagonist = context?.characters.find(c => c.role === 'protagonist')?.name || 'The Hero';
    
    return {
      title: `${protagonist}'s Cursed Adventure 😂 | Epic Comedy Short`,
      description: `🎬 Welcome to an epic tale of ${protagonist}, a lovable character from ${context?.era || 'ancient'} ${context?.location || 'lands'}!

When a mischievous curse turns every bad deed into accidental good, chaos and comedy ensue! Watch as ${protagonist} discovers that being a hero might not be so bad after all.

🎨 Created with love using AI-powered storytelling
📍 Setting: ${context?.location || 'Mystical Realm'}
⏱️ Duration: ~1 minute

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎭 CHARACTERS:
${context?.characters.map(c => `• ${c.name} - ${c.role}`).join('\n') || '• Our Hero - Protagonist'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎵 MUSIC & SFX:
Traditional ${context?.era || 'Ancient'} instrumentation meets modern cinematic scoring

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 FOLLOW FOR MORE:
New animated shorts every week!

#${context?.era?.replace(/\s+/g, '') || 'Ancient'} #Animation #Comedy #ShortFilm`,
      tags: [
        'animated short',
        'comedy animation',
        `${context?.era?.toLowerCase() || 'ancient'} animation`,
        'ai animation',
        'funny videos',
        'short film',
        'cinematic',
        context?.tone || 'comedy',
        'storytelling',
        'character animation',
        `${context?.location?.toLowerCase() || 'fantasy'}`,
        'indie animation',
        'viral video',
        'entertainment',
        'web series',
        'cartoon',
        'mythology',
        'ramayana',
        protagonist.toLowerCase().replace(/\s+/g, ''),
        'curse comedy',
        'wholesome',
        'feel good'
      ],
      thumbnailIdea: `Epic thumbnail: ${protagonist} in ${context?.visualStyle || 'dynamic'} pose, surprised/confused expression, magical sparkles, ${context?.era || 'ancient'} background, bold text "CURSED TO BE GOOD!", high contrast colors, expressive face, clickbait style but artistic`,
      category: 'Film & Animation'
    };
  }

  // ========================================================================
  // Utility Methods
  // ========================================================================

  /**
   * Get camera technique info
   */
  getCameraTechnique(type: 'angle' | 'movement' | 'shot', name: string): any {
    const techniques = CAMERA_TECHNIQUES;
    
    switch (type) {
      case 'angle':
        return techniques.angles[name as keyof typeof techniques.angles];
      case 'movement':
        return techniques.movements[name as keyof typeof techniques.movements];
      case 'shot':
        return techniques.shots[name as keyof typeof techniques.shots];
      default:
        return null;
    }
  }

  /**
   * Export script as formatted text
   */
  async exportScript(scriptId: string, format: 'json' | 'text' | 'markdown'): Promise<string> {
    const script = await this.context.memory.get(this.getStorageKey('script', scriptId));
    if (!script) throw new Error('Script not found');

    switch (format) {
      case 'json':
        return JSON.stringify(script, null, 2);
      case 'text':
        return this.formatScriptAsText(script);
      case 'markdown':
        return this.formatScriptAsMarkdown(script);
      default:
        throw new Error(`Unknown format: ${format}`);
    }
  }

  private formatScriptAsText(script: CinematicScript): string {
    // Simple text formatting
    return `CINEMATIC SCRIPT: ${script.title}\n\n${JSON.stringify(script, null, 2)}`;
  }

  private formatScriptAsMarkdown(script: CinematicScript): string {
    // Markdown formatting
    return `# ${script.title}\n\n## Hook\n${script.hook.text}\n\n## Scenes\n${script.scenes.map(s => `\n### Scene ${s.number}: ${s.title}\n${s.synopsis}\n`).join('')}`;
  }
}

// Factory function
export default function createSkill(config: SkillConfig, context: SkillContext) {
  return new CinematicScriptWriter(config, context);
}

// Export types
export type {
  StoryContext,
  Character,
  StoryIdea,
  CinematicScript,
  Scene,
  Shot,
  YouTubeMetadata,
  SkillConfig,
  SkillContext
};


// =======================================================================
// APPENDED: Expanded Cinematography Methods
// These methods extend CinematicScriptWriter class functionality
// =======================================================================

declare module './index' {
  interface CinematicScriptWriter {
    // Camera Methods
    getAllCameraAngles(): any;
    getCameraAngle(angleName: string): any;
    getAnglesByEmotion(emotion: string): any;
    getAllCameraMovements(): any;
    getCameraMovement(movementName: string): any;
    getAllShotTypes(): any;
    getShotType(shotName: string): any;
    getRecommendedCameraSetup(sceneType: string, mood: string, skillLevel?: 'beginner' | 'intermediate' | 'advanced'): any;
    suggestCameraTechnique(purpose: 'intimacy' | 'power' | 'chaos' | 'reveal' | 'action' | 'emotion' | 'comedy', difficulty?: 'beginner' | 'intermediate' | 'advanced'): any;
    
    // Lighting Methods
    getAllLightingTechniques(): any;
    getLightingTechnique(techniqueName: string): any;
    suggestLighting(sceneType: string, mood: string): string[];
    getAllCompositionRules(): any;
    getCompositionRule(ruleName: string): any;
    getAllColorGradingStyles(): any;
    getColorGradingStyle(styleName: string): any;
    suggestColorGrading(genre: string): string[];
    
    // Visual Styles Methods
    getAllVisualAesthetics(): any;
    getVisualAesthetic(aestheticName: string): any;
    getAestheticsByType(type: 'animation' | 'live-action' | 'artistic' | 'genre'): any;
    getAllGenreCinematography(): any;
    getGenreCinematography(genre: string): any;
    getIndianCinematography(style?: string): any;
    suggestVisualStyle(contentType: string, targetAudience: string, tone: string): any;
    
    // Complete Package Methods
    getSceneCinematographyPackage(genre: string, mood: string, sceneType: string, skillLevel?: 'beginner' | 'intermediate' | 'advanced'): any;
    generateCinematicPrompt(subject: string, angle: string, shot: string, lighting: string, style: string): string;
    searchCinematography(query: string): any;
  }
}

// Extend the class with new methods
CinematicScriptWriter.prototype.getAllCameraAngles = function() {
  return CinematographyAPI.camera.getAllAngles();
};

CinematicScriptWriter.prototype.getCameraAngle = function(angleName: string) {
  return CinematographyAPI.camera.getAngle(angleName);
};

CinematicScriptWriter.prototype.getAnglesByEmotion = function(emotion: string) {
  return CinematographyAPI.camera.getAnglesByEmotion(emotion);
};

CinematicScriptWriter.prototype.getAllCameraMovements = function() {
  return CinematographyAPI.camera.getAllMovements();
};

CinematicScriptWriter.prototype.getCameraMovement = function(movementName: string) {
  return CinematographyAPI.camera.getMovement(movementName);
};

CinematicScriptWriter.prototype.getAllShotTypes = function() {
  return CinematographyAPI.camera.getAllShots();
};

CinematicScriptWriter.prototype.getShotType = function(shotName: string) {
  return CinematographyAPI.camera.getShot(shotName);
};

CinematicScriptWriter.prototype.getRecommendedCameraSetup = function(
  sceneType: string,
  mood: string,
  skillLevel: 'beginner' | 'intermediate' | 'advanced' = 'intermediate'
) {
  return CinematographyAPI.camera.getRecommendedSetup(sceneType, mood, skillLevel);
};

CinematicScriptWriter.prototype.suggestCameraTechnique = function(
  purpose: 'intimacy' | 'power' | 'chaos' | 'reveal' | 'action' | 'emotion' | 'comedy',
  difficulty?: 'beginner' | 'intermediate' | 'advanced'
) {
  return CinematographyAPI.camera.suggestTechnique(purpose, difficulty);
};

CinematicScriptWriter.prototype.getAllLightingTechniques = function() {
  return CinematographyAPI.lighting.getAllTechniques();
};

CinematicScriptWriter.prototype.getLightingTechnique = function(techniqueName: string) {
  return CinematographyAPI.lighting.getTechnique(techniqueName);
};

CinematicScriptWriter.prototype.suggestLighting = function(sceneType: string, mood: string) {
  return CinematographyAPI.lighting.suggestLighting(sceneType, mood);
};

CinematicScriptWriter.prototype.getAllCompositionRules = function() {
  return CinematographyAPI.lighting.getAllCompositionRules();
};

CinematicScriptWriter.prototype.getCompositionRule = function(ruleName: string) {
  return CinematographyAPI.lighting.getCompositionRule(ruleName);
};

CinematicScriptWriter.prototype.getAllColorGradingStyles = function() {
  return CinematographyAPI.lighting.getAllColorGradingStyles();
};

CinematicScriptWriter.prototype.getColorGradingStyle = function(styleName: string) {
  return CinematographyAPI.lighting.getColorGradingStyle(styleName);
};

CinematicScriptWriter.prototype.suggestColorGrading = function(genre: string) {
  return CinematographyAPI.lighting.suggestColorGrading(genre);
};

CinematicScriptWriter.prototype.getAllVisualAesthetics = function() {
  return CinematographyAPI.visual.getAllAesthetics();
};

CinematicScriptWriter.prototype.getVisualAesthetic = function(aestheticName: string) {
  return CinematographyAPI.visual.getAesthetic(aestheticName);
};

CinematicScriptWriter.prototype.getAestheticsByType = function(type: 'animation' | 'live-action' | 'artistic' | 'genre') {
  return CinematographyAPI.visual.getAestheticsByType(type);
};

CinematicScriptWriter.prototype.getAllGenreCinematography = function() {
  return CinematographyAPI.visual.getAllGenreCinematography();
};

CinematicScriptWriter.prototype.getGenreCinematography = function(genre: string) {
  return CinematographyAPI.visual.getGenreCinematography(genre);
};

CinematicScriptWriter.prototype.getIndianCinematography = function(style?: string) {
  return CinematographyAPI.visual.getIndianCinematography(style);
};

CinematicScriptWriter.prototype.suggestVisualStyle = function(
  contentType: string,
  targetAudience: string,
  tone: string
) {
  return CinematographyAPI.visual.suggestVisualStyle(contentType, targetAudience, tone);
};

CinematicScriptWriter.prototype.getSceneCinematographyPackage = function(
  genre: string,
  mood: string,
  sceneType: string,
  skillLevel: 'beginner' | 'intermediate' | 'advanced' = 'intermediate'
) {
  return CinematographyAPI.guide.getScenePackage(genre, mood, sceneType, skillLevel);
};

CinematicScriptWriter.prototype.generateCinematicPrompt = function(
  subject: string,
  angle: string,
  shot: string,
  lighting: string,
  style: string
) {
  return CinematographyAPI.guide.generateImagePrompt(subject, angle, shot, lighting, style);
};

CinematicScriptWriter.prototype.searchCinematography = function(query: string) {
  return CinematographyAPI.guide.search(query);
};


// =======================================================================
// CONSISTENCY SYSTEM METHODS
// These methods ensure character, voice, and environment consistency
// =======================================================================

declare module './index' {
  interface CinematicScriptWriter {
    // Character Consistency
    createCharacterReference(
      characterId: string,
      characterName: string,
      visualDescription: string,
      era: string,
      style: string
    ): CharacterReferenceSheet;
    
    getCharacterReference(characterId: string): CharacterReferenceSheet | undefined;
    
    updateCharacterReference(
      characterId: string,
      updates: Partial<CharacterReferenceSheet>
    ): CharacterReferenceSheet | undefined;
    
    generateCharacterConsistencyPrompt(
      characterId: string,
      situation?: string
    ): string;
    
    // Voice Consistency
    createVoiceProfile(
      characterId: string,
      characterName: string,
      personality: string,
      age: string,
      role: string
    ): VoiceProfile;
    
    getVoiceProfile(characterId: string): VoiceProfile | undefined;
    
    generateVoiceGuidelines(characterId: string): string;
    
    // Environment Consistency
    createEnvironmentStyleGuide(
      contextId: string,
      era: string,
      period: string,
      location: string,
      visualStyle: string
    ): EnvironmentStyleGuide;
    
    getEnvironmentGuide(contextId: string): EnvironmentStyleGuide | undefined;
    
    generateEnvironmentConsistencyPrompt(contextId: string): string;
    
    // Prompt Building with Consistency
    buildConsistentPrompts(options: PromptBuildOptions): BuiltPrompts;
    
    // Validation
    validatePrompt(
      prompt: string,
      characterIds: string[],
      contextId: string
    ): ValidationResult;
    
    // Complete workflow helpers
    setupContextWithConsistency(
      contextData: StoryContext,
      characterVisuals: Record<string, string>
    ): Promise<{ context: StoryContext; guides: any }>;
  }
}

// Character Consistency Methods
CinematicScriptWriter.prototype.createCharacterReference = function(
  characterId: string,
  characterName: string,
  visualDescription: string,
  era: string,
  style: string
) {
  return promptBuilder.createCharacterReference(
    characterId,
    characterName,
    visualDescription,
    era,
    style
  );
};

CinematicScriptWriter.prototype.getCharacterReference = function(characterId: string) {
  return consistencyManager.getCharacterReference(characterId);
};

CinematicScriptWriter.prototype.updateCharacterReference = function(
  characterId: string,
  updates: Partial<CharacterReferenceSheet>
) {
  return consistencyManager.updateCharacterReference(characterId, updates);
};

CinematicScriptWriter.prototype.generateCharacterConsistencyPrompt = function(
  characterId: string,
  situation?: string
) {
  return consistencyManager.generateCharacterConsistencyPrompt(characterId, situation);
};

// Voice Consistency Methods
CinematicScriptWriter.prototype.createVoiceProfile = function(
  characterId: string,
  characterName: string,
  personality: string,
  age: string,
  role: string
) {
  return promptBuilder.createVoiceProfile(characterId, characterName, personality, age, role);
};

CinematicScriptWriter.prototype.getVoiceProfile = function(characterId: string) {
  return consistencyManager.getVoiceProfile(characterId);
};

CinematicScriptWriter.prototype.generateVoiceGuidelines = function(characterId: string) {
  return consistencyManager.generateVoiceGuidelines(characterId);
};

// Environment Consistency Methods
CinematicScriptWriter.prototype.createEnvironmentStyleGuide = function(
  contextId: string,
  era: string,
  period: string,
  location: string,
  visualStyle: string
) {
  return promptBuilder.createEnvironmentStyleGuide(contextId, era, period, location, visualStyle);
};

CinematicScriptWriter.prototype.getEnvironmentGuide = function(contextId: string) {
  return consistencyManager.getEnvironmentGuide(contextId);
};

CinematicScriptWriter.prototype.generateEnvironmentConsistencyPrompt = function(contextId: string) {
  return consistencyManager.generateEnvironmentConsistencyPrompt(contextId);
};

// Prompt Building
CinematicScriptWriter.prototype.buildConsistentPrompts = function(options: PromptBuildOptions) {
  return promptBuilder.buildPrompts(options);
};

// Validation
CinematicScriptWriter.prototype.validatePrompt = function(
  prompt: string,
  characterIds: string[],
  contextId: string
) {
  return consistencyManager.validatePrompt(prompt, characterIds, contextId);
};

// Complete workflow helper
CinematicScriptWriter.prototype.setupContextWithConsistency = async function(
  contextData: StoryContext,
  characterVisuals: Record<string, string>
) {
  // Create character references and voice profiles
  const characterRefs: Record<string, CharacterReferenceSheet> = {};
  const voiceProfiles: Record<string, VoiceProfile> = {};
  
  for (const character of contextData.characters) {
    // Create character reference
    const ref = this.createCharacterReference(
      character.id,
      character.name,
      characterVisuals[character.id] || character.appearance,
      contextData.era,
      contextData.visualStyle
    );
    characterRefs[character.id] = ref;
    
    // Create voice profile
    const voice = this.createVoiceProfile(
      character.id,
      character.name,
      character.personality,
      'adult', // Could be parameterized
      character.role
    );
    voiceProfiles[character.id] = voice;
  }
  
  // Create environment guide
  const envGuide = this.createEnvironmentStyleGuide(
    contextData.id,
    contextData.era,
    contextData.period,
    contextData.location,
    contextData.visualStyle
  );
  
  return {
    context: contextData,
    guides: {
      characters: characterRefs,
      voices: voiceProfiles,
      environment: envGuide
    }
  };
};

// Export consistency types
export {
  CharacterReferenceSheet,
  VoiceProfile,
  EnvironmentStyleGuide,
  ValidationResult
} from './consistency-system';

export { BuiltPrompts, PromptBuildOptions } from './prompt-builder';


// =======================================================================
// STORAGE SYSTEM METHODS
// Manage saving files to Google Drive or local storage
// =======================================================================

import { StorageManager, StoragePreferences, SaveOptions, SaveResult } from './storage-manager';
import { StorageConfig } from './storage-adapter';

declare module './index' {
  interface CinematicScriptWriter {
    // Storage Setup
    storage: StorageManager;
    
    askStorageLocation(): Promise<any>;
    
    connectGoogleDrive(authCode?: string): Promise<any>;
    connectLocalStorage(): Promise<any>;
    disconnectStorage(): Promise<void>;
    getStorageStatus(): Promise<any>;
    saveToStorage(options: any, content: any): Promise<any>;
    saveScriptToStorage(title: string, contextId: string, scriptId: string, options?: any): Promise<any>;
    saveAllToGoogleDrive(title: string, authCode: string, content: any): Promise<any>;
    setupContextWithConsistency(contextData: any, characterVisuals: any): Promise<any>;
  }
}

// Initialize storage manager on prototype
Object.defineProperty(CinematicScriptWriter.prototype, 'storage', {
  get: function() {
    if (!this._storage) {
      this._storage = new StorageManager();
    }
    return this._storage;
  },
  enumerable: true,
  configurable: true
});

// Storage Setup Methods
CinematicScriptWriter.prototype.askStorageLocation = function() {
  return this.storage.askStorageLocation();
};

CinematicScriptWriter.prototype.connectGoogleDrive = function(authCode?: string) {
  return this.storage.connectGoogleDrive(authCode);
};

CinematicScriptWriter.prototype.connectLocalStorage = function() {
  return this.storage.connectLocal();
};

CinematicScriptWriter.prototype.disconnectStorage = function() {
  return this.storage.disconnect();
};

CinematicScriptWriter.prototype.getStorageStatus = function() {
  return this.storage.getStatus();
};

// Save Methods
CinematicScriptWriter.prototype.saveToStorage = function(options: SaveOptions, content: any) {
  return this.storage.saveAll(options, content);
};

CinematicScriptWriter.prototype.saveScriptToStorage = async function(
  title: string,
  contextId: string,
  scriptId: string,
  options: any = {}
) {
  // Access storage through public methods
  const script = await this.exportScript(scriptId, 'json').then(JSON.parse).catch(() => null);
  const storyContext = await this.getContext(contextId);
  const metadata = null; // Will be loaded from storage via memory
  
  // Get consistency data
  const characterRefs: any = {};
  const voiceProfiles: any = {};
  
  if (storyContext) {
    for (const char of storyContext.characters) {
      const ref = this.getCharacterReference(char.id);
      const voice = this.getVoiceProfile(char.id);
      if (ref) characterRefs[char.id] = ref;
      if (voice) voiceProfiles[char.id] = voice;
    }
  }
  
  const envGuide = this.getEnvironmentGuide(contextId);
  
  // Get prompts if script exists
  let prompts = null;
  if (script && script.scenes) {
    prompts = {
      shots: script.scenes.flatMap((s: any) => s.shots || []),
      negativePrompt: 'inconsistent character design, modern clothing, anachronisms'
    };
  }
  
  // Build story idea from script
  const storyIdea = script ? {
    title: script.title,
    summary: script.hook?.text || ''
  } : null;
  
  const content = {
    script,
    prompts,
    consistency: {
      characters: characterRefs,
      environment: envGuide
    },
    voice: voiceProfiles,
    metadata,
    storyIdea,
    context: storyContext
  };
  
  const saveOptions: SaveOptions = {
    title,
    contextId,
    scriptId,
    includeScript: options.includePrompts !== false,
    includePrompts: options.includePrompts !== false,
    includeConsistency: options.includeConsistency !== false,
    includeMetadata: options.includeMetadata !== false,
    includeVoice: options.includeVoice !== false
  };
  
  return this.storage.saveAll(saveOptions, content);
};

CinematicScriptWriter.prototype.saveAllToGoogleDrive = async function(
  title: string,
  authCode: string,
  content: any
) {
  // Connect to Google Drive
  const connectResult = await this.storage.connectGoogleDrive(authCode);
  if (!connectResult.success) {
    return {
      success: false,
      folder: { id: '', name: '', path: '' },
      files: [],
      errors: [connectResult.message],
      shareLink: undefined
    };
  }
  
  // Save all content
  const saveOptions: SaveOptions = {
    title,
    contextId: content.context?.id || 'unknown',
    includeScript: true,
    includePrompts: true,
    includeConsistency: true,
    includeMetadata: true,
    includeVoice: true
  };
  
  return this.storage.saveAll(saveOptions, content);
};

// Export storage types
export {
  StorageManager,
  StoragePreferences,
  SaveOptions,
  SaveResult,
  SavedFile
} from './storage-manager';

export { StorageConfig, StorageAdapter } from './storage-adapter';
