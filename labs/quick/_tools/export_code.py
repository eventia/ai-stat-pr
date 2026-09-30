"""10분 실습 문서(ChNN-10분실습.md)의 코드 블록과 정답 코드를 차시별 코드 폴더(labs/quick/code/chNN/)로 내보낸다.

사용 (저장소 루트에서):
    python labs/quick/_tools/export_code.py            # 2~10차시 전부
    python labs/quick/_tools/export_code.py 2 3        # 지정한 차시만

- 문서가 원본이다. code/ 폴더는 이 스크립트가 만드는 결과물이므로 직접 고치지 말고, 문서를 고친 뒤 다시 실행한다.
- 파일 이름은 "절 번호_제목"이다. 같은 절의 PowerShell 블록은 한 파일로 합친다.
- 정답 코드(solutions/chNN)는 정답코드/mywork/ 로, 차시를 마친 시점의 CLAUDE.md(snapshots)는 결과_CLAUDE.md 로 복사한다.
"""
import os
import re
import shutil
import sys

QUICK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOL = os.path.join(QUICK, "solutions")
CODE = os.path.join(QUICK, "code")
EXT = {"python": ".py", "powershell": ".ps1", "text": ".txt", "markdown": ".md", "json": ".json"}
CHAPTER_TITLE = {
    2: "텍스트 정제·표준화·구조화", 3: "주요 NLP 기법", 4: "LLM 기반 텍스트 요약", 5: "통계 계산과 해석문",
    6: "표·그래프 설명문", 7: "원자료 입력·제목·부제·리드문", 8: "본문 단락 확장", 9: "문체 통일·검수·AI 감수",
    10: "보도자료 자동 생성 시스템",
}


def read_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def write_text(path: str, text: str, encoding: str = "utf-8") -> None:
    with open(path, "w", encoding=encoding, newline="\n") as f:
        f.write(text)


def short_title(heading: str) -> str:
    heading = re.sub(r"^\([^)]*\)\s*", "", heading)          # "(선택) …"처럼 앞에 붙은 괄호는 뗀다
    title = re.split(r"\s[—-]\s|\(", heading)[0]
    for key, name in [("수정 요청", "수정요청예시"), ("기대 결과", "기대결과"), ("단독", "단독시작")]:
        if key in heading:
            return name
    title = title.replace("requirements.txt", "requirements").replace("CLAUDE.md", "CLAUDE")
    return re.sub(r"[^\w가-힣]", "", title)


def parse_blocks(md_text: str):
    """(절번호, 제목, 언어, 코드) 목록. 코드 블록 안의 '#' 줄은 제목으로 보지 않는다."""
    blocks, num, title = [], "0", ""
    in_fence, lang, buf = False, "", []
    for line in md_text.splitlines():
        if line.startswith("```"):
            if in_fence:
                blocks.append((num, title, lang, "\n".join(buf).rstrip() + "\n"))
                in_fence, buf = False, []
            else:
                in_fence, lang = True, line[3:].strip() or "text"
            continue
        if in_fence:
            buf.append(line)
            continue
        m = re.match(r"^(#{2,3}) (?:(\d+(?:-\d+)?)\. )?(.*)", line)
        if m:
            level, n, text = m.groups()
            if n:
                num, title = n, short_title(text)
            elif level == "###":
                title = short_title(text)
    return blocks


def describe(name: str, lang: str, code: str) -> str:
    first = code.splitlines()[0] if code.strip() else ""
    if "프롬프트" in name and lang == "text":
        return "Claude Code에 그대로 붙여넣기"
    if "수정요청" in name:
        return "검증이 실패했을 때 Claude Code에 붙여넣기"
    if "기대결과" in name or (lang == "text" and "예시" in first):
        return "실행 결과와 비교"
    if "최종폴더구조" in name:
        return "10차시를 마친 폴더 모습(참고용)"
    if lang == "text":
        return "실행 결과와 비교(예시 출력)"
    if lang == "python":
        if first.startswith("# 선택"):
            return "check.py에 붙여넣고 python check.py (실제 API 호출, 비용 발생)"
        return "check.py에 붙여넣고 python check.py"
    if lang == "powershell" and re.search(r"(?m)^python -m mywork\.main", code):
        return "PowerShell에 붙여넣기 (실제 API 호출, 비용 발생)"
    if lang == "powershell" and "Invoke-Item" in code and name.startswith("7_"):
        return "PowerShell에 붙여넣기 (8절 실제 실행 뒤)"
    if lang == "powershell":
        return "PowerShell에 붙여넣기"
    return ""


def export(n: int):
    doc = os.path.join(QUICK, f"Ch{n:02d}-10분실습.md")
    out = os.path.join(CODE, f"ch{n:02d}")
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)

    files, counts = {}, {}
    for num, title, lang, code in parse_blocks(read_text(doc)):
        if lang == "text" and code.startswith("C:\\dev\\quick-practice\\"):
            title = "최종폴더구조"
        base = f"{num}_{title}" if title else num
        if code.startswith("# 단독 시작"):
            base = f"{num}_단독시작(앞차시건너뛸때만)"
        elif lang == "powershell" and title == "기대결과":
            base = f"{num}_결과열어보기"
        elif lang == "powershell" and code.strip() == "claude":
            base = f"{num}_ClaudeCode시작"
        elif lang == "text" and "프롬프트" in title:
            base = f"{num}_프롬프트"
        elif lang == "text" and title not in ("기대결과", "수정요청예시", "최종폴더구조"):
            base = f"{base}_예시출력"
        ext = EXT.get(lang, ".txt")
        key = base + ext
        if lang == "powershell" and key in files:            # 같은 절의 PowerShell 블록은 한 파일로
            files[key]["code"] += "\n" + code
            continue
        if key in files:
            counts[key] = counts.get(key, 1) + 1
            key = f"{base}_{counts[key]}{ext}"
        files[key] = {"lang": lang, "code": code, "num": num}

    rows = []
    for fname, f in files.items():
        enc = "utf-8-sig" if f["lang"] == "powershell" else "utf-8"   # PowerShell 5.1이 한글을 바르게 읽도록 BOM
        write_text(os.path.join(out, fname), f["code"], enc)
        rows.append((f["num"], fname, describe(fname, f["lang"], f["code"])))

    extra = []
    if n == 2:  # requirements.txt 는 1-4절 PowerShell here-string 안의 내용을 실제 파일로도 둔다
        ps = files.get("1-4_requirements만들고설치.ps1", {}).get("code", "")
        m = re.search(r'@"\n(.*?)\n"@', ps, re.S)
        if m:
            write_text(os.path.join(out, "requirements.txt"), m.group(1) + "\n")
            extra.append(("1-4", "requirements.txt", "1-4절에서 만드는 파일의 내용(참고용)"))
    snap = os.path.join(SOL, "snapshots", f"CLAUDE_after_ch{n:02d}.md")
    if os.path.exists(snap):
        shutil.copy(snap, os.path.join(out, "결과_CLAUDE.md"))
        extra.append(("3", "결과_CLAUDE.md", f"{n}차시를 마쳤을 때의 CLAUDE.md 전체(참고용)"))
    sol_dir = os.path.join(SOL, f"ch{n:02d}")
    if os.path.isdir(sol_dir):
        dst = os.path.join(out, "정답코드", "mywork")
        os.makedirs(dst)
        for f in sorted(os.listdir(sol_dir)):
            if f.endswith(".py"):
                shutil.copy(os.path.join(sol_dir, f), os.path.join(dst, f))
        if n == 2:
            write_text(os.path.join(dst, "__init__.py"), "")
        names = ", ".join(sorted(os.listdir(dst)))
        extra.append(("9", "정답코드/mywork/", f"이 차시의 정답 코드({names}) — 폴백 때 mywork\\로 복사"))

    def order(num):
        return [int(x) for x in num.split("-")]
    rows.sort(key=lambda r: order(r[0]))
    lines = [f"# {n}차시 실습 코드 — {CHAPTER_TITLE[n]}", "",
             f"실습 문서: [../../Ch{n:02d}-10분실습.md](../../Ch{n:02d}-10분실습.md) · 강의: `labs/강의자료/CH{n:02d}-ContentV10.pptx`", "",
             "문서에 나오는 코드를 **진행 순서대로** 모아 둔 폴더입니다. 파일 이름 앞의 숫자는 문서의 절 번호입니다.",
             "이 폴더는 `labs/quick/_tools/export_code.py`가 문서에서 만듭니다 — 고칠 때는 문서를 고친 뒤 다시 생성하세요.", "",
             "| 절 | 파일 | 사용법 |", "| --- | --- | --- |"]
    lines += [f"| {num} | [{fname}]({fname}) | {how} |" for num, fname, how in rows]
    lines += [f"| {num} | [{fname}]({fname.rstrip('/')}) | {how} |" for num, fname, how in extra]
    lines += ["", r"- PowerShell 명령은 2차시 1-2절 이후 항상 프로젝트 폴더(`C:\dev\quick-practice`)에서, 가상환경을 켠 상태로 실행합니다.",
              "- `.ps1`은 UTF-8(BOM)로 저장되어 있어 `powershell -File 파일명`으로 바로 실행할 수도 있습니다(프로젝트 폴더에서).",
              "- `.py`는 프로젝트 폴더 바로 아래의 `check.py`에 붙여넣어 실행합니다(`mywork` 폴더 안에서 실행하지 않음)."]
    write_text(os.path.join(out, "README.md"), "\n".join(lines) + "\n")
    print(f"ch{n:02d}: 파일 {len(rows) + len(extra)}개 → {out}")


if __name__ == "__main__":
    targets = [int(x) for x in sys.argv[1:]] or list(range(2, 11))
    for n in targets:
        export(n)
