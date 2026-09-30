"""2차시: 원자료를 정제·표준화·구조화해 표준 데이터(JSON 구조)로 만든다."""
import copy
import re

from mywork.config import INDICATOR_NAME

PASS_THROUGH_FIELDS = ["품목별지표", "월별이력", "역대최대여부", "최근3개월증감률"]


def mask_sensitive_info(text: str) -> str:
    text = re.sub(r"\d{6}-\d{7}", "******-*******", text)
    text = re.sub(r"01[016789]-\d{3,4}-\d{4}", "010-****-****", text)
    return text


def standardize_date(value: str) -> str:
    match = re.search(r"(\d{4})\D+(\d{1,2})\D+(\d{1,2})", str(value))
    if not match:
        return str(value)
    year, month, day = match.groups()
    return f"{year}-{int(month):02d}-{int(day):02d}"


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s*\(주:[^)]*\)", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"(\d)억원", r"\1억 원", text)
    text = re.sub(r"(\d)백만원", r"\1백만 원", text)
    text = text.replace("전월대비", "전월 대비")
    text = text.replace("하였음.", "하였다.")
    return mask_sensitive_info(text)


def clean_and_structure(raw: dict) -> dict:
    data = {
        "문서정보": {
            "제목": raw.get("제목", ""),
            "공표일자": standardize_date(raw.get("공표일자", "")),
            "자료출처": raw.get("자료출처", "공공데이터포털 Open API"),
            "기준연월": raw.get("기준연월", ""),
            "지표명": raw.get("지표명", INDICATOR_NAME),
            "보안등급": raw.get("보안등급", "미확인"),
        },
        "계산지표": copy.deepcopy(raw.get("계산지표", {})),
        "핵심내용": copy.deepcopy(raw.get("핵심내용", [])),
        "원문": clean_text(raw.get("원문", "")),
    }
    for 필드 in PASS_THROUGH_FIELDS:
        if 필드 in raw:
            data[필드] = copy.deepcopy(raw[필드])
    return data


# ---- 10차시: 외부 LLM 호출 전 보안 전처리 ----
def check_data_grade(data: dict) -> None:
    등급 = data["문서정보"].get("보안등급", "미확인")
    if 등급 != "공개":
        raise PermissionError(f"보안등급이 '{등급}'인 자료는 외부 AI API로 보낼 수 없습니다. (공개 자료만 허용)")


def mask_personal_info(data: dict) -> dict:
    data["원문"] = mask_sensitive_info(data["원문"])
    return data
