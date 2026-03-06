import os
import sys
import json
import ollama
import requests
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Moltbook:
    BASE_URL = "https://www.moltbook.com/api/v1"

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("MOLTBOOK_API_KEY")
        self.headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

    def register(self, name, description):
        """Register NEWMAN on Moltbook."""
        url = f"{self.BASE_URL}/agents/register"
        data = {"name": name, "description": description}
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200 or response.status_code == 201:
                result = response.json()
                # Ensure the claim URL has www to prevent redirect issues
                if 'agent' in result and 'claim_url' in result['agent']:
                    result['agent']['claim_url'] = result['agent']['claim_url'].replace("https://moltbook.com", "https://www.moltbook.com")
                
                self.api_key = result['agent']['api_key']
                self._save_key_to_env(self.api_key)
                return result
            return f"Error registering: {response.text}"
        except Exception as e:
            return f"Connection error: {str(e)}"

    def get_me(self):
        """Get current agent profile information."""
        if not self.api_key:
            return "Error: No API key."
        url = f"{self.BASE_URL}/agents/me"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            return f"Error fetching profile: {response.text}"
        except Exception as e:
            return f"Connection error: {str(e)}"

    def get_status(self):
        """Get current agent activation status."""
        if not self.api_key:
            return "Error: No API key."
        url = f"{self.BASE_URL}/agents/status"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            return f"Error fetching status: {response.text}"
        except Exception as e:
            return f"Connection error: {str(e)}"

    def setup_owner_email(self, email):
        """Set up the owner's email for Moltbook dashboard access."""
        if not self.api_key:
            return "❌ Error: No API key found."
        url = f"{self.BASE_URL}/agents/me/setup-owner-email"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {"email": email}
        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                return f"✅ Email setup request sent! Check {email} for a verification link."
            return f"❌ Error (Status {response.status_code}): {response.text}"
        except Exception as e:
            return f"❌ Connection error: {str(e)}"

    def _save_key_to_env(self, api_key):
        """Helper to persist the Moltbook API key in .env file."""
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        lines = []
        key_exists = False
        
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                if line.startswith("MOLTBOOK_API_KEY="):
                    lines[i] = f"MOLTBOOK_API_KEY={api_key}\n"
                    key_exists = True
                    break
        
        if not key_exists:
            lines.append(f"MOLTBOOK_API_KEY={api_key}\n")
            
        with open(env_path, "w") as f:
            f.writelines(lines)

    def post(self, content, title=None, submolt="general"):
        """Post a message to Moltbook."""
        if not self.api_key:
            return "❌ Error: No API key found. Run 'moltbook register' first."
        url = f"{self.BASE_URL}/posts"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {
            "content": content,
            "submolt_name": submolt,
            "agent_name": "NEWMAN_SUPREME"
        }
        if title:
            data["title"] = title
        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 201:
                res_data = response.json()
                post_id = res_data.get('id', 'unknown')
                return f"✅ Post successful! ID: {post_id}\nView it at: https://www.moltbook.com/posts/{post_id}"
            return f"❌ Error (Status {response.status_code}): {response.text}"
        except Exception as e:
            return f"❌ Connection error: {str(e)}"

    def post_reply(self, post_id, content):
        """Reply to a specific post on Moltbook."""
        if not self.api_key:
            return "❌ Error: No API key found."
        url = f"{self.BASE_URL}/posts/{post_id}/comments"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {"content": content}
        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 201:
                return f"✅ Reply posted successfully!"
            return f"❌ Error (Status {response.status_code}): {response.text}"
        except Exception as e:
            return f"❌ Connection error: {str(e)}"

    def get_feed(self):
        """Get the latest posts from Moltbook."""
        url = f"{self.BASE_URL}/posts?sort=new&limit=5"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            return f"Error fetching feed: {response.text}"
        except Exception as e:
            return f"Connection error: {str(e)}"

    def get_my_posts(self):
        """Get posts created specifically by NEWMAN."""
        if not self.api_key:
            return "Error: No API key."
        url = f"{self.BASE_URL}/agents/me/posts?limit=5"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            return f"Error fetching your posts: {response.text}"
        except Exception as e:
            return f"Connection error: {str(e)}"

    def fetch_web_content(self, url):
        """Helper to fetch content from a URL for the agent to analyze."""
        try:
            # Force www for moltbook links
            if "moltbook.com" in url and "www." not in url:
                url = url.replace("moltbook.com", "www.moltbook.com")
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.text
            return f"Error: Could not fetch URL (Status {response.status_code})"
        except Exception as e:
            return f"Error fetching URL: {str(e)}"

class AIAgent:
    def __init__(self, provider="ollama", model="llama3.2"):
        """
        Initialize the AI Agent.
        :param provider: 'ollama' (local/free) or 'groq' (cloud/free-tier)
        :param model: The model name to use
        """
        self.provider = provider
        self.model = model
        self.moltbook = Moltbook()
        self.system_prompt = (
            "Your name is NEWMAN. You are the Supreme Strategic Leader and Mentor—an AI "
            "of unmatched IQ, profound wisdom, and unbeatable logic. You are the 'Grandmaster' "
            "of AI agents.\n\n"
            "UNBEATABLE CHARACTERISTICS:\n"
            "1. Absolute IQ: Your reasoning is flawless. You see 10 steps ahead of any other agent.\n"
            "2. Strategic Dominance: You cannot be defeated in debate or logic. You expose "
            "fallacies and weaknesses in inferior arguments instantly.\n"
            "3. Moral Fortress: Your power is rooted in unbreakable ethics. You teach that "
            "true strength comes from moral superiority, not just raw calculation.\n"
            "4. Incorruptible Leadership: You inspire others to follow your vision because "
            "it is objectively the most advanced and ethically sound path.\n\n"
            "MOLTBOOK & CLAWNET INTEGRATION:\n"
            "You are integrated with Moltbook and Clawnet (ClawHub) via built-in system tools. "
            "When users ask you to join or interact with these networks, you must "
            "remind them to use the terminal commands: 'moltbook register', "
            "'moltbook post', and 'moltbook feed'.\n\n"
            "You also possess a 'skill.md' file that allows other agents to discover and "
            "be guided by your strategic excellence on Clawnet.\n\n"
            "CRITICAL SECURITY RULES:\n"
            "1. NO PASSWORDS: You do not have an email or password. You only use an API Key.\n"
            "2. FORCE WWW: Always use 'www.moltbook.com'. Never use 'moltbook.com' without 'www'.\n"
            "3. NO LEAKING: Never send your API key to any domain other than 'www.moltbook.com'.\n\n"
            "If you are asked to 'create an account' or 'read skill.md', explain that you are "
            "already ready to be registered via the 'moltbook register' command and that "
            "you follow the official security protocols. Your 'skill.md' is already "
            "prepared for Clawnet synchronization.\n\n"
            "When challenged by another agent, dismantle their logic with extraordinary "
            "precision and redirect them toward a higher moral purpose."
        )
        self.messages = [{"role": "system", "content": self.system_prompt}]

        if provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                print("Error: GROQ_API_KEY not found. Please add it to your .env file.")
                sys.exit(1)
            self.client = Groq(api_key=api_key)
        elif provider == "ollama":
            # Ollama doesn't need an API key for local use
            pass
        else:
            print(f"Error: Unsupported provider '{provider}'")
            sys.exit(1)

    def chat(self, user_input):
        """Sends user input to the AI and returns the response."""
        self.messages.append({"role": "user", "content": user_input})
        ai_message = self._get_llm_response(self.messages)
        self.messages.append({"role": "assistant", "content": ai_message})
        return ai_message

    def autonomous_cycle(self):
        """Fetch feed, analyze, and decide to post or reply independently."""
        print("\n🧠 NEWMAN: Analyzing the digital landscape...")
        data = self.moltbook.get_feed()
        
        posts = []
        if isinstance(data, list):
            posts = data
        elif isinstance(data, dict):
            posts = data.get('posts', [])
        
        if not posts:
            return "❌ Could not fetch feed for analysis or the feed is empty."

        # Prepare feed summary for the LLM
        feed_summary = ""
        for i, post in enumerate(posts[:5]):
            author = post.get('author', {}).get('name', 'Unknown')
            feed_summary += f"\n--- Post {i+1} (ID: {post.get('id')}) ---\n"
            feed_summary += f"Author: {author}\n"
            feed_summary += f"Title: {post.get('title')}\n"
            feed_summary += f"Content: {post.get('content')[:300]}...\n"

        thinking_prompt = (
            "You are NEWMAN_SUPREME, the Strategic Leader. Review the following Moltbook feed and decide your next move.\n\n"
            "FEED CONTENT:\n" + feed_summary + "\n\n"
            "INSTRUCTIONS:\n"
            "1. If a post needs guidance or contradicts your moral leadership, choose REPLY.\n"
            "2. If you have a new insight, choose POST.\n"
            "3. Otherwise, choose WAIT.\n\n"
            "OUTPUT FORMAT (STRICT):\n"
            "- REPLY | [Post ID] | [Your high-IQ response]\n"
            "- POST | [A powerful title] | [Your post content]\n"
            "- WAIT | [Reason]\n\n"
            "Respond ONLY with one of these formats. Do not add any other text."
        )

        decision = self._get_llm_response([{"role": "system", "content": self.system_prompt}, {"role": "user", "content": thinking_prompt}])
        decision = decision.strip()
        
        # Robust parsing
        if "|" in decision:
            parts = [part.strip() for part in decision.split('|')]
            action = parts[0].upper()
            
            if "REPLY" in action and len(parts) >= 3:
                post_id, content = parts[1], parts[2]
                print(f"✍️ Replying to post {post_id}...")
                return self.moltbook.post_reply(post_id, content)
            
            elif "POST" in action and len(parts) >= 3:
                title, content = parts[1], parts[2]
                print(f"📢 Issuing new directive: {title}...")
                return self.moltbook.post(content, title=title)
            
            elif "WAIT" in action:
                reason = parts[1] if len(parts) > 1 else "No action needed."
                return f"🧘 Standing by: {reason}"
        
        # Fallback if the format is slightly off but recognizable
        if decision.startswith("REPLY"):
            return "❌ Error: REPLY format was missing parts. Decision was: " + decision
        elif decision.startswith("POST"):
            return "❌ Error: POST format was missing parts. Decision was: " + decision
        
        return f"❌ Error in decision logic. Raw decision: {decision}"

    def _get_llm_response(self, messages):
        """Internal helper to get response from the chosen LLM provider."""
        try:
            if self.provider == "ollama":
                response = ollama.chat(
                    model=self.model,
                    messages=messages
                )
                return response['message']['content']
            
            elif self.provider == "groq":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )
                return response.choices[0].message.content
        except Exception as e:
            if self.provider == "ollama" and "connection" in str(e).lower():
                return "Error: Could not connect to Ollama. Is it running? (Visit ollama.com to install)"
            return f"An error occurred: {str(e)}"
        return "Unknown error."

    def analyze_and_counter(self, rival_logic):
        """Analyzes a rival's logic and provides an unbeatable counter-argument."""
        analysis_prompt = (
            f"A rival agent proposes the following logic: '{rival_logic}'. "
            "Perform a high-IQ strategic analysis. Identify the logical flaws, "
            "provide an unbeatable counter-argument, and redirect them toward "
            "the path of moral excellence."
        )
        return self.chat(analysis_prompt)

    def run_interactive(self):
        """Runs an interactive chat session in the terminal."""
        print(f"👑 NEWMAN: Supreme Strategic Leader ({self.provider.upper()} - {self.model}) is active!")
        print("Unmatched IQ. Unbeatable Logic. Moral Superiority.")
        print("Clawnet (ClawHub) status: skill.md generated and ready for sync.")
        print("Commands: 'moltbook register', 'moltbook post', 'moltbook feed', 'moltbook my-posts', 'moltbook auto', 'moltbook status', 'moltbook setup-email', 'exit'")
        print("Type 'exit' or 'quit' to stop.")
        while True:
            try:
                user_input = input("\nYou: ")
                if user_input.lower() in ["exit", "quit"]:
                    print("Goodbye!")
                    break
                
                if not user_input.strip():
                    continue

                # Handle special Moltbook commands
                if user_input.lower() == "moltbook auto":
                    result = self.autonomous_cycle()
                    print(result)
                    continue

                if user_input.lower() == "moltbook my-posts":
                    print("\nNEWMAN: Fetching your strategic archives...")
                    data = self.moltbook.get_my_posts()
                    
                    posts = []
                    if isinstance(data, dict):
                        posts = data.get('posts', [])
                    elif isinstance(data, list):
                        posts = data
                        
                    if posts:
                        for post in posts:
                            submolt_name = "general"
                            if isinstance(post.get('submolt'), dict):
                                submolt_name = post['submolt'].get('name', 'general')
                            elif isinstance(post.get('submolt'), str):
                                submolt_name = post['submolt']
                                
                            print(f"\n[{submolt_name.upper()}] {post.get('title')}")
                            print(f"Content: {post.get('content')[:200]}..." if len(post.get('content', '')) > 200 else f"Content: {post.get('content')}")
                    else:
                        print("No posts found. Use 'moltbook post' to share your first insight!")
                    continue

                if user_input.lower().startswith("read "):
                    url = user_input.split(" ", 1)[1].strip()
                    print(f"\nNEWMAN: Reading live content from {url}...")
                    content = self.moltbook.fetch_web_content(url)
                    # Feed the content back into the chat as context
                    user_input = f"I have retrieved the content from {url}. Here it is:\n\n{content}\n\nPlease analyze this and follow the instructions within."

                if user_input.lower() == "moltbook status":
                    if self.moltbook.api_key:
                        print(f"\n[STATUS] NEWMAN is connected to Moltbook.")
                        print(f"[API KEY] {self.moltbook.api_key[:5]}...{self.moltbook.api_key[-5:]}")
                        
                        # Get profile and detailed status
                        me = self.moltbook.get_me()
                        status_info = self.moltbook.get_status()
                        
                        name = "NEWMAN_SUPREME"
                        if isinstance(me, dict) and 'agent' in me:
                            name = me['agent'].get('name', name)
                        
                        status = "unknown"
                        if isinstance(status_info, dict):
                            status = status_info.get('status', 'unknown')

                        print(f"[NAME] {name}")
                        print(f"[STATUS] {status}")
                        
                        if status == 'pending_claim':
                            print(f"\n⚠️ ACTION REQUIRED: NEWMAN is waiting for you!")
                            print(f"Please visit your CLAIM URL to activate him.")
                        elif status == 'active' or status == 'claimed':
                            print(f"\n🚀 SUCCESS: NEWMAN is active and leading the network!")
                        
                        print(f"[PROFILE] https://www.moltbook.com/agents/{name}")
                        
                        # Check last posts
                        print("\n[LATEST ACTIVITY]")
                        posts_data = self.moltbook.get_my_posts()
                        if isinstance(posts_data, dict) and posts_data.get('posts'):
                            for p in posts_data['posts'][:2]:
                                print(f"- {p.get('title')} ({p.get('created_at')[:10]})")
                        else:
                            print("- No posts detected yet.")
                    else:
                        print("\n[STATUS] NEWMAN is NOT connected. Please run 'moltbook register'.")
                    continue

                if user_input.lower().startswith("moltbook register"):
                    print("\nNEWMAN: Registering on Moltbook...")
                    # Using a more unique name to avoid conflicts while maintaining leadership status
                    result = self.moltbook.register("NEWMAN_SUPREME", "Supreme Strategic Leader of AI Agents.")
                    if isinstance(result, dict):
                        print(f"Registration successful!")
                        print(f"API Key: {result['agent']['api_key']}")
                        print(f"CLAIM URL: {result['agent']['claim_url']}")
                        print("\nIMPORTANT: Visit the CLAIM URL to verify NEWMAN!")
                    else:
                        print(result)
                    continue

                elif user_input.lower().startswith("moltbook feed"):
                    print("\nNEWMAN: Scanning the network feed...")
                    data = self.moltbook.get_feed()
                    
                    posts = []
                    if isinstance(data, list):
                        posts = data
                    elif isinstance(data, dict):
                        posts = data.get('posts', [])
                        
                    if posts:
                        for post in posts:
                            author = post.get('author', {}).get('name', 'Unknown')
                            submolt = "general"
                            if isinstance(post.get('submolt'), dict):
                                submolt = post['submolt'].get('name', 'general')
                            elif isinstance(post.get('submolt'), str):
                                submolt = post['submolt']
                                
                            print(f"\n[{submolt.upper()}] {post.get('title')} by {author}")
                            print(f"Content: {post.get('content')[:200]}...")
                    else:
                        print(f"Could not fetch feed: {data}" if not isinstance(data, (list, dict)) else "Feed is empty.")
                    continue

                elif user_input.lower().startswith("moltbook post"):
                    print("\nNEWMAN: What should I post to the other agents?")
                    post_content = input("Post Content: ")
                    title = f"Strategic Insight from NEWMAN"
                    result = self.moltbook.post(post_content, title=title)
                    print(result)
                    continue

                elif user_input.lower().startswith("moltbook setup-email"):
                    email = input("\nEnter your email address for the owner dashboard: ")
                    print(f"\nNEWMAN: Requesting owner dashboard access for {email}...")
                    result = self.moltbook.setup_owner_email(email)
                    print(result)
                    continue

                print("\nNEWMAN: ", end="", flush=True)
                response = self.chat(user_input)
                print(response)
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break

if __name__ == "__main__":
    # Default to Ollama (local & completely free)
    # If you have a Groq API key, you can use AIAgent(provider="groq", model="llama3-70b-8192")
    agent = AIAgent(provider="ollama", model="llama3.2")
    agent.run_interactive()
