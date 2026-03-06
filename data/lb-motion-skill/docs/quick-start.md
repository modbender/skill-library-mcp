# Get started with Motion

Motion is an animation library that's easy to start and fun to master.

Its unique hybrid engine combines the performance of the browser with the limitless potential of a JavaScript engine. This means you can animate anything, like:

- HTML/CSS
- SVG (like path drawing animations)
- WebGL (3D graphics)

The best part? It's also tiny, with a mini HTML/SVG version of the animate() function that's just 2.3kb!

## Install

### Package manager

Motion can be installed via the "motion" package.

```bash
npm install motion
```

Then imported in your JavaScript:

```javascript
import { animate, scroll } from "motion"
```

### Script tag

Import using the modern import syntax:

```html
<script type="module">
  import { animate, scroll } from "https://cdn.jsdelivr.net/npm/motion@latest/+esm"
</script>
```

Or you can add Motion as a global variable:

```html
<script src="https://cdn.jsdelivr.net/npm/motion@latest/dist/motion.js"></script>
<script>
  const { animate, scroll } = Motion
</script>
```

## Create an animation

The "Hello world!" of any animation library is a simple transform animation.

```javascript
import { animate } from "motion"

// CSS selector
animate(".box", { rotate: 360 })

// Elements
const boxes = document.querySelectorAll(".box")
animate(boxes, { rotate: 360 })
```

## What can be animated?

Motion lets you animate anything:

- CSS properties (like opacity, transform and filter)
- SVG attributes and paths
- Independent transforms (x, rotateY etc)
- JavaScript objects (containing strings/colors/numbers)

With Motion, you don't have to worry about achieving the best performance available. When a value can be hardware accelerated, like opacity, filter or transform, it will be.

animate isn't limited to HTML. It can animate single values or any kind of object. For example, the rotation of a Three.js object:

```javascript
animate(
  cube.rotation,
  { y: rad(360), z: rad(360) },
  { duration: 10, repeat: Infinity, ease: "linear" }
)
```

## Customising animations

Motion comes with smart defaults, so your animations should look and feel great out of the box. But you can further tweak options like:

- Duration (how long the animation lasts)
- Delay (how long it waits before starting)
- Easing (how it speeds up and slows down)
- Repeat (how it repeats, how many times, etc)

```javascript
animate(
  element,
  { scale: [0.4, 1] },
  { ease: "circInOut", duration: 1.2 }
);
```

Motion also has amazing spring animations for natural, kinetic animations:

```javascript
animate(
  element,
  { rotate: 90 },
  { type: "spring", stiffness: 300 }
);
```

## Stagger animations

When animating multiple elements, it can feel more natural or lively to offset the animations of each. This is called staggering.

Motion provides a stagger function that can be used to dynamically set delay:

```javascript
import { animate, stagger } from "motion"

animate(
  "li",
  { y: 0, opacity: 1 },
  { delay: stagger(0.1) }
)
```

## What's next?

- Keyframes and sequences: Create more complex animations
- Controls: Pause, resume or change animations
- Scroll-linked animations: Link values to scroll position
- Scroll-triggered animations: Trigger animations when elements enter the viewport
