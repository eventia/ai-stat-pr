"""10차시(응용): 공공데이터포털 "온라인 수집 가격 정보" 실제 API로 통계 보도자료 생성.

main.py(온라인쇼핑 동향, xlsx 기반 예시)와는 별도의 진입점이다. 실제로 활용
승인받은 API는 main.py가 가정하는 "이미 계산된 월별 집계 통계"가 아니라
개별 상품의 낱개 판매가격 목록만 주므로, 여기서는
1) 실제 API를 호출해 품목별 평균가격을 직접 계산하고 (modules/public_api, price_stats)
2) 그 결과를 기존 4·6·7·8·9차시 모듈(수치 검증, 문체 통일, AI 감수 등)에 그대로 태워
보도자료를 완성한다. main.py와 review.py의 검증 로직은 지표명에 의존하지 않는
범용 코드라 수정 없이 재사용했다.
"""
import logging
import os
from datetime import date, timedelta

from dotenv import load_dotenv

load_dotenv()

from modules.public_api import get_average_price
from modules.price_stats import add_price_indicators, build_item_indicator
from modules.price_report import build_price_visual_descriptions, generate_headline_set
from modules.clean import clean_and_structure
from modules.nlp import analyze_document
from modules.write import generate_body_paragraphs
from modules.review import (
    assemble_full_text,
    unify_style,
    check_formatting_errors,
    cross_check_all_numbers,
    review_press_release,
)
from modules.io import save_final_document

os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename="logs/pipeline_price.log", level=logging.INFO, encoding="utf-8")

# 실습 대상 품목 (Ch01~10 예시가 다루던 생필품 곡물류와 동일한 5종을 실제 데이터로 조회)
ITEM_CODES = {"A01101": "쌀", "A01102": "현미", "A01103": "찹쌀", "A01104": "보리쌀", "A01105": "콩"}


def _shift_month(year: int, month: int, delta: int) -> tuple:
    total = (year * 12 + (month - 1)) + delta
    return total // 12, total % 12 + 1


def _month_range(year: int, month: int) -> tuple:
    # 월별 일수 차이(28~31일)가 평균가격 비교에 편차를 주지 않도록, 모든 달을
    # 1일~28일로 통일해서 비교한다 (조회기간은 최대 30일 제한도 있음).
    return f"{year}{month:02d}01", f"{year}{month:02d}28"


def _target_month() -> tuple:
    """오늘 기준 가장 최근에 '완결된' 달을 당월로 삼는다.
    (예: 오늘이 2026-09-07이면 당월=2026-08. API가 D-2 이후 데이터를 거부하므로,
    이번 달처럼 일부만 지난 달은 표본이 왜곡될 수 있어 제외한다.)"""
    today = date.today()
    first_of_this_month = today.replace(day=1)
    last_month_end = first_of_this_month - timedelta(days=1)
    return last_month_end.year, last_month_end.month


def fetch_price_dataset(item_codes: dict = ITEM_CODES) -> dict:
    """실제 API를 호출해 품목별 당월/전월/전년동월 평균가격을 계산하고,
    표준 파이프라인이 받을 수 있는 raw dict(clean_and_structure 입력)를 만든다."""
    당월_y, 당월_m = _target_month()
    전월_y, 전월_m = _shift_month(당월_y, 당월_m, -1)
    전년동월_y, 전년동월_m = _shift_month(당월_y, 당월_m, -12)

    품목별지표 = []
    for code, name in item_codes.items():
        당월 = get_average_price(code, *_month_range(당월_y, 당월_m))
        전월 = get_average_price(code, *_month_range(전월_y, 전월_m))
        전년동월 = get_average_price(code, *_month_range(전년동월_y, 전년동월_m))
        logging.info(f"{name}({code}) 당월={당월['평균가격']} 전월={전월['평균가격']} 전년동월={전년동월['평균가격']}")
        품목별지표.append(build_item_indicator(name, code, 당월, 전월, 전년동월))

    전체당월평균 = round(sum(r["당월평균가격"] for r in 품목별지표) / len(품목별지표))
    전체전월평균 = round(sum(r["전월평균가격"] for r in 품목별지표) / len(품목별지표))
    전체전년동월평균 = round(sum(r["전년동월평균가격"] for r in 품목별지표) / len(품목별지표))
    전월대비 = round((전체당월평균 - 전체전월평균) / 전체전월평균 * 100, 1)
    전년동월대비 = round((전체당월평균 - 전체전년동월평균) / 전체전년동월평균 * 100, 1)

    품목상세 = ", ".join(f"{r['품목']} {r['당월평균가격']:,}원(전월대비 {r['전월대비증감률']}%)" for r in 품목별지표)
    원문 = (
        f"공공데이터포털 온라인 수집 가격 정보에 따르면, {당월_y}년 {당월_m}월 "
        f"생필품 {len(품목별지표)}개 품목({', '.join(item_codes.values())})의 평균 판매가격은 "
        f"{전체당월평균:,}원으로 전월 대비 {전월대비}%, 전년동월대비 {전년동월대비}% 변동하였다. "
        f"품목별로는 {품목상세} 등으로 나타났다."
    )

    return {
        "제목": f"{당월_y}-{당월_m:02d} 생필품 가격 동향",
        "공표일자": date.today().isoformat(),
        "자료출처": "공공데이터포털(국가데이터처_온라인 수집 가격 정보)",
        "원문": 원문,
        "품목별지표": 품목별지표,
    }


def main() -> dict:
    try:
        logging.info("가격정보 파이프라인 시작")
        raw = fetch_price_dataset()

        data = clean_and_structure(raw)
        data = analyze_document(data["원문"], data)
        data = add_price_indicators(data)
        data["시각자료설명"] = build_price_visual_descriptions(data)

        data["헤드라인"] = generate_headline_set(data)
        data["본문"] = generate_body_paragraphs(data)

        data["최종본"] = unify_style(assemble_full_text(data))
        data["검수결과"] = {
            "표기오류검사": check_formatting_errors(data["최종본"]),
            "수치교차검증": cross_check_all_numbers(data["최종본"], data),
            "AI감수지적사항": review_press_release(data["최종본"], data),
        }

        save_final_document(data)
        logging.info("가격정보 파이프라인 완료")
        return data
    except Exception as e:
        logging.error(f"오류 발생: {e}")
        raise


if __name__ == "__main__":
    결과 = main()
    print("=== 최종 보도자료 (가격정보 API 기반) ===")
    print(결과["최종본"])
    print()
    print("수치 교차 검증 통과 여부:", 결과["검수결과"]["수치교차검증"]["통과"])
    print("표기 오류 검사:", 결과["검수결과"]["표기오류검사"])
