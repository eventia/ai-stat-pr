"""10차시 캡스톤: API 키 없이도 전체 배선(연결)이 올바른지 목업으로 검증한다.
실제 문장 품질은 이 테스트로 확인할 수 없으며, 반드시 진짜 ANTHROPIC_API_KEY로도 별도 확인해야 한다.
"""
import json
import os

import pandas as pd
import pytest

import modules.write as write_module
import modules.review as review_module


class _FakeContentBlock:
    def __init__(self, text):
        self.text = text


class _FakeMessage:
    def __init__(self, text):
        self.content = [_FakeContentBlock(text)]


def _fake_create(*, model, max_tokens, messages, system=None, **kwargs):
    """system/user 프롬프트 내용을 보고 이 호출이 어떤 단계인지 추론해 적절한 가짜 응답을 만든다."""
    prompt = messages[0]["content"]

    if "제목" in prompt and "부제" in prompt and "리드문" in prompt:
        return _FakeMessage(json.dumps({
            "제목": "1월 온라인쇼핑 거래액, 역대 최대",
            "부제": "모바일쇼핑 비중 78%로 지속 확대",
            "리드문": "통계청은 2026년 1월 온라인쇼핑 거래액이 201250억 원으로 집계되었다고 밝혔다. "
                     "이는 전월 대비 1.5%, 전년동월대비 8.7% 증가한 수치이다.",
        }, ensure_ascii=False))

    if "본문 한 단락" in prompt:
        return _FakeMessage("품목별로는 의류가 65000억 원으로 가장 많이 거래되어 1위를 차지하였다.")

    if "표준 문체로 통일" in prompt:
        return _FakeMessage(prompt.split("초안: ", 1)[-1])  # 원문을 그대로 돌려줘 수치 보존 확인

    if "전문 감수자" in prompt:
        return _FakeMessage(json.dumps([], ensure_ascii=False))

    return _FakeMessage("{}")


@pytest.fixture(autouse=True)
def patch_anthropic_client(monkeypatch):
    monkeypatch.setattr(write_module.client.messages, "create", _fake_create)


def test_main_pipeline_runs_end_to_end_with_mocked_llm(sample_data, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    # xlsx 없이, load_input이 만들 법한 raw dict를 직접 구성해 clean_and_structure부터 검증
    from modules.clean import clean_and_structure
    from modules.nlp import analyze_document
    from modules.stats import add_calculated_indicators
    from modules.charts import build_visual_descriptions
    from modules.write import generate_headline_set, generate_body_paragraphs
    from modules.review import (
        assemble_full_text, unify_style,
        check_formatting_errors, cross_check_all_numbers, review_press_release,
    )
    from modules.io import save_final_document

    raw = {
        "제목": sample_data["문서정보"]["제목"],
        "계산지표": sample_data["계산지표"],
        "원문": sample_data["원문"],
        "품목별지표": sample_data["품목별지표"],
    }

    data = clean_and_structure(raw)
    data = analyze_document(data["원문"], data)
    data = add_calculated_indicators(data)
    assert "품목별지표" in data
    data["시각자료설명"] = build_visual_descriptions(data)

    data["헤드라인"] = generate_headline_set(data)
    assert set(data["헤드라인"].keys()) == {"제목", "부제", "리드문"}

    data["본문"] = generate_body_paragraphs(data)
    assert len(data["본문"]) == len(data["시각자료설명"])

    data["최종본"] = unify_style(assemble_full_text(data))
    data["검수결과"] = {
        "표기오류검사": check_formatting_errors(data["최종본"]),
        "수치교차검증": cross_check_all_numbers(data["최종본"], data),
        "AI감수지적사항": review_press_release(data["최종본"], data),
    }
    save_final_document(data)

    assert data["검수결과"]["수치교차검증"]["통과"] is True
    assert os.path.exists(f"output/{data['문서정보']['제목']}.txt")


def test_main_module_entrypoint_runs_end_to_end_with_history_sheet(sample_data, tmp_path, monkeypatch):
    """main.py의 실제 main() 함수를 (재구현이 아니라) 직접 호출해 검증한다.
    7차 세션에서 추가된 '이력' 시트 기반 자동 계산과 3~4차시 요약 연결이
    main.py 배선에 실제로 반영되었는지 확인하는 회귀 테스트."""
    monkeypatch.chdir(tmp_path)

    요약_df = pd.DataFrame({
        "연월": ["2026-01"],
        "총거래액": [sample_data["계산지표"]["총거래액"]],
        "전월대비증감률": [sample_data["계산지표"]["전월대비증감률"]],
        "전년동월대비증감률": [sample_data["계산지표"]["전년동월대비증감률"]],
        "원문": [sample_data["원문"]],
        "품목별지표": [json.dumps(sample_data["품목별지표"], ensure_ascii=False)],
    })
    이력_df = pd.DataFrame({
        "연월": ["2025-01", "2025-11", "2025-12"],
        "총거래액": [189430, 193000, 198276],
    })
    xlsx_path = tmp_path / "sample.xlsx"
    with pd.ExcelWriter(xlsx_path) as writer:
        요약_df.to_excel(writer, sheet_name="요약", index=False)
        이력_df.to_excel(writer, sheet_name="이력", index=False)

    import main as main_module

    결과 = main_module.main(str(xlsx_path))

    assert 결과["역대최대여부"] is True  # 이력 시트만으로 자동 계산됨 (사람이 입력 안 함)
    assert "요약결과" in 결과  # 4차시 generate_summary가 실제로 호출되어 결과가 남음
    assert any(item["소주제"] == "시계열 동향" for item in 결과["시각자료설명"])  # line 차트 활성화
    assert 결과["검수결과"]["수치교차검증"]["통과"] is True
