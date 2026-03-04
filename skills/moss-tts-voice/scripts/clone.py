import requests, os, argparse

def clone_voice():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--name", default="ClonedVoice")
    args = parser.parse_args()

    api_key = os.getenv("MOSS_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}"}

    # 1. Upload
    with open(args.file, "rb") as f:
        up_resp = requests.post("https://studio.mosi.cn/api/v1/files", 
                               headers=headers, files={"file": f})
    file_id = up_resp.json().get("file_id")

    # 2. Clone
    payload = {"file_id": file_id, "voice_name": args.name}
    cl_resp = requests.post("https://studio.mosi.cn/api/v1/voice/clone", 
                            headers=headers, json=payload)
    print(cl_resp.text)

if __name__ == "__main__":
    clone_voice()