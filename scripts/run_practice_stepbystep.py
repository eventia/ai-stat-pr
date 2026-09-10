"""7차 세션 실습: 새 샘플 데이터(반려동물용품 온라인 거래 동향)로 Ch02~Ch10 파이프라인을
한 단계씩 직접 눈으로 확인하며 실행하는 스크립트.

사전 준비:
  1) python scripts/make_sample_excel_practice.py   (샘플 데이터가 아직 없다면 먼저 실행)
  2) .env에 ANTHROPIC_API_KEY가 설정되어 있어야 함 (4·7·8·9차시 단계에서 실제 API 호출)

실행: python scripts/run_practice_stepbystep.py
각 단계 끝에서 Enter를 누르면 다음 단계로 진행합니다.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
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

DATA_PATH = "data/raw/반려동물용품_2026_03.xlsx"


def 구분(제목: str):
    print("\n" + "=" * 72)
    print(제목)
    print("=" * 72)


def 다음_단계():
    input("\n[Enter] 키를 누르면 다음 단계로 진행합니다...")


def pretty(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2))


if not os.path.exists(DATA_PATH):
    print(f"먼저 샘플 데이터를 생성하세요: python scripts/make_sample_excel_practice.py")
    raise SystemExit(1)

구분("0단계. 오늘 다룰 원자료")
print(f"파일: {DATA_PATH} (시트: 요약, 이력)")
print("이 데이터는 '전월 대비 큰 폭 감소'와 '3개월 연속 감소세'가 동시에 나타나도록")
print("일부러 설계했습니다 — 지난 검토에서 발견해 이번에 고친 두 가지 버그를")
print("직접 눈으로 확인하기 위해서입니다:")
print("  1) 감소 방향 특이점이 감지는 되는데 해석문장으로 안 이어지던 버그 (modules/stats.py)")
print("  2) '역대 최대'를 사람이 직접 조사해서 입력해야 했던 문제 (modules/io.py, 이력 시트)")
다음_단계()

구분("1단계 (Ch02). 원자료 입력 + 정제·표준화·구조화")
raw = load_input(DATA_PATH)
print("[load_input 결과 — xlsx의 '이력' 시트를 읽어 아래 두 값이 자동 계산되었습니다]")
pretty({k: v for k, v in raw.items() if k != "월별이력"})
print(f"\n(월별이력: 과거 {len(raw['월별이력']) - 1}개월 + 이번 달, 총 {len(raw['월별이력'])}개월치 — 아래 4단계 꺾은선그래프에 사용됨)")

data = clean_and_structure(raw)
print("\n[clean_and_structure 결과 — 원문이 정제·표준화됨]")
print("정제 전 원문:", raw["원문"])
print("정제 후 원문:", data["원문"])
다음_단계()

구분("2단계 (Ch03). NLP 분석 — 핵심키워드·주요문장 추출 (참고용)")
data = analyze_document(data["원문"], data)
pretty(data["NLP분석결과"])
print("\n※ 이 결과는 5단계 참고 요약에만 쓰이며, 보도자료의 사실 확정에는 쓰이지 않습니다.")
print("  (실제 헤드라인·본문의 근거는 다음 단계의 계산 결과입니다.)")
다음_단계()

구분("3단계 (Ch05). 통계 계산 — 특이점 자동 탐지 + 해석문장 생성")
data = add_calculated_indicators(data)
print("역대최대여부 (이력 시트로 자동 계산됨, 사람이 입력하지 않음):", data["역대최대여부"])
print("최근3개월증감률 (이력 시트로 자동 계산됨):", data["최근3개월증감률"])
print("\n특이점목록:")
pretty(data["통계해석결과"]["특이점목록"])
print("\n해석문장 (여기서 '감소' 문장이 실제로 만들어지는지 확인하세요):")
pretty(data["통계해석결과"]["해석문장"])
다음_단계()

구분("4단계 (Ch06). 그래프 생성 — 막대·원형·꺾은선")
data["시각자료설명"] = build_visual_descriptions(data)
for 항목 in data["시각자료설명"]:
    print(f"- [{항목['그래프유형']}] {항목['소주제']}: {항목['이미지경로']}")
    print(f"    설명문: {항목['설명문']}")
print("\n'시계열 동향'(꺾은선그래프) 항목이 보이면, 그동안 파이프라인에서 도달 불가능했던")
print("기능이 이번 세션부터 실제로 연결된 것입니다. images/ 폴더에서 파일을 열어보세요.")
다음_단계()

구분("5단계 (Ch04, 실제 API 호출). 참고용 3줄요약 + 제목후보 생성")
data["요약결과"] = generate_summary(data)
pretty(data["요약결과"])
print("\n이 '제목후보'는 다음 단계 헤드라인 생성 프롬프트에 참고 자료로만 전달되며,")
print("최종 수치 검증에는 영향을 주지 않습니다.")
다음_단계()

구분("6단계 (Ch07, 실제 API 호출). 제목·부제·리드문 생성")
data["헤드라인"] = generate_headline_set(data)
pretty(data["헤드라인"])
다음_단계()

구분("7단계 (Ch08, 실제 API 호출). 본문 단락 생성")
data["본문"] = generate_body_paragraphs(data)
for 단락 in data["본문"]:
    print(f"\n[{단락['소주제']}]")
    print(단락["내용"])
다음_단계()

구분("8단계 (Ch09, 실제 API 호출). 문체 통일 + 자동 검수 + AI 감수")
data["최종본"] = unify_style(assemble_full_text(data))
print("[최종본]\n")
print(data["최종본"])

data["검수결과"] = {
    "표기오류검사": check_formatting_errors(data["최종본"]),
    "수치교차검증": cross_check_all_numbers(data["최종본"], data),
    "AI감수지적사항": review_press_release(data["최종본"], data),
}
print("\n표기오류검사:", data["검수결과"]["표기오류검사"] or "없음")
print("수치교차검증:", data["검수결과"]["수치교차검증"])
print("\nAI감수지적사항:")
pretty(data["검수결과"]["AI감수지적사항"])
다음_단계()

구분("9단계 (Ch10). 최종 문서 저장")
save_final_document(data)
print(f"저장 완료: output/{data['문서정보']['제목']}.txt")

구분("실습 종료")
print("수고하셨습니다! output/, images/ 폴더의 결과물을 직접 열어 확인해보세요.")
