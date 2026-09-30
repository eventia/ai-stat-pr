"""5차시: 증감률·비중·순위 계산, 특이점 탐지, 규칙 기반 해석문 생성(모든 계산은 이 파일이 담당)."""
import pandas as pd


def calc_category_indicators(rows: list) -> list:
    df = pd.DataFrame(rows)
    df["전월대비증감률"] = ((df["당월거래액"] - df["전월거래액"]) / df["전월거래액"] * 100).round(1)
    df["비중"] = (df["당월거래액"] / df["당월거래액"].sum() * 100).round(1)
    df["순위"] = df["당월거래액"].rank(ascending=False, method="min").astype(int)
    df = df.sort_values("순위")
    return [
        {"품목": r["품목"], "당월거래액": int(r["당월거래액"]), "전월거래액": int(r["전월거래액"]),
         "전월대비증감률": float(r["전월대비증감률"]), "비중": float(r["비중"]), "순위": int(r["순위"])}
        for _, r in df.iterrows()
    ]


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


def generate_interpretation(indicator_name: str, value: float, unit: str, point_type: str) -> str:
    값 = f"{value:,}" if isinstance(value, int) else f"{value}"
    templates = {
        "역대 최대치 경신": f"{indicator_name}은 {값}{unit}으로 동월 기준 역대 최대치를 기록하였다.",
        "전월 대비 큰 폭 증가": f"{indicator_name}이 전월 대비 {값}% 증가하며 큰 폭의 상승세를 보였다.",
        "전월 대비 큰 폭 감소": f"{indicator_name}이 전월 대비 {값}% 감소하며 큰 폭의 하락세를 보였다.",
        "전년동월 대비 큰 폭 증가": f"{indicator_name}이 전년동월 대비 {값}% 증가하며 큰 폭의 상승세를 보였다.",
        "전년동월 대비 큰 폭 감소": f"{indicator_name}이 전년동월 대비 {값}% 감소하며 큰 폭의 하락세를 보였다.",
        "최근 3개월 연속 증가세": f"{indicator_name}은 최근 3개월 연속 증가세를 이어가고 있다.",
        "최근 3개월 연속 감소세": f"{indicator_name}은 최근 3개월 연속 감소세를 이어가고 있다.",
    }
    return templates.get(point_type, "")


def build_interpretation_sentences(특이점: list, 계산지표: dict, 지표명: str = "거래액") -> list:
    값_매핑 = {
        "역대 최대치 경신": (계산지표["총거래액"], "억 원"),
        "전월 대비 큰 폭 증가": (계산지표["전월대비증감률"], "%"),
        "전월 대비 큰 폭 감소": (abs(계산지표["전월대비증감률"]), "%"),
        "전년동월 대비 큰 폭 증가": (계산지표["전년동월대비증감률"], "%"),
        "전년동월 대비 큰 폭 감소": (abs(계산지표["전년동월대비증감률"]), "%"),
        "최근 3개월 연속 증가세": (0, ""),
        "최근 3개월 연속 감소세": (0, ""),
    }
    return [generate_interpretation(지표명, *값_매핑[p], p) for p in 특이점 if p in 값_매핑]


def _shift_month(ym: str, delta_months: int) -> str:
    year, month = (int(part) for part in ym.split("-"))
    total = year * 12 + (month - 1) + delta_months
    new_year, new_month0 = divmod(total, 12)
    return f"{new_year:04d}-{new_month0 + 1:02d}"


def _rate(current: float, base: float) -> float:
    return round((current - base) / base * 100, 1)


def derive_history_indicators(history: list, current_ym: str, current_value: float) -> dict:
    if not history:
        return {"역대최대여부": None, "최근3개월증감률": [],
                "전월대비증감률": None, "전년동월대비증감률": None}

    현재_월 = current_ym.split("-")[1]
    같은달_과거값 = [h["값"] for h in history if h["연월"].split("-")[1] == 현재_월]
    역대최대여부 = current_value >= max(같은달_과거값) if 같은달_과거값 else None

    이력 = sorted(history, key=lambda h: h["연월"]) + [{"연월": current_ym, "값": current_value}]
    최근3개월증감률 = [_rate(이력[i]["값"], 이력[i - 1]["값"]) for i in range(max(1, len(이력) - 3), len(이력))]

    값_by_연월 = {h["연월"]: h["값"] for h in history}
    전월 = 값_by_연월.get(_shift_month(current_ym, -1))
    전년동월 = 값_by_연월.get(_shift_month(current_ym, -12))
    return {
        "역대최대여부": 역대최대여부,
        "최근3개월증감률": 최근3개월증감률,
        "전월대비증감률": _rate(current_value, 전월) if 전월 else None,
        "전년동월대비증감률": _rate(current_value, 전년동월) if 전년동월 else None,
    }


def add_calculated_indicators(data: dict) -> dict:
    지표 = data["계산지표"]
    if data.get("품목별지표") and "전월거래액" in data["품목별지표"][0]:
        data["품목별지표"] = calc_category_indicators(data["품목별지표"])

    기준연월 = data["문서정보"].get("기준연월", "")
    if data.get("월별이력") and 기준연월:
        과거 = [h for h in data["월별이력"] if h["연월"] < 기준연월]
        계산됨 = derive_history_indicators(과거, 기준연월, 지표["총거래액"])
        data.setdefault("역대최대여부", 계산됨["역대최대여부"])
        data.setdefault("최근3개월증감률", 계산됨["최근3개월증감률"])

    특이점 = detect_special_points(
        momRate=지표["전월대비증감률"],
        yoyRate=지표["전년동월대비증감률"],
        is_record_high=data.get("역대최대여부") is True,
        recent_momRates=data.get("최근3개월증감률"),
    )
    지표명 = data["문서정보"].get("지표명", "거래액")
    data["통계해석결과"] = {
        "특이점목록": 특이점,
        "해석문장": build_interpretation_sentences(특이점, 지표, 지표명),
    }
    return data


def check_percent_unit(text: str, is_rate_of_rate: bool) -> bool:
    if is_rate_of_rate and "%p" not in text:
        return False
    if not is_rate_of_rate and "%p" in text:
        return False
    return True
