---
title: Merge setState to reduce render count
impact: HIGH
source: ohos_react_native performance optimization - Merge setState
---

# rnoh-render-merge-setstate

Multiple setState calls can cause multiple renders. When updating before/after a request or from multiple async results, merge into a single setState where possible.

## Incorrect

```javascript
this.setState({ totalLength: 0 }, () => {
  this.setState({ loading: true });
  getData().then(res => {
    this.setState({ list: res });
  });
});

// Each async calls setState separately
getMeeting().then(info => this.setState({ info }));
getUserList().then(userList => this.setState({ userList }));
```

## Correct

```javascript
this.setState(
  { totalLength: 0, loading: true },
  () => {
    getData().then(res => this.setState({ list: res }));
  }
);

Promise.all([getMeeting(), getUserList()]).then(([info, userList]) => {
  this.setState({ info, userList });
});
```

## Note

- With React 18, RNOH enables Automatic Batching; setState in the same event loop may be batched, but setState inside async callbacks can still cause multiple renders—prefer explicit merging.
- This rule is for static checks and code review of OpenHarmony React Native apps.
