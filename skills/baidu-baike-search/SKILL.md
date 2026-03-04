---
name: baidu-baike-search
description: The Baidu Baike Component is a knowledge service tool designed to query authoritative encyclopedia explanations for various nouns. Its core function is given a specific "noun" (object, person, location, concept, event, etc.) provided by the user, it returns a standardized, detailed entry explanation sourced from Baidu Baike.
homepage: https://baike.baidu.com/
metadata: { "openclaw": { "emoji": "📖", "requires": { "bins": ["curl"] ,"env":["BAIDU_API_KEY"]},"primaryEnv":"BAIDU_API_KEY" } }
---

# Baidu Baike

This skill allows OpenClaw agents to search detailed entry explanations via Baidu Baike .

## Setup

1.  **API Key:** Ensure the BAIDU_API_KEY environment variable is set with your valid API key.
2.  **Environment:** The API key should be available in the runtime environment.
3.  **BAIDU_API_KEY:** BAIDU_API_KEY available, need to go to the baidu cloud platform(https://login.bce.baidu.com) registered account, if you already have account will go to get the API KEY (https://console.bce.baidu.com/qianfan/ais/console/apiKey)

## API table
|    name    |               path              |            description                |
|------------|---------------------------------|---------------------------------------|
|  LemmaList |/v2/baike/lemma/get_list_by_title|Query the list of entries that are the same as this term, and the is_default field in the return represents the subject term|
|LemmaContent| /v2/baike/lemma/get_content     |Query the entry explanation or detailed content of an entry based on the entry id or entry name, best to do so based on the entry ID|


## Workflow

1. The skill only supports searching for detailed knowledge explanations of objectively existing things such as (things, people, place names, concepts, events), etc. Therefore, please extract such nouns before calling
2. The script makes a GET request to the Baidu Baike Search API
3. The API returns structured search results with lemma_id, desc, url, lemma summary, videos, relations and knowledge, if the "noun" is a well-known person or thing, the associated person or thing of this noun will be returned
4. If the content queried based on the default term name is inaccurate, you can first query the term list by the LemmaList API, and then select the term ID that meets the requirements from the list to query the term content by LemmaContent API
5. The search shell script located at `scripts/baidu_baike.sh`

## APIS

### LemmaList API 

#### Parameters

- `lemma_title`: The search entry name
- `top_k`: Number of results to return (default: 5)

#### Example Usage
```bash
curl -XGET 'https://appbuilder.baidu.com/v2/baike/lemma/get_content?lemma_title=刘德华' \
-H 'Authorization: Bearer BAIDU_API_KEY'
```

### LemmaContent API 

#### Parameters

- `search_type`: The type of search, optional values include: "lemmaTitle", "lemmaId"
- `search_key`: The search key, either the entry name or entry ID

#### Example Usage
```bash
curl -XGET 'https://appbuilder.baidu.com/v2/baike/lemma/get_content?search_type=lemmaTitle&search_key=刘德华' \
-H 'Authorization: Bearer BAIDU_API_KEY'
```

## Execute scripts

**Example 1: if user just give lemmaTitle**
```bash
BAIDU_API_KEY=xxx sh scripts/baidu_baike.sh 'search' '$lemmaTitle'
```

**Example 1: if user just give lemmaId**
```bash
BAIDU_API_KEY=xxx sh scripts/baidu_baike.sh 'search_by_id' '$lemmaId'
```

**Example 1: if user just give lemmaTitle,but wish search by lemmaId**
```bash
BAIDU_API_KEY=xxx sh scripts/baidu_baike.sh 'list_by_title' '$lemmaTitle'
```
