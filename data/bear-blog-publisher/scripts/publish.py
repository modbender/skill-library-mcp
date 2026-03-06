#!/usr/bin/env python3
"""
Bear Blog Publisher - Core Module
Supports 3 authentication methods and optional AI content generation
"""

import requests
import re
import json
import os
import stat
from typing import Optional, Dict, Any, Literal
from pathlib import Path
from playwright.sync_api import sync_playwright


class BearBlogPublisher:
    """Bear Blog publishing functionality with secure credential handling"""
    
    def __init__(self, email: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize publisher with credentials.
        
        Priority:
        1. Runtime parameters (highest)
        2. Environment variables
        3. OpenClaw config file (lowest)
        
        Args:
            email: Bear Blog email (optional, will check other sources)
            password: Bear Blog password (optional, will check other sources)
        """
        self.email, self.password = self._resolve_credentials(email, password)
        
        if not self.email or not self.password:
            raise ValueError(
                "Bear Blog credentials not found. "
                "Provide as arguments, set environment variables (BEAR_BLOG_EMAIL, BEAR_BLOG_PASSWORD), "
                "or configure in ~/.openclaw/openclaw.json"
            )
    
    def _resolve_credentials(self, email: Optional[str], password: Optional[str]) -> tuple:
        """Resolve credentials from multiple sources with priority"""
        # Priority 1: Runtime parameters
        if email and password:
            return email, password
        
        # Priority 2: Environment variables
        env_email = os.environ.get('BEAR_BLOG_EMAIL')
        env_password = os.environ.get('BEAR_BLOG_PASSWORD')
        if env_email and env_password:
            return env_email, env_password
        
        # Priority 3: OpenClaw config file
        config_path = Path.home() / '.openclaw' / 'openclaw.json'
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                skill_config = config.get('skills', {}).get('bear-blog-publisher', {})
                config_email = skill_config.get('email')
                config_password = skill_config.get('password')
                if config_email and config_password:
                    # Check file permissions (should be 600)
                    file_stat = config_path.stat()
                    if file_stat.st_mode & stat.S_IRWXG or file_stat.st_mode & stat.S_IRWXO:
                        print("Warning: Config file is readable by others. Run: chmod 600 ~/.openclaw/openclaw.json")
                    return config_email, config_password
            except (json.JSONDecodeError, KeyError):
                pass
        
        return None, None
    
    def generate_content(self, topic: str, provider: Literal['openai', 'kimi'] = 'openai', 
                        tone: str = 'professional', length: str = 'medium') -> str:
        """
        Generate blog content using AI.
        
        Args:
            topic: What to write about
            provider: LLM provider ('openai' or 'kimi')
            tone: Writing style (professional, casual, technical)
            length: short, medium, or long
            
        Returns:
            Generated markdown content
        """
        length_words = {'short': '300-500', 'medium': '800-1200', 'long': '1500-2500'}
        word_count = length_words.get(length, '800-1200')
        
        prompt = f"""Write a blog post about: {topic}

Requirements:
- Tone: {tone}
- Length: {word_count} words
- Format: Markdown
- Include: Introduction, main content with examples, conclusion
- Use proper markdown formatting (headers, lists, code blocks if relevant)

Write the content now:"""

        if provider == 'openai':
            return self._generate_openai(prompt)
        elif provider == 'kimi':
            return self._generate_kimi(prompt)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _generate_openai(self, prompt: str) -> str:
        """Generate content using OpenAI API"""
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 2000
            }
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    
    def _generate_kimi(self, prompt: str) -> str:
        """Generate content using Kimi API"""
        api_key = os.environ.get('KIMI_API_KEY')
        if not api_key:
            raise ValueError("KIMI_API_KEY environment variable not set")
        
        response = requests.post(
            "https://api.moonshot.cn/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "kimi-k2.5",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 2000
            }
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    
    def upload_image(self, image_path: str) -> Dict[str, Any]:
        """
        Upload an image to Bear Blog and return the URL.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dict with 'success' (bool) and 'url' (str) or 'error' (str)
        """
        try:
            if not os.path.exists(image_path):
                return {'success': False, 'error': f'File not found: {image_path}'}
            
            session = requests.Session()
            
            # Login
            login_page = session.get("https://bearblog.dev/accounts/login/")
            csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', login_page.text)
            if not csrf_match:
                return {'success': False, 'error': 'Could not get CSRF token'}
            
            csrf_token = csrf_match.group(1)
            
            login_data = {
                'csrfmiddlewaretoken': csrf_token,
                'login': self.email,
                'password': self.password,
                'remember': 'on'
            }
            headers = {
                'Referer': 'https://bearblog.dev/accounts/login/',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            }
            
            session.post("https://bearblog.dev/accounts/login/", 
                      data=login_data, headers=headers, allow_redirects=True)
            
            # Upload image
            upload_url = "https://bearblog.dev/cattalk/dashboard/upload-image/"
            with open(image_path, 'rb') as f:
                files = {'file': (os.path.basename(image_path), f, 'image/png')}
                upload_response = session.post(upload_url, files=files,
                                             headers={'Referer': 'https://bearblog.dev/cattalk/dashboard/posts/'})
            
            if upload_response.status_code == 200:
                try:
                    image_urls = json.loads(upload_response.text)
                    if image_urls and len(image_urls) > 0:
                        return {'success': True, 'url': image_urls[0]}
                    else:
                        return {'success': False, 'error': 'No URL returned from upload'}
                except json.JSONDecodeError as e:
                    return {'success': False, 'error': f'Invalid JSON response: {e}'}
            else:
                return {'success': False, 'error': f'HTTP {upload_response.status_code}: {upload_response.text}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def publish(self, title: str, content: str, image_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Publish a blog post.
        
        Args:
            title: Blog post title
            content: Markdown content
            image_path: Optional path to image file
            
        Returns:
            Dict with 'success' (bool) and 'url' (str) or 'error' (str)
        """
        try:
            session = requests.Session()
            
            # Login
            login_page = session.get("https://bearblog.dev/accounts/login/")
            csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', login_page.text)
            if not csrf_match:
                return {'success': False, 'error': 'Could not get CSRF token'}
            
            csrf_token = csrf_match.group(1)
            
            login_data = {
                'csrfmiddlewaretoken': csrf_token,
                'login': self.email,
                'password': self.password,
                'remember': 'on'
            }
            headers = {
                'Referer': 'https://bearblog.dev/accounts/login/',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            }
            
            session.post("https://bearblog.dev/accounts/login/", 
                      data=login_data, headers=headers, allow_redirects=True)
            
            # Upload image if provided
            image_url = None
            if image_path and os.path.exists(image_path):
                try:
                    upload_url = "https://bearblog.dev/cattalk/dashboard/upload-image/"
                    with open(image_path, 'rb') as f:
                        files = {'file': (os.path.basename(image_path), f, 'image/png')}
                        upload_response = session.post(upload_url, files=files,
                                                     headers={'Referer': 'https://bearblog.dev/cattalk/dashboard/posts/'})
                    if upload_response.status_code == 200:
                        try:
                            image_urls = json.loads(upload_response.text)
                            if image_urls and len(image_urls) > 0:
                                image_url = image_urls[0]
                                print(f"Image uploaded: {image_url}")
                        except json.JSONDecodeError:
                            print(f"Image upload response: {upload_response.text}")
                    else:
                        print(f"Image upload failed: HTTP {upload_response.status_code}")
                except Exception as e:
                    print(f"Image upload error: {e}")
            
            # Create post
            new_url = "https://bearblog.dev/cattalk/dashboard/posts/new/"
            new_page = session.get(new_url)
            csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', new_page.text)
            if not csrf_match:
                return {'success': False, 'error': 'Could not get CSRF token for new post'}
            csrf_token = csrf_match.group(1)
            
            # Remove title from content if it exists (Bear Blog auto-displays title)
            body_content = content
            # Remove common title patterns from content
            title_patterns = [
                rf'^#\s*{re.escape(title)}\s*\n?',
                rf'^#\s*.*\n\n',
            ]
            for pattern in title_patterns:
                body_content = re.sub(pattern, '', body_content, flags=re.IGNORECASE)
            
            # Add image at the beginning if uploaded
            if image_url:
                body_content = f"![Image]({image_url})\n\n{body_content}"
            
            header_content = f"title: {title}"
            
            form_data = {
                'csrfmiddlewaretoken': csrf_token,
                'header_content': header_content,
                'body_content': body_content,
                'publish': 'true'
            }
            
            headers['Referer'] = new_url
            response = session.post(new_url, data=form_data, headers=headers, allow_redirects=True)
            
            if response.status_code == 200:
                return {'success': True, 'url': response.url}
            else:
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def generate_diagram(title: str, components: list) -> str:
        """Generate architecture diagram"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #f8f9fa;
    padding: 40px;
}}
.container {{
    width: 1000px;
    margin: 0 auto;
}}
.title {{
    text-align: center;
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 30px;
    color: #1a1a1a;
}}
.diagram {{
    display: flex;
    justify-content: space-between;
    gap: 20px;
}}
.box {{
    flex: 1;
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    border-left: 4px solid #4A90D9;
}}
.box-title {{
    font-weight: bold;
    margin-bottom: 10px;
    color: #4A90D9;
}}
.item {{
    padding: 8px;
    background: #f8f9fa;
    margin-bottom: 8px;
    border-radius: 4px;
    font-size: 14px;
}}
</style>
</head>
<body>
<div class="container">
    <div class="title">{title}</div>
    <div class="diagram">
        {''.join(f'<div class="box"><div class="box-title">{comp}</div></div>' for comp in components)}
    </div>
</div>
</body>
</html>
"""
        
        html_path = '/tmp/diagram.html'
        with open(html_path, 'w') as f:
            f.write(html_content)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
            page = browser.new_page(viewport={'width': 1100, 'height': 400})
            page.goto(f'file://{html_path}')
            page.wait_for_timeout(500)
            screenshot_path = '/tmp/diagram.png'
            page.screenshot(path=screenshot_path, full_page=True)
            browser.close()
        
        return screenshot_path


# CLI interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python publish.py <title> <content_file> [email] [password]")
        print("")
        print("Authentication methods (in priority order):")
        print("  1. Command line arguments: email password")
        print("  2. Environment variables: BEAR_BLOG_EMAIL, BEAR_BLOG_PASSWORD")
        print("  3. Config file: ~/.openclaw/openclaw.json")
        print("")
        print("For AI content generation, set OPENAI_API_KEY or KIMI_API_KEY")
        sys.exit(1)
    
    title = sys.argv[1]
    with open(sys.argv[2], 'r') as f:
        content = f.read()
    
    email = sys.argv[3] if len(sys.argv) > 3 else None
    password = sys.argv[4] if len(sys.argv) > 4 else None
    
    try:
        publisher = BearBlogPublisher(email, password)
        result = publisher.publish(title, content)
        
        if result['success']:
            print(f"Published: {result['url']}")
        else:
            print(f"Error: {result['error']}")
            sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
