# Blade Traps

- `{!! $html !!}` skips escaping — XSS injection vector, use `{{ }}` by default
- `{{ $var }}` on null — prints empty, use `{{ $var ?? 'default' }}`
- `@json($data)` in attribute — still need quotes: `data-x='@json($data)'`
- Component slot `$slot` always exists — but may be empty, check `$slot->isEmpty()`
- `@include` missing view — throws exception, use `@includeIf` for optional
- Inline component props — `<x-alert :type="$type">` needs colon for PHP expression
- `@stack` vs `@push` order — pushed content renders in push order, not stack location
