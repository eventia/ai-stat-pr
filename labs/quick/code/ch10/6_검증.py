# 검증 Ch10 — 전체 파이프라인을 가짜 함수로 실행 (실제 API 호출 없음, 비용 0)
import sys, os, json, shutil
import pandas as pd
sys.path.insert(0, ".")
import mywork.write as W
import mywork.review as R

def 실제호출_금지(**kwargs):
    raise RuntimeError("검증 중에 실제 API를 호출하려 함")
W.client.messages.create = 실제호출_금지
import mywork.main as M

호출 = []
헤드라인 = {"제목": "1월 온라인쇼핑 거래액, 역대 최대", "부제": "전년동월 대비 8.7% 증가한 201,250억 원",
          "리드문": "국가데이터처는 2026년 1월 온라인쇼핑 거래액이 201,250억 원으로 집계되었다고 밝혔다. "
                   "이는 전월 대비 1.5%, 전년동월 대비 8.7% 증가한 수치이다."}
def 가짜_요약(data):
    호출.append("요약"); return {"삼줄요약": [헤드라인["리드문"]], "제목후보": [헤드라인["제목"]]}
def 가짜_헤드라인(data):
    호출.append("헤드라인"); return dict(헤드라인)
def 가짜_본문(data):
    호출.append("본문")
    return [{"소주제": v["소주제"], "내용": ("" if i == 0 else "한편, ") + v["설명문"].replace("의류이", "의류가").replace("기타은", "기타는")}
            for i, v in enumerate(data["시각자료설명"])]
def 가짜_문체(text):
    호출.append("문체"); return text
def 가짜_감수(text, data):
    호출.append("감수"); return []
for 모듈 in (M, W):
    for 이름, 함수 in [("generate_summary", 가짜_요약), ("generate_headline_set", 가짜_헤드라인),
                     ("generate_body_paragraphs", 가짜_본문), ("unify_style", 가짜_문체)]:
        setattr(모듈, 이름, 함수)
for 모듈 in (M, R):
    setattr(모듈, "review_press_release", 가짜_감수)

백업 = "mywork/press_data.backup.json"
if os.path.exists("mywork/press_data.json"):
    shutil.copy("mywork/press_data.json", 백업)
만든_파일 = []
try:
    # ① 정상 흐름 → 승인대기
    결과 = M.main("data/온라인쇼핑동향_2026_01.xlsx")
    만든_파일 += list(결과["출력파일"].values())
    print("AI 함수 호출 순서:", 호출)
    print("문서상태:", 결과["문서상태"], "| 수치 교차 검증:", 결과["검수결과"]["수치교차검증"])
    print("저장된 파일:", 결과["출력파일"])
    assert 호출 == ["요약", "헤드라인", "본문", "문체", "감수"], "호출 순서가 다름"
    assert 결과["문서상태"] == "승인대기" and 결과["검수결과"]["표기오류검사"] == []
    assert 결과["출력파일"]["txt"].endswith("_승인대기.txt") and os.path.exists(결과["출력파일"]["txt"])
    for 형식 in ("hwpx", "pdf"):
        assert os.path.exists(결과["출력파일"].get(형식, "")), f"{형식} 파일이 없음"
    assert len(결과["시각자료설명"]) == 3 and "NLP분석결과" in 결과 and "통계해석결과" in 결과
    with open("logs/pipeline.log", encoding="utf-8") as f:
        assert "파이프라인 완료" in f.read(), "로그가 UTF-8로 남지 않음"

    # ② 파생 수치가 섞이면 → 검토필요
    M.unify_style = W.unify_style = lambda text: text + " 상위 세 품목이 전체의 82.0%를 차지하였다."
    결과2 = M.main("data/온라인쇼핑동향_2026_01.xlsx")
    만든_파일 += list(결과2["출력파일"].values())
    print("파생 수치가 섞인 경우:", 결과2["문서상태"], 결과2["검수결과"]["수치교차검증"]["불일치수치"])
    assert 결과2["문서상태"] == "검토필요" and 결과2["출력파일"]["txt"].endswith("_검토필요.txt")

    # ③ 보안등급이 '공개'가 아니면 → AI 호출 전에 중단
    시트 = pd.read_excel("data/온라인쇼핑동향_2026_01.xlsx", sheet_name=None, dtype={"연월": str, "공표일자": str})
    시트["요약"]["보안등급"] = "대외비"
    with pd.ExcelWriter("data/보안등급_테스트.xlsx") as w:
        for 이름, 표 in 시트.items():
            표.to_excel(w, sheet_name=이름, index=False)
    호출.clear()
    try:
        M.main("data/보안등급_테스트.xlsx")
        raise AssertionError("대외비 자료가 차단되지 않음")
    except PermissionError as e:
        print("보안등급 차단:", e)
    assert 호출 == [], "차단되기 전에 AI 함수가 호출됨"
    try:
        os.remove("data/보안등급_테스트.xlsx")
    except PermissionError:
        print("참고: 테스트 엑셀이 아직 열려 있어 지우지 못함 — load_input이 ExcelFile을 with 문으로 닫는지 확인(7차시)")
finally:
    if os.path.exists(백업):
        shutil.move(백업, "mywork/press_data.json")
    for 경로 in 만든_파일:
        if os.path.exists(경로):
            os.remove(경로)
print("Ch10 OK — 파이프라인 구조·검토필요 분기·보안등급 차단 검증 통과 (실제 실행은 8절)")
