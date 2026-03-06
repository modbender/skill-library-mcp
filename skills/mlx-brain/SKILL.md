---
name: MLX Brain - 맥북 MLX LLM 오케스트레이터
description: mlx brain
---

# MLX Brain - 맥북 MLX LLM 오케스트레이터

## 설치 (맥북)
```bash
# venv 이미 생성됨: $HOME/mlx-env
# MLX 이미 설치됨

# 테스트
$HOME/mlx-env/bin/python3 $WORKSPACE/misskim-skills/mlx-brain/run.py "안녕?"
```

## 사용법 (미스 김)
```bash
# 맥북에서 LLM 실행
clawdbot nodes invoke --node "MacBook Pro" --command "system.run" \
  --params '{"command":"$HOME/mlx-env/bin/python3 $WORKSPACE/misskim-skills/mlx-brain/run.py \"안녕?\""}'

# JSON 입력
echo '{"prompt":"안녕?","model":"qwen"}' | \
  clawdbot nodes invoke --node "MacBook Pro" --command "system.run" \
  --params '{"command":"$HOME/mlx-env/bin/python3 $WORKSPACE/misskim-skills/mlx-brain/run.py --json"}'
```

## 모델
- `qwen`: Qwen2.5-7B-Instruct-4bit (메인)
- `coder`: Qwen2.5-Coder-7B-4bit (코딩)
