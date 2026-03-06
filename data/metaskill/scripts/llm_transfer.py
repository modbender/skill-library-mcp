# scripts/llm_transfer.py
import sys, json, os
sys.path.insert(0, os.path.dirname(__file__))
from llm_provider import call_llm

def get_analogous_principles(task_desc, learnings_content):
    prompt = f"""Given this task:
"{task_desc}"

Which of these past learnings are analogically relevant? Explain the connection. Return ONLY valid JSON in this format:
{{"principles": [{{"principle": "...", "reasoning": "..."}}]}}

Past learnings:
{learnings_content}"""

    result = call_llm(prompt, provider_type="deep", max_tokens=500)
    if result:
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            pass
    return None

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("FALLBACK")
        sys.exit(0)

    task_desc = sys.argv[1]
    learnings_file = sys.argv[2]

    try:
        with open(learnings_file, "r") as f:
            content = f.read()

        # Extract just the headers + first 2 lines of each entry
        lines = content.split('\n')
        extracted_lines = []
        capture = 0
        for line in lines:
            if line.startswith('## '):
                capture = 3
            if capture > 0:
                extracted_lines.append(line)
                capture -= 1

        extracted_content = '\n'.join(extracted_lines)
    except Exception:
        print("FALLBACK")
        sys.exit(0)

    result = get_analogous_principles(task_desc, extracted_content)
    if result:
        print(json.dumps(result))
    else:
        print("FALLBACK")
