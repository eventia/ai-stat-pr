"""4/7차시: 프롬프트 조립 함수와 방어적 JSON 파싱에 대한 단위 테스트.
LLM을 실제로 호출하지 않고, 프롬프트 문자열에 필요한 정보가 빠짐없이
들어가는지와 parse_json_response의 방어적 파싱만 검증한다."""
import pytest

from modules.write import (
    build_headline_prompt,
    build_summary_prompt,
    parse_json_response,
    select_core_indicators,
)


def test_build_summary_prompt_includes_indicators_and_keywords():
    data = {
        "계산지표": {"총거래액": 201250, "전월대비증감률": 1.5, "전년동월대비증감률": 8.7},
        "NLP분석결과": {"핵심키워드": ["온라인쇼핑", "거래액"], "주요문장": ["역대 최대치를 기록하였다."]},
    }
    prompt = build_summary_prompt(data)

    assert "201250억 원" in prompt
    assert "1.5% 증가" in prompt
    assert "8.7% 증가" in prompt
    assert "온라인쇼핑, 거래액" in prompt
    assert "역대 최대치를 기록하였다." in prompt


def test_build_summary_prompt_handles_no_main_sentence():
    data = {
        "계산지표": {"총거래액": 100, "전월대비증감률": 0, "전년동월대비증감률": 0},
        "NLP분석결과": {"핵심키워드": [], "주요문장": []},
    }
    prompt = build_summary_prompt(data)
    assert '주요문장: ""' in prompt


def test_select_core_indicators_filters_to_required_fields_only():
    전체지표 = {
        "총거래액": 201250,
        "전월대비증감률": 1.5,
        "전년동월대비증감률": 8.7,
        "부가지표_기타": 999,
    }
    core = select_core_indicators(전체지표)
    assert core == {"총거래액": 201250, "전월대비증감률": 1.5, "전년동월대비증감률": 8.7}


def test_build_headline_prompt_attaches_units_and_forbids_unit_conversion():
    core = {"총거래액": 201250, "전월대비증감률": 1.5, "전년동월대비증감률": 8.7}
    prompt = build_headline_prompt(core, ["역대 최대치 경신"])

    # 단위가 붙어야 LLM이 임의로 조/억 단위를 다시 계산하지 않는다
    # (콤마 포맷은 9차시 표기 검수의 "콤마 누락" 검사를 통과시키기 위해 필요하다)
    assert "201,250억 원" in prompt
    assert "1.5%" in prompt
    assert "8.7%" in prompt
    assert "역대 최대치 경신" in prompt
    assert "환산" in prompt  # 단위 환산 금지 지시가 포함되어야 함


def test_build_headline_prompt_includes_reference_titles_when_given():
    """검토 보고서(REVIEW_Ch02-10.md, A-3) 대응: 4차시 요약 단계의 제목후보를
    참고용으로만(사실 확정에는 영향 없이) 헤드라인 프롬프트에 전달할 수 있어야 한다."""
    core = {"총거래액": 201250, "전월대비증감률": 1.5, "전년동월대비증감률": 8.7}
    prompt = build_headline_prompt(core, ["역대 최대치 경신"], ["1월 거래액 역대 최대"])
    assert "1월 거래액 역대 최대" in prompt
    assert "그대로 채택하지 않아도" in prompt


def test_build_headline_prompt_omits_reference_section_when_not_given():
    core = {"총거래액": 201250, "전월대비증감률": 1.5, "전년동월대비증감률": 8.7}
    prompt = build_headline_prompt(core, ["역대 최대치 경신"])
    assert "참고(4차시" not in prompt


def test_parse_json_response_extracts_object_ignoring_surrounding_text():
    response = '여기 결과입니다:\n```json\n{"제목": "테스트"}\n```\n감사합니다.'
    assert parse_json_response(response) == {"제목": "테스트"}


def test_parse_json_response_extracts_array():
    response = '[{"유형": "수치 오류", "위치": "1문단"}]'
    result = parse_json_response(response)
    assert result == [{"유형": "수치 오류", "위치": "1문단"}]


def test_parse_json_response_extracts_array_of_multiple_objects_in_code_fence():
    """실제 review_press_release 응답에서 재현된 버그: 배열 안에 객체가 여러 개
    있으면({...}, {...}) 예전 정규식은 배열을 감싸는 대괄호 대신 안쪽 객체의
    중괄호만 잘라내 "Extra data" 파싱 오류를 냈다."""
    response = (
        '여기 지적사항입니다.\n```json\n[\n'
        '  {"유형": "수치 오류", "위치": "1문단", "지적사항": "..."},\n'
        '  {"유형": "논리적 비약", "위치": "2문단", "지적사항": "..."}\n'
        ']\n```'
    )
    result = parse_json_response(response)
    assert len(result) == 2
    assert result[0]["유형"] == "수치 오류"
    assert result[1]["유형"] == "논리적 비약"


def test_parse_json_response_raises_on_non_json_text():
    with pytest.raises(Exception):
        parse_json_response("죄송하지만 답변할 수 없습니다.")
