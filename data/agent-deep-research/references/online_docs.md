# Online Documentation References

Links to official Google documentation relevant to this skill.

## Gemini Deep Research API

- **Deep Research Guide**: <https://ai.google.dev/gemini-api/docs/deep-research>
  Overview of the deep research agent, how to start research interactions, poll for status, and retrieve results. Covers the Interactions API used to manage long-running research tasks.

## Gemini File Search API

- **File Search Guide**: <https://ai.google.dev/gemini-api/docs/file-search>
  How to create file search stores, upload documents, and query them for grounded answers. Includes the list of supported file types (note: see `file_search_guide.md` for empirically validated types).

- **Supported File Types**: <https://ai.google.dev/gemini-api/docs/file-search#supported-files>
  Official list of supported MIME types. Many documented types do not work in practice -- see `file_search_guide.md` for details.

## Google GenAI SDK

- **Python SDK (google-genai)**: <https://googleapis.github.io/python-genai/>
  Reference documentation for the Python SDK used by the CLI scripts. Covers client initialization, file operations, and the Interactions API.

- **PyPI Package**: <https://pypi.org/project/google-genai/>
  Python package installation and version history.

## Interactions API

- **Interactions Reference**: <https://ai.google.dev/api/interactions>
  API reference for creating, polling, and managing long-running research interactions. This is the underlying API that powers the `research_start` and `research_status` commands.

## Google AI Studio

- **AI Studio**: <https://aistudio.google.com/>
  Web interface for obtaining API keys and testing Gemini models.
