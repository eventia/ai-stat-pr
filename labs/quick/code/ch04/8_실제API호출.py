# 선택 Ch04 — 실제 Claude API 호출 (1회, 비용 발생)
import sys, json
sys.path.insert(0, ".")
from mywork.write import generate_summary, MODEL_NAME
from mywork.review import find_unverified_numbers

with open("mywork/press_data.json", encoding="utf-8") as f:
    data = json.load(f)
result = generate_summary(data)
print("모델:", MODEL_NAME)
for s in result["삼줄요약"]:
    print("요약:", s, "| 근거 없는 숫자:", find_unverified_numbers(s, data))
for t in result["제목후보"]:
    print("제목:", t, "| 근거 없는 숫자:", find_unverified_numbers(t, data))
data["요약결과"] = result
with open("mywork/press_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("요약결과 저장")
