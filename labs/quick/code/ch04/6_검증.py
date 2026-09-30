# 검증 Ch04 — 가짜 응답으로 구조 확인 (실제 API 호출 없음, 비용 0)
import sys, json, copy
from types import SimpleNamespace as NS
sys.path.insert(0, ".")
import mywork.write as W
from mywork.review import verify_numbers, find_unverified_numbers

펜스 = "`" * 3   # 백틱 3개 — 모델이 응답을 코드펜스로 감싸는 경우를 흉내 냄
가짜_요약 = {"삼줄요약": ["2026년 1월 온라인쇼핑 거래액은 201,250억 원으로 집계되었다.",
                     "이는 전월 대비 1.5%, 전년동월 대비 8.7% 증가한 수치이다.",
                     "역대 1월 기준 최대치를 기록하였다."],
          "제목후보": ["1월 온라인쇼핑 거래액, 역대 최대", "온라인쇼핑 거래액 8.7% 증가", "1월 온라인쇼핑 거래액 201,250억 원"]}
captured = []
def fake_create(**kwargs):
    captured.append(kwargs)
    text = "요약입니다.\n" + 펜스 + "json\n" + json.dumps(가짜_요약, ensure_ascii=False) + "\n" + 펜스
    return NS(stop_reason="end_turn", content=[NS(type="text", text=text)])
W.client.messages.create = fake_create

with open("mywork/press_data.json", encoding="utf-8") as f:
    data = json.load(f)

# ① 프롬프트: 숫자는 콤마·단위 표기로, 증감은 부호에 따라 증가/감소로
prompt = W.build_summary_prompt(data)
print(next((줄 for 줄 in prompt.splitlines() if "201,250억 원" in 줄), "(총거래액 줄 없음)"))
assert "201,250억 원" in prompt and "1.5% 증가" in prompt and "8.7% 증가" in prompt
assert all(k in prompt for k in data["NLP분석결과"]["핵심키워드"]), "핵심키워드가 프롬프트에 없음"
감소 = copy.deepcopy(data)
감소["계산지표"]["전월대비증감률"] = -2.3
p2 = W.build_summary_prompt(감소)
assert "2.3% 감소" in p2 and "-2.3" not in p2, "감소를 부호로 처리하지 못함"

# ② 방어적 JSON 파싱
assert W.parse_json_response("설명 " + 펜스 + 'json\n{"a": 1}\n' + 펜스 + " 끝") == {"a": 1}
assert W.parse_json_response('[{"a": 1}]') == [{"a": 1}]

# ③ API 호출 방식
result = W.generate_summary(data)
call = captured[-1]
print("모델:", call["model"], "| thinking:", call.get("thinking"), "| temperature 사용:", "temperature" in call)
assert call["model"] == W.MODEL_NAME == "claude-sonnet-5-5"
assert call.get("thinking") == {"type": "between_tools"} and "temperature" not in call
assert "숫자" in call["system"], "시스템 프롬프트에 숫자 제약이 없음"
assert len(result["삼줄요약"]) == 3 and len(result["제목후보"]) == 3

# ④ 수치 교차 검증
for s in result["삼줄요약"] + result["제목후보"]:
    assert verify_numbers(s, data), f"검증 실패: {s}"
assert find_unverified_numbers("거래액은 201,500억 원으로 12.3% 증가하였다.", data) == ["201,500", "12.3"]
assert verify_numbers("생활용품은 3.5% 감소하였다.", {"품목별지표": [{"전월대비증감률": -3.5}]}), "음수 절댓값 미등록"
print("Ch04 OK — 구조 검증 통과 (실제 API 호출은 8절)")
