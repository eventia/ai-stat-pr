"""8차 세션: main_practice.py 전체 배선 검증 (API 키 없이 LLM 목업).
실제 문장 품질은 이 테스트로 확인할 수 없으며, 반드시 진짜 ANTHROPIC_API_KEY로도
별도 확인해야 한다 (scripts/run_practice_stepbystep.py 또는 main_practice.py 직접 실행).
"""
import json
import os

import pandas as pd
import pytest

import modules.write as write_module


class _FakeContentBlock:
    def __init__(self, text):
        self.text = text


class _FakeMessage:
    def __init__(self, text):
        self.content = [_FakeContentBlock(text)]


def _fake_create(*, model, max_tokens, messages, system=None, **kwargs):
    prompt = messages[0]["content"]

    if "제목" in prompt and "부제" in prompt and "리드문" in prompt:
        return _FakeMessage(json.dumps({
            "제목": "3월 반려동물용품 거래액 감소",
            "부제": "3개월 연속 감소세",
            "리드문": "반려동물용품 거래액은 49700억 원을 기록하였다. 전월 대비 -6.2%, "
                     "전년동월대비 -4.4% 감소한 수치이다.",
        }, ensure_ascii=False))
    if "본문 한 단락" in prompt:
        return _FakeMessage("사료가 22000억 원으로 가장 높은 비중을 차지하였다.")
    if "표준 문체로 통일" in prompt:
        return _FakeMessage(prompt.split("초안: ", 1)[-1])
    if "전문 감수자" in prompt:
        return _FakeMessage(json.dumps([], ensure_ascii=False))
    return _FakeMessage("{}")


@pytest.fixture(autouse=True)
def patch_anthropic_client(monkeypatch):
    monkeypatch.setattr(write_module.client.messages, "create", _fake_create)


def _write_practice_xlsx(path):
    표본매출_df = pd.DataFrame({
        "업체명": ["A", "B", "C", "D", "E"],
        "품목": ["사료", "간식", "장난감", "위생용품", "기타"],
        "매출액": [22000, 12000, 8000, 5200, 2500],
    })
    이력_df = pd.DataFrame({
        "연월": ["2024-03", "2025-03", "2025-11", "2025-12", "2026-01", "2026-02"],
        "총거래액": [45000, 52000, 61000, 58000, 55000, 53000],
    })
    메모_df = pd.DataFrame({
        "연월": ["2026-03"],
        "제목": ["2026년 3월 반려동물용품 온라인 거래 동향"],
        "메모": ["3월 한 달간 사료 프로모션을 진행함. 장난감 신제품 출시가 연기됨."],
    })
    with pd.ExcelWriter(path) as writer:
        표본매출_df.to_excel(writer, sheet_name="표본매출", index=False)
        이력_df.to_excel(writer, sheet_name="이력", index=False)
        메모_df.to_excel(writer, sheet_name="메모", index=False)


def test_main_practice_runs_end_to_end_from_raw_sample_sales(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    xlsx_path = tmp_path / "sample.xlsx"
    _write_practice_xlsx(xlsx_path)

    import main_practice

    결과 = main_practice.main(str(xlsx_path))

    # 계산지표·품목별지표가 원자료로부터 실제로 "계산"되었는지 확인 — 입력 파일
    # 어디에도 이 숫자들이 미리 들어있지 않았다.
    assert 결과["계산지표"]["총거래액"] == 49700
    assert 결과["계산지표"]["전월대비증감률"] == -6.2
    assert 결과["역대최대여부"] is False
    assert len(결과["품목별지표"]) == 5
    assert any(item["소주제"] == "시계열 동향" for item in 결과["시각자료설명"])
    assert set(결과["헤드라인"].keys()) == {"제목", "부제", "리드문"}
    assert 결과["검수결과"]["수치교차검증"]["통과"] is True
    assert os.path.exists(f"output/{결과['문서정보']['제목']}.txt")
