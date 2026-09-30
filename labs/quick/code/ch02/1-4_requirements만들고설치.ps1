@"
# 2~10차시 10분 실습 전체에서 쓰는 패키지
anthropic
python-dotenv
pandas
openpyxl
pdfplumber
requests
scikit-learn
kiwipiepy
networkx
matplotlib
reportlab
python-hwpx
pytest
"@ | Set-Content requirements.txt -Encoding utf8

python -m pip install -r requirements.txt

python -c "import anthropic, dotenv, pandas, openpyxl, pdfplumber, requests, sklearn, kiwipiepy, networkx, matplotlib, reportlab, hwpx, pytest; print('패키지 OK')"
