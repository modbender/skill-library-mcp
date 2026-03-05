"""OpenAI chat callbacks for optional LLM-assisted workflows."""

from __future__ import annotations

import os

_client = None


def _get_client():
    """Create a lazy OpenAI client on first use."""
    global _client
    if _client is not None:
        return _client

    import openai

    _client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    return _client


def openai_llm_fn(system: str, user: str) -> str:
    """Run a single OpenAI chat request."""
    client = _get_client()
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    if not response.choices:
        return ""
    choice = response.choices[0]
    message = getattr(choice, "message", None)
    if message is None or not isinstance(message.content, str):
        return ""
    return message.content


def chat_completion(system: str, user: str) -> str:
    """Backward-compatible wrapper for single completion calls."""
    return openai_llm_fn(system, user)


def openai_llm_batch_fn(requests: list[dict]) -> list[dict]:
    """Run OpenAI chat requests sequentially."""
    results: list[dict] = []
    for req in requests:
        system = str(req.get("system", ""))
        user = str(req.get("user", ""))
        request_id = req.get("id")
        result = {"response": openai_llm_fn(system, user)}
        if request_id is not None:
            result["id"] = request_id
        results.append(result)
    return results
