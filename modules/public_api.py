"""2차시: 공공데이터포털(data.go.kr) "온라인 수집 가격 정보" Open API 연동.

실제 발급받은 키로 검증됨. Ch02-PT내용.md가 원래 가정했던 가상의 API와 달리
이 API는 다음과 같은 특징이 있다 (자세한 발견 경위는 IMPLEMENTATION_LOG.md
"10. 5차 세션" 참고):

1. 응답이 JSON이 아니라 XML이다.
2. data.go.kr이 제공하는 "인코딩(Encoding)" 키를 그대로 쓰면 `requests`가
   한 번 더 인코딩해 이중 인코딩 오류가 나므로, 사용 전에 `unquote()`로
   디코딩해 둔다 (디코딩 키를 다시 디코딩해도 문제없음).
3. `getPriceInfo`는 개별 상품의 낱개 판매가격 목록만 준다 — 총거래액 같은
   집계 통계가 아니므로, 보도자료에 쓰려면 평균가격 등을 직접 계산해야 한다
   (이 계산은 modules/price_stats.py가 담당한다).
"""
import os
import statistics
import xml.etree.ElementTree as ET
from urllib.parse import unquote

import requests
from dotenv import load_dotenv

load_dotenv()
SERVICE_KEY = unquote(os.getenv("PUBLIC_API_KEY", ""))
BASE_URL = "https://apis.data.go.kr/1240000/bpp_openapi"


def get_price_item_list(page_no: int = 1, num_of_rows: int = 10) -> list:
    """전체 품목의 코드와 명칭 목록을 조회한다."""
    response = requests.get(
        f"{BASE_URL}/getPriceItemList",
        params={"serviceKey": SERVICE_KEY, "pageNo": page_no, "numOfRows": num_of_rows},
        timeout=15,
    )
    root = ET.fromstring(response.text)
    return [
        {"품목코드": item.findtext("ic"), "품목명": item.findtext("in")}
        for item in root.findall(".//item")
    ]


def get_price_info(item_code: str, start_date: str, end_date: str,
                    page_no: int = 1, num_of_rows: int = 10) -> dict:
    """품목 코드와 조회 기간(YYYYMMDD, 최대 30일, D-2까지)을 기준으로 가격정보를 조회한다."""
    response = requests.get(
        f"{BASE_URL}/getPriceInfo",
        params={
            "serviceKey": SERVICE_KEY,
            "itemCode": item_code,
            "startDate": start_date,
            "endDate": end_date,
            "pageNo": page_no,
            "numOfRows": num_of_rows,
        },
        timeout=15,
    )
    root = ET.fromstring(response.text)
    result_code = root.findtext(".//resultCode")
    if result_code and result_code != "00":
        raise RuntimeError(f"API 오류(resultCode={result_code}): {root.findtext('.//resultMsg')}")

    return {
        "품목코드": root.findtext(".//ic"),
        "품목명": root.findtext(".//in"),
        "총건수": root.findtext(".//totalCount"),
        "상품목록": [
            {
                "상품ID": item.findtext("pi"),
                "상품명": item.findtext("pn"),
                "판매가격": item.findtext("sp"),
                "할인가격": item.findtext("dp"),
                "가격일자": item.findtext("sd"),
            }
            for item in root.findall(".//items/item")
        ],
    }


def get_average_price(item_code: str, start_date: str, end_date: str,
                       sample_size: int = 1000) -> dict:
    """기간 내 판매가격의 평균을 계산한다.

    totalCount가 수천~수만 건에 달할 수 있어(예: 쌀 1개월치 15,000건 이상),
    전수 조회 대신 한 페이지(sample_size, 최대 1000 = API 최대값)만 조회해
    평균을 추정한다. 실제 통계청이라면 전수/표본설계를 따르겠지만, 이 실습에서는
    API 호출 횟수를 실습 가능한 수준으로 유지하기 위한 의도적인 단순화다.
    """
    결과 = get_price_info(item_code, start_date, end_date, num_of_rows=min(sample_size, 1000))
    가격목록 = [int(상품["판매가격"]) for 상품 in 결과["상품목록"] if 상품["판매가격"]]
    return {
        "품목코드": 결과["품목코드"],
        "품목명": 결과["품목명"],
        "전체건수": int(결과["총건수"]) if 결과["총건수"] else 0,
        "표본건수": len(가격목록),
        "평균가격": round(statistics.mean(가격목록)) if 가격목록 else None,
    }
