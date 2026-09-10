"""2차시: 공공데이터포털 Open API 연동(modules/public_api.py) 단위 테스트.
실제 네트워크 호출 없이, XML 응답 파싱과 오류 처리만 검증한다."""
import pytest

import modules.public_api as api


class _FakeResponse:
    def __init__(self, text):
        self.text = text


ITEM_LIST_XML = """<?xml version="1.0" encoding="UTF-8"?>
<response>
  <body>
    <items>
      <item><rn>1</rn><ic>A01101</ic><in>쌀</in></item>
      <item><rn>2</rn><ic>A01102</ic><in>현미</in></item>
    </items>
    <numOfRows>2</numOfRows><pageNo>1</pageNo><totalCount>402</totalCount>
  </body>
</response>"""

PRICE_INFO_XML = """<?xml version="1.0" encoding="UTF-8"?>
<response>
  <header><resultCode>00</resultCode><resultMsg>NORMAL SERVICE.</resultMsg></header>
  <body>
    <ic>A01101</ic><in>쌀</in>
    <items>
      <item><pi>1</pi><pn>테스트 쌀 20kg</pn><sp>50000</sp><dp>49000</dp><bp>0</bp><sd>2026-08-01</sd></item>
    </items>
    <numOfRows>1</numOfRows><pageNo>1</pageNo><totalCount>1</totalCount>
  </body>
</response>"""

PRICE_INFO_MULTI_XML = """<?xml version="1.0" encoding="UTF-8"?>
<response>
  <header><resultCode>00</resultCode><resultMsg>NORMAL SERVICE.</resultMsg></header>
  <body>
    <ic>A01101</ic><in>쌀</in>
    <items>
      <item><pi>1</pi><pn>상품A</pn><sp>10000</sp><dp>10000</dp><bp>0</bp><sd>2026-08-01</sd></item>
      <item><pi>2</pi><pn>상품B</pn><sp>20000</sp><dp>20000</dp><bp>0</bp><sd>2026-08-01</sd></item>
      <item><pi>3</pi><pn>상품C</pn><sp>30000</sp><dp>30000</dp><bp>0</bp><sd>2026-08-01</sd></item>
    </items>
    <numOfRows>3</numOfRows><pageNo>1</pageNo><totalCount>3</totalCount>
  </body>
</response>"""

ERROR_XML = """<?xml version="1.0" encoding="UTF-8"?>
<response>
  <header><resultCode>21</resultCode><resultMsg>SERVICE ERROR.</resultMsg></header>
</response>"""


def test_get_price_item_list_parses_code_and_name(monkeypatch):
    monkeypatch.setattr(api.requests, "get", lambda *a, **k: _FakeResponse(ITEM_LIST_XML))
    items = api.get_price_item_list()
    assert items == [{"품목코드": "A01101", "품목명": "쌀"}, {"품목코드": "A01102", "품목명": "현미"}]


def test_get_price_info_parses_item_list(monkeypatch):
    monkeypatch.setattr(api.requests, "get", lambda *a, **k: _FakeResponse(PRICE_INFO_XML))
    result = api.get_price_info(item_code="A01101", start_date="20260801", end_date="20260831")
    assert result["품목명"] == "쌀"
    assert result["총건수"] == "1"
    assert result["상품목록"] == [
        {"상품ID": "1", "상품명": "테스트 쌀 20kg", "판매가격": "50000",
         "할인가격": "49000", "가격일자": "2026-08-01"}
    ]


def test_get_price_info_raises_on_error_result_code(monkeypatch):
    monkeypatch.setattr(api.requests, "get", lambda *a, **k: _FakeResponse(ERROR_XML))
    with pytest.raises(RuntimeError, match="21"):
        api.get_price_info(item_code="A01101", start_date="20260801", end_date="20260831")


def test_get_average_price_computes_mean_of_sample(monkeypatch):
    monkeypatch.setattr(api.requests, "get", lambda *a, **k: _FakeResponse(PRICE_INFO_MULTI_XML))
    result = api.get_average_price("A01101", "20260801", "20260831")
    assert result["평균가격"] == 20000  # (10000+20000+30000)/3
    assert result["표본건수"] == 3
    assert result["전체건수"] == 3


def test_get_average_price_returns_none_when_no_data(monkeypatch):
    empty_xml = PRICE_INFO_XML.replace(
        '<item><pi>1</pi><pn>테스트 쌀 20kg</pn><sp>50000</sp><dp>49000</dp><bp>0</bp><sd>2026-08-01</sd></item>',
        "",
    ).replace("<totalCount>1</totalCount>", "<totalCount>0</totalCount>")
    monkeypatch.setattr(api.requests, "get", lambda *a, **k: _FakeResponse(empty_xml))
    result = api.get_average_price("A01101", "20260801", "20260831")
    assert result["평균가격"] is None
    assert result["표본건수"] == 0


def test_service_key_is_unquoted_even_if_already_url_encoded(monkeypatch):
    """.env에 이미 URL 인코딩된 "Encoding" 키를 넣어도 이중 인코딩되지 않아야 한다."""
    monkeypatch.setenv("PUBLIC_API_KEY", "abc%2Bdef%3D%3D")
    import importlib
    reloaded = importlib.reload(api)
    assert reloaded.SERVICE_KEY == "abc+def=="
    importlib.reload(api)  # 다른 테스트에 영향 주지 않도록 원상 복구
