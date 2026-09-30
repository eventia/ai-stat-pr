dir output
Get-Content logs\pipeline.log -Encoding UTF8 -Tail 4
Invoke-Item "output\2026년 1월 온라인쇼핑 동향_승인대기.pdf"
