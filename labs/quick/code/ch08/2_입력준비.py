# 준비 Ch08 — 앞 차시 결과 중 빠진 필드만 예시로 채우기
import json, os
SOL = r"C:\dev\claudeCLI\보도자료작성-실습1\labs\quick\solutions"   # 정답 코드 폴더. 위치가 다르면 고치세요
with open(os.path.join(SOL, "snapshots", "press_data_after_ch07.json"), encoding="utf-8") as f:
    예시 = json.load(f)
with open("mywork/press_data.json", encoding="utf-8") as f:
    data = json.load(f)
채움 = [k for k in 예시 if k not in data]
for k in 채움:
    data[k] = 예시[k]
with open("mywork/press_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("예시로 채운 필드:", 채움 or "없음 — 앞 차시 결과를 그대로 사용")
