"""10차시: 입력부터 저장까지 전체 파이프라인을 하나의 main 함수로 실행한다."""
import json
import logging
import os
import re
import sys

from mywork.charts import build_visual_descriptions
from mywork.clean import check_data_grade, clean_and_structure, mask_personal_info
from mywork.data_io import load_input
from mywork.nlp import analyze_document
from mywork.review import check_formatting_errors, cross_check_all_numbers, review_press_release
from mywork.stats import add_calculated_indicators
from mywork.write import (assemble_full_text, generate_body_paragraphs, generate_headline_set,
                          generate_summary, unify_style)

os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename="logs/pipeline.log", level=logging.INFO, encoding="utf-8",
                    format="%(asctime)s %(levelname)s %(message)s")


def save_final_document(data: dict) -> str:
    os.makedirs("output", exist_ok=True)
    상태 = data.get("문서상태", "검토필요")
    파일명 = re.sub(r'[\\/:*?"<>|]', "_", data["문서정보"]["제목"])
    경로 = f"output/{파일명}_{상태}.txt"
    with open(경로, "w", encoding="utf-8") as f:
        f.write(data["헤드라인"]["제목"] + "\n" + data["헤드라인"]["부제"] + "\n\n" + data["최종본"])
    return 경로


def main(파일경로: str, pdf경로: str = None) -> dict:
    try:
        logging.info(f"파이프라인 시작: {파일경로}")
        # 1. 입력
        raw = load_input(파일경로)
        if pdf경로:
            raw["원문"] = load_input(pdf경로)["원문"]
        # 2. 정제 + 보안 전처리 (외부 LLM API를 부르기 전에 반드시 거친다)
        data = clean_and_structure(raw)
        check_data_grade(data)
        data = mask_personal_info(data)
        # 3. NLP 분석 + 계산 + 그래프 설명 (수치는 프로그램이 계산)
        data = analyze_document(data["원문"], data)
        data = add_calculated_indicators(data)
        if data.get("품목별지표") or data.get("월별이력"):
            data["시각자료설명"] = build_visual_descriptions(data)
        # 4. AI 작성 (참고용 요약은 저장만 한다)
        data["요약결과"] = generate_summary(data)
        data["헤드라인"] = generate_headline_set(data)
        data["본문"] = generate_body_paragraphs(data)
        # 5. 검수 (표기 검사 + 수치 교차 검증 + AI 감수)
        data["최종본"] = unify_style(assemble_full_text(data))
        전체 = " ".join([data["헤드라인"]["제목"], data["헤드라인"]["부제"], data["최종본"]])
        data["검수결과"] = {
            "표기오류검사": check_formatting_errors(전체),
            "수치교차검증": cross_check_all_numbers(전체, data),
            "AI감수지적사항": review_press_release(data["최종본"], data),
        }
        # 6. 저장 (자동 검증을 통과하지 못하면 '검토필요'로 저장, 어느 쪽이든 사람의 승인이 필요)
        검증통과 = data["검수결과"]["수치교차검증"]["통과"] and not data["검수결과"]["표기오류검사"]
        data["문서상태"] = "승인대기" if 검증통과 else "검토필요"
        data["출력파일"] = {"txt": save_final_document(data)}
        try:
            from mywork.export import save_hwpx, save_pdf
            for 형식, 저장 in (("hwpx", save_hwpx), ("pdf", save_pdf)):
                try:
                    data["출력파일"][형식] = 저장(data)
                except Exception as e:
                    logging.warning(f"{형식} 저장 실패: {e}")
        except ImportError:
            logging.info("mywork/export.py가 없어 txt만 저장합니다.")
        with open("mywork/press_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"파이프라인 완료: {data['출력파일']}")
        return data
    except Exception as e:
        logging.error(f"오류 발생: {e}")
        raise


if __name__ == "__main__":
    결과 = main(sys.argv[1] if len(sys.argv) > 1 else "data/온라인쇼핑동향_2026_01.xlsx",
              sys.argv[2] if len(sys.argv) > 2 else None)
    print("=== 최종 보도자료 ===")
    print(결과["헤드라인"]["제목"])
    print(결과["헤드라인"]["부제"])
    print(결과["최종본"])
    print("수치 교차 검증 통과 여부:", 결과["검수결과"]["수치교차검증"]["통과"])
    print("표기 오류 검사:", 결과["검수결과"]["표기오류검사"])
    print("문서상태:", 결과["문서상태"])
    print("저장된 파일:", 결과["출력파일"])
