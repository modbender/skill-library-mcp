# Views Traps

- `<%= @user.bio %>` escapes HTML — use `raw` or `html_safe` only for trusted content
- `render partial:` in loop — N+1 renders, use `render collection:` instead
- `cache @model` with STI — subclasses share cache, add `@model.class.name` to key
- `content_for :x` in partial — only works if layout yields `:x` after partial renders
- Helper methods return nil — ERB outputs "nil" string, use `return ""` explicitly
- `link_to` block form — first arg must be URL, content in block
- `form_with model:` — Rails 7 defaults local:true, no Turbo unless specified
