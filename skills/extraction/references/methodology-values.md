# Methodology Values

What to look for and prioritize when extracting patterns. These values inform what's worth extracting and what makes a pattern valuable.

---

## Priority Order

When extracting from a project, prioritize in this order:

1. **Design Systems & Visual Patterns** — Highest priority
2. **Architecture & Code Patterns**
3. **Workflow & DX Patterns**
4. **Documentation Patterns**
5. **Infrastructure Patterns**

---

## Design & Visual (Highest Priority)

Look for evidence of intentional aesthetic choices:

**Aesthetic Foundation**
- Mood boards, reference lists, inspiration docs
- Documented "vibe" or design direction
- Color palettes with semantic naming
- Typography scales and font choices

**Design Tokens**
- Tailwind config customizations (not defaults)
- CSS custom properties / variables
- Theme files, color schemes
- Spacing scales, border radii, shadows

**Emotional Design Signals**
- Micro-interactions, hover states, transitions
- Loading states that feel satisfying
- Progress indicators, achievements, rewards
- Animations that enhance (not distract)

**Preferred Aesthetics to Identify**
- Retro-futuristic (CRT glows, analog-digital fusion)
- Video game UI (HUDs, score displays, achievements)
- Futuristic interfaces (sci-fi terminals, holographic)
- Anything with a distinct *feel* (not generic bootstrap)

**Anti-Patterns to Note**
- Generic template aesthetics
- Default Tailwind without customization
- "Clean" with no personality
- Missing design documentation

---

## Minimal Code Principles

Look for evidence of intentional minimalism:

**DRY Patterns**
- Shared components, utilities, helpers
- Extracted common logic
- No copy-paste duplication

**Small, Focused Files**
- Files < 200 lines (ideally < 100)
- Functions < 20 lines
- Single responsibility components

**Reusable Primitives**
- Component libraries
- Utility functions
- Shared hooks/composables

**Questions to Ask**
- Could this code be deleted without loss?
- Is there duplication that should be extracted?
- Are files doing too much?

---

## Compound Work Patterns

Look for work that compounds:

**Extracted Patterns**
- Design systems used across views
- Component libraries
- Shared configuration
- Utility packages

**Encoded Decisions**
- ADRs or decision docs
- Comments explaining "why" not "what"
- Documented trade-offs

**Reusable Infrastructure**
- Dockerfile patterns
- CI/CD configurations
- Makefile targets
- Docker Compose setups

---

## DX Patterns

Look for developer experience investments:

**Fast Feedback**
- Hot reload configuration
- Watch mode scripts
- Fast build times

**One-Command Operations**
- `make dev` or equivalent
- `make clean`, `make reset`
- `make seed` for test data

**Environment Parity**
- Local, Docker, production modes
- Easy switching between environments
- Consistent configuration

---

## UX Patterns

Look for intentional user experience:

**Minimal UI**
- Only necessary elements
- No redundant information
- Clean, focused interfaces

**Fast & Responsive**
- Optimistic updates
- Skeleton screens
- Lazy loading

**Real-Time**
- WebSocket implementations
- Live updates
- Streaming responses

---

## Documentation Patterns

Look for docs-first evidence:

**Project Documentation**
- PRDs, specs, feature docs
- Persona definitions
- Architecture diagrams

**Runbooks**
- Operational guides
- Deployment procedures
- Troubleshooting docs

**Current vs Future Separation**
- Clear distinction between what exists and what's planned
- No aspirational docs mixed with reality

---

## What's Worth Extracting

| High Value | Lower Value |
|------------|-------------|
| Patterns used across multiple views/components | One-off solutions |
| Decisions with clear rationale | Arbitrary choices |
| Workflows you'd use again | Project-specific hacks |
| Design systems with documentation | Default configurations |
| Reusable infrastructure | Overcomplicated setups |

---

## Extraction Mindset

For each pattern found, ask:

1. **Why was this built this way?** — Capture the reasoning
2. **What would you keep?** — Identify the core value
3. **What would you change?** — Note improvements
4. **What's generalizable?** — Strip project-specific details
5. **Would an expert say "this captures real knowledge"?** — The quality test
