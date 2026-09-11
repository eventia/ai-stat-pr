"""8차 세션: 표본 사업체별 매출 신고(진짜 원자료)에서 시작하는 반려동물용품 실습 전용 집계.

main.py/main_price.py가 쓰는 modules/stats.py의 add_calculated_indicators를 대체하지
않는다. "이미 계산된 표"가 아니라 "집계 전 표본 데이터"에서 시작하는 세 번째 시나리오를
위해 새로 작성했다. 특이점 탐지·해석문 생성·역대최대/추세 판별은 modules/stats.py의
범용 함수를 그대로 재사용하고, 이 모듈은 이 시나리오에만 있는 "표본 매출 → 품목별 집계"
단계만 새로 담당한다. 설계 배경은 PLAN_raw_data_redesign.md 참고.
"""
from collections import defaultdict

from modules.config import PRIMARY_INDICATOR
from modules.stats import (
    build_interpretation_sentences,
    derive_history_indicators,
    detect_special_points,
)


def aggregate_sample_sales(표본매출: list) -> list:
    """표본 사업체별 매출 신고를 품목별로 합산해 당월거래액·비중·순위를 계산한다.

    표본매출: [{"업체명": str, "품목": str, "매출액": 숫자}, ...] — 합계·비중·순위는
    이 함수를 거치기 전까지 어디에도 존재하지 않는다.
    반환: [{"품목": str, "당월거래액": int, "비중": float(%), "순위": int}, ...]
    (당월거래액 내림차순 정렬)
    """
    품목별합계 = defaultdict(float)
    for row in 표본매출:
        품목별합계[row["품목"]] += row["매출액"]

    총매출 = sum(품목별합계.values())
    품목별지표 = [
        {
            "품목": 품목,
            "당월거래액": int(round(값)),
            "비중": round(값 / 총매출 * 100, 1),
        }
        for 품목, 값 in 품목별합계.items()
    ]
    품목별지표.sort(key=lambda row: row["당월거래액"], reverse=True)
    for 순위, row in enumerate(품목별지표, start=1):
        row["순위"] = 순위
    return 품목별지표


def build_indicators(표본매출: list, 이력: list, current_ym: str) -> dict:
    """표본매출(집계 전 원자료)과 이력(월별 총액)만으로 계산지표·품목별지표·
    통계해석결과·월별이력을 전부 계산한다. 사람이 미리 계산해서 넣어주는 값은 없다.

    반환된 dict를 표준 데이터에 그대로 병합(update)하면 이후 6차시(그래프)부터는
    main.py 예시와 완전히 동일한 방식으로 동작한다 — 두 시나리오가 여기서부터
    같은 표준 스키마(계산지표/품목별지표/통계해석결과)로 합류하기 때문이다.
    """
    품목별지표 = aggregate_sample_sales(표본매출)
    총거래액 = sum(row["당월거래액"] for row in 품목별지표)

    기간지표 = derive_history_indicators(이력, current_ym, 총거래액)
    if 기간지표["전월대비증감률"] is None or 기간지표["전년동월대비증감률"] is None:
        raise ValueError(
            "이력에 전월 또는 전년동월 데이터가 없어 증감률을 계산할 수 없습니다. "
            "0이나 임의값으로 조용히 채우지 않고 예외를 발생시킵니다 — "
            "'이력' 시트에 해당 연월 데이터를 보강하십시오."
        )

    계산지표 = {
        PRIMARY_INDICATOR: 총거래액,
        "전월대비증감률": 기간지표["전월대비증감률"],
        "전년동월대비증감률": 기간지표["전년동월대비증감률"],
    }

    특이점 = detect_special_points(
        momRate=계산지표["전월대비증감률"],
        yoyRate=계산지표["전년동월대비증감률"],
        is_record_high=기간지표["역대최대여부"],
        recent_momRates=기간지표["최근3개월증감률"],
    )
    해석문장 = build_interpretation_sentences(특이점, 계산지표, 지표명=PRIMARY_INDICATOR)

    # 실제 실행 중 발견한 버그: 이력(pet_input.py에서 float로 캐스팅됨)과 방금 계산한
    # 총거래액(int)을 그대로 섞으면, pandas.DataFrame이 열 전체를 float64로 승격시켜
    # "49,700.0억 원"처럼 뒤에 ".0"이 붙는다. 이 문자열이 6차시 꺾은선그래프 설명문에
    # 그대로 들어가고, LLM이 본문에 그대로 옮기면서 9차시 수치교차검증이 실패했다
    # (계산지표에는 정수 "49700"만 등록되어 있어 "49700.0"과 매치되지 않음). 총거래액
    # 계열 숫자는 이 프로젝트 전체에서 항상 정수(억 원 단위)이므로, 모든 값을 int로
    # 통일해 pandas가 float으로 승격시킬 여지를 없앤다.
    월별이력 = sorted(
        [{"연월": h["연월"], "값": int(round(h["값"]))} for h in 이력]
        + [{"연월": current_ym, "값": 총거래액}],
        key=lambda h: h["연월"],
    )

    return {
        "계산지표": 계산지표,
        "품목별지표": 품목별지표,
        "역대최대여부": 기간지표["역대최대여부"],
        "최근3개월증감률": 기간지표["최근3개월증감률"],
        "통계해석결과": {"특이점목록": 특이점, "해석문장": 해석문장},
        "월별이력": 월별이력,
    }
