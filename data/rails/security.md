# Security Traps

- `where("email = '#{params[:email]}'")`  — SQL injection, use `where(email: params[:email])`
- `Model.new(params[:model])` without permit — mass assignment even with strong params
- `skip_forgery_protection` on API — still needed if session-based auth
- `html_safe` on user input — stored XSS, escape first then mark safe
- `send(params[:method])` — arbitrary method call, whitelist allowed methods
- `redirect_to params[:url]` — open redirect, validate against whitelist
- `YAML.load(user_input)` — code execution, use `YAML.safe_load`
