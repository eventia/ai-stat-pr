# solutions — 10분 실습 정답 코드와 준비 자료

각 차시 문서의 **9절 폴백**과 **2절 단독 시작**에서 쓰는 파일입니다. 수강생 실습 폴더(`C:\dev\quick-practice`)의 `mywork\`에 복사해서 씁니다.

| 폴더 | 내용 |
| --- | --- |
| `ch02/` | `config.py`(데이터 딕셔너리), `clean.py`(정제·표준화·구조화, 마스킹) |
| `ch03/` | `nlp.py`(형태소 분석·TF-IDF·TextRank) |
| `ch04/` | `write.py`(API 호출·요약), `review.py`(수치 교차 검증) |
| `ch05/` | `stats.py`(비중·순위·동월 비교·특이점·해석문) |
| `ch06/` | `charts.py`(그래프·설명문) |
| `ch07/` | `data_io.py`(xlsx·PDF 입력), `write.py`(4차시 + 헤드라인) |
| `ch08/` | `write.py`(4·7차시 + 본문 단락) |
| `ch09/` | `write.py`(4·7·8차시 + 문체 통일), `review.py`(4차시 + 3단계 검수) |
| `ch10/` | `clean.py`(2차시 + 보안 함수), `main.py`(전체 파이프라인), `export.py`(**제공 파일** — PDF·HWPX 저장) |
| `data/` | `raw_202601.json`(2차시 원본), `온라인쇼핑동향_2026_01.xlsx`·`.pdf`(7차시 원자료) |
| `snapshots/` | `press_data_after_chNN.json`·`CLAUDE_after_chNN.md` — 각 차시를 마친 시점의 표준 데이터와 CLAUDE.md |

- `chNN/`의 파일은 **그 차시 시점의 전체 파일**입니다. 예를 들어 `ch08/write.py`에는 4·7·8차시 함수가 모두 들어 있으므로, 8차시 폴백에서 이 파일 하나만 복사하면 됩니다.
- `snapshots/`의 LLM 결과(`요약결과`·`헤드라인`·`본문`)는 **예시 문장**입니다(숫자는 모두 원자료와 일치). 실제 API 호출을 건너뛴 경우 8·9차시 "준비" 코드가 빠진 필드만 이 예시로 채웁니다.
- 모델 ID는 `ch04/write.py`의 `MODEL_NAME = "claude-sonnet-5-5"` 한 곳에 있습니다.
- `snapshots/`와 `data/`는 `labs/quick/_tools/run_checks.py --make-snapshots`로 다시 만들 수 있습니다.
