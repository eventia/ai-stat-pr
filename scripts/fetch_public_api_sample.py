"""2차시 공공데이터포털 Open API 연동 실습 데모 — 실제 발급받은 키로 검증됨.

실제 API 호출 로직은 modules/public_api.py에 있다 (main_price.py의 통계
보도자료 파이프라인도 같은 모듈을 사용한다). 이 스크립트는 그 모듈이 실제로
동작하는지 눈으로 확인하기 위한 최소 데모다.
"""
import sys

sys.path.insert(0, ".")

# 윈도우 콘솔/파일 리다이렉션 시 기본 코드페이지(cp949)로 출력되어 한글이
# 깨지는 문제를 막기 위해 표준출력 인코딩을 명시적으로 UTF-8로 고정한다.
sys.stdout.reconfigure(encoding="utf-8")

from modules.public_api import SERVICE_KEY, get_price_info, get_price_item_list

if __name__ == "__main__":
    if not SERVICE_KEY:
        raise SystemExit(".env의 PUBLIC_API_KEY가 비어 있습니다.")

    print("=== 1) 품목 리스트 조회 (상위 5개) ===")
    for 품목 in get_price_item_list(num_of_rows=5):
        print(f"  {품목['품목코드']}  {품목['품목명']}")

    print("\n=== 2) 가격정보 조회 (쌀, 최근 기간) ===")
    결과 = get_price_info(item_code="A01101", start_date="20260801", end_date="20260831", num_of_rows=5)
    print(f"  품목: {결과['품목명']}({결과['품목코드']}), 전체 {결과['총건수']}건 중 {len(결과['상품목록'])}건 표시")
    for 상품 in 결과["상품목록"]:
        print(f"  - {상품['상품명']}: {상품['판매가격']}원 ({상품['가격일자']})")
