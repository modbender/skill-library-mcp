---
title: Create props/callbacks once (constructor or outside component)
impact: HIGH
source: ohos_react_native performance optimization - Create prop objects once
---

# rnoh-render-props-once

If the parent creates a new callback or style object on every render and passes it to a child, the child will re-render (even with PureComponent/memo) because props reference changed. Bind in the constructor or use a stable reference; move style objects to StyleSheet or module-level constants.

## Incorrect

```javascript
// New function every render → Child re-renders every time
<Child onPress={() => console.log('click')} />

// New object every render
<Child style={{ marginTop: 10 }} />
```

## Correct

```javascript
constructor(props) {
  super(props);
  this.onBindClick = this.clickAction.bind(this);
}
clickAction = () => { console.log('click'); };
// ...
<Child onPress={this.onBindClick} />
// Or useCallback for function components
const handlePress = useCallback(() => { console.log('click'); }, []);
```

Use StyleSheet.create or constants for style.

## Note

- Aligns with vercel-react-native-skills `list-performance-inline-objects` and `list-performance-callbacks`; applies to OpenHarmony React Native and affects Fabric and JS thread.
