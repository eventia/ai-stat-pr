# 검증 Ch09 — 가짜 응답으로 구조 확인 (비용 0)
import sys, json
from types import SimpleNamespace as NS
sys.path.insert(0, ".")
import mywork.write as W
from mywork.review import check_formatting_errors, cross_check_all_numbers, review_press_release

with open("mywork/press_data.json", encoding="utf-8") as f:
    data = json.load(f)

# ① 초안 조립 (리드문 + 본문 단락, 빈 줄로 구분)
draft = W.assemble_full_text(data)
assert draft.startswith(data["헤드라인"]["리드문"] + "\n\n"), "리드문 뒤에 빈 줄이 없음"
assert all(p["내용"] in draft for p in data["본문"]), "본문 단락이 빠짐"

# ② 표기 검수 (정규식 1차 필터)
나쁜 = "거래액은 201250억원으로 집계되었다. 의류 비중은 전월보다 확대되었다."
오류 = check_formatting_errors(나쁜)
for e in 오류:
    print("표기 오류:", e)
assert len(오류) == 3, "억원·콤마·%p 세 가지를 모두 잡지 못함"
정상 = f"거래액은 {data['계산지표']['총거래액']:,}억 원으로 전월 대비 {data['계산지표']['전월대비증감률']}% 증가하였다."
assert check_formatting_errors(정상) == [], "정상 문장에서 오류가 나옴"

# ③ 전체 수치 교차 검증
print("교차 검증(정상):", cross_check_all_numbers(정상, data))
assert cross_check_all_numbers(정상, data)["통과"] is True
틀림 = cross_check_all_numbers(정상 + " 상위 세 품목이 전체의 82.0%를 차지하였다.", data)
print("교차 검증(파생 수치 추가):", 틀림)
assert 틀림 == {"통과": False, "불일치수치": ["82.0"]}
print("현재 초안의 자동 검수:", check_formatting_errors(draft) or "표기 문제 없음", "|", cross_check_all_numbers(draft, data))

# ④ 문체 통일과 AI 감수 (가짜 응답)
받은 = []
응답 = iter([draft,
            '[{"유형": "문체 불일치", "위치": "본문 2단락", "지적사항": "개조식 표현이 남아 있음"}]',
            '[{"유형": "과장된 표현", "위치": "부제", "지적사항": "잘린 응답'])
def fake_create(**kwargs):
    받은.append(kwargs)
    return NS(stop_reason="end_turn", content=[NS(type="text", text=next(응답))])
W.client.messages.create = fake_create
최종본 = W.unify_style(draft)
assert "변경" in 받은[0]["messages"][0]["content"] and draft in 받은[0]["messages"][0]["content"]
지적 = review_press_release(최종본, data)
assert 지적[0]["유형"] == "문체 불일치"
assert "계산지표" in 받은[1]["messages"][0]["content"] and "통계해석결과" in 받은[1]["messages"][0]["content"], "근거자료 누락"
실패 = review_press_release(최종본, data)
print("감수 파싱 실패 시:", 실패)
assert 실패[0]["유형"] == "감수 응답 파싱 실패"
print("Ch09 OK — 문체 통일·3단계 검수 구조 검증 통과 (실제 API 호출은 8절)")
