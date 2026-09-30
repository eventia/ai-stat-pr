# 선택 Ch09 — 실제 Claude API로 문체 통일 + 3단계 검수 (2회, 비용 발생)
import sys, json
sys.path.insert(0, ".")
from mywork.write import assemble_full_text, unify_style
from mywork.review import check_formatting_errors, cross_check_all_numbers, review_press_release

with open("mywork/press_data.json", encoding="utf-8") as f:
    data = json.load(f)
최종본 = unify_style(assemble_full_text(data))
print(최종본)
검수결과 = {
    "표기오류검사": check_formatting_errors(최종본),
    "수치교차검증": cross_check_all_numbers(최종본, data),
    "AI감수지적사항": review_press_release(최종본, data),
}
print(json.dumps(검수결과, ensure_ascii=False, indent=2))
data["최종본"], data["검수결과"] = 최종본, 검수결과
with open("mywork/press_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("최종본·검수결과 저장")
