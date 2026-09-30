"""4차시~: AI가 만든 문장 속 숫자를 원본 데이터와 교차 검증한다."""
import re


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
