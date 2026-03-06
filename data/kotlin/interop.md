# Java Interop & Common Mistakes

## Common Mistakes

- `==` is structural equality in Kotlin — `===` for reference, opposite of Java
- String templates: `"$var"` or `"${expr}"` — no concatenation needed
- `lateinit` can't be primitive — use `by lazy` for computed initialization
- `object` is singleton — `companion object` for static-like members, not instance
- SAM conversion only for Java interfaces — Kotlin interfaces need explicit `fun interface`

## Java Interop Annotations

- `@JvmStatic` for companion methods callable as static — without it, need `Companion.method()`
- `@JvmOverloads` generates overloads for default params — Java doesn't see defaults otherwise
- `@JvmField` exposes property as field — without getter/setter for Java callers
- Nullability annotations propagate — annotate Java code for Kotlin safety
