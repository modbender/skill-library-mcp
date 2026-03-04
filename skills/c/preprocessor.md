# Preprocessor Traps

- `#define MAX(a,b) a>b?a:b` — `MAX(x,y)+1` breaks, need outer parens
- `#define SQ(x) (x)*(x)` — `SQ(i++)` evaluates i++ twice
- Missing include guards — multiple inclusion, redefinition errors
- `#if MACRO` when MACRO undefined — treated as 0, not error
- Macro expanding to multiple statements — wrap in `do { } while(0)`
- `#define FOO` vs `#define FOO 1` — `#if FOO` vs `#ifdef FOO` behavior
- Stringify `#x` and paste `a##b` — require extra macro layer for expansion
