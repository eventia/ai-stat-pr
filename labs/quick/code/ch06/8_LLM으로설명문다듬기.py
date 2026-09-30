# 선택 Ch06 — LLM으로 설명문 표현만 다듬기 (1회, 비용 발생)
import sys, json
sys.path.insert(0, ".")
from mywork.write import call_claude
from mywork.review import find_unverified_numbers

with open("mywork/press_data.json", encoding="utf-8") as f:
    data = json.load(f)
원문 = data["시각자료설명"][0]["설명문"]
prompt = f"""다음 규칙 기반 설명문을 보도자료 문체로 자연스럽게 다듬어 주세요.
원문의 숫자와 단위는 표기 그대로 모두 유지하십시오(예: 65,000억 원을 6조 5,000억 원으로 바꾸지 말 것).
새로운 숫자나 사실을 추가하지 말고 문장 표현만 개선하십시오. 다듬은 문장만 출력하십시오.

원문: {원문}"""
결과 = call_claude(prompt)
print("원문:", 원문)
print("다듬음:", 결과)
print("근거 없는 숫자:", find_unverified_numbers(결과, data))
