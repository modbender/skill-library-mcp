#!/usr/bin/env python3
"""
MLX Brain - 맥북 MLX LLM 실행기
사용: ./run.py "프롬프트" 또는 echo '{"prompt":"프롬프트"}' | ./run.py --json
"""

import sys
import json
from mlx_lm import load, generate

# 모델 설정 (첫 실행 시 자동 다운로드)
MODELS = {
    "qwen": "mlx-community/Qwen2.5-7B-Instruct-4bit",
    "coder": "mlx-community/Qwen2.5-Coder-7B-4bit",
}

def run_mlx(prompt: str, model_name: str = "qwen") -> str:
    """MLX로 추론"""
    model_id = MODELS.get(model_name, MODELS["qwen"])

    # 모델 로드
    model, tokenizer = load(model_id)

    # 추론
    result = generate(
        model,
        tokenizer,
        prompt=prompt,
        max_tokens=512,
        verbose=False
    )

    return result.strip()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--json":
            # JSON 모드: STDIN에서 JSON 읽기
            data = json.loads(sys.stdin.read())
            prompt = data.get("prompt", "")
            model_name = data.get("model", "qwen")
            result = run_mlx(prompt, model_name)
            print(json.dumps({"result": result}, ensure_ascii=False))
        elif sys.argv[1] == "--help":
            print("사용: ./run.py \"프롬프트\" 또는 echo '{\"prompt\":\"프롬프트\"}' | ./run.py --json")
        else:
            # 간단 모드: 인자로 프롬프트
            prompt = " ".join(sys.argv[1:])
            print(run_mlx(prompt))
    else:
        print("사용: ./run.py \"프롬프트\" 또는 echo '{\"prompt\":\"프롬프트\"}' | ./run.py --json")
