---
name: owid-oc
description: searches, retrieves, and summarizes content from Our World in Data using the `owid-catalog` Python module. Developed under Ubuntu. The developer would appreciate feedback on whether it works for you.
version: 0.1.3
---

# SKILL: Our World in Data (OWID) via `owid-catalog` Python Module

## Purpose

This skill enables OpenClaw to retrieve information from Our World in Data using the Python module [`owid-catalog`](https://pypi.org/project/owid-catalog/).

The skill focuses on:

- Searching for relevant charts  
- Selecting the most appropriate result  
- Retrieving chart data and metadata  
- Returning structured textual output  

All searches are performed in English to ensure consistency.

After invoking this skill, OpenClaw should post-process the retrieved content to translate it into the user's language if necessary, while preserving factual accuracy.

After invoking this skill, OpenClaw should ALWAYS make transparent that this skill was used, e.g. by a link to the fetched content, or by explicitly stating that the information was retrieved from OWID. This is important for transparency and attribution.


## Installation

```bash
pip install owid-catalog==1.0.0rc2
```

## Initialization

Initialize the OWID client:

```python
from owid.catalog import Client

client = Client()
```

This sets up access to the OWID catalog.

## Searching for Charts

Use the client.charts.search() function to find candidate charts.

### Basic Search

```python
results = client.charts.search("life expectancy")
```

This returns a ResponseSet of ChartResult objects ordered by popularity.

Example attributes:

- title
- subtitle
- url
- available_entities

### Recommended Search Strategy

Workflow for handling search results:
	1.	Execute client.charts.search(query, limit=3) to limit noise.
	2.	Select the most relevant result (e.g., by popularity or context).
	3.	Use the selected result to fetch the chart data.

Example:

```python
results = client.charts.search("life expectancy", limit=3)

if results:
    chart_result = results[0]
    chart_table = chart_result.fetch()
```

### Handling Ambiguity

OWID search returns multiple results; no explicit disambiguation error.

Recommended approach:
Select the most contextually relevant option
Or refine the search query

### Retrieving Chart Content

Once a chart is selected:

```python
chart_table = chart_result.fetch()

title = chart_result.title
description = chart_result.subtitle
url = chart_result.url

# Data summary can be derived from metadata
data_summary = f"Chart with {len(chart_result.available_entities)} entities, units: {chart_table.metadata.get('unit', 'N/A')}"
```

### Recommended Output Strategy

For most use cases:
Prefer description (subtitle) for concise answers.
Use data summary for key insights.
Always include url for reference.

### Error Handling

Handle the following exceptions:
ValueError
KeyError
HTTPTimeoutError (via client timeout)

Example:

```python
try:
    chart_table = chart_result.fetch()
except ValueError:
    print("Invalid chart.")
```

### Structured Return Format

The skill should return structured data such as:

```json
{
  "title": "...",
  "description": "...",
  "url": "...",
  "data_summary": "..."
}
```

Avoid returning raw tabular data unless explicitly required.

## Language Policy
Always execute searches in English (OWID default).
Even if the user asks in another language, the lookup must be performed in English.

## Post-processing Note

If the user's language is not English, OpenClaw should:
	1.	Retrieve the content in English.
	2.	Perform translation into the user's language as a post-processing step.
	3.	Clearly preserve factual accuracy during translation.

Translation must not alter the meaning of the original OWID content.

## Best Practices
Prefer precise search queries over broad terms.
Limit search results to reduce data load.
Use descriptions by default.
Handle multiple results explicitly.
Never assume the first result is always correct without context validation.

## Example End-to-End Workflow

```python
from owid.catalog import Client

client = Client()

def fetch_owid_summary(query):
    try:
        results = client.charts.search(query, limit=5)
        if not results:
            return None

        chart_result = results[0]
        chart_table = chart_result.fetch()
        return {
            "title": chart_result.title,
            "description": chart_result.subtitle,
            "url": chart_result.url,
            "data_summary": f"Chart with {len(chart_result.available_entities)} entities."
        }

    except ValueError:
        return {
            "error": "Chart not found"
        }
```

## Limitations
The module relies on the public OWID API and may be rate-limited.
Content accuracy depends on OWID.
Data summaries may omit nuance; full data retrieval should be deliberate.
