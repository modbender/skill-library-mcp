---
title: Provide stable keys for list items
impact: MEDIUM
source: ohos_react_native performance optimization - Add key to list items
---

# rnoh-list-key

When rendering a list with map, provide a **stable, unique** key for each item. Avoid using the array index as key, especially when the list order can change.

## Incorrect

```javascript
{items.map((item, index) => (
  <Child key={index} age={item.age} />
))}
// If items are inserted/removed at the head, indices shift and cause unnecessary re-renders and state bugs
```

## Correct

```javascript
{items.map((item) => (
  <Child key={item.id} age={item.age} />
))}
```

## Note

- Keys are used by React for diffing and reuse; unstable keys can cause list flicker, wrong state, and worse performance.
- Same applies with FlatList/ScrollView and other list components in React Native for OpenHarmony.
