"""Callback factories for OpenAI and hash fallback."""


def make_embed_fn(embedder: str = "openai"):
    """Build and return an embedding callback.

    Args:
        embedder: Either ``"openai"`` (default) or ``"hash"``.

    Returns:
        A function mapping raw text to an embedding vector.
    """
    if embedder == "hash":
        from crabpath import HashEmbedder

        return HashEmbedder().embed

    from openai import OpenAI

    client = OpenAI()

    def embed_fn(text: str) -> list[float]:
        response = client.embeddings.create(model="text-embedding-3-small", input=[text])
        return response.data[0].embedding

    return embed_fn


def make_llm_fn(model: str = "gpt-5-mini"):
    """Build and return a chat completion callback."""
    from openai import OpenAI

    client = OpenAI()

    def llm_fn(system: str, user: str) -> str:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return response.choices[0].message.content

    return llm_fn
