TODO
====

Here's the plan of refactoring this skill:

# Add scripts for all the commands

1. `config.py`: Add all the commands for config, it should support local and remote embedding like ollama, openai, gemini, etc.
2. `embed.py`: Add all the commands for embedding, it should support local and remote embedding like ollama, openai, gemini, etc.
3. `search.py`: Add all the commands for search, it should support local and remote embedding like ollama, openai, gemini, etc.
4. `link.py`: Add all the commands for link, it should support local and remote embedding like ollama, openai, gemini, etc.

# Config

Add new config command to configure the embedding model and other settings.

It should:

- Create a config/config.json file if it does not exist
- Support local and remote embedding like ollama, openai, gemini, etc.
- Support setting the max_input_length, default to 8192
- Support setting the default_threshold, default to 0.65
- Support setting the top_k, default to 5

# Embed

Behavioral changes:

- Embed should cache to json file instead pkl
- Embed should support local and remote embedding like ollama, openai, gemini, etc.
- Embed should read config/config.json for settings
- Embed should read `<directory>/.embeddings/embeddings.json` for cache
- Embed should support truncating text to max_input_length
- Embed should support partially update cache based on modified time

# Search

Add new search command to search notes based on query.

It should:

- Embed the query
- Compare the query embedding with the cached embeddings of all notes
- Return the top-k most similar notes

# Link

Add new link command to link notes based on query, output to link.json.

It should:

- Compare the query embedding with the cached embeddings of all notes
- Return the similar notes over the threshold
- Output to link.json
