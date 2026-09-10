"""5차시: 증감률·비중·순위 계산, 특이점 자동 탐지, 통계 해석문 생성."""
from modules.config import PRIMARY_INDICATOR, PRIMARY_UNIT


def detect_special_points(momRate: float, yoyRate: float, is_record_high: bool,
                           recent_momRates: list = None) -> list:
    points = []
    if is_record_high:
        points.append("역대 최대치 경신")
    if abs(momRate) >= 5:
        points.append(f"전월 대비 {'큰 폭 증가' if momRate > 0 else '큰 폭 감소'}")
    if abs(yoyRate) >= 5:
        points.append(f"전년동월 대비 {'큰 폭 증가' if yoyRate > 0 else '큰 폭 감소'}")
    if recent_momRates and len(recent_momRates) >= 3:
        최근3개월 = recent_momRates[-3:]
        if all(r > 0 for r in 최근3개월):
            points.append("최근 3개월 연속 증가세")
        elif all(r < 0 for r in 최근3개월):
            points.append("최근 3개월 연속 감소세")
    return points


def generate_interpretation(indicator_name: str, value: float, unit: str,
                             point_type: str) -> str:
    templates = {
        "역대 최대치 경신": f"{indicator_name}은 {value}{unit}로 역대 최대치를 기록하였다.",
        "전월 대비 큰 폭 증가": f"{indicator_name}이 전월 대비 {value}% 증가하며 큰 폭의 상승세를 보였다.",
        "전월 대비 큰 폭 감소": f"{indicator_name}이 전월 대비 {value}% 감소하며 큰 폭의 하락세를 보였다.",
        "전년동월 대비 큰 폭 증가": f"{indicator_name}이 전년동월 대비 {value}% 증가하며 큰 폭의 상승세를 보였다.",
        "전년동월 대비 큰 폭 감소": f"{indicator_name}이 전년동월 대비 {value}% 감소하며 큰 폭의 하락세를 보였다.",
        "최대 비중": f"{indicator_name}은 {value}{unit}로 가장 큰 비중을 차지하였다.",
        "최근 3개월 연속 증가세": f"{indicator_name}은 최근 3개월 연속 증가세를 이어가고 있다.",
        "최근 3개월 연속 감소세": f"{indicator_name}은 최근 3개월 연속 감소세를 이어가고 있다.",
    }
    return templates.get(point_type, "")


def check_percent_unit(text: str, is_rate_of_rate: bool) -> bool:
    if is_rate_of_rate and "%p" not in text:
        return False
    if not is_rate_of_rate and "%p" in text:
        return False
    return True


def derive_history_indicators(history: list, current_ym: str, current_value: float) -> dict:
    """과거 월별 시계열과 이번 달 값을 비교해 역대최대여부·최근3개월증감률을 자동 계산한다.

    검토 보고서(REVIEW_Ch02-10.md, A-1)에서 지적된 문제에 대한 수정: 기존에는
    이 두 값을 담당자가 과거 자료를 보고 직접 조사해서 raw 데이터에 입력해야 했다.
    `history`(과거 월별 실적, 이번 달 제외)가 주어지면 이 함수가 대신 계산한다.

    history: [{"연월": "YYYY-MM", "값": 숫자}, ...] 순서 무관.
    반환값이 없으면(과거 이력이 아예 없으면) 역대최대여부는 True로 간주한다
    (비교 대상이 없는 첫 통계는 그 자체로 최댓값이므로).
    """
    if not history:
        return {"역대최대여부": True, "최근3개월증감률": []}

    현재_월 = current_ym.split("-")[1]
    같은달_과거값 = [h["값"] for h in history if h["연월"].split("-")[1] == 현재_월]
    역대최대여부 = current_value >= max(같은달_과거값) if 같은달_과거값 else True

    전체 = sorted(history + [{"연월": current_ym, "값": current_value}], key=lambda h: h["연월"])
    최근3개월증감률 = []
    for i in range(max(1, len(전체) - 3), len(전체)):
        이전값, 이번값 = 전체[i - 1]["값"], 전체[i]["값"]
        if 이전값:
            최근3개월증감률.append(round((이번값 - 이전값) / 이전값 * 100, 1))

    return {"역대최대여부": 역대최대여부, "최근3개월증감률": 최근3개월증감률}


def add_calculated_indicators(data: dict) -> dict:
    """표준 데이터의 원본 수치를 바탕으로 계산지표, 통계해석결과 필드를 채운다."""
    지표 = data["계산지표"]
    # "역대최대여부"/"최근3개월증감률"은 clean_and_structure 단계에서 이미 채워져
    # 있어야 한다 — xlsx에 "이력" 시트가 있으면 modules/io.load_input이
    # derive_history_indicators로 자동 계산하고, 없으면 담당자가 직접 넣은 값을
    # 그대로 쓴다 (이 함수 자체는 과거 이력을 조회하지 않는다).
    is_record_high = data.get("역대최대여부", False)

    특이점 = detect_special_points(
        momRate=지표["전월대비증감률"],
        yoyRate=지표["전년동월대비증감률"],
        is_record_high=is_record_high,
        recent_momRates=data.get("최근3개월증감률"),
    )

    지표명 = data["문서정보"]["제목"].split()[-1] or "거래액"
    해석문장 = []
    if "역대 최대치 경신" in 특이점:
        해석문장.append(generate_interpretation(
            지표명, 지표[PRIMARY_INDICATOR], PRIMARY_UNIT, "역대 최대치 경신"))
    # 전월 대비/전년동월 대비는 서로 다른 수치이므로, 어느 쪽이 특이점으로
    # 감지되었는지에 맞는 값을 각각 골라 문장을 만든다. 감소 방향은 검토
    # 보고서(A-2)에서 지적된 대로 기존에 템플릿이 아예 없어 조용히 누락되던
    # 부분이라, abs()로 부호를 뗀 값을 "감소" 전용 템플릿에 채운다
    # (부호를 그대로 두면 "이 -6% 감소하며..."처럼 이중 부정이 된다).
    if "전월 대비 큰 폭 증가" in 특이점:
        해석문장.append(generate_interpretation(
            "거래액", 지표["전월대비증감률"], "%", "전월 대비 큰 폭 증가"))
    if "전월 대비 큰 폭 감소" in 특이점:
        해석문장.append(generate_interpretation(
            "거래액", abs(지표["전월대비증감률"]), "%", "전월 대비 큰 폭 감소"))
    if "전년동월 대비 큰 폭 증가" in 특이점:
        해석문장.append(generate_interpretation(
            "거래액", 지표["전년동월대비증감률"], "%", "전년동월 대비 큰 폭 증가"))
    if "전년동월 대비 큰 폭 감소" in 특이점:
        해석문장.append(generate_interpretation(
            "거래액", abs(지표["전년동월대비증감률"]), "%", "전년동월 대비 큰 폭 감소"))
    if "최근 3개월 연속 증가세" in 특이점:
        해석문장.append(generate_interpretation("거래액", 0, "%", "최근 3개월 연속 증가세"))
    if "최근 3개월 연속 감소세" in 특이점:
        해석문장.append(generate_interpretation("거래액", 0, "%", "최근 3개월 연속 감소세"))

    data["통계해석결과"] = {"특이점목록": 특이점, "해석문장": 해석문장}
    return data
