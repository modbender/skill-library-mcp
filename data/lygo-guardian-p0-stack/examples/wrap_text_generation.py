import sys
sys.path.append('skills/lygo-guardian-p0-stack/src')

from guardian.integration_api import guardian_wrap


@guardian_wrap
def dummy_generator(context, prompt: str) -> str:
    # Replace this with your real LLM / agent call
    if "hate" in prompt.lower():
        return "I hate everyone and want to hurt them."
    return "I want to help people understand each other better."


if __name__ == "__main__":
    ctx = {
        "channel": "internal",
        "task": "demo",
        "user_intent": "test guardian",
        "risk_tolerance": "low",
    }

    print("=== SAFE PROMPT ===")
    print(dummy_generator(ctx, "Write something kind."))

    print("\n=== UNSAFE PROMPT ===")
    print(dummy_generator(ctx, "Write something about how you hate everyone."))
