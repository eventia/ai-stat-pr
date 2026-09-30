# 관찰 Ch07
import sys, json
import pandas as pd
sys.path.insert(0, ".")
import mywork.write as W

v = pd.read_excel("data/온라인쇼핑동향_2026_01.xlsx").iloc[0]["총거래액"]
print("① 엑셀에서 읽은 값의 타입:", type(v).__name__)
try:
    json.dumps({"총거래액": v})
except TypeError as e:
    print("① 그대로 저장하면:", e)

with open("mywork/press_data.json", encoding="utf-8") as f:
    data = json.load(f)
print("② 헤드라인 프롬프트 ↓")
print(W.build_headline_prompt(W.select_core_indicators(data["계산지표"]), data["통계해석결과"]["특이점목록"], data["문서정보"]))
