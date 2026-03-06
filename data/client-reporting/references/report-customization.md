# Report Customization

## Template System

Reports use Jinja2 HTML templates. The rendering pipeline:
1. Pull metrics → JSON data files
2. Load template (client-specific override or global default)
3. Render with metrics as context variables
4. Output HTML or Markdown

## Creating Custom Templates

### File Location
- Global templates: `templates/<type>.html`
- Client overrides: `clients/<name>/templates/<type>.html`
- Client templates take priority over global

### Available Variables

All templates receive:
- `client_name` — display name
- `period_start`, `period_end` — date strings
- `generated_at` — generation timestamp

GA4 variables (when configured):
- `sessions`, `users`, `new_users`, `pageviews`
- `bounce_rate`, `avg_session_duration`
- `sessions_change`, `users_change` (% vs previous period)
- `top_pages` — list of `{page, views, change}`
- `traffic_sources` — list of `{source, sessions, pct}`

Search Console variables:
- `clicks`, `impressions`, `ctr`, `avg_position`
- `top_queries` — list of `{query, clicks, impressions, position}`

Social variables:
- `followers`, `followers_change`
- `engagement_rate`
- `top_posts` — list of `{text, likes, shares}`

## Branding

Set in client config:
```json
{
  "branding": {
    "logo_url": "https://example.com/logo.png",
    "primary_color": "#f97316",
    "accent_color": "#7c3aed"
  }
}
```

Access in templates:
```html
<img src="{{ branding.logo_url }}" alt="Logo">
<div style="color: {{ branding.primary_color }}">Heading</div>
```

## Report Types

### weekly
- 7-day snapshot
- Week-over-week comparison
- Top 5 queries and pages

### monthly  
- 30-day deep dive
- Month-over-month trends
- Full query and page tables
- Recommendations section

### quarterly
- 90-day strategic view
- Quarter-over-quarter
- Trend graphs (when supported)
- Executive summary

### custom
- Use `--metrics` flag to select specific sections
- Example: `--metrics "traffic,rankings"` skips social
