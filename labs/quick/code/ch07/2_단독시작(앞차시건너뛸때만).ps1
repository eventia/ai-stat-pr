# 단독 시작 Ch07 — 이미 있는 파일은 덮어쓰지 않음
$SOL = "C:\dev\claudeCLI\보도자료작성-실습1\labs\quick\solutions"
New-Item mywork, data -ItemType Directory -Force | Out-Null
if (-not (Test-Path mywork\__init__.py)) { New-Item mywork\__init__.py -ItemType File | Out-Null }
foreach ($ch in "ch06","ch05","ch04","ch03","ch02") { Get-ChildItem "$SOL\$ch\*.py" | Where-Object { -not (Test-Path "mywork\$($_.Name)") } | Copy-Item -Destination mywork\ }
Get-ChildItem "$SOL\data\*" | Where-Object { -not (Test-Path "data\$($_.Name)") } | Copy-Item -Destination data\
if (-not (Test-Path mywork\press_data.json)) { Copy-Item "$SOL\snapshots\press_data_after_ch06.json" mywork\press_data.json }
if (-not (Test-Path CLAUDE.md)) { Copy-Item "$SOL\snapshots\CLAUDE_after_ch06.md" CLAUDE.md }
