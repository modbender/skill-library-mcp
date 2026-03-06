# OpenClaw Unreal Skill

OpenClaw AI 어시스턴트를 통해 Unreal Editor를 제어합니다.

## 개요

이 스킬은 OpenClaw Unreal Plugin을 통해 AI 지원 Unreal Engine 개발을 가능하게 합니다. 플러그인은 HTTP 폴링 (`/unreal/*` 엔드포인트)을 통해 OpenClaw Gateway와 통신합니다.

## 아키텍처

```
┌──────────────────┐     HTTP      ┌─────────────────────┐
│  OpenClaw        │ ←──────────→  │  Unreal Editor      │
│  Gateway:18789   │  /unreal/*    │  (C++ Plugin)       │
└──────────────────┘               └─────────────────────┘
         ↑
         │ Extension
┌──────────────────┐
│  extension/      │
│  index.ts        │
└──────────────────┘
```

## 사전 요구 사항

1. Unreal Engine 5.x 프로젝트
2. 프로젝트에 OpenClaw Unreal Plugin 설치
3. OpenClaw Gateway 실행 중 (기본 포트: 18789)

## 설치

### 플러그인 설치

1. `openclaw-unreal-plugin` 폴더를 프로젝트의 `Plugins` 디렉토리에 복사
2. Unreal Editor 재시작
3. Edit → Plugins → OpenClaw에서 플러그인 활성화
4. Window → OpenClaw에서 연결 상태 확인

### 스킬 설치

```bash
# 스킬을 OpenClaw workspace에 복사
cp -r openclaw-unreal-skill ~/.openclaw/workspace/skills/unreal-plugin
```

## 사용 가능한 도구

### Level 관리
- `level.getCurrent` - 현재 레벨 정보 가져오기
- `level.list` - 모든 레벨 나열
- `level.open` - 경로로 레벨 열기
- `level.save` - 현재 레벨 저장

### Actor 조작
- `actor.find` - 이름으로 Actor 찾기
- `actor.getAll` - 모든 Actor 가져오기
- `actor.create` - 새 Actor 스폰 (Cube, PointLight, Camera 등)
- `actor.delete` / `actor.destroy` - Actor 제거
- `actor.getData` - Actor 상세 정보 가져오기
- `actor.setProperty` - Actor 속성 수정

### Transform
- `transform.getPosition` / `setPosition`
- `transform.getRotation` / `setRotation`
- `transform.getScale` / `setScale`

### Component
- `component.get` - Actor 컴포넌트 가져오기
- `component.add` - 컴포넌트 추가
- `component.remove` - 컴포넌트 제거

### Editor 제어
- `editor.play` - PIE (Play In Editor) 시작
- `editor.stop` - PIE 중지
- `editor.pause` / `resume` - 게임플레이 일시정지/재개
- `editor.getState` - 플레이 중인지 에디팅 중인지 확인

### Debug
- `debug.hierarchy` - World Outliner 트리
- `debug.screenshot` - 뷰포트 캡처
- `debug.log` - Output에 메시지 로그

### Input 시뮬레이션
- `input.simulateKey` - 키보드 입력 (W, A, S, D, Space 등)
- `input.simulateMouse` - 마우스 클릭/이동/스크롤
- `input.simulateAxis` - 게임패드/축 입력

### 에셋
- `asset.list` - 콘텐츠 브라우저 탐색
- `asset.import` - 외부 에셋 임포트

### 콘솔
- `console.execute` - 콘솔 명령 실행
- `console.getLogs` - Output 로그 메시지 가져오기

### Blueprint
- `blueprint.list` - 프로젝트의 블루프린트 나열
- `blueprint.open` - 에디터에서 블루프린트 열기

## 사용 예제

```
사용자: 위치 (100, 200, 50)에 큐브 만들어
AI: [unreal_execute tool="actor.create" parameters={type:"Cube", x:100, y:200, z:50} 사용]

사용자: 플레이어 스타트를 센터로 옮겨
AI: [unreal_execute tool="actor.find" parameters={name:"PlayerStart"} 사용]
    [unreal_execute tool="transform.setPosition" parameters={name:"PlayerStart", x:0, y:0, z:0} 사용]

사용자: 스크린샷 찍어
AI: [unreal_execute tool="debug.screenshot" 사용]

사용자: 게임 시작해
AI: [unreal_execute tool="editor.play" 사용]
```

## 설정

프로젝트 루트에 `openclaw.json` 생성 (선택사항):

```json
{
  "host": "127.0.0.1",
  "port": 18789,
  "autoConnect": true
}
```

또는 `~/.openclaw/unreal-plugin.json`에 전역 설정.

## HTTP 엔드포인트

Extension이 OpenClaw Gateway에 등록하는 엔드포인트:

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/unreal/register` | POST | 새 세션 등록 |
| `/unreal/poll` | GET | 대기 중인 명령 폴링 |
| `/unreal/heartbeat` | POST | 세션 유지 |
| `/unreal/result` | POST | 도구 실행 결과 전송 |
| `/unreal/status` | GET | 모든 세션 상태 조회 |

## 문제 해결

### 플러그인 연결 안됨
- `[OpenClaw]` 메시지에 대해 Output Log 확인
- Gateway 실행 확인: `openclaw gateway status`
- 포트 18789 접근 가능 확인
- Window → OpenClaw에서 연결 상태 확인 시도

### 세션 만료
- 플러그인이 세션 만료 시 자동 재연결
- Gateway 재시작 여부 확인

### 도구 작동 안함
- 플러그인 활성화 확인 (Edit → Plugins)
- 레벨 Actor 수정 시 PIE 상태가 아닌지 확인
- Actor 이름이 정확히 일치하는지 확인 (대소문자 구분)

## 🔐 보안: 모델 호출 설정

ClawHub에 퍼블리시할 때 `disableModelInvocation`을 설정할 수 있습니다:

| 설정 | AI 자동 호출 | 사용자 명시적 요청 |
|------|-------------|------------------|
| `false` (기본값) | ✅ 허용 | ✅ 허용 |
| `true` | ❌ 차단 | ✅ 허용 |

### 권장: **`false`** (기본값)

**이유:** Unreal 작업 중 AI가 자율적으로 Actor 계층 확인, 스크린샷, 컴포넌트 검사 등 보조 작업을 수행하는 것이 유용함.

**`true` 사용 시기:** 민감한 도구 (결제, 삭제, 메시지 전송 등)에 적합

## CLI 명령

```bash
# Unreal 연결 상태 확인
openclaw unreal status
```

## 라이선스

MIT 라이선스 - LICENSE 파일 참조
