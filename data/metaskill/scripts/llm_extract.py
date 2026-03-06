# scripts/llm_extract.py
import sys, json, os
sys.path.insert(0, os.path.dirname(__file__))
from llm_provider import call_llm

def extract_levels(error_desc):
    prompt = f"""Extract 3 correction levels from this error/mistake:

"{error_desc}"

Return ONLY valid JSON:
{{"surface": "what specifically went wrong in this instance", "principle": "the underlying rule or mental model that was violated", "habit": "the concrete behavioral change that prevents recurrence"}}"""

    result = call_llm(prompt, provider_type="fast", max_tokens=300)
    if result:
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            pass
    return None

if __name__ == "__main__":
    error = " ".join(sys.argv[1:])
    result = extract_levels(error)
    if result:
        print(json.dumps(result))
    else:
        print("FALLBACK")
