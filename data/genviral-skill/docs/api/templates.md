# Template Commands

Templates are reusable slideshow structures. Convert winning slideshows into templates for faster iteration.

## list-templates
```bash
genviral.sh list-templates
genviral.sh list-templates --search hooks --limit 20 --offset 0
genviral.sh list-templates --json
```

## get-template
```bash
genviral.sh get-template --id TEMPLATE_ID
```

## create-template
Create a template from a validated template config object.

```bash
# File input
genviral.sh create-template \
  --name "My Template" \
  --description "Description" \
  --visibility private \
  --config-file template-config.json

# Inline JSON
genviral.sh create-template \
  --name "My Template" \
  --visibility workspace \
  --config-json '{"version":1,"structure":{"slides":[]},"content":{},"visuals":{}}'
```

Use exactly one of `--config-file` or `--config-json`. Config must match the template config v1 schema.

## update-template
```bash
genviral.sh update-template --id TEMPLATE_ID --name "New Name"
genviral.sh update-template --id TEMPLATE_ID --visibility workspace
genviral.sh update-template --id TEMPLATE_ID --config-file new-config.json
genviral.sh update-template --id TEMPLATE_ID --config-json '{"version":1,"structure":{"slides":[]},"content":{},"visuals":{}}'
genviral.sh update-template --id TEMPLATE_ID --clear-description
```

Config input: use exactly one of `--config-file` or `--config-json` (not both).

## delete-template
```bash
genviral.sh delete-template --id TEMPLATE_ID
```

## create-template-from-slideshow
Convert an existing slideshow into a reusable template.

```bash
genviral.sh create-template-from-slideshow \
  --slideshow-id SLIDESHOW_ID \
  --name "Winning Format" \
  --description "Built from high-performing slideshow" \
  --visibility workspace \
  --preserve-text
```

`--preserve-text` supports both forms: `--preserve-text` (true) or `--preserve-text true|false`.
