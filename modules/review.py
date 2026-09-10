"""4차시: 수치 검증, 9차시: 문체 통일·표기 검수·AI 감수."""
import json
import re

from modules.write import client, MODEL_NAME, parse_json_response


def assemble_full_text(data: dict) -> str:
    """헤드라인의 리드문과 본문 전체 단락을 하나의 텍스트로 합친다."""
    return data["헤드라인"]["리드문"] + "\n\n" + "\n\n".join(p["내용"] for p in data["본문"])


# ---- 4차시: 숫자 검증 (품목별지표/계산지표 스키마 모두 지원) ----

def _collect_valid_numbers(data: dict) -> set:
    # 음수 증감률(예: -1.5)은 문장에서 보통 부호 없이 "1.5% 감소"처럼 표현되므로,
    # 절댓값도 함께 등록해 둔다. 부호까지 그대로 비교하면 "하락/감소"로 쓴
    # 정상적인 문장이 전부 "불일치"로 오탐된다 (기존 온라인쇼핑 예시는 증감률이
    # 항상 양수였던 탓에 이 문제가 드러나지 않았을 뿐, 가격 데이터처럼 실제로
    # 하락이 발생하면 바로 나타나는 버그였다).
    valid = set()
    for v in data.get("계산지표", {}).values():
        if isinstance(v, (int, float)):
            valid.add(str(v))
            valid.add(str(abs(v)))
    for row in data.get("품목별지표", []):
        for v in row.values():
            if isinstance(v, (int, float)):
                valid.add(str(v))
                valid.add(str(abs(v)))
    return valid


def _is_low_risk_number(token: str) -> bool:
    """연도(4자리)·순위·개월 수 등 1~2자리 숫자는 문맥상 자연스럽게 등장하므로 대조 대상에서 제외한다."""
    if "." in token:
        return False  # 소수(증감률 등)는 항상 정밀 대조
    if len(token) == 4 and token.isdigit() and 1900 <= int(token) <= 2100:
        return True
    return len(token) <= 2


def find_unverified_numbers(text: str, data: dict) -> list:
    valid_numbers = _collect_valid_numbers(data)
    unmatched = []
    for raw in re.findall(r'\d[\d,]*\.?\d*', text):
        cleaned = raw.replace(",", "")
        if _is_low_risk_number(cleaned):
            continue
        if cleaned not in valid_numbers:
            unmatched.append(raw)
    return unmatched


def verify_numbers(summary_text: str, source_data: dict) -> bool:
    return len(find_unverified_numbers(summary_text, source_data)) == 0


def cross_check_all_numbers(final_text: str, data: dict) -> dict:
    unmatched = find_unverified_numbers(final_text, data)
    return {"통과": len(unmatched) == 0, "불일치수치": unmatched}


# ---- 9차시: 문체 통일 ----

def unify_style(draft_text: str) -> str:
    prompt = f"""아래 초안을 통계청 보도자료 표준 문체로 통일해 주세요.
모든 문장을 객관적 서술체("~하였다")로 통일하고, 주관적 수식어는 제거하되
사실과 수치는 절대 변경하지 마세요. 숫자는 원문에 쓰인 표기(예: 201,250억 원)를
그대로 유지하고, 조/억 단위 환산 등으로 다시 쓰지 마세요.
수정한 보도자료 본문만 출력하고, 수정 내용에 대한 설명이나 목록은 덧붙이지 마세요.

초안: {draft_text}"""

    message = client.messages.create(
        model=MODEL_NAME,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


# ---- 9차시: 표기 오류 자동 검수 ----

def check_formatting_errors(text: str) -> list:
    """정규표현식 기반 1차 표기 오류 필터. 완벽하지 않으므로 최종 확인은 사람이 담당한다."""
    errors = []
    if "억원" in text:
        errors.append("단위 표기 오류: '억원'은 '억 원'으로 띄어써야 함")
    if re.search(r'(?<!\d)\d{5,}(?!\d)', text):
        errors.append("천 단위 구분 콤마 누락 의심: 콤마 없는 5자리 이상 숫자 발견")
    if re.search(r'비중.{0,10}(증가|감소|확대|축소)', text) and "%p" not in text:
        errors.append("비중(구성비) 변화 표현에는 %p 표기가 필요한지 확인 필요")
    return errors


# ---- 9차시: AI 감수 ----

def review_press_release(final_text: str, data: dict) -> list:
    # 감수자가 "역대 최대"·"몇 개월 연속 증가" 같은 표현을 근거 없는 과장으로
    # 오판하지 않도록, 계산지표뿐 아니라 통계해석결과·품목별지표 등 관련 근거
    # 자료를 전부 함께 제공한다 (이전에는 계산지표만 넘겨져 품목별지표가 있어도
    # 감수자에게 전달되지 않는 문제가 있었다).
    근거자료 = {
        k: data[k]
        for k in ("계산지표", "통계해석결과", "품목별지표", "역대최대여부", "최근3개월증감률")
        if k in data
    }
    prompt = f"""당신은 통계 보도자료 전문 감수자입니다. 아래 원본 데이터와 완성된
보도자료를 대조하여 수치 오류, 과장된 표현, 문체 불일치, 논리적 비약을 지적해 주세요.
지적사항은 최대 5건까지, 항목당 한 문장으로 간결하게 작성하십시오.

원본 데이터: {json.dumps(근거자료, ensure_ascii=False)}
완성된 보도자료: {final_text}

JSON 배열 형식으로만 답하십시오. 예: [{{"유형": "...", "위치": "...", "지적사항": "..."}}]"""

    message = client.messages.create(
        model=MODEL_NAME,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    try:
        return parse_json_response(message.content[0].text)
    except (ValueError, json.JSONDecodeError):
        # 실제로 겪은 문제: 감수 응답이 max_tokens 한도에 걸려 JSON이 중간에
        # 잘리면 parse_json_response가 닫는 괄호를 못 찾아 예외를 던지고 전체
        # 파이프라인이 멈췄다. 이 단계는 9차시 3단계 검수 안전장치 중 "AI 감수"
        # 하나일 뿐이므로, 파싱에 실패해도 나머지 검수(표기·수치 검증)는 이미
        # 끝난 상태로 결과를 보여줄 수 있도록 예외 대신 안내 항목을 반환한다.
        return [{
            "유형": "감수 응답 파싱 실패",
            "위치": "-",
            "지적사항": "AI 감수 응답이 잘리거나 JSON 형식이 아니어서 자동으로 해석하지 못했습니다. "
                       "표기오류검사·수치교차검증 결과로 우선 판단하고, 필요하면 재실행하십시오.",
        }]
