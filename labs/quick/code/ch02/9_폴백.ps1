$SOL = "C:\dev\claudeCLI\보도자료작성-실습1\labs\quick\solutions"   # 정답 코드 폴더. 위치가 다르면 고치세요
New-Item mywork -ItemType Directory -Force | Out-Null
if (-not (Test-Path mywork\__init__.py)) { New-Item mywork\__init__.py -ItemType File | Out-Null }
Copy-Item "$SOL\ch02\*.py" mywork\ -Force
