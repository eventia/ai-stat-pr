"""10차시(제공 파일): 검수를 마친 최종 보도자료를 PDF와 HWPX(한글) 파일로 저장한다.

공식 서식 변환은 실무 후처리 단계이므로 Claude Code로 만들지 않고 이 파일을 그대로 복사해 사용한다."""
import os
import re
from xml.sax.saxutils import escape

from hwpx import HwpxDocument
from PIL import Image as PILImage
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, KeepTogether, Paragraph, SimpleDocTemplate, Spacer

_FONT_NAME = "KoreanFont"
_MARGIN = 2.5 * cm
_MAX_IMAGE_HEIGHT = 10 * cm
_HWPX_IMAGE_WIDTH_MM = 150.0
_HWPX_MAX_IMAGE_HEIGHT_MM = 100.0


def _find_korean_font() -> str:
    """한글을 그릴 수 있는 TTF 폰트 경로를 찾는다. .env의 KOREAN_FONT_PATH가 있으면 우선한다."""
    후보 = [
        os.getenv("KOREAN_FONT_PATH", ""),
        r"C:\Windows\Fonts\malgun.ttf",
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/Library/Fonts/NanumGothic.ttf",
    ]
    for 경로 in 후보:
        if 경로 and os.path.exists(경로):
            return 경로
    raise RuntimeError(
        "한글 TTF 폰트를 찾을 수 없어 PDF를 만들 수 없습니다. "
        ".env에 KOREAN_FONT_PATH=<한글 .ttf 파일 경로>를 지정하세요."
    )


def _safe_stem(data: dict) -> str:
    """제목을 파일명으로 쓸 수 있게 Windows 금지 문자를 '_'로 바꾼다."""
    제목 = re.sub(r'[\\/:*?"<>|]', "_", data["문서정보"]["제목"]).strip()
    상태 = data.get("문서상태")
    return f"{제목}_{상태}" if 상태 else 제목


def _collect(data: dict) -> dict:
    """PDF와 HWPX가 함께 쓰는 문서 구성 요소(제목·부제·본문 단락·그림)를 표준 데이터에서 뽑는다."""
    헤드라인 = data.get("헤드라인", {})
    단락 = [" ".join(p.split()) for p in re.split(r"\n\s*\n", data["최종본"]) if p.strip()]

    # 막대·원형 그래프처럼 한 이미지를 여러 소주제가 공유하므로 이미지 경로 기준으로 묶는다.
    소주제_by_경로 = {}
    for 항목 in data.get("시각자료설명", []):
        경로 = 항목.get("이미지경로")
        if 경로 and os.path.exists(경로):
            소주제_by_경로.setdefault(경로, []).append(항목["소주제"])

    return {
        "제목": 헤드라인.get("제목") or data["문서정보"]["제목"],
        "부제": 헤드라인.get("부제", ""),
        "단락": 단락,
        "그림": [(경로, " · ".join(소주제)) for 경로, 소주제 in 소주제_by_경로.items()],
    }


def save_pdf(data: dict, output_dir: str = "output") -> str:
    os.makedirs(output_dir, exist_ok=True)
    pdfmetrics.registerFont(TTFont(_FONT_NAME, _find_korean_font()))
    문서 = _collect(data)
    경로 = os.path.join(output_dir, f"{_safe_stem(data)}.pdf")

    제목_스타일 = ParagraphStyle("제목", fontName=_FONT_NAME, fontSize=20, leading=28, spaceAfter=8, wordWrap="CJK")
    부제_스타일 = ParagraphStyle("부제", fontName=_FONT_NAME, fontSize=13, leading=20, spaceAfter=18,
                             textColor=HexColor("#555555"), wordWrap="CJK")
    본문_스타일 = ParagraphStyle("본문", fontName=_FONT_NAME, fontSize=11, leading=20, spaceAfter=10, wordWrap="CJK")
    캡션_스타일 = ParagraphStyle("캡션", fontName=_FONT_NAME, fontSize=9, leading=13, alignment=TA_CENTER,
                             textColor=HexColor("#555555"), wordWrap="CJK")

    story = [Paragraph(escape(문서["제목"]), 제목_스타일)]
    if 문서["부제"]:
        story.append(Paragraph(escape(문서["부제"]), 부제_스타일))
    story += [Paragraph(escape(p), 본문_스타일) for p in 문서["단락"]]

    최대_너비 = A4[0] - 2 * _MARGIN
    for 그림경로, 캡션 in 문서["그림"]:
        너비px, 높이px = PILImage.open(그림경로).size
        너비 = 최대_너비
        높이 = 너비 * 높이px / 너비px
        if 높이 > _MAX_IMAGE_HEIGHT:
            높이 = _MAX_IMAGE_HEIGHT
            너비 = 높이 * 너비px / 높이px
        story.append(Spacer(1, 8))
        story.append(KeepTogether([Image(그림경로, width=너비, height=높이),
                                   Paragraph(escape(f"[그림] {캡션}"), 캡션_스타일)]))

    SimpleDocTemplate(경로, pagesize=A4, leftMargin=_MARGIN, rightMargin=_MARGIN,
                      topMargin=_MARGIN, bottomMargin=_MARGIN, title=문서["제목"]).build(story)
    return 경로


def save_hwpx(data: dict, output_dir: str = "output") -> str:
    os.makedirs(output_dir, exist_ok=True)
    문서 = _collect(data)
    경로 = os.path.join(output_dir, f"{_safe_stem(data)}.hwpx")

    hwpx = HwpxDocument.new()
    hwpx.add_heading(문서["제목"], level=1)
    # 새 문단이 직전 문단(제목)의 스타일을 물려받지 않도록 inherit_style=False로 바탕글 스타일을 쓴다.
    if 문서["부제"]:
        hwpx.add_paragraph(문서["부제"], inherit_style=False)
    for 단락 in 문서["단락"]:
        hwpx.add_paragraph(단락, inherit_style=False)

    for 그림경로, 캡션 in 문서["그림"]:
        너비px, 높이px = PILImage.open(그림경로).size
        너비mm = _HWPX_IMAGE_WIDTH_MM
        높이mm = 너비mm * 높이px / 너비px
        if 높이mm > _HWPX_MAX_IMAGE_HEIGHT_MM:
            높이mm = _HWPX_MAX_IMAGE_HEIGHT_MM
            너비mm = 높이mm * 너비px / 높이px
        with open(그림경로, "rb") as f:
            hwpx.add_picture(f.read(), os.path.splitext(그림경로)[1].lstrip(".").lower(),
                             width_mm=너비mm, height_mm=높이mm, align="center")
        hwpx.add_paragraph(f"[그림] {캡션}", inherit_style=False)

    hwpx.save_to_path(경로)
    return 경로
