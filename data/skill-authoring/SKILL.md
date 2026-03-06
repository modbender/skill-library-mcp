---
name: skill-authoring
description: Guide for creating effective SKILL.md files that extend agent capabilities. Use when creating new skills, updating existing ones, or teaching the agent specialized workflows.
metadata:
  author: misskim
  version: "1.0"
  origin: Concept from Anthropic skill-creator, adapted for Clawdbot agentskills.io standard
---

# Skill Authoring Guide

agentskills.io 표준에 맞는 효과적인 스킬 작성법.

## 핵심 원칙

### 1. 간결함이 왕
컨텍스트 윈도우는 공공재다. 모든 스킬이 이 공간을 공유한다.

**기본 가정: 에이전트는 이미 매우 똑똑하다.**
에이전트가 모르는 것만 추가할 것. 모든 문장마다 자문:
- "이 설명이 정말 필요한가?"
- "이 단락이 토큰 비용을 정당화하는가?"

장황한 설명보다 간결한 예제를 선호.

### 2. 자유도 매칭

| 자유도 | 언제 | 형태 |
|--------|------|------|
| **높음** | 여러 접근법이 유효, 맥락에 따라 판단 | 텍스트 지침 |
| **중간** | 선호 패턴 존재, 일부 변형 허용 | 의사코드/파라미터 있는 스크립트 |
| **낮음** | 취약한 작업, 일관성 필수 | 구체적 스크립트, 최소 파라미터 |

좁은 다리(절벽 옆) = 구체적 가드레일 (낮은 자유도)
넓은 평원 = 다양한 경로 허용 (높은 자유도)

## SKILL.md 구조

```yaml
---
name: my-skill-name        # 필수, 소문자+하이픈, 1-64자
description: >             # 필수, 1-1024자
  무엇을 하는지 + 언제 사용하는지 + 관련 키워드
license: Apache-2.0        # 선택
metadata:                  # 선택
  author: misskim
  version: "1.0"
---

# 스킬 제목

[에이전트가 따를 지침 - 마크다운 자유형식]
```

### 필수 필드
- **name:** 디렉토리명과 일치, 소문자+하이픈만
- **description:** 스킬 활성화 트리거 역할 → 키워드 풍부하게

### 디렉토리 구조
```
skill-name/
├── SKILL.md          # 필수
├── scripts/          # 실행 코드 (Python/Bash/JS)
├── references/       # 상세 문서 (필요 시 로드)
└── assets/           # 정적 리소스 (템플릿, 이미지, 데이터)
```

## 우리 환경 특화 고려사항

1. **Clawdbot 에이전트:** skills/ 또는 ~/.clawdbot/skills/에 배치
2. **MiniPC 연동:** nodes.run 명령으로 외부 작업 위임 가능
3. **서브에이전트:** 스킬이 서브에이전트를 스폰하도록 설계 가능
4. **보안:** scripts/ 코드는 신뢰할 수 있는 것만 포함
5. **SKILL.md 500줄 이하 유지** — 상세 내용은 references/로 분리

## 나쁜 스킬 vs 좋은 스킬

**나쁜:** "PDF를 처리합니다" (description이 너무 짧음)
**좋은:** "PDF 파일에서 텍스트/표를 추출하고, 폼을 채우고, 여러 PDF를 병합합니다. PDF 문서 작업이나 문서 추출을 언급할 때 사용."

**나쁜:** 에이전트가 이미 아는 Python 문법 설명
**좋은:** 에이전트가 모르는 도메인 특화 지식/워크플로우 제공
