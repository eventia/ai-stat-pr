"""7차시: xlsx·PDF 원자료를 읽어 raw dict로 만든다(정제는 clean_and_structure가 담당)."""
import json
import os

import pandas as pd
import pdfplumber

from mywork.config import PRIMARY_INDICATOR, REQUIRED_FIELDS
from mywork.stats import derive_history_indicators


def _to_python(value):
    return value.item() if hasattr(value, "item") else value


def _maybe_json(value):
    if isinstance(value, str) and value.strip().startswith(("[", "{")):
        return json.loads(value)
    return value


def load_input(파일경로: str) -> dict:
    확장자 = os.path.splitext(파일경로)[1].lower()

    if 확장자 == ".xlsx":
        with pd.ExcelFile(파일경로) as 엑셀:
            df = pd.read_excel(엑셀, sheet_name=엑셀.sheet_names[0], dtype={"연월": str, "공표일자": str})
            row = {k: _to_python(v) for k, v in df.iloc[0].to_dict().items()}
            연월 = str(row["연월"])
            연도, 월 = 연월.split("-")
            raw = {
                "제목": f"{연도}년 {int(월)}월 온라인쇼핑 동향",
                "기준연월": 연월,
                "계산지표": {field: row[field] for field in REQUIRED_FIELDS},
                "원문": row.get("원문", ""),
            }
            for 선택필드 in ["공표일자", "자료출처", "보안등급"]:
                if 선택필드 in row and pd.notna(row[선택필드]):
                    raw[선택필드] = str(row[선택필드])
            for json필드 in ["핵심내용", "품목별지표"]:
                if json필드 in row:
                    raw[json필드] = _maybe_json(row[json필드])

            if "이력" in 엑셀.sheet_names:
                이력_df = pd.read_excel(엑셀, sheet_name="이력", dtype={"연월": str})
                history = [{"연월": str(r["연월"]), "값": _to_python(r[PRIMARY_INDICATOR])} for _, r in 이력_df.iterrows()]
                raw["월별이력"] = history + [{"연월": 연월, "값": row[PRIMARY_INDICATOR]}]
                계산됨 = derive_history_indicators(history, 연월, row[PRIMARY_INDICATOR])
                raw.setdefault("역대최대여부", 계산됨["역대최대여부"])
                raw.setdefault("최근3개월증감률", 계산됨["최근3개월증감률"])
        return raw

    if 확장자 == ".pdf":
        with pdfplumber.open(파일경로) as pdf:
            full_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        return {"원문": full_text}

    raise ValueError(f"지원하지 않는 파일 형식입니다: {확장자}")
