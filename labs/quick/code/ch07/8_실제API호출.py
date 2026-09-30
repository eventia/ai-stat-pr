# 선택 Ch07 — 실제 Claude API로 제목·부제·리드문 생성 (1회, 비용 발생)
import sys, json
sys.path.insert(0, ".")
from mywork.write import generate_headline_set
from mywork.review import find_unverified_numbers

with open("mywork/press_data.json", encoding="utf-8") as f:
    data = json.load(f)
hs = generate_headline_set(data)
for 항목 in ["제목", "부제", "리드문"]:
    print(f"[{항목}] {hs[항목]}")
    print("   근거 없는 숫자:", find_unverified_numbers(hs[항목], data))
data["헤드라인"] = hs
with open("mywork/press_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("헤드라인 저장")
