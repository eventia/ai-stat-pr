# 관찰 Ch06
import sys, json
import pandas as pd
sys.path.insert(0, ".")

with open("mywork/press_data.json", encoding="utf-8") as f:
    data = json.load(f)
h = pd.DataFrame(data["월별이력"]).rename(columns={"값": "거래액"}).sort_values("연월").reset_index(drop=True)
h["증감"] = h["거래액"].diff()
h["방향바뀜"] = h["증감"] * h["증감"].shift(-1) < 0
print(h.tail(6).to_string(index=False))
for v in data["시각자료설명"]:
    print(f"[{v['소주제']}] {v['설명문']}")
