# AI를 활용한 통계 보도자료 작성 실습 (Ch01~Ch10)

10개 차시의 강의안(`pt/ChNN-PT내용.md`)을 실제로 실행 가능한 파이썬 프로젝트로 구현한 것입니다. 학생 배포용 강의안은 `lect/`, 손으로 따라 하는 실습 가이드는 `labs/`에 있습니다.

## 빠른 시작

```bash
# 1. 가상환경 생성 및 활성화
python -m venv myvenv
myvenv\Scripts\activate.bat        # CMD
# 또는 myvenv\Scripts\Activate.ps1  # PowerShell

# 2. 패키지 설치
pip install -r requirements.txt

# 3. API 키 설정
# 프로젝트 루트에 .env 파일을 만들고 아래 두 줄을 입력
#   ANTHROPIC_API_KEY=발급받은키
#   PUBLIC_API_KEY=발급받은키          (data.go.kr, 2차시 공공 API 실습용. "Encoding"/"Decoding" 키 중 아무거나 넣어도 됨 — 코드에서 자동으로 디코딩함)
# (.env는 .gitignore에 포함되어 있어 git에 올라가지 않음)

# 4. 샘플 데이터 생성 (최초 1회)
python scripts/make_sample_excel.py        # 기본 샘플 (품목별지표 없음)
python scripts/make_sample_excel_full.py   # 전체 경로 확인용 샘플 (품목별지표 포함 → 6차시 그래프까지 생성됨)
python scripts/make_sample_pdf.py          # PDF 입력 경로 확인용 샘플

# 5. 단위 테스트 실행 (API 키 불필요, 84개)
pytest tests/ -v

# 6. 전체 파이프라인 실행 (API 키 필요)
python main.py            # 온라인쇼핑 동향 예시 (xlsx에 이미 계산된 표 입력)
python main_price.py      # 생필품 가격 동향 (공공데이터포털 실제 API, 진짜 원자료)
python main_practice.py   # 반려동물용품 예시 (표본매출 원자료 → 코드가 직접 집계·계산)

# 7. 직접 한 단계씩 실습해보기 (API 키 필요) — 진짜 원자료로 Ch02~Ch10을 Enter로 넘기며 확인
python scripts/make_sample_excel_practice_raw.py   # 샘플 xlsx 생성 (최초 1회, 계산된 숫자 없음)
python scripts/run_practice_stepbystep.py          # 단계별 실행 + 결과 확인
```

## 폴더 구조

| 경로 | 설명 |
| --- | --- |
| `modules/io.py` | 7·10차시: xlsx/PDF 입력, 최종 문서(txt) 저장 |
| `modules/export.py` | 10차시: 최종 보도자료를 PDF(`reportlab`)·HWPX(`python-hwpx`)로 저장 (`main.py`가 호출) |
| `modules/clean.py` | 2차시: 텍스트 정제·표준화·구조화, 개인정보 마스킹 |
| `modules/nlp.py` | 3차시: 명사/키워드(TF-IDF)/주요문장(TextRank) 추출 |
| `modules/stats.py` | 5차시: 증감률·비중·순위 계산, 특이점 탐지, 해석문 생성, 역대최대/추세 자동 계산(`derive_history_indicators`) |
| `modules/config.py` | 지표명·단위 하드코딩을 모아둔 설정 (`REQUIRED_FIELDS` 등) |
| `modules/charts.py` | 6차시: 그래프 생성 및 설명문 자동 생성 |
| `modules/write.py` | 4·7·8차시: LLM 기반 요약·헤드라인·본문 생성 (`MODEL_NAME` 상수 보유) |
| `modules/review.py` | 4·9차시: 수치 검증, 문체 통일, 표기 검수, AI 감수 |
| `main.py` | 10차시: 전체 파이프라인 진입점 (온라인쇼핑 동향, xlsx 기반 예시) |
| `modules/public_api.py` | 2차시: 공공데이터포털 "온라인 수집 가격 정보" Open API 연동 (실제 서비스 키로 검증됨) |
| `modules/price_stats.py` | 5차시(응용): 가격정보 API용 평균가격·등락률 계산, 해석문 생성 |
| `modules/price_report.py` | 6·7·8차시(응용): 가격정보 API용 헤드라인·그래프 설명 생성 |
| `main_price.py` | 10차시(응용): 공공데이터포털 실제 API 기반 통계 보도자료 진입점 (진짜 원자료 예시) |
| `modules/pet_input.py` | 8차 세션(응용): 표본 사업체별 매출 신고(원자료) 입력, 계산 없음 |
| `modules/pet_stats.py` | 8차 세션(응용): 표본매출을 품목별로 집계 + 증감률·특이점·해석문장 계산 |
| `main_practice.py` | 8차 세션(응용): 반려동물용품 실습 진입점 — "진짜 원자료"부터 시작하는 세 번째 예시 |
| `tests/` | 각 차시 모듈의 단위 테스트 (LLM 호출 없이 실행 가능) |
| `scripts/make_sample_excel.py` | 실습용 기본 샘플 xlsx 생성 (품목별지표 없음) |
| `scripts/make_sample_excel_full.py` | 품목별지표·역대최대여부 등을 포함한 "전체 경로" 샘플 xlsx 생성 |
| `scripts/make_sample_excel_practice_raw.py` | 표본 사업체별 매출 신고만 담은 원자료 샘플 생성 (계산된 숫자 없음) |
| `scripts/run_practice_stepbystep.py` | Ch02~Ch10을 Enter로 한 단계씩 넘기며 직접 확인하는 실습 스크립트 |
| `scripts/make_sample_pdf.py` | PDF 입력 경로 확인용 샘플 PDF 생성 |
| `scripts/fetch_public_api_sample.py` | 2차시: 공공 API 연동 최소 데모 (`modules/public_api.py` 사용) |

## 문서 구조

| 경로 | 설명 |
| --- | --- |
| `lect/` | 학생 배포용 강의안(md·pptx) |
| `pt/` | 강의 원본과 수정 이력 |
| `labs/ChNN-실습.md` | 표준 실습 — 완성된 `modules/`를 단계별로 실행하며 따라 하기 |
| `labs/강의자료/` | 강의 PPT 최종본(CH02~CH10-ContentV10.pptx, 검토 의견 반영 완료) |
| **`labs/quick/`** | **10분 단축 실습** — 새 폴더에서 Claude Code로 직접 만들며 진행. 시작점은 [labs/quick/README.md](labs/quick/README.md), 진행 현황은 [labs/quick/00-진행현황.md](labs/quick/00-진행현황.md) |
| `docs/` | 구현 경위·검토 보고서·참고자료 |

## 데이터 흐름

```
xlsx/PDF (modules/io.load_input)
  → 표준 JSON (modules/clean.clean_and_structure)
  → NLP분석결과 (modules/nlp.analyze_document)
  → 계산지표/통계해석결과/시각자료설명 (modules/stats, modules/charts)
  → 헤드라인/본문 (modules/write, LLM 호출)
  → 최종본/검수결과 (modules/review: 문체 통일 + 자동 수치검증 + AI 감수)
  → output/*.txt (modules/io.save_final_document)
  → output/*.pdf, output/*.hwpx (modules/export.save_pdf / save_hwpx)
```

## 테스트

```bash
pytest tests/ -v
```

API 키 없이도 대부분의 로직(정제, NLP, 통계, 그래프, 검증 규칙)을 검증할 수 있습니다. `tests/test_ch10_pipeline.py`는 Claude API 응답을 가짜(mock)로 대체해 전체 배선을 검증합니다 — **실제 문장 품질은 검증하지 않으므로**, API 키를 넣고 `python main.py`를 직접 실행해 결과를 확인해야 합니다.

## 공공데이터포털 Open API로 실제 보도자료 만들기 (2차시 응용)

```bash
python scripts/fetch_public_api_sample.py   # API 연동만 확인하는 최소 데모
python main_price.py                        # 실제 데이터로 통계 보도자료까지 완성
```

`.env`의 `PUBLIC_API_KEY`로 data.go.kr의 실제 공공 API(품목 리스트 조회 + 가격정보 조회)를 호출합니다. 이 API는 총거래액 같은 집계 통계가 아니라 개별 상품의 낱개 판매가격 목록만 주므로, `main_price.py`가 실제로 여러 품목의 당월/전월/전년동월 평균가격을 계산해 `main.py`와 같은 4·6·7·8·9차시 검증 절차(수치 검증, 문체 통일, AI 감수)를 거친 보도자료를 만듭니다. `main.py`(온라인쇼핑 동향 예시)는 별도로 그대로 유지되어 있습니다.

## 세 가지 예시가 서로 다른 지점에서 시작하는 이유

이 프로젝트에는 진입점이 세 개 있습니다. 서로 다른 데이터를 다루기 때문이 아니라, **원자료가 어디까지 가공되어 있는가**가 다릅니다.

| 진입점 | 원자료 상태 | "계산" 단계가 하는 일 |
| --- | --- | --- |
| `main.py` | 이미 계산된 표 (총거래액·증감률·품목별지표가 xlsx에 다 들어있음) | 특이점 판별·해석문장 생성만 담당 |
| `main_price.py` | 진짜 원자료 (공공데이터포털의 개별 상품 가격 목록) | 평균가격·증감률 계산부터 전부 담당 |
| `main_practice.py` | 합성 원자료 (표본 사업체별 매출 신고, 실제 API는 없음) | 품목별 집계·증감률·특이점 계산부터 전부 담당 |

`main.py`가 "이미 계산된 표"에서 시작하는 것 자체는 잘못된 설계가 아닙니다 — 실제 통계청 발표자료도 전월비·전년동월비를 이미 계산해서 함께 공개하는 경우가 흔합니다. 다만 "처음부터 배우는 실습"이라면 계산 자체를 코드가 하는 걸 봐야 의미가 있으므로, `main_practice.py`는 일부러 `main_price.py`처럼 집계 전 원자료에서 시작하도록 설계했습니다(자세한 설계 배경은 [PLAN_raw_data_redesign.md](docs/PLAN_raw_data_redesign.md) 참고).

## 진행 기록 / 다음에 할 일

- 작업을 잠시 멈췄다가 다시 시작할 때는 **[TASKS.md](TASKS.md)부터** 읽으세요 (재개 체크리스트 + 완료/남은 작업 목록).
- 전체 구현 과정, 실행 중 발견한 문제와 해결 방법은 [IMPLEMENTATION_LOG.md](docs/IMPLEMENTATION_LOG.md)에 시간 순으로 기록되어 있습니다.

## 보안 원칙 (CLAUDE.md 참고)

- 수치 계산은 항상 `modules/stats.py`가 전담하며 AI에게 맡기지 않습니다.
- API 키는 `.env`에서만 관리하며 코드에 직접 적지 않습니다.
- AI가 생성한 모든 문장은 `modules/review.py`의 검증 함수로 원본 수치와 교차 검증합니다.
