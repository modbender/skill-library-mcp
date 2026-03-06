# MML Elements — Full Attribute Reference

## Table of Contents
- [m-group](#m-group)
- [m-cube](#m-cube)
- [m-sphere](#m-sphere)
- [m-cylinder](#m-cylinder)
- [m-plane](#m-plane)
- [m-model](#m-model)
- [m-character](#m-character)
- [m-light](#m-light)
- [m-image](#m-image)
- [m-video](#m-video)
- [m-audio](#m-audio)
- [m-label](#m-label)
- [m-frame](#m-frame)
- [m-link](#m-link)
- [m-prompt](#m-prompt)
- [m-interaction](#m-interaction)
- [m-position-probe](#m-position-probe)
- [m-chat-probe](#m-chat-probe)
- [m-attr-anim](#m-attr-anim)
- [m-attr-lerp](#m-attr-lerp)

---

## Shared Transform Attributes (all visible elements)

| Attr | Type | Default | Description |
|------|------|---------|-------------|
| `x` | float | 0 | Position X (meters) |
| `y` | float | 0 | Position Y (meters) |
| `z` | float | 0 | Position Z (meters) |
| `rx` | float | 0 | Rotation X (degrees) |
| `ry` | float | 0 | Rotation Y (degrees) |
| `rz` | float | 0 | Rotation Z (degrees) |
| `sx` | float | 1 | Scale X |
| `sy` | float | 1 | Scale Y |
| `sz` | float | 1 | Scale Z |
| `visible` | bool | true | Show/hide |
| `debug` | bool | false | Show debug axes |
| `socket` | string | — | Bone name to attach to (Web only) |
| `id` | string | — | Unique identifier |
| `class` | string | — | Space-separated class names |

## Shared Collision Attributes (primitives, m-model, m-character, m-image, m-video)

| Attr | Type | Default | Description |
|------|------|---------|-------------|
| `collide` | bool | true | Participate in collision detection |
| `collision-interval` | int | — | Ms between collision checks (required to enable events) |
| `oncollisionstart` | script | — | On collision start |
| `oncollisionmove` | script | — | On collision move |
| `oncollisionend` | script | — | On collision end |

---

## m-group
Container for grouping/transforming children as a unit.
- Transform attrs only + `onclick`

## m-cube
3D box primitive.

| Attr | Type | Default |
|------|------|---------|
| `width` | float | 1 (meters) |
| `height` | float | 1 (meters) |
| `depth` | float | 1 (meters) |
| `color` | string | "white" |
| `opacity` | float | 1 |
| `cast-shadows` | bool | true |
+ Transform, Collision, `onclick`

## m-sphere
3D sphere primitive.

| Attr | Type | Default |
|------|------|---------|
| `radius` | float | 0.5 (meters) |
| `color` | string | "white" |
| `opacity` | float | 1 |
| `cast-shadows` | bool | true |
+ Transform, Collision, `onclick`

## m-cylinder
3D cylinder primitive.

| Attr | Type | Default |
|------|------|---------|
| `radius` | float | 0.5 (meters) |
| `height` | float | — |
| `color` | string | "white" |
| `opacity` | float | 1 |
| `cast-shadows` | bool | true |
+ Transform, Collision, `onclick`

## m-plane
Flat plane primitive.

| Attr | Type | Default |
|------|------|---------|
| `width` | float | 1 (meters) |
| `height` | float | 1 (meters) |
| `color` | string | "white" |
| `opacity` | float | 1 |
| `cast-shadows` | bool | true |
+ Transform, Collision, `onclick`

## m-model
Load external 3D model (GLTF, OBJ, FBX).

| Attr | Type | Default |
|------|------|---------|
| `src` | string | — (URI to model file) |
| `anim-src` | string | — (URI to animation file) |
| `anim-loop` | bool | true |
| `anim-enabled` | bool | true |
| `start-time` | int | 0 (ms) |
| `pause-time` | int | — |
| `cast-shadows` | bool | true |
+ Transform, Collision, `onclick`

## m-character
3D character. Can contain `m-model` children for composition.

| Attr | Type | Default |
|------|------|---------|
| `src` | string | — (URI to character model) |
| `anim-src` | string | — (URI to animation) |
| `anim-loop` | bool | true |
| `anim-enabled` | bool | true |
| `start-time` | int | 0 (ms) |
| `pause-time` | int | — |
| `cast-shadows` | bool | true |
+ Transform, Collision, `onclick`

## m-light
Point or spotlight.

| Attr | Type | Default |
|------|------|---------|
| `type` | enum | "point" ("point" or "spotlight") |
| `intensity` | float | 1 (candela) |
| `distance` | float | 0 (0 = infinite) |
| `angle` | float | 45 (degrees, spotlight only) |
| `enabled` | bool | true |
| `cast-shadows` | bool | true |
| `color` | string | "white" |
+ Transform, `onclick`

## m-image
Display image in 3D.

| Attr | Type | Default |
|------|------|---------|
| `src` | string | — (URI) |
| `width` | float | 1 (meters) |
| `height` | float | 1 (meters) |
| `emissive` | float | 0 |
| `opacity` | float | 1 |
| `cast-shadows` | bool | true |
+ Transform, Collision

## m-video
Display video in 3D. Supports WHEP streaming (use `whep://` protocol).

| Attr | Type | Default |
|------|------|---------|
| `src` | string | — (URI or whep://) |
| `width` | float | 1 (meters) |
| `height` | float | 1 (meters) |
| `emissive` | float | 0 |
| `loop` | bool | true |
| `enabled` | bool | true |
| `volume` | float | 1 |
| `start-time` | int | 0 (ms) |
| `pause-time` | int | — |
| `cast-shadows` | bool | true |
+ Transform, Collision

## m-audio
Spatial audio source.

| Attr | Type | Default |
|------|------|---------|
| `src` | string | — (URI) |
| `loop` | bool | true |
| `loop-duration` | float | — (seconds, Web only) |
| `enabled` | bool | true |
| `volume` | float | 1 |
| `cone-angle` | float | 360 (degrees, Web only) |
| `cone-falloff-angle` | float | 0 (Web only) |
| `start-time` | int | 0 (ms) |
| `pause-time` | int | — |
+ Transform

## m-label
Text displayed on a plane.

| Attr | Type | Default |
|------|------|---------|
| `content` | string | — |
| `width` | float | 1 (meters) |
| `height` | float | 1 (meters) |
| `emissive` | float | 0 |
| `font-size` | float | 24 (centimeters) |
| `font-color` | string | "black" |
| `padding` | float | 8 (centimeters) |
| `alignment` | enum | "left" ("left", "center", "right") |
| `color` | string | "white" (background) |
| `cast-shadows` | bool | true |
+ Transform, `onclick`

## m-frame
Embed another MML document. Supports content bounds and distance-based loading.

| Attr | Type | Default |
|------|------|---------|
| `src` | string | — (URI to MML doc) |
| `min-x` | float | — (Web only) |
| `max-x` | float | — (Web only) |
| `min-y` | float | — (Web only) |
| `max-y` | float | — (Web only) |
| `min-z` | float | — (Web only) |
| `max-z` | float | — (Web only) |
| `load-range` | float | — (meters, Web only) |
| `unload-range` | float | 1 (meters, Web only) |
+ Transform

## m-link
Open URL on click. No visual — children are clickable. **Web only.**

| Attr | Type | Default |
|------|------|---------|
| `href` | string | — |
| `target` | string | "_blank" ("_self" or "_blank") |
+ Transform

## m-prompt
Text input dialog on click.

| Attr | Type | Default |
|------|------|---------|
| `message` | string | — |
| `placeholder` | string | — |
| `prefill` | string | — |
| `onprompt` | script | — |
+ Transform

## m-interaction
Contextual action at a point in space.

| Attr | Type | Default |
|------|------|---------|
| `range` | float | 5 (meters) |
| `in-focus` | bool | true (Web only) |
| `line-of-sight` | bool | false (Web only) |
| `priority` | int | 1 |
| `prompt` | string | — |
| `oninteract` | script | — |
+ Transform

## m-position-probe
Track user positions within range.

| Attr | Type | Default |
|------|------|---------|
| `range` | float | 10 (meters) |
| `interval` | int | 1000 (ms) |
| `onpositionenter` | script | — |
| `onpositionmove` | script | — |
| `onpositionleave` | script | — |
+ Transform

## m-chat-probe
Receive chat messages from nearby users.

| Attr | Type | Default |
|------|------|---------|
| `range` | float | 1 (meters) |
| `onchat` | script | — |
+ Transform

## m-attr-anim
Document-time-synchronized keyframe animation. Place as child of target element.

| Attr | Type | Default |
|------|------|---------|
| `attr` | string | — (parent attribute to animate) |
| `start` | string | — (start value) |
| `end` | string | — (end value) |
| `start-time` | int | 0 (ms) |
| `pause-time` | int | — |
| `duration` | int | 1000 (ms) |
| `loop` | bool | true |
| `easing` | enum | — (linear if omitted) |
| `ping-pong` | bool | false |
| `ping-pong-delay` | int | 0 (ms, part of duration) |

## m-attr-lerp
Smooth transitions when attributes change. Place as child. **Web only.**

| Attr | Type | Default |
|------|------|---------|
| `attr` | string | — (comma-separated attrs, or "all") |
| `duration` | int | 1000 (ms) |
| `easing` | enum | — (linear if omitted) |
