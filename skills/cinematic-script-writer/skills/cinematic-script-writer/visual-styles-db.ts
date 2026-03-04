/**
 * Visual Styles & Genre-Specific Cinematography Database
 * Aesthetics, film styles, and genre conventions
 */

// ============================================================================
// VISUAL AESTHETICS / STYLES
// ============================================================================

export const VISUAL_AESTHETICS = {
  // Animation Styles
  'pixar-3d': {
    description: 'High-quality 3D animation with appealing character designs',
    characteristics: {
      modeling: 'Stylized but appealing, exaggerated proportions',
      lighting: 'Warm, soft, cinematic three-point lighting',
      texturing: 'Clean, slightly stylized, subsurface skin scattering',
      animation: 'Snappy, exaggerated, squash and stretch principles',
      rendering: 'Physically based rendering, motion blur, depth of field'
    },
    emotionalQuality: 'Warm, family-friendly, emotionally resonant',
    bestFor: 'Family films, comedies, emotional stories',
    examples: ['Toy Story', 'Inside Out', 'Coco']
  },
  
  'disney-classic': {
    description: 'Traditional Disney hand-drawn aesthetic',
    characteristics: {
      style: 'Fluid, expressive, painterly backgrounds',
      line: 'Clean outlines, varying line weight',
      color: 'Vibrant, warm, rich saturation',
      animation: 'Fluid, graceful, classical principles'
    },
    emotionalQuality: 'Magical, nostalgic, enchanting, romantic',
    bestFor: 'Fairy tales, musicals, period pieces',
    examples: ['The Lion King', 'Beauty and the Beast', 'Aladdin']
  },
  
  'anime': {
    description: 'Japanese animation style',
    characteristics: {
      style: 'Cel-shaded or limited animation, detailed backgrounds',
      eyes: 'Large, expressive eyes with detailed highlights',
      hair: 'Stylized, gravity-defying, vibrant colors',
      effects: 'Speed lines, impact frames, limited animation techniques',
      shading: 'Hard shadows, limited color palette per scene'
    },
    emotionalQuality: 'Expressive, energetic, emotional, stylized',
    bestFor: 'Action, fantasy, romance, slice of life',
    examples: ['Studio Ghibli', 'Your Name', 'Attack on Titan']
  },
  
  'spider-verse': {
    description: 'Comic book come to life - mixed frame rates and styles',
    characteristics: {
      frameRate: 'On twos (12fps) for characters, 24fps for camera',
      style: 'Comic book dots, line work, hand-drawn elements',
      errors: 'Intentional misregistration, smears, multiples',
      rendering: '3D base with 2D styling, halftone patterns'
    },
    emotionalQuality: 'Energetic, youthful, comic-book, fresh',
    bestFor: 'Comic adaptations, energetic action, youth stories',
    examples: ['Spider-Man: Into the Spider-Verse', 'Arcane']
  },
  
  'stop-motion': {
    description: 'Physical puppets animated frame by frame',
    characteristics: {
      texture: 'Visible fingerprints, fabric texture, real materials',
      movement: 'Slight jitter, stepped motion, charming imperfection',
      lighting: 'Practical, atmospheric, dramatic shadows',
      scale: 'Miniature sets, macro photography aesthetic'
    },
    emotionalQuality: 'Handcrafted, charming, slightly eerie, tangible',
    bestFor: 'Dark fairy tales, quirky comedies, Halloween themes',
    examples: ['Coraline', 'Kubo and the Two Strings', 'Wallace and Gromit']
  },
  
  'claymation': {
    description: 'Clay figures animated',
    characteristics: {
      material: 'Visible clay texture, fingerprints, malleable forms',
      style: 'Chunky, rounded forms, squash and stretch in clay',
      lighting: 'Dramatic, sculptural lighting to show form',
      animation: 'Distinctive stepped movement, morphing capabilities'
    },
    emotionalQuality: 'Playful, childlike, tactile, humorous',
    bestFor: 'Comedy, children\'s content, quirky stories',
    examples: ['Chicken Run', 'Shaun the Sheep', 'Rudolph']
  },
  
  'cut-out': {
    description: 'Flat illustrated elements animated like paper cut-outs',
    characteristics: {
      style: 'Flat, 2D illustrated elements, paper aesthetic',
      joints: 'Visible articulation points, hinged limbs',
      depth: 'Limited, shadowbox-style layering',
      texture: 'Paper grain, craft materials aesthetic'
    },
    emotionalQuality: 'Handmade, storybook, educational, charming',
    bestFor: 'Children\'s educational, South Park style humor',
    examples: ['South Park', 'Monty Python animations', 'Blue\'s Clues']
  },
  
  'motion-graphics': {
    description: 'Graphic design in motion',
    characteristics: {
      style: 'Clean vectors, typography, geometric shapes',
      animation: 'Smooth easing, precise timing, graph editor curves',
      rendering: 'Crisp, clean, often flat colors or gradients'
    },
    emotionalQuality: 'Modern, professional, tech-forward, clean',
    bestFor: 'Explainers, tech, corporate, title sequences',
    examples: ['Tech explainers', 'Title sequences', 'UI animations']
  },
  
  'low-poly': {
    description: '3D with minimal polygon count',
    characteristics: {
      modeling: 'Geometric, faceted surfaces, visible edges',
      shading: 'Flat shading or simple gradients',
      style: 'Minimalist, retro-3D, video game aesthetic'
    },
    emotionalQuality: 'Minimalist, retro, indie-game, artistic',
    bestFor: 'Indie games, stylized animation, abstract concepts',
    examples: ['Indie game aesthetics', 'Kurzgesagt', 'Abstract explainers']
  },
  
  'voxel': {
    description: '3D pixel art - blocky cubic world',
    characteristics: {
      style: 'Blocky, cubic, Minecraft-like aesthetic',
      detail: 'Chunky, simplified forms, pixelated textures',
      world: 'Built from cubes, destructible aesthetic'
    },
    emotionalQuality: 'Retro-gaming, playful, blocky, digital',
    bestFor: 'Gaming content, retro aesthetics, playful subjects',
    examples: ['Minecraft', 'Crossy Road', 'Voxel art']
  },
  
  // Realistic/Live-Action Styles
  'documentary': {
    description: 'Realistic, observational cinematography',
    characteristics: {
      camera: 'Handheld or shoulder mount, natural movement',
      lighting: 'Available light, practical sources, naturalistic',
      framing: 'Slightly loose, often rule of thirds, reactive',
      color: 'Natural, minimal grading, sometimes flat for grading'
    },
    emotionalQuality: 'Authentic, raw, observational, real',
    bestFor: 'Documentaries, realism, found footage, true stories',
    examples: ['Planet Earth', 'The Office', 'Paranormal Activity']
  },
  
  'cinema-verite': {
    description: 'Fly-on-wall documentary style',
    characteristics: {
      camera: 'Handheld, often shaky, reactive to action',
      presence: 'Camera visible, acknowledged, intrusive',
      editing: 'Long takes, jump cuts, natural pacing',
      sound: 'Natural sound, often poor quality, location audio'
    },
    emotionalQuality: 'Raw, immediate, unfiltered, intrusive',
    bestFor: 'Hard-hitting docs, social realism, political films',
    examples: ['Grey Gardens', 'Hoop Dreams', 'The War Room']
  },
  
  'found-footage': {
    description: 'Appears to be discovered/recovered footage',
    characteristics: {
      source: 'Security cams, phones, consumer cameras',
      quality: 'Poor, degraded, compression artifacts',
      framing: 'Amateur, often bad composition, accidental',
      continuity: 'Timestamp overlays, camera UI visible'
    },
    emotionalQuality: 'Real, scary, authentic, voyeuristic',
    bestFor: 'Horror, supernatural, conspiracy, realism',
    examples: ['The Blair Witch Project', 'Paranormal Activity', 'Cloverfield']
  },
  
  'mockumentary': {
    description: 'Fictional content shot as documentary',
    characteristics: {
      interviews: 'Characters talk to camera, documentary style',
      camera: 'Handheld, multiple cameras, documentary crew visible',
      style: 'Realistic lighting, natural locations, improvised feel'
    },
    emotionalQuality: 'Comedic, satirical, realistic but absurd',
    bestFor: 'Comedy, satire, workplace shows',
    examples: ['The Office', 'Parks and Recreation', 'What We Do in the Shadows']
  },
  
  'music-video': {
    description: 'High-energy, stylized visual storytelling',
    characteristics: {
      pacing: 'Matches music beat, quick cuts, rhythmic editing',
      style: 'Bold colors, stylized grading, artistic compositions',
      effects: 'Heavy visual effects, transitions, speed ramps',
      performance: 'Artist focus, lip-sync, choreography emphasis'
    },
    emotionalQuality: 'Energetic, stylish, artistic, expressive',
    bestFor: 'Music videos, high-energy content, fashion',
    examples: ['Beyoncé visuals', 'OK Go', 'Tyler the Creator videos']
  },
  
  'commercial': {
    description: 'Polished, product-focused, aspirational',
    characteristics: {
      lighting: 'High-key, flawless, beauty lighting',
      camera: 'Smooth motion, perfect compositions, slow motion',
      color: 'Vibrant, saturated, product colors pop',
      pacing: 'Fast-paced, punchy, sells lifestyle'
    },
    emotionalQuality: 'Aspirational, polished, desirable, perfect',
    bestFor: 'Advertisements, product showcases, lifestyle',
    examples: ['Apple commercials', 'Luxury car ads', 'Fashion campaigns']
  },
  
  // Artistic Styles
  'film-noir': {
    description: 'Classic Hollywood crime style',
    characteristics: {
      lighting: 'High contrast, venetian blind shadows, harsh shadows',
      camera: 'Low angles, dutch angles, dramatic compositions',
      setting: 'Night, rain, urban, shadows',
      color: 'Black and white, or heavy desaturation'
    },
    emotionalQuality: 'Mysterious, dangerous, seductive, cynical',
    bestFor: 'Crime, mystery, neo-noir, detective stories',
    examples: ['The Maltese Falcon', 'Sin City', 'Blade Runner']
  },
  
  'german-expressionism': {
    description: 'Distorted, psychological, angular',
    characteristics: {
      sets: 'Angular, distorted, painted shadows, artificial',
      lighting: 'Harsh contrasts, painted light, stylized shadows',
      acting: 'Exaggerated, theatrical, expressive',
      camera: 'Dutch angles, forced perspective, dramatic compositions'
    },
    emotionalQuality: 'Disturbed, psychological, nightmarish, stylized',
    bestFor: 'Horror, psychological thrillers, art films',
    examples: ['The Cabinet of Dr. Caligari', 'Nosferatu', 'The Crow']
  },
  
  'french-new-wave': {
    description: 'Breathless, jump cuts, location shooting',
    characteristics: {
      camera: 'Handheld, natural light, location shooting',
      editing: 'Jump cuts, direct address, breaking fourth wall',
      style: 'Naturalistic, spontaneous, self-aware'
    },
    emotionalQuality: 'Intellectual, spontaneous, cool, rebellious',
    bestFor: 'Art house, indie films, relationship dramas',
    examples: ['Breathless', 'Jules and Jim', '400 Blows']
  },
  
  ' Dogme-95': {
    description: 'Strict naturalism rules, anti-Hollywood',
    characteristics: {
      rules: 'Location only, hand-held only, no props, no lighting',
      style: 'Raw, unpolished, realistic, present tense',
      sound: 'Direct sound only, no music added'
    },
    emotionalQuality: 'Raw, honest, immediate, unpolished',
    bestFor: 'Realism, social issues, intense drama',
    examples: ['The Celebration', 'The Idiots', 'Italian for Beginners']
  },
  
  'surrealist': {
    description: 'Dream logic, irrational imagery, symbolic',
    characteristics: {
      imagery: 'Bizarre juxtapositions, dreamlike scenarios',
      narrative: 'Non-linear, symbolic, unconscious themes',
      style: 'Unreal, fantastical, unsettling'
    },
    emotionalQuality: 'Dreamlike, disturbing, symbolic, irrational',
    bestFor: 'Dream sequences, psychological, art films',
    examples: ['Un Chien Andalou', 'Eraserhead', 'The Holy Mountain']
  },
  
  // Genre Styles
  'horror': {
    description: 'Designed to create fear and unease',
    characteristics: {
      lighting: 'Low-key, shadows, underlight, practical sources',
      camera: 'Slow pushes, sudden movements, POV shots',
      color: 'Desaturated, teal/orange, green for sickness',
      sound: 'Uneven soundscape, sudden silences, low frequencies'
    },
    emotionalQuality: 'Scary, tense, unsettling, suspenseful',
    bestFor: 'Horror, thrillers, suspense',
    examples: ['The Conjuring', 'Hereditary', 'Get Out']
  },
  
  'sci-fi': {
    description: 'Futuristic, technological, otherworldly',
    characteristics: {
      lighting: 'Neon, practical lights, sterile or moody',
      production: 'Clean lines, futuristic design, VFX heavy',
      color: 'Teal/orange, blue for sci-fi, or neon colors',
      camera: 'Smooth, precise, sometimes handheld for realism'
    },
    emotionalQuality: 'Futuristic, awe-inspiring, isolating, technological',
    bestFor: 'Science fiction, space, future settings, technology',
    examples: ['Blade Runner 2049', 'Interstellar', 'The Matrix']
  },
  
  'fantasy': {
    description: 'Magical, epic, otherworldly',
    characteristics: {
      lighting: 'Magical sources, god rays, ethereal glow',
      production: 'Elaborate sets, costumes, VFX creatures',
      color: 'Golden, vibrant, or desaturated depending on tone',
      scale: 'Epic wide shots, detailed world-building'
    },
    emotionalQuality: 'Magical, epic, wonderous, heroic',
    bestFor: 'Fantasy, fairy tales, epic adventures, magic',
    examples: ['Lord of the Rings', 'Pan\'s Labyrinth', 'The Witcher']
  },
  
  'western': {
    description: 'Vast landscapes, morally complex',
    characteristics: {
      framing: 'Wide landscapes, lone figures, horizon lines',
      color: 'Warm, earthy tones, golden hour, dusty',
      camera: 'Stable, epic, sweeping, or tense close-ups',
      lighting: 'Natural, harsh sunlight, dramatic shadows'
    },
    emotionalQuality: 'Epic, lonely, morally complex, rugged',
    bestFor: 'Westerns, desert settings, lone hero stories',
    examples: ['The Good, Bad and Ugly', 'Django Unchained', 'True Grit']
  },
  
  'war': {
    description: 'Chaotic, gritty, realistic',
    characteristics: {
      camera: 'Shaky cam, documentary style, chaotic movement',
      color: 'Desaturated, bleach bypass, muted',
      sound: 'Distorted, loud, realistic combat audio',
      style: 'Gritty, dirty, handheld, immersive'
    },
    emotionalQuality: 'Intense, chaotic, realistic, traumatic',
    bestFor: 'War films, action, survival, combat',
    examples: ['Saving Private Ryan', '1917', 'Black Hawk Down']
  },
  
  'romance': {
    description: 'Soft, warm, intimate',
    characteristics: {
      lighting: 'Soft, flattering, golden hour, practical sources',
      camera: 'Smooth, close-ups, two-shots, intimate framing',
      color: 'Warm tones, golden, soft pastels, pink hues',
      lens: 'Shallow depth of field, dreamy quality'
    },
    emotionalQuality: 'Romantic, warm, intimate, emotional',
    bestFor: 'Romance, romantic comedies, emotional dramas',
    examples: ['The Notebook', 'Before Sunrise', 'La La Land']
  },
  
  'comedy': {
    description: 'Bright, clear, framed for performance',
    characteristics: {
      lighting: 'High-key, bright, even, no shadows on faces',
      camera: 'Stable, three-camera style, wide shots for physical comedy',
      timing: 'Precise framing for punchlines, reaction shots',
      color: 'Bright, saturated, cheerful'
    },
    emotionalQuality: 'Light, funny, clear, entertaining',
    bestFor: 'Comedy, sitcoms, light entertainment',
    examples: ['Bridesmaids', 'The Grand Budapest Hotel', 'Modern Family']
  },
  
  'thriller': {
    description: 'Tense, controlled, suspenseful',
    characteristics: {
      lighting: 'Low-key, shadows, selective illumination',
      camera: 'Controlled movement, slow pushes, dutch angles',
      color: 'Cool tones, desaturated, occasional color pop',
      editing: 'Precise pacing, controlled rhythm'
    },
    emotionalQuality: 'Tense, suspenseful, controlled, mysterious',
    bestFor: 'Thrillers, mysteries, suspense, crime',
    examples: ['Se7en', 'Zodiac', 'Prisoners']
  },
  
  'indian-miniature': {
    description: 'Inspired by Indian miniature painting traditions',
    characteristics: {
      color: 'Vibrant jewel tones, rich reds, golds, blues, greens',
      composition: 'Flat perspective, decorative borders, pattern-filled',
      detail: 'Intricate patterns, floral motifs, geometric designs',
      figure: 'Stylized figures, elegant poses, traditional attire'
    },
    emotionalQuality: 'Ornate, cultural, historical, decorative',
    bestFor: 'Indian historical, mythological, cultural stories',
    examples: ['Mughal-e-Azam styling', 'Indian art-inspired animation']
  },
  
  'indian-classical-art': {
    description: 'Based on classical Indian art traditions',
    characteristics: {
      style: 'Ajanta cave painting style, or Raja Ravi Varma realism',
      color: 'Earthy tones or vibrant period colors',
      figure: 'Idealized forms, traditional Indian features',
      ornamentation: 'Traditional jewelry, clothing details'
    },
    emotionalQuality: 'Cultural, classical, historical, reverent',
    bestFor: 'Indian mythology, historical epics, cultural content',
    examples: ['Epic Indian tales', 'Mythological retellings']
  }
};

// ============================================================================
// GENRE-SPECIFIC CINEMATOGRAPHY
// ============================================================================

export const GENRE_CINEMATOGRAPHY = {
  'action': {
    cameraMovement: ['handheld', 'gimbal', 'steadicam', 'whip-pan'],
    shotTypes: ['wide', 'medium', 'close-up', 'POV'],
    angles: ['eye-level', 'low-angle', 'dynamic'],
    editing: 'Fast-paced, quick cuts, 2-3 seconds per shot',
    lighting: 'High contrast, practical lights, natural',
    colorGrading: 'Teal-orange, high saturation, contrast',
    keyElements: ['Clear geography', 'Impact frames', 'Motion blur', 'Dynamic compositions']
  },
  
  'comedy': {
    cameraMovement: ['static', 'minimal', 'dolly'],
    shotTypes: ['medium', 'two-shot', 'medium-close-up', 'reaction-shot'],
    angles: ['eye-level', 'slight-low'],
    editing: 'Precise timing, hold on reactions, rhythmic',
    lighting: 'High-key, bright, even, flattering',
    colorGrading: 'Warm, saturated, cheerful',
    keyElements: ['Wide shots for physical comedy', 'Reaction shots', 'Clean framing', 'No dutch angles (unless absurd comedy)']
  },
  
  'drama': {
    cameraMovement: ['subtle', 'slow-dolly', 'pan', 'tilt'],
    shotTypes: ['close-up', 'medium-close-up', 'two-shot'],
    angles: ['eye-level', 'slight variations'],
    editing: 'Paced with performance, longer takes',
    lighting: 'Motivated, dramatic shadows, three-point',
    colorGrading: 'Natural to slightly stylized, emotional',
    keyElements: ['Intimate framing', 'Emotional close-ups', 'Naturalistic', 'Performance-focused']
  },
  
  'horror': {
    cameraMovement: ['slow-push', 'handheld', 'static-tension'],
    shotTypes: ['close-up', 'POV', 'wide-empty', 'insert'],
    angles: ['dutch', 'low', 'high', 'unusual'],
    editing: 'Variable - slow burn or quick cuts for scares',
    lighting: 'Low-key, shadows, practical sources, underlight',
    colorGrading: 'Desaturated, cool tones, occasional warmth',
    keyElements: ['Negative space', 'Shadows', 'POV shots', 'Sound design crucial', 'Reveal timing']
  },
  
  'romance': {
    cameraMovement: ['smooth', 'slow-dolly', 'crane'],
    shotTypes: ['close-up', 'two-shot', 'medium'],
    angles: ['eye-level', 'soft-low'],
    editing: 'Leisurely, flowing, emotional beats',
    lighting: 'Soft, flattering, golden hour, practical',
    colorGrading: 'Warm, golden, soft, pastel',
    keyElements: ['Shallow depth of field', 'Two-shots', 'Golden hour', 'Intimate framing']
  },
  
  'sci-fi': {
    cameraMovement: ['smooth', 'crane', 'steadicam', 'precise'],
    shotTypes: ['wide', 'establishing', 'close-up-tech'],
    angles: ['eye-level', 'dramatic-low', 'high-tech'],
    editing: 'Clean, modern, sometimes fast for action',
    lighting: 'Practical-motivated, neon, sterile, dramatic',
    colorGrading: 'Teal-orange, blue sci-fi, neon accents',
    keyElements: ['World-building shots', 'Technology focus', 'Clean lines', 'VFX integration']
  },
  
  'fantasy': {
    cameraMovement: ['sweeping', 'crane', 'smooth', 'majestic'],
    shotTypes: ['extreme-wide', 'wide', 'epic-close-up'],
    angles: ['dramatic', 'heroic-low', 'overview'],
    editing: 'Epic pacing, spectacle moments',
    lighting: 'Dramatic, magical sources, god-rays',
    colorGrading: 'Golden epic, or stylized palette, vibrant',
    keyElements: ['Scale', 'Magic visualization', 'Creature shots', 'World-building']
  },
  
  'thriller': {
    cameraMovement: ['controlled', 'slow-push', 'pan', 'handheld-tension'],
    shotTypes: ['close-up', 'over-shoulder', 'insert'],
    angles: ['dutch', 'slanted', 'dramatic'],
    editing: 'Controlled rhythm, tension-building',
    lighting: 'Low-key, shadows, selective lighting',
    colorGrading: 'Cool, desaturated, high contrast',
    keyElements: ['Tension in framing', 'Shadows', 'Information reveals', 'Controlled pace']
  },
  
  'documentary': {
    cameraMovement: ['handheld', 'shoulder-mount', 'observational'],
    shotTypes: ['medium', 'close-up', 'wide-context'],
    angles: ['eye-level', 'natural'],
    editing: 'Observational, reactive, natural pace',
    lighting: 'Available light, practical, natural',
    colorGrading: 'Natural, minimal, or stylized for effect',
    keyElements: ['Real moments', 'Interview framing', 'B-roll context', 'Authentic feel']
  },
  
  'musical': {
    cameraMovement: ['flowing', 'crane', 'steadicam', 'choreographed'],
    shotTypes: ['wide', 'full', 'medium', 'reaction'],
    angles: ['dramatic', 'theatrical', 'eye-level'],
    editing: 'Rhythmic with music, longer takes for dance',
    lighting: 'Theatrical, dramatic, colorful',
    colorGrading: 'Saturated, vibrant, stylized',
    keyElements: ['Full body for dance', 'Energy', 'Color', 'Camera choreography']
  },
  
  'western': {
    cameraMovement: ['stable', 'slow', 'epic-pans'],
    shotTypes: ['extreme-wide', 'wide', 'close-up-confrontation'],
    angles: ['heroic-low', 'eye-level', 'landscape'],
    editing: 'Deliberate, standoffs held, landscape appreciation',
    lighting: 'Natural, harsh sun, dramatic shadows, golden hour',
    colorGrading: 'Warm, earthy, golden, sometimes desaturated',
    keyElements: ['Landscape', 'Standoff framing', 'Lone figure', 'Horizon lines']
  },
  
  'period-drama': {
    cameraMovement: ['refined', 'smooth', 'elegant'],
    shotTypes: ['wide-detail', 'medium', 'intimate-close-up'],
    angles: ['eye-level', 'slight variations'],
    editing: 'Leisurely, appreciative of production design',
    lighting: 'Naturalistic or candle/practical motivated',
    colorGrading: 'Period-appropriate, often desaturated or warm',
    keyElements: ['Production design', 'Costume detail', 'Authentic lighting', 'Period accuracy']
  },
  
  'noir': {
    cameraMovement: ['dramatic', 'shadow-revealing'],
    shotTypes: ['close-up', 'shadow-shot', 'venetian-blind'],
    angles: ['dramatic-low', 'dutch', 'high-contrast'],
    editing: 'Sharp, rhythmic, tension-building',
    lighting: 'High contrast, venetian blind shadows, harsh',
    colorGrading: 'Black and white or heavily desaturated',
    keyElements: ['Shadows', 'Light patterns', 'Cigarette smoke', 'Rain', 'Urban night']
  },
  
  'animation-comedy': {
    cameraMovement: ['snappy', 'energetic', 'cartoon-physics'],
    shotTypes: ['wide', 'medium', 'extreme-close-up'],
    angles: ['exaggerated', 'dynamic', 'cartoon'],
    editing: 'Fast, rhythmic, sound-driven',
    lighting: 'Bright, colorful, stylized shadows',
    colorGrading: 'Saturated, vibrant, appealing',
    keyElements: ['Exaggeration', 'Squash and stretch', 'Appealing poses', 'Clear silhouettes', 'Expressive faces']
  }
};

// ============================================================================
// INDIAN CINEMATOGRAPHY STYLES
// ============================================================================

export const INDIAN_CINEMATOGRAPHY = {
  'bollywood-masala': {
    songs: 'Vibrant colors, multiple locations, costume changes, large groups',
    drama: 'Emotional close-ups, dramatic lighting, saturated colors',
    action: 'Stylized, slow-motion, heroic angles',
    family: 'Warm lighting, traditional settings, rich colors',
    characteristics: 'High saturation, vibrant costumes, dramatic compositions'
  },
  
  'bollywood-contemporary': {
    style: 'Modern, urban, influenced by Western cinema',
    lighting: 'Naturalistic to stylized depending on genre',
    color: 'Variable - natural for drama, stylized for genre films',
    characteristics: 'Polished, professional, genre-appropriate'
  },
  
  'art-house-indian': {
    style: 'Realistic, naturalistic, socially conscious',
    lighting: 'Available light, natural, documentary feel',
    camera: 'Handheld, observational, long takes',
    color: 'Natural, minimal grading',
    characteristics: 'Authentic locations, non-actors, realism'
  },
  
  'mythological-epic': {
    style: 'Grand, colorful, devotional',
    lighting: 'Dramatic, golden, divine light rays',
    camera: 'Sweeping, majestic, reverential angles',
    color: 'Vibrant, rich, gold accents',
    characteristics: 'Scale, divinity, traditional aesthetics, grandeur'
  },
  
  'period-historical-indian': {
    style: 'Authentic to period, rich production design',
    lighting: 'Natural or candle-lit, period-appropriate',
    camera: 'Smooth, appreciative of detail',
    color: 'Period-graded, often warm or sepia',
    characteristics: 'Authenticity, detail, historical accuracy'
  }
};

// Export all visual styles data
export const VISUAL_STYLES_DB = {
  aesthetics: VISUAL_AESTHETICS,
  genre: GENRE_CINEMATOGRAPHY,
  indian: INDIAN_CINEMATOGRAPHY
};

export default VISUAL_STYLES_DB;
