# 검증 Ch02
import sys, json, copy
sys.path.insert(0, ".")
from mywork.config import DATA_DICTIONARY, REQUIRED_FIELDS, INDICATOR_UNITS
from mywork.clean import mask_sensitive_info, standardize_date, clean_text, clean_and_structure

# ① 강의 슬라이드 21의 '정제 전 → 정제 후'를 그대로 재현
before = "2026년  1월 온라인쇼핑   거래액은   201,250억원으로   전월대비  1.5%   증가하였음.(주:잠정치)"
after = clean_text(before)
print("정제 전:", before)
print("정제 후:", after)
assert after == "2026년 1월 온라인쇼핑 거래액은 201,250억 원으로 전월 대비 1.5% 증가하였다.", "슬라이드 21과 다름"

# ② 데이터 딕셔너리에서 필수 항목·단위를 뽑아내는가
assert REQUIRED_FIELDS == ["총거래액", "전월대비증감률", "전년동월대비증감률"]
assert INDICATOR_UNITS == {"총거래액": "억 원", "전월대비증감률": "%", "전년동월대비증감률": "%"}
assert DATA_DICTIONARY["공표일자"]["등급"] == "참고"

# ③ 날짜 표준화
for d in ["2026.3.1", "2026/03/01", "2026-3-1", "2026년 3월 1일"]:
    assert standardize_date(d) == "2026-03-01", f"{d} 변환 실패"

# ④ 마스킹 (휴대전화 앞자리 6가지 + 지역번호는 그대로 + 주민번호)
for p in ["010", "011", "016", "017", "018", "019"]:
    assert mask_sensitive_info(f"{p}-1234-5678") == "010-****-****", f"{p}-1234-5678 이 마스킹되지 않음"
    assert mask_sensitive_info(f"{p}-123-4567") == "010-****-****", f"{p}-123-4567 이 마스킹되지 않음"
assert mask_sensitive_info("02-123-4567") == "02-123-4567"
assert mask_sensitive_info("900101-1234567") == "******-*******"

# ⑤ 원본 보존 + 구조화
with open("data/raw_202601.json", encoding="utf-8") as f:
    raw = json.load(f)
raw_before = copy.deepcopy(raw)
data = clean_and_structure(raw)
assert raw == raw_before, "원본(raw)이 바뀌었음 — 원본 보존 위반"
assert data["계산지표"] == raw["계산지표"], "계산지표가 바뀌었음"
assert data["문서정보"]["공표일자"] == "2026-03-01"
assert data["문서정보"]["자료출처"] == "공공데이터포털 Open API"
assert data["문서정보"]["지표명"] == "온라인쇼핑 거래액"
assert data["원문"] == ("2026년 1월 온라인쇼핑 거래액은 201,250억 원으로 전월 대비 1.5% 증가하였다. "
                        "전년동월대비로는 8.7% 증가한 수치이다. 이는 역대 1월 기준 최대치를 기록한 것이다. "
                        "모바일쇼핑 거래액 비중은 전체의 78%를 차지하며 꾸준한 증가세를 보이고 있다.")
assert len(data["품목별지표"]) == 5 and len(data["월별이력"]) == 13
data["품목별지표"][0]["당월거래액"] = -1
assert raw["품목별지표"][0]["당월거래액"] == 65000, "품목별지표를 복사하지 않고 그대로 넣었음"

with open("mywork/press_data.json", "w", encoding="utf-8") as f:
    json.dump(clean_and_structure(raw), f, ensure_ascii=False, indent=2)
print("문서정보:", data["문서정보"])
print("Ch02 OK — mywork/press_data.json 저장")
