# 관찰 Ch02
import sys, json
sys.path.insert(0, ".")
from mywork.clean import mask_sensitive_info, standardize_date

with open("data/raw_202601.json", encoding="utf-8") as f:
    raw = json.load(f)
with open("mywork/press_data.json", encoding="utf-8") as f:
    data = json.load(f)
print("[원본 원문]", repr(raw["원문"][:60]), "...")
print("[정제 원문]", repr(data["원문"][:60]), "...")
print("[원본 공표일자]", raw["공표일자"], "→ [정제]", data["문서정보"]["공표일자"])
print("[계산지표 동일?]", raw["계산지표"] == data["계산지표"])
for s in ["문의 010-1234-5678", "문의 011-123-4567", "문의 02-123-4567", "주민 900101-1234567"]:
    print(s, "->", mask_sensitive_info(s))
