"""4차시~: AI가 만든 문장 속 숫자를 원본 데이터와 교차 검증한다."""
import json
import re

from mywork.write import call_claude, parse_json_response


def _collect_valid_numbers(data: dict) -> set:
    valid = set()
    values = list(data.get("계산지표", {}).values())
    for row in data.get("품목별지표", []):
        values += list(row.values())
    for v in values:
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            continue
        valid.add(str(v))
        valid.add(str(abs(v)))  # "-2.1" 은 문장에서 "2.1% 감소"로 쓰이므로 절댓값도 등록
    return valid


def _is_low_risk_number(token: str) -> bool:
    if "." in token:
        return False
    if len(token) == 4 and token.isdigit() and 1900 <= int(token) <= 2100:
        return True
    return len(token) <= 2


def find_unverified_numbers(text: str, data: dict) -> list:
    valid_numbers = _collect_valid_numbers(data)
    unmatched = []
    for raw in re.findall(r"\d[\d,]*\.?\d*", text):
        cleaned = raw.replace(",", "").rstrip(".")
        if _is_low_risk_number(cleaned):
            continue
        if cleaned not in valid_numbers:
            unmatched.append(raw)
    return unmatched


def verify_numbers(summary_text: str, source_data: dict) -> bool:
    return len(find_unverified_numbers(summary_text, source_data)) == 0


# ---- 9차시: 표기 검수·전체 수치 교차 검증·AI 감수 ----
def check_formatting_errors(text: str) -> list:
    errors = []
    if re.search(r"\d억원", text):
        errors.append("단위 표기 오류: '억원'은 '억 원'으로 띄어써야 함")
    if re.search(r"(?<![\d,.])\d{5,}(?![\d,])", text):
        errors.append("천 단위 구분 콤마 누락 의심: 콤마 없는 5자리 이상 숫자 발견")
    if re.search(r"비중.{0,10}(증가|감소|확대|축소)", text) and "%p" not in text:
        errors.append("비중(구성비) 변화 표현에는 %p 표기가 필요한지 확인 필요")
    return errors


def cross_check_all_numbers(final_text: str, data: dict) -> dict:
    unmatched = find_unverified_numbers(final_text, data)
    return {"통과": len(unmatched) == 0, "불일치수치": unmatched}


def review_press_release(final_text: str, data: dict) -> list:
    근거자료 = {k: data[k] for k in ("계산지표", "통계해석결과", "품목별지표", "역대최대여부", "최근3개월증감률") if k in data}
    prompt = f"""당신은 통계 보도자료 전문 감수자입니다. 아래 원본 데이터와 완성된 보도자료를 대조하여
수치 오류, 과장된 표현, 문체 불일치, 논리적 비약을 지적해 주세요.
지적사항은 최대 5건까지, 항목당 한 문장으로 간결하게 작성하십시오. 문제가 없으면 빈 배열 []을 출력하십시오.

원본 데이터: {json.dumps(근거자료, ensure_ascii=False)}
완성된 보도자료: {final_text}

JSON 배열 형식으로만 답하십시오. 예: [{{"유형": "...", "위치": "...", "지적사항": "..."}}]"""
    try:
        return parse_json_response(call_claude(prompt, system="당신은 통계 보도자료 전문 감수자입니다.", max_tokens=2000))
    except (ValueError, json.JSONDecodeError):
        return [{"유형": "감수 응답 파싱 실패", "위치": "-",
                 "지적사항": "AI 감수 응답이 잘리거나 JSON 형식이 아니어서 자동으로 해석하지 못했습니다."}]
