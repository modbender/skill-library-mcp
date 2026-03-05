# Multi-Root Quickstart

Osori의 multi-root 기능으로 프로젝트를 **업무/개인/실험** 등으로 분류할 수 있습니다.

## 1. Root 추가

```bash
/root-add work 업무
/root-add personal 개인
```

## 2. Discovery Path 설정

각 root에 프로젝트를 자동 탐색할 디렉토리를 등록합니다:

```bash
/root-path-add work ~/Developer/work
/root-path-add personal ~/Developer/personal
```

## 3. 일괄 스캔

```bash
/scan ~/Developer/work work
/scan ~/Developer/personal personal
```

한 번의 scan으로 해당 경로의 모든 git 프로젝트가 지정된 root에 등록됩니다.

## 4. Root별 조회

```bash
/list work          # 업무 프로젝트만
/list personal      # 개인 프로젝트만
/list               # 전체
```

```bash
/status work        # 업무 프로젝트 git status만
```

## 5. Root 범위로 Switch

```bash
/switch my-app --root work
```

같은 이름의 프로젝트가 여러 root에 있어도 scope를 지정하면 정확히 찾습니다.

## 6. Fingerprints도 Root 필터 지원

```bash
/fingerprints --root work    # 업무 프로젝트 핑거프린트만
```

## 7. Root 정리

더 이상 필요 없는 root는 안전하게 삭제:

```bash
# 프로젝트를 다른 root로 옮긴 후 삭제
/root-remove old-root --reassign work

# 또는 강제로 default에 옮기고 삭제
/root-remove old-root --force
```

`default` root는 삭제할 수 없습니다 (안전장치).

## Tips

- **Root는 논리적 분류**입니다 — 실제 파일 시스템 구조와 무관합니다
- Discovery path는 `/scan` 시 탐색 범위를 지정하는 용도입니다
- `/find`, `/switch`, `/fingerprints` 모두 `--root` 옵션을 지원합니다
