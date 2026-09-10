"""7차시 PDF 입력 경로 검증용 샘플 PDF 생성.

pdfplumber는 텍스트 추출만 하므로, 별도 PDF 생성 라이브러리를 새로 추가하지
않고 이미 requirements.txt에 있는 matplotlib으로 텍스트 한 페이지짜리
PDF를 만든다 (matplotlib PDF 백엔드는 텍스트를 래스터가 아닌 실제 텍스트
객체로 임베드하므로 pdfplumber로 추출 가능하다).
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

os.makedirs("data/raw", exist_ok=True)

plt.rc("font", family="Malgun Gothic")
본문 = (
    "2026년 1월 온라인쇼핑 동향\n\n"
    "2026년 1월 온라인쇼핑 거래액은 201,250억 원으로 전월 대비 1.5% 증가하였다.\n"
    "전년동월대비로는 8.7% 증가한 수치이다. 이는 역대 1월 기준 최대치를 기록한 것이다.\n"
    "모바일쇼핑 거래액 비중은 전체의 78%를 차지하며 꾸준한 증가세를 보이고 있다."
)

fig = plt.figure(figsize=(8.27, 11.69))  # A4
fig.text(0.1, 0.9, 본문, fontsize=12, va="top", wrap=True)
path = "data/raw/온라인쇼핑동향_2026_01.pdf"
plt.savefig(path)
plt.close(fig)
print(f"생성 완료: {path}")
