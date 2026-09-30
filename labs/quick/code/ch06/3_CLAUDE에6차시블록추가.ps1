# CLAUDE.md Ch06 블록 추가 (이미 있으면 건너뜀)
$block = @'

<!-- quick-practice:ch06:start -->
## 6차시 규칙 — 그래프와 설명문
- matplotlib은 `matplotlib.use("Agg")`로 파일 저장만 하고, 한글 폰트는 "Malgun Gothic", 그림은 `images/`에 PNG로 저장한다.
- 그래프에는 제목(기준 시점 포함)·단위·출처를 넣는다.
- 설명문에는 항상 주어(무엇에 대한 설명인지)를 넣는다. 꺾은선 설명문의 주어는 `label`(지표명)로 받는다.
- 시각자료설명 항목은 `소주제`·`그래프유형`·`이미지경로`·`설명문` 4개 키를 가진다. 설명문의 숫자는 계산된 값을 그대로 쓴다.
<!-- quick-practice:ch06:end -->
'@
if (Select-String -Path CLAUDE.md -Pattern "quick-practice:ch06:start" -Quiet) { "이미 있음 — 건너뜀" }
else { [IO.File]::AppendAllText("$PWD\CLAUDE.md", $block, [Text.UTF8Encoding]::new($false)); "ch06 블록 추가 완료" }
