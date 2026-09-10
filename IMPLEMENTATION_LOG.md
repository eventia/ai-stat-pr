# 구현 진행 기록 (Implementation Log)

이 문서는 Ch01~Ch10 강의안(PT/실습 문서)을 실제로 동작하는 코드로 옮기면서 진행한 모든 작업, 실행 결과, 발견한 문제와 해결 방법을 시간 순서대로 기록한 것입니다.

## 0. 배경

- 1차 검토(문서만 읽고 코드 리뷰): 함수 누락, 정규식 버그, 스키마 불일치 등을 발견해 각 `ChNN-PT내용.md`/`ChNN-실습.md`에 `> **[수정]**` 형태로 반영.
- 2차 검토(웹 검색으로 이중 확인): `kiwipiepy` 패키지명, summa의 한국어 미지원, Claude 모델 ID 현황을 확인 후 문서에 반영.
- **이번 단계(3차)**: 문서에 반영한 코드를 실제 `modules/*.py` 파일로 옮기고, 가상환경에 패키지를 설치해 **직접 실행·테스트**하며 검증. 이 과정에서 문서 검토만으로는 발견할 수 없었던 문제 2건을 추가로 찾아 수정함.

## 1. 환경 구성

```
python -m venv myvenv
myvenv\Scripts\python.exe -m pip install -r requirements.txt
myvenv\Scripts\python.exe -m pip install pytest
```

- Python 3.13.12, pip 25.3 (Windows 11)
- `requirements.txt`의 모든 패키지(anthropic, python-dotenv, pandas, openpyxl, pdfplumber, requests, scikit-learn, kiwipiepy, networkx, matplotlib, pytest)가 정상 설치됨. 설치 실패나 버전 충돌 없음.
- `ANTHROPIC_API_KEY`는 이 환경에 설정되어 있지 않음 → LLM 실제 호출은 이번 단계에서 검증 불가 (아래 4절 참고).

## 2. 폴더 구조

```
보도자료작성-실습1/
├── requirements.txt, .env.example, .gitignore, CLAUDE.md
├── main.py
├── modules/
│   ├── io.py       (7,10차시: load_input, save_final_document)
│   ├── clean.py    (2차시: clean_and_structure, mask_sensitive_info)
│   ├── nlp.py      (3차시: 키워드/문장 추출)
│   ├── stats.py    (5차시: 계산/특이점/해석)
│   ├── charts.py   (6차시: 그래프/설명문)
│   ├── write.py    (4,7,8차시: LLM 생성 - MODEL_NAME, client 보유)
│   └── review.py   (4,9차시: 검증/문체/감수)
├── tests/
│   ├── conftest.py, fixtures/sample_standard_data.json
│   └── test_ch02_clean.py ... test_ch10_pipeline.py (30개 테스트)
├── scripts/make_sample_excel.py
├── data/raw/온라인쇼핑동향_2026_01.xlsx (샘플 생성)
├── images/, output/, logs/ (실행 산출물 저장 위치)
└── myvenv/ (가상환경, git 추적 제외)
```

## 3. 테스트 결과

`pytest tests/ -v` 최종 결과: **30 passed, 0 failed**

| 테스트 파일 | 검증 대상 | 결과 |
| --- | --- | --- |
| test_ch02_clean.py | 정제·표준화, 개인정보 마스킹 | 2/2 통과 |
| test_ch03_nlp.py | 명사/키워드/문장 추출, analyze_document | 6/6 통과 (아래 4-1 수정 후) |
| test_ch05_stats.py | 증감률 계산, 특이점 탐지, 해석문 생성 | 6/6 통과 |
| test_ch06_charts.py | 그래프 설명문(bar/pie/line), 이미지 파일 생성 | 5/5 통과 |
| test_ch09_review.py | 숫자 검증, 표기 오류 검수 | 10/10 통과 |
| test_ch10_pipeline.py | LLM 응답을 목업(mock)으로 대체한 전체 파이프라인 통합 | 1/1 통과 |

## 4. 실제 실행으로 새로 발견하고 고친 문제 (문서 검토만으로는 못 찾은 것)

### 4-1. kiwipiepy 복합명사 분리 문제 (Ch03)

**증상**: `test_extract_nouns_returns_only_nouns`, `test_extract_keywords_tfidf_finds_domain_keywords` 최초 실행 시 실패.

**원인**: 실제로 `kiwipiepy 0.23.2`를 돌려보니, 문서에서 예시로 든 `['온라인쇼핑', '거래액', '전월', '대비']`와 다르게 "온라인쇼핑"이 "온라인"+"쇼핑"으로, "거래액은"의 "거래액"이 문맥(조사 유무)에 따라 "거래"+"액"으로 분리되는 경우가 확인됨. 기본 사전만으로는 도메인 특화 복합명사를 하나로 인식하지 못함.

**해결**: `modules/nlp.py`에서 `Kiwi()` 초기화 직후 `kiwi.add_user_word("온라인쇼핑", "NNP", 0.0)` 등으로 도메인 복합명사(온라인쇼핑, 모바일쇼핑, 거래액, 역대급)를 사용자 사전에 등록. 재실행 결과 정상 통과.

**문서 반영**: `Ch03-PT내용.md` 페이지 3 코드와 설명에 사용자 사전 등록 코드 및 발견 경위를 추가.

### 4-2. 단일 문서 TF-IDF의 실제 동작 (Ch03)

**증상**: `extract_keywords_tfidf`/`extract_main_sentences`/`filter_sentences_by_keywords`를 실제 실행해보니, 문서에 적힌 기대 결과(`['온라인쇼핑', '거래액', '역대', '최대', '모바일쇼핑']`, 주요문장 2개)와 실제 결과(`['온라인쇼핑', '전월', '기록', '기준', '역대']`, 주요문장 1개)가 다름.

**원인 분석**: 문장을 문서 단위로 취급하는 TF-IDF/TextRank는 서로 다른 기준(단어 희소성 vs 문장 간 유사도)으로 동작하는 독립적인 알고리즘이라, 매우 짧은 예시 텍스트(4문장)에서는 두 결과가 항상 일치하지는 않음. 이는 코드 버그가 아니라 **배경 코퍼스 없이 단일 문서에 TF-IDF를 적용할 때의 근본적인 한계**이자 두 알고리즘의 독립성에서 비롯된 자연스러운 결과.

**해결 방향**: 코드를 억지로 특정 출력에 맞추기보다, ① 문서에 실제 실행 결과를 정직하게 반영 ② "역대 최대치"라는 사실은 3차시(NLP 추출, 보조 요약용)가 아니라 5차시 `add_calculated_indicators`(규칙 기반 계산, 결정적)가 `통계해석결과`에 별도로 확정하므로 최종 보도자료의 사실 정확성에는 영향이 없음을 명시.

**문서 반영**: `Ch03-실습.md` 페이지 3~5의 실행 결과를 실측값으로 교체하고, 원인과 영향 범위를 설명하는 `[수정]` 노트 추가.

### 4-3. Windows 로그 파일 한글 인코딩 깨짐 (Ch10)

**증상**: `main.py` 실행 후 생성된 `logs/pipeline.log`를 열어보니 한글이 모두 깨져 있음 (`INFO:root:파이프라인 시작` 이 `INFO:root:\xc6\xc4\xc0\xcc...`로 저장됨).

**원인**: `logging.basicConfig(filename=..., level=...)`가 `encoding`을 지정하지 않으면 윈도우 시스템 기본 코드페이지(cp949)로 로그 파일을 엶. UTF-8 편집기/도구로 열면 깨져 보임.

**해결**: `logging.basicConfig(..., encoding="utf-8")`로 인코딩을 명시. `main.py`와 `Ch10-PT내용.md` 양쪽에 반영하고 재실행으로 정상 출력 확인.

### 4-4. (재확인) anthropic 클라이언트는 키 없이도 import/생성은 가능

**검증**: `anthropic.Anthropic()`은 API 키가 없어도 객체 생성은 성공하며, 실제로 `.messages.create()`를 호출하는 시점에만 `Could not resolve authentication method` 오류가 발생함을 실제 실행으로 확인. 따라서 `modules/write.py`, `modules/review.py`를 API 키 없이도 정상적으로 import·단위 테스트할 수 있음 (수정 불필요, 우려가 기우였음을 실행으로 확인).

## 5. 전체 파이프라인 실행 검증

- `python main.py` 실행 결과: 입력(xlsx 읽기) → 정제 → NLP 분석 → 계산지표/특이점 계산까지 **정상 동작**을 확인. `generate_headline_set` 단계에서 `ANTHROPIC_API_KEY` 부재로 인한 인증 오류로 정확히 멈춤 (설계대로 동작 — 이 이전 단계에 코드 결함이 없음을 의미).
- `tests/test_ch10_pipeline.py`에서 `client.messages.create`를 가짜(mock) 응답으로 대체해 **입력→정제→NLP→계산→그래프→헤드라인→본문→문체통일→자동검수→저장**까지 전 구간을 실제로 실행·검증함. 최종 파일이 `output/`에 저장되고 수치 교차 검증이 통과함을 확인.

## 6. 아직 검증하지 못한 것 (실제 API 키 필요)

- `generate_summary`, `generate_headline_set`, `expand_to_paragraph`, `unify_style`, `review_press_release`가 **실제 Claude 응답의 문장 품질**(자연스러움, 6하원칙 충족, 감수 지적의 타당성 등)은 검증하지 못했습니다. 목업 테스트는 "배선이 맞는가"만 확인하며, "문장이 실제로 잘 나오는가"는 `.env`에 유효한 `ANTHROPIC_API_KEY`를 넣고 `python main.py`를 재실행해 사람이 직접 확인해야 합니다.
- 공공데이터포털(data.go.kr) Open API 연동(2차시)은 실제 서비스 키가 없어 실행하지 않았습니다.
- hwpx/docx 등 공식 서식 변환(10차시 확장 언급 부분)은 이번 실습 범위에 포함하지 않았습니다(문서에도 향후 확장 과제로 명시되어 있음).

## 7. 결론 (3차 세션 시점)

- 문서 리뷰 단계에서 고친 스키마/함수 정의는 실제 실행 결과와 **모순 없이 일치**함을 확인했습니다.
- 순수 코드 리뷰로는 발견할 수 없었던 3가지 문제(4-1 복합명사 분리, 4-2 TF-IDF 알고리즘 특성, 4-3 로그 인코딩)를 실제 실행으로 찾아 수정하고, 그 근거를 각 차시 문서에도 반영했습니다.
- API 키만 발급받아 `.env`에 넣으면 `python main.py`로 Ch01~Ch10 전 과정이 실제로 동작하는 상태입니다. — **실제로 해보니 이 예상은 절반만 맞았습니다.** 아래 8절 참고.

---

## 8. 4차 세션: 실제 API 키로 품질 검증 (2026-09-06, 01:52~02:10)

TASKS.md의 "🔴 최우선" 항목(실제 API 키로 `python main.py`를 돌려 문장 품질을 확인하는 것)을 실행에 옮긴 세션입니다. 그런데 **키를 넣고 처음 돌리자마자 인증 오류로 즉시 실패**했고, 원인을 고치자 이번엔 **본문이 통째로 비어 있는** 등, 이전 세션(3차)의 "API 키 이전 단계까지는 정상"이라는 결론이 무색하게 실제 LLM 호출 구간에서만 발현되는 문제가 연쇄적으로 발견되었습니다. 문서 리뷰·목업 테스트로는 절대 못 잡는 유형의 버그들이었고, 정확히 이걸 확인하려고 이 세션을 시작한 것이므로 예상된 결과이기도 합니다.

### 8-1. 타임라인 (생성 / 수정 / 실행 / 발견)

| 시각(대략) | 구분 | 대상 | 내용 |
| --- | --- | --- | --- |
| 01:52 | 확인 | `.env` | 사용자가 `.env.example`을 삭제하고 `.env`를 직접 생성, `ANTHROPIC_API_KEY` 입력 확인. `PUBLIC_API_KEY`는 아직 플레이스홀더(`xxxx...`)임을 확인 |
| 01:53 | 실행 | `pytest tests/` | 재개 전 기준선 확인 — 30 passed |
| 01:53 | 실행 | `python main.py` | 최초 실제 API 실행 → **즉시 실패**: `Could not resolve authentication method` |
| 01:54 | 발견(버그①) | `main.py` | `modules.write`를 임포트하는 시점에 `client = anthropic.Anthropic()`이 실행되는데, `load_dotenv()` 호출이 그 **뒤**에 있어 클라이언트가 키 없이 생성됨 |
| 01:54 | 수정 | `main.py` | `load_dotenv()`를 다른 모듈 임포트보다 먼저 호출하도록 위치 이동 |
| 01:55 | 실행 | `python main.py` | 재실행 성공(API 호출 3회) — 그러나 **수치교차검증 실패**, 본문이 리드문 한 줄뿐 |
| 01:56 | 발견(버그②) | `modules/write.py generate_body_paragraphs` | 샘플 xlsx에 `품목별지표`가 없어 `build_visual_descriptions`가 호출되지 않았고, 그 결과 `시각자료설명`이 아예 없어 본문 단락이 0개로 생성됨 |
| 01:57 | 발견(버그③) | `modules/io.py load_input` | xlsx 셀은 스칼라만 담을 수 있는데, `품목별지표`(리스트) 컬럼이 있어도 JSON 파싱 없이 그대로 대입하도록 되어 있어 실제로는 못 씀 |
| 01:57 | 발견(버그④) | `modules/clean.py clean_and_structure` | `역대최대여부`/`최근3개월증감률`을 표준 데이터로 전달하지 않아, xlsx로 실제 실행하면 "역대 최대" 같은 사실이 특이점 목록에 영영 반영 안 됨 |
| 01:58 | 수정 | `modules/io.py` | `품목별지표`/`최근3개월증감률` JSON 문자열 파싱, `역대최대여부`/`최근3개월증감률` 컬럼 인식 추가 |
| 01:58 | 수정 | `modules/clean.py` | `역대최대여부`/`최근3개월증감률` 표준 데이터 전달 추가 + **`mask_sensitive_info`를 파이프라인에 연결**(그동안 정의만 되고 호출되지 않던 함수) |
| 01:59 | 생성 | `scripts/make_sample_excel_full.py` | 품목별지표·역대최대여부·최근3개월증감률까지 포함한 "전체 경로" 샘플 xlsx 생성 스크립트 |
| 01:59 | 생성 | `data/raw/온라인쇼핑동향_2026_01_상세.xlsx` | 위 스크립트로 생성한 샘플 데이터 (git 추적 제외) |
| 02:00 | 실행 | 상세 xlsx로 전체 파이프라인 | 표기오류검사 1건, **수치교차검증 실패**(`1,250` 불일치), AI감수가 "원본에 없는 수치"라며 다수 오탐 |
| 02:01 | 발견(버그⑤) | `modules/write.py build_headline_prompt` | 프롬프트에 `총거래액 201250`처럼 **단위 없이** 숫자만 전달 → LLM이 임의로 "20조 1,250억원"으로 환산 표기하며 원본 문자열(`201250`)과 불일치 발생 |
| 02:01 | 발견(버그⑥) | `modules/review.py review_press_release` | `data.get('계산지표', data.get('품목별지표', {}))` 코드가 `계산지표`가 항상 있어 **품목별지표를 절대 감수자에게 전달하지 못하는** 로직 오류 → AI가 실제로 존재하는 품목별 수치를 "근거 없음"으로 오판 |
| 02:02 | 수정 | `modules/write.py` | `build_headline_prompt`에 지표별 단위(억 원/%)를 명시하고 "조 단위로 환산하지 말라"는 지시 추가 |
| 02:02 | 수정 | `modules/review.py` | `unify_style` 프롬프트에 원문 표기 유지·수정 설명 금지 지시 추가, `review_press_release`의 근거자료를 계산지표+통계해석결과+품목별지표 등으로 정정 |
| 02:03 | 실행 | 상세 xlsx로 재실행 | 표기오류검사 0건, **수치교차검증 통과**. 그러나 AI감수가 "해석문장의 '전년동월대비 8.7% 증가'가 실제로는 전월대비 수치"라는 **진짜 버그**를 지적 |
| 02:04 | 발견(버그⑦) | `modules/stats.py add_calculated_indicators` | "큰 폭 증가" 특이점이 전월 대비/전년동월 대비 어느 쪽이든 뭉뚱그려 감지되는데, 해석문장 생성 시에는 항상 `전년동월대비증감률` 값을 쓰면서 템플릿 문구는 고정으로 "전월 대비"라고 적어, 두 조건이 동시에 안 맞으면 문구와 수치가 어긋남 |
| 02:04 | 수정 | `modules/stats.py` | "전월 대비 큰 폭 증가"/"전년동월 대비 큰 폭 증가" 템플릿을 분리하고, 감지된 조건에 맞는 값을 각각 사용하도록 수정 |
| 02:05 | 생성 | `scripts/make_sample_pdf.py` | PDF 입력 경로(한 번도 실행해 본 적 없던 `load_input`의 `.pdf` 분기)를 검증하기 위해 matplotlib으로 샘플 PDF 생성 |
| 02:05 | 생성 | `data/raw/온라인쇼핑동향_2026_01.pdf` | 위 스크립트로 생성한 샘플 PDF (git 추적 제외) |
| 02:06 | 실행/확인 | `load_input(...).pdf 분기` | pdfplumber로 한글 원문이 깨짐 없이 정상 추출됨을 확인 — **버그 없음, 최초로 실행 검증됨** |
| 02:06 | 생성 | `tests/test_ch07_io.py` | `modules/io.py` 단위 테스트 5건 신규 작성 (xlsx 기본/JSON 컬럼 파싱, PDF 목업, 확장자 오류, 저장) — 그동안 커버리지가 없던 부분 |
| 02:07 | 생성 | `tests/test_ch04_write.py` | 프롬프트 조립 함수(`build_summary_prompt`, `select_core_indicators`, `build_headline_prompt`)와 `parse_json_response` 단위 테스트 7건 신규 작성 |
| 02:08 | 실행 | `pytest tests/` | 42 passed — **그런데 직후 재실행에서 1건 실패** (`test_ch10_pipeline.py`, `_tkinter.TclError`) |
| 02:08 | 발견(환경 이슈) | 이 컴퓨터의 matplotlib | 기본 백엔드가 `TkAgg`로 잡히는데 로컬 Tcl/Tk 설치가 손상되어 있어, matplotlib이 파일 저장만 하는데도 간헐적으로 GUI 백엔드 초기화를 시도하다 실패 (코드 버그 아님, 환경 문제) |
| 02:09 | 수정 | `modules/charts.py`, `scripts/make_sample_pdf.py` | `matplotlib.use("Agg")`로 비대화형 백엔드 강제 지정 → 이후 2회 연속 재실행에서 재현 안 됨 |
| 02:09 | 실행 | 상세 xlsx로 최종 재실행 | `parse_json_response`에서 **`json.decoder.JSONDecodeError: Extra data`** 발생 |
| 02:09 | 발견(버그⑧, 근본 원인) | `modules/write.py parse_json_response` | 정규식 `\{.*\}\|\[.*\]`이 배열(`[{...},{...}]`) 응답에서도 **객체 쪽 대안을 먼저 시도**해, 배열을 감싸는 대괄호 대신 안쪽 객체의 중괄호만 잘라내 `{...}, {...}`라는 깨진 JSON을 만들어냄 (`review_press_release`처럼 "객체들의 배열"을 기대하는 곳에서만 발현) |
| 02:09 | 수정 | `modules/write.py` | 정규식 대신, 문자열에서 먼저 등장하는 여는 괄호(`{` 또는 `[`)를 찾아 그와 짝이 맞는 종류의 마지막 닫는 괄호까지 잘라내는 방식으로 재작성. 더 이상 쓰이지 않는 `import re` 삭제 |
| 02:09 | 생성 | `tests/test_ch04_write.py`(추가) | 위 버그를 그대로 재현하는 회귀 테스트 1건 추가 |
| 02:10 | 실행 | `pytest tests/` | **43 passed** |
| 02:10 | 실행 | 상세 xlsx로 최종 재실행 | 표기오류검사 0건, 수치교차검증 통과(불일치 없음), AI감수 5건 — 모두 "품목 5개 중 중간 순위·증감률이 본문에서 빠졌다"류의 **타당한 내용 지적** (아래 8-3 참고) |
| 02:10 | 수정 | `.gitignore` | `data/raw/*.pdf` 패턴 추가 (생성된 샘플 PDF 제외) |
| 02:10 | 수정 | `README.md` | 삭제된 `.env.example`을 복사하라는 안내를 실제 상태(수동으로 `.env` 작성)에 맞게 수정, 새 샘플 생성 스크립트 3종을 표에 추가 |

### 8-2. 파일 변경 요약

**신규 생성**
- `scripts/make_sample_excel_full.py`, `data/raw/온라인쇼핑동향_2026_01_상세.xlsx`
- `scripts/make_sample_pdf.py`, `data/raw/온라인쇼핑동향_2026_01.pdf`
- `tests/test_ch07_io.py` (5 tests), `tests/test_ch04_write.py` (8 tests)
- `output/2026-01 온라인쇼핑 동향.txt`, `images/2026-01 온라인쇼핑 동향_품목별.png`, `logs/pipeline.log` (모두 실행 산출물, git 추적 제외)

**수정**
- `main.py` — `load_dotenv()` 호출 순서를 다른 모듈 임포트보다 앞으로 이동 (버그①)
- `modules/io.py` — 품목별지표/최근3개월증감률 JSON 문자열 파싱, 역대최대여부 컬럼 인식 추가 (버그③)
- `modules/clean.py` — 역대최대여부/최근3개월증감률 전달 추가, `mask_sensitive_info` 호출 연결 (버그④ + TASKS.md 기존 지적사항 해결)
- `modules/write.py` — `build_headline_prompt`에 단위 명시 및 환산 금지 지시 추가(버그⑤), `parse_json_response` 재작성(버그⑧), 미사용 `import re` 제거
- `modules/review.py` — `unify_style` 프롬프트 보강, `review_press_release`의 근거자료 구성 로직 수정(버그⑥)
- `modules/stats.py` — 전월 대비/전년동월 대비 "큰 폭 증가" 해석문장 분리(버그⑦)
- `modules/charts.py` — `matplotlib.use("Agg")` 추가 (환경 이슈 대응)
- `.gitignore`, `README.md` — 위 8-1 표 참고

**삭제**: 없음 (기존 파일을 삭제한 적 없음)

### 8-3. 마지막 실행 결과와, 코드를 고치지 않고 "발견만" 해 둔 것

최종 재실행 결과(수치교차검증 통과, 표기오류 0건) 이후 AI 감수가 남긴 5건의 지적은 전부 다음 한 가지 사실로 요약됩니다: `modules/charts.py`의 `generate_chart_description("bar", ...)`는 품목 5개 중 **1위·2위·꼴찌 3개만** 언급하고(중간 순위인 3·4위 누락), 품목별 `전월대비증감률` 자체를 어떤 차트 설명에도 담지 않습니다. 이 때문에 본문이 항상 "의류 1위, 가전 2위, 기타가 가장 낮음"까지만 말하고 식품·생활용품과 품목별 증감률은 아예 언급되지 않습니다.

이건 코드 버그가 아니라 6차시 예제 함수의 **의도된 단순화**(그래프 설명문을 짧게 유지하려는 설계)이지만, 실제 API로 돌려보니 그 단순화가 AI 감수 단계에서 "정보 누락"으로 반복 지적될 만큼 눈에 띄는 한계라는 게 이번에 처음 확인되었습니다. 코드를 임의로 고치기보다, 다음 재개 시 사람이 "본문에 몇 개 품목까지 담을지" 판단해서 `generate_chart_description`/`generate_table_description`을 확장할지 결정하는 게 맞다고 보아 **의도적으로 수정하지 않고 TASKS.md에 논의 항목으로만 남겼습니다.**

그 외에 AI 감수가 "전년동월대비 8.7%는 '큰 폭'이라 보기 애매하다"는 취지로 스스로 헷갈리는 코멘트를 한 번 남긴 적이 있는데, 확인해보니 실제 해석문장은 정확했고 **AI 감수 쪽의 착오**였습니다. "3단계 안전장치 중 AI 감수도 완벽하지 않으므로 사람의 최종 확인이 꼭 필요하다"는 Ch09의 원래 취지를 실제 사례로 재확인한 셈입니다.

### 8-4. 여전히 못 한 것 (다음 재개 시 최우선)

- **공공데이터포털 Open API 연동은 여전히 미실행**입니다. `.env`의 `PUBLIC_API_KEY`가 아직 플레이스홀더(`xxxx...`)라 실제 서비스 키가 있어야 진행할 수 있습니다.
- 위 8-3의 품목별 설명 커버리지 확장 여부는 사람의 판단이 필요해 보류했습니다.

## 9. 결론 (4차 세션 시점, 최신)

- 3차 세션에서 "API 키만 있으면 끝까지 동작한다"고 결론 내렸던 것과 달리, **실제 키로 돌려보니 LLM 호출 구간에서만 발현되는 버그 8건**(인증 초기화 순서, 품목별지표 파싱, 표준화 단계의 필드 누락, 숫자 단위 불일치 2건, 감수 근거자료 누락, 해석문장 mom/yoy 혼동, JSON 파싱 정규식 결함)이 추가로 발견되어 모두 수정했습니다. 이는 "문서 리뷰 → 목업 테스트 → 실제 실행"이라는 3단계 검증이 왜 전부 필요한지를 그대로 보여주는 사례입니다.
- 품목별지표를 포함한 전체 경로, PDF 입력 경로, `mask_sensitive_info` 연결까지 이번 세션에서 전부 실제로 실행·확인했습니다.
- 테스트는 30개 → **43개**로 늘었고 전부 통과합니다.
- 남은 것은 공공데이터포털 API 실제 연동(서비스 키 필요)과, 품목별 본문 설명 범위를 넓힐지에 대한 판단뿐이었습니다 — 전자는 10절에서 이어서 진행했습니다.

---

## 10. 5차 세션: 공공데이터포털 API 실제 연동 (2026-09-07)

사용자가 data.go.kr에서 `PUBLIC_API_KEY`를 실제로 발급받아 `.env`에 넣었습니다. 그런데 활용신청해 승인받은 상세기능이 Ch02 문서의 가상 예시(`tn_pubr_public_online_shopping_api`, "온라인쇼핑 동향" JSON API)와는 **전혀 다른 API**였습니다 — 실제로는 아래 표처럼 "품목 리스트 조회"와 "가격정보 조회" 두 기능만 허용된 키였습니다.

| No. | 상세기능 | 설명 |
| --- | --- | --- |
| 1 | 품목 리스트 조회 `/getPriceItemList` | 온라인 수집 가격 정보에서 제공하는 전체 품목의 코드와 명칭 정보를 조회 |
| 2 | 가격정보 조회 `/getPriceInfo` | 품목 코드와 조회 일자를 기준으로 해당 가격정보를 조회 |

### 10-1. 타임라인

| 시각(대략) | 구분 | 대상 | 내용 |
| --- | --- | --- | --- |
| 11:05 | 확인 | 사용자 제공 정보 | 활용신청 상세기능이 Ch02 예시와 다름을 확인. End Point를 사용자에게 요청 → `https://apis.data.go.kr/1240000/bpp_openapi` 확보 |
| 11:07 | 실행 | `getPriceItemList` 첫 호출 | `resultCode: 30, SERVICE_KEY_IS_NOT_REGISTERED_ERROR` — 실패 |
| 11:07 | 발견(버그⑨) | `.env`의 `PUBLIC_API_KEY` | 요청 URL에 `%252B`(= `%2B`가 다시 인코딩된 것)가 찍힘 — `.env`에 이미 URL-인코딩된 "Encoding" 키가 들어 있어 `requests`가 이를 한 번 더 인코딩(이중 인코딩)한 것이 원인. 이전 세션에서 TASKS.md에 "주의"로만 남겨뒀던 바로 그 문제가 실제로 재현됨 |
| 11:08 | 수정(임시 검증) | - | `urllib.parse.unquote()`로 디코딩 후 재호출 → `resultCode` 없이 정상 XML 응답 확인 (`getPriceItemList` 성공: 쌀/현미/찹쌀/보리쌀/콩 등 402개 품목) |
| 11:09 | 발견 | 응답 형식 | 응답이 **JSON이 아니라 XML**임을 확인 (`type`/`_type`/`dataType`/`resultType` 등 파라미터를 시도해도 JSON으로 전환되지 않음 — 이 API는 XML 고정) |
| 11:09~11:10 | 실행/실패 | `getPriceInfo` 호출 | `itemCode`만으로는 계속 `PARAMETER FAIL. CHECK REQUEST PARAMETER.` — 정확한 요청변수 이름을 몰라 여러 조합을 시도했으나 실패 |
| 11:10 | 조사 | WebSearch | 이 API가 "국가데이터처(구 통계청)_온라인 수집 가격 정보"(data.go.kr 데이터셋 15080757)이며, 원 출처는 한국소비자원 참가격 포털(price.go.kr)임을 확인 |
| 11:11 | 확인(사용자 승인) | data.go.kr 활용가이드 문서 | `getPriceInfo`의 정확한 요청변수 명세가 다운로드 문서에만 있어, 사용자에게 다운로드 허락을 구하고 승인받음 |
| 11:11 | 다운로드 | `통계청_온라인수집가격정보_OPEN-API활용가이드_v2.2.docx` | data.go.kr 공식 페이지에서 다운로드 (scratchpad에 저장, 프로젝트에는 포함하지 않음) |
| 11:12 | 확인 | 위 문서 | 정확한 스펙 확보: `getPriceInfo` 필수 파라미터는 `itemCode`, `startDate`/`endDate`(YYYYMMDD, 최대 30일, D-2까지), 응답 필드는 `pi`(상품ID)/`pn`(상품명)/`sp`(판매가격)/`dp`(할인가격)/`bp`(혜택가격)/`sd`(가격일자) |
| 11:13 | 실행 | `getPriceInfo` 재시도 | 실제 품목코드(`A01101`=쌀)와 유효 기간(`20260801`~`20260831`)으로 호출 → **정상 응답 확인**. 실제 온라인 판매 상품(태국쌀, 강화섬쌀 등)의 가격 목록이 반환됨 (해당 품목 전체 15,432건 중 5건 표시) |
| 11:14 | 생성 | `scripts/fetch_public_api_sample.py` | `get_price_item_list`/`get_price_info` 함수로 정리. `urllib.parse.unquote()` 방어 코드 포함, XML은 표준 라이브러리 `xml.etree.ElementTree`로 파싱(새 의존성 추가 없음) |
| 11:15 | 발견(버그⑩) | 스크립트 stdout | `python scripts/fetch_public_api_sample.py`를 파일로 리다이렉션하면 한글이 cp949로 깨짐 (지난 세션의 로그 인코딩 문제와 동일한 종류) |
| 11:15 | 수정 | `scripts/fetch_public_api_sample.py` | 스크립트 상단에 `sys.stdout.reconfigure(encoding="utf-8")` 추가 → 재실행 후 정상 출력 확인 |
| 11:16 | 생성 | `tests/test_ch02_public_api.py` | 네트워크 호출을 목업으로 대체해 XML 파싱, 오류 코드 처리, 이중 인코딩 방어 로직을 검증하는 테스트 4건 작성 |
| 11:16 | 실행 | `pytest tests/` | **47 passed** (43 → 47) |
| 11:16 | 수정 | `Ch02-PT내용.md` | 실제 API와 예시 코드가 다른 3가지 지점(XML 응답, 이중 인코딩, 파라미터 형식)을 `[수정]` 노트로 반영, `scripts/fetch_public_api_sample.py` 링크 추가 |

### 10-2. 파일 변경 요약

**신규 생성**
- `scripts/fetch_public_api_sample.py` — 실제 서비스 키로 검증된 공공 API 연동 코드
- `tests/test_ch02_public_api.py` (4 tests)

**수정**
- `Ch02-PT내용.md` — 페이지 19에 `[수정]` 노트 추가

**삭제**: 없음

### 10-3. 중요 발견 — 이 API는 main.py 파이프라인과 데이터 형태가 다릅니다

`getPriceInfo`는 통계 집계치(총거래액, 증감률 등)를 주지 않고, **개별 상품의 낱개 판매가격 목록**을 줍니다(품목 하나에 하루 수천~수만 건). 반면 `main.py`/`modules/stats.py`는 이미 계산된 월별 집계 지표(총거래액/전월대비증감률/전년동월대비증감률)를 입력으로 가정합니다. 즉 이 API로 실제 보도자료를 쓰려면:

1. 특정 품목·기간의 가격 목록을 받아와
2. 대표값(예: 평균가)을 직접 계산하고
3. 그 대표값의 전월/전년동월 대비 증감률까지 별도로 계산하는

새로운 집계 단계가 필요합니다. 이는 5차시 `stats.py`가 하는 일을 새로 하나 더 만드는 수준의 작업이라, 이번 세션에서는 "API 호출 자체가 정상 동작하는가"만 검증하고, 파이프라인 연결 여부는 TASKS.md에 논의 항목으로 남겼습니다.

### 10-4. 결론 (5차 세션 시점, 최신)

- **"공공데이터포털 API 연동"이라는 같은 이름의 작업도, 실제로 어떤 API가 승인되었는지에 따라 완전히 다른 작업이 될 수 있다**는 것이 이번 세션의 핵심 교훈입니다. Ch02 문서가 가정한 가상 API와 실제 승인된 API는 이름, 요청변수, 응답 형식(JSON vs XML), 심지어 데이터의 성격(집계 통계 vs 개별 상품 가격)까지 전부 달랐습니다.
- 그럼에도 이전 세션에서 "이중 인코딩 문제를 주의하라"고 미리 남겨둔 메모 덕분에, 실제로 그 문제가 터졌을 때 바로 원인을 알아볼 수 있었습니다.
- 테스트는 43개 → **47개**로 늘었고 전부 통과합니다.
- 남은 것: 이 가격정보 API를 실제 보도자료 파이프라인에 연결할지(집계 로직 신규 개발 필요), 품목별 본문 설명 범위를 넓힐지 — 둘 다 사람의 판단이 필요해 TASKS.md에 논의 항목으로 남겨두었습니다.

---

## 11. 6차 세션: 가격정보 API로 실제 통계 보도자료 생성 (2026-09-07, 11:16~11:43)

10절 마지막에 논의 항목으로만 남겨뒀던 "이 가격정보 API를 실제 파이프라인에 연결"하는 작업을 이번 세션에서 실제로 진행했습니다. 사용자 요청: "전체 진행을 해보고 통계 관련 보고서가 제대로 나오는지 확인 + API가 변경되었으니 그 API를 쓰는 보도자료를 작성하도록 수정."

### 11-1. 설계 방향

`main.py`(온라인쇼핑 동향, xlsx 기반)는 이미 검증되어 있고 그 자체로 완결된 예시이므로 **건드리지 않고**, 별도의 진입점 `main_price.py`를 새로 만들었습니다. 재사용 가능한 것과 새로 만들어야 하는 것을 구분한 기준:

| 재사용(그대로 사용 가능) | 새로 작성 |
| --- | --- |
| `modules/stats.detect_special_points`, `generate_interpretation` (지표명을 인자로 받는 진짜 범용 함수) | `modules/price_stats.py` — 평균가격 계산, "총거래액"이 아니라 "평균 판매가격"에 맞는 해석문 조립 |
| `modules/write.expand_to_paragraph`, `generate_body_paragraphs` (소주제/설명문 문자열만 다뤄 지표명과 무관) | `modules/price_report.py` — 헤드라인 프롬프트(단위 "억 원"→"원"), 품목별 가격 비교 그래프 설명 |
| `modules/review.py` 전체 (검증·문체통일·AI감수 모두 필드명에 의존하지 않는 범용 코드였음이 이번에 재확인됨) | `main_price.py` — 실제 API 호출→집계→표준데이터 조립 오케스트레이션 |
| `modules/clean.clean_and_structure`, `modules/nlp.analyze_document`, `modules/io.save_final_document` | |

품목은 기존 예시가 다루던 생필품 곡물 5종(쌀·현미·찹쌀·보리쌀·콩)의 실제 데이터를 그대로 사용해 기존 강의 흐름과의 연속성을 유지했습니다.

### 11-2. 타임라인

| 시각 | 구분 | 대상 | 내용 |
| --- | --- | --- | --- |
| 11:17 | 생성 | `modules/public_api.py` | `scripts/fetch_public_api_sample.py`에 있던 API 호출 로직을 모듈로 승격하고, 표본(최대 1000건) 평균가격을 계산하는 `get_average_price()` 추가. 전수조사가 아닌 표본 평균인 이유(품목당 월 1만 건 이상이라 전수 조회 시 API 호출이 과도해짐)를 주석으로 명시 |
| 11:18 | 수정 | `scripts/fetch_public_api_sample.py` | 위 모듈을 import하도록 축소 (로직 중복 제거) |
| 11:19 | 수정 | `tests/test_ch02_public_api.py` | import 경로를 `modules.public_api`로 변경, `get_average_price` 테스트 2건 추가 |
| 11:19 | 실행 | 데모 스크립트 재실행 | 리팩터링 후에도 실제 API 호출이 정상 동작함을 재확인 |
| 11:21 | 생성 | `modules/price_stats.py` | `add_price_indicators()` — 품목별 평균가격으로 전체 대표 계산지표 산출, `detect_special_points`/`generate_interpretation` 재사용. 하락(감소) 문구는 기존 함수에 없어 직접 추가 |
| 11:24 | 생성 | `modules/price_report.py` | 가격 데이터 전용 헤드라인 프롬프트, 품목별 가격 비교 막대그래프 설명 생성 (원형그래프는 "비중" 개념이 가격에는 안 맞아 의도적으로 제외) |
| 11:27 | 생성 | `main_price.py` | 실제 API로 당월/전월/전년동월 평균가격을 조회해 표준 데이터를 만들고, 기존 4·6·7·8·9차시 모듈에 태워 보도자료를 완성하는 전체 오케스트레이션 |
| 11:29 | 실행 | `pytest tests/` | 49 passed (새 모듈 추가 후 회귀 없음 확인) |
| 11:30 | 실행 | `main_price.py` 1차 실행 (실제 API + 실제 LLM) | **성공적으로 끝까지 실행됨.** 그러나 검수 단계에서 문제 2건 발견 |
| 11:31 | 발견(버그⑪) | 표기오류검사 | 리드문의 "32230원"에 천 단위 콤마 누락 — 프롬프트에 넣은 지표 값에 콤마 포맷을 안 넣어서 모델이 그대로 베낀 것 |
| 11:31 | 발견(버그⑫, 핵심) | `modules/review.py _collect_valid_numbers` | **수치교차검증이 "1.5% 감소", "51.7% 하락"처럼 정상적인 문장을 전부 불일치로 오판.** 원인: 원본 값이 음수(-1.5, -51.7)인데 문장은 부호 없이 "감소/하락"으로 표현하는 것이 자연스러운 한국어 어법인데, 검증기가 문자열을 부호까지 그대로(`"-1.5"`) 비교해 "1.5"를 못 찾음. **기존 온라인쇼핑 예시는 증감률이 항상 양수(1.5%, 8.7% 증가)였기 때문에 이 버그가 지금까지 한 번도 드러나지 않았음** — 실제로 하락이 있는 가격 데이터를 붙여보고 나서야 발견됨 |
| 11:33 | 수정 | `modules/review.py` | `_collect_valid_numbers`가 절댓값도 함께 유효 수치 집합에 등록하도록 수정 |
| 11:34 | 수정 | `modules/write.py`, `modules/price_report.py` | `build_headline_prompt`가 지표 값을 콤마 포함 표기(`f"{v:,}"`)로 프롬프트에 넣도록 수정 (온라인쇼핑 파이프라인도 동일하게 수정 — 향후 큰 수치가 다시 나와도 안전하도록) |
| 11:35 | 수정 | `tests/test_ch04_write.py` | 콤마 포맷 반영해 기대값 `"201250억 원"` → `"201,250억 원"` 갱신 |
| 11:35 | 생성 | `tests/test_ch09_review.py`(추가) | 음수 증감률 검증 버그의 회귀 테스트 1건 추가 |
| 11:36 | 실행 | `pytest tests/` | **50 passed** |
| 11:38 | 실행 | `main_price.py` 2차(최종) 실행 | **표기오류검사 0건, 수치교차검증 통과(불일치 없음)**. AI감수는 "평균 12.1% 증가 이면에 품목별로는 최대 +56.5%~-51.7%까지 큰 등락이 상쇄되어 있다는 설명이 없다"는 등 타당한 내용 지적 5건 — 코드 버그 아님, 사람이 참고할 문체/구성 피드백 |
| 11:39 | 확인 | `output/2026-08 생필품 가격 동향.txt`, `images/..._품목별가격.png` | 실제 산출물 생성 확인, 사용자에게 전달 |

### 11-3. 파일 변경 요약

**신규 생성**
- `modules/public_api.py`, `modules/price_stats.py`, `modules/price_report.py`, `main_price.py`
- `output/2026-08 생필품 가격 동향.txt`, `images/2026-08 생필품 가격 동향_품목별가격.png`, `logs/pipeline_price.log` (실행 산출물, git 추적 제외 — `.gitignore`의 `output/*.txt`/`images/*.png`/`logs/*.log` 패턴에 이미 포함됨)

**수정**
- `scripts/fetch_public_api_sample.py` — `modules/public_api.py`를 사용하도록 축소
- `modules/review.py` — `_collect_valid_numbers`가 음수 값의 절댓값도 유효 수치로 인정하도록 수정 (버그⑫)
- `modules/write.py` — `build_headline_prompt`가 콤마 포함 표기로 지표를 프롬프트에 전달 (버그⑪)
- `tests/test_ch02_public_api.py` — import 경로 변경 + `get_average_price` 테스트 2건 추가
- `tests/test_ch04_write.py`, `tests/test_ch09_review.py` — 콤마 포맷 반영 + 음수 증감률 회귀 테스트 추가

**삭제**: 없음

### 11-4. 결과물 — 실제 데이터로 만든 보도자료 (2026-08 생필품 가격 동향)

> 평균 판매가격은 32,230원을 기록하였다. 전월 대비 12.1% 증가하였으나, 전년 동월 대비 1.5% 감소하였다.
>
> 품목별 당월 평균 판매가격을 비교한 결과, 쌀이 74,675원으로 가장 높았으며, 보리쌀은 11,352원으로 가장 낮았다.
>
> 전월 대비 품목별 등락률을 살펴본 결과, 찹쌀이 56.5%로 가장 높은 상승률을 기록하였으며, 콩은 -51.7%로 가장 큰 하락폭을 나타냈다.

검수결과: 표기오류검사 0건, 수치교차검증 통과(불일치 없음), AI감수 5건(전부 코드 문제가 아니라 "평균 증가율 이면의 품목별 등락 폭 설명 부족" 같은 문체/구성 피드백).

### 11-5. 결론 (6차 세션 시점, 최신)

- **"기존 예시가 항상 양수만 다뤘다"는 사실 자체가 숨은 버그를 가리고 있었습니다.** `_collect_valid_numbers`의 부호 비교 버그는 코드 리뷰로도, 30~47개의 기존 테스트로도 걸러지지 않았는데, 실제 하락이 존재하는 새 데이터를 흘려보내자마자 바로 드러났습니다. "실행해서 확인한다"는 이 프로젝트 전체의 검증 철학이 이번에도 유효했습니다.
- 기존 `main.py`/`modules/write.py`/`modules/stats.py`를 깨지 않고, 재사용 가능한 범용 함수(검증·문체통일·AI감수·본문확장)는 그대로 쓰고 지표명에 얽매인 부분만 새로 작성하는 방식으로 새 데이터 파이프라인을 붙일 수 있음을 확인했습니다.
- 테스트는 47개 → **50개**로 늘었고 전부 통과합니다.
- 남은 것: `main_price.py`가 조회 대상으로 고정한 5개 곡물 품목을 다른 품목으로 바꾸거나 개수를 늘리는 것, `get_average_price`의 표본(최대 1000건) 크기를 늘려 정확도를 높일지 여부 — 둘 다 사용자가 원하면 쉽게 조정 가능한 파라미터라 별도 개발 없이 바로 가능합니다.

## 12. 7차 세션: 검토 보고서(REVIEW_Ch02-10.md) 개선 제안 실행 (2026-09-10)

### 12-1. 배경

6차 세션 종료 후 사용자가 "Ch02~Ch10 PT·실습 자료를 실제로 코드와 대조해 꼼꼼히 검토해달라"고 요청했다. `modules/*.py`, `main.py`, `tests/`를 한 줄 한 줄 대조한 결과를 [REVIEW_Ch02-10.md](REVIEW_Ch02-10.md)로 정리했고, 그중 4가지가 특히 중요했다.

1. **(A-1)** "역대 최대"·"최근 3개월 추세" 판별이 실제로는 자동화되지 않고, 담당자가 과거 자료를 조사해 직접 입력해야 하는 값이었다.
2. **(A-2)** `detect_special_points`가 감지하는 "큰 폭 감소"·"연속 감소세"가 `generate_interpretation`/`add_calculated_indicators`에는 템플릿이 없어 해석문장으로 연결되지 않았다. 하락하는 통계에서는 자동화가 조용히 정보를 누락시키는 실제 결함이었다(6차 세션의 가격정보 파이프라인에서 우회책으로만 처리했었음).
3. **(A-3)** 3~4차시(NLP 키워드/주요문장, LLM 3줄요약)의 결과물이 `main.py`에서 전혀 호출되지 않아 최종 산출물과 단절된 죽은 코드였다.
4. **(B-1)** "다른 통계표에도 동일 파이프라인 재사용 가능"이라는 주장이 실제로는 지표명 하드코딩 때문에 절반만 사실이었다.

사용자가 "문서에 있는 개선 제안을 실행해달라"고 요청해, 이번 세션에서 6가지 제안을 모두 코드로 실행했다.

### 12-2. 수정한 파일과 이유

| 파일 | 수정 내용 |
| --- | --- |
| [modules/stats.py](modules/stats.py) | `generate_interpretation`에 "전월/전년동월 대비 큰 폭 감소", "최근 3개월 연속 증가세/감소세" 템플릿 추가. `add_calculated_indicators`가 6가지 특이점 유형을 모두 해석문장으로 연결하도록 수정(감소는 `abs()`로 부호를 뗀 값 사용, 이중 부정 방지). `derive_history_indicators(history, current_ym, current_value)` 신규 — 과거 월별 이력과 이번 달 값을 비교해 `역대최대여부`/`최근3개월증감률`을 자동 계산 |
| [modules/io.py](modules/io.py) | `load_input`의 xlsx 분기가 "이력" 시트(연월, 총거래액)가 있으면 `derive_history_indicators`를 호출해 자동 계산하고, `월별이력` 필드에도 담아 6차시 꺾은선그래프에 재사용할 수 있게 함. 명시적으로 `역대최대여부`/`최근3개월증감률` 열이 있으면 그 값을 우선(자동 계산 결과를 덮어쓰지 않도록 `setdefault` 사용). `계산지표` 딕셔너리도 `REQUIRED_FIELDS` 기반으로 생성하도록 단순화 |
| [modules/charts.py](modules/charts.py) | `build_visual_descriptions`를 `품목별지표`/`월별이력` 각각 독립적으로 조건 분기하도록 재작성 — `월별이력`이 있으면 실제로 꺾은선 그래프를 그려, 지금까지 코드는 있지만 도달 불가능했던 "line" 분기를 처음으로 실제 파이프라인에 연결 |
| [modules/clean.py](modules/clean.py) | `clean_and_structure`가 `월별이력` 필드도 통과시키도록 한 줄 추가 |
| [modules/write.py](modules/write.py) | `REQUIRED_FIELDS`/`지표_단위`를 `modules/config.py`에서 import하도록 변경(중복 정의 제거). `build_headline_prompt`에 `참고_제목후보` 선택 인자 추가 — 4차시 `generate_summary`의 `제목후보`를 "그대로 채택하지 않아도 되는 참고용 표현 아이디어"로만 프롬프트에 전달(새로운 숫자는 들여오지 않으므로 `verify_numbers` 검증에 영향 없음) |
| [modules/config.py](modules/config.py) | 신규 — `PRIMARY_INDICATOR`, `PRIMARY_UNIT`, `REQUIRED_FIELDS`, `INDICATOR_UNITS`를 한곳에 모음. 다만 이것만으로 "다른 통계표 재사용"이 완전히 해결되는 것은 아니며, `modules/stats.py`/`modules/io.py`의 필드 구조 의존은 여전히 남아 있다는 것을 파일 docstring에 명시 |
| [main.py](main.py) | 그래프 단계 호출 조건을 `"품목별지표" in data`에서 `"품목별지표" in data or "월별이력" in data`로 확장. `add_calculated_indicators` 다음에 `data["요약결과"] = generate_summary(data)` 추가 — 이전까지 어디서도 호출되지 않던 4차시 함수를 실제로 연결 |
| `Ch03/04/05/06/07/10-PT내용.md` | 위 수정 내용을 `[수정, 7차 세션]` 노트로 각 문서에 반영, 코드 예시도 최신 구현과 일치하도록 갱신 |

### 12-3. 왜 완전한 리팩터링 대신 이 수준으로 멈췄는가

`REQUIRED_FIELDS`를 실제로 다른 지표명으로 바꿔 쓸 수 있게 하려면 `modules/stats.py`(계산 로직 필드명), `modules/io.py`(xlsx 컬럼명), `modules/write.py`(프롬프트 문구)까지 모두 함께 일반화해야 한다. 이는 사실상 6차 세션에서 가격정보 파이프라인을 위해 `price_stats.py`/`price_report.py`를 별도로 만든 것과 같은 결론에 도달한다 — "완전히 하나의 코드로 통합"하기보다 "필드 구조가 다르면 그 부분만 새로 작성하고, 검증·문체통일·본문확장처럼 지표명에 의존하지 않는 부분은 재사용한다"는 원칙이 이 프로젝트 전체에서 더 현실적인 것으로 재확인되었다. 그래서 `modules/config.py`는 "하드코딩을 한곳에 모아 반복 수정을 줄이는" 수준으로 범위를 한정했다.

### 12-4. 검증

- `derive_history_indicators`, 감소/연속감소 해석문장, io.py "이력" 시트 자동 계산, charts.py 꺾은선그래프 활성화, `build_headline_prompt` 참고문구 각각에 대해 회귀 테스트를 추가했다.
- `main.py`의 실제 `main()` 함수를 (재구현이 아니라) 직접 호출해 "이력" 시트가 있는 xlsx로 끝까지 실행되는지 검증하는 통합 테스트(`test_main_module_entrypoint_runs_end_to_end_with_history_sheet`)를 신규 추가했다 — 기존 `test_ch10_pipeline.py`의 테스트는 `main.py`의 단계를 테스트 파일 안에서 재구현할 뿐 실제 `main.main()`을 호출하지 않는다는 것을 이번에 발견했기 때문이다.
- 테스트 50개 → **61개**, 전부 통과 확인 (`pytest tests/ -q` → `61 passed`).

### 12-5. 실습용 샘플 데이터 준비 중 실제로 새로 발견·수정한 버그 2건

개선 제안을 실행한 뒤, 사용자가 직접 실습을 진행해볼 수 있도록 새 시나리오("2026년 3월 반려동물용품 온라인 거래 동향")의 샘플 xlsx(`scripts/make_sample_excel_practice.py`)와 단계별 실행 스크립트(`scripts/run_practice_stepbystep.py`)를 만들었다. 이 데이터는 일부러 "전월 대비 큰 폭 감소"와 "3개월 연속 감소세"가 동시에 나타나도록 설계했다 — 방금 고친 A-2 수정이 실제로 동작하는지 확인하기 위해서다. 사용자에게 넘기기 전에 스크립트를 처음부터 끝까지 직접 실행해 검증하는 과정에서, 지금까지 한 번도 실행된 적 없던 코드 경로(꺾은선그래프가 처음으로 실제 파이프라인에 연결됨)가 새로운 버그 2건을 드러냈다.

**버그⑬ (line 차트 설명문에 주어 누락 → LLM 환각)**: `generate_chart_description`의 `line` 분기가 만드는 문장("2024-03부터 2026-03까지 증가세를 보이고 있으며...")에 주어(무엇이 증가했는지)가 없었다. 이 문장을 8차시 `expand_to_paragraph`가 본문으로 확장하는 과정에서, 실제로 LLM이 "디지털 콘텐츠 시장 규모는 지속적인 증가세를 나타내고 있다"처럼 **원본에 전혀 없는 엉뚱한 주제를 지어내는 환각**이 관찰되었다. `verify_numbers`는 숫자(연도, 금액)만 대조하므로 이 환각을 잡아내지 못했다 — 주제 자체가 틀렸다는 것은 수치 검증의 사각지대였다. `generate_chart_description(chart_type, data, label=None)`에 `label` 인자를 추가해 항상 지표명으로 문장을 시작하도록 수정했다(`build_visual_descriptions`는 `modules/config.PRIMARY_INDICATOR`를 label로 전달). 이 "고아 기능이 처음 실전 투입되자마자 드러난 버그"는, 검토 보고서가 지적했던 "6차시 line 기능이 한 번도 end-to-end로 실행된 적이 없다"는 진단이 정확했음을 다시 한번 보여준다.

**버그⑭ (AI 감수 응답 절단 시 파이프라인 전체 크래시)**: 같은 실행에서 `review_press_release`가 `ValueError: substring not found`로 죽었다. 원인은 `max_tokens=800`이 이 응답에는 부족해 JSON 배열이 닫는 대괄호 없이 잘렸고, `parse_json_response`가 문자열 전체에서 닫는 괄호를 찾지 못해 예외를 던졌기 때문이다. `max_tokens`를 1500으로 늘리고 프롬프트에 "지적사항은 최대 5건, 항목당 한 문장"이라는 분량 제약을 추가했으며, 그래도 파싱에 실패하면 예외 대신 안내 항목 하나를 반환하도록 `try/except`를 추가했다 — AI 감수는 9차시 3단계 안전장치 중 하나일 뿐이므로, 이 단계가 실패해도 이미 끝난 표기·수치 검증 결과는 그대로 보여줄 수 있어야 한다.

두 버그 모두 회귀 테스트를 추가했다(`test_generate_chart_description_line_always_names_a_subject`, `test_review_press_release_returns_fallback_on_truncated_response`). 테스트는 61개 → **63개**, 전부 통과. 수정 후 `scripts/run_practice_stepbystep.py`를 다시 처음부터 끝까지 실행해 정상 완료(종료 코드 0)됨을 확인했다.

흥미로운 부작용 하나를 기록해 둔다: 수정 후에도 최종본에는 "최근 3개월 연속 감소세"(리드문)와 "총거래액은 지속적인 증가세를 나타내고 있다"(4문단, 2년치 전체 이력의 처음과 끝만 비교)라는 **서로 다른 기간을 기준으로 한, 언뜻 모순돼 보이는 두 문장**이 함께 실렸다. 이번 실행에서는 AI 감수가 4문단을 "근거 없는 서술"로 정확히 짚어냈다 — 코드 버그가 아니라 "장기 추세"와 "최근 3개월 모멘텀"이라는 서로 다른 지표를 같은 보도자료에 함께 쓸 때 반드시 사람이 맥락을 맞춰봐야 한다는 것을 보여주는 사례이며, 검수 시스템이 의도대로 작동한 좋은 예시로 남겨둔다.

### 12-6. 결론

REVIEW_Ch02-10.md가 지적한 4가지 핵심 문제 중 3가지(A-1, A-2, A-3)를 실제 코드 변경으로 해소했고, 1가지(B-1)는 부분적으로 개선했다(완전한 일반화는 각 통계표의 필드 구조가 다른 한 근본적으로 어렵다는 것을 재확인). 그 개선 사항을 실습용 새 데이터로 실제 검증하는 과정에서 지금까지 한 번도 실행되지 않았던 코드 경로가 발동되어 버그 2건이 추가로 드러났고, 그 자리에서 함께 수정했다 — "실행해서 확인한다"는 이 프로젝트의 검증 철학이 이번에도 유효했다.
