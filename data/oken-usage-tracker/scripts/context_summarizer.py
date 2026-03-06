"""context_summarizer.py

Produce a short summary of a long context to reduce tokens sent to LLMs.
This is a lightweight example using simple heuristics; replace with model-based summarization if desired.
"""
import textwrap


def summarize_text(text, target_chars=700):
    """Naive summarizer: compress by keeping first/last sections and key lines.
    target_chars approximates desired output size (not tokens).
    """
    if not text:
        return ''
    if len(text) <= target_chars:
        return text
    # split into lines and keep top/bottom sections
    lines = [l for l in text.splitlines() if l.strip()]
    if not lines:
        return text[:target_chars]
    head = '\n'.join(lines[:10])
    tail = '\n'.join(lines[-10:])
    mid = '\n'.join(lines[10:-10])
    # extract a few highest-information lines heuristically (longest lines)
    candidates = sorted(lines, key=lambda l: len(l), reverse=True)[:5]
    combined = '\n'.join([head] + candidates + [tail])
    return (combined[:target_chars]).strip()


if __name__ == '__main__':
    long_text = '\n'.join(['Line %d: ' % i + 'x'* (i%80) for i in range(200)])
    s = summarize_text(long_text, target_chars=800)
    print(s[:1200])
