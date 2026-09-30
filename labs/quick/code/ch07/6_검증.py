# 검증 Ch07 — 입력 함수와 헤드라인 흐름 (가짜 응답, 비용 0)
import sys, json
from types import SimpleNamespace as NS
sys.path.insert(0, ".")
from mywork.data_io import load_input
from mywork.clean import clean_and_structure
from mywork.review import verify_numbers
import mywork.write as W

with open("mywork/press_data.json", encoding="utf-8") as f:
    data = json.load(f)

# ① xlsx 입력 → 2차시 결과와 같은 표준 데이터가 되는가
raw = load_input("data/온라인쇼핑동향_2026_01.xlsx")
json.dumps(raw, ensure_ascii=False)  # numpy 타입이 남아 있으면 여기서 TypeError
print("xlsx:", raw["제목"], "|", raw["계산지표"], "| 이력", len(raw["월별이력"]), "개 | 역대최대:", raw["역대최대여부"])
assert raw["제목"] == "2026년 1월 온라인쇼핑 동향" and raw["계산지표"] == data["계산지표"]
assert type(raw["계산지표"]["총거래액"]) is int, "numpy 타입이 남아 있음"
assert len(raw["월별이력"]) == 13 and raw["역대최대여부"] is True and raw["최근3개월증감률"] == [2.0, 1.8, 1.5]
assert raw["품목별지표"][0]["품목"] == "의류", "품목별지표 JSON 문자열을 풀지 않음"
표준 = clean_and_structure(raw)
assert 표준["원문"] == data["원문"] and 표준["문서정보"]["공표일자"] == "2026-03-01"

# ② PDF 입력 → 원문만
pdf = load_input("data/온라인쇼핑동향_2026_01.pdf")
print("pdf 키:", list(pdf))
assert list(pdf) == ["원문"] and clean_and_structure(pdf)["원문"] == data["원문"]
try:
    load_input("data/raw_202601.json")
    raise AssertionError("json 파일을 거부하지 않음")
except ValueError as e:
    print("지원하지 않는 형식:", e)

# ③ 핵심지표 선정과 헤드라인 프롬프트
assert W.select_core_indicators({**data["계산지표"], "모바일비중": 78}) == data["계산지표"]
prompt = W.build_headline_prompt(W.select_core_indicators(data["계산지표"]), data["통계해석결과"]["특이점목록"], data["문서정보"])
for 필수 in ["국가데이터처", "2026년 1월", "온라인쇼핑 거래액", "201,250억 원", "1.5%", "8.7%", "역대 최대치 경신"]:
    assert 필수 in prompt, f"헤드라인 프롬프트에 '{필수}' 없음"

# ④ 가짜 응답으로 생성 → 제목·부제·리드문 모두 수치 검증
sample = {"제목": "1월 온라인쇼핑 거래액, 역대 최대",
          "부제": "전년동월 대비 8.7% 증가한 201,250억 원",
          "리드문": "국가데이터처는 2026년 1월 온라인쇼핑 거래액이 201,250억 원으로 집계되었다고 밝혔다. "
                   "이는 전월 대비 1.5%, 전년동월 대비 8.7% 증가한 수치이다."}
W.client.messages.create = lambda **kw: NS(stop_reason="end_turn", content=[NS(type="text", text=json.dumps(sample, ensure_ascii=False))])
hs = W.generate_headline_set(data)
for 항목 in ["제목", "부제", "리드문"]:
    ok = verify_numbers(hs[항목], data)
    print(f"{항목} 수치 검증:", "통과" if ok else "재검토 필요")
    assert ok
print("Ch07 OK — 입력·헤드라인 구조 검증 통과 (실제 API 호출은 8절)")
