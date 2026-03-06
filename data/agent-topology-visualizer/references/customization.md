# Customization Guide

## Custom CSS

Add a `css` field to your topology JSON to inject custom styles into the output:

```json
{
  "css": ".arch-svg { filter: saturate(1.2); }"
}
```

The CSS is injected into a `<style>` block inside the HTML output. Only use CSS you've written or reviewed.

## Embedding in Existing Pages

Use `--format svg` to get just the SVG element, then embed it in your own page:

```html
<div class="my-diagram-container">
  <!-- paste SVG output here -->
</div>
```

The `--format paths` option outputs only the `<path>` elements for injection into an existing SVG.

## Background Options

The default dark theme includes a constellation-style star field. Control it with:

```json
{
  "background": {
    "stars": true,
    "starCount": 150,
    "starColor": "rgba(200,214,224,0.3)"
  }
}
```

Set `"stars": false` to disable the star field for embedding in pages with their own background.
