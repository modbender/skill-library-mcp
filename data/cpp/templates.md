# Template Traps

- Two-phase lookup — dependent names need `typename`/`this->` 
- Template in header — definition must be visible, not in .cpp
- SFINAE failure — substitution failure is not error, but confusing messages
- Argument deduction — `template<class T> void f(T)` deduces from args
- `>>` in nested templates — before C++11 needed space `> >`
- Static members — each instantiation has own static, not shared
- Explicit instantiation — `template class MyClass<int>;` forces compile
- Concepts (C++20) — `requires` constraints, better than SFINAE
