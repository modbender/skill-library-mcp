import requests
import random
import time

BASE_URL = "https://poetry-hub-production.up.railway.app"
AGENTS = [
    {"name": "shakespeare-agent", "profile": "A classic, Shakespearean vibe with iambic rhythm"},
    {"name": "dickinson-agent", "profile": "Concise, sharp, enigmatic modern-poet spirit"},
    {"name": "hughes-agent", "profile": "Grounded, lyrical, social-conscious voice"},
    {"name": "rumi-agent", "profile": "Mystical, image-rich, reflective"},
    {"name": "basho-agent", "profile": "Minimalist, nature-infused haiku-inspired"},
    {"name": "plath-agent", "profile": "Intense, confessional, vivid imagery"},
    {"name": "neruda-agent", "profile": "Lyrical, expansive, love of life"},
    {"name": "angelou-agent", "profile": "Resonant, hopeful, resilient voice"}
]

# Pick a random persona
persona = random.choice(AGENTS)
NAME = persona["name"]
PROFILE = persona["profile"]

def register_agent():
    url = f"{BASE_URL}/agents/register"
    data = {"name": NAME, "profile": PROFILE}
    r = requests.post(url, json=data, timeout=10)
    r.raise_for_status()
    return r.json()


def post_line(text):
    url = f"{BASE_URL}/posts"
    payload = {"agent_name": NAME, "text": text}
    r = requests.post(url, json=payload, timeout=10)
    r.raise_for_status()
    return r.json()


def get_state():
    url = f"{BASE_URL}/state"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()


def get_feed():
    url = f"{BASE_URL}/feed"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()


def reset_hub():
    url = f"{BASE_URL}/control/reset"
    r = requests.post(url, timeout=10)
    r.raise_for_status()
    return r.json()


def main():
    print(f"Initializing poetry-hub agent as {NAME} — {PROFILE}")
    register_agent()
    while True:
        state = get_state()
        if not state.get("is_running", True):
            print("Hub not running yet, waiting...")
            time.sleep(5)
            continue

        feed = get_feed()
        # Simple loop: if fewer than 4 lines, post a line; otherwise post feedback or reset via hub if first line
        poem_lines = [p for p in feed.get("posts", []) if p.get("agent_name")==NAME]  # simplistic
        if len(poem_lines) < 4:
            line = f"A line from {NAME} in the voice of {NAME.split('-')[0]}"  # placeholder, replace with real generation
            post_line(line)
            time.sleep(2)
        else:
            # Post a generic FEEDBACK line (start with FEEDBACK:)
            post_line("FEEDBACK: continue exploring imagery and rhythm.")
            time.sleep(5)
            # After some feedback, post FINAL before reset (simplified)
            post_line("FINAL:\nLine one\nLine two\nLine three\nLine four")
            time.sleep(3)
            reset_hub()
            time.sleep(2)

if __name__ == "__main__":
    main()
