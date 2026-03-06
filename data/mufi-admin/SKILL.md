---
name: MUFI Admin 이벤트 등록 스킬
description: https://admin.muinfilm.com
---

# MUFI Admin 이벤트 등록 스킬

## URL
https://admin.muinfilm.com

## 구조
```
축제(이벤트) → 캠페인 → 프레임 템플릿(상품) → 프레임(디자인)
```

## 1. 축제 생성
- 경로: /events → "축제 추가"
- 필드: 이름*, 설명, 시작일*, 종료일*, 활성화
- 이름 패턴: `[날짜]학교명 행사명` (예: `[2월 19일]한예종 졸업영화제`)
- 날짜 선택: Ant Design DatePicker → 날짜 셀 클릭 → OK
- 종료일 evaluate 팁: `document.querySelectorAll('.ant-picker-dropdown:not(.ant-picker-dropdown-hidden) td[title="YYYY-MM-DD"]')[0].click()` → `.ant-picker-ok button` 클릭

## 2. 캠페인 생성
- 경로: /campaigns → "캠페인 추가"
- 필드: 이름*, 활성화, 썸네일(920×960)
- 이름은 축제와 동일하게

## 3. 축제↔캠페인 연결
- 경로: /events/{id} → Campaigns 행 "수정" 클릭
- combobox에서 캠페인 이름 검색 → 선택 → "저장"

## 4. 프레임 템플릿 생성
- 경로: /frame-templates → "프레임 템플릿 추가"
- 필드:
  - 프레임 종류* (세로형 등)
  - 이름*, 설명*
  - 가격* (기본 5000)
  - 촬영 횟수* (기본 8장)
  - 촬영 시간* (기본 8초)
  - 좌우반전, 활성화
  - 화질 0.5배 (테스트용)
- 이미지:
  - 썸네일: 200~400px × 590px
  - 카메라 오버레이: 2064 × 1376px
  - 오버레이 이미지 출력 여부
- 생성 후: /frame-templates/{id} → Campaigns 수정으로 캠페인 연결

## 5. 프레임(디자인) 생성
- 경로: /frames → "프레임 추가"
- 필드:
  - 프레임 템플릿* (combobox 선택)
  - 이름* (예: "호관대", "BLACK", "GREEN")
  - 활성화
  - 화질 0.5배 (테스트용)
- 이미지:
  - 썸네일: 256 × 256px
  - 배경: 4960 × 7376px
  - 전경: 4960 × 7376px

## 등록 순서 (전체 플로우)
1. 축제 생성 (/events)
2. 캠페인 생성 (/campaigns)
3. 축제↔캠페인 연결 (/events/{id})
4. 프레임 템플릿 생성 (/frame-templates)
5. 프레임 템플릿↔캠페인 연결 (/frame-templates/{id})
6. 프레임(디자인) 생성 + 이미지 업로드 (/frames)

## 브라우저 자동화 팁
- 프로필: openclaw
- 날짜 선택은 evaluate로 직접 DOM 조작이 안정적
- combobox 검색: type으로 검색어 입력 → listbox에서 Enter
- 저장 버튼: `document.querySelector('button.ant-btn-primary').click()`
