# CLAUDE.md Ch03 블록 추가 (이미 있으면 건너뜀)
$block = @'

<!-- quick-practice:ch03:start -->
## 3차시 규칙 — NLP 분석
- 키워드·주요 문장 추출은 생성형 AI 없이 형태소 분석·TF-IDF·TextRank로 한다.
- 주요 문장은 원문 문장을 그대로 골라 원문 순서로 반환한다(새 문장 생성·수정 금지).
- 도메인 복합명사(온라인쇼핑, 모바일쇼핑, 거래액, 역대급)는 Kiwi 사용자 사전에 등록한다.
- 문서가 1건이면 문장 하나하나를 문서로 취급해 TF-IDF를 계산한다.
- NLP 결과는 참고용이며 보도자료의 숫자·사실을 확정하는 데 쓰지 않는다.
<!-- quick-practice:ch03:end -->
'@
if (Select-String -Path CLAUDE.md -Pattern "quick-practice:ch03:start" -Quiet) { "이미 있음 — 건너뜀" }
else { [IO.File]::AppendAllText("$PWD\CLAUDE.md", $block, [Text.UTF8Encoding]::new($false)); "ch03 블록 추가 완료" }
