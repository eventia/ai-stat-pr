"""2차시: 텍스트 정제·표준화·구조화."""
import re


def clean_and_structure(raw: dict) -> dict:
    """API 원본 응답 + 비정형 원문(raw['원문'])을 표준 JSON 구조로 변환한다."""
    text = raw.get("원문", "")

    # 1. 정제(Cleaning): 중복 공백, 괄호 주석 제거
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\(주:[^)]*\)", "", text)

    # 2. 표준화(Normalization): 단위 표기 통일(억원 -> 억 원)
    text = re.sub(r"(\d)억원", r"\1억 원", text)
    text = re.sub(r"(\d)백만원", r"\1백만 원", text)

    # 2-1. 개인정보 마스킹: 통계 원문에도 담당자 연락처 등이 섞여 들어올 수 있으므로 항상 적용한다.
    text = mask_sensitive_info(text)

    # 3. 구조화(Structuring): 표준 필드로 라벨링
    표준데이터 = {
        "문서정보": {
            "제목": raw.get("제목", ""),
            "공표일자": raw.get("공표일자", ""),
            "자료출처": raw.get("자료출처", "공공데이터포털 Open API"),
        },
        "계산지표": raw.get("계산지표", {}),
        "핵심내용": raw.get("핵심내용", []),
        "원문": text,
    }
    # 5차시 add_calculated_indicators가 참조하는 과거 이력 기반 필드는
    # raw에 있을 때만 표준 데이터로 그대로 전달한다 (없으면 기본값으로 처리됨).
    if "품목별지표" in raw:
        표준데이터["품목별지표"] = raw["품목별지표"]
    if "역대최대여부" in raw:
        표준데이터["역대최대여부"] = raw["역대최대여부"]
    if "최근3개월증감률" in raw:
        표준데이터["최근3개월증감률"] = raw["최근3개월증감률"]
    if "월별이력" in raw:
        표준데이터["월별이력"] = raw["월별이력"]
    return 표준데이터


def mask_sensitive_info(text: str) -> str:
    """1차시: 개인정보(주민등록번호, 전화번호) 자동 마스킹."""
    text = re.sub(r'\d{6}-[1-4]\d{6}', '******-*******', text)
    text = re.sub(r'01[016789]-\d{3,4}-\d{4}', '010-****-****', text)
    return text
