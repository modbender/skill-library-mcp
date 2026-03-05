---
title: Use PureComponent / React.memo to avoid unnecessary re-renders
impact: HIGH
source: ohos_react_native performance optimization - Render optimization
---

# rnoh-render-pure-memo

When props or state have not changed, avoid running render again to reduce JS and Fabric cost in RNOH.

## Incorrect

```javascript
// Child re-renders on every parent setState even when props are unchanged
class Child extends React.Component {
  render() {
    console.log('child render');
    return <Text>{this.props.text}</Text>;
  }
}
export default class App extends React.Component {
  state = { count: 0 };
  increment = () => {
    const newCount = count < 5 ? count + 1 : count;
    this.setState({ count: newCount });
  };
  render() {
    return (
      <>
        <Text>{this.state.count}</Text>
        <Child text="static" />
        <Button title="+" onPress={this.increment} />
      </>
    );
  }
}
```

## Correct

**Class: PureComponent**

```javascript
class Child extends React.PureComponent {
  render() {
    return <Text>{this.props.text}</Text>;
  }
}
```

**Function: React.memo**

```javascript
const Child = React.memo((props) => {
  return <Text>{props.text}</Text>;
});
// Optional custom compare
const Child2 = React.memo((props) => <Text>{props.text}</Text>, (prev, next) => prev.text === next.text);
```

## Notes

- PureComponent only does **shallow comparison**; deep property or same-reference mutations may not trigger updates.
- Prefer **new objects** in setState; do not mutate existing state by reference.
