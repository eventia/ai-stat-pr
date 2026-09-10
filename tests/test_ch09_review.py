import modules.write as write_module
from modules.review import (
    assemble_full_text,
    check_formatting_errors,
    cross_check_all_numbers,
    find_unverified_numbers,
    review_press_release,
    verify_numbers,
)


def test_verify_numbers_passes_on_faithful_sentence_with_commas_and_dates(sample_data):
    sentence = "2026년 1월 온라인쇼핑 거래액은 201,250억 원을 기록하였다."
    assert verify_numbers(sentence, sample_data) is True


def test_verify_numbers_passes_on_percentages(sample_data):
    sentence = "이는 전월 대비 1.5%, 전년동월대비 8.7% 증가한 수치이다."
    assert verify_numbers(sentence, sample_data) is True


def test_verify_numbers_fails_on_hallucinated_number(sample_data):
    sentence = "온라인쇼핑 거래액은 999,999억 원을 기록하였다."
    assert verify_numbers(sentence, sample_data) is False


def test_verify_numbers_supports_pumok_list_schema(sample_data):
    # 계산지표가 아니라 품목별지표(리스트)에만 있는 수치도 검증 가능해야 한다
    sentence = "품목별로는 의류가 65,000억 원으로 가장 많이 거래되어 1위를 차지하였고, 가전이 52,000억 원으로 그 뒤를 이었다."
    assert verify_numbers(sentence, sample_data) is True


def test_verify_numbers_passes_when_negative_rate_written_as_decrease():
    """원본 수치가 음수(-1.5)여도 "1.5% 감소"처럼 부호 없이 자연스럽게 쓴
    문장은 통과해야 한다. 가격정보 API 연동 중 실제로 겪은 버그: 기존
    온라인쇼핑 예시는 증감률이 항상 양수였던 탓에 이 문제가 드러나지 않았다."""
    data = {"계산지표": {"전년동월대비증감률": -1.5}}
    sentence = "전년동월대비로는 1.5% 감소한 것으로 나타났다."
    assert verify_numbers(sentence, data) is True


def test_cross_check_all_numbers_returns_dict_with_pass_flag(sample_data):
    text = "온라인쇼핑 거래액은 201,250억 원으로 8.7% 증가하였다."
    result = cross_check_all_numbers(text, sample_data)
    assert result["통과"] is True
    assert result["불일치수치"] == []


def test_cross_check_all_numbers_detects_mismatch(sample_data):
    text = "온라인쇼핑 거래액은 123,456억 원으로 증가하였다."
    result = cross_check_all_numbers(text, sample_data)
    assert result["통과"] is False
    assert len(result["불일치수치"]) > 0


def test_check_formatting_errors_flags_missing_space():
    errors = check_formatting_errors("201250억원으로 집계되었다.")
    assert any("억원" in e for e in errors)


def test_check_formatting_errors_no_false_positive_when_space_present():
    errors = check_formatting_errors("201,250억 원으로 집계되었다.")
    assert errors == []


def test_check_formatting_errors_flags_missing_comma():
    errors = check_formatting_errors("거래액은 201250억 원이다.")
    assert any("콤마" in e for e in errors)


def test_review_press_release_returns_fallback_on_truncated_response(monkeypatch):
    """실제 실습 중 재현된 크래시의 회귀 테스트: AI 감수 응답이 max_tokens 한도에
    걸려 JSON이 중간에 잘리면(닫는 괄호가 아예 없으면) parse_json_response가
    ValueError를 던져 파이프라인 전체가 멈췄다. 이제는 예외 대신 안내 항목을
    반환해 나머지 검수 결과(표기·수치 검증)는 그대로 볼 수 있어야 한다."""
    class _FakeContentBlock:
        text = '[{"유형": "수치 오류", "위치": "1문단", "지적사항": "이어서 계속 작성 중이었는데'  # 닫는 괄호 없이 잘림

    class _FakeMessage:
        content = [_FakeContentBlock()]

    monkeypatch.setattr(write_module.client.messages, "create", lambda **kwargs: _FakeMessage())

    result = review_press_release("아무 최종본", {"계산지표": {}})
    assert isinstance(result, list)
    assert len(result) == 1
    assert "파싱 실패" in result[0]["유형"]


def test_assemble_full_text_joins_headline_and_body():
    data = {
        "헤드라인": {"리드문": "리드문 문장입니다."},
        "본문": [{"소주제": "A", "내용": "본문 단락 1"}, {"소주제": "B", "내용": "본문 단락 2"}],
    }
    full_text = assemble_full_text(data)
    assert "리드문 문장입니다." in full_text
    assert "본문 단락 1" in full_text
    assert "본문 단락 2" in full_text
