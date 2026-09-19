"""10차시: 최종 보도자료를 PDF·HWPX로 저장하는 modules/export.py 단위 테스트.
LLM·네트워크 없이 실행되며, PDF 테스트는 한글 TTF 폰트가 없는 환경에서는 건너뛴다."""
import os
import re
import zipfile

import pdfplumber
import pytest
from hwpx import HwpxDocument
from PIL import Image

import modules.export as export


@pytest.fixture
def press(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    os.makedirs("images")
    Image.new("RGB", (400, 200), "white").save("images/chart.png")
    return {
        "문서정보": {"제목": "2026년 1월 온라인쇼핑 동향"},
        "헤드라인": {"제목": "1월 온라인쇼핑 거래액, 역대 최대", "부제": "모바일쇼핑 비중 78%로 지속 확대"},
        "최종본": "통계청은 2026년 1월 온라인쇼핑 거래액이 201,250억 원으로 집계되었다고 밝혔다.\n\n"
                 "품목별로는 의류가 65,000억 원으로 가장 많이 거래되었다.",
        "시각자료설명": [
            {"소주제": "품목별 동향", "이미지경로": "images/chart.png"},
            {"소주제": "품목별 비중", "이미지경로": "images/chart.png"},
            {"소주제": "시계열 동향", "이미지경로": "images/missing.png"},
        ],
    }


def test_collect_groups_shared_image_and_skips_missing_files(press):
    문서 = export._collect(press)
    assert 문서["제목"] == "1월 온라인쇼핑 거래액, 역대 최대"
    assert 문서["부제"] == "모바일쇼핑 비중 78%로 지속 확대"
    assert len(문서["단락"]) == 2
    assert 문서["그림"] == [("images/chart.png", "품목별 동향 · 품목별 비중")]


def test_collect_falls_back_to_document_title_without_headline(press):
    del press["헤드라인"]
    문서 = export._collect(press)
    assert 문서["제목"] == "2026년 1월 온라인쇼핑 동향"
    assert 문서["부제"] == ""


def test_safe_stem_replaces_forbidden_filename_characters():
    assert export._safe_stem({"문서정보": {"제목": '2026/01: 동향?'}}) == "2026_01_ 동향_"


def test_save_hwpx_creates_valid_document_with_text_and_image(press, tmp_path):
    경로 = export.save_hwpx(press, "output")
    assert 경로.endswith("2026년 1월 온라인쇼핑 동향.hwpx")

    with zipfile.ZipFile(경로) as z:
        assert z.read("mimetype") == b"application/hwp+zip"
        assert [n for n in z.namelist() if n.startswith("BinData/")] == ["BinData/BIN0001.png"]

    문서 = HwpxDocument.open(경로)
    assert 문서.validate().ok
    본문 = 문서.text.plain()
    assert "1월 온라인쇼핑 거래액, 역대 최대" in 본문
    assert "201,250억 원으로 집계되었다고 밝혔다." in 본문
    assert "[그림] 품목별 동향 · 품목별 비중" in 본문


def test_save_hwpx_body_paragraphs_do_not_inherit_heading_style(press):
    경로 = export.save_hwpx(press, "output")
    with zipfile.ZipFile(경로) as z:
        xml = z.read("Contents/section0.xml").decode("utf-8")
    스타일 = dict((텍스트, 아이디) for 아이디, 텍스트 in
                 re.findall(r'<hp:p [^>]*styleIDRef="(\d+)"[^>]*>(?:(?!</hp:p>).)*?<hp:t>([^<]*)</hp:t>', xml, flags=re.S))
    제목_스타일 = 스타일["1월 온라인쇼핑 거래액, 역대 최대"]
    assert 스타일["모바일쇼핑 비중 78%로 지속 확대"] != 제목_스타일
    assert 스타일["품목별로는 의류가 65,000억 원으로 가장 많이 거래되었다."] != 제목_스타일


def _한글폰트_또는_건너뛰기():
    try:
        export._find_korean_font()
    except RuntimeError:
        pytest.skip("한글 TTF 폰트가 없는 환경")


def test_save_pdf_embeds_korean_text_and_image(press):
    _한글폰트_또는_건너뛰기()
    경로 = export.save_pdf(press, "output")
    assert 경로.endswith("2026년 1월 온라인쇼핑 동향.pdf")
    with open(경로, "rb") as f:
        assert f.read(5) == b"%PDF-"
    with pdfplumber.open(경로) as pdf:
        텍스트 = "\n".join(page.extract_text() for page in pdf.pages)
        그림수 = sum(len(page.images) for page in pdf.pages)
    assert "1월 온라인쇼핑 거래액, 역대 최대" in 텍스트
    assert "201,250억 원으로" in 텍스트
    assert "[그림] 품목별 동향 · 품목별 비중" in 텍스트
    assert 그림수 == 1


def test_save_pdf_escapes_xml_special_characters(press):
    _한글폰트_또는_건너뛰기()
    press["최종본"] = "A&B <거래액> 증가"
    경로 = export.save_pdf(press, "output")
    with pdfplumber.open(경로) as pdf:
        assert "A&B <거래액> 증가" in pdf.pages[0].extract_text()


def test_find_korean_font_raises_clear_error_when_no_font(monkeypatch):
    monkeypatch.delenv("KOREAN_FONT_PATH", raising=False)
    monkeypatch.setattr(export.os.path, "exists", lambda p: False)
    with pytest.raises(RuntimeError, match="KOREAN_FONT_PATH"):
        export._find_korean_font()
