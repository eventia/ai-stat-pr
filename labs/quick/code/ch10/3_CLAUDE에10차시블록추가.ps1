# CLAUDE.md Ch10 블록 추가 (이미 있으면 건너뜀)
$block = @'

<!-- quick-practice:ch10:start -->
## 10차시 규칙 — 전체 파이프라인
- 순서: 입력 → 정제 → 보안등급 확인 → 개인정보 마스킹 → NLP → 계산 → 그래프 → AI 작성 → 문체 통일 → 3단계 검수 → 저장.
- 보안등급이 "공개"가 아니면 외부 AI API를 부르기 전에 PermissionError로 중단한다.
- 자동 검증(수치 교차 검증·표기 검사)을 통과하면 문서상태 "승인대기", 아니면 "검토필요"로 저장한다. 어느 쪽이든 사람의 최종 승인이 필요하다.
- 로그는 `logs/pipeline.log`에 `encoding="utf-8"`로 남긴다. 실행은 프로젝트 폴더에서 `python -m mywork.main`.
- `mywork/export.py`는 제공 파일이므로 수정하지 않는다. 형식(hwpx·pdf)마다 따로 try로 감싸 한쪽 실패가 다른 쪽을 막지 않게 한다.
<!-- quick-practice:ch10:end -->
'@
if (Select-String -Path CLAUDE.md -Pattern "quick-practice:ch10:start" -Quiet) { "이미 있음 — 건너뜀" }
else { [IO.File]::AppendAllText("$PWD\CLAUDE.md", $block, [Text.UTF8Encoding]::new($false)); "ch10 블록 추가 완료" }
