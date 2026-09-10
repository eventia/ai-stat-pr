"""7차시: xlsx/PDF 원자료 입력, 10차시: 최종 문서 저장."""
import json
import os

import pandas as pd
import pdfplumber

from modules.config import REQUIRED_FIELDS
from modules.stats import derive_history_indicators


def load_input(파일경로: str) -> dict:
    """확장자에 따라 xlsx 또는 PDF 원자료를 읽어 raw dict로 반환한다."""
    확장자 = os.path.splitext(파일경로)[1].lower()

    if 확장자 == ".xlsx":
        엑셀 = pd.ExcelFile(파일경로)
        df = pd.read_excel(엑셀, sheet_name=엑셀.sheet_names[0])
        row = df.iloc[0].to_dict()
        # "제목" 열이 있으면 그대로 쓰고, 없으면(기존 온라인쇼핑 동향 샘플과의 하위 호환)
        # 예전과 동일한 기본값으로 채운다 — 다른 통계표(예: 반려동물용품 동향)를 붙일 때
        # 마다 "온라인쇼핑 동향"이라는 제목이 그대로 찍히던 문제를 수정했다.
        raw = {
            "제목": row.get("제목") or f"{row.get('연월', '')} 온라인쇼핑 동향",
            "계산지표": {field: row[field] for field in REQUIRED_FIELDS},
            "원문": row.get("원문", ""),
        }
        # xlsx 셀은 스칼라 값만 담을 수 있으므로, 리스트/객체 형태의 값은
        # JSON 문자열로 저장해 두었다가 여기서 파싱한다.
        if "품목별지표" in df.columns:
            값 = row["품목별지표"]
            raw["품목별지표"] = json.loads(값) if isinstance(값, str) else 값

        # 검토 보고서(REVIEW_Ch02-10.md, A-1) 대응: "역대최대여부"/"최근3개월증감률"을
        # 담당자가 과거 자료를 보고 직접 입력하지 않아도 되도록, xlsx에 "이력" 시트
        # (연월, 총거래액 등 REQUIRED_FIELDS[0] 컬럼)가 있으면 자동으로 계산한다.
        # 명시적으로 "역대최대여부"/"최근3개월증감률" 열이 있으면 그 값을 우선한다
        # (수작업으로 다른 판단을 반영하고 싶은 경우를 덮어쓰지 않기 위함).
        if "이력" in 엑셀.sheet_names:
            이력_df = pd.read_excel(엑셀, sheet_name="이력")
            history = [
                {"연월": str(r["연월"]), "값": r[REQUIRED_FIELDS[0]]}
                for _, r in 이력_df.iterrows()
            ]
            raw["월별이력"] = history + [
                {"연월": str(row.get("연월", "")), "값": row[REQUIRED_FIELDS[0]]}
            ]
            계산됨 = derive_history_indicators(history, str(row.get("연월", "")), row[REQUIRED_FIELDS[0]])
            raw.setdefault("역대최대여부", 계산됨["역대최대여부"])
            raw.setdefault("최근3개월증감률", 계산됨["최근3개월증감률"])

        if "역대최대여부" in df.columns:
            raw["역대최대여부"] = bool(row["역대최대여부"])
        if "최근3개월증감률" in df.columns:
            값 = row["최근3개월증감률"]
            raw["최근3개월증감률"] = json.loads(값) if isinstance(값, str) else 값
        return raw
    elif 확장자 == ".pdf":
        with pdfplumber.open(파일경로) as pdf:
            full_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        return {"원문": full_text}
    else:
        raise ValueError(f"지원하지 않는 파일 형식입니다: {확장자}")


def save_final_document(data: dict):
    os.makedirs("output", exist_ok=True)
    with open(f"output/{data['문서정보']['제목']}.txt", "w", encoding="utf-8") as f:
        f.write(data["최종본"])
    # 실무에서는 python-docx, hwpx 라이브러리 등을 활용해
    # 공식 보도자료 서식(제목, 로고, 표, 그래프 삽입)에 맞춰 최종 변환
