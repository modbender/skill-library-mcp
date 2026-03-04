# JavaScript Patterns and Traps

## Type Coercion

- **`==` vs `===`** — Always use `===`; `"0" == false` is true, `"0" === false` is false
- **`typeof null`** — Returns `"object"` (bug from JS v1); check with `=== null`
- **`NaN !== NaN`** — Use `Number.isNaN()` not `=== NaN`
- **Array in boolean context** — Empty array `[]` is truthy; check `.length` for emptiness

## Async

- **`forEach` doesn't await** — Use `for...of` loop or `Promise.all(arr.map(async...))` for parallel
- **Unhandled rejection** — Always `.catch()` or wrap in try/catch; uncaught rejections crash Node
- **`async` function returns Promise** — Even if you return a value, caller gets a Promise
- **Race conditions** — Multiple `setState` calls can overwrite; use functional updates or refs

## DOM

- **`querySelector` returns null** — Check before accessing properties; `document.querySelector('.x').classList` crashes if `.x` missing
- **Event delegation** — Add listener to parent, check `e.target`; better than listeners on each child
- **`innerHTML` security** — Never insert user content with `innerHTML`; use `textContent` or sanitize
- **Live vs static NodeLists** — `getElementsByClassName` is live (updates); `querySelectorAll` is static

## Objects/Arrays

- **Shallow copy** — `{...obj}` and `[...arr]` are shallow; nested objects share references
- **Array holes** — `Array(5)` creates holes; `.map()` skips them; use `Array(5).fill()` instead
- **`delete` on array** — Creates hole, doesn't shift; use `.splice()` to remove elements
- **Object key order** — Guaranteed insertion order for string keys; numeric keys sort ascending

## Functions

- **`this` in arrow functions** — Lexically bound; can't be changed with `.bind()`, `.call()`, `.apply()`
- **Default parameters evaluate** — `fn(x = Date.now())` evaluates on each call, not definition
- **Rest parameters must be last** — `fn(...rest, other)` is syntax error
