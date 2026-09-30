# CLAUDE.md Ch09 블록 추가 (이미 있으면 건너뜀)
$block = @'

<!-- quick-practice:ch09:start -->
## 9차시 규칙 — 문체 통일과 검수
- 문체 통일은 표현만 바꾸고 숫자·콤마·단위와 단락 구분(빈 줄)을 바꾸지 않는다. 설명·머리말 없이 본문만 출력하게 한다.
- 검수는 3단계: `check_formatting_errors`(표기) → `cross_check_all_numbers`(수치) → `review_press_release`(AI 감수).
- 수치 교차 검증은 4차시 `find_unverified_numbers`를 재사용한다(요약과 최종본에 같은 기준 적용).
- AI 감수 응답의 파싱 실패는 예외 대신 안내 항목 1개로 돌려준다. 감수 결과는 참고이며 반영 여부는 사람이 판단한다.
<!-- quick-practice:ch09:end -->
'@
if (Select-String -Path CLAUDE.md -Pattern "quick-practice:ch09:start" -Quiet) { "이미 있음 — 건너뜀" }
else { [IO.File]::AppendAllText("$PWD\CLAUDE.md", $block, [Text.UTF8Encoding]::new($false)); "ch09 블록 추가 완료" }
