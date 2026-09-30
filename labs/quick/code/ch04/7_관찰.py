# 관찰 Ch04
import os, sys
sys.path.insert(0, ".")
print("① load_dotenv 전:", "키 있음" if os.getenv("ANTHROPIC_API_KEY") else "키 없음")
from dotenv import load_dotenv
load_dotenv()
print("① load_dotenv 후:", "키 있음" if os.getenv("ANTHROPIC_API_KEY") else "키 없음(.env 확인)")

from mywork.review import find_unverified_numbers
data = {"계산지표": {"총거래액": 201250, "전월대비증감률": 1.5, "전년동월대비증감률": 8.7}}
for s in ["거래액은 201,250억 원으로 전월 대비 1.5% 증가하였다.",
          "거래액은 201,520억 원으로 전월 대비 1.6% 증가하였다.",
          "역대 최대 실적을 압도적으로 경신하며 사상 최고의 성장세를 보였다.",
          "모바일쇼핑 비중은 78%로 15% 늘었다."]:
    print("② 근거 없는 숫자:", find_unverified_numbers(s, data), "←", s)
