"""4차시: LLM 기반 요약, 7차시: 헤드라인 생성, 8차시: 본문 생성."""
import json

import anthropic

from modules.config import REQUIRED_FIELDS, INDICATOR_UNITS as 지표_단위

client = anthropic.Anthropic()  # .env의 ANTHROPIC_API_KEY 자동 로드
MODEL_NAME = "claude-sonnet-4-5"  # 실습 시점에 console.anthropic.com에서 최신 모델 ID를 확인하여 교체


def parse_json_response(response_text: str):
    """모델 응답에서 코드펜스나 부연 설명이 섞여 있어도 JSON 객체({})나 배열([])만 추출해 파싱한다.

    처음 등장하는 '{' 또는 '[' 중 먼저 나오는 쪽을 시작점으로 삼고, 그와 짝을
    이루는 닫는 괄호(문자열 전체에서 마지막으로 등장하는 같은 종류의 괄호)까지를
    잘라 파싱한다. 이전에는 정규식 `\\{.*\\}|\\[.*\\]`로 항상 객체({}) 쪽을 먼저
    시도했는데, 응답이 [{"a":1}, {"b":2}]처럼 배열이면 배열을 감싸는 대괄호를
    무시하고 내부 객체의 중괄호만 잘라내 "Extra data" 파싱 오류가 발생했다.
    """
    open_pos, open_char = None, None
    for i, ch in enumerate(response_text):
        if ch in "{[":
            open_pos, open_char = i, ch
            break
    if open_pos is None:
        return json.loads(response_text)

    close_char = "}" if open_char == "{" else "]"
    close_pos = response_text.rindex(close_char)
    return json.loads(response_text[open_pos:close_pos + 1])


# ---- 4차시: 요약 ----

def build_summary_prompt(data: dict) -> str:
    지표 = data["계산지표"]
    키워드 = ", ".join(data["NLP분석결과"]["핵심키워드"])
    주요문장 = data["NLP분석결과"]["주요문장"][0] if data["NLP분석결과"]["주요문장"] else ""

    return f"""다음 자료를 참고하여 3줄 요약과 제목 후보 3개를 작성해 주세요.
계산지표: 총거래액 {지표['총거래액']}억 원, 전월대비 {지표['전월대비증감률']}% 증가,
전년동월대비 {지표['전년동월대비증감률']}% 증가
핵심키워드: {키워드}
주요문장: "{주요문장}"

결과는 반드시 아래 JSON 형식으로만 출력하십시오.
{{"삼줄요약": ["문장1", "문장2", "문장3"], "제목후보": ["제목1", "제목2", "제목3"]}}"""


def generate_summary(data: dict) -> dict:
    prompt = build_summary_prompt(data)
    message = client.messages.create(
        model=MODEL_NAME,
        max_tokens=500,
        system="당신은 통계청 보도자료 작성 담당자입니다. 제공된 숫자만 사용하고 "
               "반드시 JSON 형식으로만 답하십시오.",
        messages=[{"role": "user", "content": prompt}],
    )
    return parse_json_response(message.content[0].text)


# ---- 7차시: 헤드라인 ----

def select_core_indicators(계산지표: dict) -> dict:
    return {k: v for k, v in 계산지표.items() if k in REQUIRED_FIELDS}


def build_headline_prompt(core: dict, special_points: list, 참고_제목후보: list = None) -> str:
    # 천 단위 콤마를 미리 넣어 프롬프트에 보여줘야, 실제로 이 값이 그대로
    # 인용됐을 때 9차시 check_formatting_errors의 "콤마 누락" 검사도 통과한다
    # (콤마 없이 숫자만 주면 모델이 "20조 1,250억원"처럼 임의로 재포맷하거나
    # 반대로 "201250원"처럼 콤마 없이 쓰는 경우가 실제로 관찰되었다).
    지표문장 = ", ".join(f"{k} {v:,}{지표_단위.get(k, '')}" for k, v in core.items())
    특이점문장 = ", ".join(special_points)

    # 검토 보고서(REVIEW_Ch02-10.md, A-3) 대응: 3~4차시(NLP 키워드·LLM 3줄요약)의
    # 산출물이 최종 산출물과 완전히 단절되어 있던 문제를 가볍게 연결한다. 다만
    # "사실 확정은 5차시 계산 결과가 담당한다"는 원래 설계를 유지하기 위해,
    # 여기서는 새로운 숫자를 들여오지 않고 "표현 아이디어"로만 참고시킨다 —
    # 그대로 채택하지 않아도 되며, 최종 문장은 여전히 verify_numbers로 검증된다.
    참고문장 = ""
    if 참고_제목후보:
        참고문장 = ("\n참고(4차시 요약 단계에서 생성된 제목 아이디어, 그대로 채택하지 않아도 됨): "
                    + ", ".join(참고_제목후보))

    return f"""아래 정보를 바탕으로 다음 3가지를 JSON으로 작성해 주세요.
1) 제목(15자 내외, 핵심 수치 또는 증감 방향 포함)
2) 부제(제목과 중복되지 않는 두 번째 정보, 25자 내외)
3) 리드문(6하원칙에 따라 3~4문장)

숫자는 아래 핵심지표에 주어진 표기(예: 201,250억 원)를 콤마까지 그대로 사용하고,
조 단위로 환산하거나 자릿수를 다시 계산하지 마세요.

핵심지표: {지표문장}
특이사항: {특이점문장}{참고문장}

결과는 반드시 아래 JSON 형식으로만 출력하십시오.
{{"제목": "...", "부제": "...", "리드문": "..."}}"""


def generate_headline_set(data: dict) -> dict:
    core = select_core_indicators(data["계산지표"])
    참고_제목후보 = data.get("요약결과", {}).get("제목후보", [])
    prompt = build_headline_prompt(core, data["통계해석결과"]["특이점목록"], 참고_제목후보)

    message = client.messages.create(
        model=MODEL_NAME,
        max_tokens=600,
        system="통계청 보도자료 작성 담당자로서 제공된 사실만 사용하여 JSON 형식으로 답하십시오.",
        messages=[{"role": "user", "content": prompt}],
    )
    return parse_json_response(message.content[0].text)


# ---- 8차시: 본문 ----

def expand_to_paragraph(subtopic: str, source_facts: str) -> str:
    prompt = f"""아래 그래프 설명 소재를 바탕으로 통계 보도자료의 본문 한 단락(3~4문장)을
작성해 주세요. 두괄식 구조를 따르고, 제공된 사실 외의 내용은 추가하지 마세요.

소주제: {subtopic}
설명 소재: {source_facts}"""

    message = client.messages.create(
        model=MODEL_NAME,
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def generate_body_paragraphs(data: dict) -> list:
    """시각자료설명 목록을 소주제별 본문 단락으로 확장하고, 표준 '본문' 스키마로 반환한다."""
    연결어_목록 = ["", "한편, ", "아울러, "]
    본문 = []
    for i, 항목 in enumerate(data.get("시각자료설명", [])):
        subtopic = 항목["소주제"]
        내용 = expand_to_paragraph(subtopic, 항목["설명문"])
        if i > 0:
            내용 = 연결어_목록[min(i, len(연결어_목록) - 1)] + 내용[0].lower() + 내용[1:]
        본문.append({"소주제": subtopic, "내용": 내용})
    return 본문
