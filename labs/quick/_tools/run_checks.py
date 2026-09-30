"""10분 실습 문서(labs/quick/ChNN-10분실습.md)의 코드 블록을 빈 폴더에서 차례로 실행해 검증한다.

사용 (저장소 루트에서, 2~10차시 패키지가 설치된 파이썬으로):
    python labs/quick/_tools/run_checks.py --work <빈 작업 폴더> [--make-snapshots]
    python labs/quick/_tools/run_checks.py --work <빈 작업 폴더> --standalone 7

- Claude Code가 만든 코드 대신 정답 코드(solutions/chNN/*.py)를 복사해 넣고 문서의 블록을 실행한다.
- 실행하는 블록: 첫 줄이 '# 준비 ChNN' · '# 검증 ChNN' · '# 관찰 ChNN'인 파이썬 블록,
  CLAUDE.md를 만들거나 블록을 추가하는 PowerShell 블록, 10차시 export.py 복사 블록.
- '# 선택 ChNN'(실제 API 호출) 블록은 실행하지 않는다. 대신 --make-snapshots일 때
  그 단계의 결과를 아래 SAMPLE_LLM 예시로 채워 solutions/snapshots/에 차시별 스냅숏을 남긴다.
- 각 블록의 출력은 <작업 폴더>/_out/ 에 저장되고, 마지막에 통과·실패 요약을 출력한다.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

QUICK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOL = os.path.join(QUICK, "solutions")

SAMPLE_LLM = {
    4: {"요약결과": {
        "삼줄요약": ["2026년 1월 온라인쇼핑 거래액은 201,250억 원으로 집계되었다.",
                 "이는 전월 대비 1.5%, 전년동월 대비 8.7% 증가한 수치이다.",
                 "온라인쇼핑 거래액은 역대 1월 기준 최대치를 기록하였다."],
        "제목후보": ["1월 온라인쇼핑 거래액, 역대 최대 기록", "온라인쇼핑 거래액 전년동월 대비 8.7% 증가",
                 "1월 온라인쇼핑 거래액 201,250억 원"]}},
    7: {"헤드라인": {
        "제목": "1월 온라인쇼핑 거래액, 역대 최대",
        "부제": "전년동월 대비 8.7% 증가한 201,250억 원",
        "리드문": "국가데이터처는 2026년 1월 온라인쇼핑 거래액이 201,250억 원으로 집계되었다고 밝혔다. "
                 "이는 전월 대비 1.5%, 전년동월 대비 8.7% 증가한 수치이다. "
                 "온라인쇼핑 거래액은 동월 기준 역대 최대치를 기록하였으며, 최근 3개월 연속 증가세를 이어가고 있다."}},
    8: {"본문": [
        {"소주제": "품목별 동향",
         "내용": "품목별로는 의류가 65,000억 원으로 가장 많이 거래되었으며, 가전이 52,000억 원으로 그 뒤를 이었다. "
                "반면 기타 품목은 10,000억 원으로 가장 낮은 수준을 보였다."},
        {"소주제": "품목별 비중",
         "내용": "한편, 품목별 비중을 살펴보면 의류가 전체의 32.3%로 가장 큰 비중을 차지하였으며, "
                "가전(25.8%)과 식품(23.9%)이 그 뒤를 이었다."},
        {"소주제": "시계열 동향",
         "내용": "아울러, 온라인쇼핑 거래액은 2025년 1월부터 2026년 1월까지 증가세를 보였다. "
                "2025년 9월에 방향이 바뀐 뒤 상승세가 이어져 2026년 1월에는 201,250억 원을 기록하였다."}]},
}

BLOCK_RE = re.compile(r"```(\w+)\n(.*?)```", re.S)


def blocks_for(n: int, standalone: bool):
    text = open(os.path.join(QUICK, f"Ch{n:02d}-10분실습.md"), encoding="utf-8").read()
    tag = f"Ch{n:02d}"
    picked = []
    for lang, code in BLOCK_RE.findall(text):
        first = code.splitlines()[0] if code.strip() else ""
        if lang == "python" and re.match(rf"# (준비|검증|관찰) {tag}\b", first):
            picked.append(("py", first, code))
        elif lang == "powershell":
            if first.startswith(f"# 단독 시작 {tag}"):
                if standalone:
                    picked.insert(0, ("ps", first, code))
            elif f"quick-practice:ch{n:02d}:start" in code:
                picked.append(("ps", f"# CLAUDE.md {tag}", code))
            elif "ch10\\export.py" in code and "단독" not in code:
                picked.append(("ps", "# export 복사 Ch10", code))
    return picked


def run(kind, code, work, env, out_path):
    ext = ".py" if kind == "py" else ".ps1"
    script = os.path.join(work, "_block" + ext)
    with open(script, "w", encoding="utf-8-sig" if kind == "ps" else "utf-8", newline="\n") as f:
        f.write(code)
    cmd = [sys.executable, script] if kind == "py" else \
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script]
    p = subprocess.run(cmd, cwd=work, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    os.remove(script)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(p.stdout + ("\n[stderr]\n" + p.stderr if p.stderr.strip() else ""))
    return p.returncode, p.stdout, p.stderr


def copy_solution(n, work):
    os.makedirs(os.path.join(work, "mywork"), exist_ok=True)
    init = os.path.join(work, "mywork", "__init__.py")
    if not os.path.exists(init):
        open(init, "w").close()
    for f in os.listdir(os.path.join(SOL, f"ch{n:02d}")):
        if f.endswith(".py"):
            shutil.copy(os.path.join(SOL, f"ch{n:02d}", f), os.path.join(work, "mywork", f))


def inject_sample(n, work):
    path = os.path.join(work, "mywork", "press_data.json")
    data = json.load(open(path, encoding="utf-8"))
    sample = dict(SAMPLE_LLM.get(n, {}))
    if n == 9:
        import importlib
        sys.path.insert(0, work)
        write = importlib.import_module("mywork.write")
        review = importlib.import_module("mywork.review")
        최종본 = write.assemble_full_text(data)
        전체 = " ".join([data["헤드라인"]["제목"], data["헤드라인"]["부제"], 최종본])
        sample = {"최종본": 최종본, "검수결과": {"표기오류검사": review.check_formatting_errors(전체),
                                          "수치교차검증": review.cross_check_all_numbers(전체, data),
                                          "AI감수지적사항": []}}
    for k, v in sample.items():
        data.setdefault(k, v)
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--make-snapshots", action="store_true")
    ap.add_argument("--standalone", type=int)
    args = ap.parse_args()
    work = os.path.abspath(args.work)
    os.makedirs(work, exist_ok=True)
    out = os.path.join(work, "_out")
    os.makedirs(out, exist_ok=True)
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8",
               PATH=os.path.dirname(sys.executable) + os.pathsep + os.environ.get("PATH", ""))
    env.pop("ANTHROPIC_API_KEY", None)  # 검증은 실제 API 없이 통과해야 한다

    chapters = [args.standalone] if args.standalone else list(range(2, 11))
    results = []
    for n in chapters:
        copy_solution(n, work)
        for kind, name, code in blocks_for(n, standalone=bool(args.standalone)):
            safe = re.sub(r"[^\w가-힣]+", "_", name).strip("_")
            rc, so, se = run(kind, code, work, env, os.path.join(out, f"ch{n:02d}_{safe}.txt"))
            ok = rc == 0 and ("OK" in so if "검증" in name else True)
            results.append((n, name, ok))
            print(f"[{'PASS' if ok else 'FAIL'}] ch{n:02d} {name}")
            if not ok:
                print(so[-1500:], se[-3000:])
        if args.make_snapshots and not args.standalone and n <= 9:
            inject_sample(n, work)
            snap = os.path.join(SOL, "snapshots")
            os.makedirs(snap, exist_ok=True)
            shutil.copy(os.path.join(work, "mywork", "press_data.json"), os.path.join(snap, f"press_data_after_ch{n:02d}.json"))
            shutil.copy(os.path.join(work, "CLAUDE.md"), os.path.join(snap, f"CLAUDE_after_ch{n:02d}.md"))
            data_dir = os.path.join(SOL, "data")
            os.makedirs(data_dir, exist_ok=True)
            for f in ("raw_202601.json", "온라인쇼핑동향_2026_01.xlsx", "온라인쇼핑동향_2026_01.pdf"):
                if os.path.exists(os.path.join(work, "data", f)):
                    shutil.copy(os.path.join(work, "data", f), os.path.join(data_dir, f))
    failed = [r for r in results if not r[2]]
    print(f"\n총 {len(results)}개 블록, 실패 {len(failed)}개")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
