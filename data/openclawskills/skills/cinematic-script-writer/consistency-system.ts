/**
 * Consistency System
 * Ensures character, voice, and environment consistency across all generated content
 */

// ============================================================================
// Character Consistency Types
// ============================================================================

export interface CharacterReferenceSheet {
  characterId: string;
  characterName: string;
  version: string;
  createdAt: string;
  updatedAt: string;
  
  // Visual Consistency
  visual: {
    baseDescription: string;           // Core appearance never changes
    features: CharacterFeatures;       // Detailed breakdown
    colorPalette: ColorPalette;        // Exact colors to use
    proportions: BodyProportions;      // Size relationships
    expressions: ExpressionGuide;      // How emotions look
    angles: AngleReferences;           // How they look from different views
  };
  
  // Wardrobe Consistency
  wardrobe: {
    defaultOutfit: Outfit;
    variations: Outfit[];              // Different situations
    accessories: Accessory[];
    eraAppropriate: boolean;
    clothingDetails: string;
  };
  
  // Style Consistency
  style: {
    artStyle: string;                  // pixar-3d, anime, etc.
    renderingNotes: string;
    consistencyKeywords: string[];     // Words to always include
    negativePrompts: string[];         // What to avoid
    referenceArtists?: string[];
  };
}

export interface CharacterFeatures {
  face: {
    shape: string;
    skinTone: string;
    skinTexture: string;
    forehead: string;
    eyebrows: string;
    eyes: {
      shape: string;
      color: string;
      size: string;
      specialFeatures: string;
      expressionDefault: string;
    };
    nose: {
      shape: string;
      size: string;
      specialFeatures: string;
    };
    mouth: {
      shape: string;
      lips: string;
      teeth: string;
      expressionDefault: string;
    };
    ears: string;
    cheekbones: string;
    jawline: string;
    chin: string;
    facialHair?: string;
    distinctiveMarks: string[];        // Scars, moles, birthmarks
  };
  
  hair: {
    color: string;
    texture: string;
    length: string;
    style: string;
    distinctiveFeatures: string;
    movement: string;
  };
  
  body: {
    type: string;
    height: string;
    build: string;
    posture: string;
    distinctiveFeatures: string[];
  };
  
  // Non-human features
  nonHuman?: {
    type: string;                      // horns, wings, tail, etc.
    description: string;
    color: string;
    texture: string;
    size: string;
    movement: string;
  }[];
}

export interface ColorPalette {
  primary: string[];                   // Main colors
  secondary: string[];                 // Accent colors
  skin: string;
  hair: string;
  eyes: string;
  clothing: string[];
  signature: string;                   // Most recognizable color
}

export interface BodyProportions {
  headToBody: string;
  specialRatios: string[];
  comparativeSize: string;             // "Taller than average", etc.
}

export interface ExpressionGuide {
  neutral: string;
  happy: string;
  sad: string;
  angry: string;
  surprised: string;
  scared: string;
  thinking: string;
  mischievous: string;
  determined: string;
  custom?: Record<string, string>;     // Character-specific expressions
}

export interface AngleReferences {
  front: string;
  threeQuarter: string;
  profile: string;
  back: string;
  lowAngle: string;
  highAngle: string;
}

export interface Outfit {
  name: string;
  occasion: string;
  description: string;
  era: string;
  colors: string[];
  materials: string[];
  components: {
    head?: string;
    top: string;
    bottom: string;
    footwear?: string;
    outerwear?: string;
  };
  accessories: string[];
}

export interface Accessory {
  name: string;
  description: string;
    alwaysWorn: boolean;
  significance?: string;
}

// ============================================================================
// Voice Consistency Types
// ============================================================================

export interface VoiceProfile {
  characterId: string;
  characterName: string;
  version: string;
  
  // Speech Characteristics
  speech: {
    pitch: 'very-high' | 'high' | 'medium' | 'low' | 'very-low';
    speed: 'very-fast' | 'fast' | 'normal' | 'slow' | 'very-slow';
    volume: 'quiet' | 'soft' | 'normal' | 'loud' | 'booming';
    clarity: 'mumbled' | 'soft' | 'clear' | 'crisp' | 'booming';
    rhythm: string;                    // Speech pattern
    accent?: string;
    dialect?: string;
    lisp?: string;
    stutter?: boolean;
    fillerWords: string[];             // "um", "like", etc.
  };
  
  // Language Patterns
  language: {
    vocabularyLevel: 'simple' | 'casual' | 'educated' | 'sophisticated' | 'archaic';
    sentenceLength: 'short' | 'medium' | 'long' | 'variable';
    formality: 'very-casual' | 'casual' | 'neutral' | 'formal' | 'very-formal';
    slangUsage: 'none' | 'minimal' | 'moderate' | 'heavy';
    technicalTerms: string[];          // Field-specific jargon
    catchphrases: string[];
    recurringPhrases: string[];
    uniqueWords: string[];             // Made-up or character-specific words
  };
  
  // Personality in Speech
  personality: {
    humorStyle?: 'witty' | 'sarcastic' | 'slapstick' | 'dry' | 'dark' | 'none';
    directness: 'very-indirect' | 'indirect' | 'balanced' | 'direct' | 'blunt';
    emotionality: 'stoic' | 'reserved' | 'balanced' | 'expressive' | 'dramatic';
    politeness: 'rude' | 'casual' | 'polite' | 'formal' | 'excessive';
    confidence: 'insecure' | 'hesitant' | 'moderate' | 'confident' | 'arrogant';
  };
  
  // Emotional Voice Mapping
  emotions: {
    neutral: VoiceEmotion;
    happy: VoiceEmotion;
    sad: VoiceEmotion;
    angry: VoiceEmotion;
    surprised: VoiceEmotion;
    scared: VoiceEmotion;
    excited: VoiceEmotion;
    tired: VoiceEmotion;
    custom?: Record<string, VoiceEmotion>;
  };
  
  // Speech Examples
  examples: {
    greeting: string;
    farewell: string;
    question: string;
    exclamation: string;
    apology: string;
    threat: string;
    joke: string;
    custom: Record<string, string>;
  };
}

export interface VoiceEmotion {
  pitchShift: 'much-higher' | 'higher' | 'same' | 'lower' | 'much-lower';
  speedShift: 'much-faster' | 'faster' | 'same' | 'slower' | 'much-slower';
  volumeShift: 'much-quieter' | 'quieter' | 'same' | 'louder' | 'much-louder';
  specialCharacteristics: string[];
  description: string;
}

// ============================================================================
// Environment Consistency Types
// ============================================================================

export interface EnvironmentStyleGuide {
  contextId: string;
  era: string;
  period: string;
  location: string;
  createdAt: string;
  updatedAt: string;
  
  // Era Specifications
  eraSpecs: {
    name: string;
    timePeriod: string;
    geographicRegion: string;
    historicalAccuracy: 'strict' | 'loose' | 'fantasy-inspired';
    anachronismsAllowed: string[];     // Intentional exceptions
    anachronismsForbidden: string[];   // Strictly never allowed
  };
  
  // Architecture
  architecture: {
    buildingStyles: BuildingStyle[];
    materials: string[];
    constructionTechniques: string[];
    decorativeElements: string[];
    colorPalettes: string[];
    scale: string;                     // Size relationships
    distinctiveFeatures: string[];
  };
  
  // Clothing & Fashion
  clothing: {
    socialClasses: Record<string, ClothingClass>;
    materials: string[];
    colors: string[];
    patterns: string[];
    accessories: string[];
    footwear: string[];
    headwear: string[];
    jewelry: string[];
    modestyStandards: string;
    weatherAppropriate: string;
  };
  
  // Props & Objects
  props: {
    everyday: string[];                // Common household items
    professional: string[];            // Work-related
    luxury: string[];                  // High-status items
    weapons?: string[];                // If applicable
    transportation: string[];
    lighting: string[];                // Lamps, candles, etc.
    eating: string[];                  // Utensils, dishes
    forbidden: string[];               // Modern items to avoid
  };
  
  // Environment Details
  environment: {
    landscape: string;
    vegetation: string[];
    wildlife: string[];
    weatherPatterns: string[];
    timeOfDayLighting: Record<string, string>;
    atmosphericConditions: string[];
  };
  
  // People & Society
  society: {
    populationDensity: string;
    diversity: string;
    occupations: string[];
    socialBehaviors: string[];
    greetings: string[];
    customs: string[];
    taboos: string[];
  };
  
  // Visual Style
  visualStyle: {
    colorPalette: string[];
    lightingStyle: string;
    textureStyle: string;
    atmosphere: string;
    referenceImages?: string[];
    referenceFilms?: string[];
    artDirection: string;
  };
}

export interface BuildingStyle {
  type: string;
  description: string;
  materials: string[];
  features: string[];
  purpose: string;                     // residential, temple, market, etc.
  socialClass?: string;
}

export interface ClothingClass {
  description: string;
  men: string;
  women: string;
  children: string;
  materials: string[];
  colors: string[];
  accessories: string[];
}

// ============================================================================
// Consistency Validators
// ============================================================================

export interface ConsistencyValidator {
  validateCharacter(prompt: string, reference: CharacterReferenceSheet): ValidationResult;
  validateEnvironment(prompt: string, guide: EnvironmentStyleGuide): ValidationResult;
  validateAnachronisms(prompt: string, era: string): ValidationResult;
  validateVoice(dialogue: string, voice: VoiceProfile): ValidationResult;
}

export interface ValidationResult {
  valid: boolean;
  warnings: string[];
  errors: string[];
  suggestions: string[];
  correctedPrompt?: string;
}

// ============================================================================
// Consistency Manager
// ============================================================================

export class ConsistencyManager {
  private characterSheets: Map<string, CharacterReferenceSheet> = new Map();
  private voiceProfiles: Map<string, VoiceProfile> = new Map();
  private environmentGuides: Map<string, EnvironmentStyleGuide> = new Map();
  
  // Character Consistency
  
  createCharacterReference(
    characterId: string,
    characterName: string,
    visualDescription: string,
    era: string,
    style: string
  ): CharacterReferenceSheet {
    const sheet: CharacterReferenceSheet = {
      characterId,
      characterName,
      version: '1.0',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      visual: this.parseVisualDescription(visualDescription, style),
      wardrobe: this.generateWardrobe(era, characterName),
      style: {
        artStyle: style,
        renderingNotes: this.getRenderingNotes(style),
        consistencyKeywords: this.generateConsistencyKeywords(characterName, visualDescription),
        negativePrompts: this.generateNegativePrompts(era)
      }
    };
    
    this.characterSheets.set(characterId, sheet);
    return sheet;
  }
  
  getCharacterReference(characterId: string): CharacterReferenceSheet | undefined {
    return this.characterSheets.get(characterId);
  }
  
  updateCharacterReference(
    characterId: string,
    updates: Partial<CharacterReferenceSheet>
  ): CharacterReferenceSheet | undefined {
    const existing = this.characterSheets.get(characterId);
    if (!existing) return undefined;
    
    const updated = {
      ...existing,
      ...updates,
      updatedAt: new Date().toISOString()
    };
    
    this.characterSheets.set(characterId, updated);
    return updated;
  }
  
  // Generate consistency prompt for image generation
  generateCharacterConsistencyPrompt(
    characterId: string,
    situation?: string
  ): string {
    const sheet = this.characterSheets.get(characterId);
    if (!sheet) return '';
    
    const parts = [
      // Base description
      sheet.visual.baseDescription,
      
      // Key features
      this.formatFeatures(sheet.visual.features),
      
      // Colors
      this.formatColorPalette(sheet.visual.colorPalette),
      
      // Wardrobe for situation
      situation ? this.getWardrobeForSituation(sheet, situation) : sheet.wardrobe.defaultOutfit.description,
      
      // Style consistency
      ...sheet.style.consistencyKeywords,
      
      // Art style
      sheet.style.artStyle
    ];
    
    return parts.filter(Boolean).join(', ');
  }
  
  // Voice Consistency
  
  createVoiceProfile(
    characterId: string,
    characterName: string,
    personality: string,
    age: string,
    role: string
  ): VoiceProfile {
    const profile: VoiceProfile = {
      characterId,
      characterName,
      version: '1.0',
      speech: this.inferSpeechCharacteristics(personality, age),
      language: this.inferLanguagePatterns(personality, role),
      personality: this.inferPersonalityTraits(personality),
      emotions: this.generateEmotionMap(personality),
      examples: this.generateSpeechExamples(characterName, personality)
    };
    
    this.voiceProfiles.set(characterId, profile);
    return profile;
  }
  
  getVoiceProfile(characterId: string): VoiceProfile | undefined {
    return this.voiceProfiles.get(characterId);
  }
  
  // Generate dialogue guidelines
  generateVoiceGuidelines(characterId: string): string {
    const profile = this.voiceProfiles.get(characterId);
    if (!profile) return '';
    
    return `
Voice Profile for ${profile.characterName}:
- Pitch: ${profile.speech.pitch}, Speed: ${profile.speech.speed}, Volume: ${profile.speech.volume}
- Vocabulary: ${profile.language.vocabularyLevel}, Formality: ${profile.language.formality}
- Catchphrases: ${profile.language.catchphrases.join(', ')}
- Speech Examples:
  - Greeting: "${profile.examples.greeting}"
  - Question: "${profile.examples.question}"
  - Exclamation: "${profile.examples.exclamation}"
    `.trim();
  }
  
  // Environment Consistency
  
  createEnvironmentStyleGuide(
    contextId: string,
    era: string,
    period: string,
    location: string,
    visualStyle: string
  ): EnvironmentStyleGuide {
    const guide: EnvironmentStyleGuide = {
      contextId,
      era,
      period,
      location,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      eraSpecs: this.defineEraSpecs(era, period),
      architecture: this.defineArchitecture(era, location),
      clothing: this.defineClothing(era),
      props: this.defineProps(era),
      environment: this.defineEnvironment(era, location),
      society: this.defineSociety(era),
      visualStyle: this.defineVisualStyle(era, visualStyle)
    };
    
    this.environmentGuides.set(contextId, guide);
    return guide;
  }
  
  getEnvironmentGuide(contextId: string): EnvironmentStyleGuide | undefined {
    return this.environmentGuides.get(contextId);
  }
  
  // Validate prompt for consistency
  validatePrompt(
    prompt: string,
    characterIds: string[],
    contextId: string
  ): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    const suggestions: string[] = [];
    
    const guide = this.environmentGuides.get(contextId);
    if (guide) {
      // Check for anachronisms
      guide.eraSpecs.anachronismsForbidden.forEach(item => {
        if (prompt.toLowerCase().includes(item.toLowerCase())) {
          errors.push(`Anachronism detected: "${item}" does not belong in ${guide.eraSpecs.name}`);
        }
      });
      
      // Check for era-appropriate elements
      guide.clothing.materials.forEach(material => {
        if (!prompt.toLowerCase().includes(material.toLowerCase())) {
          suggestions.push(`Consider using era-appropriate material: ${material}`);
        }
      });
    }
    
    return {
      valid: errors.length === 0,
      warnings,
      errors,
      suggestions
    };
  }
  
  // Generate environment consistency prompt
  generateEnvironmentConsistencyPrompt(contextId: string): string {
    const guide = this.environmentGuides.get(contextId);
    if (!guide) return '';
    
    const parts = [
      `Setting: ${guide.location}, ${guide.era}`,
      `Architecture: ${guide.architecture.buildingStyles.map(b => b.type).join(', ')}`,
      `Materials: ${guide.architecture.materials.join(', ')}`,
      `Clothing: ${guide.clothing.materials.join(', ')} fabrics`,
      `Colors: ${guide.visualStyle.colorPalette.join(', ')}`,
      `Atmosphere: ${guide.visualStyle.atmosphere}`,
      `Style: ${guide.visualStyle.artDirection}`
    ];
    
    return parts.join(', ');
  }
  
  // Private helper methods
  
  private parseVisualDescription(description: string, style: string): CharacterReferenceSheet['visual'] {
    // Parse natural language description into structured format
    // This is a simplified version - could use NLP for better parsing
    return {
      baseDescription: description,
      features: this.extractFeatures(description),
      colorPalette: this.extractColors(description),
      proportions: { headToBody: '1:6', specialRatios: [], comparativeSize: 'average' },
      expressions: this.generateExpressionGuide(description),
      angles: this.generateAngleReferences(description)
    };
  }
  
  private extractFeatures(description: string): CharacterFeatures {
    // Extract features from description
    return {
      face: {
        shape: '',
        skinTone: '',
        skinTexture: '',
        forehead: '',
        eyebrows: '',
        eyes: {
          shape: '',
          color: '',
          size: '',
          specialFeatures: '',
          expressionDefault: ''
        },
        nose: { shape: '', size: '', specialFeatures: '' },
        mouth: { shape: '', lips: '', teeth: '', expressionDefault: '' },
        ears: '',
        cheekbones: '',
        jawline: '',
        chin: '',
        distinctiveMarks: []
      },
      hair: { color: '', texture: '', length: '', style: '', distinctiveFeatures: '', movement: '' },
      body: { type: '', height: '', build: '', posture: '', distinctiveFeatures: [] },
      nonHuman: []
    };
  }
  
  private extractColors(description: string): ColorPalette {
    // Extract color information
    return {
      primary: [],
      secondary: [],
      skin: '',
      hair: '',
      eyes: '',
      clothing: [],
      signature: ''
    };
  }
  
  private generateExpressionGuide(description: string): ExpressionGuide {
    return {
      neutral: '',
      happy: '',
      sad: '',
      angry: '',
      surprised: '',
      scared: '',
      thinking: '',
      mischievous: '',
      determined: ''
    };
  }
  
  private generateAngleReferences(description: string): AngleReferences {
    return {
      front: '',
      threeQuarter: '',
      profile: '',
      back: '',
      lowAngle: '',
      highAngle: ''
    };
  }
  
  private generateWardrobe(era: string, characterName: string): CharacterReferenceSheet['wardrobe'] {
    return {
      defaultOutfit: {
        name: 'Default',
        occasion: 'Everyday',
        description: '',
        era: era,
        colors: [],
        materials: [],
        components: { top: '', bottom: '' },
        accessories: []
      },
      variations: [],
      accessories: [],
      eraAppropriate: true,
      clothingDetails: ''
    };
  }
  
  private getRenderingNotes(style: string): string {
    const notes: Record<string, string> = {
      'pixar-3d': 'High-quality 3D render, subsurface scattering on skin, appealing character design',
      'anime': 'Cel-shaded, clean lines, expressive eyes, limited animation style',
      'disney-classic': 'Hand-drawn aesthetic, fluid animation, rich colors',
      'spider-verse': 'On twos frame rate, comic book dots, offset printing style'
    };
    return notes[style] || 'Consistent art style throughout';
  }
  
  private generateConsistencyKeywords(name: string, description: string): string[] {
    return [
      'consistent character design',
      'same character across frames',
      'character continuity'
    ];
  }
  
  private generateNegativePrompts(era: string): string[] {
    return [
      'modern clothing',
      'anachronistic elements',
      'inconsistent features'
    ];
  }
  
  private formatFeatures(features: CharacterFeatures): string {
    const parts = [];
    if (features.face.eyes.color) parts.push(`${features.face.eyes.color} eyes`);
    if (features.hair.color) parts.push(`${features.hair.color} ${features.hair.style} hair`);
    if (features.body.build) parts.push(`${features.body.build} build`);
    return parts.join(', ');
  }
  
  private formatColorPalette(palette: ColorPalette): string {
    return `Color scheme: ${palette.primary.join(', ')} with ${palette.secondary.join(', ')} accents`;
  }
  
  private getWardrobeForSituation(sheet: CharacterReferenceSheet, situation: string): string {
    const variation = sheet.wardrobe.variations.find(v => 
      situation.toLowerCase().includes(v.occasion.toLowerCase())
    );
    return variation?.description || sheet.wardrobe.defaultOutfit.description;
  }
  
  private inferSpeechCharacteristics(personality: string, age: string): VoiceProfile['speech'] {
    return {
      pitch: 'medium',
      speed: 'normal',
      volume: 'normal',
      clarity: 'clear',
      rhythm: 'natural',
      fillerWords: []
    };
  }
  
  private inferLanguagePatterns(personality: string, role: string): VoiceProfile['language'] {
    return {
      vocabularyLevel: 'casual',
      sentenceLength: 'medium',
      formality: 'casual',
      slangUsage: 'minimal',
      technicalTerms: [],
      catchphrases: [],
      recurringPhrases: [],
      uniqueWords: []
    };
  }
  
  private inferPersonalityTraits(personality: string): VoiceProfile['personality'] {
    return {
      humorStyle: undefined,
      directness: 'balanced',
      emotionality: 'balanced',
      politeness: 'polite',
      confidence: 'moderate'
    };
  }
  
  private generateEmotionMap(personality: string): VoiceProfile['emotions'] {
    const defaultEmotion: VoiceEmotion = {
      pitchShift: 'same',
      speedShift: 'same',
      volumeShift: 'same',
      specialCharacteristics: [],
      description: ''
    };
    
    return {
      neutral: defaultEmotion,
      happy: defaultEmotion,
      sad: defaultEmotion,
      angry: defaultEmotion,
      surprised: defaultEmotion,
      scared: defaultEmotion,
      excited: defaultEmotion,
      tired: defaultEmotion
    };
  }
  
  private generateSpeechExamples(name: string, personality: string): VoiceProfile['examples'] {
    return {
      greeting: `Hello!`,
      farewell: `Goodbye!`,
      question: `What do you mean?`,
      exclamation: `Oh my!`,
      apology: `I'm sorry.`,
      threat: `You'll regret this!`,
      joke: `That's funny!`,
      custom: {}
    };
  }
  
  private defineEraSpecs(era: string, period: string): EnvironmentStyleGuide['eraSpecs'] {
    const anachronisms: Record<string, string[]> = {
      'Ramayana Era': ['glasses', 'watches', 'modern footwear', 'synthetic fabrics', 'plastic', 'metal zippers', 'buttons', 'modern jewelry'],
      'Ancient Greece': ['modern clothing', 'synthetic materials', 'electronics'],
      'Medieval': ['modern clothing', 'glasses', 'watches'],
      'default': ['smartphones', 'computers', 'cars', 'electricity', 'plastic']
    };
    
    return {
      name: era,
      timePeriod: period,
      geographicRegion: '',
      historicalAccuracy: 'strict',
      anachronismsAllowed: [],
      anachronismsForbidden: anachronisms[era] || anachronisms['default']
    };
  }
  
  private defineArchitecture(era: string, location: string): EnvironmentStyleGuide['architecture'] {
    const buildingStyles: Record<string, BuildingStyle[]> = {
      'Ramayana Era': [
        { type: 'Temple', description: 'Stone temples with intricate carvings', materials: ['stone', 'marble', 'wood'], features: ['pillars', 'domes', 'carvings'], purpose: 'religious' },
        { type: 'Palace', description: 'Magnificent royal residences', materials: ['stone', 'marble', 'wood', 'gold'], features: ['courtyards', 'pillars', 'fountains'], purpose: 'residential' },
        { type: 'Hut', description: 'Simple dwellings', materials: ['mud', 'thatch', 'bamboo', 'wood'], features: ['thatched roof', 'open windows'], purpose: 'residential' },
        { type: 'Market', description: 'Open-air trading spaces', materials: ['wood', 'fabric', 'bamboo'], features: ['stalls', 'awnings'], purpose: 'commercial' }
      ],
      'default': [
        { type: 'Building', description: 'Period-appropriate structure', materials: ['local materials'], features: [], purpose: 'general' }
      ]
    };
    
    return {
      buildingStyles: buildingStyles[era] || buildingStyles['default'],
      materials: ['stone', 'wood', 'mud', 'thatch', 'bamboo'],
      constructionTechniques: ['mortar and stone', 'wooden joinery', 'mud bricks'],
      decorativeElements: ['carvings', 'paintings', 'textiles'],
      colorPalettes: ['earthy tones', 'natural colors', 'mineral pigments'],
      scale: 'human-scale',
      distinctiveFeatures: ['period architecture', 'traditional design']
    };
  }
  
  private defineClothing(era: string): EnvironmentStyleGuide['clothing'] {
    const eraClothing: Record<string, EnvironmentStyleGuide['clothing']> = {
      'Ramayana Era': {
        socialClasses: {
          royal: {
            description: 'Rich fabrics, elaborate jewelry',
            men: 'Dhoti, upper body cloth, royal jewelry, turbans',
            women: 'Saree with gold borders, heavy jewelry, elaborate hair',
            children: 'Simple dhoti or saree, minimal jewelry',
            materials: ['silk', 'fine cotton', 'brocade', 'gold thread'],
            colors: ['royal blue', 'deep red', 'gold', 'saffron'],
            accessories: ['gold crowns', 'necklaces', 'armlets', 'anklets', 'earrings']
          },
          common: {
            description: 'Simple, functional clothing',
            men: 'Simple dhoti, bare chest or cotton upper cloth',
            women: 'Cotton saree or similar draped garment',
            children: 'Minimal clothing, simple fabrics',
            materials: ['cotton', 'linen', 'wool'],
            colors: ['white', 'off-white', 'earth tones', 'natural dyes'],
            accessories: ['simple jewelry', 'head coverings', 'utility items']
          },
          ascetic: {
            description: 'Simple religious garb',
            men: 'Saffron or white robes, minimal possessions',
            women: 'Simple white or saffron garments',
            children: 'Simple robes',
            materials: ['rough cotton', 'bark cloth'],
            colors: ['saffron', 'white', 'ochre'],
            accessories: ['staff', 'water pot', 'prayer beads']
          }
        },
        materials: ['cotton', 'silk', 'linen', 'wool', 'brocade'],
        colors: ['white', 'saffron', 'red', 'blue', 'gold', 'green', 'earth tones'],
        patterns: ['brocade', 'woven borders', 'simple stripes', 'temple designs'],
        accessories: ['jewelry', 'headpieces', 'shawls', ' waistbands'],
        footwear: ['barefoot', 'wooden sandals', 'leather slippers'],
        headwear: ['turbans', 'crown', 'simple head coverings', 'uncovered'],
        jewelry: ['gold', 'silver', 'precious stones', 'beads', 'flowers'],
        modestyStandards: 'Varied by social class, draped garments',
        weatherAppropriate: 'Light fabrics for hot climate, layers for cool'
      }
    };
    
    return eraClothing[era] || {
      socialClasses: {},
      materials: ['natural fabrics'],
      colors: ['natural dyes'],
      patterns: [],
      accessories: [],
      footwear: [],
      headwear: [],
      jewelry: [],
      modestyStandards: '',
      weatherAppropriate: ''
    };
  }
  
  private defineProps(era: string): EnvironmentStyleGuide['props'] {
    const eraProps: Record<string, EnvironmentStyleGuide['props']> = {
      'Ramayana Era': {
        everyday: ['clay pots', 'wooden bowls', 'baskets', 'mats', 'oil lamps', 'wooden furniture'],
        professional: ['farming tools', 'weaving looms', 'pottery wheels', 'trade goods'],
        luxury: ['golden vessels', 'silver ornaments', 'intricate textiles', 'precious stones'],
        weapons: ['swords', 'bows', 'arrows', 'spears', 'shields', 'maces'],
        transportation: ['horse chariots', 'elephants', 'palanquins', 'walking', 'boats'],
        lighting: ['oil lamps', 'torches', 'candles', 'clay diyas'],
        eating: ['leaf plates', 'wooden bowls', 'metal cups', 'hands'],
        forbidden: ['glasses', 'watches', 'plastic', 'metal utensils', 'synthetic fabrics', 'modern furniture']
      }
    };
    
    return eraProps[era] || {
      everyday: [],
      professional: [],
      luxury: [],
      transportation: [],
      lighting: [],
      eating: [],
      forbidden: []
    };
  }
  
  private defineEnvironment(era: string, location: string): EnvironmentStyleGuide['environment'] {
    return {
      landscape: location,
      vegetation: ['native trees', 'seasonal plants', 'crops'],
      wildlife: ['native animals', 'birds', 'insects'],
      weatherPatterns: ['seasonal variations', 'monsoon', 'dry season'],
      timeOfDayLighting: {
        dawn: 'soft golden light',
        morning: 'bright clear light',
        noon: 'harsh overhead light',
        afternoon: 'warm golden light',
        dusk: 'orange and purple sky',
        night: 'moonlight and firelight'
      },
      atmosphericConditions: ['dust', 'humidity', 'seasonal fog', 'clear skies']
    };
  }
  
  private defineSociety(era: string): EnvironmentStyleGuide['society'] {
    return {
      populationDensity: 'varied',
      diversity: 'diverse',
      occupations: ['farming', 'trading', 'crafts', 'religious', 'royal service'],
      socialBehaviors: ['traditional greetings', 'hierarchical interactions'],
      greetings: ['Namaste', 'pranam', 'verbal greetings'],
      customs: ['religious rituals', 'social hierarchies', 'traditional practices'],
      taboos: ['disrespect to elders', 'breaking caste rules', 'improper dress']
    };
  }
  
  private defineVisualStyle(era: string, visualStyle: string): EnvironmentStyleGuide['visualStyle'] {
    return {
      colorPalette: ['earthy tones', 'natural colors', 'period-appropriate pigments'],
      lightingStyle: 'natural or motivated lighting',
      textureStyle: 'authentic materials',
      atmosphere: 'immersive and historically grounded',
      referenceFilms: this.getReferenceFilms(era),
      artDirection: `${era}-accurate with ${visualStyle} aesthetic`
    };
  }
  
  private getReferenceFilms(era: string): string[] {
    const refs: Record<string, string[]> = {
      'Ramayana Era': ['Ramayana: The Legend of Prince Rama', 'Baahubali', 'Padmaavat'],
      'Ancient Greece': ['300', 'Troy', 'Gladiator'],
      'Medieval': ['Braveheart', 'Kingdom of Heaven', 'The Name of the Rose']
    };
    return refs[era] || [];
  }
}

// Export singleton instance
export const consistencyManager = new ConsistencyManager();
export default consistencyManager;
