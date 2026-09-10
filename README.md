# AI를 활용한 통계 보도자료 작성 실습 (Ch01~Ch10)

10개 차시의 강의안(`ChNN-PT내용.md`, `ChNN-실습.md`)을 실제로 실행 가능한 파이썬 프로젝트로 구현한 것입니다.

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

# 5. 단위 테스트 실행 (API 키 불필요, 63개)
pytest tests/ -v

# 6. 전체 파이프라인 실행 (API 키 필요)
python main.py          # 온라인쇼핑 동향 예시 (xlsx 기반, 가상 데이터)
python main_price.py    # 생필품 가격 동향 (공공데이터포털 실제 API 기반)

# 7. 직접 한 단계씩 실습해보기 (API 키 필요) — 새 샘플 데이터로 Ch02~Ch10을 Enter로 넘기며 확인
python scripts/make_sample_excel_practice.py   # 샘플 xlsx 생성 (최초 1회)
python scripts/run_practice_stepbystep.py      # 단계별 실행 + 결과 확인
```

## 폴더 구조

| 경로 | 설명 |
| --- | --- |
| `modules/io.py` | 7·10차시: xlsx/PDF 입력, 최종 문서 저장 |
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
| `main_price.py` | 10차시(응용): 공공데이터포털 실제 API 기반 통계 보도자료 진입점 |
| `tests/` | 각 차시 모듈의 단위 테스트 (LLM 호출 없이 실행 가능) |
| `scripts/make_sample_excel.py` | 실습용 기본 샘플 xlsx 생성 (품목별지표 없음) |
| `scripts/make_sample_excel_full.py` | 품목별지표·역대최대여부 등을 포함한 "전체 경로" 샘플 xlsx 생성 |
| `scripts/make_sample_pdf.py` | PDF 입력 경로 확인용 샘플 PDF 생성 |
| `scripts/fetch_public_api_sample.py` | 2차시: 공공 API 연동 최소 데모 (`modules/public_api.py` 사용) |

## 데이터 흐름

```
xlsx/PDF (modules/io.load_input)
  → 표준 JSON (modules/clean.clean_and_structure)
  → NLP분석결과 (modules/nlp.analyze_document)
  → 계산지표/통계해석결과/시각자료설명 (modules/stats, modules/charts)
  → 헤드라인/본문 (modules/write, LLM 호출)
  → 최종본/검수결과 (modules/review: 문체 통일 + 자동 수치검증 + AI 감수)
  → output/*.txt (modules/io.save_final_document)
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

## 진행 기록 / 다음에 할 일

- 작업을 잠시 멈췄다가 다시 시작할 때는 **[TASKS.md](TASKS.md)부터** 읽으세요 (재개 체크리스트 + 완료/남은 작업 목록).
- 전체 구현 과정, 실행 중 발견한 문제와 해결 방법은 [IMPLEMENTATION_LOG.md](IMPLEMENTATION_LOG.md)에 시간 순으로 기록되어 있습니다.

## 보안 원칙 (CLAUDE.md 참고)

- 수치 계산은 항상 `modules/stats.py`가 전담하며 AI에게 맡기지 않습니다.
- API 키는 `.env`에서만 관리하며 코드에 직접 적지 않습니다.
- AI가 생성한 모든 문장은 `modules/review.py`의 검증 함수로 원본 수치와 교차 검증합니다.
