# Embedding Reference

How to embed UNITH digital humans in websites and applications.

---

## Quick Embed (iframe)

The simplest way to embed a digital human. Use the `publicUrl` from creation:

```html
<iframe
  src="https://app.unith.ai/s/<publicId>"
  width="400"
  height="600"
  frameborder="0"
  allow="camera; microphone; autoplay"
  allowfullscreen>
</iframe>
```

### Required permissions

The `allow` attribute must include:
- `camera` — if the digital human uses video input
- `microphone` — for voice-based conversation
- `autoplay` — for the avatar to start speaking

---

## JavaScript Widget

For more control, use the UNITH JavaScript widget:

```html
<div id="unith-avatar"></div>

<script src="https://cdn.unith.ai/widget/latest/unith-widget.js"></script>
<script>
  UnithWidget.init({
    containerId: 'unith-avatar',
    publicId: '<publicId>',
    width: 400,
    height: 600,
    autoStart: true,
    onReady: function() {
      console.log('Digital human is ready');
    },
    onMessage: function(message) {
      console.log('Avatar said:', message.text);
    }
  });
</script>
```

### Widget Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `containerId` | string | required | ID of the DOM element to render into |
| `publicId` | string | required | The digital human's public ID |
| `width` | number | `400` | Widget width in pixels |
| `height` | number | `600` | Widget height in pixels |
| `autoStart` | boolean | `false` | Start conversation automatically on load |
| `onReady` | function | `null` | Callback when the widget is fully loaded |
| `onMessage` | function | `null` | Callback when the avatar sends a message |
| `onError` | function | `null` | Callback on errors |

---

## React Component

```jsx
import { useEffect, useRef } from 'react';

function UnithAvatar({ publicId, width = 400, height = 600 }) {
  const containerRef = useRef(null);

  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://cdn.unith.ai/widget/latest/unith-widget.js';
    script.onload = () => {
      window.UnithWidget.init({
        containerId: containerRef.current.id,
        publicId,
        width,
        height,
        autoStart: true,
      });
    };
    document.head.appendChild(script);

    return () => {
      if (window.UnithWidget?.destroy) {
        window.UnithWidget.destroy();
      }
      document.head.removeChild(script);
    };
  }, [publicId, width, height]);

  return <div id="unith-avatar-container" ref={containerRef} />;
}

export default UnithAvatar;
```

---

## Responsive Embedding

For mobile-friendly layouts:

```html
<style>
  .unith-wrapper {
    position: relative;
    width: 100%;
    max-width: 400px;
    margin: 0 auto;
  }
  .unith-wrapper iframe {
    width: 100%;
    height: 600px;
    border: none;
    border-radius: 12px;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.12);
  }
  @media (max-width: 480px) {
    .unith-wrapper iframe {
      height: 100vh;
      border-radius: 0;
    }
  }
</style>

<div class="unith-wrapper">
  <iframe
    src="https://app.unith.ai/s/<publicId>"
    allow="camera; microphone; autoplay"
    allowfullscreen>
  </iframe>
</div>
```

---

## Content Security Policy

If your site uses CSP headers, add these directives:

```
frame-src https://app.unith.ai;
script-src https://cdn.unith.ai;
connect-src https://platform-api.unith.ai;
```
