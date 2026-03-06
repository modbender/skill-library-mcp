---
name: playwright-testing
description: Test web applications and games using Playwright on MiniPC. Use when verifying frontend functionality, debugging UI behavior, capturing screenshots, or QA testing games. Supports headless browser automation via nodes.run or browser.proxy.
metadata:
  author: misskim
  version: "1.0"
  origin: Concept from Anthropic webapp-testing, adapted for Clawdbot + MiniPC environment
---

# Playwright Testing (MiniPC)

MiniPC에 설치된 Playwright를 활용한 웹앱/게임 테스트.

## 환경

- **실행 위치:** MiniPC (nodes.run 또는 browser.proxy)
- **브라우저:** Chromium headless
- **용도:** 게임 QA, 웹앱 기능 테스트, 스크린샷, 콘솔 로그 캡처

## 판단 트리

```
테스트 대상 → 정적 HTML인가?
├─ Yes → 파일 내용 직접 읽어 셀렉터 파악
│        → Playwright 스크립트로 자동화
└─ No (동적 웹앱) → 서버 실행 중인가?
    ├─ No → 서버 먼저 실행 (MiniPC에서)
    └─ Yes → 정찰-행동 패턴:
        1. 페이지 이동 + networkidle 대기
        2. 스크린샷 또는 DOM 검사
        3. 셀렉터 파악
        4. 동작 실행
```

## 핵심 패턴

### 정찰-행동 (Reconnaissance-Then-Action)

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('http://localhost:PORT')
    page.wait_for_load_state('networkidle')  # 필수!

    # 1. 정찰: DOM 상태 파악
    page.screenshot(path='/tmp/inspect.png', full_page=True)

    # 2. 셀렉터 탐색
    buttons = page.locator('button').all()

    # 3. 행동: 파악된 셀렉터로 조작
    page.click('text=Start Game')

    browser.close()
```

### 게임 QA 테스트

```python
# 게임 로드 확인
page.goto('http://localhost:9877/game.html')
page.wait_for_load_state('networkidle')

# 캔버스 렌더링 확인
canvas = page.locator('canvas')
assert canvas.is_visible()

# 게임 상호작용 테스트
page.click('canvas', position={'x': 400, 'y': 300})
page.wait_for_timeout(1000)

# 스코어/상태 변화 확인
score = page.locator('#score').inner_text()
page.screenshot(path='/tmp/game-test.png')

# 콘솔 에러 캡처
errors = []
page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
```

## ⚠️ 핵심 주의사항

- **networkidle 먼저!** 동적 앱은 반드시 JS 실행 완료 후 DOM 검사
- **headless=True 필수** (MiniPC에 모니터 없음)
- **MiniPC에서 실행** — 맥 스튜디오에서 직접 브라우저 금지
- **코드 리뷰만으로 QA 불충분** — 실제 플레이 테스트 필수
- **browser.proxy 또는 nodes.run 활용**

## Clawdbot에서 실행 방법

```
# 방법 1: browser tool (proxy)
browser action=navigate target=node node=MiniPC targetUrl="http://localhost:9877/game.html"
browser action=screenshot target=node node=MiniPC

# 방법 2: nodes.run으로 Python 스크립트 실행
nodes.run node=MiniPC command=["python3", "test_script.py"]
```
