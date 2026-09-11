"""8차 세션: 진짜 원자료(표본 사업체별 매출 신고) 입력 — 반려동물용품 실습 전용.

modules/io.py::load_input과 이름이 비슷하지만 역할이 다르다. load_input은 "이미
계산된 표"(총거래액·증감률까지 채워진 xlsx)를 읽어들이는 반면, 이 함수는 어떤 계산도
하지 않는다 — xlsx의 "표본매출"(집계 전 원자료), "이력"(이미 발표된 월별 총액),
"메모"(숫자 없는 정성적 원문) 세 시트를 그대로 읽어 raw dict로만 반환한다. 집계·증감률
계산은 modules/pet_stats.py가 담당한다 (자세한 설계 배경은 PLAN_raw_data_redesign.md).
"""
import pandas as pd

REQUIRED_SHEETS = {"표본매출", "이력", "메모"}


def load_raw_practice_input(파일경로: str) -> dict:
    """표본매출/이력/메모 세 시트를 읽어 raw dict로 반환한다. 계산은 하지 않는다."""
    엑셀 = pd.ExcelFile(파일경로)
    누락 = REQUIRED_SHEETS - set(엑셀.sheet_names)
    if 누락:
        raise ValueError(f"필수 시트가 없습니다: {', '.join(sorted(누락))}")

    표본매출_df = pd.read_excel(엑셀, sheet_name="표본매출")
    이력_df = pd.read_excel(엑셀, sheet_name="이력")
    메모_df = pd.read_excel(엑셀, sheet_name="메모")

    # pandas가 xlsx 숫자 컬럼을 numpy 스칼라(int64/float64)로 읽어오는데, 이후
    # json.dumps(review_press_release 등)로 직렬화할 때 실패하므로 순수 파이썬
    # float/str로 명시적으로 변환해 둔다.
    표본매출 = [
        {"업체명": str(row["업체명"]), "품목": str(row["품목"]), "매출액": float(row["매출액"])}
        for _, row in 표본매출_df.iterrows()
    ]
    이력 = [
        {"연월": str(row["연월"]), "값": float(row["총거래액"])}
        for _, row in 이력_df.iterrows()
    ]

    메모_행 = 메모_df.iloc[0]
    return {
        "제목": str(메모_행.get("제목", "")),
        "연월": str(메모_행.get("연월", "")),
        "원문": str(메모_행.get("메모", "")),
        "표본매출": 표본매출,
        "이력": 이력,
    }
