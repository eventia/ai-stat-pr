# Task 문서 (진행 상황 및 재개 가이드)

이 문서는 **다음에 이어서 작업할 때 가장 먼저 읽어야 할 문서**입니다. 지금까지 무엇을 했는지, 무엇이 검증되었는지, 다음에 무엇부터 해야 하는지를 정리했습니다. 세부 경위(왜 그렇게 고쳤는지)는 [IMPLEMENTATION_LOG.md](IMPLEMENTATION_LOG.md)를 참고하세요.

---

## 0. 재개 시 가장 먼저 할 일 (5분 체크)

```bash
cd "보도자료작성-실습1"

# 1) 가상환경 활성화
myvenv\Scripts\activate.bat        # CMD
# 또는: myvenv\Scripts\Activate.ps1  # PowerShell

# 2) 아직도 테스트가 통과하는지 확인 (환경이 그대로인지 검증)
pytest tests/ -v
# 기대 결과: 75 passed

# 3) API 키가 준비됐다면 .env 확인 후 실제 파이프라인 실행
python main.py            # 온라인쇼핑 동향 예시 (이미 계산된 표 입력)
python main_price.py      # 가격정보 공공 API 기반 실제 통계 보도자료 (진짜 원자료)
python main_practice.py   # 반려동물용품 예시 (표본매출 원자료 → 코드가 직접 집계·계산)
```

`pytest`가 50개 모두 통과하지 않는다면, 그 사이 파이썬/패키지 버전이 바뀌었거나 파일이 수정된 것이므로 원인부터 파악하세요.

---

## 1. 지금까지 한 일 (완료됨)

### 1차: 문서 리뷰 (실행 전, 읽기만)
- Ch01~Ch10 PT내용/실습 문서 전체를 읽고, 코드로 그대로 옮겼을 때 작동하지 않을 부분을 찾음
- 발견한 문제(요약): 정의 없이 호출만 되는 함수 다수, `verify_numbers`의 콤마·날짜 숫자 처리 버그, `check_formatting_errors`의 죽은 코드/반대로 동작하는 정규식, 패키지명 오타(`kiwi-nlp`→`kiwipiepy`), 스키마 불일치(계산지표 vs 품목별지표), Ch10 캡스톤이 6·9차시 안전장치를 호출하지 않던 문제 등

### 2차: 웹 검색으로 이중 확인 후 문서 수정
- `kiwipiepy` 패키지명, summa 라이브러리의 한국어 미지원, Claude 모델 ID 현황을 웹 검색으로 확인
- Ch01~Ch10의 `-PT내용.md`/`-실습.md` 파일에 `> **[수정]**` 형태로 근거와 함께 수정 사항을 반영 (문서만 수정, 코드 실행은 아직 안 함)
- 주요 수정: `MODEL_NAME` 상수 도입, `parse_json_response`(방어적 JSON 파싱), `find_unverified_numbers`(수치 검증 통합), summa 제거 후 TF-IDF+networkx로 TextRank 직접 구현, 누락 함수(`build_headline_prompt`, `generate_body_paragraphs`, `add_calculated_indicators`, `load_input`, `assemble_full_text`, `build_visual_descriptions`, `clean_and_structure`) 신규 작성, 윈도우 venv 활성화 명령 오타 수정

### 3차: 실제 프로젝트 구축 + 실행 검증 (이번 세션)
- 가상환경(`myvenv`) 생성, `requirements.txt` 설치 완료 (Python 3.13.12, 11개 패키지 정상 설치)
- `modules/` 7개 파일(`io`, `clean`, `nlp`, `stats`, `charts`, `write`, `review`) + `main.py` 작성 — 문서에서 확정한 코드를 그대로 이식
- `tests/` 작성 및 실행: **30개 테스트 전부 통과**
  - test_ch02_clean, test_ch03_nlp, test_ch05_stats, test_ch06_charts, test_ch09_review, test_ch10_pipeline(LLM 목업)
- `main.py` 실제 실행 → 입력~계산 단계까지 정상 동작 확인, API 키 부재로 `generate_headline_set`에서 정확히 예상된 지점에 멈춤을 확인
- **실제 실행으로만 발견한 문제 3건**을 찾아 코드와 문서 양쪽에 반영
  1. kiwipiepy가 "온라인쇼핑"/"거래액"을 문맥에 따라 쪼개는 문제 → `kiwi.add_user_word()`로 사용자 사전 등록
  2. 단일 문서 TF-IDF/TextRank의 실제 결과가 문서의 예시와 다름 → 실측값으로 문서 교체, "사실 확정은 5차시 규칙 기반 계산이 담당"이라는 안전장치가 있음을 확인·명시
  3. 윈도우에서 `logging.basicConfig`가 로그 파일을 cp949로 열어 한글이 깨지는 문제 → `encoding="utf-8"` 추가
- `README.md`, `IMPLEMENTATION_LOG.md`, `CLAUDE.md`, `.env.example`, `.gitignore`, `scripts/make_sample_excel.py` 작성

### 4차: 실제 API 키로 품질 검증 (2026-09-06 01:52~02:10)
- 사용자가 `.env.example`을 삭제하고 `.env`를 직접 만들어 `ANTHROPIC_API_KEY`를 입력함
- 실제 키로 `python main.py`를 여러 차례 반복 실행하며 **LLM 호출 구간에서만 발현되는 버그 8건**을 연쇄적으로 발견·수정 (인증 클라이언트 생성 순서, 품목별지표 JSON 파싱 누락, 통계 해석 필드 표준화 단계 유실, 숫자 단위 표기 불일치 2건, AI 감수 근거자료 누락, 해석문장 전월/전년동월 혼동, JSON 파싱 정규식 결함)
- 품목별지표 포함 xlsx(`scripts/make_sample_excel_full.py`)와 PDF 입력(`scripts/make_sample_pdf.py`) 샘플을 새로 만들어 그동안 미실행이던 두 경로를 실제로 실행·검증
- `mask_sensitive_info`를 `clean_and_structure`에 연결
- `modules/io.py`, `modules/write.py` 단위 테스트를 새로 작성해 테스트를 30개 → 43개로 확대
- 상세 내용과 시각별 타임라인은 [IMPLEMENTATION_LOG.md "8. 4차 세션"](IMPLEMENTATION_LOG.md) 참고

### 5차: 공공데이터포털 API 실제 연동 (2026-09-07)
- 사용자가 실제로 활용신청·승인받은 API는 Ch02 예시(가상의 온라인쇼핑 동향 JSON API)와 달리 **"국가데이터처(구 통계청)_온라인 수집 가격 정보"**(품목 리스트 조회 + 가격정보 조회, XML 응답) API였음을 확인
- data.go.kr 공식 활용가이드 문서(v2.2.docx)를 다운로드해 정확한 요청변수(`itemCode`, `startDate`/`endDate` 등) 명세를 확보
- 실제 호출 중 **이중 URL 인코딩 문제**(발급받은 키가 이미 인코딩된 "Encoding" 키였음)를 재현하고, `urllib.parse.unquote()`로 방어하도록 수정
- 두 오퍼레이션(`getPriceItemList`, `getPriceInfo`) 모두 실제 서비스 키로 정상 호출·파싱됨을 확인 (`scripts/fetch_public_api_sample.py` 신규 작성)
- Ch02-PT내용.md에 실제와 다른 점(XML 응답, 이중 인코딩, 파라미터 형식) `[수정]` 노트로 반영
- `tests/test_ch02_public_api.py` 신규 작성(4건, 네트워크 목업)으로 테스트 43개 → 47개
- 상세 내용은 [IMPLEMENTATION_LOG.md "10. 5차 세션"](IMPLEMENTATION_LOG.md) 참고

### 6차: 가격정보 API로 실제 통계 보도자료 파이프라인 구축 (2026-09-07, 11:16~11:43)
- `main.py`(온라인쇼핑 동향, xlsx 기반)는 건드리지 않고 별도 진입점 `main_price.py`를 신규 작성
- `modules/public_api.py`(API 호출을 스크립트에서 모듈로 승격 + 평균가격 계산), `modules/price_stats.py`(집계·해석문), `modules/price_report.py`(가격 데이터 전용 헤드라인·그래프 설명) 3개 모듈 신규 작성
- `modules/review.py`(수치검증·문체통일·AI감수)와 `modules/write.py`의 본문 확장 함수는 지표명에 의존하지 않는 범용 코드임을 확인하고 그대로 재사용
- 실제 API + 실제 LLM으로 끝까지 실행해 **표기오류검사 0건, 수치교차검증 통과**하는 보도자료 완성 (`output/2026-08 생필품 가격 동향.txt`)
- 이 과정에서 진짜 버그 2건 발견·수정: 큰 숫자 콤마 누락, **음수 증감률(하락)을 검증 못 하던 `review.py`의 숨은 버그** — 기존 예시가 항상 양수만 다뤘던 탓에 지금까지 안 드러났던 버그
- 테스트 47개 → 50개로 확대
- 상세 내용은 [IMPLEMENTATION_LOG.md "11. 6차 세션"](IMPLEMENTATION_LOG.md) 참고

### 7차: 검토 보고서(REVIEW_Ch02-10.md) 개선 제안 실행 (2026-09-10)
- 사용자 요청으로 Ch02~Ch10 PT·실습 자료를 실제 코드와 대조 검토해 [REVIEW_Ch02-10.md](REVIEW_Ch02-10.md) 작성, 그 안의 개선 제안 6가지를 모두 실행함
- **(시급, A-2 수정)** `add_calculated_indicators`/`generate_interpretation`에 "큰 폭 감소", "연속 감소세" 템플릿 추가 — 하락하는 통계에서 특이점은 감지되는데 해석문장이 조용히 비던 결함 수정
- **(중요, A-1 수정)** `derive_history_indicators` 신규 작성 — xlsx의 "이력" 시트(연월, 총거래액)를 `load_input`이 읽어 `역대최대여부`/`최근3개월증감률`을 자동 계산. 이전에는 담당자가 과거 자료를 직접 조사해 수작업으로 입력해야 했음
- **(중요, A-3 수정)** `main.py`가 `generate_summary`(4차시)를 실제로 호출해 `요약결과`에 저장하고, 그 `제목후보`를 7차시 헤드라인 프롬프트에 참고용으로 전달 — 이전에는 어디서도 호출되지 않던 죽은 코드였음(사실 확정 근거는 여전히 5차시 계산 결과만 사용)
- **(개선, B-1 일부)** `modules/config.py` 신규 — `REQUIRED_FIELDS`/`INDICATOR_UNITS` 하드코딩을 한곳으로 모음 (완전한 재사용성 보장은 아니며, `modules/stats.py`/`modules/io.py`의 필드 구조 의존은 여전히 남아 있음)
- **(경미, 개선5 수정)** 꺾은선그래프(line)가 `build_visual_descriptions`에서 실제로는 도달 불가능한 "고아 기능"이었던 문제 수정 — `월별이력`이 있으면 실제로 꺾은선 그래프 생성
- **(경미, 개선6)** Ch04-PT내용.md에 LLM 출력 비결정성 안내 추가
- 개선 제안을 검증하려고 새 실습용 샘플 데이터(`scripts/make_sample_excel_practice.py`, "2026년 3월 반려동물용품 온라인 거래 동향" — 일부러 감소 시나리오로 설계)와 단계별 실행 스크립트(`scripts/run_practice_stepbystep.py`, Ch02~Ch10을 Enter로 한 단계씩 진행하며 확인)를 만들어 실제로 처음부터 끝까지 실행하는 과정에서 **버그 2건을 추가로 발견·수정**: (1) 꺾은선그래프 설명문에 주어가 없어 LLM이 본문 확장 시 "디지털 콘텐츠 시장 규모는..."처럼 엉뚱한 주제를 지어내던 환각(6차시 line 기능이 이번에 처음 실전 투입되며 드러남), (2) AI 감수 응답이 `max_tokens` 한도에 걸려 잘리면 파이프라인 전체가 죽던 크래시(`max_tokens` 상향 + 파싱 실패 시 예외 대신 안내 항목 반환)
- 테스트 50개 → **63개**로 확대 (감소 케이스 회귀 2건, `derive_history_indicators` 4건, io 이력 시트 1건, charts line 활성화·주어 포함 2건, headline 참고문구 2건, main.py 실제 호출 통합 테스트 1건, review 파싱 실패 폴백 1건), 전부 통과
- 상세 내용은 [IMPLEMENTATION_LOG.md "12. 7차 세션"](IMPLEMENTATION_LOG.md) 참고

### 완료 체크리스트

- [x] 프로젝트 폴더 구조 생성 (`modules/`, `tests/`, `data/`, `images/`, `output/`, `logs/`, `scripts/`)
- [x] `requirements.txt` / `.env.example` / `.gitignore` / `CLAUDE.md`
- [x] `modules/io.py`, `clean.py`, `nlp.py`, `stats.py`, `charts.py`, `write.py`, `review.py`, `main.py`
- [x] 공용 테스트 픽스처(`tests/fixtures/sample_standard_data.json`) — 계산지표+품목별지표 통합
- [x] 샘플 xlsx 생성 스크립트 및 실행
- [x] 단위 테스트 30개 작성 및 전부 통과 확인
- [x] LLM 목업으로 전체 파이프라인(main 로직) 배선 검증
- [x] `python main.py` 실제 실행 → API 키 이전 단계까지 정상 동작 확인
- [x] 실행 중 발견한 문제 3건 수정 및 문서 반영
- [x] `README.md`, `IMPLEMENTATION_LOG.md` 작성
- [x] 실제 `ANTHROPIC_API_KEY`로 전체 파이프라인 실행 (2026-09-06)
- [x] 실제 API 호출 구간에서만 발현되는 버그 8건 발견 및 수정
- [x] 품목별지표 포함 xlsx 전체 경로 실행 검증, PDF 입력 경로 실행 검증
- [x] `mask_sensitive_info` 파이프라인 연결
- [x] `modules/io.py`, `modules/write.py` 단위 테스트 추가 (30개 → 43개)
- [x] 공공데이터포털 API 실제 서비스 키로 연동 검증 (2026-09-07), 이중 인코딩 버그 수정
- [x] `tests/test_ch02_public_api.py` 추가 (43개 → 47개)
- [x] 가격정보 API를 실제로 사용하는 `main_price.py` 통계 보도자료 파이프라인 구축 (2026-09-07)
- [x] `review.py`의 음수 증감률 검증 버그, 헤드라인 숫자 콤마 누락 버그 발견·수정 (47개 → 50개)
- [x] `REVIEW_Ch02-10.md` 검토 보고서 작성 및 개선 제안 6가지 전부 실행 (2026-09-10, 50개 → 61개)

### 8차: "진짜 원자료"부터 시작하는 실습으로 근본 재설계 (2026-09-11)
- 사용자가 "실습을 처음부터 시작한다면 왜 이미 계산된 값이 든 파일에서 시작하는가"를 지적 → `main_price.py` 스타일로 근본 재설계하기로 결정, [PLAN_raw_data_redesign.md](PLAN_raw_data_redesign.md)로 먼저 설계 문서화
- `modules/pet_input.py`(원자료 3개 시트 읽기, 계산 없음), `modules/pet_stats.py`(표본매출을 품목별로 groupby 집계 + 증감률·특이점·해석문장 전부 계산) 신규 작성
- `modules/stats.py::derive_history_indicators`를 확장해 전월대비/전년동월대비증감률까지 이력만으로 계산하도록 함(기존에는 역대최대·최근3개월만 자동 계산). "특이점→해석문장" 로직을 `build_interpretation_sentences`로 추출해 `add_calculated_indicators`와 `pet_stats.py`가 공유
- `main_practice.py` 신규 진입점 — `main.py`/`main_price.py`와 나란한 세 번째 예시. 계산 단계만 새로 작성하고, 그래프·헤드라인·본문·검수·저장은 전부 기존 함수 재사용
- 실제 실행 중 버그 1건 추가 발견·수정: 이력(float)과 새로 계산한 총거래액(int)이 섞여 "49,700.0억 원"으로 표시되며 수치교차검증이 실패하던 문제 (상세: [IMPLEMENTATION_LOG.md "13. 8차 세션"](IMPLEMENTATION_LOG.md))
- 테스트 63개 → **75개**로 확대, 전부 통과. `data/raw/반려동물용품_2026_03_원자료.xlsx`로 표기오류 0건·수치교차검증 통과 확인

---

## 2. 앞으로 해야 할 일 (우선순위 순)

> **2026-09-06 갱신**: 아래 🔴/🟠/🟡 항목은 이번 세션에서 실제로 진행했습니다. 무엇을 어떻게 했고 실행 중 어떤 버그를 새로 발견·수정했는지는 [IMPLEMENTATION_LOG.md](IMPLEMENTATION_LOG.md)의 "8. 4차 세션" 항목에 시각별로 정리되어 있습니다. 요약: 실제 API 키로 처음 돌리자마자 인증 오류로 실패했고, 그걸 고치니 본문이 텅 비었고, 그걸 고치니 숫자 표기가 어긋났고... 하는 식으로 **총 8건의 버그를 연쇄적으로 발견·수정**했습니다. 문서 리뷰나 목업 테스트로는 절대 못 잡는 유형이었다는 게 이번에 실제로 증명되었습니다.

### 🔴 최우선 — 실제 API 키로 품질 검증
- [x] Anthropic API 키 발급 후 `.env`의 `ANTHROPIC_API_KEY`에 입력 (2026-09-06, 사용자가 직접 처리)
- [x] `python main.py` 재실행 → 여러 차례 재실행하며 아래를 확인
  - [x] `검수결과.수치교차검증.통과`가 실제로 `True`인지 — **여러 번 `False`가 나왔고 원인 3가지(인증 순서, 숫자 단위 불일치 2건)를 찾아 수정 후 `True`로 통과함을 확인**
  - [x] 표기오류검사 — 마지막 실행에서 0건
  - [x] AI 감수 지적사항이 타당한가 — 대부분 타당한 지적(품목 일부 누락 등, 8-3 참고)이었고, 1건은 AI 감수 자체의 착오였음을 확인
  - [ ] 제목·부제·리드문의 6하원칙 충족 여부, 본문 두괄식 구조·연결어 자연스러움은 **기계적으로는 확인했으나 사람이 문장을 읽고 최종 판단하는 절차는 아직 남음** — `output/2026-01 온라인쇼핑 동향.txt`를 열어 직접 읽어보는 것을 권장
- [ ] 모델 ID 재확인: `modules/write.py`의 `MODEL_NAME = "claude-sonnet-4-5"`가 재개 시점에도 유효한지 콘솔에서 확인 (이번 세션에서는 정상 호출되어 존재는 확인했으나 "최신" 여부는 재개 시점에 다시 확인 권장)

### 🟠 다음 우선순위 — 미실행 실습 보완
- [x] **2차시 공공데이터포털 Open API 연동**: 실제 서비스 키로 검증 완료 (2026-09-07). 단, **활용신청한 상세기능이 Ch02 예시와 다른 API였습니다** — 사용자가 실제로 승인받은 것은 "국가데이터처(구 통계청)_온라인 수집 가격 정보"(품목 리스트 조회 `getPriceItemList` + 가격정보 조회 `getPriceInfo`, 응답은 XML)였고, Ch02 예시가 가정한 가상의 "온라인쇼핑 동향"(JSON) API가 아니었습니다. 실제 호출 중 이중 인코딩 문제(발급받은 키가 이미 URL-인코딩된 "Encoding" 키였음)까지 재현·수정했습니다. 검증된 코드는 `scripts/fetch_public_api_sample.py`, 테스트는 `tests/test_ch02_public_api.py` (4건) 참고. 상세 경위: IMPLEMENTATION_LOG.md "10. 5차 세션"
- [x] **품목별지표 포함 xlsx로 전체 경로 실행**: `scripts/make_sample_excel_full.py`로 상세 샘플을 만들어 그래프 생성(6차시)까지 포함한 전체 경로를 실제로 실행·확인함. 이 과정에서 xlsx의 리스트/불리언 컬럼이 애초에 파싱되지 않던 버그, 통계 해석문 필드가 표준화 단계에서 유실되던 버그를 발견·수정함
- [x] **PDF 입력 경로 검증**: `scripts/make_sample_pdf.py`로 샘플 PDF를 만들어 `load_input`의 `.pdf` 분기를 실행 → pdfplumber가 한글을 깨짐 없이 정상 추출함을 확인 (버그 없음)
- [x] **`mask_sensitive_info` 파이프라인 연결**: `modules/clean.py::clean_and_structure` 안에서 원문에 대해 호출하도록 연결 완료

### ✅ 가격정보 API로 실제 보도자료 파이프라인 구축 완료 (2026-09-07, 6차 세션)
- [x] **`main_price.py` 신규 진입점**: 실제 가격정보 API(당월/전월/전년동월 평균가격)로 통계 보도자료를 끝까지 생성·검증. 기존 `main.py`는 건드리지 않고, `modules/public_api.py`(API 연동), `modules/price_stats.py`(평균가격 집계·해석문), `modules/price_report.py`(헤드라인·그래프 설명) 3개 모듈을 새로 만들어 붙였습니다. `modules/review.py`(검증·문체통일·AI감수)와 `modules/write.py`의 `expand_to_paragraph`/`generate_body_paragraphs`는 지표명에 의존하지 않는 범용 코드라 수정 없이 재사용했습니다.
- [x] 실행 결과: `output/2026-08 생필품 가격 동향.txt` — 표기오류검사 0건, 수치교차검증 통과(불일치 없음). 실행 파일은 [IMPLEMENTATION_LOG.md "11. 6차 세션"](IMPLEMENTATION_LOG.md) 11-4 참고
- [x] 이 과정에서 진짜 버그 2건을 새로 발견·수정: (1) 프롬프트에 넣은 큰 숫자에 콤마가 안 붙어 표기오류로 걸리던 문제, (2) **`review.py`의 수치교차검증이 음수 증감률(하락)을 못 알아보던 버그** — 기존 온라인쇼핑 예시는 증감률이 항상 양수였던 탓에 지금까지 발견되지 않았던, 실행해봐야만 드러나는 버그였습니다.
- [x] "품목별 본문 설명이 일부 품목·증감률을 다루지 않는다"는 이전 논의 항목은 이번 파이프라인에서 등락률 비교 문단을 별도로 추가해 부분적으로 개선했습니다 (완전히 해결된 것은 아니며, AI 감수가 여전히 "평균 증가율 이면의 품목별 등락 폭 설명 부족"을 지적함 — 문체/구성 개선의 여지로 남아있음)

### 🟡 테스트 커버리지 보완
- [x] `modules/io.py`에 대한 단위 테스트 추가 완료 (`tests/test_ch07_io.py`, 5건 — xlsx 기본/JSON 컬럼 파싱, PDF 목업, 확장자 오류, 저장)
- [x] `modules/write.py`의 프롬프트 생성 함수 단위 테스트 추가 완료 (`tests/test_ch04_write.py`, 8건 — `build_summary_prompt`, `select_core_indicators`, `build_headline_prompt`, `parse_json_response` 포함, 실제로 겪은 JSON 파싱 버그의 회귀 테스트 포함)
- 테스트는 30개 → **50개**로 증가, 전부 통과 (공공데이터포털 API 연동 테스트 6건, 음수 증감률 회귀 테스트 포함)

### 🟢 문서화된 확장 과제 (10차시에 이미 "향후 확장"으로 명시된 것들, 미착수)
- [ ] hwpx/docx 등 공식 보도자료 서식으로 최종 변환 (현재는 `.txt` 저장까지만 구현)
- [ ] 다른 통계표(물가, 수출입 등)에도 동일 파이프라인 재사용 — 재사용 시 `modules/nlp.py`의 `kiwi.add_user_word(...)` 목록에 해당 도메인 복합명사 추가 필요
- [ ] 여러 파일을 한 번에 처리하는 배치 실행 기능
- [ ] 웹 인터페이스 연동

---

## 3. 알아두면 좋은 것 (재개할 때 헷갈리지 않도록)

- **`.env` 파일은 git에 올라가지 않습니다** (`.gitignore`에 포함). `.env.example`은 삭제되었으므로, 다른 컴퓨터/새 클론에서 재개한다면 `.env` 파일을 새로 만들어 `ANTHROPIC_API_KEY=...`, `PUBLIC_API_KEY=...` 두 줄을 직접 입력해야 합니다.
- **`myvenv/`도 git 추적 대상이 아닙니다.** 다른 컴퓨터/새 클론에서 재개한다면 `python -m venv myvenv` + `pip install -r requirements.txt`부터 다시 해야 합니다.
- 테스트는 전부 **API 키 없이 실행 가능**합니다 (`test_ch10_pipeline.py`만 목업으로 LLM을 대체). API 키가 있어야만 확인 가능한 것은 위 "🔴 최우선" 항목뿐입니다.
- 각 차시 문서(`ChNN-PT내용.md`, `ChNN-실습.md`)의 `> **[수정]**` 표시가 이번 세션까지 반영된 모든 수정 이력입니다. 문서와 `modules/` 코드는 서로 동기화되어 있어야 하며, 앞으로 코드를 더 고치면 해당 문서에도 `[수정]` 노트를 남기는 방식을 유지하세요.
- `.env`의 `PUBLIC_API_KEY`는 실제 발급받은 값으로 채워져 있고 정상 작동을 확인했습니다(2026-09-07). 단, 이 키는 "온라인쇼핑 동향"이 아니라 "온라인 수집 가격 정보"(품목별 가격 조회) API용입니다 — Ch02 문서의 원래 예시와 다른 API이니 재개 시 헷갈리지 마세요.
- 이 컴퓨터는 matplotlib 기본 백엔드(`TkAgg`)의 Tcl/Tk 설치가 손상되어 있어 `savefig`만 해도 간헐적으로 `_tkinter.TclError`가 날 수 있습니다. `modules/charts.py`에 `matplotlib.use("Agg")`를 명시해 두었으니 새 스크립트에서 matplotlib을 쓸 때도 같은 방식을 따르세요.
- `data/raw/온라인쇼핑동향_2026_01_상세.xlsx`(품목별지표 포함)와 `data/raw/온라인쇼핑동향_2026_01.pdf`가 새로 생겼습니다. 둘 다 git 추적 제외 대상이라 재클론 시 각각 `scripts/make_sample_excel_full.py`, `scripts/make_sample_pdf.py`로 재생성해야 합니다.

---

## 4. 참고 문서 지도

| 문서 | 용도 |
| --- | --- |
| **TASKS.md** (이 문서) | 재개용 상태 요약 + 할 일 목록 |
| [IMPLEMENTATION_LOG.md](IMPLEMENTATION_LOG.md) | 무엇을 왜 그렇게 고쳤는지의 상세 경위 |
| [README.md](README.md) | 프로젝트 실행 방법, 폴더 구조 |
| [CLAUDE.md](CLAUDE.md) | 코딩 규칙 (수치 계산은 프로그램, AI는 문장만 등) |
| `ChNN-PT내용.md` / `ChNN-실습.md` | 차시별 강의 원본 + 수정 이력(`[수정]` 노트) |
