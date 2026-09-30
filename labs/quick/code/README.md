# 10분 실습 코드 모음 (차시별)

10분 단축 실습 문서(`labs/quick/ChNN-10분실습.md`)에 나오는 **코드만** 차시별로 모아 둔 폴더입니다. 실습 시간에는 해당 차시 폴더를 열어 파일 이름 앞의 절 번호 순서대로 사용하고, 나중에 확인할 때도 문서 없이 코드만 볼 수 있습니다.

| 차시 | 폴더 | 주제 | 상태 |
| --- | --- | --- | --- |
| 2 | [ch02/](ch02/) | 텍스트 정제·표준화·구조화 | 완료 |
| 3 | [ch03/](ch03/) | 주요 NLP 기법 | 완료 |
| 4 | [ch04/](ch04/) | LLM 기반 텍스트 요약 | 준비 중 |
| 5 | [ch05/](ch05/) | 통계 계산과 해석문 | 준비 중 |
| 6 | [ch06/](ch06/) | 표·그래프 설명문 | 준비 중 |
| 7 | [ch07/](ch07/) | 원자료 입력·제목·부제·리드문 | 준비 중 |
| 8 | [ch08/](ch08/) | 본문 단락 확장 | 준비 중 |
| 9 | [ch09/](ch09/) | 문체 통일·검수·AI 감수 | 준비 중 |
| 10 | [ch10/](ch10/) | 보도자료 자동 생성 시스템 | 준비 중 |

**각 차시 폴더의 구성**

```text
chNN/
├─ README.md                  파일 목록·절 번호·사용법
├─ 1-1_….ps1, 2_….py, …       문서의 코드 블록(파일 이름 = 절 번호_제목)
│    .ps1  PowerShell에 붙여넣기(UTF-8 BOM이라 powershell -File로도 실행 가능)
│    .py   check.py에 붙여넣고 python check.py
│    4_프롬프트.txt            Claude Code에 붙여넣기
│    6_기대결과.txt, *_예시출력.txt   실행 결과와 비교
├─ 결과_CLAUDE.md             그 차시를 마쳤을 때의 CLAUDE.md 전체
└─ 정답코드/mywork/           그 차시의 정답 코드(폴백 때 mywork\로 복사)
```

**관리 방법**

- 원본은 **문서**입니다. 이 폴더는 `labs/quick/_tools/export_code.py`가 문서와 `solutions/`에서 만들어 내므로, 직접 고치지 말고 문서(또는 `solutions/`)를 고친 뒤 다시 생성합니다.
  ```powershell
  python labs\quick\_tools\export_code.py 2      # 2차시만 다시 생성
  python labs\quick\_tools\export_code.py        # 2~10차시 전부
  ```
- 문서를 고쳤다면 먼저 `python labs\quick\_tools\run_checks.py --work <빈 폴더>`로 코드가 그대로 동작하는지 확인한 뒤 생성합니다.
