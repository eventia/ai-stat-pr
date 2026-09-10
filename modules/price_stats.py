"""5차시(응용): 공공데이터포털 "온라인 수집 가격 정보"를 이용한 통계 계산.

modules/stats.py의 add_calculated_indicators는 "거래액"이라는 문구가
해석문장 템플릿에 고정되어 있어 가격 데이터에는 그대로 재사용할 수 없다
(예: "거래액이 전월 대비 상승" 같은 어색한 문장이 나옴). 대신 detect_special_points/
generate_interpretation처럼 지표명을 인자로 받는 진짜 범용 함수는 그대로 재사용하고,
"평균 판매가격" 지표에 맞는 해석문 조립만 이 모듈이 새로 담당한다.
"""
from modules.stats import detect_special_points, generate_interpretation

INDICATOR_NAME = "평균 판매가격"
INDICATOR_UNIT = "원"


def pct_change(current: float, previous: float) -> float:
    """이전 값 대비 증감률(%). 원본 수치는 항상 API 응답의 판매가격 그대로 쓰고,
    비교 계산만 이 함수가 담당한다 (CLAUDE.md 원칙: 수치 계산은 AI에게 맡기지 않음)."""
    if previous == 0:
        return 0.0
    return round((current - previous) / previous * 100, 1)


def build_item_indicator(품목명: str, 품목코드: str, 당월: dict, 전월: dict, 전년동월: dict) -> dict:
    """품목 하나의 당월/전월/전년동월 평균가격으로 품목별지표 한 행을 만든다."""
    return {
        "품목": 품목명,
        "품목코드": 품목코드,
        "당월평균가격": 당월["평균가격"],
        "전월평균가격": 전월["평균가격"],
        "전년동월평균가격": 전년동월["평균가격"],
        "전월대비증감률": pct_change(당월["평균가격"], 전월["평균가격"]),
        "전년동월대비증감률": pct_change(당월["평균가격"], 전년동월["평균가격"]),
        "표본건수": 당월["표본건수"],
    }


def add_price_indicators(data: dict) -> dict:
    """품목별지표(당월/전월/전년동월 평균가격 포함)를 바탕으로 전체 대표 계산지표와
    통계해석결과를 채운다. modules/stats.add_calculated_indicators의 가격판 대응 함수."""
    품목별지표 = data["품목별지표"]

    전체당월평균 = round(sum(row["당월평균가격"] for row in 품목별지표) / len(품목별지표))
    전체전월평균 = round(sum(row["전월평균가격"] for row in 품목별지표) / len(품목별지표))
    전체전년동월평균 = round(sum(row["전년동월평균가격"] for row in 품목별지표) / len(품목별지표))

    전월대비 = pct_change(전체당월평균, 전체전월평균)
    전년동월대비 = pct_change(전체당월평균, 전체전년동월평균)

    data["계산지표"] = {
        INDICATOR_NAME: 전체당월평균,
        "전월대비증감률": 전월대비,
        "전년동월대비증감률": 전년동월대비,
    }

    for i, row in enumerate(sorted(품목별지표, key=lambda r: r["당월평균가격"], reverse=True), start=1):
        row["순위"] = i

    특이점 = detect_special_points(
        momRate=전월대비,
        yoyRate=전년동월대비,
        is_record_high=data.get("역대최대여부", False),
        recent_momRates=data.get("최근3개월증감률"),
    )

    해석문장 = []
    if "전월 대비 큰 폭 증가" in 특이점 or "전월 대비 큰 폭 감소" in 특이점:
        point_type = "전월 대비 큰 폭 증가" if 전월대비 > 0 else "전월 대비 큰 폭 감소"
        해석문장.append(_해석문(point_type, 전월대비))
    if "전년동월 대비 큰 폭 증가" in 특이점 or "전년동월 대비 큰 폭 감소" in 특이점:
        point_type = "전년동월 대비 큰 폭 증가" if 전년동월대비 > 0 else "전년동월 대비 큰 폭 감소"
        해석문장.append(_해석문(point_type, 전년동월대비))

    data["통계해석결과"] = {"특이점목록": 특이점, "해석문장": 해석문장}
    return data


def _해석문(point_type: str, value: float) -> str:
    """generate_interpretation은 "증가" 템플릿만 갖고 있으므로, 하락(감소) 문구는
    여기서 직접 채워 넣는다 — 가격은 거래액과 달리 증감 둘 다 뉴스 가치가 있어
    "하락"도 명시적으로 다뤄야 한다."""
    if "감소" in point_type:
        기준 = "전월" if "전월" in point_type else "전년동월"
        return f"{INDICATOR_NAME}이 {기준} 대비 {abs(value)}% 하락하며 큰 폭의 하락세를 보였다."
    return generate_interpretation(INDICATOR_NAME, value, "%", point_type)
