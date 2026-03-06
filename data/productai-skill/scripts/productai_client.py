"""
ProductAI API Client

Python client for interacting with the ProductAI.photo API.
"""

import json
import time
import re
from pathlib import Path
from typing import Optional, Union, List
from urllib.parse import urlparse
import requests


class ProductAIClient:
    """Client for ProductAI.photo API."""
    
    # Default request timeout in seconds
    DEFAULT_TIMEOUT = 30
    
    def __init__(self, api_key: str, api_endpoint: str = "https://api.productai.photo/v1"):
        """
        Initialize ProductAI client.
        
        Args:
            api_key: Your ProductAI API key
            api_endpoint: API base URL (default: https://api.productai.photo/v1)
        """
        self.api_key = api_key
        self.api_endpoint = api_endpoint.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'x-api-key': api_key,
            'Content-Type': 'application/json'
        })
    
    @staticmethod
    def validate_image_url(url: str) -> None:
        """
        Validate image URL for security.
        
        Args:
            url: URL to validate
        
        Raises:
            ValueError: If URL is invalid or insecure
        """
        parsed = urlparse(url)
        
        # Only allow HTTPS
        if parsed.scheme != 'https':
            raise ValueError(f"Only HTTPS URLs are allowed. Got: {parsed.scheme}://")
        
        # Block private/local network addresses (SSRF prevention)
        hostname = parsed.hostname
        if not hostname:
            raise ValueError("Invalid URL: missing hostname")
        
        # Block localhost, private IPs, link-local
        blocked_patterns = [
            r'^localhost$',
            r'^127\.',
            r'^10\.',
            r'^172\.(1[6-9]|2[0-9]|3[01])\.',
            r'^192\.168\.',
            r'^169\.254\.',
            r'^::1$',
            r'^fe80:',
        ]
        
        for pattern in blocked_patterns:
            if re.match(pattern, hostname, re.IGNORECASE):
                raise ValueError(f"Private/local addresses are not allowed: {hostname}")
    
    def generate(
        self,
        image_url: Union[str, List[str]],
        prompt: str,
        model: str = "nanobanana"
    ) -> dict:
        """
        Generate AI-powered product image.
        
        Args:
            image_url: URL(s) of source image(s). Can be:
                      - Single URL string for one image
                      - List of URLs for multiple reference images (seedream, nanobanana, nanobananapro support 2 images)
            prompt: Text description of desired output
            model: Model to use. Options:
                  - gpt-low (2 tokens)
                  - gpt-medium (3 tokens)
                  - gpt-high (8 tokens)
                  - kontext-pro (3 tokens)
                  - nanobanana (3 tokens)
                  - nanobananapro (8 tokens)
                  - seedream (3 tokens)
        
        Returns:
            dict with job_id and status
        
        Raises:
            requests.HTTPError: If API request fails
            ValueError: If image URL is invalid
        """
        # Validate image URLs
        urls_to_validate = [image_url] if isinstance(image_url, str) else image_url
        for url in urls_to_validate:
            self.validate_image_url(url)
        
        payload = {
            "model": model,
            "image_url": image_url,
            "prompt": prompt
        }
        
        response = self.session.post(
            f"{self.api_endpoint}/api/generate",
            json=payload,
            timeout=self.DEFAULT_TIMEOUT
        )
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('status') != 'OK':
            raise Exception(f"API error: {data}")
        
        return data['data']
    
    def upscale(self, image_url: str) -> dict:
        """
        Upscale an image using AI (20 tokens).
        
        Args:
            image_url: URL of the image to upscale
        
        Returns:
            dict with job_id and status
        
        Raises:
            requests.HTTPError: If API request fails
            ValueError: If image URL is invalid
        """
        # Validate image URL
        self.validate_image_url(image_url)
        
        payload = {
            "image_url": image_url
        }
        
        response = self.session.post(
            f"{self.api_endpoint}/api/upscale",
            json=payload,
            timeout=self.DEFAULT_TIMEOUT
        )
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('status') != 'OK':
            raise Exception(f"API error: {data}")
        
        return data['data']
    
    def get_job_status(self, job_id: int) -> dict:
        """
        Check the status of a generation job.
        
        Args:
            job_id: Job ID returned from generate() or upscale()
        
        Returns:
            dict with status, and image_url if completed
        
        Raises:
            requests.HTTPError: If API request fails
        """
        response = self.session.get(
            f"{self.api_endpoint}/api/job/{job_id}",
            timeout=self.DEFAULT_TIMEOUT
        )
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('status') != 'OK':
            raise Exception(f"API error: {data}")
        
        return data['data']
    
    def wait_for_completion(
        self,
        job_id: int,
        poll_interval: int = 5,
        timeout: int = 300
    ) -> str:
        """
        Poll job status until completion.
        
        Args:
            job_id: Job ID to monitor
            poll_interval: Seconds to wait between checks (default: 5)
            timeout: Maximum seconds to wait (default: 300)
        
        Returns:
            str: URL of generated image
        
        Raises:
            TimeoutError: If job doesn't complete within timeout
            Exception: If job fails
        """
        start_time = time.time()
        
        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise TimeoutError(f"Job {job_id} did not complete within {timeout} seconds")
            
            status_data = self.get_job_status(job_id)
            status = status_data.get('status')
            
            if status == 'COMPLETED':
                return status_data['image_url']
            elif status == 'ERROR':
                raise Exception(f"Job {job_id} failed")
            elif status == 'RUNNING':
                time.sleep(poll_interval)
            else:
                raise Exception(f"Unknown status: {status}")
    
    def generate_and_wait(
        self,
        image_url: Union[str, List[str]],
        prompt: str,
        model: str = "nanobanana",
        poll_interval: int = 5,
        timeout: int = 300
    ) -> str:
        """
        Generate image and wait for completion (convenience method).
        
        Args:
            image_url: URL(s) of source image(s)
            prompt: Text description
            model: Model to use
            poll_interval: Seconds between status checks
            timeout: Maximum wait time
        
        Returns:
            str: URL of generated image
        """
        job = self.generate(image_url, prompt, model)
        job_id = job['id']
        
        print(f"Job {job_id} started. Waiting for completion...")
        return self.wait_for_completion(job_id, poll_interval, timeout)
    
    def upscale_and_wait(
        self,
        image_url: str,
        poll_interval: int = 5,
        timeout: int = 300
    ) -> str:
        """
        Upscale image and wait for completion (convenience method).
        
        Args:
            image_url: URL of image to upscale
            poll_interval: Seconds between status checks
            timeout: Maximum wait time
        
        Returns:
            str: URL of upscaled image
        """
        job = self.upscale(image_url)
        job_id = job['id']
        
        print(f"Upscale job {job_id} started. Waiting for completion...")
        return self.wait_for_completion(job_id, poll_interval, timeout)


def load_config(config_path: Optional[Path] = None) -> dict:
    """
    Load ProductAI configuration.
    
    Args:
        config_path: Path to config file (default: ~/.openclaw/workspace/productai/config.json)
    
    Returns:
        dict: Configuration data
    
    Raises:
        FileNotFoundError: If config file doesn't exist
    """
    if config_path is None:
        config_path = Path.home() / '.openclaw' / 'workspace' / 'productai' / 'config.json'
    
    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}\n"
            f"Run scripts/setup.py to create it."
        )
    
    with open(config_path) as f:
        return json.load(f)


def create_client_from_config(config_path: Optional[Path] = None) -> ProductAIClient:
    """
    Create ProductAI client from configuration file.
    
    Args:
        config_path: Path to config file
    
    Returns:
        ProductAIClient instance
    """
    config = load_config(config_path)
    return ProductAIClient(
        api_key=config['api_key'],
        api_endpoint=config.get('api_endpoint', 'https://api.productai.photo/v1')
    )
