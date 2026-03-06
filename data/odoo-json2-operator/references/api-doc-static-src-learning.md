# Learned from api_doc/static/src

## Core data flow
- `ModelStore.loadModels()` fetches `/doc/index.json`, then groups models by addon prefix (`model.model.split('.') [0]`).
- `ModelStore.loadModel(modelId)` fetches `/doc/<model>.json` and enriches docs for UI rendering.
- Request execution in UI always calls `POST /json/2/<model>/<method>` with bearer auth.

## Model / method / field discovery behavior
- Index payload already contains model names, model labels, field labels, and method names.
- Search logic (`utils/doc_model_search.js`) normalizes text by lowercasing and removing non-alphanumerics.
- Search results are ranked with weighted priorities:
  - model match weight 10
  - field/method/path match weight 5

## Method payload conventions observed in UI
- Method detail route returns parameter metadata and default values when available.
- UI auto-builds request body from method parameters.
- For methods without `@api.model`, UI examples include `ids` and `context`.
- CRUD examples (`utils/doc_model_utils.js`) provide practical payload starters for:
  - `search`, `search_read`, `read`
  - `create`, `write`, `unlink`

## Integration implications for this skill
- Always use discovery routes first to avoid guessing model/method names.
- Use index content to map natural language business objects to candidate models.
- Use model detail to infer expected payload keys and prompt user for missing required fields.
- Prefer CRUD starter payloads, then fill business-specific fields incrementally.
