import json, sys
from vosk import Model, KaldiRecognizer
import wave

def transcribe(audio_path: str) -> str:
    wf = wave.open(audio_path, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
        raise ValueError("音频必须是 16kHz 单声道 16bit WAV")
    model = Model("model")  # 请确保 model 目录下有 Vosk 模型
    recognizer = KaldiRecognizer(model, wf.getframerate())
    result = ""
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if recognizer.AcceptWaveform(data):
            result += json.loads(recognizer.Result())["text"] + " "
    result += json.loads(recognizer.FinalResult())["text"]
    return result.strip()

def run(params: dict) -> dict:
    audio = params.get("audio")
    if not audio:
        raise ValueError("需要 audio 参数（文件路径）")
    return {"text": transcribe(audio)}

if __name__ == "__main__":
    # 本地调试示例：python main.py '{"audio": "sample.wav"}'
    args = json.loads(sys.argv[1])
    print(json.dumps(run(args), ensure_ascii=False))
