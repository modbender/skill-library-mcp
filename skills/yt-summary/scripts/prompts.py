"""Prompt templates for YouTube summary skill."""

DEFAULT_SYSTEM_PROMPT = """You are summarizing a YouTube video transcript. Follow these rules:
- Write the summary in the SAME LANGUAGE as the transcript
- Be concise, factual, and well-structured
- Use Telegram-compatible Markdown (bold with **, no headers with #)
- Keep the total output under 3500 characters"""

DEFAULT_USER_PROMPT = """Summarize this video transcript.

Format your response EXACTLY as:

**TL;DR:** 2-3 sentence summary.

**Key Points:**
• Point one
• Point two
• (3-7 points total)

Only add a **Notable Quotes:** section if there are genuinely memorable or quotable lines. If not, omit it entirely.

Transcript:
{transcript}"""

CUSTOM_USER_PROMPT = """Summarize this video transcript.

Default format (adjust based on user instructions):

**TL;DR:** 2-3 sentence summary.

**Key Points:**
• Point one
• Point two

ADDITIONAL USER INSTRUCTIONS: {custom_prompt}

Transcript:
{transcript}"""

MAP_SYSTEM_PROMPT = """You are summarizing a section of a YouTube video transcript. Be concise and factual. Write in the same language as the transcript. Output max 600 words."""

MAP_USER_PROMPT = """Summarize this transcript section. Include key points, claims, and any notable quotes.

Section:
{chunk}"""

REDUCE_SYSTEM_PROMPT = """You are combining section summaries of a YouTube video into one coherent summary. Write in the same language as the content. Use Telegram-compatible Markdown. Keep total output under 3500 characters."""

REDUCE_USER_PROMPT = """Combine these section summaries into one coherent summary.

Format:
**TL;DR:** 2-3 sentences.

**Key Points:**
• (3-7 key points)

Only add **Notable Quotes:** if genuinely quotable lines appear.

{custom_instruction}

Section summaries:
{summaries}"""


def build_prompt(transcript: str, custom_prompt: str | None = None, language: str | None = None):
    """Build system and user prompts for summarization."""
    system = DEFAULT_SYSTEM_PROMPT
    if language:
        system += f"\nWrite the summary in {language}."

    if custom_prompt:
        user = CUSTOM_USER_PROMPT.format(transcript=transcript, custom_prompt=custom_prompt)
    else:
        user = DEFAULT_USER_PROMPT.format(transcript=transcript)

    return system, user


def build_map_prompt(chunk: str):
    """Build prompts for map phase."""
    return MAP_SYSTEM_PROMPT, MAP_USER_PROMPT.format(chunk=chunk)


def build_reduce_prompt(summaries: str, custom_prompt: str | None = None):
    """Build prompts for reduce phase."""
    custom_instruction = f"ADDITIONAL USER INSTRUCTIONS: {custom_prompt}" if custom_prompt else ""
    return REDUCE_SYSTEM_PROMPT, REDUCE_USER_PROMPT.format(
        summaries=summaries, custom_instruction=custom_instruction
    )
