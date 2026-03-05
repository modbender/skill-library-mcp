## Setup

### tsconfig.json

```json
{
  "compilerOptions": {
    "paths": {
      "@aioz-ui/core-v3/*": ["../../packages/aioz-ui/packages/core-v3/src/*"],
      "@aioz-ui/icon-react": [
        "../../packages/aioz-ui/packages/icon-react/src/lucide-react.suffixed"
      ]
    }
  }
}
```

### package.json

```json
{
  "dependencies": {
    "@aioz-ui/core-v3": "workspace:^",
    "@aioz-ui/icon-react": "workspace:^"
  }
}
```

### globals.css

```css
@import 'tailwindcss';
@import '../../packages/aioz-ui/packages/core/src/styles/__index.css';
@custom-variant dark (&:is(.dark *));
```

All components import from `@aioz-ui/core-v3/components`.
Icons import from `@aioz-ui/icon-react`.

---
