# -*- coding: utf-8 -*-
"""ChNN-PT내용.md -> lect/CH-NN-Content.md 일괄 변환 스크립트.

이 스크립트가 하는 일 (Ch02~Ch10):
1. 맨 앞에 "과정명"/"차시명"/"도입"/"학습내용,학습목표" 4개 페이지를 새로 삽입한다
   (도입/학습목표 내용은 아래 CHAPTERS 딕셔너리에 차시별로 직접 작성되어 있다).
2. "## 소주제 N. ..." 헤더와 "### 페이지 N. ..."(또는 "### [추가] 페이지 N-M. ...")
   헤더를 라인 단위로 스캔해 순서대로 찾아내고, 순차적으로 새 페이지 번호를 매긴다.
   ("[추가]" 하위 페이지가 원본에서 "---" 구분자 없이 바로 이어지는 경우가 있어,
   "---" 기준이 아니라 헤더 라인 자체를 기준으로 페이지 경계를 나눈다.)
3. 각 페이지 블록에서 마지막 "일반 산문 단락"(글머리표/코드블록/표/blockquote가 아닌
   마지막 문단)을 찾아 "> **[Note]** ..." 블록인용으로 감싼다 — 발표자 노트로 표시.
4. "---"로 페이지를 다시 이어 붙여 저장한다.

Ch01은 실습 내용이 강의안(PT) 안에 섞여 있는 유일한 차시라 처리 방식이 다르다.
Ch01-PT내용.md를 자동 변환하는 대신, 이미 사람이 페이지 분리·실습 제거·도입/학습목표
작성을 마친 `re-ch01.md`(프로젝트 루트)를 입력으로 받아 "[Note]" 표시만 추가한다.
`re-ch01.md`가 없으면 Ch01은 건너뛴다.

실행: python scripts/generate_lecture_content.py
결과: lect/CH-01-Content.md ~ lect/CH-10-Content.md
"""
import os
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LECT_DIR = os.path.join(PROJECT_ROOT, "lect")

COURSE_NAME = 'AI를 활용한 통계 보도자료 작성(NLP+LLM)'

PAGE_RE = re.compile(r'^###\s+(?:\[추가\]\s*)?페이지\s*[\d\-]+\.\s*(.+)$')
SUBTOPIC_RE = re.compile(r'^##\s+소주제\s*(\d+)\.\s*(.+)$')
CONTENT_PAGE_RE = re.compile(r'^###\s+페이지\s*\d+\.')


# ---------------------------------------------------------------------------
# 공통: 문단 분리 및 "발표자 노트" 감싸기
# ---------------------------------------------------------------------------

def split_paragraphs(body_lines):
    """빈 줄 기준으로 문단을 나누되, 코드펜스(```...```)는 하나의 문단으로 취급한다."""
    paragraphs = []
    current = []
    in_code = False
    for line in body_lines:
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code = not in_code
            current.append(line)
            if not in_code:
                paragraphs.append(current)
                current = []
            continue
        if in_code:
            current.append(line)
            continue
        if stripped == '':
            if current:
                paragraphs.append(current)
                current = []
        else:
            current.append(line)
    if current:
        paragraphs.append(current)
    return paragraphs


def is_plain_prose(para_lines):
    first = para_lines[0].strip()
    if first.startswith('```') or first.startswith('>') or first.startswith('|') or first.startswith('#'):
        return False
    if re.match(r'^[-*]\s', first) or re.match(r'^\d+[.)]\s', first):
        return False
    return True


def mark_note(body_lines):
    """마지막 산문 단락을 찾아 "> **[Note]** ..." blockquote로 감싼다."""
    paragraphs = split_paragraphs(body_lines)
    note_idx = None
    for i in range(len(paragraphs) - 1, -1, -1):
        if is_plain_prose(paragraphs[i]):
            note_idx = i
            break
    if note_idx is None:
        return body_lines  # 산문 문단이 없으면 그대로 둔다 (드문 경우)

    out = []
    for i, para in enumerate(paragraphs):
        if i == note_idx:
            out.append('> **[Note]** ' + para[0].strip())
            out.extend('> ' + extra for extra in para[1:])
        else:
            out.extend(para)
        if i != len(paragraphs) - 1:
            out.append('')
    return out


# ---------------------------------------------------------------------------
# Ch02~Ch10: 원본 PT 문서를 처음부터 재구성
# ---------------------------------------------------------------------------

def parse_sections(text):
    lines = text.replace('\r\n', '\n').split('\n')
    sections = []
    current = None
    in_code = False

    def finalize():
        if current is not None:
            body = current['body']
            while body and body[0].strip() == '':
                body.pop(0)
            while body and body[-1].strip() == '':
                body.pop()
            current['body'] = body
            sections.append(current)

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code = not in_code
            current = current or {'type': 'raw', 'title': None, 'body': []}
            current['body'].append(line)
            continue
        if in_code:
            current = current or {'type': 'raw', 'title': None, 'body': []}
            current['body'].append(line)
            continue
        if stripped == '---':
            continue
        if stripped.startswith('# Ch '):
            continue  # 원본 H1 제목 줄은 건너뜀 (차시명 페이지로 별도 처리)
        m_sub = SUBTOPIC_RE.match(stripped)
        if m_sub:
            finalize()
            current = {'type': 'subtopic',
                       'title': f"소주제 {m_sub.group(1)}. {m_sub.group(2)}", 'body': []}
            continue
        m_page = PAGE_RE.match(stripped)
        if m_page:
            finalize()
            current = {'type': 'page', 'title': m_page.group(1), 'body': []}
            continue
        current = current or {'type': 'raw', 'title': None, 'body': []}
        current['body'].append(line)
    finalize()
    return sections


def transform(text, chapter_no, chapter_title, intro_text, study_content, study_goals):
    sections = parse_sections(text)
    result = []

    def add_simple_page(md_heading):
        result.extend([md_heading, '', '---', ''])

    add_simple_page(f'# 페이지 01. 과정명 "{COURSE_NAME}"')
    add_simple_page(f'# 페이지 02. 차시명 "Ch {chapter_no:02d}. {chapter_title}"')

    result.extend(['# 페이지 03. 도입', '', intro_text.strip(), '', '---', ''])

    result.extend(['# 페이지 04. 학습내용, 학습목표', '', '학습내용'])
    result.extend(f'{i}. {c}' for i, c in enumerate(study_content, 1))
    result.extend(['', '학습목표'])
    result.extend(f'{i}. {g}' for i, g in enumerate(study_goals, 1))
    result.extend(['', '---', ''])

    page_num = 5
    for sec in sections:
        if sec['type'] == 'subtopic':
            result.extend([f"# 페이지 {page_num:02d}. {sec['title']}", '', '---', ''])
            page_num += 1
        elif sec['type'] == 'page':
            body = mark_note(sec['body'])
            result.append(f"### 페이지 {page_num:02d}. {sec['title']}")
            result.append('')
            result.extend(body)
            result.extend(['', '---', ''])
            page_num += 1
        elif sec['body']:
            result.extend(sec['body'])
            result.append('')

    text_out = '\n'.join(result).strip()
    while text_out.endswith('---'):
        text_out = text_out[:-3].rstrip()
    return text_out + '\n'


# ---------------------------------------------------------------------------
# Ch01: 이미 손질된 re-ch01.md에 "[Note]"만 추가
# ---------------------------------------------------------------------------

def transform_ch01(text):
    lines = text.replace('\r\n', '\n').split('\n')
    out = []
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        if CONTENT_PAGE_RE.match(line.strip()):
            out.append(line)
            i += 1
            body = []
            while i < n and lines[i].strip() != '---':
                body.append(lines[i])
                i += 1
            while body and body[0].strip() == '':
                body.pop(0)
            while body and body[-1].strip() == '':
                body.pop()
            out.append('')
            out.extend(mark_note(body))
            out.append('')
            if i < n:
                out.append(lines[i])
                i += 1
        else:
            out.append(line)
            i += 1

    text_out = '\n'.join(out)
    text_out = re.sub(r'\n{3,}', '\n\n', text_out).strip()
    while text_out.endswith('---'):
        text_out = text_out[:-3].rstrip()
    return text_out + '\n'


# ---------------------------------------------------------------------------
# 차시별 도입/학습내용/학습목표 (Ch02~Ch10)
# ---------------------------------------------------------------------------

CHAPTERS = {
    2: dict(
        title="텍스트 정제 및 데이터 구조화 기법 실습",
        intro=(
            "1차시에서는 AI가 계산과 문장 작성을 나누어 맡는 전체 그림과 보안 원칙을 살펴보았습니다. "
            "이제 그 그림을 실제로 채워나가기 위한 첫 단계, 즉 원자료를 다루는 방법부터 시작합니다. "
            "통계 보도자료의 재료는 깔끔하게 정리된 표로만 오지 않습니다. 엑셀 통계표처럼 정형화된 자료도 있고, "
            "담당자가 작성한 설명 보고서처럼 형식이 정해지지 않은 비정형 자료도 함께 섞여 있습니다. "
            "이 서로 다른 두 자료를 어떻게 구분하고, 하나의 표준 형식으로 정리하며, 실시간으로 공개된 공공 데이터까지 "
            "끌어와 활용할 수 있는지가 이번 시간의 핵심입니다. 이 단계를 제대로 갖추지 않으면, 이후에 아무리 정교한 "
            "계산과 AI 문장 생성 기능을 붙이더라도 애초에 잘못되거나 불완전한 자료 위에 쌓아 올리는 셈이 됩니다."
        ),
        content=[
            "정형, 비정형 통계자료의 특징 이해",
            "AI 분석을 위한 데이터 항목 정의",
            "텍스트 정제, 표준화, 구조화 원칙 이해",
            "공공 Open API 연동 및 실시간 데이터 수집",
        ],
        goals=[
            "정형 데이터와 비정형 데이터의 차이를 구분하고 설명할 수 있다.",
            "보도자료 작성에 필요한 데이터 항목을 정의하고 우선순위를 구분할 수 있다.",
            "원본 텍스트를 정제·표준화·구조화하여 표준 데이터 구조로 변환할 수 있다.",
            "공공데이터포털 Open API를 연동하여 실시간 통계 데이터를 수집할 수 있다.",
        ],
    ),
    3: dict(
        title="주요 NLP 기법 실습",
        intro=(
            "2차시에서 정형·비정형 데이터를 하나의 표준 구조로 정리하는 방법을 익혔다면, 이번 3차시에서는 그 표준 "
            "데이터 안에 담긴 비정형 원문을 실제로 분석하는 단계로 넘어갑니다. 사람이 쓴 문장은 정보가 풍부하지만, "
            "그 안에서 어떤 단어와 문장이 정말 중요한지는 기계가 스스로 판단할 수 있어야 합니다. 이번 시간에는 "
            "형태소 분석과 통계적 기법을 이용해 문서에서 핵심 키워드를 뽑아내고, 여러 문장 중 가장 중요한 문장을 "
            "골라내며, 이 둘을 결합해 문서 전체의 주제를 규칙 기반으로 요약하는 방법을 배웁니다. 아직 생성형 AI를 "
            "사용하지 않고도 이런 분석이 가능하다는 것을 확인하는 것이 이번 차시의 중요한 목표입니다."
        ),
        content=["키워드 추출 기능 구현", "주요 문장 추출 기능 구현", "문서 주제 요약 기능 구현"],
        goals=[
            "형태소 분석과 TF-IDF를 이용해 문서의 핵심 키워드를 추출할 수 있다.",
            "TextRank 알고리즘을 이용해 문서의 주요 문장을 원문 그대로 추출할 수 있다.",
            "키워드와 주요 문장을 결합해 규칙 기반으로 문서 주제를 요약할 수 있다.",
        ],
    ),
    4: dict(
        title="LLM 기반 텍스트 요약 실습",
        intro=(
            "3차시에서는 규칙과 통계에 기반한 전통적인 자연어 처리로 키워드와 주요 문장을 뽑아냈습니다. 이번 4차시에서는 "
            "한 단계 더 나아가, 생성형 AI(LLM)에게 그 결과를 참고 자료로 건네주고 사람이 읽기 좋은 자연스러운 문장으로 "
            "다시 쓰게 합니다. 다만 AI에게 무작정 맡기면 사실과 다른 내용을 그럴듯하게 지어내는 환각 현상이 발생할 수 "
            "있으므로, 역할과 맥락, 출력 형식, 제약 조건을 명확히 담은 프롬프트를 설계하는 방법과 함께, 생성된 문장 속 "
            "숫자가 원본과 정확히 일치하는지 자동으로 검증하는 방법까지 함께 다룹니다."
        ),
        content=["요약 프롬프트 설계", "요약문 계획 및 구현", "요약 결과 검토 및 수정"],
        goals=[
            "역할·맥락·출력형식·제약조건을 담은 LLM 프롬프트를 설계할 수 있다.",
            "Claude API를 호출하여 통계자료를 3줄 요약과 제목 후보로 생성할 수 있다.",
            "생성된 요약문의 수치를 원본 데이터와 자동으로 대조·검증할 수 있다.",
        ],
    ),
    5: dict(
        title="통계적 패턴 기반 텍스트와 통계자료 해석",
        intro=(
            "지금까지는 이미 문장으로 작성된 원문을 다루었다면, 이번 5차시에서는 순수한 숫자로만 이루어진 통계표 "
            "자체를 분석 대상으로 삼습니다. 보도자료에서 가장 중요한 것은 결국 '얼마나 늘었고 줄었는지', '어떤 항목이 "
            "가장 크고 작은지', '이 수치가 역대 최고·최저에 해당하는지'를 정확히 짚어내는 일입니다. 이러한 계산을 "
            "AI에게 맡기면 실수할 위험이 있으므로, 이번 시간에는 pandas를 이용해 증감률과 비중, 순위를 프로그램이 "
            "직접 계산하고, 임계값과 과거 이력을 기준으로 특이점을 자동으로 탐지하며, 그 결과를 정해진 문장 틀에 "
            "채워 넣어 1차 해석문을 만드는 방법을 배웁니다."
        ),
        content=["증감률·비중·순위 계산", "주요 변화와 특이점 자동 탐지", "통계 해석 분석 내용 생성"],
        goals=[
            "pandas를 이용해 전월대비·전년동월대비증감률, 비중, 순위를 계산할 수 있다.",
            "임계값과 과거 이력 비교를 기준으로 특이점을 자동으로 탐지할 수 있다.",
            "특이점 유형에 맞는 해석 문장을 규칙 기반으로 자동 생성할 수 있다.",
        ],
    ),
    6: dict(
        title="표, 그래프 기반 설명문 자동 생성 실습",
        intro=(
            "5차시에서 계산한 증감률과 순위 같은 지표는 숫자만으로는 한눈에 와닿지 않을 때가 많습니다. 보도자료에는 "
            "그래서 항상 표와 그래프가 함께 실립니다. 이번 6차시에서는 계산된 지표를 막대, 꺾은선, 원형 그래프로 "
            "시각화하는 방법과, 각 그래프가 어떤 이야기를 담고 있는지를 다시 문장으로 풀어내는 방법을 배웁니다. "
            "같은 데이터라도 그래프 유형에 따라 강조해야 할 포인트가 다르다는 것, 그리고 그 설명문에는 반드시 "
            "'무엇에 대한 설명인지'가 분명히 드러나야 한다는 것이 이번 시간의 핵심입니다."
        ),
        content=["표·그래프 구성", "그래프 유형별 설명문 템플릿 설계", "표·그래프 설명문 생성 기능 구현"],
        goals=[
            "matplotlib으로 막대·꺾은선·원형 그래프를 생성할 수 있다.",
            "그래프 유형에 맞는 설명 포인트를 구분하고 문장 템플릿을 설계할 수 있다.",
            "그래프 데이터를 입력받아 설명문을 자동으로 생성하는 함수를 구현할 수 있다.",
        ],
    ),
    7: dict(
        title="통계 보도자료 작성 실습1 (핵심지표 요약)",
        intro=(
            "1~6차시를 거치며 데이터 수집, 정제, NLP 분석, 요약, 통계 해석, 그래프 설명까지 보도자료의 재료를 모두 "
            "준비했습니다. 이제 7차시부터는 이 재료들을 실제로 조립해서 보도자료라는 완성된 글의 첫인상, 즉 제목과 "
            "부제, 리드문(첫 문단)을 만들어 볼 차례입니다. 엑셀이나 PDF 원자료를 직접 입력받는 단계부터 시작해서, "
            "그중 정말 중요한 핵심지표만 골라내고, 6하원칙에 따라 빠짐없이 정보를 담은 리드문을 생성한 뒤, 그 안의 "
            "모든 숫자가 원본과 일치하는지 검증하는 과정까지 다룹니다."
        ),
        content=["핵심지표 선정", "제목·부제·리드문 생성 프롬프트 설계", "보도자료 첫 문단 자동 생성"],
        goals=[
            "xlsx 또는 PDF 원자료를 입력받아 표준 데이터로 변환할 수 있다.",
            "필수·선택·참고 기준에 따라 핵심지표를 자동으로 선정할 수 있다.",
            "6하원칙에 기반한 프롬프트로 제목·부제·리드문을 생성하고 검증할 수 있다.",
        ],
    ),
    8: dict(
        title="통계 보도자료 작성 실습2 (그래프 설명)",
        intro=(
            "7차시에서 보도자료의 첫 문단인 리드문을 완성했다면, 이제 그 뒤에 이어질 본문을 채울 차례입니다. "
            "리드문이 전체 내용을 압축한 한 문단이라면, 본문은 그 내용을 품목별, 분야별로 구체적으로 풀어내는 "
            "부분입니다. 이번 8차시에서는 6차시에서 만든 짧은 그래프 설명문 하나하나를, 두괄식 구조를 갖춘 완결된 "
            "본문 단락으로 확장하는 방법과, 여러 단락을 연결어로 자연스럽게 이어 붙여 하나의 글로 완성하는 방법을 "
            "배웁니다."
        ),
        content=["그래프별 설명 소재 정리", "그래프 설명을 본문 단락으로 확장", "보도자료 본문 생성 기능 구현"],
        goals=[
            "그래프 설명 소재를 소주제 단위로 정리할 수 있다.",
            "프롬프트를 이용해 짧은 설명문을 두괄식 본문 단락으로 확장할 수 있다.",
            "여러 본문 단락을 연결어로 자연스럽게 이어 붙이는 함수를 구현할 수 있다.",
        ],
    ),
    9: dict(
        title="통계 보도자료 작성 실습3 (문체, 자동교정, 감수 모델 실습)",
        intro=(
            "7~8차시를 거치며 제목, 부제, 리드문, 본문까지 담긴 보도자료 초안을 완성했습니다. 다만 이 초안은 여러 "
            "차시에 걸쳐 서로 다른 프롬프트로 생성되었기 때문에 문체가 뒤섞여 있을 수 있습니다. 이번 9차시에서는 "
            "초안 전체의 문체를 하나로 통일하고, 정규표현식으로 표기 오류를 자동 검수하며, 마지막으로 AI에게 "
            "제3자 감수자 역할을 맡겨 사람이 놓치기 쉬운 문제까지 짚어내는 방법을 배웁니다. 이는 사람이 최종 승인을 "
            "내리기 전, 자동화 시스템이 갖추어야 할 마지막 안전장치입니다."
        ),
        content=["보도자료 문체 변환", "수치·단위·표현 오류 검수", "자동 교정·감수 기능 구현"],
        goals=[
            "초안 전체를 통계청 보도자료 표준 문체로 통일할 수 있다.",
            "정규표현식과 수치 교차 검증으로 표기 오류와 환각을 자동으로 검수할 수 있다.",
            "AI 감수자 역할을 부여해 지적사항을 받고 반영 여부를 판단할 수 있다.",
        ],
    ),
    10: dict(
        title="AI 기반 보도자료 자동 생성 시스템 구축 실습",
        intro=(
            "지난 9번의 차시를 거치며 데이터 수집부터 최종 검수까지 필요한 모든 부품을 하나씩 만들어왔습니다. 이제 "
            "마지막 10차시에서는 이 부품들을 하나의 실행 스크립트로 연결하여, 원자료 입력 하나만으로 검수까지 끝난 "
            "보도자료가 자동으로 완성되는 전체 시스템을 구축합니다. 입력부터 저장까지 전 과정을 하나의 main 함수로 "
            "통합하고, 실제로 실행해 결과를 확인하며, 앞으로 이 시스템을 다른 통계표나 더 큰 규모로 확장하려면 "
            "무엇을 더 고민해야 하는지까지 짚어봅니다."
        ),
        content=["전체 자동화 워크플로우 설계", "분석·요약·작성·검수 기능 통합"],
        goals=[
            "지금까지 만든 함수들을 하나의 main 함수로 통합하여 설계할 수 있다.",
            "입력부터 저장까지 전체 파이프라인을 실행하고 결과를 검증할 수 있다.",
        ],
    ),
}


def main():
    os.makedirs(LECT_DIR, exist_ok=True)

    ch01_src = os.path.join(PROJECT_ROOT, "re-ch01.md")
    if os.path.exists(ch01_src):
        with open(ch01_src, "r", encoding="utf-8") as f:
            out = transform_ch01(f.read())
        dst = os.path.join(LECT_DIR, "CH-01-Content.md")
        with open(dst, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"generated {dst}")
    else:
        print("re-ch01.md 없음 — Ch01 건너뜀 (실습 제거·도입/학습목표 작성이 먼저 필요)")

    for n, spec in CHAPTERS.items():
        src = os.path.join(PROJECT_ROOT, f"Ch{n:02d}-PT내용.md")
        with open(src, "r", encoding="utf-8") as f:
            text = f.read()
        out = transform(text, n, spec["title"], spec["intro"], spec["content"], spec["goals"])
        dst = os.path.join(LECT_DIR, f"CH-{n:02d}-Content.md")
        with open(dst, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"generated {dst}")


if __name__ == "__main__":
    main()
