"""8차 세션 실습: 진짜 원자료(표본 사업체별 매출 신고)에서 시작하는 반려동물용품
통계 보도자료 파이프라인을 한 단계씩 직접 눈으로 확인하며 실행하는 스크립트.

이전 버전과의 핵심 차이(PLAN_raw_data_redesign.md 참고): 예전에는 입력 파일 안에
이미 총거래액·증감률·품목별지표가 계산되어 들어있었다. 이번에는 "표본매출"(집계 전
원자료)과 "이력"(이미 발표된 월별 총액)만 있고, 총거래액·증감률·특이점·해석문장은
전부 이 스크립트가 실행되는 동안 코드가 직접 계산한다.

사전 준비:
  1) python scripts/make_sample_excel_practice_raw.py   (샘플 데이터가 아직 없다면 먼저 실행)
  2) .env에 ANTHROPIC_API_KEY가 설정되어 있어야 함 (5·7·8·9단계에서 실제 API 호출)

실행: python scripts/run_practice_stepbystep.py
각 단계 끝에서 Enter를 누르면 다음 단계로 진행합니다.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
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

DATA_PATH = "data/raw/반려동물용품_2026_03_원자료.xlsx"


def 구분(제목: str):
    print("\n" + "=" * 72)
    print(제목)
    print("=" * 72)


def 다음_단계():
    input("\n[Enter] 키를 누르면 다음 단계로 진행합니다...")


def pretty(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2))


if not os.path.exists(DATA_PATH):
    print("먼저 샘플 데이터를 생성하세요: python scripts/make_sample_excel_practice_raw.py")
    raise SystemExit(1)

구분("0단계. 오늘 다룰 원자료")
print(f"파일: {DATA_PATH} (시트: 표본매출, 이력, 메모)")
print("'표본매출' 시트에는 표본 사업체 23곳이 신고한 품목별 매출만 있고, 합계도 증감률도")
print("들어있지 않습니다. 이번 실습에서는 다음을 전부 코드가 직접 계산하는 것을 볼 수 있습니다:")
print("  - 총거래액, 품목별 당월거래액·비중·순위 (표본매출을 품목별로 합산)")
print("  - 전월대비/전년동월대비증감률, 역대최대여부, 최근3개월증감률 (이력 + 위 총거래액)")
다음_단계()

구분("1단계 (Ch07 입력, 계산 없음). 원자료 3개 시트 읽기")
raw = load_raw_practice_input(DATA_PATH)
print("표본매출 (앞 5건만 표시, 총 {}건) — 합계·비중·순위 없음:".format(len(raw["표본매출"])))
pretty(raw["표본매출"][:5])
print(f"\n이력 ({len(raw['이력'])}개월치, 이미 발표된 월별 총액):")
pretty(raw["이력"])
print(f"\n메모(원문, 정제 전): {raw['원문']}")
다음_단계()

구분("2단계 (Ch02). 정제·표준화·구조화")
data = clean_and_structure(raw)
print("정제 후 원문:", data["원문"])
print("\n표본매출/이력은 계산되지 않은 채 그대로 다음 단계로 전달됩니다.")
다음_단계()

구분("3단계 (Ch03). NLP 분석 — 핵심키워드·주요문장 추출 (참고용)")
data = analyze_document(data["원문"], data)
pretty(data["NLP분석결과"])
print("\n※ 원문에 최종 수치가 전혀 없으므로, 이번에는 키워드가 실제 운영 이슈(프로모션,")
print("  배송 지연, 신제품 등)를 반영합니다 — 예전처럼 결론 문장을 그대로 되뽑는 게 아닙니다.")
다음_단계()

구분("4단계 (Ch05, 이번 실습의 핵심). 표본매출 + 이력만으로 전부 계산하기")
지표결과 = build_indicators(data["표본매출"], data["이력"], data["연월"])
data.update(지표결과)
print("계산지표 (표본매출을 합산하고, 이력과 비교해서 나온 값 — 입력 파일에는 없었음):")
pretty(data["계산지표"])
print("\n품목별지표 (표본매출을 품목별로 합산·정렬한 결과):")
pretty(data["품목별지표"])
print("\n역대최대여부:", data["역대최대여부"], " / 최근3개월증감률:", data["최근3개월증감률"])
print("\n특이점목록:")
pretty(data["통계해석결과"]["특이점목록"])
print("\n해석문장:")
pretty(data["통계해석결과"]["해석문장"])
다음_단계()

구분("5단계 (Ch06). 그래프 생성 — 막대·원형·꺾은선")
data["시각자료설명"] = build_visual_descriptions(data)
for 항목 in data["시각자료설명"]:
    print(f"- [{항목['그래프유형']}] {항목['소주제']}: {항목['이미지경로']}")
    print(f"    설명문: {항목['설명문']}")
다음_단계()

구분("6단계 (Ch04, 실제 API 호출). 참고용 3줄요약 + 제목후보 생성")
data["요약결과"] = generate_summary(data)
pretty(data["요약결과"])
다음_단계()

구분("7단계 (Ch07, 실제 API 호출). 제목·부제·리드문 생성")
data["헤드라인"] = generate_headline_set(data)
pretty(data["헤드라인"])
다음_단계()

구분("8단계 (Ch08, 실제 API 호출). 본문 단락 생성")
data["본문"] = generate_body_paragraphs(data)
for 단락 in data["본문"]:
    print(f"\n[{단락['소주제']}]")
    print(단락["내용"])
다음_단계()

구분("9단계 (Ch09, 실제 API 호출). 문체 통일 + 자동 검수 + AI 감수")
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

구분("10단계 (Ch10). 최종 문서 저장")
save_final_document(data)
print(f"저장 완료: output/{data['문서정보']['제목']}.txt")

구분("실습 종료")
print("수고하셨습니다! output/, images/ 폴더의 결과물을 직접 열어 확인해보세요.")
print("이번에는 입력 파일 어디에도 총거래액·증감률이 없었다는 점을 다시 확인해보세요")
print("(data/raw/반려동물용품_2026_03_원자료.xlsx의 '표본매출' 시트를 열어보면 됩니다).")
