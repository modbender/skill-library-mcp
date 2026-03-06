/**
 * Consistent Prompt Builder
 * Builds image/video generation prompts with character and environment consistency
 */

import { 
  consistencyManager, 
  CharacterReferenceSheet, 
  EnvironmentStyleGuide,
  VoiceProfile 
} from './consistency-system';

export interface PromptBuildOptions {
  characterIds: string[];
  contextId: string;
  shotType: string;
  cameraAngle: string;
  cameraMovement: string;
  lighting: string;
  mood: string;
  action?: string;
  background?: string;
  timeOfDay?: string;
  includeEnvironment?: boolean;
  includeNegativePrompts?: boolean;
}

export interface BuiltPrompts {
  imagePrompt: string;
  videoPrompt: string;
  negativePrompt: string;
  consistencyNotes: string;
  characterConsistencyStrings: Record<string, string>;
  environmentConsistencyString: string;
  voiceGuidelines: Record<string, string>;
  validationWarnings: string[];
}

export class ConsistentPromptBuilder {
  
  /**
   * Build complete prompts with full consistency
   */
  buildPrompts(options: PromptBuildOptions): BuiltPrompts {
    const { characterIds, contextId } = options;
    
    // Get consistency data
    const characterSheets = characterIds.map(id => 
      consistencyManager.getCharacterReference(id)
    ).filter(Boolean) as CharacterReferenceSheet[];
    
    const environmentGuide = consistencyManager.getEnvironmentGuide(contextId);
    
    // Build consistency strings
    const characterConsistencyStrings: Record<string, string> = {};
    const voiceGuidelines: Record<string, string> = {};
    
    characterSheets.forEach(sheet => {
      characterConsistencyStrings[sheet.characterId] = 
        this.buildCharacterConsistencyString(sheet);
      
      const voiceProfile = consistencyManager.getVoiceProfile(sheet.characterId);
      if (voiceProfile) {
        voiceGuidelines[sheet.characterId] = 
          this.buildVoiceGuidelineString(voiceProfile);
      }
    });
    
    const environmentConsistencyString = environmentGuide 
      ? this.buildEnvironmentConsistencyString(environmentGuide)
      : '';
    
    // Build main prompts
    const imagePrompt = this.buildImagePrompt(options, characterSheets, environmentGuide);
    const videoPrompt = this.buildVideoPrompt(options, characterSheets, environmentGuide);
    const negativePrompt = this.buildNegativePrompt(options, characterSheets, environmentGuide);
    
    // Validate
    const validationWarnings = this.validatePrompts(
      imagePrompt, 
      characterIds, 
      contextId
    );
    
    // Build consistency notes
    const consistencyNotes = this.buildConsistencyNotes(
      characterSheets,
      environmentGuide
    );
    
    return {
      imagePrompt,
      videoPrompt,
      negativePrompt,
      consistencyNotes,
      characterConsistencyStrings,
      environmentConsistencyString,
      voiceGuidelines,
      validationWarnings
    };
  }
  
  /**
   * Build image generation prompt with consistency
   */
  private buildImagePrompt(
    options: PromptBuildOptions,
    characterSheets: CharacterReferenceSheet[],
    environmentGuide?: EnvironmentStyleGuide
  ): string {
    const parts: string[] = [];
    
    // 1. Shot type and camera
    parts.push(`${options.shotType} shot`);
    parts.push(`${options.cameraAngle} camera angle`);
    
    // 2. Subject with character consistency
    const characterDescriptions = characterSheets.map(sheet => {
      const baseDesc = sheet.visual.baseDescription;
      const features = this.formatKeyFeatures(sheet.visual.features);
      const colors = sheet.visual.colorPalette.signature;
      return `${baseDesc}, ${features}, ${colors}`;
    });
    
    if (characterDescriptions.length === 1) {
      parts.push(characterDescriptions[0]);
    } else {
      parts.push(characterDescriptions.join('; '));
    }
    
    // 3. Action/Expression
    if (options.action) {
      parts.push(options.action);
    }
    
    // 4. Wardrobe (era-appropriate)
    const wardrobeDescs = characterSheets.map(sheet => {
      return `${sheet.characterName} wearing ${sheet.wardrobe.defaultOutfit.description}`;
    });
    if (wardrobeDescs.length > 0) {
      parts.push(wardrobeDescs.join(', '));
    }
    
    // 5. Environment
    if (options.includeEnvironment !== false && environmentGuide) {
      parts.push(this.buildEnvironmentDescription(environmentGuide, options));
    } else if (options.background) {
      parts.push(options.background);
    }
    
    // 6. Lighting
    parts.push(`${options.lighting} lighting`);
    if (options.timeOfDay) {
      parts.push(`${options.timeOfDay} light`);
    }
    
    // 7. Mood
    parts.push(`${options.mood} mood`);
    
    // 8. Style consistency
    if (characterSheets.length > 0) {
      const style = characterSheets[0].style;
      parts.push(style.artStyle);
      parts.push(...style.consistencyKeywords);
    }
    
    // 9. Quality modifiers
    parts.push('highly detailed, 8k, cinematic composition');
    
    return parts.filter(Boolean).join(', ');
  }
  
  /**
   * Build video generation prompt with consistency
   */
  private buildVideoPrompt(
    options: PromptBuildOptions,
    characterSheets: CharacterReferenceSheet[],
    environmentGuide?: EnvironmentStyleGuide
  ): string {
    const parts: string[] = [];
    
    // 1. Shot and camera movement
    parts.push(`${options.shotType} shot`);
    parts.push(`${options.cameraMovement} camera movement`);
    parts.push(`${options.cameraAngle} angle`);
    
    // 2. Subject with consistency
    const characterDescriptions = characterSheets.map(sheet => {
      return `${sheet.characterName}: ${sheet.visual.baseDescription}`;
    });
    parts.push(characterDescriptions.join('; '));
    
    // 3. Action (more detailed for video)
    if (options.action) {
      parts.push(`${options.action}, natural movement`);
    }
    
    // 4. Environment context
    if (environmentGuide && options.includeEnvironment !== false) {
      parts.push(`Setting: ${environmentGuide.location}`);
      parts.push(`Architecture: ${environmentGuide.architecture.buildingStyles[0]?.type || 'period-appropriate'}`);
    }
    
    // 5. Lighting and atmosphere
    parts.push(`${options.lighting} lighting`);
    parts.push(`${options.mood} atmosphere`);
    
    // 6. Technical specs
    parts.push('smooth motion, 24fps cinematic, high quality');
    
    return parts.filter(Boolean).join(', ');
  }
  
  /**
   * Build negative prompt to avoid inconsistencies
   */
  private buildNegativePrompt(
    options: PromptBuildOptions,
    characterSheets: CharacterReferenceSheet[],
    environmentGuide?: EnvironmentStyleGuide
  ): string {
    const negatives: string[] = [];
    
    // Character inconsistencies
    negatives.push('inconsistent character design');
    negatives.push('different character in each frame');
    negatives.push('changing features');
    negatives.push('wrong eye color');
    negatives.push('wrong hair color');
    negatives.push('anatomical errors');
    
    // Environment anachronisms
    if (environmentGuide) {
      negatives.push(...environmentGuide.props.forbidden);
      negatives.push('modern buildings', 'modern clothing', 'anachronistic elements');
    }
    
    // Quality issues
    negatives.push('blurry', 'low quality', 'deformed', 'mutated');
    negatives.push('extra limbs', 'missing limbs', 'bad anatomy');
    negatives.push('watermark', 'signature', 'text', 'logo');
    
    // Character-specific negatives
    characterSheets.forEach(sheet => {
      negatives.push(...sheet.style.negativePrompts);
    });
    
    return negatives.join(', ');
  }
  
  /**
   * Build character consistency string for reuse
   */
  private buildCharacterConsistencyString(sheet: CharacterReferenceSheet): string {
    const parts = [
      `CHARACTER: ${sheet.characterName}`,
      `BASE: ${sheet.visual.baseDescription}`,
      `FEATURES: ${this.formatKeyFeatures(sheet.visual.features)}`,
      `COLORS: ${this.formatColorPalette(sheet.visual.colorPalette)}`,
      `WARDROBE: ${sheet.wardrobe.defaultOutfit.description}`,
      `STYLE: ${sheet.style.artStyle}`,
      `KEY IDENTIFIERS: ${sheet.style.consistencyKeywords.join(', ')}`
    ];
    return parts.join('\n');
  }
  
  /**
   * Build environment consistency string
   */
  private buildEnvironmentConsistencyString(guide: EnvironmentStyleGuide): string {
    const parts = [
      `ERA: ${guide.era}`,
      `LOCATION: ${guide.location}`,
      `ARCHITECTURE: ${guide.architecture.buildingStyles.map(b => b.type).join(', ')}`,
      `MATERIALS: ${guide.architecture.materials.join(', ')}`,
      `CLOTHING MATERIALS: ${guide.clothing.materials.join(', ')}`,
      `CLOTHING COLORS: ${guide.clothing.colors.join(', ')}`,
      `FORBIDDEN: ${guide.props.forbidden.join(', ')}`
    ];
    return parts.join('\n');
  }
  
  /**
   * Build voice guideline string
   */
  private buildVoiceGuidelineString(profile: VoiceProfile): string {
    return `
${profile.characterName} Voice:
- Pitch: ${profile.speech.pitch}, Speed: ${profile.speech.speed}
- Volume: ${profile.speech.volume}, Clarity: ${profile.speech.clarity}
- Vocabulary: ${profile.language.vocabularyLevel}, Formality: ${profile.language.formality}
- Catchphrases: ${profile.language.catchphrases.join(', ') || 'None'}
- Examples: "${profile.examples.greeting}" | "${profile.examples.question}"
    `.trim();
  }
  
  /**
   * Build environment description
   */
  private buildEnvironmentDescription(
    guide: EnvironmentStyleGuide,
    options: PromptBuildOptions
  ): string {
    const parts = [
      `${guide.era} setting`,
      `${guide.location}`,
      guide.architecture.buildingStyles[0]?.description || '',
      options.timeOfDay ? `${guide.environment.timeOfDayLighting[options.timeOfDay] || ''}` : ''
    ];
    return parts.filter(Boolean).join(', ');
  }
  
  /**
   * Format key features for prompt
   */
  private formatKeyFeatures(features: CharacterReferenceSheet['visual']['features']): string {
    const parts = [];
    
    if (features.face.eyes.color) {
      parts.push(`${features.face.eyes.color} eyes`);
    }
    if (features.face.eyes.shape) {
      parts.push(`${features.face.eyes.shape} eye shape`);
    }
    if (features.hair.color && features.hair.style) {
      parts.push(`${features.hair.color} ${features.hair.style} hair`);
    }
    if (features.body.build) {
      parts.push(`${features.body.build} build`);
    }
    if (features.nonHuman && features.nonHuman.length > 0) {
      features.nonHuman.forEach(f => {
        parts.push(`${f.color} ${f.description}`);
      });
    }
    
    return parts.join(', ');
  }
  
  /**
   * Format color palette
   */
  private formatColorPalette(palette: CharacterReferenceSheet['visual']['colorPalette']): string {
    const colors = [
      ...palette.primary,
      palette.skin,
      palette.hair
    ].filter(Boolean);
    return colors.join(', ');
  }
  
  /**
   * Validate prompts for consistency issues
   */
  private validatePrompts(
    prompt: string,
    characterIds: string[],
    contextId: string
  ): string[] {
    const warnings: string[] = [];
    
    const result = consistencyManager.validatePrompt(
      prompt,
      characterIds,
      contextId
    );
    
    warnings.push(...result.warnings);
    warnings.push(...result.suggestions);
    
    return warnings;
  }
  
  /**
   * Build comprehensive consistency notes
   */
  private buildConsistencyNotes(
    characterSheets: CharacterReferenceSheet[],
    environmentGuide?: EnvironmentStyleGuide
  ): string {
    const parts: string[] = [];
    
    parts.push('=== CHARACTER CONSISTENCY ===');
    characterSheets.forEach(sheet => {
      parts.push(`\n${sheet.characterName}:`);
      parts.push(`  Base: ${sheet.visual.baseDescription}`);
      parts.push(`  Signature Colors: ${sheet.visual.colorPalette.signature}`);
      parts.push(`  Key Features: ${this.formatKeyFeatures(sheet.visual.features)}`);
      parts.push(`  Wardrobe: ${sheet.wardrobe.defaultOutfit.description}`);
    });
    
    if (environmentGuide) {
      parts.push('\n=== ENVIRONMENT CONSISTENCY ===');
      parts.push(`Era: ${environmentGuide.era}`);
      parts.push(`Location: ${environmentGuide.location}`);
      parts.push(`Architecture: ${environmentGuide.architecture.buildingStyles.map(b => b.type).join(', ')}`);
      parts.push(`Forbidden Elements: ${environmentGuide.props.forbidden.slice(0, 5).join(', ')}...`);
    }
    
    return parts.join('\n');
  }
  
  /**
   * Create character reference from description
   */
  createCharacterReference(
    characterId: string,
    characterName: string,
    visualDescription: string,
    era: string,
    style: string
  ): CharacterReferenceSheet {
    return consistencyManager.createCharacterReference(
      characterId,
      characterName,
      visualDescription,
      era,
      style
    );
  }
  
  /**
   * Create voice profile
   */
  createVoiceProfile(
    characterId: string,
    characterName: string,
    personality: string,
    age: string,
    role: string
  ): VoiceProfile {
    return consistencyManager.createVoiceProfile(
      characterId,
      characterName,
      personality,
      age,
      role
    );
  }
  
  /**
   * Create environment style guide
   */
  createEnvironmentStyleGuide(
    contextId: string,
    era: string,
    period: string,
    location: string,
    visualStyle: string
  ): EnvironmentStyleGuide {
    return consistencyManager.createEnvironmentStyleGuide(
      contextId,
      era,
      period,
      location,
      visualStyle
    );
  }
}

// Export singleton
export const promptBuilder = new ConsistentPromptBuilder();

export default promptBuilder;
