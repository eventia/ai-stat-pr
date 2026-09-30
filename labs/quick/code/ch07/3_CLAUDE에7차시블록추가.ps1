# CLAUDE.md Ch07 블록 추가 (이미 있으면 건너뜀)
$block = @'

<!-- quick-practice:ch07:start -->
## 7차시 규칙 — 원자료 입력과 헤드라인
- 입력 모듈 이름은 `data_io.py`로 한다(표준 라이브러리 `io`와 이름 충돌 방지).
- xlsx에서 읽은 숫자는 numpy 타입이므로 파이썬 기본 타입(int·float·str)으로 바꿔 담는다.
- PDF는 원문만 채운다. 제목·리드문의 수치는 xlsx의 계산지표에서 가져온다.
- 헤드라인 프롬프트는 6하원칙 요소 중 주어진 것만 쓰고, 없는 요소(어디서·왜)는 지어내지 않는다. 발표 주체는 `config.ISSUER`.
- 제목·부제·리드문 모두 `verify_numbers`로 검증한다.
<!-- quick-practice:ch07:end -->
'@
if (Select-String -Path CLAUDE.md -Pattern "quick-practice:ch07:start" -Quiet) { "이미 있음 — 건너뜀" }
else { [IO.File]::AppendAllText("$PWD\CLAUDE.md", $block, [Text.UTF8Encoding]::new($false)); "ch07 블록 추가 완료" }
