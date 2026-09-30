# CLAUDE.md Ch05 블록 추가 (이미 있으면 건너뜀)
$block = @'

<!-- quick-practice:ch05:start -->
## 5차시 규칙 — 통계 계산과 해석
- 증감률·비중·순위·역대 최대 판단은 모두 `mywork/stats.py`의 파이썬 함수가 계산한다. `계산지표`는 바꾸지 않는다.
- 역대 최대는 같은 달(동월)끼리만 비교한다. 비교 대상이 없으면 None(판단 불가)으로 두고 0이나 True로 채우지 않는다.
- 감소 문장은 abs()로 부호를 뗀 값을 "감소" 템플릿에 넣는다(이중 부정 금지).
- 해석문의 주어는 `문서정보["지표명"]`을 쓴다(제목에서 잘라 쓰지 않는다).
- 계산 결과를 JSON으로 저장할 수 있도록 numpy 숫자는 파이썬 int·float로 바꾼다.
<!-- quick-practice:ch05:end -->
'@
if (Select-String -Path CLAUDE.md -Pattern "quick-practice:ch05:start" -Quiet) { "이미 있음 — 건너뜀" }
else { [IO.File]::AppendAllText("$PWD\CLAUDE.md", $block, [Text.UTF8Encoding]::new($false)); "ch05 블록 추가 완료" }
