# hwpx_my
<<<<<<< HEAD
hwpx 템플릿을 활용한 생성형 AI 문서 작성
=======

HWPX 문서(.hwpx) 생성·편집·템플릿 치환 스킬 (hwpx_my)

이 스킬은 python-hwpx를 사용해 HWPX 양식을 기반으로 문서를 생성하거나 플레이스홀더를 치환합니다.

사용법 (로컬):

1. 필수: 의존성 설치
   ```bash
   python3 -m pip install --user -r requirements.txt
   ```

2. 사용자 업로드는 `uploads/`에 넣고, 결과는 `outputs/`에 생성됩니다.

3. 템플릿 분석
   ```bash
   ./run.py analyze-template assets/report-template.hwpx
   ```

4. 템플릿 적용
   ```bash
   ./run.py apply-template assets/report-template.hwpx mapping.json outputs/out.hwpx
   ```

참고: `scripts/fix_namespaces.py`가 후처리용으로 포함되어 있습니다. 모든 치환 후 이 스크립트를 실행해 네임스페이스를 정리합니다.
>>>>>>> 8164f45 (Finalize hwpx_my package and README/LICENSE/install script)
