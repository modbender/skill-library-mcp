---
name: hwpx_my
description: "HWPX 문서(.hwpx 파일)를 생성, 읽기, 편집, 템플릿 치환하는 스킬. 한글 HWPX 포맷을 다루며 양식 기반 템플릿 치환 워크플로우를 제공합니다."
---

# hwpx_my

HWPX 문서 생성·편집 스킬 (hwpx_my)

이 스킬은 ZIP-level 치환을 통한 템플릿 기반 문서 생성을 지원합니다. 기본 제공 템플릿은 `assets/report-template.hwpx` 입니다. 사용자가 업로드한 템플릿은 `uploads/` 폴더에 놓아 사용합니다. 결과는 `outputs/`에 생성됩니다.

Commands:
- analyze-template <path> : 템플릿 내 텍스트 플레이스홀더를 추출
- apply-template <template> <mapping.json> <out.hwpx> : mapping에 따라 치환하고 outputs에 저장

Notes:
- For full ObjectFinder features install python-hwpx; a lightweight shim is provided under lib/hwpx_shim.py if python-hwpx is unavailable.

License: MIT
