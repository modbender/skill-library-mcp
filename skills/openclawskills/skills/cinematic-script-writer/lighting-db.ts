/**
 * Comprehensive Lighting & Visual Style Database
 * Lighting techniques, composition rules, color theory, and genre-specific approaches
 */

// ============================================================================
// LIGHTING TECHNIQUES
// ============================================================================

export const LIGHTING_TECHNIQUES = {
  // Three-Point Lighting
  'three-point': {
    description: 'Key light, fill light, and backlight setup',
    components: {
      key: 'Main light source, creates shadows and defines form',
      fill: 'Reduces shadows created by key, controls contrast',
      back: 'Separates subject from background, creates rim light'
    },
    emotionalImpact: 'Professional, flattering, balanced, standard',
    bestFor: 'Interviews, dialogue, standard coverage, beauty shots',
    difficulty: 'beginner',
    typicalRatio: 'Key:Fill = 2:1 to 4:1'
  },
  
  'key-light-only': {
    description: 'Only key light, no fill',
    emotionalImpact: 'Dramatic, high contrast, mysterious, noir',
    bestFor: 'Drama, noir, horror, dramatic portraits, suspicion',
    difficulty: 'beginner'
  },
  
  'high-key': {
    description: 'Bright, low contrast, minimal shadows',
    emotionalImpact: 'Happy, optimistic, light, comedic, sterile, clinical',
    bestFor: 'Comedy, commercials, medical dramas, sitcoms, musicals',
    difficulty: 'intermediate',
    characteristics: 'Bright overall, soft shadows, white backgrounds common'
  },
  
  'low-key': {
    description: 'Dark, high contrast, dramatic shadows',
    emotionalImpact: 'Dramatic, mysterious, suspenseful, noir, serious',
    bestFor: 'Drama, horror, noir, thriller, serious content',
    difficulty: 'intermediate',
    characteristics: 'Dark overall, strong shadows, selective lighting'
  },
  
  // Natural Lighting
  'golden-hour': {
    description: 'Warm light just after sunrise or before sunset',
    emotionalImpact: 'Romantic, nostalgic, magical, warm, beautiful',
    bestFor: 'Romance, beauty shots, nature, emotional moments, endings',
    difficulty: 'intermediate (time limited)',
    characteristics: 'Warm orange/golden, long shadows, soft, magical',
    colorTemp: '3200K-3500K'
  },
  
  'blue-hour': {
    description: 'Deep blue light just before sunrise or after sunset',
    emotionalImpact: 'Melancholic, mysterious, urban, cool, contemplative',
    bestFor: 'Cityscapes, transition scenes, mystery, urban drama',
    difficulty: 'intermediate (time limited)',
    characteristics: 'Deep blue sky, artificial lights visible, cool tones',
    colorTemp: '6000K-10000K'
  },
  
  'magic-hour': {
    description: 'Both golden and blue hour characteristics',
    emotionalImpact: 'Transitional, ethereal, magical, dreamlike',
    bestFor: 'Fantasy, transitions, dream sequences, magical moments',
    difficulty: 'advanced (very brief window)',
    characteristics: 'Mixed warm and cool tones, unique quality'
  },
  
  'daylight': {
    description: 'Natural sunlight',
    emotionalImpact: 'Realistic, natural, neutral, everyday',
    bestFor: 'Documentary, realism, outdoor scenes, everyday life',
    difficulty: 'beginner',
    characteristics: 'Varies by time of day and weather',
    colorTemp: '5600K (noon), warmer early/late'
  },
  
  'overcast': {
    description: 'Soft diffused natural light from cloudy sky',
    emotionalImpact: 'Neutral, soft, melancholic, subdued, gentle',
    bestFor: 'Portraits, subtle emotions, even lighting, sadness',
    difficulty: 'beginner',
    characteristics: 'Soft shadows, even lighting, slightly cool'
  },
  
  // Dramatic Lighting
  'chiaroscuro': {
    description: 'Extreme contrast between light and dark',
    emotionalImpact: 'Dramatic, intense, artistic, mysterious, classic',
    bestFor: 'Drama, art films, noir, classical portraits, horror',
    difficulty: 'advanced',
    characteristics: 'Deep blacks, bright highlights, Caravaggio style',
    origin: 'Italian Renaissance painting technique'
  },
  
  'silhouette': {
    description: 'Subject completely backlit, appears as dark shape',
    emotionalImpact: 'Mysterious, anonymous, dramatic, threatening, heroic',
    bestFor: 'Reveals, anonymous figures, dramatic entrances, endings',
    difficulty: 'intermediate',
    characteristics: 'Subject completely dark, background bright'
  },
  
  'rim-light': {
    description: 'Light from behind creating outline around subject',
    emotionalImpact: 'Separation, ethereal, heroic, angelic, isolation',
    bestFor: 'Separating subject, heroic shots, dreamlike quality',
    difficulty: 'intermediate',
    characteristics: 'Edge of subject highlighted, front may be dark'
  },
  
  'motivated-lighting': {
    description: 'Light appears to come from visible sources in scene',
    emotionalImpact: 'Realistic, naturalistic, believable',
    bestFor: 'Realism, practical light sources (lamps, windows, fires)',
    difficulty: 'advanced',
    characteristics: 'Lamps, windows, fires, screens motivate the light'
  },
  
  'practical-lighting': {
    description: 'Using actual light sources visible in scene',
    emotionalImpact: 'Realistic, intimate, naturalistic',
    bestFor: 'Realism, night interiors, found footage, documentary',
    difficulty: 'intermediate',
    characteristics: 'Table lamps, street lights, phone screens, candles'
  },
  
  'moonlight': {
    description: 'Simulated moonlight - cool blue, soft',
    emotionalImpact: 'Romantic, mysterious, eerie, magical, quiet',
    bestFor: 'Night scenes, romance, mystery, horror, fantasy',
    difficulty: 'intermediate',
    characteristics: 'Cool blue tone, soft shadows, slightly underexposed',
    colorTemp: '4000K-5000K (simulated)'
  },
  
  'candlelight': {
    description: 'Warm flickering light from candles or fire',
    emotionalImpact: 'Intimate, romantic, historical, dangerous, warm',
    bestFor: 'Period pieces, romance, intimate scenes, danger',
    difficulty: 'intermediate',
    characteristics: 'Very warm (2000K), flickering, soft, orange',
    colorTemp: '1800K-2200K'
  },
  
  'firelight': {
    description: 'Warm flickering light from fire sources',
    emotionalImpact: 'Primitive, dangerous, warm, camping, survival',
    bestFor: 'Campfire scenes, survival, historical, danger',
    difficulty: 'intermediate',
    characteristics: 'Warm orange, dancing shadows, flickering'
  },
  
  'neon': {
    description: 'Colored light from neon or LED signs',
    emotionalImpact: 'Urban, modern, cyberpunk, gritty, cool',
    bestFor: 'City nights, cyberpunk, modern noir, urban drama',
    difficulty: 'intermediate',
    characteristics: 'Saturated colors, high contrast, urban feel'
  },
  
  'fluorescent': {
    description: 'Cool greenish light from fluorescent tubes',
    emotionalImpact: 'Clinical, sterile, institutional, eerie, artificial',
    bestFor: 'Offices, hospitals, institutions, horror, cold environments',
    difficulty: 'beginner',
    characteristics: 'Greenish tint, flat, uniform, slightly flickering',
    colorTemp: '4000K-5000K but with green spike'
  },
  
  'tungsten': {
    description: 'Warm orange light from incandescent bulbs',
    emotionalImpact: 'Cozy, warm, homey, nostalgic, intimate',
    bestFor: 'Homes, warmth, nostalgia, intimacy, period pieces',
    difficulty: 'beginner',
    characteristics: 'Very warm orange, soft, flattering',
    colorTemp: '2700K-3200K'
  },
  
  'single-source': {
    description: 'One light source only',
    emotionalImpact: 'Dramatic, realistic, mysterious, stark',
    bestFor: 'Drama, horror, realism, artistic statements',
    difficulty: 'intermediate',
    characteristics: 'Hard shadows, high contrast, defined direction'
  },
  
  'top-light': {
    description: 'Light from directly above',
    emotionalImpact: 'Oppressive, interrogation, revealing flaws, harsh',
    bestFor: 'Interrogations, horror, revealing true nature',
    difficulty: 'intermediate',
    characteristics: 'Shadows under eyes, harsh, unflattering'
  },
  
  'under-light': {
    description: 'Light from below subject',
    emotionalImpact: 'Horror, scary, unnatural, ghost stories, campfire tales',
    bestFor: 'Horror, telling scary stories, supernatural, nightmares',
    difficulty: 'beginner',
    characteristics: 'Shadows above, unnatural, classic horror look'
  },
  
  'bounce-light': {
    description: 'Light bounced off surfaces for softening',
    emotionalImpact: 'Soft, flattering, natural, gentle',
    bestFor: 'Beauty, interviews, softening harsh light, fill',
    difficulty: 'intermediate',
    characteristics: 'Very soft, diffused, even, flattering'
  },
  
  'book-light': {
    description: 'Light through diffusion then bounced',
    emotionalImpact: 'Ultra soft, dreamy, ethereal, beauty',
    bestFor: 'Beauty shots, dreamy sequences, high-end commercials',
    difficulty: 'advanced',
    characteristics: 'Extremely soft, no shadows, flattering'
  },
  
  'available-light': {
    description: 'Using only existing light in location',
    emotionalImpact: 'Realistic, documentary, raw, authentic',
    bestFor: 'Documentary, realism, run-and-gun, authentic feel',
    difficulty: 'advanced',
    characteristics: 'Variable quality, may be challenging exposure'
  },
  
  'strobe': {
    description: 'Flashing light effects',
    emotionalImpact: 'Chaos, emergency, club scene, disorientation, intensity',
    bestFor: 'Clubs, emergencies, parties, chaotic scenes',
    difficulty: 'intermediate',
    characteristics: 'Sharp flashes, freezing motion, dramatic'
  },
  
  'lens-flare': {
    description: 'Light hitting lens creating artifacts',
    emotionalImpact: 'Dreamy, nostalgic, sci-fi, warm, epic',
    bestFor: 'Sci-fi, flashbacks, nostalgic moments, epic shots',
    difficulty: 'intermediate (often added in post)',
    characteristics: 'Light artifacts, streaks, orbs, glow'
  },
  
  'god-rays': {
    description: 'Visible light beams through atmosphere',
    emotionalImpact: 'Divine, spiritual, magical, atmospheric',
    bestFor: 'Spiritual moments, forests, dusty environments, magic',
    difficulty: 'intermediate (requires atmosphere)',
    characteristics: 'Visible beams of light, ethereal quality'
  },
  
  'volume-light': {
    description: 'Light visible through fog, smoke, dust',
    emotionalImpact: 'Atmospheric, mysterious, cinematic, texture',
    bestFor: 'Atmosphere, concerts, horror, dramatic interiors',
    difficulty: 'intermediate (requires haze/smoke)',
    characteristics: 'Light becomes visible in air, textured beams'
  }
};

// ============================================================================
// COMPOSITION RULES
// ============================================================================

export const COMPOSITION_RULES = {
  'rule-of-thirds': {
    description: 'Divide frame into 3x3 grid, place subjects at intersections',
    purpose: 'Balanced, visually pleasing, professional composition',
    whenToUse: 'Almost all compositions as starting point',
    whenToBreak: 'For symmetry, tension, or specific stylistic choices',
    difficulty: 'beginner'
  },
  
  'golden-ratio': {
    description: 'Compose using golden spiral or 1.618:1 ratio',
    purpose: 'Naturally pleasing, organic, sophisticated composition',
    whenToUse: 'Landscapes, nature, fine art, architectural',
    whenToBreak: 'When symmetry or centered composition is needed',
    difficulty: 'advanced'
  },
  
  'symmetry': {
    description: 'Balanced composition around central axis',
    purpose: 'Formality, perfection, artificiality, unease (when broken)',
    whenToUse: 'Architecture, reflections, formal scenes, Wes Anderson style',
    whenToBreak: 'For dynamism, naturalism, or casual feel',
    difficulty: 'intermediate'
  },
  
  'asymmetry': {
    description: 'Unbalanced, dynamic composition',
    purpose: 'Energy, movement, naturalism, tension',
    whenToUse: 'Action, natural settings, dynamic scenes',
    whenToBreak: 'For calm, formality, or symmetry needs',
    difficulty: 'intermediate'
  },
  
  'leading-lines': {
    description: 'Use natural lines to guide eye to subject',
    purpose: 'Direct attention, depth, visual journey',
    whenToUse: 'Roads, architecture, nature paths, corridors',
    whenToBreak: 'When avoiding guidance or for chaos',
    difficulty: 'beginner'
  },
  
  'frame-within-frame': {
    description: 'Use elements to create frame around subject',
    purpose: 'Focus attention, depth, layers, context',
    whenToUse: 'Doorways, windows, arches, tree branches',
    whenToBreak: 'For openness or simplicity',
    difficulty: 'intermediate'
  },
  
  'depth-layers': {
    description: 'Foreground, middle ground, background composition',
    purpose: 'Three-dimensionality, depth, immersion',
    whenToUse: 'Landscapes, establishing shots, environmental portraits',
    whenToBreak: 'For flat graphic looks or simplicity',
    difficulty: 'intermediate'
  },
  
  'center-composition': {
    description: 'Subject in center of frame',
    purpose: 'Directness, power, confrontation, symmetry',
    whenToUse: 'Portraits, symmetry, direct address, Kubrick style',
    whenToBreak: 'Most other compositions',
    difficulty: 'beginner'
  },
  
  'headroom': {
    description: 'Space above subject\'s head',
    purpose: 'Comfortable framing, breathing room',
    guidelines: 'Eyes at top third for close-ups, more for wide shots',
    whenToBreak: 'For tension (too little) or isolation (too much)',
    difficulty: 'beginner'
  },
  
  'nose-room': {
    description: 'Space in front of subject\'s looking direction',
    purpose: 'Comfortable viewing, shows where subject looks',
    guidelines: 'More space in direction subject faces',
    whenToBreak: 'For confinement (no room) or mystery',
    difficulty: 'beginner'
  },
  
  'negative-space': {
    description: 'Large empty areas in frame',
    purpose: 'Isolation, minimalism, focus on subject, scale',
    whenToUse: 'Minimalist compositions, isolation, scale, advertising',
    whenToBreak: 'For busy scenes or context needs',
    difficulty: 'intermediate'
  },
  
  'fill-frame': {
    description: 'Subject fills entire frame',
    purpose: 'Intimacy, detail, intensity, no distraction',
    whenToUse: 'Close-ups, textures, patterns, abstract',
    whenToBreak: 'For context or environment needs',
    difficulty: 'beginner'
  },
  
  'triangles': {
    description: 'Arrange subjects in triangular composition',
    purpose: 'Stability, hierarchy, dynamic groups',
    whenToUse: 'Group shots, multiple subjects, portraits',
    whenToBreak: 'For linear or random arrangements',
    difficulty: 'intermediate'
  },
  
  'diagonals': {
    description: 'Use diagonal lines for dynamic composition',
    purpose: 'Energy, movement, dynamism, tension',
    whenToUse: 'Action scenes, dynamic portraits, sports',
    whenToBreak: 'For stability or calm',
    difficulty: 'intermediate'
  },
  
  's-curve': {
    description: 'Use S-shaped lines in composition',
    purpose: 'Graceful, flowing, natural, elegant',
    whenToUse: 'Roads, rivers, fashion, elegant subjects',
    whenToBreak: 'For directness or geometric compositions',
    difficulty: 'intermediate'
  },
  
  'patterns-textures': {
    description: 'Use repeating patterns or interesting textures',
    purpose: 'Visual interest, abstraction, background interest',
    whenToUse: 'Backgrounds, abstract shots, architectural',
    whenToBreak: 'When distracting from subject',
    difficulty: 'beginner'
  },
  
  'rule-of-odds': {
    description: 'Odd number of subjects more interesting',
    purpose: 'Visual interest, dynamic grouping',
    whenToUse: 'Group compositions, still life',
    whenToBreak: 'For pairs, symmetry, or specific needs',
    difficulty: 'beginner'
  },
  
  'visual-weight': {
    description: 'Balance heavy and light visual elements',
    purpose: 'Compositional balance',
    guidelines: 'Dark = heavy, bright = light; large = heavy, small = light',
    whenToBreak: 'For intentional imbalance',
    difficulty: 'advanced'
  }
};

// ============================================================================
// COLOR GRADING STYLES
// ============================================================================

export const COLOR_GRADING_STYLES = {
  'teal-orange': {
    description: 'Teal shadows, orange highlights - blockbuster look',
    emotionalImpact: 'Cinematic, modern, commercial, pleasing',
    bestFor: 'Action, blockbusters, commercials, modern films',
    characteristics: 'Skin tones orange, shadows teal/cyan, high contrast',
    examples: ['Transformers', 'Mad Max: Fury Road', 'Most modern blockbusters']
  },
  
  'bleach-bypass': {
    description: 'Silver retention, desaturated high contrast',
    emotionalImpact: 'Gritty, harsh, cold, war-like, intense',
    bestFor: 'War films, gritty dramas, sci-fi, post-apocalyptic',
    characteristics: 'Desaturated, high contrast, metallic feel',
    examples: ['Saving Private Ryan', 'Black Hawk Down', 'Fight Club']
  },
  
  'day-for-night': {
    description: 'Shot in day, graded to look like night',
    emotionalImpact: 'Blue-tinted darkness, classic Hollywood',
    bestFor: 'Classical Hollywood, budget productions',
    characteristics: 'Blue tint, underexposed, moon-like shadows',
    examples: ['Old Hollywood films', 'Budget productions']
  },
  
  'noir': {
    description: 'High contrast black and white',
    emotionalImpact: 'Mystery, danger, classic, stylish',
    bestFor: 'Noir films, mystery, crime, classic styling',
    characteristics: 'Deep blacks, bright whites, strong shadows',
    examples: ['The Maltese Falcon', 'Sin City', 'Schindler\'s List (select scenes)']
  },
  
  'sepia': {
    description: 'Warm brown monochromatic tones',
    emotionalImpact: 'Nostalgic, historical, aged, warm memories',
    bestFor: 'Period pieces, flashbacks, memories, westerns',
    characteristics: 'Brown/gold tones, aged photograph look',
    examples: ['The Godfather', 'O Brother Where Art Thou', 'Flashbacks']
  },
  
  'desaturated': {
    description: 'Reduced color saturation',
    emotionalImpact: 'Gritty, realistic, bleak, serious, documentary',
    bestFor: 'War films, documentaries, serious drama, horror',
    characteristics: 'Muted colors, realistic, less vibrant',
    examples: ['Children of Men', 'The Road', 'Saving Private Ryan']
  },
  
  'high-saturation': {
    description: 'Vivid, enhanced colors',
    emotionalImpact: 'Fantasy, comic book, vibrant, energetic, stylized',
    bestFor: 'Comic book films, animation, fantasy, music videos',
    characteristics: 'Popping colors, vibrant, unrealistic but beautiful',
    examples: ['Speed Racer', 'Sucker Punch', 'Guardians of the Galaxy']
  },
  
  'monochrome': {
    description: 'Single color tint throughout',
    emotionalImpact: 'Stylized, artistic, specific mood',
    bestFor: 'Artistic statements, specific moods, stylized films',
    characteristics: 'Blue monochrome, gold monochrome, etc.',
    examples: ['The Matrix (green)', 'O Brother (sepia)', 'Blade Runner (blue)']
  },
  
  'vintage': {
    description: 'Aged film look with grain, fade, and color shift',
    emotionalImpact: 'Nostalgic, old-timey, memories, period',
    bestFor: 'Period pieces, flashbacks, memories, found footage',
    characteristics: 'Film grain, faded blacks, color shifting, vignette',
    examples: ['The Artist', 'Super 8', 'Grindhouse']
  },
  
  'cross-process': {
    description: 'Chemical cross-processing look',
    emotionalImpact: 'Edgy, alternative, fashion, artistic',
    bestFor: 'Music videos, fashion, artistic films, indie',
    characteristics: 'Shifted colors, high contrast, unpredictable',
    examples: ['Music videos', 'Fashion photography', 'Indie films']
  },
  
  'natural': {
    description: 'True-to-life colors',
    emotionalImpact: 'Realistic, documentary, authentic',
    bestFor: 'Documentaries, realism, nature films',
    characteristics: 'Accurate colors, minimal grading',
    examples: ['Nature documentaries', 'Realist cinema']
  },
  
  'duotone': {
    description: 'Two-color grading (usually shadows and highlights)',
    emotionalImpact: 'Stylized, graphic, artistic',
    bestFor: 'Music videos, commercials, artistic statements',
    characteristics: 'Two dominant colors throughout',
    examples: ['Sin City', 'Music videos', 'Title sequences']
  },
  
  'dayglow': {
    description: 'Neon, electric, saturated colors',
    emotionalImpact: 'Futuristic, cyberpunk, energetic, artificial',
    bestFor: 'Cyberpunk, sci-fi, clubs, future settings',
    characteristics: 'Neon colors, electric blues and pinks, high contrast',
    examples: ['Blade Runner 2049', 'Neon Demon', 'Cyberpunk aesthetics']
  },
  
  'warm': {
    description: 'Enhanced warm tones - oranges, yellows, reds',
    emotionalImpact: 'Cozy, inviting, nostalgic, romantic, sunset',
    bestFor: 'Romance, nostalgia, sunset scenes, warm climates',
    characteristics: 'Yellow/orange cast, warm skin tones',
    examples: ['La La Land', 'Call Me By Your Name', 'Warm climate films']
  },
  
  'cool': {
    description: 'Enhanced cool tones - blues, greens',
    emotionalImpact: 'Cold, clinical, melancholic, winter, isolated',
    bestFor: 'Winter scenes, hospital, isolation, sadness',
    characteristics: 'Blue/green cast, cool skin tones',
    examples: ['The Revenant', 'Winter\'s Bone', 'Cold environment films']
  },
  
  'golden': {
    description: 'Enhanced golden/yellow tones',
    emotionalImpact: 'Wealth, luxury, warmth, nostalgia, magic hour',
    bestFor: 'Luxury, fantasy, golden hour emphasis, period pieces',
    characteristics: 'Gold tint, warm highlights, rich shadows',
    examples: ['The Great Gatsby', 'Gladiator', 'Wes Anderson films']
  },
  
  'matrix-green': {
    description: 'Green-tinted digital world',
    emotionalImpact: 'Digital, artificial, computer-generated, toxic',
    bestFor: 'Sci-fi, computer worlds, toxic environments',
    characteristics: 'Green cast, digital aesthetic',
    examples: ['The Matrix', 'Digital world representations']
  }
};

// Export all lighting and visual data
export const LIGHTING_DB = {
  techniques: LIGHTING_TECHNIQUES,
  composition: COMPOSITION_RULES,
  colorGrading: COLOR_GRADING_STYLES
};

export default LIGHTING_DB;
