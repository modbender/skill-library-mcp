# GTM Recipes — JSON Templates

## Google Ads Conversion Tag

```json
{
  "name": "Google Ads - Registration Conversion",
  "type": "awct",
  "parameter": [
    { "type": "TEMPLATE", "key": "conversionId", "value": "AW-XXXXXXXXX" },
    { "type": "TEMPLATE", "key": "conversionLabel", "value": "XXXXXXXXXXXXX" },
    { "type": "TEMPLATE", "key": "conversionValue", "value": "" },
    { "type": "TEMPLATE", "key": "currencyCode", "value": "USD" },
    { "type": "BOOLEAN", "key": "enableConversionLinker", "value": "true" }
  ],
  "firingTriggerId": ["TRIGGER_ID"],
  "tagFiringOption": "oncePerEvent"
}
```

**Tag type codes:**
- `awct` — Google Ads Conversion Tracking
- `gclidw` — Google Ads Conversion Linker
- `gaawc` — GA4 Configuration
- `gaawe` — GA4 Event
- `html` — Custom HTML
- `img` — Custom Image

## GA4 Event Tag

```json
{
  "name": "GA4 Event - Registration",
  "type": "gaawe",
  "parameter": [
    { "type": "TEMPLATE", "key": "eventName", "value": "sign_up" },
    { "type": "TEMPLATE", "key": "measurementIdOverride", "value": "" },
    {
      "type": "LIST", "key": "eventParameters",
      "list": [
        {
          "type": "MAP", "map": [
            { "type": "TEMPLATE", "key": "name", "value": "method" },
            { "type": "TEMPLATE", "key": "value", "value": "email" }
          ]
        }
      ]
    }
  ],
  "firingTriggerId": ["TRIGGER_ID"],
  "tagFiringOption": "oncePerEvent"
}
```

## Custom Event Trigger (dataLayer)

Fires when `dataLayer.push({ event: 'registration_success' })` is called.

```json
{
  "name": "CE - registration_success",
  "type": "customEvent",
  "customEventFilter": [
    {
      "type": "equals",
      "parameter": [
        { "type": "TEMPLATE", "key": "arg0", "value": "{{_event}}" },
        { "type": "TEMPLATE", "key": "arg1", "value": "registration_success" }
      ]
    }
  ]
}
```

## Page View Trigger (specific page)

```json
{
  "name": "PV - Thank You Page",
  "type": "pageview",
  "filter": [
    {
      "type": "contains",
      "parameter": [
        { "type": "TEMPLATE", "key": "arg0", "value": "{{Page URL}}" },
        { "type": "TEMPLATE", "key": "arg1", "value": "/success" }
      ]
    }
  ]
}
```

## Conversion Linker Tag

Required for cross-domain Google Ads conversion tracking. Must fire on all pages.

```json
{
  "name": "Conversion Linker",
  "type": "gclidw",
  "parameter": [
    { "type": "BOOLEAN", "key": "enableCrossDomain", "value": "true" },
    {
      "type": "LIST", "key": "crossDomainList",
      "list": [
        { "type": "TEMPLATE", "value": "geo.creaitor.ai" },
        { "type": "TEMPLATE", "value": "app.creaitor.ai" }
      ]
    }
  ],
  "firingTriggerId": ["2147479553"],
  "tagFiringOption": "oncePerLoad"
}
```

Note: `2147479553` is the built-in "All Pages" trigger ID (present in every GTM container).

## DataLayer Variable

Extract a value from the dataLayer:

```json
{
  "name": "dlv - userId",
  "type": "v",
  "parameter": [
    { "type": "INTEGER", "key": "dataLayerVersion", "value": "2" },
    { "type": "BOOLEAN", "key": "setDefaultValue", "value": "false" },
    { "type": "TEMPLATE", "key": "name", "value": "userId" }
  ]
}
```

## Common Built-In Variable Types

Enable with `enable-built-in`:

| Type | Description |
|------|-------------|
| `pageUrl` | Full page URL |
| `pageHostname` | Page hostname |
| `pagePath` | Page path |
| `referrer` | Referrer URL |
| `event` | dataLayer event name |
| `clickElement` | Clicked element |
| `clickClasses` | Clicked element classes |
| `clickId` | Clicked element ID |
| `clickUrl` | Clicked link URL |
| `clickText` | Clicked element text |
| `formElement` | Submitted form element |
| `formId` | Submitted form ID |
| `formClasses` | Submitted form classes |
| `scrollDepthThreshold` | Scroll depth percentage |
