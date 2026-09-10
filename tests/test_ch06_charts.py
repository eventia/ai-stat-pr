import os

import pandas as pd

from modules.charts import (
    build_visual_descriptions,
    generate_chart_description,
    generate_table_description,
)

품목_df = pd.DataFrame({
    "품목": ["의류", "가전", "식품", "생활용품", "기타"],
    "당월거래액": [65000, 52000, 48000, 26250, 10000],
    "비중": [32.4, 25.9, 23.9, 13.1, 5.0],
    "순위": [1, 2, 3, 4, 5],
})


def test_generate_chart_description_bar():
    desc = generate_chart_description("bar", 품목_df)
    assert "의류" in desc and "65,000억 원" in desc
    assert "기타" in desc  # 최하위 항목 언급


def test_generate_chart_description_pie():
    desc = generate_chart_description("pie", 품목_df)
    assert "32.4%" in desc


def test_generate_chart_description_line():
    line_df = pd.DataFrame({
        "연월": ["2025-11", "2025-12", "2026-01"],
        "거래액": [190000, 198276, 201250],
    })
    desc = generate_chart_description("line", line_df)
    assert "증가" in desc
    assert "2026-01" in desc


def test_generate_chart_description_line_always_names_a_subject():
    """실제 실습 중 재현된 버그의 회귀 테스트: 이 문장에 주어가 없으면(예: "2024-03부터
    ... 증가세를 보이고 있으며...") 8차시 expand_to_paragraph가 본문으로 확장할 때
    LLM이 "디지털 콘텐츠 시장 규모는..."처럼 엉뚱한 주제를 지어내는 환각이 실제로
    관찰되었다. 주어(지표명)가 항상 문장에 포함되어야 한다."""
    line_df = pd.DataFrame({
        "연월": ["2025-11", "2025-12", "2026-01"],
        "거래액": [190000, 198276, 201250],
    })
    기본_주어_문장 = generate_chart_description("line", line_df)
    assert 기본_주어_문장.startswith("총거래액")  # label 생략 시 modules/config.PRIMARY_INDICATOR로 대체

    커스텀_주어_문장 = generate_chart_description("line", line_df, label="반려동물용품 거래액")
    assert 커스텀_주어_문장.startswith("반려동물용품 거래액")


def test_generate_table_description():
    desc = generate_table_description(품목_df)
    assert "1위 의류" in desc


def test_build_visual_descriptions_creates_image_file(sample_data, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = build_visual_descriptions(sample_data)
    assert len(result) == 2
    for item in result:
        assert os.path.exists(item["이미지경로"])
        assert item["소주제"] in ("품목별 동향", "품목별 비중")
        assert item["설명문"]  # 설명문이 비어있지 않아야 함


def test_build_visual_descriptions_adds_line_chart_when_history_present(sample_data, tmp_path, monkeypatch):
    """검토 보고서(REVIEW_Ch02-10.md, 5번 개선 제안) 회귀 테스트: 꺾은선그래프는
    코드는 있었지만 파이프라인에서 도달 불가능한 고아 기능이었다. 월별이력이
    주어지면 실제로 세 번째(시계열 동향) 항목이 생성되어야 한다."""
    monkeypatch.chdir(tmp_path)
    data = dict(sample_data)
    data["월별이력"] = [
        {"연월": "2025-11", "값": 190000},
        {"연월": "2025-12", "값": 198276},
        {"연월": "2026-01", "값": 201250},
    ]
    result = build_visual_descriptions(data)
    assert len(result) == 3
    시계열 = [item for item in result if item["소주제"] == "시계열 동향"][0]
    assert 시계열["그래프유형"] == "꺾은선그래프"
    assert os.path.exists(시계열["이미지경로"])
    assert "증가" in 시계열["설명문"]
