# AI 보도자료 작성 프로젝트 규칙

- 수치 계산(증감률, 비중, 순위 등)은 반드시 `modules/stats.py`의 파이썬 함수가 처리하며, AI 모델에게 계산을 맡기지 않는다.
- API 비밀키(ANTHROPIC_API_KEY, PUBLIC_API_KEY)는 절대 코드에 직접 적지 않고 `.env` 파일에서 불러온다.
- AI가 생성한 문장은 `modules/review.py`의 `verify_numbers`/`cross_check_all_numbers`로 원본 수치와 반드시 교차 검증한다.
- 문장은 자연스럽고 명확한 공공 보도자료체(객관적 서술체, "~하였다")로 작성한다.
- 모델 ID는 `modules/write.py`의 `MODEL_NAME` 상수 한 곳에서만 관리한다.
