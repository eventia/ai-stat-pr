python -m venv .venv
.\.venv\Scripts\Activate.ps1
$env:PYTHONUTF8 = "1"
python -c "import sys; print(sys.version.split()[0]); print(sys.executable)"
