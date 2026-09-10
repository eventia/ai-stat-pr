"""7·8차시(응용): 가격정보 API 데이터로 헤드라인·본문 생성, 6차시(응용): 그래프 설명.

modules/write.py의 build_headline_prompt/REQUIRED_FIELDS는 "총거래액"(억 원)
전제로 고정되어 있어 "평균 판매가격"(원) 데이터에는 그대로 못 쓴다. 반면
parse_json_response/client/MODEL_NAME과 8차시의 expand_to_paragraph/
generate_body_paragraphs는 지표명에 의존하지 않는 진짜 범용 코드라 그대로
재사용한다. 기존 온라인쇼핑 동향 파이프라인(main.py, modules/write.py)은
이미 검증되어 있으므로 건드리지 않고, 이 모듈에 가격 데이터 전용 프롬프트만
새로 작성했다.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from modules.write import MODEL_NAME, client, generate_body_paragraphs, parse_json_response  # noqa: F401
from modules.price_stats import INDICATOR_NAME, INDICATOR_UNIT

REQUIRED_FIELDS = [INDICATOR_NAME, "전월대비증감률", "전년동월대비증감률"]
지표_단위 = {INDICATOR_NAME: INDICATOR_UNIT, "전월대비증감률": "%", "전년동월대비증감률": "%"}


def select_core_indicators(계산지표: dict) -> dict:
    return {k: v for k, v in 계산지표.items() if k in REQUIRED_FIELDS}


def build_headline_prompt(core: dict, special_points: list) -> str:
    # 콤마 포맷을 프롬프트에 미리 보여줘야 9차시 표기 검수(콤마 누락 검사)를
    # 통과하는 문장이 나온다 — 콤마 없이 정수만 주면 모델이 "32230원"처럼
    # 콤마 없이 그대로 베끼는 경우가 실제로 관찰되었다.
    지표문장 = ", ".join(f"{k} {v:,}{지표_단위.get(k, '')}" for k, v in core.items())
    특이점문장 = ", ".join(special_points) if special_points else "특별한 변동 없음"
    예시값 = f"{list(core.values())[0]:,}" if core else ""
    return f"""아래 정보를 바탕으로 다음 3가지를 JSON으로 작성해 주세요.
1) 제목(15자 내외, 핵심 수치 또는 등락 방향 포함)
2) 부제(제목과 중복되지 않는 두 번째 정보, 25자 내외)
3) 리드문(6하원칙에 따라 3~4문장)

숫자는 아래 핵심지표에 주어진 표기(콤마 포함)를 그대로 사용하고 반올림하거나
단위를 바꾸지 마세요 (예: {INDICATOR_NAME} {예시값}{INDICATOR_UNIT}).

핵심지표: {지표문장}
특이사항: {특이점문장}

결과는 반드시 아래 JSON 형식으로만 출력하십시오.
{{"제목": "...", "부제": "...", "리드문": "..."}}"""


def generate_headline_set(data: dict) -> dict:
    core = select_core_indicators(data["계산지표"])
    prompt = build_headline_prompt(core, data["통계해석결과"]["특이점목록"])

    message = client.messages.create(
        model=MODEL_NAME,
        max_tokens=600,
        system="통계청 보도자료 작성 담당자로서 제공된 사실만 사용하여 JSON 형식으로 답하십시오.",
        messages=[{"role": "user", "content": prompt}],
    )
    return parse_json_response(message.content[0].text)


# ---- 6차시(응용): 품목별 가격 비교 그래프·설명문 ----

def _가격_막대그래프_설명(품목별지표: list) -> str:
    정렬 = sorted(품목별지표, key=lambda r: r["당월평균가격"], reverse=True)
    최고, 최저 = 정렬[0], 정렬[-1]
    return (f"품목별 당월 평균 판매가격을 비교하면 {최고['품목']}이 {최고['당월평균가격']:,}원으로 "
            f"가장 높았으며, {최저['품목']}이 {최저['당월평균가격']:,}원으로 가장 낮았다.")


def _가격_등락률_설명(품목별지표: list) -> str:
    정렬 = sorted(품목별지표, key=lambda r: r["전월대비증감률"], reverse=True)
    상승, 하락 = 정렬[0], 정렬[-1]
    return (f"전월 대비 등락률을 살펴보면 {상승['품목']}이 {상승['전월대비증감률']}%로 가장 많이 올랐고, "
            f"{하락['품목']}이 {하락['전월대비증감률']}%로 가장 많이 내렸다.")


def build_price_visual_descriptions(data: dict) -> list:
    """품목별지표로 막대그래프 이미지를 생성하고, 소주제별 시각자료설명 목록을 반환한다.
    (modules/charts.py의 build_visual_descriptions와 같은 역할이지만, "비중"이 의미
    없는 가격 데이터 특성상 원형그래프 대신 등락률 비교로 구성했다.)"""
    os.makedirs("images", exist_ok=True)
    품목별지표 = data["품목별지표"]
    품목 = [row["품목"] for row in 품목별지표]
    가격 = [row["당월평균가격"] for row in 품목별지표]

    plt.rc("font", family="Malgun Gothic")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(품목, 가격, color="#4C72B0")
    ax.set_ylabel("평균 판매가격(원)")
    이미지경로 = f"images/{data['문서정보']['제목']}_품목별가격.png"
    plt.savefig(이미지경로, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return [
        {"소주제": "품목별 가격 비교", "그래프유형": "막대그래프", "이미지경로": 이미지경로,
         "설명문": _가격_막대그래프_설명(품목별지표)},
        {"소주제": "품목별 등락률", "그래프유형": "표", "이미지경로": 이미지경로,
         "설명문": _가격_등락률_설명(품목별지표)},
    ]
