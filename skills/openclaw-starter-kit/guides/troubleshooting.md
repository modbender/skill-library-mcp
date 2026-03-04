# 트러블슈팅 FAQ

## 🔴 Gateway가 안 켜져요
```bash
openclaw doctor        # 문제 진단
openclaw gateway start # 수동 시작
```
- Node.js 버전 확인: `node -v` (v18 이상 필요)
- 포트 충돌: `lsof -i :18789` 로 확인

## 🔴 봇이 응답 안 해요
1. gateway 실행 중인지 확인: `openclaw status`
2. API 키 유효한지 확인: `openclaw configure --section models`
3. 텔레그램 allowlist에 내 번호 있는지 확인
4. 봇 토큰이 맞는지 확인

## 🔴 "Command not found: openclaw"
```bash
# npm 글로벌 경로 확인
npm list -g openclaw

# 경로가 안 잡히면
export PATH="$PATH:$(npm config get prefix)/bin"
```

## 🔴 스킬 설치가 안 돼요
```bash
# 권한 문제
sudo npm install -g openclaw

# 스킬 재설치
openclaw skills install [스킬명] --force
```

## 🔴 API 키 오류 (401/403)
- 키가 만료되었을 수 있음 → 새로 발급
- 복사할 때 앞뒤 공백이 들어갔을 수 있음
- `openclaw configure`로 다시 입력

## 🔴 메모리가 안 쌓여요
- MEMORY.md 파일이 존재하는지 확인
- `memory/` 폴더가 있는지 확인
- 에이전트에게 "기억해" 라고 명시적으로 말하기

## 🔴 하트비트가 안 돌아요
- HEARTBEAT.md 파일이 워크스페이스 루트에 있는지 확인
- gateway가 실행 중인지 확인
- heartbeat 간격 설정 확인: `openclaw configure`

## 💡 만능 해결법
```bash
openclaw doctor     # 1. 진단
openclaw health     # 2. 상태 확인
openclaw gateway restart  # 3. 재시작
```
그래도 안 되면 → OpenClaw Discord 커뮤니티에 질문!
https://discord.com/invite/clawd
