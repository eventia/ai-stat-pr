$SOL = "C:\dev\claudeCLI\보도자료작성-실습1\labs\quick\solutions"   # 정답 코드 폴더. 위치가 다르면 고치세요
Copy-Item "$SOL\ch10\export.py" mywork\export.py
python -c "import mywork.export; print('export OK')"
