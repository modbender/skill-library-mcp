from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openrouter_api_key: str = ""
    data_dir: str = "data"
    results_dir: str = "results"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    max_tokens: int | None = None
    temperature: float = 0.0
    battle_token: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

MODELS = [
    {
        "id": "nvidia/nemotron-nano-12b-v2-vl:free",
        "name": "NVIDIA Nemotron Nano 12B VL",
        "provider": "NVIDIA",
        "params": "12B",
    },
    {
        "id": "google/gemma-3-27b-it:free",
        "name": "Google Gemma 3 27B",
        "provider": "Google",
        "params": "27B",
    },
    {
        "id": "google/gemma-3-4b-it:free",
        "name": "Google Gemma 3 4B",
        "provider": "Google",
        "params": "4B",
    },
    {
        "id": "google/gemma-3-12b-it:free",
        "name": "Google Gemma 3 12B",
        "provider": "Google",
        "params": "12B",
    },
]

PROMPT = """Look at the image. Is it a hot dog (food: a sausage served in a bun/roll; any cooking style)?

Output exactly:
Observations: <brief description of what is visible>
Answer: <yes|no>"""
