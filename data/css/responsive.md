# Responsive Techniques

## Viewport Units Traps

- `100vh` on mobile includes toolbar—content behind address bar
- `100dvh` (dynamic viewport) changes as toolbar hides/shows—causes reflow
- `100svh` (small viewport) always excludes toolbar—most predictable
- Mix: `height: 100svh; min-height: 100dvh` for hero sections

## Media Query Patterns

- Mobile-first: use `min-width`—base styles for mobile, layer up for larger
- `min-width` is mobile-first; `max-width` is desktop-first—don't mix approaches
- Common breakpoints: 640px, 768px, 1024px, 1280px—but adapt to your content
- Prefer intrinsic sizing over breakpoints—fewer media queries needed

## Container Queries

- `container-type: inline-size` on parent—enables queries on that container
- `@container (min-width: 400px) { ... }`—component responds to ITS container
- `container-name` for targeting specific ancestor—`@container sidebar (min-width: ...)`
- Better than media queries for reusable components—same component, different contexts

## Fluid Typography

- `clamp(min, preferred, max)` for smooth scaling—`font-size: clamp(1rem, 2vw + 0.5rem, 2rem)`
- Don't use only vw—user can't resize text, accessibility issue
- Always include rem component—`2vw + 0.5rem` allows zoom to work
- Test at extreme widths—very wide screens can make huge text

## Fluid Spacing

- `clamp()` for padding/margin too—`padding: clamp(1rem, 5vw, 3rem)`
- CSS `min()` and `max()` for one-sided constraints—`width: min(100%, 800px)`
- Combine with calc: `calc(1rem + 2vw)`—smooth transition between sizes
- Use CSS custom properties for consistent fluid scales

## Image Responsiveness

- `max-width: 100%; height: auto` on images—prevents overflow, maintains ratio
- `object-fit: cover` vs `contain`: cover crops, contain letterboxes
- `aspect-ratio` on container holds space—prevents layout shift during load
- `srcset` and `sizes` for art direction—browser picks best image

## Layout Shifts

- Reserve space for images—use `aspect-ratio` or explicit dimensions
- Font loading causes shift—use `font-display: swap` or preload critical fonts
- Ads/embeds shift content—reserve space with `min-height`
- `scrollbar-gutter: stable`—prevents shift when scrollbar appears/disappears

## Testing Responsive

- Test on real devices—emulators miss real performance and touch targets
- Test with real content—long words, missing images, user-generated text
- Test both orientations—landscape tablet is not the same as desktop
- Check over-scroll behavior—pull-to-refresh, bounce effects
