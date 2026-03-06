# Figma AI Workflow

## Figma's AI Capabilities

### Built-in Features
- **AI image generation**: Text-to-image in frames
- **Background removal**: Smart object isolation
- **Generative fill**: Expand or replace content
- **Auto-naming layers**: Contextual layer organization
- **Asset search**: AI-powered library search

### Access
Available in Actions menu or inline toolbar. No plugin needed for core features.

## Vibe Design in Figma

### Workflow Pattern
1. Create rough layout (boxes, frames)
2. Use AI to generate content for frames
3. Iterate with "regenerate" and prompts
4. Replace AI content with real assets
5. Apply design system tokens

### Frame-Based Generation
```
1. Create frame at target size
2. Select frame
3. Actions → Generate image
4. Describe what should fill the frame
5. Regenerate until good enough
6. Refine or replace manually
```

## Useful Plugins

### AI-Powered
- **Magician**: AI design assistant, multiple features
- **Wireframe Designer**: Quick wireframe generation
- **Automator**: AI-powered automation

### Workflow Enhancement
- **Content Reel**: Real placeholder content
- **Unsplash**: Stock photos in Figma
- **Iconify**: Icon library access

## Design System Integration

### Maintaining Consistency
When using AI-generated concepts:
1. Extract color values → match to your palette
2. Note spacing proportions → apply your grid
3. Identify typography style → use your type scale
4. Capture component ideas → build with your tokens

### Token Application
After AI exploration:
```
AI output: "Nice blue card with shadow"
Your implementation:
  - Background: surface.secondary
  - Shadow: elevation.md
  - Padding: space.4
  - Border-radius: radius.lg
```

## Prototype Workflow

### AI → Interactive
1. Generate screen concepts in Figma AI
2. Extract layout and flow ideas
3. Rebuild with components
4. Add interactions and transitions
5. Test and iterate

### Speed Tips
- Use AI for hero images, illustrations
- Keep UI chrome (nav, buttons) as components
- AI for placeholder content during ideation
- Replace with real content before handoff

## Collaboration

### Sharing AI Concepts
- Comment on AI-generated frames with intent
- Mark what's "direction" vs "final"
- Use sections: "AI Exploration" vs "Production"

### Developer Handoff
- Never hand off raw AI output
- Rebuild in components with proper naming
- Use Dev Mode for clean specs
- Document design decisions, not AI prompts
