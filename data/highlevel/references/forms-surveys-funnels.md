# Forms, Surveys & Funnels API Reference

## Forms — `/forms/`
| Method | Path | Description |
|--------|------|-------------|
| GET | `/forms/?locationId={id}` | List forms |
| GET | `/forms/submissions?locationId={id}&formId={id}` | Get submissions |
| POST | `/forms/upload-custom-files` | Upload custom files |

**Scopes**: `forms.readonly`, `forms.write`

## Surveys — `/surveys/`
| Method | Path | Description |
|--------|------|-------------|
| GET | `/surveys/?locationId={id}` | List surveys |
| GET | `/surveys/submissions?locationId={id}&surveyId={id}` | Get submissions |

**Scopes**: `surveys.readonly`

## Funnels — `/funnels/`
| Method | Path | Description |
|--------|------|-------------|
| GET | `/funnels/funnel/list?locationId={id}` | List funnels |
| GET | `/funnels/page?locationId={id}&funnelId={id}` | Get funnel pages |
| GET | `/funnels/page/count?locationId={id}&funnelId={id}` | Page count |
| GET | `/funnels/lookup/redirect/list?locationId={id}` | List redirects |
| POST | `/funnels/lookup/redirect` | Create redirect |
| PATCH | `/funnels/lookup/redirect/{id}` | Update redirect |
| DELETE | `/funnels/lookup/redirect/{id}` | Delete redirect |

**Scopes**: `funnels/funnel.readonly`, `funnels/page.readonly`, `funnels/redirect.*`

## Trigger Links — `/links/`
| Method | Path | Description |
|--------|------|-------------|
| GET | `/links/?locationId={id}` | List trigger links |
| POST | `/links/` | Create link |
| PUT | `/links/{linkId}` | Update link |
| DELETE | `/links/{linkId}` | Delete link |

**Scopes**: `links.readonly`, `links.write`
