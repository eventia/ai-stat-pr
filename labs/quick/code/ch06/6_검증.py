# 검증 Ch06
import sys, os, json
import pandas as pd
sys.path.insert(0, ".")
from mywork.charts import generate_chart_description, generate_table_description, build_visual_descriptions

with open("mywork/press_data.json", encoding="utf-8") as f:
    data = json.load(f)
items = pd.DataFrame(data["품목별지표"])
history = pd.DataFrame(data["월별이력"]).rename(columns={"값": "거래액"})

bar = generate_chart_description("bar", items)
pie = generate_chart_description("pie", items)
line = generate_chart_description("line", history, label="온라인쇼핑 거래액")
print("막대:", bar)
print("원형:", pie)
print("꺾은선:", line)
assert bar.startswith("의류") and "65,000억 원" in bar and "52,000억 원" in bar and "10,000억 원" in bar
assert "32.3%" in pie and "(25.8%)" in pie and "(23.9%)" in pie
assert line.startswith("온라인쇼핑 거래액은 2025-01부터 2026-01까지 증가세"), "꺾은선 주어·추세 확인"
assert "2025-09에 방향이 바뀐 뒤" in line and line.endswith("201,250억 원을 기록하였다.")
assert generate_chart_description("line", history).startswith("총거래액은"), "label이 없을 때 기본 주어"
assert generate_table_description(items).startswith("품목별 순위는 1위 의류(32.3%), 2위 가전(25.8%)")

visuals = build_visual_descriptions(data)
assert [v["소주제"] for v in visuals] == ["품목별 동향", "품목별 비중", "시계열 동향"]
assert all(set(v) == {"소주제", "그래프유형", "이미지경로", "설명문"} for v in visuals)
assert all(os.path.exists(v["이미지경로"]) for v in visuals), "그래프 파일이 없음"
data["시각자료설명"] = visuals
with open("mywork/press_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("그래프:", sorted({v["이미지경로"] for v in visuals}))
print("Ch06 OK — 시각자료설명 저장")
