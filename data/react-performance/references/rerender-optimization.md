# Re-render Optimization

## Derive State During Render — Not in Effects (MEDIUM)

If a value can be computed from current props/state, derive it inline.

```tsx
// BAD — redundant state + effect
const [fullName, setFullName] = useState('')
useEffect(() => {
  setFullName(firstName + ' ' + lastName)
}, [firstName, lastName])

// GOOD — derive during render
const fullName = firstName + ' ' + lastName
```

Reference: [You Might Not Need an Effect](https://react.dev/learn/you-might-not-need-an-effect)

## Functional setState for Stable Callbacks (MEDIUM)

Use functional updates to prevent stale closures and eliminate state
dependencies from callbacks.

```tsx
// BAD — requires state dependency, risk of stale closure
const addItems = useCallback((newItems: Item[]) => {
  setItems([...items, ...newItems])
}, [items])

// GOOD — stable callback, always latest state
const addItems = useCallback((newItems: Item[]) => {
  setItems((curr) => [...curr, ...newItems])
}, [])
```

Benefits: stable callback references, no stale closures, fewer dependencies.

Use functional updates when: state depends on current value, inside
useCallback/useMemo, in event handlers, in async operations.
Direct updates fine for: static values (`setCount(0)`), props-only (`setName(newName)`).

## Defer State Reads to Usage Point (MEDIUM)

Don't subscribe to dynamic state if you only read it inside callbacks.

```tsx
// BAD — subscribes to all searchParams changes
const searchParams = useSearchParams()
const handleShare = () => {
  const ref = searchParams.get('ref')
  shareChat(chatId, { ref })
}

// GOOD — reads on demand, no subscription
const handleShare = () => {
  const params = new URLSearchParams(window.location.search)
  shareChat(chatId, { ref: params.get('ref') })
}
```

## Lazy State Initialization (MEDIUM)

Pass a function to `useState` for expensive initial values.

```tsx
// BAD — runs on every render
const [settings, setSettings] = useState(
  JSON.parse(localStorage.getItem('settings') || '{}')
)

// GOOD — runs only once
const [settings, setSettings] = useState(() =>
  JSON.parse(localStorage.getItem('settings') || '{}')
)
```

Use for: localStorage/sessionStorage reads, building data structures, DOM reads,
heavy transformations. Skip for: `useState(0)`, `useState(props.value)`.

## Subscribe to Derived Booleans (MEDIUM)

Subscribe to derived booleans instead of continuous values to reduce re-renders.

```tsx
// BAD — re-renders on every pixel
const width = useWindowWidth()
const isMobile = width < 768

// GOOD — re-renders only when boolean flips
const isMobile = useMediaQuery('(max-width: 767px)')
```

## Use Transitions for Non-Urgent Updates (MEDIUM)

Mark frequent, non-urgent updates as transitions.

```tsx
import { startTransition } from 'react'

// BAD — blocks UI on every scroll
const handler = () => setScrollY(window.scrollY)

// GOOD — non-blocking
const handler = () => startTransition(() => setScrollY(window.scrollY))
```

## Extract to Memoized Components (MEDIUM)

Extract expensive work into memoized components to enable early returns.

```tsx
const UserAvatar = memo(function UserAvatar({ user }: { user: User }) {
  const id = useMemo(() => computeAvatarId(user), [user])
  return <Avatar id={id} />
})

function Profile({ user, loading }: Props) {
  if (loading) return <Skeleton />
  return <div><UserAvatar user={user} /></div>
}
```

Note: React Compiler makes manual `memo()`/`useMemo()` unnecessary.
