# git-auto - Git 워크스페이스 자동화 🐧

워크스페이스의 git 작업을 자동화하는 스킬.

## 기능

### 1. status - 상태 확인
```bash
git status --short
```
- 변경된 파일 수와 종류 요약
- Modified, Added, Deleted 파일 분류
- 간결한 한글 요약 제공

### 2. commit - 자동 커밋
변경사항을 분석하여 의미있는 커밋 메시지를 자동 생성 후 커밋:
```bash
git add -A
git commit -m "자동생성된 메시지"
```

**커밋 메시지 생성 규칙:**
- 변경된 파일들을 분석하여 주요 변경사항 파악
- 파일 종류별 이모지 prefix 자동 선택:
  - `✨` feat: 새 기능, 스킬 추가 (skills/)
  - `🐛` fix: 버그 수정
  - `📝` docs: 문서 변경 (README, *.md)
  - `🔧` chore: 설정, 도구 변경
  - `🗃️` memory: 메모리 파일 업데이트 (memory/)
- 제목: 50자 이내, 한국어 OK
- 필요시 body에 상세 내역 추가

### 3. push - 푸시
현재 브랜치를 origin으로 푸시:
```bash
git push origin $(git branch --show-current)
```
- 기본적으로 `main` 브랜치 가정
- 실제 브랜치명 자동 감지

### 4. log - 커밋 로그
최근 N개 커밋 요약:
```bash
git log -n N --oneline --decorate
```
- 기본값: 최근 10개
- 커밋 해시, 메시지, 브랜치 정보 표시

### 5. diff - 변경사항 요약
마지막 커밋 이후 변경사항 요약:
```bash
git diff --stat
git diff --shortstat
```
- 파일별 변경 라인 수
- 전체 통계 (파일 수, 추가/삭제 라인)

## 안전 규칙

### 🚫 금지 사항
1. **Force push 절대 금지**
   - `git push --force` 또는 `-f` 옵션 사용 불가
   
2. **민감한 파일 커밋 방지**
   - `.secrets/` 디렉토리
   - `.env` 파일
   - 커밋 전 `.gitignore` 확인

3. **대규모 변경 시 확인**
   - 100개 이상 파일 변경 시 형님에게 확인 요청
   - `git diff --stat | wc -l` 로 체크

### ✅ 안전 가이드
- 커밋 전 항상 `git status` 먼저 확인
- 민감한 정보가 포함된 파일이 staged 되었는지 체크
- push 전 로컬 변경사항과 리모트 동기화 확인

## 사용 예시

**상태 확인:**
- "git 상태 보여줘"
- "변경사항 있어?"
- "git status"

**자동 커밋:**
- "커밋해줘"
- "변경사항 커밋"
- "자동 커밋"

**푸시:**
- "푸시해줘"
- "git push"
- "리모트에 올려줘"

**로그 확인:**
- "최근 커밋 보여줘"
- "git log"
- "커밋 히스토리"

**변경 요약:**
- "뭐 바뀌었어?"
- "diff 보여줘"
- "변경사항 요약"

---
> 🐧 Built by **무펭이** — [무펭이즘(Mupengism)](https://github.com/mupeng) 생태계 스킬
