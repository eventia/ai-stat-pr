# 5차시 실습 코드 — 통계 계산과 해석문

실습 문서: [../../Ch05-10분실습.md](../../Ch05-10분실습.md) · 강의: `labs/강의자료/CH05-ContentV10.pptx`

문서에 나오는 코드를 **진행 순서대로** 모아 둔 폴더입니다. 파일 이름 앞의 숫자는 문서의 절 번호입니다.
이 폴더는 `labs/quick/_tools/export_code.py`가 문서에서 만듭니다 — 고칠 때는 문서를 고친 뒤 다시 생성하세요.

| 절 | 파일 | 사용법 |
| --- | --- | --- |
| 1 | [1_시작전준비.ps1](1_시작전준비.ps1) | PowerShell에 붙여넣기 |
| 2 | [2_단독시작(앞차시건너뛸때만).ps1](2_단독시작(앞차시건너뛸때만).ps1) | PowerShell에 붙여넣기 |
| 3 | [3_CLAUDE에5차시블록추가.ps1](3_CLAUDE에5차시블록추가.ps1) | PowerShell에 붙여넣기 |
| 4 | [4_프롬프트.txt](4_프롬프트.txt) | Claude Code에 그대로 붙여넣기 |
| 5 | [5_생성결과확인.ps1](5_생성결과확인.ps1) | PowerShell에 붙여넣기 |
| 6 | [6_검증.py](6_검증.py) | check.py에 붙여넣고 python check.py |
| 6 | [6_기대결과.txt](6_기대결과.txt) | 실행 결과와 비교 |
| 7 | [7_관찰.py](7_관찰.py) | check.py에 붙여넣고 python check.py |
| 7 | [7_관찰_예시출력.txt](7_관찰_예시출력.txt) | 실행 결과와 비교(예시 출력) |
| 9 | [9_폴백.ps1](9_폴백.ps1) | PowerShell에 붙여넣기 |
| 3 | [결과_CLAUDE.md](결과_CLAUDE.md) | 5차시를 마쳤을 때의 CLAUDE.md 전체(참고용) |
| 9 | [정답코드/mywork/](정답코드/mywork) | 이 차시의 정답 코드(stats.py) — 폴백 때 mywork\로 복사 |

- PowerShell 명령은 2차시 1-2절 이후 항상 프로젝트 폴더(`C:\dev\quick-practice`)에서, 가상환경을 켠 상태로 실행합니다.
- `.ps1`은 UTF-8(BOM)로 저장되어 있어 `powershell -File 파일명`으로 바로 실행할 수도 있습니다(프로젝트 폴더에서).
- `.py`는 프로젝트 폴더 바로 아래의 `check.py`에 붙여넣어 실행합니다(`mywork` 폴더 안에서 실행하지 않음).
