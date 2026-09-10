from modules.clean import clean_and_structure, mask_sensitive_info


def test_clean_and_structure_normalizes_units_and_whitespace():
    raw = {
        "제목": "2026년 1월 온라인쇼핑 동향",
        "공표일자": "2026-03-01",
        "계산지표": {"총거래액": 201250, "전월대비증감률": 1.5},
        "핵심내용": ["온라인쇼핑 거래액 역대 최대 달성"],
        "원문": "2026년  1월 온라인쇼핑   거래액은   201250억원으로   전월대비  1.5%   증가하였음.(주:잠정치)",
    }
    result = clean_and_structure(raw)

    assert result["문서정보"]["제목"] == "2026년 1월 온라인쇼핑 동향"
    assert result["계산지표"]["총거래액"] == 201250
    assert "  " not in result["원문"]  # 중복 공백 제거
    assert "(주:" not in result["원문"]  # 괄호 주석 제거
    assert "억원" not in result["원문"]  # 단위 표기 통일
    assert "억 원" in result["원문"]


def test_mask_sensitive_info_masks_rrn_and_phone():
    text = "담당자 연락처는 010-1234-5678이며 주민등록번호는 900101-1234567입니다."
    masked = mask_sensitive_info(text)
    assert "900101-1234567" not in masked
    assert "010-1234-5678" not in masked
    assert "******-*******" in masked
    assert "010-****-****" in masked
