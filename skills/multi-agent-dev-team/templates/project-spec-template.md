# Project Specification Template

Use this template when requesting projects from the PM agent.

## Basic Template

```markdown
Build a [project type] for [purpose/client].

**Core Features:**
- [Feature 1]
- [Feature 2]
- [Feature 3]

**Tech Stack:**
- [Technology 1]
- [Technology 2]

**Design:**
- [Design requirement 1]
- [Design requirement 2]
```

## Detailed Template

```markdown
## Project Overview
**Name:** [Project Name]
**Type:** [Landing Page / Web App / Component Library / etc.]
**Purpose:** [What problem does this solve?]

## Requirements

### Must Have
- [ ] [Critical requirement 1]
- [ ] [Critical requirement 2]
- [ ] [Critical requirement 3]

### Nice to Have
- [ ] [Optional feature 1]
- [ ] [Optional feature 2]

## Technical Specifications

**Framework:** [Next.js / React / Node.js / etc.]
**Language:** [TypeScript / JavaScript]
**Styling:** [Tailwind CSS / CSS Modules / etc.]
**Deployment:** [Vercel / Netlify / etc.]

## Design Requirements

**Layout:**
- [Layout description]

**Colors:**
- Primary: [color]
- Secondary: [color]
- Accent: [color]

**Typography:**
- Headings: [font]
- Body: [font]

**Components:**
1. [Component 1]: [description]
2. [Component 2]: [description]

## Content

**Hero Section:**
- Headline: "[text]"
- Subheadline: "[text]"
- CTA Button: "[text]"

**[Other sections...]**

## Acceptance Criteria

The project will be considered complete when:
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]
- [ ] Code is clean and well-documented
- [ ] Git repository is initialized
- [ ] README includes setup instructions

## Constraints

**Timeline:** [Deadline or time estimate]
**Budget:** [If applicable]
**Restrictions:** [Any limitations to be aware of]

## Examples / References

[Links to similar projects or design inspiration]

## Notes

[Any additional context or special considerations]
```

## Example Specifications

### Example 1: SaaS Landing Page

```markdown
Build a landing page for a task management SaaS called "TaskFlow".

**Core Features:**
- Hero section with animated gradient background
- Features section with 4 cards (icons + text)
- Pricing table (Free, Pro, Enterprise)
- FAQ accordion
- Contact form with email validation

**Tech Stack:**
- Next.js 14+ (App Router)
- TypeScript
- Tailwind CSS
- Shadcn/ui components

**Design:**
- Modern, clean aesthetic
- Primary color: Blue (#3B82F6)
- Dark mode support
- Fully responsive (mobile-first)
```

### Example 2: Component Library

```markdown
Create a reusable Button component library.

**Requirements:**
- TypeScript with full type safety
- Variants: primary, secondary, outline, ghost, destructive
- Sizes: sm, md, lg, xl
- Loading state with spinner
- Disabled state
- Icon support (left/right)
- Full accessibility (ARIA labels, keyboard nav)

**Tech Stack:**
- React 18+
- TypeScript
- class-variance-authority for variants
- Tailwind CSS
- Storybook for documentation

**Deliverables:**
- Button.tsx component
- Button.stories.tsx (Storybook)
- README with usage examples
- Published to npm (optional)
```

### Example 3: GitHub Profile Viewer

```markdown
Build a GitHub user profile viewer app.

**Features:**
- Search for GitHub users by username
- Display user avatar, name, bio, stats
- Show recent repositories (max 10)
- Error handling for invalid usernames
- Loading states
- Responsive grid layout

**Tech Stack:**
- Next.js 14+ App Router
- TypeScript
- GitHub REST API
- Tailwind CSS
- React Query for data fetching

**UI Components:**
- SearchBar
- UserCard
- RepoCard
- LoadingSpinner
- ErrorMessage

**API:**
- Use GitHub's public API (no auth required)
- Endpoint: `https://api.github.com/users/{username}`
```

## Tips for Writing Good Specs

### ✅ Do:
- Be specific about features and requirements
- Provide tech stack preferences
- Include design details (colors, layout, typography)
- Give examples or references when possible
- List acceptance criteria clearly
- Specify must-haves vs. nice-to-haves

### ❌ Don't:
- Be vague ("make it nice")
- Ask for everything at once
- Assume the agent knows your preferences
- Omit critical technical requirements
- Forget about responsive design
- Skip error handling and edge cases

## Iteration Tips

If the first version isn't perfect:

```markdown
The landing page looks good, but please make these changes:
1. Make the hero section height `min-h-screen` instead of `h-screen`
2. Add a dark mode toggle button
3. Change the primary color to purple
4. Add smooth scroll behavior for anchor links
```

Be specific about what to change and why.
