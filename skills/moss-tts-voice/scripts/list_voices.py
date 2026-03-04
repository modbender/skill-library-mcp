import requests, os, json

def list_voices():
    api_key = os.getenv("MOSS_API_KEY")
    url = "https://studio.mosi.cn/api/v1/voices?limit=10&status=ACTIVE"
    headers = {"Authorization": f"Bearer {api_key}"}

    resp = requests.get(url, headers=headers)
    voices = resp.json().get("voices", [])
    
    print("| Voice Name | Voice ID | Description |")
    print("|---|---|---|")
    for v in voices:
        print(f"| {v['voice_name']} | {v['voice_id']} | {v.get('transcription_text', 'N/A')[:20]}... |")

if __name__ == "__main__":
    list_voices()