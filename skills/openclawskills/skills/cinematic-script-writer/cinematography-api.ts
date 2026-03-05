/**
 * Cinematography API - Unified access to all camera, lighting, and visual techniques
 */

import { CINEMATOGRAPHY_DB } from './cinematography-db';
import { LIGHTING_DB } from './lighting-db';
import { VISUAL_STYLES_DB } from './visual-styles-db';

// ============================================================================
// Camera Techniques API
// ============================================================================

export class CameraTechniquesAPI {
  /**
   * Get all camera angles
   */
  static getAllAngles() {
    return CINEMATOGRAPHY_DB.angles;
  }

  /**
   * Get specific camera angle details
   */
  static getAngle(angleName: string) {
    return CINEMATOGRAPHY_DB.angles[angleName as keyof typeof CINEMATOGRAPHY_DB.angles] || null;
  }

  /**
   * Get angles by emotional impact
   */
  static getAnglesByEmotion(emotion: string) {
    const angles = Object.entries(CINEMATOGRAPHY_DB.angles);
    return angles
      .filter(([_, data]) => 
        data.emotionalImpact.toLowerCase().includes(emotion.toLowerCase())
      )
      .map(([name, data]) => ({ name, ...data }));
  }

  /**
   * Get angles by difficulty level
   */
  static getAnglesByDifficulty(difficulty: 'beginner' | 'intermediate' | 'advanced') {
    const angles = Object.entries(CINEMATOGRAPHY_DB.angles);
    return angles
      .filter(([_, data]) => data.difficulty === difficulty)
      .map(([name, data]) => ({ name, ...data }));
  }

  /**
   * Get all camera movements
   */
  static getAllMovements() {
    return CINEMATOGRAPHY_DB.movements;
  }

  /**
   * Get specific camera movement details
   */
  static getMovement(movementName: string) {
    return CINEMATOGRAPHY_DB.movements[movementName as keyof typeof CINEMATOGRAPHY_DB.movements] || null;
  }

  /**
   * Get movements by emotional impact
   */
  static getMovementsByEmotion(emotion: string) {
    const movements = Object.entries(CINEMATOGRAPHY_DB.movements);
    return movements
      .filter(([_, data]) => 
        data.emotionalImpact.toLowerCase().includes(emotion.toLowerCase())
      )
      .map(([name, data]) => ({ name, ...data }));
  }

  /**
   * Get movements by speed
   */
  static getMovementsBySpeed(speed: string) {
    const movements = Object.entries(CINEMATOGRAPHY_DB.movements);
    return movements
      .filter(([_, data]) => 
        data.speed.toLowerCase().includes(speed.toLowerCase())
      )
      .map(([name, data]) => ({ name, ...data }));
  }

  /**
   * Get all shot types
   */
  static getAllShots() {
    return CINEMATOGRAPHY_DB.shots;
  }

  /**
   * Get specific shot type details
   */
  static getShot(shotName: string) {
    return CINEMATOGRAPHY_DB.shots[shotName as keyof typeof CINEMATOGRAPHY_DB.shots] || null;
  }

  /**
   * Get shots by emotional impact
   */
  static getShotsByEmotion(emotion: string) {
    const shots = Object.entries(CINEMATOGRAPHY_DB.shots);
    return shots
      .filter(([_, data]) => 
        data.emotionalImpact.toLowerCase().includes(emotion.toLowerCase())
      )
      .map(([name, data]) => ({ name, ...data }));
  }

  /**
   * Suggest camera technique based on context
   */
  static suggestTechnique(
    purpose: 'intimacy' | 'power' | 'chaos' | 'reveal' | 'action' | 'emotion' | 'comedy',
    difficulty?: 'beginner' | 'intermediate' | 'advanced'
  ) {
    const suggestions: any = {
      intimacy: {
        angles: ['eye-level', 'close-up', 'over-shoulder'],
        movements: ['dolly-in', 'static', 'slow-pan'],
        shots: ['close-up', 'extreme-close-up', 'medium-close-up']
      },
      power: {
        angles: ['low-angle', 'worm-eye', 'low-angle-shot'],
        movements: ['static', 'slow-dolly', 'crane'],
        shots: ['low-angle-shot', 'wide', 'silhouette']
      },
      chaos: {
        angles: ['dutch-angle', 'handheld', 'whip-pan'],
        movements: ['handheld', 'whip-pan', 'shaky'],
        shots: ['handheld', 'medium', 'reaction-shot']
      },
      reveal: {
        angles: ['high-angle', 'overhead', 'crane-shot'],
        movements: ['crane', 'drone', 'dolly-out', 'zoom-out'],
        shots: ['wide', 'establishing', 'extreme-wide']
      },
      action: {
        angles: ['eye-level', 'low-angle', 'POV'],
        movements: ['handheld', 'steadicam', 'gimbal', 'whip-pan'],
        shots: ['medium', 'wide', 'POV', 'reaction-shot']
      },
      emotion: {
        angles: ['eye-level', 'close-up'],
        movements: ['static', 'slow-dolly-in', 'rack-focus'],
        shots: ['close-up', 'extreme-close-up', 'reaction-shot']
      },
      comedy: {
        angles: ['eye-level', 'slight-low-angle'],
        movements: ['static', 'dolly'],
        shots: ['medium', 'two-shot', 'reaction-shot']
      }
    };

    return suggestions[purpose] || suggestions.emotion;
  }

  /**
   * Get complete camera setup recommendation
   */
  static getRecommendedSetup(
    sceneType: string,
    emotion: string,
    skillLevel: 'beginner' | 'intermediate' | 'advanced' = 'intermediate'
  ) {
    const setups: Record<string, any> = {
      'dialogue-intimate': {
        angle: 'eye-level',
        movement: 'static',
        shot: 'medium-close-up',
        lighting: 'soft-key',
        lens: '85mm'
      },
      'dialogue-confrontation': {
        angle: 'slight-low-angle',
        movement: 'slow-dolly',
        shot: 'medium',
        lighting: 'chiaroscuro',
        lens: '50mm'
      },
      'hero-entrance': {
        angle: 'low-angle',
        movement: 'crane-down',
        shot: 'wide',
        lighting: 'rim-light',
        lens: '24mm'
      },
      'villain-reveal': {
        angle: 'low-angle',
        movement: 'slow-push',
        shot: 'medium',
        lighting: 'low-key',
        lens: '35mm'
      },
      'chase-action': {
        angle: 'eye-level',
        movement: 'steadicam',
        shot: 'medium',
        lighting: 'natural',
        lens: '24-70mm'
      },
      'emotional-moment': {
        angle: 'eye-level',
        movement: 'rack-focus',
        shot: 'close-up',
        lighting: 'soft-key',
        lens: '85mm'
      },
      'horror-suspense': {
        angle: 'dutch-angle',
        movement: 'slow-push',
        shot: 'medium',
        lighting: 'low-key',
        lens: '35mm'
      },
      'comedic-fall': {
        angle: 'high-angle',
        movement: 'static',
        shot: 'wide',
        lighting: 'high-key',
        lens: '35mm'
      }
    };

    return setups[sceneType] || setups['emotional-moment'];
  }
}

// ============================================================================
// Lighting API
// ============================================================================

export class LightingAPI {
  /**
   * Get all lighting techniques
   */
  static getAllTechniques() {
    return LIGHTING_DB.techniques;
  }

  /**
   * Get specific lighting technique
   */
  static getTechnique(techniqueName: string) {
    return LIGHTING_DB.techniques[techniqueName as keyof typeof LIGHTING_DB.techniques] || null;
  }

  /**
   * Get techniques by emotional impact
   */
  static getTechniquesByEmotion(emotion: string) {
    const techniques = Object.entries(LIGHTING_DB.techniques);
    return techniques
      .filter(([_, data]) => 
        data.emotionalImpact.toLowerCase().includes(emotion.toLowerCase())
      )
      .map(([name, data]) => ({ name, ...data }));
  }

  /**
   * Get techniques by difficulty
   */
  static getTechniquesByDifficulty(difficulty: 'beginner' | 'intermediate' | 'advanced') {
    const techniques = Object.entries(LIGHTING_DB.techniques);
    return techniques
      .filter(([_, data]) => data.difficulty === difficulty)
      .map(([name, data]) => ({ name, ...data }));
  }

  /**
   * Suggest lighting for scene type
   */
  static suggestLighting(sceneType: string, mood: string) {
    const suggestions: Record<string, string[]> = {
      'interior-day': ['available-light', 'window-light', 'practical-lighting'],
      'interior-night': ['practical-lighting', 'moonlight', 'tungsten', 'low-key'],
      'exterior-day': ['daylight', 'overcast', 'golden-hour'],
      'exterior-night': ['moonlight', 'street-light', 'neon', 'practical-lighting'],
      'studio': ['three-point', 'high-key', 'book-light'],
      'horror': ['low-key', 'under-light', 'single-source', 'chiaroscuro'],
      'romance': ['soft-key', 'golden-hour', 'candlelight', 'high-key'],
      'drama': ['motivated-lighting', 'chiaroscuro', 'practical-lighting'],
      'comedy': ['high-key', 'three-point', 'soft-key'],
      'noir': ['chiaroscuro', 'venetian-blind', 'low-key'],
      'sci-fi': ['neon', 'practical-lighting', 'motivated-lighting'],
      'fantasy': ['god-rays', 'golden-hour', 'volume-light']
    };

    const key = `${sceneType}-${mood}`;
    return suggestions[key] || suggestions['interior-day'] || ['three-point'];
  }

  /**
   * Get all composition rules
   */
  static getAllCompositionRules() {
    return LIGHTING_DB.composition;
  }

  /**
   * Get specific composition rule
   */
  static getCompositionRule(ruleName: string) {
    return LIGHTING_DB.composition[ruleName as keyof typeof LIGHTING_DB.composition] || null;
  }

  /**
   * Get all color grading styles
   */
  static getAllColorGradingStyles() {
    return LIGHTING_DB.colorGrading;
  }

  /**
   * Get specific color grading style
   */
  static getColorGradingStyle(styleName: string) {
    return LIGHTING_DB.colorGrading[styleName as keyof typeof LIGHTING_DB.colorGrading] || null;
  }

  /**
   * Suggest color grading for genre
   */
  static suggestColorGrading(genre: string) {
    const suggestions: Record<string, string[]> = {
      'action': ['teal-orange', 'high-saturation', 'desaturated'],
      'comedy': ['warm', 'high-saturation', 'natural'],
      'drama': ['natural', 'desaturated', 'warm', 'cool'],
      'horror': ['desaturated', 'cool', 'bleach-bypass'],
      'romance': ['warm', 'golden', 'soft'],
      'sci-fi': ['teal-orange', 'cool', 'matrix-green', 'dayglow'],
      'fantasy': ['golden', 'high-saturation', 'warm'],
      'thriller': ['desaturated', 'cool', 'teal-orange'],
      'documentary': ['natural', 'desaturated', 'vintage'],
      'noir': ['noir', 'desaturated', 'high-contrast'],
      'period': ['sepia', 'vintage', 'warm', 'desaturated'],
      'music-video': ['high-saturation', 'cross-process', 'dayglow']
    };

    return suggestions[genre.toLowerCase()] || ['natural'];
  }
}

// ============================================================================
// Visual Styles API
// ============================================================================

export class VisualStylesAPI {
  /**
   * Get all visual aesthetics
   */
  static getAllAesthetics() {
    return VISUAL_STYLES_DB.aesthetics;
  }

  /**
   * Get specific aesthetic
   */
  static getAesthetic(aestheticName: string) {
    return VISUAL_STYLES_DB.aesthetics[aestheticName as keyof typeof VISUAL_STYLES_DB.aesthetics] || null;
  }

  /**
   * Get aesthetics by type
   */
  static getAestheticsByType(type: 'animation' | 'live-action' | 'artistic' | 'genre') {
    const animation = ['pixar-3d', 'disney-classic', 'anime', 'spider-verse', 'stop-motion', 'claymation', 'cut-out', 'motion-graphics', 'low-poly', 'voxel'];
    const liveAction = ['documentary', 'cinema-verite', 'found-footage', 'mockumentary', 'music-video', 'commercial'];
    const artistic = ['film-noir', 'german-expressionism', 'french-new-wave', 'Dogme-95', 'surrealist'];
    const genre = ['horror', 'sci-fi', 'fantasy', 'western', 'war', 'romance', 'comedy', 'thriller', 'indian-miniature', 'indian-classical-art'];

    const map: Record<string, string[]> = { animation, 'live-action': liveAction, artistic, genre };
    const names = map[type] || [];
    
    return names.map(name => ({
      name,
      ...VISUAL_STYLES_DB.aesthetics[name as keyof typeof VISUAL_STYLES_DB.aesthetics]
    }));
  }

  /**
   * Get all genre cinematography
   */
  static getAllGenreCinematography() {
    return VISUAL_STYLES_DB.genre;
  }

  /**
   * Get genre cinematography
   */
  static getGenreCinematography(genre: string) {
    return VISUAL_STYLES_DB.genre[genre as keyof typeof VISUAL_STYLES_DB.genre] || null;
  }

  /**
   * Get Indian cinematography styles
   */
  static getIndianCinematography(style?: string) {
    if (style) {
      return VISUAL_STYLES_DB.indian[style as keyof typeof VISUAL_STYLES_DB.indian] || null;
    }
    return VISUAL_STYLES_DB.indian;
  }

  /**
   * Suggest visual style for content
   */
  static suggestVisualStyle(
    contentType: string,
    targetAudience: string,
    tone: string
  ) {
    const suggestions: Record<string, any> = {
      'animation-family': {
        primary: 'pixar-3d',
        alternatives: ['disney-classic', 'claymation'],
        lighting: 'three-point',
        colorGrading: 'high-saturation'
      },
      'animation-action': {
        primary: 'spider-verse',
        alternatives: ['anime', 'low-poly'],
        lighting: 'dramatic',
        colorGrading: 'high-saturation'
      },
      'animation-horror': {
        primary: 'stop-motion',
        alternatives: ['claymation', 'cut-out'],
        lighting: 'low-key',
        colorGrading: 'desaturated'
      },
      'live-action-drama': {
        primary: 'documentary',
        alternatives: ['cinema-verite'],
        lighting: 'natural',
        colorGrading: 'natural'
      },
      'live-action-comedy': {
        primary: 'mockumentary',
        alternatives: ['commercial'],
        lighting: 'high-key',
        colorGrading: 'warm'
      },
      'music-promotion': {
        primary: 'music-video',
        alternatives: ['commercial'],
        lighting: 'stylized',
        colorGrading: 'high-saturation'
      },
      'indian-mythological': {
        primary: 'indian-miniature',
        alternatives: ['indian-classical-art', 'fantasy'],
        lighting: 'god-rays',
        colorGrading: 'golden'
      }
    };

    const key = `${contentType}-${targetAudience}-${tone}`;
    return suggestions[key] || suggestions['animation-family'];
  }
}

// ============================================================================
// Complete Cinematography Guide
// ============================================================================

export class CinematographyGuide {
  /**
   * Get complete cinematography package for a scene
   */
  static getScenePackage(
    genre: string,
    mood: string,
    sceneType: string,
    skillLevel: 'beginner' | 'intermediate' | 'advanced' = 'intermediate'
  ) {
    const genreData = VisualStylesAPI.getGenreCinematography(genre);
    const cameraSetup = CameraTechniquesAPI.getRecommendedSetup(sceneType, mood, skillLevel);
    const lighting = LightingAPI.suggestLighting(sceneType, mood);
    const colorGrading = LightingAPI.suggestColorGrading(genre);

    return {
      genreConventions: genreData,
      camera: cameraSetup,
      lighting: lighting,
      colorGrading: colorGrading,
      completeSetup: {
        angle: cameraSetup.angle,
        movement: cameraSetup.movement,
        shot: cameraSetup.shot,
        lighting: lighting[0],
        colorGrading: colorGrading[0],
        lens: cameraSetup.lens
      }
    };
  }

  /**
   * Generate prompt for image generation with cinematography
   */
  static generateImagePrompt(
    subject: string,
    angle: string,
    shot: string,
    lighting: string,
    style: string
  ) {
    const angleData = CameraTechniquesAPI.getAngle(angle);
    const shotData = CameraTechniquesAPI.getShot(shot);
    const lightingData = LightingAPI.getTechnique(lighting);
    const styleData = VisualStylesAPI.getAesthetic(style);

    const parts = [
      `${shot} shot`,
      angleData?.description || angle,
      lightingData?.description || lighting,
      styleData?.characteristics ? Object.values(styleData.characteristics).join(', ') : style,
      subject
    ];

    return parts.join(', ');
  }

  /**
   * Search all techniques
   */
  static search(query: string) {
    const results: any = {
      angles: [],
      movements: [],
      shots: [],
      lighting: [],
      composition: [],
      colorGrading: [],
      aesthetics: []
    };

    const q = query.toLowerCase();

    // Search angles
    Object.entries(CINEMATOGRAPHY_DB.angles).forEach(([name, data]) => {
      if (data.description.toLowerCase().includes(q) || 
          data.emotionalImpact.toLowerCase().includes(q)) {
        results.angles.push({ name, ...data });
      }
    });

    // Search movements
    Object.entries(CINEMATOGRAPHY_DB.movements).forEach(([name, data]) => {
      if (data.description.toLowerCase().includes(q) || 
          data.emotionalImpact.toLowerCase().includes(q)) {
        results.movements.push({ name, ...data });
      }
    });

    // Search shots
    Object.entries(CINEMATOGRAPHY_DB.shots).forEach(([name, data]) => {
      if (data.description.toLowerCase().includes(q) || 
          data.emotionalImpact.toLowerCase().includes(q)) {
        results.shots.push({ name, ...data });
      }
    });

    // Search lighting
    Object.entries(LIGHTING_DB.techniques).forEach(([name, data]) => {
      if (data.description.toLowerCase().includes(q) || 
          data.emotionalImpact.toLowerCase().includes(q)) {
        results.lighting.push({ name, ...data });
      }
    });

    return results;
  }
}

// Export all APIs
export const CinematographyAPI = {
  camera: CameraTechniquesAPI,
  lighting: LightingAPI,
  visual: VisualStylesAPI,
  guide: CinematographyGuide
};

export default CinematographyAPI;
