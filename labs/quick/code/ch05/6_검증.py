# 검증 Ch05
import sys, json
sys.path.insert(0, ".")
from mywork.stats import (calc_category_indicators, detect_special_points, build_interpretation_sentences,
                          derive_history_indicators, add_calculated_indicators, check_percent_unit)

with open("mywork/press_data.json", encoding="utf-8") as f:
    data = json.load(f)

# ① 품목별 전월대비증감률·비중·순위 (pandas 계산)
items = calc_category_indicators(data["품목별지표"])
for r in items:
    print(r)
assert [r["비중"] for r in items] == [32.3, 25.8, 23.9, 13.0, 5.0]
assert [r["순위"] for r in items] == [1, 2, 3, 4, 5]
assert [r["전월대비증감률"] for r in items] == [1.7, 4.4, 3.4, -3.5, -8.9]
assert all(type(r["당월거래액"]) is int and type(r["비중"]) is float for r in items), "numpy 타입이 섞임"

# ② 과거 이력만으로 역대 최대·최근 추세·증감률 계산 (동월 기준)
과거 = [h for h in data["월별이력"] if h["연월"] < "2026-01"]
h = derive_history_indicators(과거, "2026-01", 201250)
print("이력 계산:", h)
assert h == {"역대최대여부": True, "최근3개월증감률": [2.0, 1.8, 1.5], "전월대비증감률": 1.5, "전년동월대비증감률": 8.7}
assert h["전월대비증감률"] == data["계산지표"]["전월대비증감률"], "이력으로 다시 계산한 값이 계산지표와 다름"
assert h["전년동월대비증감률"] == data["계산지표"]["전년동월대비증감률"]
assert derive_history_indicators([], "2026-01", 201250)["역대최대여부"] is None, "이력이 없을 때 None이 아님"

# ③ 슬라이드 14의 예시와 감소 문장
assert detect_special_points(1.5, 8.7, True, [2.0, 1.8, 1.5]) == ["역대 최대치 경신", "전년동월 대비 큰 폭 증가", "최근 3개월 연속 증가세"]
감소 = build_interpretation_sentences(["전월 대비 큰 폭 감소"], {"총거래액": 1, "전월대비증감률": -6.2, "전년동월대비증감률": 0}, "온라인쇼핑 거래액")
assert 감소 == ["온라인쇼핑 거래액이 전월 대비 6.2% 감소하며 큰 폭의 하락세를 보였다."], 감소
assert check_percent_unit("비중이 3%p 확대", True) and not check_percent_unit("비중이 3% 확대", True)

# ④ 통합 함수 → 표준 데이터에 저장 (슬라이드 18·20의 해석문 재현)
계산지표_전 = dict(data["계산지표"])
data = add_calculated_indicators(data)
r = data["통계해석결과"]
print("특이점:", r["특이점목록"])
for s in r["해석문장"]:
    print("해석:", s)
assert r["해석문장"][:2] == ["온라인쇼핑 거래액은 201,250억 원으로 동월 기준 역대 최대치를 기록하였다.",
                          "온라인쇼핑 거래액이 전년동월 대비 8.7% 증가하며 큰 폭의 상승세를 보였다."]
assert data["계산지표"] == 계산지표_전 and data["역대최대여부"] is True and data["품목별지표"][0]["비중"] == 32.3
with open("mywork/press_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("Ch05 OK — 품목별지표·통계해석결과 저장")
