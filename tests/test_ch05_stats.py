import pandas as pd

from modules.stats import (
    add_calculated_indicators,
    build_interpretation_sentences,
    check_percent_unit,
    derive_history_indicators,
    detect_special_points,
    generate_interpretation,
)


def test_detect_special_points_record_high_and_yoy():
    points = detect_special_points(momRate=1.5, yoyRate=8.7, is_record_high=True)
    assert "역대 최대치 경신" in points
    assert "전년동월 대비 큰 폭 증가" in points
    assert "전월 대비" not in "".join(points)  # momRate=1.5는 5% 미만이라 큰 폭 아님


def test_detect_special_points_consecutive_trend():
    points = detect_special_points(momRate=1.0, yoyRate=1.0, is_record_high=False,
                                    recent_momRates=[2.0, 1.8, 1.5])
    assert "최근 3개월 연속 증가세" in points


def test_pandas_pct_change_matches_manual_momrate():
    df = pd.DataFrame({"연월": ["2025-12", "2026-01"], "거래액": [198276, 201250]})
    df["전월대비증감률"] = df["거래액"].pct_change() * 100
    assert round(df["전월대비증감률"].iloc[-1], 1) == 1.5


def test_generate_interpretation_fills_template():
    sentence = generate_interpretation("온라인쇼핑 거래액", 201250, "억 원", "역대 최대치 경신")
    assert "201250억 원" in sentence
    assert "역대 최대치" in sentence


def test_check_percent_unit_flags_pp_confusion():
    assert check_percent_unit("전년동월 대비 8.7% 증가", is_rate_of_rate=False) is True
    assert check_percent_unit("전년동월 대비 8.7%p 증가", is_rate_of_rate=False) is False
    assert check_percent_unit("비중이 3.0%p 확대", is_rate_of_rate=True) is True


def test_add_calculated_indicators_populates_interpretation(sample_data):
    result = add_calculated_indicators(sample_data)
    assert "통계해석결과" in result
    assert "역대 최대치 경신" in result["통계해석결과"]["특이점목록"]
    assert len(result["통계해석결과"]["해석문장"]) > 0


def test_add_calculated_indicators_generates_sentence_for_decrease(sample_data):
    """검토 보고서(REVIEW_Ch02-10.md, A-2)에서 지적된 결함에 대한 회귀 테스트.
    감소 방향 특이점은 감지는 되지만 해석문장으로 연결되지 않는 결함이 있었다."""
    data = dict(sample_data)
    data["계산지표"] = dict(data["계산지표"])
    data["계산지표"]["전월대비증감률"] = -6.0
    data["계산지표"]["전년동월대비증감률"] = -7.0
    data["역대최대여부"] = False

    result = add_calculated_indicators(data)
    특이점 = result["통계해석결과"]["특이점목록"]
    해석문장 = " ".join(result["통계해석결과"]["해석문장"])

    assert "전월 대비 큰 폭 감소" in 특이점
    assert "전년동월 대비 큰 폭 감소" in 특이점
    assert "6.0% 감소" in 해석문장
    assert "7.0% 감소" in 해석문장
    assert "-" not in 해석문장  # 부호가 그대로 남아 이중 부정(예: "-6% 감소")이 되면 안 된다


def test_add_calculated_indicators_generates_sentence_for_consecutive_decrease(sample_data):
    data = dict(sample_data)
    data["계산지표"] = dict(data["계산지표"])
    data["계산지표"]["전월대비증감률"] = 1.0
    data["계산지표"]["전년동월대비증감률"] = 1.0
    data["역대최대여부"] = False
    data["최근3개월증감률"] = [-1.0, -1.2, -0.8]

    result = add_calculated_indicators(data)
    assert "최근 3개월 연속 감소세" in result["통계해석결과"]["특이점목록"]
    assert any("연속 감소세" in s for s in result["통계해석결과"]["해석문장"])


def test_derive_history_indicators_detects_record_high_for_same_month():
    history = [
        {"연월": "2024-01", "값": 175320},
        {"연월": "2025-01", "값": 189430},
        {"연월": "2025-12", "값": 300000},  # 다른 달이므로 비교 대상에서 제외되어야 함
    ]
    result = derive_history_indicators(history, "2026-01", 201250)
    assert result["역대최대여부"] is True


def test_derive_history_indicators_detects_not_record_high():
    history = [{"연월": "2025-01", "값": 250000}]
    result = derive_history_indicators(history, "2026-01", 201250)
    assert result["역대최대여부"] is False


def test_derive_history_indicators_computes_recent_three_month_rates():
    history = [
        {"연월": "2025-10", "값": 190000},
        {"연월": "2025-11", "값": 193000},
        {"연월": "2025-12", "값": 198276},
    ]
    result = derive_history_indicators(history, "2026-01", 201250)
    assert len(result["최근3개월증감률"]) == 3
    assert all(r > 0 for r in result["최근3개월증감률"])


def test_derive_history_indicators_with_no_history_defaults_to_record_high():
    result = derive_history_indicators([], "2026-01", 100)
    assert result["역대최대여부"] is True
    assert result["최근3개월증감률"] == []
    assert result["전월대비증감률"] is None
    assert result["전년동월대비증감률"] is None


def test_derive_history_indicators_computes_mom_and_yoy_rates_from_raw_history():
    """8차 세션(PLAN_raw_data_redesign.md): 전월대비/전년동월대비증감률도 더 이상
    사람이 미리 계산해서 넣는 값이 아니라, 이력(월별 총액)만으로 이 함수가 계산해야
    한다. 2026-02(53000)과 2025-03(52000)만 있으면 2026-03의 두 증감률이 계산된다."""
    history = [
        {"연월": "2025-03", "값": 52000},
        {"연월": "2026-02", "값": 53000},
    ]
    result = derive_history_indicators(history, "2026-03", 49700)
    assert result["전월대비증감률"] == -6.2
    assert result["전년동월대비증감률"] == -4.4


def test_derive_history_indicators_returns_none_when_comparison_month_missing():
    """전월/전년동월 데이터가 이력에 없으면 0이나 임의값으로 조용히 채우지 않고
    None을 반환해, 호출부(pet_stats.build_indicators)가 명시적으로 처리하게 한다."""
    history = [{"연월": "2025-01", "값": 100000}]  # 전월도 전년동월도 아님
    result = derive_history_indicators(history, "2026-03", 49700)
    assert result["전월대비증감률"] is None
    assert result["전년동월대비증감률"] is None


def test_build_interpretation_sentences_matches_add_calculated_indicators_output(sample_data):
    """add_calculated_indicators가 위임하는 build_interpretation_sentences가 실제로
    같은 결과를 내는지 확인 — 8차 세션에서 modules/pet_stats.py와 공유하기 위해
    분리한 함수라, 분리 전후 동작이 달라지면 안 된다."""
    지표 = sample_data["계산지표"]
    특이점 = detect_special_points(
        momRate=지표["전월대비증감률"], yoyRate=지표["전년동월대비증감률"],
        is_record_high=sample_data["역대최대여부"],
        recent_momRates=sample_data["최근3개월증감률"],
    )
    직접_호출 = build_interpretation_sentences(특이점, 지표, "온라인쇼핑 동향".split()[-1])
    통합_호출 = add_calculated_indicators(dict(sample_data))["통계해석결과"]["해석문장"]
    assert 직접_호출 == 통합_호출
