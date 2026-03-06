# UX Psychology

Psychological principles for designing intuitive, effective user experiences.

## Table of Contents

1. [Gestalt Principles](#gestalt-principles)
2. [Cognitive Load in UX](#cognitive-load-in-ux)
3. [Attention & Perception](#attention--perception)
4. [Interaction Psychology](#interaction-psychology)
5. [Emotional Design](#emotional-design)

---

## Gestalt Principles

How humans perceive visual elements as unified wholes.

### Core Principles

| Principle | Description | UX Application |
|-----------|-------------|----------------|
| **Proximity** | Close elements perceived as groups | Group related controls |
| **Similarity** | Similar elements perceived as related | Consistent button styles |
| **Continuity** | Eye follows lines/curves | Visual flow, progress indicators |
| **Closure** | Mind completes incomplete shapes | Logos, icons |
| **Figure-Ground** | Distinguish foreground from background | Modal overlays, focus states |
| **Common Region** | Elements in same region grouped | Cards, containers |
| **Symmetry** | Symmetric objects perceived as unified | Balanced layouts |
| **Common Fate** | Moving together = related | Animation groups |

### Application Examples

| Principle | Good Example | Bad Example |
|-----------|--------------|-------------|
| Proximity | Form fields with labels close | Labels far from inputs |
| Similarity | All CTAs same color | Inconsistent button styles |
| Closure | Progress circle 75% complete | Confusing incomplete shapes |
| Figure-Ground | Clear modal with dimmed background | Unclear focus areas |

---

## Cognitive Load in UX

### Load Types in Interface Design

| Type | Source | Reduction Strategy |
|------|--------|-------------------|
| **Intrinsic** | Task complexity | Progressive disclosure |
| **Extraneous** | Poor design | Simplify, clarify |
| **Germane** | Learning the system | Familiar patterns, consistency |

### Reducing Cognitive Load

| Strategy | Implementation |
|----------|----------------|
| **Chunking** | Group related items (7±2 rule for menus) |
| **Progressive disclosure** | Show only what's needed now |
| **Recognition over recall** | Show options, don't make users remember |
| **Defaults** | Smart pre-selections |
| **Constraints** | Limit invalid choices |
| **Consistency** | Same action = same result everywhere |

### Hick's Law

**Decision time increases with number and complexity of choices.**

| # Options | Effect | Solution |
|-----------|--------|----------|
| 1-3 | Fast decision | Ideal for primary actions |
| 4-7 | Moderate slowdown | Acceptable with clear categories |
| 8+ | Decision paralysis | Categorize, search, filter |

### Fitts's Law

**Time to target depends on distance and target size.**

| Application | Implementation |
|-------------|----------------|
| Important buttons | Larger, easier to hit |
| Edge/corner placement | Effectively infinite size (screen edge) |
| Touch targets | Minimum 44×44 pixels (iOS guideline) |
| Related actions | Close together |

---

## Attention & Perception

### Visual Hierarchy

| Level | Element | Purpose |
|-------|---------|---------|
| 1 | Headlines, hero images | Capture attention |
| 2 | Subheads, key benefits | Communicate value |
| 3 | Body text, details | Inform decisions |
| 4 | Fine print, metadata | Support, legal |

### Attention Patterns

| Pattern | Description | Design Response |
|---------|-------------|-----------------|
| **F-Pattern** | Scan top, then down left | Key info top-left |
| **Z-Pattern** | Zig-zag for sparse pages | Landing pages |
| **Layer-cake** | Headings only | Clear hierarchy |
| **Spotted** | Jump to specific elements | Visual differentiation |

### Pre-Attentive Attributes

Processed in <250ms without conscious attention:

| Attribute | Use Case |
|-----------|----------|
| Color | Status, categories, attention |
| Size | Importance, hierarchy |
| Shape | Differentiation, icons |
| Position | Grouping, relationships |
| Orientation | Direction, flow |
| Motion | Alerts, state changes |

### Banner Blindness

Users ignore banner-like elements:

| Cause | Solution |
|-------|----------|
| Ad-like appearance | Native, content-like design |
| Peripheral placement | Inline, contextual |
| Repetitive exposure | Vary placement, timing |
| Irrelevance | Personalized, relevant content |

---

## Interaction Psychology

### Affordances

Perceived properties suggesting use:

| Affordance Type | Description | Example |
|-----------------|-------------|---------|
| **Physical** | Real properties | Button depth, handle shape |
| **Perceived** | Suggested action | Button shadow = clickable |
| **Hidden** | Undiscovered features | Swipe gestures |
| **False** | Misleading suggestion | Fake buttons |

### Feedback Principles

| Principle | Description | Example |
|-----------|-------------|---------|
| **Immediate** | Instant response | Button press state |
| **Continuous** | Ongoing status | Progress bars |
| **Comprehensible** | Clear meaning | Success/error messages |
| **Appropriate** | Matches action importance | Subtle vs. modal |

### Error Prevention & Recovery

| Strategy | Implementation |
|----------|----------------|
| **Constraints** | Prevent invalid input |
| **Confirmation** | "Are you sure?" for destructive |
| **Undo** | Allow reversal |
| **Defaults** | Safe starting values |
| **Forgiveness** | Graceful degradation |

### Jakob's Law

**Users spend most time on OTHER sites.**

| Implication | Application |
|-------------|-------------|
| Use familiar patterns | Standard navigation, forms |
| Meet expectations | Links look like links |
| Reduce learning curve | Conventions over innovation |
| Innovation with caution | For genuine improvement only |

---

## Emotional Design

### Norman's Three Levels

| Level | Description | Design Focus |
|-------|-------------|--------------|
| **Visceral** | Immediate reaction | Aesthetics, first impression |
| **Behavioral** | Use experience | Usability, effectiveness |
| **Reflective** | Conscious thought | Brand, identity, meaning |

### Emotional States in UX

| State | Trigger | Design Response |
|-------|---------|-----------------|
| **Frustration** | Errors, confusion | Clear errors, help |
| **Anxiety** | Uncertainty | Progress, confirmation |
| **Delight** | Exceeded expectations | Micro-interactions, polish |
| **Trust** | Consistency, reliability | Professional, stable |
| **Accomplishment** | Completed tasks | Celebration, progress |

### Micro-Interactions

Small moments that create emotional connection:

| Type | Purpose | Example |
|------|---------|---------|
| **Triggers** | Initiate interaction | Pull to refresh |
| **Rules** | Define behavior | What happens when |
| **Feedback** | Communicate status | Animation, sound |
| **Loops/modes** | Repeat or change | Habit formation |

### Peak-End Rule in UX

| Application | Implementation |
|-------------|----------------|
| Create positive peaks | Delightful surprises |
| End on high note | Success confirmation, thank you |
| Minimize negative peaks | Smooth error recovery |
| Compress pain | Get difficult parts over quickly |

---

## Dark UX Patterns (Avoid)

| Pattern | Description | Ethical Alternative |
|---------|-------------|---------------------|
| **Roach motel** | Easy in, hard out | Easy cancellation |
| **Trick questions** | Confusing checkboxes | Clear, honest options |
| **Sneak into basket** | Auto-add items | Opt-in only |
| **Hidden costs** | Surprise fees | Transparent pricing |
| **Bait and switch** | Advertise one, deliver another | Honest representation |
| **Confirmshaming** | Guilt-trip decline | Neutral options |
| **Forced continuity** | Silent auto-renew | Clear renewal notice |
| **Misdirection** | Distract from important | Honest visual hierarchy |

---

## Accessibility Psychology

### Cognitive Accessibility

| Principle | Implementation |
|-----------|----------------|
| **Predictability** | Consistent behavior |
| **Simplicity** | Clear language, simple flows |
| **Error tolerance** | Forgiving input, easy recovery |
| **Focus support** | Clear progress, minimal distraction |
| **Memory support** | Recognition over recall |

### Universal Design Benefits

Accessibility improvements help everyone:

| Feature | Primary Benefit | Universal Benefit |
|---------|-----------------|-------------------|
| Captions | Deaf users | Noisy environments |
| High contrast | Low vision | Bright sunlight |
| Keyboard navigation | Motor impairments | Power users |
| Clear language | Cognitive differences | Non-native speakers |
| Large touch targets | Motor impairments | One-handed use |
