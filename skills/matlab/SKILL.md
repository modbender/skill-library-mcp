---
name: MATLAB
description: Avoid common MATLAB mistakes — indexing traps, matrix vs element-wise ops, and vectorization pitfalls.
metadata: {"clawdbot":{"emoji":"📐","requires":{"bins":["matlab"]},"os":["linux","darwin","win32"]}}
---

## Indexing
- 1-based indexing — first element is `A(1)`, not `A(0)`
- `end` keyword for last index — `A(end)`, `A(end-1)`, works in any dimension
- Linear indexing on matrices — `A(5)` accesses 5th element column-major order
- Logical indexing returns vector — `A(A > 0)` gives 1D result regardless of A's shape

## Matrix vs Element-wise
- `*` is matrix multiplication — `.*` for element-wise
- `/` solves `A*x = B` — `./` for element-wise division
- `^` is matrix power — `.^` for element-wise power
- Forgetting the dot is silent bug — dimensions might accidentally match

## Vector Shape Matters
- Row vector: `[1 2 3]` or `[1, 2, 3]` — shape is 1×3
- Column vector: `[1; 2; 3]` — shape is 3×1
- Transpose with `'` (conjugate) or `.'` (non-conjugate) — for complex, they differ
- `*` between row and column gives scalar or matrix — depending on order

## Array Preallocation
- Growing arrays in loops is slow — preallocate: `A = zeros(1000, 1)`
- `zeros`, `ones`, `nan` for preallocation — specify size upfront
- Cell arrays: `cell(n, m)` — preallocate cells too

## Broadcasting
- Implicit expansion since R2016b — `A + b` works if dimensions compatible
- Singleton dimensions expand — `[1;2;3] + [10 20]` gives 3×2
- Before R2016b needed `bsxfun` — legacy code may still use it

## NaN Handling
- `NaN ~= NaN` is true — use `isnan()` to check
- Most operations propagate NaN — `sum([1 NaN 3])` is NaN
- Use `'omitnan'` flag — `sum(A, 'omitnan')`, `mean(A, 'omitnan')`

## Cell Arrays vs Matrices
- `{}` for cell arrays — hold mixed types, different sizes
- `()` indexing returns cell — `C(1)` is 1×1 cell
- `{}` indexing extracts content — `C{1}` is the actual value
- Comma-separated list from `C{:}` — useful for function arguments

## Common Mistakes
- `=` for assignment, `==` for comparison — `if x = 5` is error in MATLAB
- Semicolon suppresses output — forget it and flood command window
- `clear` removes all variables — use `clearvars` for selective, `close all` for figures
- `i` and `j` are imaginary unit — don't use as loop variables, or reassign explicitly
- String vs char: `"text"` vs `'text'` — double quotes are string arrays (R2017a+)

## Functions
- Anonymous functions: `f = @(x) x^2` — quick inline functions
- Multiple outputs: `[a, b] = func()` — must capture or use `~` to ignore
- `nargin`/`nargout` for optional args — check how many inputs/outputs provided
- `varargin`/`varargout` for variable args — cell array of extra arguments

## Debugging
- `dbstop if error` — breakpoint on any error
- `keyboard` in code pauses execution — enter debug mode at that line
- `whos` shows variable sizes — `size(A)` for specific variable
