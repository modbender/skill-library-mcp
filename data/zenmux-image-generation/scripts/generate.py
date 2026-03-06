import argparse
import os
import requests
import json
import base64
import mimetypes

# --- Argument Parsing ---
ap = argparse.ArgumentParser(description="Generate an image via ZenMux API (Supports Multi-Image-to-Image).")
ap.add_argument("--prompt", required=True, help="Text prompt for the image.")
ap.add_argument("--images", nargs="+", help="Paths to one or more reference images for generation.")
ap.add_argument("--model", default="google/gemini-3-pro-image-preview", help="The model to use for generation.")
ap.add_argument("--output", default="generated_image.png", help="Output file name for the image.")
args = ap.parse_args()

# --- API Configuration ---
api_key = os.environ.get("ZENMUX_API_KEY")
base_url = "https://zenmux.ai/api/vertex-ai"

if not api_key:
    print("Error: ZENMUX_API_KEY environment variable is not set.")
    exit(1)

# --- Image Generation Logic ---
try:
    print(f"Starting image generation with model: {args.model}")
    url = f"{base_url}/v1/models/{args.model}:generateContent"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Build parts list
    parts = [{"text": args.prompt}]

    # Add image data if provided (supports multiple images)
    if args.images:
        for img_path in args.images:
            if not os.path.exists(img_path):
                print(f"Error: Image file not found at {img_path}")
                continue # Skip missing files
            
            mime_type, _ = mimetypes.guess_type(img_path)
            if not mime_type:
                mime_type = "image/png" # Default fallback
                
            with open(img_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
                parts.append({
                    "inlineData": {
                        "mimeType": mime_type,
                        "data": encoded_string
                    }
                })
            print(f"Reference image added: {img_path} ({mime_type})")

    data = {
        "contents": [
            {
                "role": "user",
                "parts": parts
            }
        ],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"]
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    print(f"Request sent. Response status code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        if "candidates" in result and result["candidates"]:
            for candidate in result["candidates"]:
                if "content" in candidate and "parts" in candidate["content"]:
                    for part in candidate["content"]["parts"]:
                        if "inlineData" in part and "data" in part["inlineData"]:
                            print("Image data found in response.")
                            image_data = base64.b64decode(part['inlineData']['data'])
                            with open(args.output, "wb") as f:
                                f.write(image_data)
                            print(f"Success! Image saved to: {args.output}")
                            exit(0) # Success
        print("Error: Image data not found in the successful response.")
    else:
        print(f"Error: API returned status {response.status_code}")
        print(f"Response body: {response.text}")

except Exception as e:
    print(f"An unexpected error occurred: {e}")

# If we reach here, it means something went wrong
exit(1)
