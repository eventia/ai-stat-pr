# python -c 명령어 옵션 및 패키지 검증 구문 해설

> **작성 위치**: `labs/quick/antigravity/Ch02_python_c_옵션해설.md`  
> **대상 코드**: `Ch02-10분실습.md`의 패키지 설치 확인 단계

---

## 1. 코드 원문

```powershell
python -c "import anthropic, dotenv, pandas, openpyxl, pdfplumber, requests, sklearn, kiwipiepy, networkx, matplotlib, reportlab, hwpx, pytest; print('패키지 OK')"
```

---

## 2. `python -c` 란?

* **`-c`는 Command(명령어)의 약자**입니다.
* 별도의 파이썬 스크립트 파일(`.py`)을 생성하거나 파이썬 대화형 쉘(REPL)에 들어가지 않고, **터미널(PowerShell, Bash 등) 명령줄에서 직접 파이썬 코드를 즉시 한 줄로 실행**할 때 사용하는 파이썬 기본 실행 옵션입니다.

```bash
# 기본 사용 형식
python -c "파이썬 코드"
```

---

## 3. 코드의 동작 원리 및 목적

### 3-1. 동작 원리
1. **패키지 일괄 Import 시도**:
   - `import anthropic, dotenv, pandas, ...` 구문이 실행됩니다.
   - 나열된 패키지 중 **하나라도 설치되어 있지 않거나 문제가 있으면**, 즉시 `ModuleNotFoundError` 예외가 발생하며 프로세스가 중단됩니다.
2. **최종 정상 확인**:
   - 모든 패키지가 정상적으로 설치되어 에러 없이 임포트가 완료되면, 세미콜론(`;`) 뒤의 `print('패키지 OK')`가 실행됩니다.
   - 터미널에 최종적으로 **`패키지 OK`**라는 문구가 출력됩니다.

### 3-2. 이 방식을 쓰는 이유 (실습 설계 관점)
* **초고속 스모크 테스트(Smoke Test)**:
  - `pip install -r requirements.txt`가 끝난 직후, 각 패키지가 정말 현재 활성화된 가상환경(`.venv`)에 올바르게 설치되었는지 1초 만에 확인합니다.
* **임시 파일 생성 불필요**:
  - `test.py` 같은 검증용 임시 파일을 만들고 지우는 번거로움 없이 터미널 한 줄로 깔끔하게 끝낼 수 있습니다.
