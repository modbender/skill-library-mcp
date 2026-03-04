/**
 * Comprehensive Cinematography Database
 * Camera techniques, lighting, composition, visual styles, and genre-specific approaches
 */

// ============================================================================
// CAMERA ANGLES - Expanded
// ============================================================================

export const CAMERA_ANGLES = {
  // Standard Angles
  'eye-level': {
    description: 'Camera at subject\'s eye level - neutral, natural perspective',
    emotionalImpact: 'Creates connection, equality, neutrality, immersion',
    bestFor: 'Dialogue scenes, emotional moments, establishing character presence, POV sequences',
    commonUses: ['Conversations', 'Character introductions', 'Intimate moments'],
    difficulty: 'beginner',
    lensRecommendation: '35mm-50mm for natural look'
  },
  
  'low-angle': {
    description: 'Camera below subject looking up - subject dominates frame',
    emotionalImpact: 'Power, dominance, heroism, intimidation, authority, superiority',
    bestFor: 'Revealing villains, heroic moments, making subject imposing, establishing hierarchy',
    commonUses: ['Hero entrances', 'Villain reveals', 'Monument shots', 'Power dynamics'],
    difficulty: 'beginner',
    lensRecommendation: 'Wide angle 16-24mm for dramatic distortion'
  },
  
  'high-angle': {
    description: 'Camera above subject looking down - subject appears smaller',
    emotionalImpact: 'Vulnerability, weakness, inferiority, submission, overview, insignificance',
    bestFor: 'Showing subject small/helpless, establishing scale, surveillance feel',
    commonUses: ['Character defeat', 'Establishing geography', 'God\'s eye view', 'Vulnerability'],
    difficulty: 'beginner',
    lensRecommendation: 'Standard 35-50mm'
  },
  
  'bird-eye': {
    description: 'Extreme high angle directly above subject',
    emotionalImpact: 'Subject is insignificant, lost, or part of larger system, detachment',
    bestFor: 'Epic scale, isolation, maze-like situations, patterns, strategic overview',
    commonUses: ['Battlefield overview', 'Character lost in city', 'Pattern recognition', 'Chess game'],
    difficulty: 'intermediate',
    lensRecommendation: 'Wide angle or aerial lens'
  },
  
  'worm-eye': {
    description: 'Extreme low angle from ground level looking up',
    emotionalImpact: 'Overwhelming presence, massive scale, awe, grandeur, oppression',
    bestFor: 'Monuments, giants, towering structures, dramatic architecture, imposing figures',
    commonUses: ['Skyscrapers', 'Gods/deities', 'Tall characters', 'Dramatic architecture'],
    difficulty: 'intermediate',
    lensRecommendation: 'Ultra-wide 10-16mm'
  },
  
  // Dramatic Angles
  'dutch-angle': {
    description: 'Tilted camera, horizon not level (also called canted angle)',
    emotionalImpact: 'Unease, disorientation, tension, psychological distress, unnatural state',
    bestFor: 'Chaos, dreams, insanity, danger moments, intoxication, supernatural',
    commonUses: ['Nightmares', 'Villain lairs', 'Action sequences', 'Drug sequences', 'Horror'],
    difficulty: 'intermediate',
    lensRecommendation: 'Any, but wide angles enhance the effect'
  },
  
  'overhead': {
    description: 'Directly above subject but not as extreme as bird-eye',
    emotionalImpact: 'Omniscience, detachment, pattern recognition, surveillance',
    bestFor: 'Table scenes, bed scenes, action sequences, rituals, patterns',
    commonUses: ['Dining scenes', 'Fight choreography', 'Board games', 'Surgery scenes'],
    difficulty: 'intermediate',
    lensRecommendation: 'Wide angle 16-24mm'
  },
  
  'shoulder-level': {
    description: 'Camera at subject\'s shoulder height',
    emotionalImpact: 'Intimate but not invasive, casual observation, documentary feel',
    bestFor: 'Following shots, casual conversations, documentary style, walking scenes',
    commonUses: ['Walking conversations', 'Following characters', 'Documentary'],
    difficulty: 'beginner',
    lensRecommendation: '35-50mm'
  },
  
  'knee-level': {
    description: 'Camera at knee height',
    emotionalImpact: 'Child\'s perspective, unusual viewpoint, grounded feeling',
    bestFor: 'Child POV, pet POV, unusual perspectives, emphasizing height',
    commonUses: ['Child protagonist', 'Pet views', 'Tall character introduction'],
    difficulty: 'intermediate',
    lensRecommendation: 'Wide angle 24-35mm'
  },
  
  'ground-level': {
    description: 'Camera at ground level',
    emotionalImpact: 'Vulnerability, connection to earth, small creatures\' perspective',
    bestFor: 'Small animals, insects, low objects, dramatic entrances',
    commonUses: ['Insect documentaries', 'Child playing', 'Dramatic entrances'],
    difficulty: 'intermediate',
    lensRecommendation: 'Macro or wide angle'
  },
  
  // Special Angles
  'pov': {
    description: 'Character\'s point of view - what the character sees',
    emotionalImpact: 'Immersion, subjectivity, identification with character',
    bestFor: 'First-person sequences, horror, action, building tension',
    commonUses: ['First-person sequences', 'Horror reveals', 'Shooting scenes', 'Exploration'],
    difficulty: 'intermediate',
    lensRecommendation: '50mm to match human vision'
  },
  
  'over-shoulder': {
    description: 'Looking past one subject\'s shoulder at another',
    emotionalImpact: 'Conversation intimacy, spatial relationship, connection',
    bestFor: 'Dialogue scenes, establishing spatial relationships, conversations',
    commonUses: ['Two-person conversations', 'Interviews', 'Confrontations'],
    difficulty: 'beginner',
    lensRecommendation: '50-85mm for compression'
  },
  
  'profile': {
    description: 'Side view of subject',
    emotionalImpact: 'Objectivity, detachment, movement emphasis, contemplation',
    bestFor: 'Movement shots, contemplative moments, silhouettes, mystery',
    commonUses: ['Walking silhouettes', 'Contemplation', 'Mystery characters'],
    difficulty: 'beginner',
    lensRecommendation: 'Any'
  },
  
  'three-quarter': {
    description: 'Between front and profile (45-degree angle)',
    emotionalImpact: 'Dynamic, flattering, revealing but not fully frontal',
    bestFor: 'Portraits, character introductions, beauty shots',
    commonUses: ['Portrait photography', 'Character introductions', 'Glamour shots'],
    difficulty: 'beginner',
    lensRecommendation: '85mm for portraits'
  },
  
  'reflection': {
    description: 'Shot of subject in mirror, water, or reflective surface',
    emotionalImpact: 'Introspection, duality, alternate reality, self-examination',
    bestFor: 'Character introspection, dual personalities, artistic shots',
    commonUses: ['Mirror scenes', 'Identity crisis', 'Artistic sequences'],
    difficulty: 'advanced',
    lensRecommendation: 'Any with attention to reflection angles'
  },
  
  'aerial': {
    description: 'From aircraft or drone',
    emotionalImpact: 'Epic scale, overview, detachment, grandeur',
    bestFor: 'Establishing shots, landscapes, action sequences, cityscapes',
    commonUses: ['Opening shots', 'Chase sequences', 'Nature documentaries', 'City reveals'],
    difficulty: 'advanced',
    lensRecommendation: 'Wide angle with ND filters'
  },
  
  'crane-shot': {
    description: 'High angle using crane equipment',
    emotionalImpact: 'Dramatic revelation, transition, epic scale, overview',
    bestFor: 'Opening/closing shots, dramatic reveals, scene transitions',
    commonUses: ['Movie openings', 'Wedding reveals', 'Concert openings', 'Epic moments'],
    difficulty: 'advanced',
    lensRecommendation: 'Wide angle 16-35mm'
  },
  
  'worms-view': {
    description: 'Camera on ground looking straight up through objects',
    emotionalImpact: 'Overwhelmed, trapped, surrounded, looking up at threats',
    bestFor: 'Forest canopy, city streets, surrounded feeling, claustrophobia',
    commonUses: ['Forest shots', 'City street canyons', 'Surrounded by enemies'],
    difficulty: 'intermediate',
    lensRecommendation: 'Ultra-wide fisheye 8-15mm'
  }
};

// ============================================================================
// CAMERA MOVEMENTS - Expanded
// ============================================================================

export const CAMERA_MOVEMENTS = {
  // Basic Movements
  'static': {
    description: 'Fixed position - no movement',
    emotionalImpact: 'Stability, observation, contemplation, objectivity, formality',
    bestFor: 'Dialogue, interviews, stable moments, establishing shots, formal scenes',
    technicalNotes: 'Use tripod or solid surface. Consider slight breathing for realism.',
    speed: 'none',
    difficulty: 'beginner'
  },
  
  'pan': {
    description: 'Horizontal rotation left or right',
    emotionalImpact: 'Revealing space, searching, following horizontal action, discovery',
    bestFor: 'Landscape reveals, following movement, establishing surroundings',
    technicalNotes: 'Smooth controlled motion. Speed depends on scene energy.',
    speed: 'variable',
    difficulty: 'beginner'
  },
  
  'tilt': {
    description: 'Vertical rotation up or down',
    emotionalImpact: 'Revealing height, following vertical action, awe, looking up/down',
    bestFor: 'Tall structures, vertical reveals, looking up at hero, sky to ground',
    technicalNotes: 'Smooth vertical sweep. Often combined with pan.',
    speed: 'variable',
    difficulty: 'beginner'
  },
  
  // Dolly Movements
  'dolly-in': {
    description: 'Camera moves closer to subject',
    emotionalImpact: 'Intimacy, intensity, revelation, focusing attention, importance',
    bestFor: 'Emotional moments, reveals, emphasizing reaction, building tension',
    technicalNotes: 'Smooth track or wheels. Speed: slow for drama, fast for action.',
    speed: 'slow to medium',
    difficulty: 'intermediate'
  },
  
  'dolly-out': {
    description: 'Camera moves away from subject',
    emotionalImpact: 'Isolation, context, withdrawal, scale, loneliness',
    bestFor: 'Revealing environment, ending scenes, showing isolation, epic scale',
    technicalNotes: 'Smooth backward motion. Often reveals something important.',
    speed: 'slow to medium',
    difficulty: 'intermediate'
  },
  
  'dolly-zoom': {
    description: 'Dolly in while zooming out (or vice versa) - Vertigo effect',
    emotionalImpact: 'Disorientation, realization, shock, psychological unease',
    bestFor: 'Moments of realization, horror reveals, psychological distress',
    technicalNotes: 'Requires coordination of dolly and zoom. Classic Hitchcock technique.',
    speed: 'slow',
    difficulty: 'advanced'
  },
  
  'truck': {
    description: 'Camera moves left or right parallel to scene',
    emotionalImpact: 'Following parallel action, revealing side details, tracking',
    bestFor: 'Walking alongside characters, revealing wall details, parallel action',
    technicalNotes: 'Sideways movement. Can be handheld or tracked.',
    speed: 'medium',
    difficulty: 'intermediate'
  },
  
  'pedestal': {
    description: 'Camera moves up or down vertically (not tilting)',
    emotionalImpact: 'Revealing vertical space, rising above, descending into',
    bestFor: 'Rising above crowd, descending into pit, height changes',
    technicalNotes: 'Vertical movement maintaining same angle. Requires jib or crane.',
    speed: 'medium',
    difficulty: 'intermediate'
  },
  
  // Complex Movements
  'crane': {
    description: 'Sweeping vertical arcs using crane or jib',
    emotionalImpact: 'Epic scale, transitions, dramatic reveals, grandeur',
    bestFor: 'Opening/closing shots, dramatic reveals, concert openings, weddings',
    technicalNotes: 'Large vertical and horizontal arc. Majestic, flowing movement.',
    speed: 'slow to medium',
    difficulty: 'advanced'
  },
  
  'jib': {
    description: 'Smaller crane movements, more intimate',
    emotionalImpact: 'Elegance, smooth transitions, floating quality',
    bestFor: 'Product shots, food photography, intimate reveals, music videos',
    technicalNotes: 'Smaller arc than crane. Great for precise movements.',
    speed: 'smooth and controlled',
    difficulty: 'intermediate'
  },
  
  'steadicam': {
    description: 'Smooth floating movement using Steadicam rig',
    emotionalImpact: 'Dream-like, following through space, fluid, natural movement',
    bestFor: 'Following characters through spaces, long takes, music videos, walking scenes',
    technicalNotes: 'Requires Steadicam operator. Smooth gliding motion.',
    speed: 'variable, smooth',
    difficulty: 'advanced'
  },
  
  'handheld': {
    description: 'Shaky natural camera movement',
    emotionalImpact: 'Documentary feel, urgency, realism, chaos, immediacy',
    bestFor: 'Documentary, action scenes, found footage, realistic drama, running',
    technicalNotes: 'Controlled shakiness. Adds energy and realism.',
    speed: 'variable',
    difficulty: 'intermediate'
  },
  
  'gimbal': {
    description: 'Smooth stabilized handheld movement',
    emotionalImpact: 'Professional fluidity, modern feel, dynamic smoothness',
    bestFor: 'Modern action, music videos, vlogs, smooth following shots',
    technicalNotes: 'Electronic stabilization. Smooth but with handheld freedom.',
    speed: 'variable, smooth',
    difficulty: 'intermediate'
  },
  
  'drone': {
    description: 'Aerial movement using drone',
    emotionalImpact: 'Epic scale, freedom, bird\'s perspective, grandeur',
    bestFor: 'Establishing shots, landscapes, action sequences, impossible angles',
    technicalNotes: 'Remote controlled flight. Wide range of movement possibilities.',
    speed: 'variable',
    difficulty: 'advanced'
  },
  
  // Zoom and Focus
  'zoom-in': {
    description: 'Changing focal length to magnify subject',
    emotionalImpact: 'Sudden focus, emphasis, surprise, discovery, importance',
    bestFor: 'Emphasis, reveals, dramatic moments, directing attention',
    technicalNotes: 'Optical zoom. Different feel than dolly - compresses space.',
    speed: 'fast or slow depending on effect',
    difficulty: 'beginner'
  },
  
  'zoom-out': {
    description: 'Changing focal length to widen view',
    emotionalImpact: 'Context, revelation, isolation, showing the bigger picture',
    bestFor: 'Revealing surroundings, ending shots, showing scale',
    technicalNotes: 'Optical zoom out. Classic ending technique.',
    speed: 'slow to medium',
    difficulty: 'beginner'
  },
  
  'rack-focus': {
    description: 'Shifting focus from one plane to another',
    emotionalImpact: 'Connection, choice, revelation, shifting attention',
    bestFor: 'Revealing connections, foreground/background relationships, choices',
    technicalNotes: 'Precise focus pull. Requires planning of focal points.',
    speed: 'smooth transition',
    difficulty: 'advanced'
  },
  
  'whip-pan': {
    description: 'Very fast pan creating motion blur',
    emotionalImpact: 'Energy, chaos, transition, disorientation, excitement',
    bestFor: 'Action transitions, fast reveals, chaotic moments, music videos',
    technicalNotes: 'Fast blur transition. Often used as transition device.',
    speed: 'very fast',
    difficulty: 'intermediate'
  },
  
  'whip-tilt': {
    description: 'Very fast tilt creating vertical motion blur',
    emotionalImpact: 'Sudden vertical shift, surprise, energy',
    bestFor: 'Vertical reveals, falling, rising, dramatic transitions',
    technicalNotes: 'Fast vertical blur. Less common than whip-pan.',
    speed: 'very fast',
    difficulty: 'intermediate'
  },
  
  'orbit': {
    description: 'Camera circles around subject',
    emotionalImpact: 'Scrutiny, revelation, 360 view, importance, celebration',
    bestFor: 'Character reveals, important moments, showcasing subject',
    technicalNotes: 'Circular path around subject. Requires space or circular track.',
    speed: 'slow to medium',
    difficulty: 'advanced'
  },
  
  'snorricam': {
    description: 'Camera rigged to actor\'s body',
    emotionalImpact: 'Intense subjectivity, disorientation, drunkenness, instability',
    bestFor: 'Intoxicated POV, disorientation, intense action, drug sequences',
    technicalNotes: 'Camera attached to actor. Face stays in frame while background moves.',
    speed: 'matches actor movement',
    difficulty: 'advanced'
  },
  
  'follow-focus': {
    description: 'Continuous focus adjustment to keep moving subject sharp',
    emotionalImpact: 'Professional tracking, importance on moving subject',
    bestFor: 'Moving subjects, shallow depth of field tracking',
    technicalNotes: 'Requires focus puller skill. Critical for shallow DOF.',
    speed: 'matches subject',
    difficulty: 'advanced'
  }
};

// ============================================================================
// SHOT TYPES - Expanded
// ============================================================================

export const SHOT_TYPES = {
  // Distance Shots
  'extreme-wide': {
    description: 'Subject very small in vast environment',
    emotionalImpact: 'Isolation, scale, epic scope, insignificance, environment dominates',
    bestFor: 'Establishing vast landscapes, showing scale, isolation, opening shots',
    framing: 'Subject takes up less than 1/4 of frame',
    lens: 'Wide angle 10-24mm'
  },
  
  'wide': {
    description: 'Full subject plus extensive surroundings',
    emotionalImpact: 'Context, environment, scale, spatial relationships',
    bestFor: 'Establishing shots, action sequences, showing full body movement',
    framing: 'Full subject visible with environment',
    lens: 'Wide angle 16-35mm'
  },
  
  'medium-wide': {
    description: 'Subject from knees up with some environment',
    emotionalImpact: 'Some context with character focus, movement emphasis',
    bestFor: 'Character movement, slight environment context, action',
    framing: 'Knees to head',
    lens: '35-50mm'
  },
  
  'medium': {
    description: 'Subject from waist up',
    emotionalImpact: 'Dialogue focus with some body language, interaction',
    bestFor: 'Dialogue, interaction, showing body language',
    framing: 'Waist to head',
    lens: '50mm'
  },
  
  'medium-close-up': {
    description: 'Subject from chest up',
    emotionalImpact: 'Intimate dialogue, facial expressions, personality',
    bestFor: 'Dialogue, reactions, interviews, showing emotion',
    framing: 'Chest to head',
    lens: '50-85mm'
  },
  
  'close-up': {
    description: 'Subject head and shoulders',
    emotionalImpact: 'Intimacy, emotion, reaction, importance',
    bestFor: 'Emotional moments, reactions, emphasizing importance',
    framing: 'Head and shoulders',
    lens: '85mm'
  },
  
  'extreme-close-up': {
    description: 'Detail only - eyes, mouth, hands, objects',
    emotionalImpact: 'Intense emotion, symbolism, detail importance, intimacy',
    bestFor: 'Eyes, hands holding object, important details, intense emotion',
    framing: 'Fills frame with detail',
    lens: 'Macro or 100mm+'
  },
  
  // Special Shots
  'establishing': {
    description: 'Wide shot establishing location and time',
    emotionalImpact: 'Setting the scene, geography, time period, atmosphere',
    bestFor: 'Scene openings, location establishment, time/place setting',
    framing: 'Wide view of location',
    lens: 'Wide angle'
  },
  
  'master': {
    description: 'Wide shot showing all characters and action in scene',
    emotionalImpact: 'Full scene context, spatial relationships, staging',
    bestFor: 'Scene coverage, showing all actors, action staging',
    framing: 'Wide enough for all action',
    lens: 'Wide to standard'
  },
  
  'two-shot': {
    description: 'Two characters in frame',
    emotionalImpact: 'Relationship, interaction, equality, dialogue',
    bestFor: 'Conversations between two people, relationship scenes',
    framing: 'Two subjects',
    lens: '35-50mm'
  },
  
  'three-shot': {
    description: 'Three characters in frame',
    emotionalImpact: 'Group dynamic, triangle relationship, interaction',
    bestFor: 'Small group interactions, trio dynamics',
    framing: 'Three subjects',
    lens: '28-35mm'
  },
  
  'group-shot': {
    description: 'Multiple characters in frame',
    emotionalImpact: 'Team, ensemble, crowd, social dynamics',
    bestFor: 'Group scenes, ensemble cast, crowd reactions',
    framing: 'Multiple subjects',
    lens: 'Wide angle'
  },
  
  'over-shoulder': {
    description: 'Looking past one subject at another',
    emotionalImpact: 'Conversation intimacy, spatial relationship',
    bestFor: 'Dialogue, conversations, interviews',
    framing: 'Shoulder in foreground, face in background',
    lens: '50-85mm'
  },
  
  'point-of-view': {
    description: 'What a character sees',
    emotionalImpact: 'Immersion, subjectivity, identification',
    bestFor: 'First person, character perspective, reactions to POV',
    framing: 'Character\'s exact view',
    lens: '50mm (human eye)'
  },
  
  'reaction-shot': {
    description: 'Close-up of character reacting to something',
    emotionalImpact: 'Emotional response, internal state, impact',
    bestFor: 'Emotional beats, comedy reactions, dramatic moments',
    framing: 'Face showing reaction',
    lens: '50-85mm'
  },
  
  'insert': {
    description: 'Detail shot of object or action detail',
    emotionalImpact: 'Importance of detail, information, symbolism',
    bestFor: 'Objects, details, important information, hands doing something',
    framing: 'Object fills frame',
    lens: 'Macro or any'
  },
  
  'cutaway': {
    description: 'Shot of something other than main action',
    emotionalImpact: 'Context, foreshadowing, parallel action, B-roll',
    bestFor: 'Environment details, parallel action, atmosphere',
    framing: 'Varies',
    lens: 'Any'
  },
  
  'aerial': {
    description: 'From above, bird\'s eye view',
    emotionalImpact: 'Scale, overview, patterns, detachment',
    bestFor: 'Landscapes, cityscapes, action overview',
    framing: 'Top-down view',
    lens: 'Wide angle'
  },
  
  'underwater': {
    description: 'Submerged camera',
    emotionalImpact: 'Otherworldly, floating, dreamlike, danger',
    bestFor: 'Underwater scenes, drowning, dream sequences',
    framing: 'Submerged perspective',
    lens: 'Underwater housing'
  },
  
  'mirror-shot': {
    description: 'Reflection in mirror or reflective surface',
    emotionalImpact: 'Introspection, duality, self-examination',
    bestFor: 'Character reflection, identity, vanity',
    framing: 'Mirror reflection',
    lens: 'Any with angle consideration'
  },
  
  'silhouette': {
    description: 'Subject as dark shape against bright background',
    emotionalImpact: 'Mystery, anonymity, drama, shape emphasis',
    bestFor: 'Anonymous figures, dramatic reveals, shape emphasis',
    framing: 'Backlit subject',
    lens: 'Any'
  },
  
  'shadow-shot': {
    description: 'Focusing on shadow rather than subject',
    emotionalImpact: 'Threat, mystery, foreboding, symbolism',
    bestFor: 'Threat, mystery, horror, artistic shots',
    framing: 'Shadow prominent',
    lens: 'Any'
  },
  
  'low-angle-shot': {
    description: 'Shot from below subject (different from low-angle)',
    emotionalImpact: 'Power, threat, dominance, awe',
    bestFor: 'Powerful figures, threats, heroic poses',
    framing: 'Looking up at subject',
    lens: 'Wide angle'
  },
  
  'high-angle-shot': {
    description: 'Shot from above subject (different from high-angle)',
    emotionalImpact: 'Vulnerability, weakness, surveillance',
    bestFor: 'Vulnerable characters, overview shots',
    framing: 'Looking down at subject',
    lens: 'Any'
  },
  
  'through-frame': {
    description: 'Subject viewed through foreground element',
    emotionalImpact: 'Voyeurism, obstruction, depth, layers',
    bestFor: 'Peeking, observation, depth composition',
    framing: 'Subject through foreground',
    lens: 'Shallow depth of field'
  },
  
  'dirty-single': {
    description: 'Close-up with some foreground element visible',
    emotionalImpact: 'Intimacy with context, depth, environment present',
    bestFor: 'Intimate shots with location context',
    framing: 'Close-up with foreground blur',
    lens: '50-85mm shallow DOF'
  }
};

// Export all cinematography data
export const CINEMATOGRAPHY_DB = {
  angles: CAMERA_ANGLES,
  movements: CAMERA_MOVEMENTS,
  shots: SHOT_TYPES
};

export default CINEMATOGRAPHY_DB;
