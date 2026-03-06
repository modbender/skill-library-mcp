#!/usr/bin/env python3
"""
xAI Grok Imagine Video API Client
Handles text-to-video, image-to-video, and video editing via natural language.
"""

import requests
import time
import json
import os
from typing import Optional, Dict, Any


class GrokImagineVideoClient:
    """Client for interacting with xAI Grok Imagine Video API."""

    def __init__(self, api_key: str, base_url: str = "https://api.x.ai/v1"):
        """
        Initialize the client.

        Args:
            api_key: xAI API key from environment or config
            base_url: API base URL (default: https://api.x.ai/v1)
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def text_to_video(
        self,
        prompt: str,
        duration: int = 10,
        aspect_ratio: str = "16:9",
        resolution: str = "480p"
    ) -> Dict[str, Any]:
        """
        Generate video from text prompt.

        Args:
            prompt: Text description of the video to generate
            duration: Video duration in seconds (1-15)
            aspect_ratio: Aspect ratio (16:9, 9:16, 1:1, 4:3, 3:4, 3:2, 2:3)
            resolution: Resolution (480p, 720p)

        Returns:
            API response with request_id
        """
        url = f"{self.base_url}/videos/generations"
        payload = {
            "model": "grok-imagine-video",
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution
        }

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def image_to_video(
        self,
        image_url: str,
        prompt: str = "",
        duration: int = 10
    ) -> Dict[str, Any]:
        """
        Animate a static image into video.

        Args:
            image_url: Public URL of the source image OR base64 data URI
            prompt: Optional text prompt to guide animation
            duration: Video duration in seconds (1-15)

        Returns:
            API response with request_id
        """
        url = f"{self.base_url}/videos/generations"
        payload = {
            "model": "grok-imagine-video",
            "prompt": prompt,
            "image": {"url": image_url},
            "duration": duration
        }

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def edit_video(
        self,
        video_url: str,
        edit_prompt: str
    ) -> Dict[str, Any]:
        """
        Edit an existing video via natural language instruction.

        Args:
            video_url: Public URL of the source video
            edit_prompt: Natural language instruction for the edit

        Returns:
            API response with request_id
        """
        url = f"{self.base_url}/videos/generations"
        payload = {
            "model": "grok-imagine-video",
            "prompt": edit_prompt,
            "video_url": video_url
        }

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def generate_image(
        self,
        prompt: str,
        n: int = 1,
        aspect_ratio: str = "1:1",
        response_format: str = "url"
    ) -> Dict[str, Any]:
        """
        Generate images from a text prompt.

        Args:
            prompt: Text description of the image to generate
            n: Number of image variations (1-10)
            aspect_ratio: Aspect ratio (1:1, 16:9, 9:16, 4:3, 3:4, 3:2, 2:3, etc.)
            response_format: "url" for temporary URL or "b64_json" for base64 data

        Returns:
            API response with image URL(s) or base64 data
        """
        url = f"{self.base_url}/images/generations"
        payload = {
            "model": "grok-imagine-image",
            "prompt": prompt,
            "n": n,
            "aspect_ratio": aspect_ratio,
            "response_format": response_format
        }

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def edit_image(
        self,
        image_url: str,
        prompt: str,
        n: int = 1,
        response_format: str = "url"
    ) -> Dict[str, Any]:
        """
        Edit an existing image via natural language instruction.

        Args:
            image_url: Public URL or base64 data URI of the source image
            prompt: Natural language instruction for the edit
            n: Number of variations (1-10)
            response_format: "url" for temporary URL or "b64_json" for base64 data

        Returns:
            API response with edited image URL(s) or base64 data
        """
        url = f"{self.base_url}/images/edits"
        payload = {
            "model": "grok-imagine-image",
            "prompt": prompt,
            "image": {"url": image_url, "type": "image_url"},
            "n": n,
            "response_format": response_format
        }

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def download_image(self, image_url: str, output_path: str) -> str:
        """
        Download a generated image file.

        Args:
            image_url: URL of the generated image
            output_path: Local path to save the image

        Returns:
            Path to the downloaded file
        """
        response = requests.get(image_url, stream=True)
        response.raise_for_status()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return output_path

    def get_job_status(self, request_id: str) -> Dict[str, Any]:
        """
        Check the status of a video generation request.

        Args:
            request_id: The request ID from the initial generation request

        Returns:
            Job status with fields: status (if pending), video (if done)
        """
        url = f"{self.base_url}/videos/{request_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def wait_for_completion(
        self,
        request_id: str,
        poll_interval: int = 10,
        timeout: int = 600,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Poll job status until completion or timeout.

        Args:
            request_id: The request ID to poll
            poll_interval: Seconds between status checks
            timeout: Maximum seconds to wait
            progress_callback: Optional function called with progress updates

        Returns:
            Final response with video_url if successful

        Raises:
            TimeoutError: If job doesn't complete within timeout
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            response = self.get_job_status(request_id)

            if progress_callback:
                progress_callback(response)

            # Check if video is done (response has video object)
            if "video" in response and response.get("video", {}).get("url"):
                return response

            # If not done, wait and retry
            time.sleep(poll_interval)

        raise TimeoutError(f"Request {request_id} timed out after {timeout} seconds")

    def download_video(self, response_data: Dict[str, Any], output_path: str) -> str:
        """
        Download a completed video file.

        Args:
            response_data: Response from get_job_status (contains video.url)
            output_path: Local path to save the video

        Returns:
            Path to the downloaded file
        """
        video_url = response_data.get("video", {}).get("url")
        if not video_url:
            raise ValueError("No video URL in response")

        response = requests.get(video_url, stream=True)
        response.raise_for_status()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return output_path


def main():
    """Example usage."""
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        print("Error: XAI_API_KEY environment variable not set")
        return 1

    client = GrokImagineVideoClient(api_key)

    # Choose mode:
    # 1. Text-to-video
    # 2. Image-to-video
    # 3. Video editing

    mode = "text"  # Change to "image" or "edit" for other modes

    if mode == "text":
        # Example: Text-to-video
        print("Starting text-to-video generation...")
        result = client.text_to_video("A beautiful sunset over the ocean", duration=10)
        request_id = result.get("request_id")
        print(f"Job started: {request_id}")

    elif mode == "image":
        # Example: Image-to-video
        print("Starting image-to-video generation...")
        result = client.image_to_video(
            image_url="https://example.com/landscape.jpg",
            prompt="Animate the clouds and add gentle wind",
            duration=10
        )
        request_id = result.get("request_id")
        print(f"Job started: {request_id}")

    elif mode == "edit":
        # Example: Video editing
        print("Starting video edit...")
        result = client.edit_video(
            video_url="https://example.com/source.mp4",
            edit_prompt="Add a warm sunset filter"
        )
        request_id = result.get("request_id")
        print(f"Job started: {request_id}")

    # Wait for completion
    print("Waiting for completion...")
    final_response = client.wait_for_completion(
        request_id,
        progress_callback=lambda r: print(f"Polling... {'Done!' if 'video' in r else 'Pending'}")
    )

    video_url = final_response.get("video", {}).get("url")
    print(f"Video ready: {video_url}")

    # Download
    output_path = "/tmp/video_output.mp4"
    client.download_video(final_response, output_path)
    print(f"Downloaded to: {output_path}")

    return 0


if __name__ == "__main__":
    exit(main())
