# 관찰 Ch09
import sys
sys.path.insert(0, ".")
from mywork.review import check_formatting_errors

for s in ["거래액은 201,250억 원이다.",
          "거래액은 201,250억원이다.",
          "2026년 거래액은 201250억 원이다.",
          "의류 비중이 3%p 확대되었다.",
          "의류 비중이 3% 확대되었다.",
          "거래액이 3%p 증가하였다."]:
    print(check_formatting_errors(s) or "문제 없음", "←", s)
