"""6차시: 표·그래프 기반 설명문 자동 생성."""
import os

import matplotlib
# 화면에 띄우지 않고 파일로만 저장하므로 비대화형 백엔드를 명시한다.
# (일부 환경에서는 기본값이 TkAgg로 잡히는데, Tcl/Tk 설치가 불완전하면
# savefig 시점에 tkinter 오류가 발생할 수 있다.)
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from modules.config import PRIMARY_INDICATOR


def generate_chart_description(chart_type: str, data: pd.DataFrame, label: str = None) -> str:
    if chart_type == "bar":
        sorted_df = data.sort_values("당월거래액", ascending=False)
        top, second, last = sorted_df.iloc[0], sorted_df.iloc[1], sorted_df.iloc[-1]
        return (f"{top['품목']}이 {top['당월거래액']:,}억 원으로 가장 높았으며, "
                f"{second['품목']}이 {second['당월거래액']:,}억 원으로 그 뒤를 이었다. "
                f"반면 {last['품목']}은 {last['당월거래액']:,}억 원으로 가장 낮은 수준을 보였다.")
    elif chart_type == "pie":
        sorted_df = data.sort_values("비중", ascending=False)
        top3 = sorted_df.iloc[:3]
        return (f"품목별 비중을 살펴보면 {top3.iloc[0]['품목']}이 전체의 {top3.iloc[0]['비중']}%로 "
                f"가장 큰 비중을 차지하였으며, {top3.iloc[1]['품목']}({top3.iloc[1]['비중']}%), "
                f"{top3.iloc[2]['품목']}({top3.iloc[2]['비중']}%)이 그 뒤를 이었다.")
    elif chart_type == "line":
        # 검토 보고서(REVIEW_Ch02-10.md) 후속 실습 중 실제로 재현된 버그: 이 문장에
        # 주어(무엇이 증가/감소했는지)가 없으면, 8차시 expand_to_paragraph가 이
        # 설명문만 보고 본문을 확장할 때 LLM이 엉뚱한 주제를 지어내는 환각이
        # 실제로 관찰되었다(예: "디지털 콘텐츠 시장 규모는..."). label로 주어를
        # 명시해 이 문제를 막는다.
        sorted_df = data.sort_values("연월")
        시작, 종료 = sorted_df.iloc[0], sorted_df.iloc[-1]
        추세방향 = "증가" if 종료["거래액"] > 시작["거래액"] else "감소"
        주어 = label or PRIMARY_INDICATOR
        return (f"{주어}은 {시작['연월']}부터 {종료['연월']}까지 {추세방향}세를 보이고 있으며, "
                f"{종료['연월']}에 {종료['거래액']:,}억 원을 기록하였다.")
    return ""


def generate_table_description(data: pd.DataFrame) -> str:
    lines = []
    for _, row in data.sort_values("순위").iterrows():
        lines.append(f"{row['순위']}위 {row['품목']}({row['비중']}%)")
    return "품목별 순위는 " + ", ".join(lines) + " 순으로 나타났다."


def build_visual_descriptions(data: dict) -> list:
    """품목별지표로 막대·원형 그래프를, 월별이력으로 꺾은선 그래프를 생성해 시각자료설명 목록을 반환한다."""
    os.makedirs("images", exist_ok=True)
    plt.rc("font", family="Malgun Gothic")
    제목 = data["문서정보"]["제목"]
    결과 = []

    if "품목별지표" in data:
        품목_df = pd.DataFrame(data["품목별지표"])
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        axes[0].bar(품목_df["품목"], 품목_df["당월거래액"], color="#4C72B0")
        axes[1].pie(품목_df["비중"], labels=품목_df["품목"], autopct="%.1f%%")
        품목_이미지경로 = f"images/{제목}_품목별.png"
        plt.savefig(품목_이미지경로, dpi=150, bbox_inches="tight")
        plt.close(fig)

        결과.append({"소주제": "품목별 동향", "그래프유형": "막대그래프", "이미지경로": 품목_이미지경로,
                    "설명문": generate_chart_description("bar", 품목_df)})
        결과.append({"소주제": "품목별 비중", "그래프유형": "원형그래프", "이미지경로": 품목_이미지경로,
                    "설명문": generate_chart_description("pie", 품목_df)})

    # 검토 보고서(REVIEW_Ch02-10.md, 5번 개선 제안) 대응: 꺾은선그래프(line) 분기는
    # generate_chart_description에 코드와 템플릿이 있었지만, 파이프라인에서 이 함수를
    # 호출하는 곳이 없어 실제로는 도달 불가능한 "고아 기능"이었다. 이제 modules/io.py가
    # xlsx의 "이력" 시트를 읽어 채워주는 "월별이력"이 있으면 실제로 꺾은선 그래프를
    # 그리고 추세 설명문을 생성한다.
    if "월별이력" in data and data["월별이력"]:
        이력_df = pd.DataFrame(data["월별이력"]).rename(columns={"값": "거래액"}).sort_values("연월")
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        ax2.plot(이력_df["연월"], 이력_df["거래액"], marker="o", color="#DD8452")
        ax2.set_title(f"{제목} 월별 추이")
        추이_이미지경로 = f"images/{제목}_추이.png"
        plt.savefig(추이_이미지경로, dpi=150, bbox_inches="tight")
        plt.close(fig2)

        결과.append({"소주제": "시계열 동향", "그래프유형": "꺾은선그래프", "이미지경로": 추이_이미지경로,
                    "설명문": generate_chart_description("line", 이력_df)})

    return 결과
