# 검증 Ch08 — 가짜 응답으로 구조 확인 (비용 0)
import sys, json
from types import SimpleNamespace as NS
sys.path.insert(0, ".")
import mywork.write as W
from mywork.review import verify_numbers

with open("mywork/press_data.json", encoding="utf-8") as f:
    data = json.load(f)
assert len(data["시각자료설명"]) == 3, "6차시 시각자료설명이 3개가 아님"

받은_프롬프트 = []
응답 = iter(["품목별로는 의류가 65,000억 원으로 가장 많이 거래되었으며, 가전이 52,000억 원으로 그 뒤를 이었다.",
            "   ",   # 빈 응답 — 건너뛰어야 함
            "온라인쇼핑 거래액은 2025년 1월부터 증가세를 보였으며, 2026년 1월에 201,250억 원을 기록하였다."])
def fake_create(**kwargs):
    받은_프롬프트.append(kwargs["messages"][0]["content"])
    return NS(stop_reason="end_turn", content=[NS(type="text", text=next(응답))])
W.client.messages.create = fake_create

본문 = W.generate_body_paragraphs(data)
for p in 본문:
    print(f"[{p['소주제']}] {p['내용']}")

# ① 프롬프트 조건
첫_프롬프트 = 받은_프롬프트[0]
assert "품목별 동향" in 첫_프롬프트 and data["시각자료설명"][0]["설명문"] in 첫_프롬프트
assert "두괄식" in 첫_프롬프트 and "계산" in 첫_프롬프트, "두괄식·새 계산 금지 조건이 없음"
# ② 빈 응답은 건너뛰고, 연결어는 실제로 추가된 단락 기준
assert [p["소주제"] for p in 본문] == ["품목별 동향", "시계열 동향"], "빈 응답을 건너뛰지 않음"
assert 본문[0]["내용"].startswith("품목별로는") and 본문[1]["내용"].startswith("한편, 온라인쇼핑"), "연결어 규칙 확인"
# ③ 조립과 수치 검증
전체 = W.assemble_body(본문)
assert 전체.count("\n\n") == 1
for p in 본문:
    assert verify_numbers(p["내용"], data), p["내용"]
print("Ch08 OK — 본문 구조 검증 통과 (실제 API 호출은 8절)")
