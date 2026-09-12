"""강의안(./lect) 본문에 실제로 등장하는 예시 수치만 그대로 사용해
Ch05/Ch06 강의안에 삽입할 그래프 이미지를 생성한다.

새로운 숫자를 지어내지 않고, 각 페이지의 코드/텍스트에 이미 적혀 있는
값만으로 그래프를 그린다. 결과는 lect/images/ 아래에 저장되며,
강의안 마크다운의 ![](images/파일명.png) 구문이 이 파일들을 가리킨다.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

plt.rc("font", family="Malgun Gothic")
plt.rc("axes", unicode_minus=False)

LECT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lect")
IMAGES_DIR = os.path.join(LECT_DIR, "images")
os.makedirs(IMAGES_DIR, exist_ok=True)

BAR_COLOR = "#4C72B0"
HIGHLIGHT_COLOR = "#DD8452"
PIE_COLORS = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2"]


def save(fig, filename):
    path = os.path.join(IMAGES_DIR, filename)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {path}")


# ---------------------------------------------------------------------------
# Ch05 페이지 08. 전월대비증감률 계산 예시 (2025-12 -> 2026-01)
# ---------------------------------------------------------------------------
def ch05_page08():
    df = pd.DataFrame({"연월": ["2025-12", "2026-01"], "거래액": [198276, 201250]})
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(df["연월"], df["거래액"], color=[BAR_COLOR, HIGHLIGHT_COLOR], width=0.5)
    ax.set_title("온라인쇼핑 거래액 전월대비 비교")
    ax.set_ylabel("거래액(억 원)")
    ax.set_ylim(0, max(df["거래액"]) * 1.2)
    for bar, value in zip(bars, df["거래액"]):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 2000, f"{value:,}", ha="center")
    momrate = (df["거래액"].iloc[1] / df["거래액"].iloc[0] - 1) * 100
    ax.annotate(
        f"전월대비 +{momrate:.1f}%",
        xy=(1, df["거래액"].iloc[1]), xytext=(0.5, max(df["거래액"]) * 1.12),
        ha="center", color=HIGHLIGHT_COLOR, fontweight="bold",
        arrowprops=dict(arrowstyle="->", color=HIGHLIGHT_COLOR),
    )
    save(fig, "ch05_거래액_증감_비교.png")


# ---------------------------------------------------------------------------
# Ch05 페이지 09. 품목별 비중(구성비) 계산 예시
# ---------------------------------------------------------------------------
def ch05_page09():
    category_df = pd.DataFrame({
        "품목": ["의류", "가전", "식품", "기타"],
        "거래액": [65000, 52000, 48000, 36250],
    })
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.pie(
        category_df["거래액"], labels=category_df["품목"], autopct="%.1f%%",
        colors=PIE_COLORS, startangle=90,
    )
    ax.set_title("품목별 거래액 비중")
    save(fig, "ch05_품목별_비중.png")


# ---------------------------------------------------------------------------
# Ch05 페이지 10. 품목별 순위 산정 예시 (최댓값/최솟값 강조)
# ---------------------------------------------------------------------------
def ch05_page10():
    category_df = pd.DataFrame({
        "품목": ["의류", "가전", "식품", "기타"],
        "거래액": [65000, 52000, 48000, 36250],
    })
    sorted_df = category_df.sort_values("거래액", ascending=False).reset_index(drop=True)
    colors = [HIGHLIGHT_COLOR if i == 0 else "#C44E52" if i == len(sorted_df) - 1 else BAR_COLOR
              for i in range(len(sorted_df))]
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(sorted_df["품목"], sorted_df["거래액"], color=colors)
    ax.set_title("품목별 거래액 순위")
    ax.set_ylabel("거래액(억 원)")
    ax.set_ylim(0, max(sorted_df["거래액"]) * 1.25)
    for rank, (bar, value) in enumerate(zip(bars, sorted_df["거래액"]), start=1):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 1500, f"{rank}위\n{value:,}", ha="center")
    save(fig, "ch05_품목별_순위.png")


# ---------------------------------------------------------------------------
# Ch05 페이지 12. 역대 최고 판별 예시 (2024-01 / 2025-01 / 2026-01)
# ---------------------------------------------------------------------------
def ch05_page12():
    history_df = pd.DataFrame({
        "연월": ["2024-01", "2025-01", "2026-01"],
        "거래액": [175320, 189430, 201250],
    })
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(history_df["연월"], history_df["거래액"], marker="o", color=BAR_COLOR, linewidth=2)
    last_x, last_y = history_df["연월"].iloc[-1], history_df["거래액"].iloc[-1]
    ax.scatter([last_x], [last_y], color=HIGHLIGHT_COLOR, s=110, zorder=5)
    ax.annotate(
        "역대 최대", xy=(last_x, last_y), xytext=(last_x, last_y + 9000),
        ha="center", color=HIGHLIGHT_COLOR, fontweight="bold",
        arrowprops=dict(arrowstyle="->", color=HIGHLIGHT_COLOR),
    )
    ax.set_title("1월 기준 온라인쇼핑 거래액 추이(역대 최대 판별)")
    ax.set_ylabel("거래액(억 원)")
    ax.set_ylim(0, max(history_df["거래액"]) * 1.3)
    save(fig, "ch05_역대최대_추이.png")


# ---------------------------------------------------------------------------
# Ch06 페이지 08. matplotlib 막대그래프 생성 코드의 실제 실행 결과
# (코드에 적힌 savefig 경로와 동일한 파일명을 그대로 사용한다)
# ---------------------------------------------------------------------------
def ch06_page08():
    품목 = ["의류", "가전", "식품", "생활용품", "기타"]
    거래액 = [65000, 52000, 48000, 26250, 10000]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(품목, 거래액, color=BAR_COLOR)
    ax.set_title("2026년 1월 품목별 온라인쇼핑 거래액")
    ax.set_ylabel("거래액(억 원)")
    save(fig, "품목별_거래액.png")


# ---------------------------------------------------------------------------
# Ch06 페이지 13. 원형그래프(비중) 설명문 템플릿과 짝을 이루는 실제 그래프
# ---------------------------------------------------------------------------
def ch06_page13():
    품목 = ["의류", "가전", "식품", "생활용품", "기타"]
    거래액 = [65000, 52000, 48000, 26250, 10000]
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.pie(거래액, labels=품목, autopct="%.1f%%", colors=PIE_COLORS, startangle=90)
    ax.set_title("품목별 거래액 비중")
    save(fig, "ch06_품목별_비중.png")


def main():
    ch05_page08()
    ch05_page09()
    ch05_page10()
    ch05_page12()
    ch06_page08()
    ch06_page13()


if __name__ == "__main__":
    main()
