# Task 문서 (진행 상황 및 재개 가이드)

이 문서는 **다음에 이어서 작업할 때 가장 먼저 읽어야 할 문서**입니다. 지금까지 무엇을 했는지, 무엇이 검증되었는지, 다음에 무엇부터 해야 하는지를 정리했습니다. 세부 경위(왜 그렇게 고쳤는지)는 [IMPLEMENTATION_LOG.md](docs/IMPLEMENTATION_LOG.md)를 참고하세요.

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

`pytest`가 75개 모두 통과하지 않는다면, 그 사이 파이썬/패키지 버전이 바뀌었거나 파일이 수정된 것이므로 원인부터 파악하세요.

**문서 위치가 두 차례 바뀌었습니다** (2026-09-18, 10~11차 세션):
- `Ch02-실습.md` ~ `Ch10-실습.md` → **`labs/`**로 이동, PPT 슬라이드 구조에서 손으로 따라 하는 단계별 실행 가이드로 전면 재작성. 앞으로 실습 파일은 전부 `labs/`에 둘 것
- `Ch01-PT내용.md` ~ `Ch10-PT내용.md`, `re-ch01.md` → **`pt/`**로 이동
- `IMPLEMENTATION_LOG.md`, `PLAN_raw_data_redesign.md`, `REVIEW_Ch02-10.md`, 참고자료 3종 → **`docs/`**로 이동
- 루트에는 `README.md`/`CLAUDE.md`/`TASKS.md`와 실행용 코드·데이터 디렉토리만 남음

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
- 상세 내용과 시각별 타임라인은 [IMPLEMENTATION_LOG.md "8. 4차 세션"](docs/IMPLEMENTATION_LOG.md) 참고

### 5차: 공공데이터포털 API 실제 연동 (2026-09-07)
- 사용자가 실제로 활용신청·승인받은 API는 Ch02 예시(가상의 온라인쇼핑 동향 JSON API)와 달리 **"국가데이터처(구 통계청)_온라인 수집 가격 정보"**(품목 리스트 조회 + 가격정보 조회, XML 응답) API였음을 확인
- data.go.kr 공식 활용가이드 문서(v2.2.docx)를 다운로드해 정확한 요청변수(`itemCode`, `startDate`/`endDate` 등) 명세를 확보
- 실제 호출 중 **이중 URL 인코딩 문제**(발급받은 키가 이미 인코딩된 "Encoding" 키였음)를 재현하고, `urllib.parse.unquote()`로 방어하도록 수정
- 두 오퍼레이션(`getPriceItemList`, `getPriceInfo`) 모두 실제 서비스 키로 정상 호출·파싱됨을 확인 (`scripts/fetch_public_api_sample.py` 신규 작성)
- Ch02-PT내용.md에 실제와 다른 점(XML 응답, 이중 인코딩, 파라미터 형식) `[수정]` 노트로 반영
- `tests/test_ch02_public_api.py` 신규 작성(4건, 네트워크 목업)으로 테스트 43개 → 47개
- 상세 내용은 [IMPLEMENTATION_LOG.md "10. 5차 세션"](docs/IMPLEMENTATION_LOG.md) 참고

### 6차: 가격정보 API로 실제 통계 보도자료 파이프라인 구축 (2026-09-07, 11:16~11:43)
- `main.py`(온라인쇼핑 동향, xlsx 기반)는 건드리지 않고 별도 진입점 `main_price.py`를 신규 작성
- `modules/public_api.py`(API 호출을 스크립트에서 모듈로 승격 + 평균가격 계산), `modules/price_stats.py`(집계·해석문), `modules/price_report.py`(가격 데이터 전용 헤드라인·그래프 설명) 3개 모듈 신규 작성
- `modules/review.py`(수치검증·문체통일·AI감수)와 `modules/write.py`의 본문 확장 함수는 지표명에 의존하지 않는 범용 코드임을 확인하고 그대로 재사용
- 실제 API + 실제 LLM으로 끝까지 실행해 **표기오류검사 0건, 수치교차검증 통과**하는 보도자료 완성 (`output/2026-08 생필품 가격 동향.txt`)
- 이 과정에서 진짜 버그 2건 발견·수정: 큰 숫자 콤마 누락, **음수 증감률(하락)을 검증 못 하던 `review.py`의 숨은 버그** — 기존 예시가 항상 양수만 다뤘던 탓에 지금까지 안 드러났던 버그
- 테스트 47개 → 50개로 확대
- 상세 내용은 [IMPLEMENTATION_LOG.md "11. 6차 세션"](docs/IMPLEMENTATION_LOG.md) 참고

### 7차: 검토 보고서(REVIEW_Ch02-10.md) 개선 제안 실행 (2026-09-10)
- 사용자 요청으로 Ch02~Ch10 PT·실습 자료를 실제 코드와 대조 검토해 [REVIEW_Ch02-10.md](docs/REVIEW_Ch02-10.md) 작성, 그 안의 개선 제안 6가지를 모두 실행함
- **(시급, A-2 수정)** `add_calculated_indicators`/`generate_interpretation`에 "큰 폭 감소", "연속 감소세" 템플릿 추가 — 하락하는 통계에서 특이점은 감지되는데 해석문장이 조용히 비던 결함 수정
- **(중요, A-1 수정)** `derive_history_indicators` 신규 작성 — xlsx의 "이력" 시트(연월, 총거래액)를 `load_input`이 읽어 `역대최대여부`/`최근3개월증감률`을 자동 계산. 이전에는 담당자가 과거 자료를 직접 조사해 수작업으로 입력해야 했음
- **(중요, A-3 수정)** `main.py`가 `generate_summary`(4차시)를 실제로 호출해 `요약결과`에 저장하고, 그 `제목후보`를 7차시 헤드라인 프롬프트에 참고용으로 전달 — 이전에는 어디서도 호출되지 않던 죽은 코드였음(사실 확정 근거는 여전히 5차시 계산 결과만 사용)
- **(개선, B-1 일부)** `modules/config.py` 신규 — `REQUIRED_FIELDS`/`INDICATOR_UNITS` 하드코딩을 한곳으로 모음 (완전한 재사용성 보장은 아니며, `modules/stats.py`/`modules/io.py`의 필드 구조 의존은 여전히 남아 있음)
- **(경미, 개선5 수정)** 꺾은선그래프(line)가 `build_visual_descriptions`에서 실제로는 도달 불가능한 "고아 기능"이었던 문제 수정 — `월별이력`이 있으면 실제로 꺾은선 그래프 생성
- **(경미, 개선6)** Ch04-PT내용.md에 LLM 출력 비결정성 안내 추가
- 개선 제안을 검증하려고 새 실습용 샘플 데이터(`scripts/make_sample_excel_practice.py`, "2026년 3월 반려동물용품 온라인 거래 동향" — 일부러 감소 시나리오로 설계)와 단계별 실행 스크립트(`scripts/run_practice_stepbystep.py`, Ch02~Ch10을 Enter로 한 단계씩 진행하며 확인)를 만들어 실제로 처음부터 끝까지 실행하는 과정에서 **버그 2건을 추가로 발견·수정**: (1) 꺾은선그래프 설명문에 주어가 없어 LLM이 본문 확장 시 "디지털 콘텐츠 시장 규모는..."처럼 엉뚱한 주제를 지어내던 환각(6차시 line 기능이 이번에 처음 실전 투입되며 드러남), (2) AI 감수 응답이 `max_tokens` 한도에 걸려 잘리면 파이프라인 전체가 죽던 크래시(`max_tokens` 상향 + 파싱 실패 시 예외 대신 안내 항목 반환)
- 테스트 50개 → **63개**로 확대 (감소 케이스 회귀 2건, `derive_history_indicators` 4건, io 이력 시트 1건, charts line 활성화·주어 포함 2건, headline 참고문구 2건, main.py 실제 호출 통합 테스트 1건, review 파싱 실패 폴백 1건), 전부 통과
- 상세 내용은 [IMPLEMENTATION_LOG.md "12. 7차 세션"](docs/IMPLEMENTATION_LOG.md) 참고

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
- [x] `Ch02-실습.md` ~ `Ch10-실습.md`를 `labs/`로 이동하고 단계별 실행 가이드로 전면 재작성, 파일 기반 실습 체인(`data/processed/press_data.json`) 도입 (2026-09-18)
- [x] `labs/REVIEW_LOG_2026-09-18.md` 작성 — 재구성 과정·발견한 문제·차시별 산출물 정리

### 8차: "진짜 원자료"부터 시작하는 실습으로 근본 재설계 (2026-09-11)
- 사용자가 "실습을 처음부터 시작한다면 왜 이미 계산된 값이 든 파일에서 시작하는가"를 지적 → `main_price.py` 스타일로 근본 재설계하기로 결정, [PLAN_raw_data_redesign.md](docs/PLAN_raw_data_redesign.md)로 먼저 설계 문서화
- `modules/pet_input.py`(원자료 3개 시트 읽기, 계산 없음), `modules/pet_stats.py`(표본매출을 품목별로 groupby 집계 + 증감률·특이점·해석문장 전부 계산) 신규 작성
- `modules/stats.py::derive_history_indicators`를 확장해 전월대비/전년동월대비증감률까지 이력만으로 계산하도록 함(기존에는 역대최대·최근3개월만 자동 계산). "특이점→해석문장" 로직을 `build_interpretation_sentences`로 추출해 `add_calculated_indicators`와 `pet_stats.py`가 공유
- `main_practice.py` 신규 진입점 — `main.py`/`main_price.py`와 나란한 세 번째 예시. 계산 단계만 새로 작성하고, 그래프·헤드라인·본문·검수·저장은 전부 기존 함수 재사용
- 실제 실행 중 버그 1건 추가 발견·수정: 이력(float)과 새로 계산한 총거래액(int)이 섞여 "49,700.0억 원"으로 표시되며 수치교차검증이 실패하던 문제 (상세: [IMPLEMENTATION_LOG.md "13. 8차 세션"](docs/IMPLEMENTATION_LOG.md))
- 테스트 63개 → **75개**로 확대, 전부 통과. `data/raw/반려동물용품_2026_03_원자료.xlsx`로 표기오류 0건·수치교차검증 통과 확인

### 9차: 학생 대상 강의안(`./lect/`) `[수정]` 이력 제거 및 `[Note]` 전면 보강 (2026-09-12)
- 사용자가 "이 강의안은 바로 학생들에게 보여질 내용"이라며, `./lect/CH-01~10-Content.md`에 남아있던 개발 이력 주석(`> **[수정]**`)을 학생에게 부적절하다고 지적 → 전체 제거
- 강의 중 슬라이드 본문이 아니라 `[Note]`만 소리 내어 읽을 것이므로, 페이지 06 이후 모든 `[Note]`를 그 페이지 내용을 혼자서도 완결되게 설명하는 발표 대본 수준(문단당 4~8문장)으로 재작성
- `[수정]` 블록 중 학생이 알아야 할 실질적 기술 정보(kiwipiepy 토크나이저 특성, LLM 헤드라인 헛구름(hallucination) 사례, `review_press_release` 응답 절단 크래시 원인 등)는 자기참조 서술만 걷어내고 해당 `[Note]`에 직접 설명으로 흡수
- `CH-01`~`CH-10-Content.md` 10개 파일 전체 재작성 완료. `[수정]` 문자열 0건, `### 페이지 NN` 개수와 `[Note]` 개수 1:1 일치 확인 (상세: [IMPLEMENTATION_LOG.md "14. 9차 세션"](docs/IMPLEMENTATION_LOG.md))
- `ChNN-PT내용.md`(원본 개발 이력 문서, 현재 `pt/`)는 미변경 — `[수정]` 이력은 그대로 유지, `./lect/` 학생 배포용 사본에서만 제거됨

### 10차: 2~10차시 실습 자료를 `labs/`로 전면 재구성 + 실행 검증 (2026-09-18)
- 사용자가 정한 우선순위 원칙 적용: ① 실습 파일(`-실습.md`)이 강의안보다 우선, ② 실습은 `lect/CH-NN-Content.md`(학생 배포용 강의안)를 참고해서 검토, ③ 앞으로 실습 파일은 전부 `labs/` 디렉토리에 저장
- 루트의 `Ch02-실습.md` ~ `Ch10-실습.md` 9개 파일을 `git mv`로 `labs/`로 이동하고, PPT 슬라이드("페이지 N, 실습 절차 1/2/3") 구조를 **0단계부터 이어지는 손으로 따라 하는 실행 가이드**로 전면 재작성
- **파일 기반 실습 체인 신규 도입**: 2차시가 `data/processed/press_data.json`을 생성하고, 3~10차시가 이 파일을 `json.load`로 불러와 필드를 추가한 뒤 다시 저장 — "이전 차시 결과를 이어받는다"는 서술만 있던 것을 실제 파일로 만듦(`.gitignore`에 `data/processed/*.json` 추가, `output`/`images`/`logs`와 동일하게 재생성 가능한 산출물로 취급)
- 각 실습 문서 상단에 "이 실습으로 만들어지는 것"(생성되는 JSON 필드·이미지·텍스트 파일)을 구체적으로 명시, LLM 호출 단계에는 비용·비결정성 경고 추가
- **실제로 코드를 실행하며 새로 발견한 문제** (상세 근거는 [labs/REVIEW_LOG_2026-09-18.md](labs/REVIEW_LOG_2026-09-18.md)):
  1. 5차시 문서의 품목별 비중 예시값(32.4%/25.9%, 합계 100.3%)이 실제 `pandas` 계산값(32.3%/25.8%, 합계 100.0%)과 달랐음 — 검증 없이 쓰인 값이었던 것으로 보임. 5·6·8차시 문서를 전부 실측값으로 교체
  2. `add_calculated_indicators`가 지표명을 `제목.split()[-1]`로 추출하는데, 제목이 "~동향"으로 끝나면 "**동향**은 201250억 원로 역대 최대치를 기록하였다"처럼 어색한 문장이 나옴 — 코드는 고치지 않고(범위 밖) 실습 문서에 현상과 우회법(`build_interpretation_sentences`에 지표명 직접 지정)을 기록
  3. **검증 시스템이 실제로 작동하는 사례를 재현**: AI가 본문에서 "상위 세 품목이 전체의 82.0%를 차지"처럼 스스로 계산한 파생 수치를 넣으면 `cross_check_all_numbers`가 실제로 이를 불일치로 잡아냄 — CLAUDE.md 원칙("계산은 AI에게 맡기지 않는다")이 왜 필요한지 보여주는 실제 사례로 9차시 핵심 예시로 채택
  4. 기존 8차시 문서가 참조하던 `assemble_body` 함수가 실제 코드베이스에는 없음(존재하는 것은 9차시의 `assemble_full_text`) — 문서에서 참조 제거
  5. `tests/test_ch08_write.py`가 존재하지 않음(8차시 함수는 LLM 호출 전용이라 `test_ch10_pipeline.py`가 목업으로 배선만 검증) — 문서에 명시
  6. `load_input`으로 실제 xlsx(`data/raw/온라인쇼핑동향_2026_01.xlsx`)를 읽으면 제목이 "2026-01 온라인쇼핑 동향"(하이픈)으로 나와, 지금까지 문서가 써온 "2026년 1월 온라인쇼핑 동향"과 표기가 다름 — 버그 아님, 원인과 함께 7차시 문서에 기록
- 이번 재검토에서는 **실제 Claude API를 직접 호출하지 않았음** (비용 발생 방지) — 프롬프트 조립·JSON 파싱·수치 검증 등 비-LLM 로직은 전부 실제 실행으로 검증했고, LLM 응답 예시는 과거 세션에서 실제로 API를 호출해 확인한 값을 재사용하되 "표현은 매번 달라질 수 있음"을 명시
- `pytest tests/ -v` **75개 전부 통과** 재확인 (변경 없음, 회귀 없음을 확인)
- 상세 근거와 차시별 산출물 표는 [labs/REVIEW_LOG_2026-09-18.md](labs/REVIEW_LOG_2026-09-18.md) 참고

### 11차: 루트에 흩어진 문서를 3단계 콘텐츠 구조로 재정리 (2026-09-18)
- "문서들의 위치를 구조적으로 파악하기 쉽게 정리해달라"는 요청에 따라, 사용자에게 구조 옵션을 확인(3단계 콘텐츠 구조 선택)한 뒤 진행
- **`pt/` 신설** — `Ch01-PT내용.md` ~ `Ch10-PT내용.md`(10개)와 `re-ch01.md`를 `git mv`로 이동. 이제 `pt/`(강의 개발 원본) → `lect/`(학생 배포용) → `labs/`(손으로 하는 실습)이 나란한 3단계 구조가 됨
- **`docs/` 신설** — `IMPLEMENTATION_LOG.md`, `PLAN_raw_data_redesign.md`, `REVIEW_Ch02-10.md`(프로젝트 관리/이력 문서)와 `AI를활용한통계보도자료작성-10차시개요.txt`, `공공데이터포털API신청.txt`, `통계청_온라인수집가격정보_OPEN-API활용가이드_v2.2.docx`(참고자료 3종)를 이동
- 루트에는 **README.md·CLAUDE.md·TASKS.md**(가장 먼저 읽어야 할 3개 문서)와 `main*.py`, `modules/`, `tests/`, `scripts/`, `data/` 등 실행에 필요한 코드·데이터 디렉토리만 남김
- **실제 코드 의존성 발견 및 수정**: `scripts/generate_lecture_content.py`가 `re-ch01.md`와 `ChNN-PT내용.md`를 프로젝트 루트에서 직접 읽고 있었음(단순 docs가 아니라 `lect/` 생성 파이프라인의 실제 입력이었음) — `PT_DIR` 상수를 추가해 `pt/`를 읽도록 수정 (단, `lect/` 파일이 이미 커밋 전 상태로 수정되어 있어 이번에는 스크립트를 실행하지 않고 경로만 고쳐둠)
- 이동한 파일들이 서로 참조하던 마크다운 링크(`modules/`, `tests/`, `scripts/`, `main.py`, 다른 문서 등 총 60여 건)를 전부 새 위치 기준 상대경로로 일괄 수정 — `docs/` 안에서 서로를 참조하는 링크(`IMPLEMENTATION_LOG.md` ↔ `REVIEW_Ch02-10.md` ↔ `PLAN_raw_data_redesign.md`)는 같은 폴더로 함께 이동했으므로 `../` 없이 그대로 둠
- `README.md`·`TASKS.md`의 문서 지도, 안내 문구도 새 경로에 맞게 갱신
- 코드가 이동한 것이 아니라 문서만 이동했으므로 `pytest tests/ -v` 재실행으로 회귀 없음 확인(75 passed)

---

## 2. 앞으로 해야 할 일 (우선순위 순)

### 🔴 최우선 — 10~11차 재구성 마무리 (세션 직후 남은 일)
- [ ] **git commit**: `labs/`·`pt/`·`docs/` 신설을 포함한 `git mv` 20여 건 + `.gitignore` 수정 + 신규 파일(`labs/REVIEW_LOG_2026-09-18.md`) + 링크 일괄 수정 + `scripts/generate_lecture_content.py` 경로 수정이 아직 커밋되지 않았습니다. 사용자 승인 후 커밋할 것
- [ ] **실제 API로 `labs/` 문서의 LLM 단계를 직접 한 번씩 실행**: 이번 재검토에서는 비용 문제로 `generate_summary`/`generate_headline_set`/`generate_body_paragraphs`/`unify_style`/`review_press_release`를 직접 호출하지 않았습니다. 문서에 적힌 "예시 실행 결과"는 과거 세션 값을 재사용한 것이므로, 다음에 API 키로 한 번 쭉 실행하며 예시 결과가 여전히 그럴듯한지 확인 권장 (숫자·형식만 맞으면 문장 표현 자체는 달라져도 무방)
- [ ] 9차시 문서에서 의도적으로 재현한 "82.0% 파생 수치 불일치" 예시가, 실제로 8차시 LLM이 매번 같은 표현("상위 세 품목이 전체의 82.0%를 차지")을 쓰지 않을 수 있음 — 실제 실행 시 이 문장이 안 나오면 검증 실패 사례를 손으로 재현하도록 문서에 안내가 필요할 수 있음

### 🟠 다음 우선순위 — 이번에 발견했지만 코드는 고치지 않은 문제 처리 여부 결정
- [ ] `modules/stats.py::add_calculated_indicators`의 지표명 자동 추출(`제목.split()[-1]`)이 "~동향"으로 끝나는 제목에서 "동향은 ~"처럼 어색한 문장을 만드는 문제 — 고칠지(예: 제목에서 "동향"/"현황" 등 접미어를 제외하고 추출) 여부 결정 필요
- [ ] AI가 본문에서 파생 수치(품목 비중 합계 등)를 스스로 계산해 넣을 때 `cross_check_all_numbers`가 잡아내기만 하고 고쳐주지는 않는 문제 — 근본 해결은 `modules/stats.py`가 상위 N개 누적 비중 같은 파생값을 미리 계산해 `계산지표`에 넣어주는 것. 실습용 예시로 남겨둘지, 실제로 고칠지 결정 필요
- [ ] `modules/charts.py::generate_table_description`이 여전히 `build_visual_descriptions`에서 호출되지 않는 별도 함수로 남아있음 — 연결할지, "심화 학습용"으로 문서에만 남길지 결정 필요

> **2026-09-06 갱신**: 아래 🔴/🟠/🟡 항목은 이번 세션에서 실제로 진행했습니다. 무엇을 어떻게 했고 실행 중 어떤 버그를 새로 발견·수정했는지는 [IMPLEMENTATION_LOG.md](docs/IMPLEMENTATION_LOG.md)의 "8. 4차 세션" 항목에 시각별로 정리되어 있습니다. 요약: 실제 API 키로 처음 돌리자마자 인증 오류로 실패했고, 그걸 고치니 본문이 텅 비었고, 그걸 고치니 숫자 표기가 어긋났고... 하는 식으로 **총 8건의 버그를 연쇄적으로 발견·수정**했습니다. 문서 리뷰나 목업 테스트로는 절대 못 잡는 유형이었다는 게 이번에 실제로 증명되었습니다.

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
- [x] 실행 결과: `output/2026-08 생필품 가격 동향.txt` — 표기오류검사 0건, 수치교차검증 통과(불일치 없음). 실행 파일은 [IMPLEMENTATION_LOG.md "11. 6차 세션"](docs/IMPLEMENTATION_LOG.md) 11-4 참고
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
- 각 차시 원본 문서(`pt/ChNN-PT내용.md`)의 `> **[수정]**` 표시가 이번 세션까지 반영된 모든 수정 이력입니다. 문서와 `modules/` 코드는 서로 동기화되어 있어야 하며, 앞으로 코드를 더 고치면 해당 문서에도 `[수정]` 노트를 남기는 방식을 유지하세요.
- **`./lect/CH-01~10-Content.md`(학생 배포용 강의안)에는 `[수정]` 표시를 남기지 마세요.** 9차 세션에서 전부 제거했고, 학생에게 보여지는 문서이므로 앞으로 이 폴더 파일을 고칠 때도 개발 이력 서술 없이 바로 최종 내용과 발표용 `[Note]`만 반영해야 합니다. 코드 변경으로 `pt/ChNN-PT내용.md`에 새 `[수정]` 노트가 생기면, `./lect/` 쪽에는 그 사실만 자연스러운 `[Note]` 설명으로 옮기세요.
- **11차 세션(2026-09-18)부터 문서 위치가 다시 한번 바뀌었습니다.** `ChNN-PT내용.md`(10개)와 `re-ch01.md`는 `pt/`로, `IMPLEMENTATION_LOG.md`/`PLAN_raw_data_redesign.md`/`REVIEW_Ch02-10.md`/참고자료 3종은 `docs/`로 이동했습니다. `scripts/generate_lecture_content.py`도 이 새 경로(`pt/`)를 읽도록 함께 수정했습니다. `README.md`/`CLAUDE.md`/`TASKS.md`와 `main*.py`, `modules/`, `tests/`, `scripts/`, `data/` 등 코드·실행 관련 디렉토리는 그대로 루트에 있습니다.
- `.env`의 `PUBLIC_API_KEY`는 실제 발급받은 값으로 채워져 있고 정상 작동을 확인했습니다(2026-09-07). 단, 이 키는 "온라인쇼핑 동향"이 아니라 "온라인 수집 가격 정보"(품목별 가격 조회) API용입니다 — Ch02 문서의 원래 예시와 다른 API이니 재개 시 헷갈리지 마세요.
- 이 컴퓨터는 matplotlib 기본 백엔드(`TkAgg`)의 Tcl/Tk 설치가 손상되어 있어 `savefig`만 해도 간헐적으로 `_tkinter.TclError`가 날 수 있습니다. `modules/charts.py`에 `matplotlib.use("Agg")`를 명시해 두었으니 새 스크립트에서 matplotlib을 쓸 때도 같은 방식을 따르세요.
- `data/raw/온라인쇼핑동향_2026_01_상세.xlsx`(품목별지표 포함)와 `data/raw/온라인쇼핑동향_2026_01.pdf`가 새로 생겼습니다. 둘 다 git 추적 제외 대상이라 재클론 시 각각 `scripts/make_sample_excel_full.py`, `scripts/make_sample_pdf.py`로 재생성해야 합니다.

---

## 4. 참고 문서 지도

| 문서 | 용도 |
| --- | --- |
| **TASKS.md** (이 문서) | 재개용 상태 요약 + 할 일 목록 |
| [IMPLEMENTATION_LOG.md](docs/IMPLEMENTATION_LOG.md) | 무엇을 왜 그렇게 고쳤는지의 상세 경위 |
| [README.md](README.md) | 프로젝트 실행 방법, 폴더 구조 |
| [CLAUDE.md](CLAUDE.md) | 코딩 규칙 (수치 계산은 프로그램, AI는 문장만 등) |
| `pt/ChNN-PT내용.md`, `pt/re-ch01.md` | 차시별 강의 원본 + 수정 이력(`[수정]` 노트). `lect/`를 만드는 소스 |
| `lect/CH-NN-Content.md` | 학생 배포용 강의안(발표 대본, `[수정]` 이력 없음) |
| **`labs/ChNN-실습.md`** | **손으로 따라 하는 실습 가이드 (2026-09-18부터 여기로 이동, 이제부터 실습 파일은 전부 여기에 저장)** |
| [labs/REVIEW_LOG_2026-09-18.md](labs/REVIEW_LOG_2026-09-18.md) | `labs/` 재구성 작업의 상세 근거·발견한 문제·차시별 산출물 |
| [docs/REVIEW_Ch02-10.md](docs/REVIEW_Ch02-10.md) | 2026-09-10 시점 PT/실습 자료 대조 검토 보고서 (이후 대부분 반영됨) |
| `docs/` 나머지 (10차시개요.txt, API 신청 메모, 활용가이드 docx) | 참고자료·과정 기획 원본 |
