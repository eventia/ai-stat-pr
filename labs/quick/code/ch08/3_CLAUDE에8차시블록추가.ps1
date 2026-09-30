# CLAUDE.md Ch08 블록 추가 (이미 있으면 건너뜀)
$block = @'

<!-- quick-practice:ch08:start -->
## 8차시 규칙 — 본문 단락
- 본문 단락 프롬프트에는 두괄식, 제공된 사실 외 추가 금지, "소재에 없는 합계·차이·비율을 새로 계산하지 말 것"을 넣는다.
- 연결어("", "한편, ", "아울러, ")는 코드가 붙이고, 빈 응답은 건너뛴다. `lower()` 같은 영문 대소문자 처리는 하지 않는다.
- 본문은 [{"소주제", "내용"}] 목록으로 저장하고, 모든 단락을 `verify_numbers`로 검증한다.
<!-- quick-practice:ch08:end -->
'@
if (Select-String -Path CLAUDE.md -Pattern "quick-practice:ch08:start" -Quiet) { "이미 있음 — 건너뜀" }
else { [IO.File]::AppendAllText("$PWD\CLAUDE.md", $block, [Text.UTF8Encoding]::new($false)); "ch08 블록 추가 완료" }
