"""8차 세션: 진짜 원자료(표본매출/이력/메모 시트) 입력 단위 테스트.
PLAN_raw_data_redesign.md 참고."""
import pandas as pd
import pytest

from modules.pet_input import load_raw_practice_input


def _write_valid_xlsx(path):
    표본매출_df = pd.DataFrame({
        "업체명": ["A", "B"],
        "품목": ["사료", "간식"],
        "매출액": [1000, 500],
    })
    이력_df = pd.DataFrame({"연월": ["2026-02"], "총거래액": [1400]})
    메모_df = pd.DataFrame({
        "연월": ["2026-03"], "제목": ["테스트 보도자료"], "메모": ["  테스트   메모   내용  "],
    })
    with pd.ExcelWriter(path) as writer:
        표본매출_df.to_excel(writer, sheet_name="표본매출", index=False)
        이력_df.to_excel(writer, sheet_name="이력", index=False)
        메모_df.to_excel(writer, sheet_name="메모", index=False)


def test_load_raw_practice_input_reads_all_three_sheets(tmp_path):
    path = tmp_path / "sample.xlsx"
    _write_valid_xlsx(path)

    raw = load_raw_practice_input(str(path))

    assert raw["제목"] == "테스트 보도자료"
    assert raw["연월"] == "2026-03"
    assert "메모" in raw["원문"]
    assert raw["표본매출"] == [
        {"업체명": "A", "품목": "사료", "매출액": 1000.0},
        {"업체명": "B", "품목": "간식", "매출액": 500.0},
    ]
    assert raw["이력"] == [{"연월": "2026-02", "값": 1400.0}]


def test_load_raw_practice_input_values_are_plain_python_types(tmp_path):
    """pandas가 만드는 numpy 스칼라가 그대로 남아있으면 나중에 review.py의
    json.dumps에서 직렬화 오류가 나므로, 순수 파이썬 타입인지 확인한다."""
    path = tmp_path / "sample.xlsx"
    _write_valid_xlsx(path)

    raw = load_raw_practice_input(str(path))

    assert type(raw["표본매출"][0]["매출액"]) is float
    assert type(raw["이력"][0]["값"]) is float


def test_load_raw_practice_input_raises_on_missing_sheet(tmp_path):
    path = tmp_path / "incomplete.xlsx"
    pd.DataFrame({"업체명": ["A"], "품목": ["사료"], "매출액": [100]}).to_excel(path, index=False)

    with pytest.raises(ValueError, match="필수 시트"):
        load_raw_practice_input(str(path))
