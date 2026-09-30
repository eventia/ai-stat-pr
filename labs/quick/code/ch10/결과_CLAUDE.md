# AI 보도자료 작성 프로젝트 규칙

- 수치 계산(증감률, 비중, 순위 등)은 반드시 `mywork/stats.py`의 파이썬 함수가 처리하며, AI 모델에게 계산을 맡기지 않는다.
- API 비밀키(ANTHROPIC_API_KEY, PUBLIC_API_KEY)는 절대 코드에 직접 적지 않고 `.env` 파일에서 불러온다.
- AI가 생성한 문장은 `mywork/review.py`의 `verify_numbers`/`cross_check_all_numbers`로 원본 수치와 반드시 교차 검증한다.
- 문장은 자연스럽고 명확한 공공 보도자료체(객관적 서술체, "~하였다")로 작성한다.
- 모델 ID는 `mywork/write.py`의 `MODEL_NAME` 상수 한 곳에서만 관리한다.

<!-- quick-practice:common:start -->
## 10분 실습 공통 규칙 (mywork/)
- 결과 코드는 `mywork/` 패키지 안에만 만든다. 프롬프트의 설명만으로 직접 작성하고, 프로젝트 밖의 다른 코드는 열어보거나 복사하지 않는다.
- `mywork` 안의 모듈끼리는 절대 경로로 import 한다 (예: `from mywork.config import REQUIRED_FIELDS`).
- 프롬프트가 지정한 함수 이름·시그니처를 그대로 쓰고, 요청하지 않은 기능·예외처리·주석·문서 파일은 추가하지 않는다.
- 표준 데이터(`mywork/press_data.json`)의 키 이름은 한글 그대로 쓴다 (`문서정보`, `계산지표`, `핵심내용`, `원문`, `품목별지표`, `월별이력`, `NLP분석결과`, `요약결과`, `통계해석결과`, `시각자료설명`, `헤드라인`, `본문`, `최종본`, `검수결과`).
- 기존 파일에 함수를 추가하라는 요청이면 이미 있는 함수는 고치지 않는다.
- 코드를 만든 뒤에는 `python -c "import mywork.<모듈>"`로 import 오류만 확인하고 끝낸다.
<!-- quick-practice:common:end -->

<!-- quick-practice:ch02:start -->
## 2차시 규칙 — 정제·표준화·구조화
- 정제·표준화 단계(`clean`)는 구조만 표준화하고 수치 계산은 하지 않는다. `계산지표`는 값을 바꾸지 않고 그대로 전달한다.
- 원본 자료(`data/raw_*.json`)와 입력 dict는 수정하지 않는다. 정제는 항상 사본에 적용한다(원본 보존).
- 표기 표준: 금액은 "억 원"처럼 숫자와 단위를 띄우고, 날짜는 YYYY-MM-DD로 통일한다.
- 개인정보(주민등록번호·휴대전화)는 정제 단계에서 코드로 마스킹한다(LLM에 보내기 전에).
<!-- quick-practice:ch02:end -->
<!-- quick-practice:ch03:start -->
## 3차시 규칙 — NLP 분석
- 키워드·주요 문장 추출은 생성형 AI 없이 형태소 분석·TF-IDF·TextRank로 한다.
- 주요 문장은 원문 문장을 그대로 골라 원문 순서로 반환한다(새 문장 생성·수정 금지).
- 도메인 복합명사(온라인쇼핑, 모바일쇼핑, 거래액, 역대급)는 Kiwi 사용자 사전에 등록한다.
- 문서가 1건이면 문장 하나하나를 문서로 취급해 TF-IDF를 계산한다.
- NLP 결과는 참고용이며 보도자료의 숫자·사실을 확정하는 데 쓰지 않는다.
<!-- quick-practice:ch03:end -->
<!-- quick-practice:ch04:start -->
## 4차시 규칙 — Claude API 호출과 요약
- Claude API 호출은 `mywork/write.py`의 `call_claude` 한 곳을 거친다. `load_dotenv()`는 `anthropic.Anthropic()`보다 먼저 호출한다.
- 모델은 `MODEL_NAME = "claude-sonnet-5-5"`, `thinking={"type": "between_tools"}`를 쓰고 `temperature`는 넣지 않는다.
- 응답은 `content`에서 `type == "text"`인 블록만 모아 쓴다. `stop_reason`이 "refusal"이면 예외를 낸다.
- 프롬프트에 넣는 숫자는 콤마·단위를 붙인 표기로 넣고, 감소는 abs()로 부호를 떼어 "감소"로 쓴다.
- 결과는 JSON으로 요청하고 `parse_json_response`로 파싱한다. 생성된 문장의 숫자는 `verify_numbers`로 검증한다.
<!-- quick-practice:ch04:end -->
<!-- quick-practice:ch05:start -->
## 5차시 규칙 — 통계 계산과 해석
- 증감률·비중·순위·역대 최대 판단은 모두 `mywork/stats.py`의 파이썬 함수가 계산한다. `계산지표`는 바꾸지 않는다.
- 역대 최대는 같은 달(동월)끼리만 비교한다. 비교 대상이 없으면 None(판단 불가)으로 두고 0이나 True로 채우지 않는다.
- 감소 문장은 abs()로 부호를 뗀 값을 "감소" 템플릿에 넣는다(이중 부정 금지).
- 해석문의 주어는 `문서정보["지표명"]`을 쓴다(제목에서 잘라 쓰지 않는다).
- 계산 결과를 JSON으로 저장할 수 있도록 numpy 숫자는 파이썬 int·float로 바꾼다.
<!-- quick-practice:ch05:end -->
<!-- quick-practice:ch06:start -->
## 6차시 규칙 — 그래프와 설명문
- matplotlib은 `matplotlib.use("Agg")`로 파일 저장만 하고, 한글 폰트는 "Malgun Gothic", 그림은 `images/`에 PNG로 저장한다.
- 그래프에는 제목(기준 시점 포함)·단위·출처를 넣는다.
- 설명문에는 항상 주어(무엇에 대한 설명인지)를 넣는다. 꺾은선 설명문의 주어는 `label`(지표명)로 받는다.
- 시각자료설명 항목은 `소주제`·`그래프유형`·`이미지경로`·`설명문` 4개 키를 가진다. 설명문의 숫자는 계산된 값을 그대로 쓴다.
<!-- quick-practice:ch06:end -->
<!-- quick-practice:ch07:start -->
## 7차시 규칙 — 원자료 입력과 헤드라인
- 입력 모듈 이름은 `data_io.py`로 한다(표준 라이브러리 `io`와 이름 충돌 방지).
- xlsx에서 읽은 숫자는 numpy 타입이므로 파이썬 기본 타입(int·float·str)으로 바꿔 담는다.
- PDF는 원문만 채운다. 제목·리드문의 수치는 xlsx의 계산지표에서 가져온다.
- 헤드라인 프롬프트는 6하원칙 요소 중 주어진 것만 쓰고, 없는 요소(어디서·왜)는 지어내지 않는다. 발표 주체는 `config.ISSUER`.
- 제목·부제·리드문 모두 `verify_numbers`로 검증한다.
<!-- quick-practice:ch07:end -->
<!-- quick-practice:ch08:start -->
## 8차시 규칙 — 본문 단락
- 본문 단락 프롬프트에는 두괄식, 제공된 사실 외 추가 금지, "소재에 없는 합계·차이·비율을 새로 계산하지 말 것"을 넣는다.
- 연결어("", "한편, ", "아울러, ")는 코드가 붙이고, 빈 응답은 건너뛴다. `lower()` 같은 영문 대소문자 처리는 하지 않는다.
- 본문은 [{"소주제", "내용"}] 목록으로 저장하고, 모든 단락을 `verify_numbers`로 검증한다.
<!-- quick-practice:ch08:end -->
<!-- quick-practice:ch09:start -->
## 9차시 규칙 — 문체 통일과 검수
- 문체 통일은 표현만 바꾸고 숫자·콤마·단위와 단락 구분(빈 줄)을 바꾸지 않는다. 설명·머리말 없이 본문만 출력하게 한다.
- 검수는 3단계: `check_formatting_errors`(표기) → `cross_check_all_numbers`(수치) → `review_press_release`(AI 감수).
- 수치 교차 검증은 4차시 `find_unverified_numbers`를 재사용한다(요약과 최종본에 같은 기준 적용).
- AI 감수 응답의 파싱 실패는 예외 대신 안내 항목 1개로 돌려준다. 감수 결과는 참고이며 반영 여부는 사람이 판단한다.
<!-- quick-practice:ch09:end -->
<!-- quick-practice:ch10:start -->
## 10차시 규칙 — 전체 파이프라인
- 순서: 입력 → 정제 → 보안등급 확인 → 개인정보 마스킹 → NLP → 계산 → 그래프 → AI 작성 → 문체 통일 → 3단계 검수 → 저장.
- 보안등급이 "공개"가 아니면 외부 AI API를 부르기 전에 PermissionError로 중단한다.
- 자동 검증(수치 교차 검증·표기 검사)을 통과하면 문서상태 "승인대기", 아니면 "검토필요"로 저장한다. 어느 쪽이든 사람의 최종 승인이 필요하다.
- 로그는 `logs/pipeline.log`에 `encoding="utf-8"`로 남긴다. 실행은 프로젝트 폴더에서 `python -m mywork.main`.
- `mywork/export.py`는 제공 파일이므로 수정하지 않는다. 형식(hwpx·pdf)마다 따로 try로 감싸 한쪽 실패가 다른 쪽을 막지 않게 한다.
<!-- quick-practice:ch10:end -->