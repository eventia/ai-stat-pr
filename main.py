"""10차시: AI 기반 보도자료 자동 생성 시스템 - 전체 파이프라인 진입점."""
import logging
import os

from dotenv import load_dotenv

# modules.write/review는 임포트 시점에 anthropic.Anthropic() 클라이언트를 생성하며,
# 이때 환경변수를 읽어 키를 확정한다. 그 뒤에 load_dotenv()를 호출하면 이미 생성된
# 클라이언트에는 반영되지 않으므로, 다른 모듈을 임포트하기 전에 반드시 먼저 호출한다.
load_dotenv()

from modules.io import load_input, save_final_document
from modules.clean import clean_and_structure
from modules.nlp import analyze_document
from modules.stats import add_calculated_indicators
from modules.charts import build_visual_descriptions
from modules.write import generate_summary, generate_headline_set, generate_body_paragraphs
from modules.review import (
    assemble_full_text,
    unify_style,
    check_formatting_errors,
    cross_check_all_numbers,
    review_press_release,
)

os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename="logs/pipeline.log", level=logging.INFO, encoding="utf-8")


def main(파일경로: str) -> dict:
    try:
        logging.info(f"파이프라인 시작: {파일경로}")

        # 1. 입력
        raw_data = load_input(파일경로)
        # 2. 정제
        data = clean_and_structure(raw_data)
        # 3. NLP 분석 + 계산 + 그래프 설명 (수치는 프로그램이 계산, AI는 문장만 담당)
        data = analyze_document(data["원문"], data)
        data = add_calculated_indicators(data)
        if "품목별지표" in data or "월별이력" in data:
            data["시각자료설명"] = build_visual_descriptions(data)
        # 3-1. 3~4차시 참고 요약 (검토 보고서 A-3: 사실 확정에는 쓰이지 않는
        # 참고용이지만, 이전에는 아예 호출되지 않아 죽은 코드였다. 이제
        # generate_headline_set이 이 결과의 "제목후보"를 표현 참고용으로 읽는다.)
        data["요약결과"] = generate_summary(data)
        # 4. AI 작성
        data["헤드라인"] = generate_headline_set(data)
        data["본문"] = generate_body_paragraphs(data)
        # 5. 검수 (자동 수치·표기 교차 검증 + AI 감수, 1차시 3단계 안전장치)
        data["최종본"] = unify_style(assemble_full_text(data))
        data["검수결과"] = {
            "표기오류검사": check_formatting_errors(data["최종본"]),
            "수치교차검증": cross_check_all_numbers(data["최종본"], data),
            "AI감수지적사항": review_press_release(data["최종본"], data),
        }
        # 6. 저장
        save_final_document(data)
        logging.info("파이프라인 완료")
        return data
    except Exception as e:
        logging.error(f"오류 발생: {e}")
        raise


if __name__ == "__main__":
    결과 = main("data/raw/온라인쇼핑동향_2026_01.xlsx")
    print("=== 최종 보도자료 ===")
    print(결과["최종본"])
    print("수치 교차 검증 통과 여부:", 결과["검수결과"]["수치교차검증"]["통과"])
    print("표기 오류 검사:", 결과["검수결과"]["표기오류검사"])
