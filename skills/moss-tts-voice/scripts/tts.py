import requests, base64, argparse, os, json

def tts():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", required=True)
    parser.add_argument("--voice_id", default="2001286865130360832")
    parser.add_argument("--output", default="output.wav")
    args = parser.parse_args()

    api_key = os.getenv("MOSS_API_KEY")
    url = "https://studio.mosi.cn/v1/audio/tts"
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "moss-tts",
        "text": args.text,
        "voice_id": args.voice_id,
        "sampling_params": {"temperature": 1.7, "top_p": 0.8, "top_k": 25}
    }

    resp = requests.post(url, json=payload, headers=headers)
    data = resp.json()

    if "audio_data" in data:
        with open(args.output, "wb") as f:
            f.write(base64.b64decode(data["audio_data"]))
        print(f"Successfully saved to {args.output}")
    else:
        print(f"Error: {data}")

if __name__ == "__main__":
    tts()