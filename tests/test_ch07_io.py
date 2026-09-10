"""7차시: xlsx/PDF 입력, 최종 문서 저장에 대한 단위 테스트."""
import json
import os

import pandas as pd
import pytest

from modules.io import load_input, save_final_document


def test_load_input_xlsx_basic_columns_only(tmp_path):
    df = pd.DataFrame({
        "연월": ["2026-01"],
        "총거래액": [201250],
        "전월대비증감률": [1.5],
        "전년동월대비증감률": [8.7],
        "원문": ["샘플 원문"],
    })
    path = tmp_path / "sample.xlsx"
    df.to_excel(path, index=False)

    raw = load_input(str(path))

    assert raw["제목"] == "2026-01 온라인쇼핑 동향"
    assert raw["계산지표"] == {"총거래액": 201250, "전월대비증감률": 1.5, "전년동월대비증감률": 8.7}
    assert raw["원문"] == "샘플 원문"
    assert "품목별지표" not in raw
    assert "역대최대여부" not in raw
    assert "최근3개월증감률" not in raw


def test_load_input_xlsx_parses_json_string_columns(tmp_path):
    """xlsx 셀에는 리스트/불리언을 직접 담을 수 없으므로, JSON 문자열로 저장된
    품목별지표·최근3개월증감률과 불리언 역대최대여부가 올바르게 파싱되는지 확인한다."""
    품목별지표 = [{"품목": "의류", "당월거래액": 65000, "비중": 32.4, "순위": 1}]
    df = pd.DataFrame({
        "연월": ["2026-01"],
        "총거래액": [201250],
        "전월대비증감률": [1.5],
        "전년동월대비증감률": [8.7],
        "역대최대여부": [True],
        "최근3개월증감률": [json.dumps([2.0, 1.8, 1.5])],
        "품목별지표": [json.dumps(품목별지표, ensure_ascii=False)],
        "원문": ["샘플 원문"],
    })
    path = tmp_path / "sample_full.xlsx"
    df.to_excel(path, index=False)

    raw = load_input(str(path))

    assert raw["역대최대여부"] is True
    assert raw["최근3개월증감률"] == [2.0, 1.8, 1.5]
    assert raw["품목별지표"] == 품목별지표


def test_load_input_xlsx_computes_history_indicators_from_history_sheet(tmp_path):
    """검토 보고서(REVIEW_Ch02-10.md, A-1) 대응 회귀 테스트: "이력" 시트가 있으면
    역대최대여부·최근3개월증감률을 담당자가 입력하지 않아도 자동 계산되어야 한다."""
    요약_df = pd.DataFrame({
        "연월": ["2026-01"],
        "총거래액": [201250],
        "전월대비증감률": [1.5],
        "전년동월대비증감률": [8.7],
        "원문": ["샘플 원문"],
    })
    이력_df = pd.DataFrame({
        "연월": ["2025-01", "2025-11", "2025-12"],
        "총거래액": [189430, 193000, 198276],
    })
    path = tmp_path / "sample_with_history.xlsx"
    with pd.ExcelWriter(path) as writer:
        요약_df.to_excel(writer, sheet_name="요약", index=False)
        이력_df.to_excel(writer, sheet_name="이력", index=False)

    raw = load_input(str(path))

    assert raw["역대최대여부"] is True  # 2025-01(189430)보다 2026-01(201250)이 큼
    assert len(raw["최근3개월증감률"]) == 3
    assert "월별이력" in raw


def test_load_input_pdf_extracts_text(tmp_path, monkeypatch):
    """실제 PDF 렌더링 없이도 pdfplumber 연동 로직만 검증하도록 pdfplumber.open을 가짜로 대체한다."""
    import modules.io as io_module

    class _FakePage:
        def __init__(self, text):
            self._text = text

        def extract_text(self):
            return self._text

    class _FakePdf:
        def __init__(self, pages):
            self.pages = pages

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    def _fake_open(path):
        return _FakePdf([_FakePage("첫 페이지 내용"), _FakePage("둘째 페이지 내용")])

    monkeypatch.setattr(io_module.pdfplumber, "open", _fake_open)

    raw = io_module.load_input("dummy.pdf")

    assert raw == {"원문": "첫 페이지 내용\n둘째 페이지 내용"}


def test_load_input_rejects_unsupported_extension(tmp_path):
    path = tmp_path / "sample.txt"
    path.write_text("아무 내용", encoding="utf-8")

    with pytest.raises(ValueError):
        load_input(str(path))


def test_save_final_document_writes_utf8_text_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    data = {"문서정보": {"제목": "테스트 보도자료"}, "최종본": "본문 내용입니다."}

    save_final_document(data)

    saved_path = tmp_path / "output" / "테스트 보도자료.txt"
    assert saved_path.exists()
    assert saved_path.read_text(encoding="utf-8") == "본문 내용입니다."
