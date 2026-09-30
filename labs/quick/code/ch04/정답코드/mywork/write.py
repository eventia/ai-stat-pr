"""4차시~: Claude API로 문장을 생성한다(계산은 하지 않고, 계산된 값을 문장으로만 옮긴다)."""
import json
import re

import anthropic
from dotenv import load_dotenv

from mywork.config import INDICATOR_UNITS

load_dotenv()  # 반드시 client 생성보다 먼저 호출해야 .env의 ANTHROPIC_API_KEY가 읽힌다
client = anthropic.Anthropic()
MODEL_NAME = "claude-sonnet-5-5"  # 모델 ID는 이 한 곳에서만 관리한다

SYSTEM_PROMPT = (
    "당신은 국가데이터처 보도자료 작성 담당자입니다. 제공된 계산지표와 문장만을 근거로 사용하고, "
    "제공되지 않은 숫자는 절대로 만들어내지 마십시오. 객관적 사실만 서술하고 수식어를 남용하지 마십시오."
)


def format_value(field: str, value) -> str:
    text = f"{value:,}" if isinstance(value, int) else f"{value}"
    return text + INDICATOR_UNITS.get(field, "")


def call_claude(prompt: str, system: str = SYSTEM_PROMPT, max_tokens: int = 2000) -> str:
    message = client.messages.create(
        model=MODEL_NAME,
        max_tokens=max_tokens,
        system=system,
        thinking={"type": "between_tools"},  # 추가 사고(thinking) 없이 바로 답하게 한다
        messages=[{"role": "user", "content": prompt}],
    )
    if message.stop_reason == "refusal":
        raise RuntimeError("모델이 요청을 거절했습니다.")
    return "".join(block.text for block in message.content if block.type == "text").strip()


def parse_json_response(response_text: str):
    match = re.search(r"(\{.*\}|\[.*\])", response_text, re.DOTALL)
    json_text = match.group(0) if match else response_text
    return json.loads(json_text)


def _change_text(rate: float) -> str:
    return f"{abs(rate)}% {'증가' if rate >= 0 else '감소'}"


def build_summary_prompt(data: dict) -> str:
    지표 = data["계산지표"]
    키워드 = ", ".join(data["NLP분석결과"]["핵심키워드"])
    주요문장 = " / ".join(data["NLP분석결과"]["주요문장"])
    return f"""다음 자료를 참고하여 3줄 요약과 제목 후보 3개를 작성해 주세요.
숫자는 아래에 적힌 표기(콤마·단위 포함) 그대로 쓰고, 새로 계산하거나 단위를 바꾸지 마십시오.

계산지표: 총거래액 {format_value('총거래액', 지표['총거래액'])}, 전월대비 {_change_text(float(지표['전월대비증감률']))}, 전년동월대비 {_change_text(float(지표['전년동월대비증감률']))}
핵심키워드: {키워드}
주요문장: "{주요문장}"

[예시]
입력: 총거래액 1,500억 원, 전월대비 2.1% 감소
출력: {{"삼줄요약": ["온라인쇼핑 거래액은 1,500억 원으로 집계되었다.", "이는 전월 대비 2.1% 감소한 수치이다.", "거래액은 감소세로 전환되었다."], "제목후보": ["온라인쇼핑 거래액 2.1% 감소", "온라인쇼핑 거래액 감소 전환", "온라인쇼핑 거래액 1,500억 원"]}}

결과는 반드시 아래 JSON 형식으로만 출력하십시오. 다른 설명은 붙이지 마십시오.
{{"삼줄요약": ["문장1", "문장2", "문장3"], "제목후보": ["제목1", "제목2", "제목3"]}}"""


def generate_summary(data: dict) -> dict:
    return parse_json_response(call_claude(build_summary_prompt(data)))
