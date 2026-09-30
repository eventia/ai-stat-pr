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