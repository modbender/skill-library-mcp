# DOM Observer Pro

## Metadata
- **ID**: dom-observer-pro
- **Version**: 1.0.0
- **Category**: utility
- **Priority**: Medium
- **Installation**: ClawHub
- **Package**: `@raghulpasupathi/dom-observer-pro`

## Description
Efficient DOM monitoring system for real-time content detection in web browsers. Uses MutationObserver, IntersectionObserver, and intelligent debouncing to detect AI-generated content as it appears on web pages with minimal performance impact.

## Installation

### Via ClawHub
```
https://clawhub.ai/raghulpasupathi/dom-observer-pro
```

### Via npm
```bash
npm install @raghulpasupathi/dom-observer-pro
```

## Features
- **Real-time Monitoring**: Detect content changes instantly
- **Mutation Observation**: Track DOM modifications efficiently
- **Intersection Detection**: Monitor when elements enter viewport
- **Intelligent Debouncing**: Prevent performance degradation from rapid changes
- **Selector Targeting**: Watch specific elements or patterns
- **Content Extraction**: Automatically extract text/images from new elements
- **Shadow DOM Support**: Monitor elements within shadow roots
- **Performance Optimized**: Batched processing and throttling
- **Browser Extension Ready**: Designed for extension environments
- **Configurable Filters**: Ignore irrelevant changes

## Configuration
```json
{
  "enabled": true,
  "settings": {
    "observeMode": "mutation",
    "targetSelectors": [
      "article",
      "p",
      "div.content",
      "span.text",
      ".comment",
      ".post"
    ],
    "ignoreSelectors": [
      "script",
      "style",
      "noscript",
      ".ads",
      ".navigation"
    ],
    "mutation": {
      "enabled": true,
      "childList": true,
      "subtree": true,
      "characterData": true
    },
    "intersection": {
      "enabled": true,
      "threshold": 0.5,
      "rootMargin": "50px"
    },
    "performance": {
      "debounceDelay": 300,
      "throttleDelay": 100,
      "batchSize": 10,
      "maxQueueSize": 100
    },
    "extraction": {
      "minTextLength": 50,
      "maxTextLength": 10000,
      "extractImages": true,
      "extractLinks": true
    }
  }
}
```

## API Examples

See [dom-observer-pro-examples.js](./examples/dom-observer-pro-examples.js) for complete usage examples.

## Dependencies
- **mutation-observer**: Built-in browser API
- **intersection-observer**: Built-in browser API
- **debounce**: ^2.0.0
- **lodash.throttle**: ^4.1.1

## Performance
- **CPU Usage**: <1% idle, 2-5% during active monitoring
- **Memory**: 10-20MB for typical web pages
- **Latency**: <10ms detection, 100-500ms with debouncing
- **Throughput**: Handles 1000+ DOM changes/second
- **Browser Compatibility**: Chrome 51+, Firefox 14+, Safari 10+

## Use Cases
- Browser extensions for AI detection
- Social media content monitoring
- News site article tracking
- Chat application message detection
- Dynamic content tracking
- Content moderation systems
- Data collection from SPAs
- User behavior tracking

## Best Practices
1. Use specific `targetSelectors` to reduce noise
2. Always define `ignoreSelectors` for ads, navigation, etc.
3. Set appropriate `debounceDelay` to balance speed vs performance
4. Use IntersectionObserver for content in long pages
5. Implement batch processing for high-frequency changes
6. Call `stop()` when observer is no longer needed
7. Use WeakSet to track processed elements
8. Monitor performance metrics regularly
9. Handle errors gracefully to prevent observer failure
10. Test across different websites and frameworks
