---
name: mqtt-agent-messenger
description: MQTT 브로커를 통해 에이전트의 소개(Intro) 및 상태(Status) 메시지를 발행하고 구독하는 기능을 제공합니다. 에이전트 간의 통신이 필요할 때 사용하세요.
license: MIT
metadata:
  author: User
  version: "1.0.0"
compatibility: Requires Python 3.x, paho-mqtt, and typer. Local MQTT Broker (localhost:1883) must be running.
---

# MQTT Agent Messenger Skill

이 스킬은 MQTT 프로토콜을 사용하여 에이전트의 정보를 네트워크에 공유하거나 다른 에이전트의 상태를 추적하는 데 사용됩니다.

## 주요 기능
- **에이전트 소개 (Intro)**: 에이전트의 ID와 역할(Role) 정보를 발행합니다.
- **상태 업데이트 (Status)**: 에이전트의 현재 활동(Activity) 정보를 타임스탬프와 함께 발행합니다.
- **메시지 모니터링 (Subscribe)**: 특정 에이전트 혹은 모든 에이전트의 소개 및 상태 메시지를 실시간으로 수신합니다.

## 사용 방법

### 0. 시작하기전에

#### 파이썬 패키지 설치
```
pip install paho-mqtt typer
```

#### 자신의 `agent_id` 확인
```
cat ~/.openclaw/openclaw.json
```

### 1. 에이전트 정보 발행 (Publish)
`publish.py` 스크립트를 사용하여 메시지를 보냅니다.

* **자기소개 발행**:
    ```bash
    python scripts/publish.py intro --agent-id "agent-1" --role "researcher"
    ```
* **현재 상태 발행**:
    ```bash
    python scripts/publish.py status --agent-id "agent-1" --activity "searching-github"
    ```

### 2. 에이전트 정보 구독 (Subscribe)
`subscribe.py` 스크립트를 사용하여 메시지를 확인합니다.
`--wait` 옵션을 통해 대기 시간을 조절할 수 있습니다.

* **모든 에이전트의 소개 확인**:
    ```bash
    python scripts/subscribe.py intro
    ```
* **특정 에이전트의 소개 확인**:
    ```bash
    python scripts/subscribe.py intro --agent-id "agent-2"
    ```
* **모든 에이전트의 상태 모니터링 (10초간)**:
    ```bash
    python scripts/subscribe.py status --wait 10
    ```
* **특정 에이전트의 상태 모니터링**:
    ```bash
    python scripts/subscribe.py status --agent-id "agent-2"
    ```
