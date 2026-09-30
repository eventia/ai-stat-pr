"""6차시: 막대·원형·꺾은선 그래프를 만들고, 그래프 유형별 설명문을 규칙 기반으로 생성한다."""
import os

import matplotlib

matplotlib.use("Agg")  # 창을 띄우지 않고 파일로만 저장한다
import matplotlib.pyplot as plt
import pandas as pd

plt.rc("font", family="Malgun Gothic")
plt.rc("axes", unicode_minus=False)


def generate_chart_description(chart_type: str, data: pd.DataFrame, label: str = None) -> str:
    if chart_type == "bar":
        정렬_df = data.sort_values("당월거래액", ascending=False)
        첫째, 둘째, 마지막 = 정렬_df.iloc[0], 정렬_df.iloc[1], 정렬_df.iloc[-1]
        return (f"{첫째['품목']}이 {int(첫째['당월거래액']):,}억 원으로 가장 높았으며, "
                f"{둘째['품목']}이 {int(둘째['당월거래액']):,}억 원으로 그 뒤를 이었다. "
                f"반면 {마지막['품목']}은 {int(마지막['당월거래액']):,}억 원으로 가장 낮은 수준을 보였다.")
    if chart_type == "pie":
        정렬_df = data.sort_values("비중", ascending=False)
        첫째, 둘째, 셋째 = 정렬_df.iloc[0], 정렬_df.iloc[1], 정렬_df.iloc[2]
        return (f"품목별 비중을 살펴보면 {첫째['품목']}이 전체의 {첫째['비중']}%로 "
                f"가장 큰 비중을 차지하였으며, {둘째['품목']}({둘째['비중']}%), "
                f"{셋째['품목']}({셋째['비중']}%)이 그 뒤를 이었다.")
    if chart_type == "line":
        정렬_df = data.sort_values("연월").reset_index(drop=True)
        시작, 종료 = 정렬_df.iloc[0], 정렬_df.iloc[-1]
        추세방향 = "증가" if 종료["거래액"] > 시작["거래액"] else "감소"
        주어 = label or "총거래액"
        증감 = 정렬_df["거래액"].diff()
        변곡점 = 정렬_df[증감 * 증감.shift(-1) < 0]
        문장 = f"{주어}은 {시작['연월']}부터 {종료['연월']}까지 {추세방향}세를 보이고 있으며, "
        if not 변곡점.empty:
            문장 += f"{변곡점.iloc[-1]['연월']}에 방향이 바뀐 뒤 "
        return 문장 + f"{종료['연월']}에 {int(종료['거래액']):,}억 원을 기록하였다."
    raise ValueError(f"지원하지 않는 그래프 유형: {chart_type}")


def generate_table_description(data: pd.DataFrame) -> str:
    lines = [f"{int(row['순위'])}위 {row['품목']}({row['비중']}%)" for _, row in data.sort_values("순위").iterrows()]
    return "품목별 순위는 " + ", ".join(lines) + " 순으로 나타났다."


def build_visual_descriptions(data: dict) -> list:
    os.makedirs("images", exist_ok=True)
    제목 = data["문서정보"]["제목"]
    지표명 = data["문서정보"].get("지표명", "거래액")
    출처 = data["문서정보"].get("자료출처", "국가데이터처")
    결과 = []

    if data.get("품목별지표"):
        품목_df = pd.DataFrame(data["품목별지표"])
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
        axes[0].bar(품목_df["품목"], 품목_df["당월거래액"], color="#4C72B0")
        axes[0].set_title(f"{제목} 품목별 거래액")
        axes[0].set_ylabel("거래액(억 원)")
        axes[1].pie(품목_df["비중"], labels=품목_df["품목"], autopct="%.1f%%", startangle=90)
        axes[1].set_title(f"{제목} 품목별 비중(%)")
        fig.text(0.99, -0.02, f"자료: {출처}", ha="right", va="top", fontsize=8)
        품목_경로 = "images/품목별_거래액_비중.png"
        fig.savefig(품목_경로, dpi=150, bbox_inches="tight")
        plt.close(fig)
        결과.append({"소주제": "품목별 동향", "그래프유형": "막대그래프", "이미지경로": 품목_경로,
                   "설명문": generate_chart_description("bar", 품목_df)})
        결과.append({"소주제": "품목별 비중", "그래프유형": "원형그래프", "이미지경로": 품목_경로,
                   "설명문": generate_chart_description("pie", 품목_df)})

    if data.get("월별이력"):
        이력_df = pd.DataFrame(data["월별이력"]).rename(columns={"값": "거래액"}).sort_values("연월")
        fig2, ax2 = plt.subplots(figsize=(8, 4))
        ax2.plot(이력_df["연월"], 이력_df["거래액"], marker="o", color="#DD8452")
        ax2.set_title(f"{제목} 월별 추이")
        ax2.set_ylabel("거래액(억 원)")
        ax2.tick_params(axis="x", rotation=45)
        ax2.set_xlabel(f"자료: {출처}", loc="right", fontsize=8)
        추이_경로 = "images/월별_거래액_추이.png"
        fig2.savefig(추이_경로, dpi=150, bbox_inches="tight")
        plt.close(fig2)
        결과.append({"소주제": "시계열 동향", "그래프유형": "꺾은선그래프", "이미지경로": 추이_경로,
                   "설명문": generate_chart_description("line", 이력_df, label=지표명)})
    return 결과
