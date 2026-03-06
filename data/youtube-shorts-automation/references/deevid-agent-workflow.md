# Deevid Agent 영상 생성 워크플로

## 개요
Deevid AI Agent (https://deevid.ai/ko/agent)를 사용하여 이미지 → 영상 변환.
**⚠️ "이미지를 동영상으로" 도구 절대 사용 금지** → 무음 영상만 생성됨.
Agent는 Start Image Master V2.0 모델 사용 → BGM + 대사 포함 영상 생성.

## 비용
- Agent 영상: 8초 = 20 크레딧 (오디오 포함)
- 이미지 생성: 1장 = 6 크레딧

## 이미지 생성 단계
1. https://deevid.ai/ko/ 접속 (로그인 필요)
2. "이미지 만들기" 선택
3. 프롬프트 입력 (9:16 세로 비율 지정)
4. 생성 후 이미지 URL 확보 (CDN: `sp.deevid.ai/storage/...`)
5. 이미지 다운로드: `curl -o image.jpg <URL>`

## Agent 영상 생성 단계
1. https://deevid.ai/ko/agent 접속
2. 파일 첨부 input (`input[type=file]`)으로 이미지 업로드
3. contenteditable div에 영상 프롬프트 입력
   - 예: "이 이미지를 기반으로 계단을 오르는 여성의 짧은 영상을 만들어줘. 경쾌한 배경음악과 함께."
4. "만들기" 버튼 클릭
5. 생성 완료까지 대기 (보통 2-5분)
6. 결과 영상 URL 추출: `<video>` 태그의 `src` 속성
   - CDN 패턴: `https://sp.deevid.ai/storage/v1/object/public/user-video/{uuid}.mp4`
7. 영상 다운로드: `curl -o video.mp4 <URL>`

## 브라우저 조작 주의사항
- Deevid는 SPA → 페이지 로딩 후 요소 렌더링 대기 필요
- Agent 채팅은 contenteditable div 사용 (일반 textarea 아님)
- 영상 생성 중 페이지 이탈 금지
- 영상 완료 시 카드 형태로 결과 표시 → video 태그에서 src 추출
