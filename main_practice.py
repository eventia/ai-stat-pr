"""8차 세션: 진짜 원자료(표본 사업체별 매출 신고)에서 시작하는 반려동물용품 통계
보도자료 자동 생성 파이프라인.

main.py(이미 계산된 표 입력)·main_price.py(공공 가격정보 API)와 나란히 놓이는 세 번째
예시. 설계 배경은 PLAN_raw_data_redesign.md를 참고. 핵심 차이는 "계산" 단계다 —
main.py는 xlsx에 이미 채워진 총거래액·증감률을 그대로 읽지만, 이 파이프라인은
"표본매출"(집계 전 원자료)과 "이력"(이미 발표된 월별 총액)만으로 총거래액·증감률·
특이점·해석문장을 전부 modules/pet_stats.py가 직접 계산한다. 그 이후 단계(그래프,
헤드라인, 본문, 검수, 저장)는 main.py와 완전히 동일한 함수를 그대로 재사용한다.
"""
import logging
import os

from dotenv import load_dotenv

# modules.write/review는 임포트 시점에 anthropic.Anthropic() 클라이언트를 생성하며,
# 이때 환경변수를 읽어 키를 확정한다. 그 뒤에 load_dotenv()를 호출하면 이미 생성된
# 클라이언트에는 반영되지 않으므로, 다른 모듈을 임포트하기 전에 반드시 먼저 호출한다.
load_dotenv()

from modules.pet_input import load_raw_practice_input
from modules.pet_stats import build_indicators
from modules.clean import clean_and_structure
from modules.nlp import analyze_document
from modules.charts import build_visual_descriptions
from modules.write import generate_summary, generate_headline_set, generate_body_paragraphs
from modules.review import (
    assemble_full_text,
    unify_style,
    check_formatting_errors,
    cross_check_all_numbers,
    review_press_release,
)
from modules.io import save_final_document

os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename="logs/pipeline_practice.log", level=logging.INFO, encoding="utf-8")


def main(파일경로: str) -> dict:
    try:
        logging.info(f"파이프라인 시작: {파일경로}")

        # 1. 입력 — 계산 없음. 표본매출/이력/메모를 그대로 읽기만 한다.
        raw = load_raw_practice_input(파일경로)
        # 2. 정제 (원문 정제·표준화 + 표본매출/이력 통과)
        data = clean_and_structure(raw)
        # 3. NLP 분석 (참고용 — 사실 확정에는 쓰이지 않음)
        data = analyze_document(data["원문"], data)
        # 4. 계산 — main.py와 가장 다른 지점. 이미 계산된 값을 읽는 게 아니라
        # 표본매출 + 이력만으로 총거래액·증감률·특이점·해석문장·월별이력을 전부 계산한다.
        지표결과 = build_indicators(data["표본매출"], data["이력"], data["연월"])
        data.update(지표결과)
        # 5. 그래프 (품목별지표·월별이력 모두 있으므로 막대·원형·꺾은선 전부 생성됨)
        data["시각자료설명"] = build_visual_descriptions(data)
        # 6. AI 작성 — modules/write.py를 수정 없이 그대로 재사용
        data["요약결과"] = generate_summary(data)
        data["헤드라인"] = generate_headline_set(data)
        data["본문"] = generate_body_paragraphs(data)
        # 7. 검수 — modules/review.py를 수정 없이 그대로 재사용
        data["최종본"] = unify_style(assemble_full_text(data))
        data["검수결과"] = {
            "표기오류검사": check_formatting_errors(data["최종본"]),
            "수치교차검증": cross_check_all_numbers(data["최종본"], data),
            "AI감수지적사항": review_press_release(data["최종본"], data),
        }
        # 8. 저장
        save_final_document(data)
        logging.info("파이프라인 완료")
        return data
    except Exception as e:
        logging.error(f"오류 발생: {e}")
        raise


if __name__ == "__main__":
    결과 = main("data/raw/반려동물용품_2026_03_원자료.xlsx")
    print("=== 최종 보도자료 ===")
    print(결과["최종본"])
    print("수치 교차 검증 통과 여부:", 결과["검수결과"]["수치교차검증"]["통과"])
    print("표기 오류 검사:", 결과["검수결과"]["표기오류검사"])
