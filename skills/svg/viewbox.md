# viewBox — Critical Scaling Traps

## viewBox vs width/height

```svg
<!-- ✅ Scales to any container size -->
<svg viewBox="0 0 24 24">
  <circle cx="12" cy="12" r="10"/>
</svg>

<!-- ❌ Fixed 24x24, never scales -->
<svg width="24" height="24">
  <circle cx="12" cy="12" r="10"/>
</svg>
```

**Rule:** Always include viewBox. Remove fixed `width`/`height` for responsive SVGs.

## Coordinates Must Match viewBox

Elements outside viewBox bounds are **invisible**:

```svg
<!-- ❌ Circle at 500,500 but viewBox only covers 0-100 -->
<svg viewBox="0 0 100 100">
  <circle cx="500" cy="500" r="40"/>  <!-- invisible -->
</svg>
```

## viewBox Is Unitless

```svg
<!-- ❌ WRONG — units break viewBox -->
<svg viewBox="0 0 100px 100px">

<!-- ✅ Correct — no units -->
<svg viewBox="0 0 100 100">
```

## preserveAspectRatio Traps

Default `xMidYMid meet` is usually correct. Only override with intent:

```svg
<!-- Stretches/distorts the SVG -->
<svg viewBox="0 0 100 50" preserveAspectRatio="none">
```

**Common trap:** Setting `none` to "fix" sizing issues instead of fixing viewBox.

## Figma/Illustrator Export Trap

Exports often include viewBox offset from artboard position:

```svg
<!-- ❌ Exported with offset -->
<svg viewBox="234 567 100 100">

<!-- ✅ Normalized -->
<svg viewBox="0 0 100 100">
```

Always normalize viewBox to `0 0 width height` unless offset is intentional.
