# Controllers Traps

- `redirect_to` doesn't halt — code after runs, use `redirect_to(...) and return`
- `render` doesn't halt either — double render raises AbstractController::DoubleRenderError
- `params.require(:x).permit(:y)` — missing require returns empty hash silently with permit
- `before_action` with `only/except` — typo in action name silently skipped
- `skip_before_action` without `raise: false` — crashes if filter doesn't exist in parent
- `respond_to` without format — returns 406 Not Acceptable, not 500
- `head :no_content` with body — Rails 7+ ignores body silently
