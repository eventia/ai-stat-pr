# PowerShell 환경 변수($env:) 및 PYTHONUTF8="1" 상세 해설

> **작성 위치**: `labs/quick/antigravity/PowerShell_환경변수_PYTHONUTF8_해설.md`  
> **주제**: PowerShell 가상 드라이브 `$env:`의 구조, 환경 변수 확인 방법, `PYTHONUTF8 = "1"`의 필요성

---

## 1. `$env:` 란 무엇인가?

### 1-1. PowerShell의 가상 드라이브(PSDrive) 개념
* PowerShell은 일반 디스크 드라이브(`C:`, `D:`)뿐만 아니라, **시스템 환경 변수, 레지스트리, 별칭(Alias) 등을 드라이브 형태로 추상화**하여 관리합니다. 이를 **PSDrive**라고 부릅니다.
* 그중 **환경 변수(Environment)**를 담당하는 가상 드라이브 이름이 바로 **`Env:`**입니다.

### 1-2. `$env:변수명` 문법
* `$env:변수명`은 **"Env: 드라이브에 있는 특정 환경 변수에 접근하겠다"**는 의미의 PowerShell 표준 문법입니다.
* 예시:
  - `$env:USERNAME` : 현재 로그인한 윈도우 사용자 이름
  - `$env:PATH` : 시스템 PATH 환경 변수 값
  - `$env:PYTHONUTF8 = "1"` : 현재 PowerShell 세션에 `PYTHONUTF8` 환경 변수를 정의하고 값 `1`을 대입

> [!NOTE]
> `$env:변수명 = "값"` 형태로 설정한 변수는 **현재 열려 있는 터미널 세션 동안에만 유지(프로세스 레벨)**되며, 터미널을 닫으면 자동으로 사라지므로 시스템에 부작용을 주지 않는 안전한 방식입니다.

---

## 2. `$env:` 에 있는 값을 확인하는 방법

PowerShell에서 환경 변수를 확인하는 방법은 크게 3가지가 있습니다.

### 2-1. 특정 환경 변수 1개 확인하기
가장 간단한 방법은 변수명 자체를 입력하거나 출력하는 것입니다.

```powershell
# 방법 1: 변수명만 입력 (가장 추천)
$env:PYTHONUTF8

# 방법 2: Write-Output 또는 echo 사용
echo $env:PYTHONUTF8

# 방법 3: Get-Item / Get-ChildItem Cmdlet 사용
Get-Item Env:PYTHONUTF8
```

### 2-2. 특정 단어가 포함된 환경 변수 검색하기
환경 변수 이름의 일부만 기억나거나 관련 변수를 모아보고 싶을 때 사용합니다.

```powershell
# 이름에 "PYTHON"이 포함된 모든 환경 변수 조회
Get-ChildItem Env:*PYTHON*

# 이름에 "UTF"가 포함된 환경 변수 조회
Get-ChildItem Env:*UTF*
```

### 2-3. 전체 환경 변수 목록 확인하기
`Env:`는 가상 드라이브이므로 일반 폴더 목록을 보듯이 `dir` 또는 `Get-ChildItem`을 쓰면 전체 목록(이름과 값)이 표 형태로 출력됩니다.

```powershell
# 전체 환경 변수 목록 출력
Get-ChildItem Env:

# 또는 단축 별칭(alias) 사용
dir env:
ls env:
```

---

## 3. `$env:PYTHONUTF8 = "1"` 은 왜 필요할까?

### 3-1. Python 3.7+ UTF-8 Mode (PEP 540)
* 파이썬은 윈도우에서 기본적으로 **시스템 기본 로캘(한국어 윈도우의 경우 CP949 / EUC-KR)**을 사용하여 파일 및 콘솔 입출력을 처리하려는 성향이 있습니다.
* 하지만 본 프로젝트의 보도자료 데이터(`press_data.json`), 한글 로그, LLM 프롬프트/응답은 모두 **UTF-8**로 인코딩되어 있습니다.
* 따라서 별도 설정이 없으면 한글 텍스트를 터미널에 출력하거나 파일로 읽을 때 다음과 같은 치명적인 에러가 발생합니다:
  ```text
  UnicodeEncodeError: 'cp949' codec can't encode character ...
  UnicodeDecodeError: 'cp949' codec can't decode byte ...
  ```

### 3-2. 해결책으로서의 `PYTHONUTF8 = "1"`
* `$env:PYTHONUTF8 = "1"`을 실행하면 파이썬 인터프리터의 **UTF-8 모드**가 강제로 활성화됩니다.
* 그 결과:
  1. `print()`를 통한 터미널 표준 입출력(`sys.stdout`)이 UTF-8로 고정되어 **한글 깨짐이 사라집니다.**
  2. `open()` 함수 실행 시 `encoding` 옵션을 지정하지 않더라도 기본 인코딩이 UTF-8로 동작합니다.
* 실습을 원활하고 오류 없이 진행하기 위한 필수적인 **Windows 방어 조치**입니다.
