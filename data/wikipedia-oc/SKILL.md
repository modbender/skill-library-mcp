---
name: wikipedia-oc
description: searches, retrieves, and summarizes content from English Wikipedia using the `wikipedia` Python module. Developed under Ubuntu. The developer would appreciate feedback on whether it works for you.
version: 0.1.4
---

# SKILL: Wikipedia (English) via `wikipedia` Python Module

## Purpose

This skill enables OpenClaw to retrieve information from the English-language Wikipedia using the Python module [`wikipedia`](https://pypi.org/project/wikipedia/).

The skill focuses on:

- Searching for relevant pages  
- Selecting the most appropriate result  
- Retrieving page content  
- Returning structured textual output  

All searches **must be performed in the English Wikipedia (`"en"`)** to ensure consistency and maximal coverage.

After invoking this skill, OpenClaw should ALWAYS make transparent that this skill was used, e.g. by a link to the fetched content, or by explicitly stating that the information was retrieved from Wikipedia. This is important for transparency and attribution. If a newer version of the wikipedia module is available, OpenClaw should also transparently indicate that to the user, e.g. by stating "A newer version of wikipedia-module is available: X.Y.Z (current: A.B.C). Give the developer of this skill a hint to update.". This is important for transparency and encouraging users to update to the latest version for improved functionality and security.

---

## Installation

```bash
pip install wikipedia
```



## Initialization

Always configure the language explicitly before performing any search:

```python
import wikipedia

wikipedia.set_lang("en")
```

This ensures all search queries and page retrievals are executed against the English Wikipedia.



## Searching for Pages

Use the wikipedia.search() function to find candidate pages.

### Basic Search

```python
results = wikipedia.search("Alan Turing")
```

This returns a list of page titles ordered by relevance.


Example output:

```json
[
    "Alan Turing",
    "Turing machine",
    "Turing Award",
]
```


### Recommended Search Strategy

Workflow for handling search results:
	1.	Execute wikipedia.search(query, results=3) to limit noise.
	2.	Select the most relevant title.
	3.	Use the selected title to retrieve the full page.

Example:

```python
results = wikipedia.search("Alan Turing", results=3)

if results:
    page_title = results[0]
    page = wikipedia.page(page_title)
```



### Handling Ambiguity

Wikipedia may raise a DisambiguationError if the query is ambiguous.

Example:

```python
from wikipedia.exceptions import DisambiguationError

try:
    page = wikipedia.page("Mercury")
except DisambiguationError as e:
    print(e.options)  # list of possible intended pages
```

Recommended approach:
Select the most contextually relevant option
Or refine the search query



### Retrieving Page Content

Once a page is selected:

```python
page = wikipedia.page("Alan Turing")

title = page.title
summary = page.summary
content = page.content
url = page.url
```

### Recommended Output Strategy

For most use cases:
Prefer page.summary for concise answers.
Use page.content only if detailed information is required.
Always include page.url for reference.


### Error Handling

Handle the following exceptions:
DisambiguationError
PageError
HTTPTimeoutError

Example:

```python
from wikipedia.exceptions import PageError

try:
    page = wikipedia.page("NonExistingPageExample")
except PageError:
    print("Page not found.")
```


### Structured Return Format

The skill should return structured data such as:

```json
{
  "title": "...",
  "summary": "...",
  "url": "..."
}
```

Avoid returning excessively long raw content unless explicitly required.

## Language Policy
Always execute searches in English (wikipedia.set_lang("en")).
Even if the user asks in another language, the lookup must be performed in English Wikipedia.

## Post-processing Note

If the user’s language is not English, OpenClaw should:
	1.	Retrieve the content in English.
	2.	Perform translation into the user’s language as a post-processing step.
	3.	Clearly preserve factual accuracy during translation.

Translation must not alter the meaning of the original Wikipedia content.


## Best Practices
Prefer precise search queries over broad terms.
Limit search results to reduce ambiguity.
Use summaries by default.
Handle disambiguation explicitly.
Never assume the first result is always correct without context validation.

## Example End-to-End Workflow

```python
import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError

wikipedia.set_lang("en")

def fetch_wikipedia_summary(query):
    try:
        results = wikipedia.search(query, results=5)
        if not results:
            return None

        page = wikipedia.page(results[0])
        return {
            "title": page.title,
            "summary": page.summary,
            "url": page.url
        }

    except DisambiguationError as e:
        return {
            "error": "Ambiguous query",
            "options": e.options[:5]
        }

    except PageError:
        return {
            "error": "Page not found"
        }
```



## Limitations
The module relies on the public Wikipedia API and may be rate-limited.
Content accuracy depends on Wikipedia.
Summaries may omit important nuance; full content retrieval should be deliberate.
