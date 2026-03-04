# Motion.dev Documentation Skill

Complete documentation for Motion.dev (formerly Framer Motion) - a modern animation library for React, JavaScript, and Vue.

## What is Motion?

Motion is a powerful animation library that combines:
- **Performance**: Hardware-accelerated animations
- **Size**: Just 2.3kb for core functionality
- **Flexibility**: Animate HTML, SVG, WebGL, and JavaScript objects
- **Ease of use**: Intuitive API with smart defaults

## Installation

```bash
npm install motion
```

## Quick Examples

### Vanilla JavaScript

```javascript
import { animate } from "motion"

animate(".box", {
  rotate: 360,
  scale: 1.2
})
```

### React

```jsx
import { motion } from "motion/react"

<motion.div
  animate={{ x: 100 }}
  transition={{ type: "spring" }}
/>
```

### Scroll Animations

```javascript
import { scroll } from "motion"

scroll(animate(".parallax", {
  transform: ["translateY(0px)", "translateY(200px)"]
}))
```

## Key Features

- ✅ Spring physics for natural motion
- ✅ Scroll-linked and scroll-triggered animations
- ✅ Gesture support (drag, hover, tap)
- ✅ Layout animations
- ✅ SVG path animations
- ✅ Stagger effects
- ✅ Timeline sequences
- ✅ Performance optimizations

## Documentation

See `docs/` folder for comprehensive guides:
- `quick-start.md` - Getting started guide
- More coming soon...

## External Resources

- 🌐 Official site: https://motion.dev
- 📦 GitHub: https://github.com/motiondivision/motion
- 📚 Examples: https://motion.dev/examples
- 💬 Discord: https://discord.gg/motion

## Version

Motion Documentation Skill v1.0.0
