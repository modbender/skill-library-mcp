# 🦞 OpenClaw Unreal Skill

Unreal Engine 통합을 위한 OpenClaw 스킬. [OpenClaw Unreal Plugin](https://github.com/openclaw/openclaw-unreal-plugin)과 함께 작동합니다.

## 설치

```bash
# OpenClaw workspace에 복제 또는 복사
cp -r openclaw-unreal-skill ~/.openclaw/workspace/skills/unreal-plugin
```

## 구조

```
openclaw-unreal-skill/
├── extension/
│   ├── index.ts       # 도구 정의 및 핸들러
│   └── package.json   # Extension 메타데이터
├── scripts/           # 헬퍼 스크립트
├── SKILL.md           # 스킬 문서 (영문)
├── SKILL_KO.md        # 스킬 문서 (한국어)
├── README.md          # 영문 README
├── README_KO.md       # 한국어 README (이 파일)
└── LICENSE            # MIT 라이선스
```

## 사용법

설치 후 스킬은 OpenClaw에 의해 자동으로 로드됩니다. 자연어로 Unreal Editor와 상호작용:

- "레벨 계층 구조를 보여줘"
- "위치 100, 200, 50에 큐브 만들어"
- "플레이 모드 시작해"
- "스크린샷 찍어"
- "플레이어 스타트를 원점으로 옮겨"

## 요구 사항

1. OpenClaw Gateway 실행 중
2. OpenClaw Plugin이 설치된 Unreal Engine 프로젝트
3. Gateway에 연결된 플러그인

## 도구

전체 도구 문서는 [SKILL_KO.md](SKILL_KO.md) 참조.

## 라이선스

MIT 라이선스
