# 준비 Ch07 — xlsx·PDF 원자료 만들기
import json
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

with open("data/raw_202601.json", encoding="utf-8") as f:
    raw = json.load(f)

요약 = pd.DataFrame([{
    "연월": raw["기준연월"], "공표일자": raw["공표일자"], "보안등급": raw["보안등급"],
    **raw["계산지표"],
    "핵심내용": json.dumps(raw["핵심내용"], ensure_ascii=False),
    "원문": raw["원문"],
    "품목별지표": json.dumps(raw["품목별지표"], ensure_ascii=False),
}])
이력 = pd.DataFrame([{"연월": h["연월"], "총거래액": h["값"]} for h in raw["월별이력"] if h["연월"] < raw["기준연월"]])
with pd.ExcelWriter("data/온라인쇼핑동향_2026_01.xlsx") as w:
    요약.to_excel(w, sheet_name="요약", index=False)
    이력.to_excel(w, sheet_name="이력", index=False)

문장들 = ["2026년 1월 온라인쇼핑 거래액은 201,250억 원으로 전월 대비 1.5% 증가하였다.",
          "전년동월대비로는 8.7% 증가한 수치이다.",
          "이는 역대 1월 기준 최대치를 기록한 것이다.",
          "모바일쇼핑 거래액 비중은 전체의 78%를 차지하며 꾸준한 증가세를 보이고 있다."]
pdfmetrics.registerFont(TTFont("Malgun", "C:/Windows/Fonts/malgun.ttf"))
c = canvas.Canvas("data/온라인쇼핑동향_2026_01.pdf", pagesize=A4)
c.setFont("Malgun", 10)
for i, 문장 in enumerate(문장들):
    c.drawString(50, 800 - i * 18, 문장)
c.save()
print("원자료 생성: data/온라인쇼핑동향_2026_01.xlsx (요약·이력 시트), data/온라인쇼핑동향_2026_01.pdf")
