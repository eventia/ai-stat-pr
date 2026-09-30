# 선택 Ch08 — 실제 Claude API로 본문 단락 생성 (3회, 비용 발생)
import sys, json
sys.path.insert(0, ".")
from mywork.write import generate_body_paragraphs
from mywork.review import find_unverified_numbers

with open("mywork/press_data.json", encoding="utf-8") as f:
    data = json.load(f)
본문 = generate_body_paragraphs(data)
for p in 본문:
    print(f"[{p['소주제']}] {p['내용']}")
    print("   근거 없는 숫자:", find_unverified_numbers(p["내용"], data))
data["본문"] = 본문
with open("mywork/press_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("본문 저장")
