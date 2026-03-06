#!/usr/bin/env python3
"""
Open WebUI CLI Tool
Complete API client for Open WebUI - models, chat, files, knowledge, Ollama proxy.

Environment Variables:
    OPENWEBUI_URL: Base URL of Open WebUI instance (default: http://localhost:3000)
    OPENWEBUI_TOKEN: API key from Settings > Account

Usage:
    python3 openwebui-cli.py models list
    python3 openwebui-cli.py chat --model llama3.2 --message "Hello"
    python3 openwebui-cli.py files upload --file document.pdf
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib.parse import urljoin
except ImportError:
    print("Error: 'requests' library required. Install with: pip install requests")
    sys.exit(1)


class OpenWebUIClient:
    """Client for Open WebUI API interactions."""

    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        self.base_url = (base_url or os.getenv("OPENWEBUI_URL", "http://localhost:3000")).rstrip("/")
        self.token = token or os.getenv("OPENWEBUI_TOKEN")
        
        if not self.token:
            raise ValueError("API token required. Set OPENWEBUI_TOKEN or use --token")
        
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        })
        
        # Allow insecure transport for local development (localhost)
        if self.base_url.startswith("http://localhost") or self.base_url.startswith("http://127.0.0.1"):
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def _url(self, endpoint: str) -> str:
        """Build full URL from endpoint."""
        return urljoin(self.base_url + "/", endpoint.lstrip("/"))

    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Execute HTTP request with error handling."""
        url = self._url(endpoint)
        verify = not (self.base_url.startswith("http://localhost") or self.base_url.startswith("http://127.0.0.1"))
        
        try:
            response = self.session.request(method, url, verify=verify, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP {e.response.status_code}"
            try:
                detail = e.response.json()
                error_msg += f": {detail}"
            except:
                error_msg += f": {e.response.text}"
            print(f"Error: {error_msg}", file=sys.stderr)
            sys.exit(1)
        except requests.exceptions.ConnectionError:
            print(f"Error: Cannot connect to {self.base_url}. Check OPENWEBUI_URL.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    def mask_token(self, token: str) -> str:
        """Redact token for safe logging."""
        if len(token) > 8:
            return f"{token[:4]}...{token[-4:]}"
        return "****"

    # Models
    def list_models(self) -> dict:
        """GET /api/models - List all available models."""
        return self._request("GET", "/api/models")

    def list_ollama_models(self) -> dict:
        """GET /ollama/api/tags - List Ollama models."""
        return self._request("GET", "/ollama/api/tags")

    def get_ollama_status(self) -> dict:
        """GET /ollama/ - Check Ollama connection status."""
        return self._request("GET", "/ollama/")

    # Chat
    def chat_completion(self, model: str, message: str, stream: bool = False, files: Optional[list] = None) -> dict:
        """POST /api/chat/completions - OpenAI-compatible chat."""
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": message}],
            "stream": stream
        }
        if files:
            payload["files"] = files
        return self._request("POST", "/api/chat/completions", json=payload)

    # Files & RAG
    def upload_file(self, file_path: str, process: bool = True) -> dict:
        """POST /api/v1/files/ - Upload file for RAG."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        url = self._url("/api/v1/files/")
        verify = not (self.base_url.startswith("http://localhost") or self.base_url.startswith("http://127.0.0.1"))
        
        headers = {"Authorization": f"Bearer {self.token}"}
        # Remove Content-Type for multipart
        
        params = {"process": process, "process_in_background": True}
        
        with open(path, "rb") as f:
            files = {"file": (path.name, f, "application/octet-stream")}
            response = requests.post(url, headers=headers, files=files, params=params, verify=verify)
            response.raise_for_status()
            return response.json()

    def get_file_status(self, file_id: str) -> dict:
        """GET /api/v1/files/{id}/process/status - Check processing status."""
        return self._request("GET", f"/api/v1/files/{file_id}/process/status")

    def wait_for_file(self, file_id: str, timeout: int = 300, poll_interval: int = 2) -> dict:
        """Poll file status until completed or failed."""
        start = time.time()
        while time.time() - start < timeout:
            status = self.get_file_status(file_id)
            state = status.get("status")
            if state == "completed":
                return status
            elif state == "failed":
                raise Exception(f"Processing failed: {status.get('error', 'Unknown error')}")
            time.sleep(poll_interval)
        raise TimeoutError(f"File processing did not complete within {timeout}s")

    # Knowledge
    def list_knowledge(self) -> list:
        """GET /api/v1/knowledge/ - List knowledge collections."""
        return self._request("GET", "/api/v1/knowledge/")

    def create_knowledge(self, name: str, description: str = "") -> dict:
        """POST /api/v1/knowledge/create - Create knowledge collection."""
        payload = {"name": name, "description": description}
        return self._request("POST", "/api/v1/knowledge/create", json=payload)

    def add_file_to_knowledge(self, knowledge_id: str, file_id: str) -> dict:
        """POST /api/v1/knowledge/{id}/file/add - Add file to collection."""
        payload = {"file_id": file_id}
        return self._request("POST", f"/api/v1/knowledge/{knowledge_id}/file/add", json=payload)

    # Ollama Operations
    def ollama_generate(self, model: str, prompt: str, stream: bool = False) -> dict:
        """POST /ollama/api/generate - Generate completion."""
        payload = {"model": model, "prompt": prompt, "stream": stream}
        return self._request("POST", "/ollama/api/generate", json=payload)

    def ollama_embed(self, model: str, input_text: str) -> dict:
        """POST /ollama/api/embed - Generate embeddings."""
        payload = {"model": model, "input": [input_text] if isinstance(input_text, str) else input_text}
        return self._request("POST", "/ollama/api/embed", json=payload)

    def ollama_pull(self, model: str) -> dict:
        """POST /ollama/api/pull - Pull/download model."""
        payload = {"name": model}
        return self._request("POST", "/ollama/api/pull", json=payload)

    def ollama_delete(self, model: str) -> dict:
        """DELETE /ollama/api/delete - Delete model."""
        payload = {"name": model}
        return self._request("DELETE", "/ollama/api/delete", json=payload)


def print_json(data: dict):
    """Pretty print JSON."""
    print(json.dumps(data, indent=2))


def confirm(prompt: str) -> bool:
    """Ask for confirmation."""
    response = input(f"{prompt} [y/N]: ").strip().lower()
    return response in ("y", "yes")


def main():
    parser = argparse.ArgumentParser(
        description="Open WebUI CLI - Complete API client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  OPENWEBUI_URL     Open WebUI instance URL (default: http://localhost:3000)
  OPENWEBUI_TOKEN   API key from Settings > Account

Examples:
  %(prog)s models list
  %(prog)s chat --model llama3.2 --message "Hello"
  %(prog)s files upload --file doc.pdf
"""
    )
    parser.add_argument("--url", help="Open WebUI URL (overrides env var)")
    parser.add_argument("--token", help="API token (overrides env var)")

    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Models
    models_cmd = subparsers.add_parser("models", help="Model operations")
    models_sub = models_cmd.add_subparsers(dest="subcommand")
    models_sub.add_parser("list", help="List all models")
    models_sub.add_parser("ollama", help="List Ollama models")

    # Chat
    chat_cmd = subparsers.add_parser("chat", help="Chat completion")
    chat_cmd.add_argument("--model", "-m", required=True, help="Model name")
    chat_cmd.add_argument("--message", "-msg", required=True, help="User message")
    chat_cmd.add_argument("--stream", action="store_true", help="Stream response")
    chat_cmd.add_argument("--file-id", help="File ID for RAG context")
    chat_cmd.add_argument("--collection-id", help="Knowledge collection ID for RAG")

    # Files
    files_cmd = subparsers.add_parser("files", help="File operations")
    files_sub = files_cmd.add_subparsers(dest="subcommand")
    
    upload_cmd = files_sub.add_parser("upload", help="Upload file for RAG")
    upload_cmd.add_argument("--file", "-f", required=True, help="File path")
    upload_cmd.add_argument("--no-process", action="store_true", help="Don't process file immediately")
    upload_cmd.add_argument("--wait", "-w", action="store_true", help="Wait for processing to complete")
    
    status_cmd = files_sub.add_parser("status", help="Check file processing status")
    status_cmd.add_argument("file_id", help="File ID")

    # Knowledge
    knowledge_cmd = subparsers.add_parser("knowledge", help="Knowledge base operations")
    knowledge_sub = knowledge_cmd.add_subparsers(dest="subcommand")
    knowledge_sub.add_parser("list", help="List collections")
    
    create_know_cmd = knowledge_sub.add_parser("create", help="Create collection")
    create_know_cmd.add_argument("--name", "-n", required=True, help="Collection name")
    create_know_cmd.add_argument("--description", "-d", default="", help="Description")
    
    add_file_cmd = knowledge_sub.add_parser("add-file", help="Add file to collection")
    add_file_cmd.add_argument("--collection-id", "-c", required=True, help="Collection ID")
    add_file_cmd.add_argument("--file-id", "-f", required=True, help="File ID")

    # Ollama
    ollama_cmd = subparsers.add_parser("ollama", help="Ollama proxy operations")
    ollama_sub = ollama_cmd.add_subparsers(dest="subcommand")
    ollama_sub.add_parser("status", help="Check Ollama status")
    
    pull_cmd = ollama_sub.add_parser("pull", help="Pull/download model")
    pull_cmd.add_argument("--model", "-m", required=True, help="Model name")
    
    delete_cmd = ollama_sub.add_parser("delete", help="Delete model")
    delete_cmd.add_argument("--model", "-m", required=True, help="Model name")
    
    generate_cmd = ollama_sub.add_parser("generate", help="Generate completion")
    generate_cmd.add_argument("--model", "-m", required=True, help="Model name")
    generate_cmd.add_argument("--prompt", "-p", required=True, help="Prompt text")
    
    embed_cmd = ollama_sub.add_parser("embed", help="Generate embeddings")
    embed_cmd.add_argument("--model", "-m", required=True, help="Embedding model")
    embed_cmd.add_argument("--input", "-i", required=True, help="Input text")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        client = OpenWebUIClient(base_url=args.url, token=args.token)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("Set OPENWEBUI_TOKEN environment variable or use --token", file=sys.stderr)
        sys.exit(1)

    # Execute commands
    try:
        if args.command == "models":
            if args.subcommand == "list":
                print_json(client.list_models())
            elif args.subcommand == "ollama":
                print_json(client.list_ollama_models())
            else:
                models_cmd.print_help()

        elif args.command == "chat":
            files = None
            if args.file_id:
                files = [{"type": "file", "id": args.file_id}]
            elif args.collection_id:
                files = [{"type": "collection", "id": args.collection_id}]
            
            response = client.chat_completion(
                model=args.model,
                message=args.message,
                stream=args.stream,
                files=files
            )
            if args.stream:
                print(response)  # Handle streaming differently if needed
            else:
                print_json(response)

        elif args.command == "files":
            if args.subcommand == "upload":
                print(f"Uploading {args.file}...")
                result = client.upload_file(args.file, process=not args.no_process)
                print_json(result)
                file_id = result.get("id")
                if args.wait and not args.no_process:
                    print(f"Waiting for processing of file {file_id}...")
                    status = client.wait_for_file(file_id)
                    print("Processing complete!")
                    print_json(status)
            elif args.subcommand == "status":
                print_json(client.get_file_status(args.file_id))
            else:
                files_cmd.print_help()

        elif args.command == "knowledge":
            if args.subcommand == "list":
                print_json(client.list_knowledge())
            elif args.subcommand == "create":
                print_json(client.create_knowledge(args.name, args.description))
            elif args.subcommand == "add-file":
                print_json(client.add_file_to_knowledge(args.collection_id, args.file_id))
            else:
                knowledge_cmd.print_help()

        elif args.command == "ollama":
            if args.subcommand == "status":
                print_json(client.get_ollama_status())
            elif args.subcommand == "pull":
                if confirm(f"This will download model '{args.model}'. Continue?"):
                    print(f"Pulling model {args.model}... (this may take a while)")
                    print_json(client.ollama_pull(args.model))
                else:
                    print("Cancelled.")
            elif args.subcommand == "delete":
                if confirm(f"⚠️ WARNING: This will permanently delete model '{args.model}'. Continue?"):
                    print_json(client.ollama_delete(args.model))
                else:
                    print("Cancelled.")
            elif args.subcommand == "generate":
                print_json(client.ollama_generate(args.model, args.prompt))
            elif args.subcommand == "embed":
                print_json(client.ollama_embed(args.model, args.input))
            else:
                ollama_cmd.print_help()

        else:
            parser.print_help()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
