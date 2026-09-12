# 페이지 01. 과정명 "AI를 활용한 통계 보도자료 작성(NLP+LLM)"

---

# 페이지 02. 차시명 "Ch 03. 주요 NLP 기법 실습"

---

# 페이지 03. 도입

2차시에서 정형·비정형 데이터를 하나의 표준 구조로 정리하는 방법을 익혔다면, 이번 3차시에서는 그 표준 데이터 안에 담긴 비정형 원문을 실제로 분석하는 단계로 넘어갑니다. 사람이 쓴 문장은 정보가 풍부하지만, 그 안에서 어떤 단어와 문장이 정말 중요한지는 기계가 스스로 판단할 수 있어야 합니다. 이번 시간에는 형태소 분석과 통계적 기법을 이용해 문서에서 핵심 키워드를 뽑아내고, 여러 문장 중 가장 중요한 문장을 골라내며, 이 둘을 결합해 문서 전체의 주제를 규칙 기반으로 요약하는 방법을 배웁니다. 아직 생성형 AI를 사용하지 않고도 이런 분석이 가능하다는 것을 확인하는 것이 이번 차시의 중요한 목표입니다.

---

# 페이지 04. 학습내용, 학습목표

학습내용
1. 키워드 추출 기능 구현
2. 주요 문장 추출 기능 구현
3. 문서 주제 요약 기능 구현

학습목표
1. 형태소 분석과 TF-IDF를 이용해 문서의 핵심 키워드를 추출할 수 있다.
2. TextRank 알고리즘을 이용해 문서의 주요 문장을 원문 그대로 추출할 수 있다.
3. 키워드와 주요 문장을 결합해 규칙 기반으로 문서 주제를 요약할 수 있다.

---

> **[수정, 7차 세션] 이 차시 결과물의 위치 명확화 (REVIEW_Ch02-10.md A-3)**: 이 차시가 만드는 `NLP분석결과`(핵심키워드, 주요문장)는 **보도자료의 사실 확정에는 쓰이지 않는 참고용 분석**입니다. 실제 헤드라인·본문 생성은 5차시 `add_calculated_indicators`가 계산한 검증된 수치만 근거로 삼습니다(Ch03-실습.md 페이지4 참고). 7차 세션부터는 4차시의 `generate_summary`(이 결과를 입력으로 쓰는 유일한 함수)가 `main.py`에서 실제로 호출되어 `요약결과`로 저장되고, 그 `제목후보`가 7차시 헤드라인 생성 프롬프트에 "참고용 표현 아이디어"로만 전달됩니다 — 새로운 숫자를 들여오지는 않으므로 최종 수치 검증(`verify_numbers`) 대상에는 영향을 주지 않습니다.

# 페이지 05. 소주제 1. 키워드 추출 기능 구현

---

### 페이지 06. 3차시 학습 목표와 전체 흐름

3차시에서 만들 세 가지 기능

- 키워드 추출: 문서에서 가장 중요한 단어를 골라내는 기능
- 주요 문장 추출: 문서에서 핵심을 담고 있는 문장을 골라내는 기능
- 문서 주제 요약: 키워드와 주요 문장을 결합해 짧은 요약을 만드는 기능
- 2차시에서 완성한 표준 입력 데이터(JSON)의 비정형 원문을 입력값으로 사용

> **[Note]** 2차시에서는 데이터를 정제하고 표준 구조로 담아내는 방법을 배웠습니다. 이번 3차시에서는 그 표준 데이터 안에 들어있는 비정형 문장을 실제로 분석하여, 핵심 단어와 핵심 문장을 자동으로 뽑아내는 세 가지 NLP 기능을 직접 구현합니다.

---

### 페이지 07. 키워드 추출의 원리, 단어가 얼마나 중요한지 점수 매기기

키워드 추출의 핵심 아이디어

- 문서 안에서 자주 등장하는 단어일수록 중요할 가능성이 높음
- 그러나 조사, 어미처럼 모든 문서에 흔히 등장하는 단어는 제외해야 함
- TF-IDF: 한 문서에서는 자주 나오지만, 다른 문서에서는 드물게 나오는 단어에 높은 점수를 부여하는 계산 방식

> **[Note]** 키워드 추출은 단순히 자주 나오는 단어를 세는 것이 아닙니다. "이", "그", "있다"처럼 모든 문서에 흔한 단어는 제외하고, 해당 문서만의 특징적인 단어를 찾아내야 합니다. 이를 위해 TF-IDF라는 계산 방식을 사용하여 단어별 중요도 점수를 매깁니다.

---

### 페이지 08. 한국어 형태소 분석기로 명사만 골라내기

형태소 분석기 활용

- 한국어는 조사와 어미가 단어에 붙어 있어, 영어처럼 공백만으로 단어를 나누기 어려움
- 형태소 분석기(Kiwi, KoNLPy 등)를 사용해 문장을 의미 단위로 쪼갬
- 키워드 후보로는 대부분 명사(NNG, NNP)만 추출하여 사용

```python
from kiwipiepy import Kiwi

_kiwi = Kiwi()  # 형태소 분석기는 초기화 비용이 크므로 모듈 전역에서 한 번만 생성

# 실제 실행 결과, 기본 사전만으로는 "온라인쇼핑"이 "온라인"+"쇼핑"으로, "거래액은"의
# "거래액"이 문맥에 따라 "거래"+"액"으로 갈라지는 경우가 확인되었다. 보도자료의 핵심
# 소재가 쪼개지지 않도록 도메인 복합명사는 사용자 사전에 등록해 하나의 명사로 고정한다.
for _word in ["온라인쇼핑", "모바일쇼핑", "거래액", "역대급"]:
    _kiwi.add_user_word(_word, "NNP", 0.0)

def extract_nouns(text: str) -> list:
    """텍스트에서 명사(NNG, NNP 등 'NN'으로 시작하는 품사 태그)만 추출한다."""
    return [token.form for token in _kiwi.tokenize(text) if token.tag.startswith("NN")]

text = "온라인쇼핑 거래액은 전월 대비 1.5% 증가하였다."
nouns = extract_nouns(text)
print(nouns)
# ['온라인쇼핑', '거래액', '전월', '대비', '증가']
```

> **[Note]** 한국어 문장에서 바로 키워드를 뽑으면 조사나 어미까지 함께 섞여 나옵니다. 그래서 먼저 형태소 분석기로 문장을 쪼갠 뒤, 명사에 해당하는 품사만 골라내는 전처리 과정을 거칩니다. `extract_nouns` 함수로 만들어두면 이후 실습(Ch03-실습)에서 `extract_nouns(data["원문"])` 형태로 바로 재사용할 수 있습니다.

> **[수정] 실행 가능한 함수로 보강 + 실제 실행으로 발견한 토크나이저 문제 수정**: 기존 문서는 위 코드가 한 번의 예시 실행일 뿐, 재사용 가능한 함수로 정의되어 있지 않았고, 예시 결과(`['온라인쇼핑', '거래액', '전월', '대비']`)도 실제 kiwipiepy 실행 결과와 달랐습니다. 실제로 `myvenv`에 `kiwipiepy 0.23.2`를 설치해 돌려보니: ① "온라인쇼핑"이 "온라인"+"쇼핑" 두 개의 명사로 분리되고, ② "거래액은"처럼 조사가 붙으면 "거래액"이 "거래"+"액"으로 갈라지는 경우가 있었으며(반면 "거래액 비중"처럼 조사가 없으면 붙어 있는 등 문맥에 따라 결과가 달라짐), ③ "증가하였다"에서 "증가"도 명사로 추출되어 예시의 4개보다 많은 명사가 나왔습니다. ①·②는 `kiwi.add_user_word(...)`로 도메인 복합명사를 사용자 사전에 등록해 고정했고, ③은 실제로 "증가"도 유효한 명사이므로 예시 주석을 실제 실행 결과에 맞게 수정했습니다. 이후 페이지의 `extract_keywords_tfidf`, `split_sentences`, `extract_main_sentences`도 같은 이유로 함수 형태로 보강했습니다.

---

### 페이지 09. Python 코드, TF-IDF로 키워드 점수 계산하기

scikit-learn을 활용한 TF-IDF 계산

```python
from sklearn.feature_extraction.text import TfidfVectorizer

documents = [
    "온라인쇼핑 거래액 전월 대비 증가",
    "온라인쇼핑 거래액 역대 최대 기록",
    "소비자 물가 상승률 전월 대비 둔화"
]

vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(documents)
keywords = vectorizer.get_feature_names_out()
scores = tfidf_matrix.toarray()[1]  # 두 번째 문서(온라인쇼핑 거래액 역대 최대 기록)

for word, score in sorted(zip(keywords, scores), key=lambda x: -x[1])[:5]:
    print(word, round(score, 3))
```

명사만 추출된 단어 목록을 scikit-learn의 TfidfVectorizer에 입력하면, 각 단어에 대한 중요도 점수가 자동으로 계산됩니다. 점수가 높은 순서대로 정렬하면 문서를 대표하는 핵심 키워드 목록을 얻을 수 있습니다.

> **[수정] 단일 문서 분석 시 주의점**: 위 예시는 서로 다른 보도자료 "3건"을 놓고 비교하기 때문에 TF-IDF가 의미를 가집니다. 그러나 실제 실습(Ch03-실습)에서는 보도자료 원문 "1건"만 분석 대상입니다. 문서가 1건뿐이면 IDF(다른 문서에서 얼마나 드문가)가 모든 단어에서 똑같아져, TF-IDF가 사실상 단순 빈도(TF)와 차이가 없어지는 한계가 있습니다.
>
> 이를 보완하기 위해 아래 `extract_keywords_tfidf` 함수는 한 편의 보도자료를 "문장 단위로 쪼갠 뒤, 각 문장을 하나의 문서처럼" 취급하여 TF-IDF를 계산합니다. 이렇게 하면 "여러 문장에 고르게 등장하는 흔한 단어"보다 "특정 문장에 집중적으로 등장하는 단어"에 높은 점수를 주는, 문서 1건에서도 유효한 TF-IDF 키워드 추출이 가능합니다. (여러 보도자료를 누적한 배경 코퍼스가 있다면 그 코퍼스로 IDF를 계산하는 방식이 더 정교하며, 10차시 이후 확장 과제로 남겨둡니다.)

```python
from sklearn.feature_extraction.text import TfidfVectorizer

def extract_keywords_tfidf(text: str, top_n: int = 5) -> list:
    """보도자료 원문 1건을 문장 단위 코퍼스로 취급해 TF-IDF 키워드를 추출한다."""
    sentences = split_sentences(text)
    noun_docs = [" ".join(extract_nouns(s)) for s in sentences]
    noun_docs = [doc for doc in noun_docs if doc.strip()]
    if not noun_docs:
        return []

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(noun_docs)
    terms = vectorizer.get_feature_names_out()
    # 문장별 최고 점수를 단어의 대표 점수로 사용
    max_scores = tfidf_matrix.toarray().max(axis=0)

    keyword_scores = list(zip(terms, max_scores))
    return clean_keywords(keyword_scores, top_n=top_n)
```

> **[Note]** `extract_keywords_tfidf`는 내부적으로 `split_sentences`(다음 소주제에서 정의)로 문장을 나누고, 각 문장에서 `extract_nouns`로 명사만 남긴 뒤 TF-IDF를 계산합니다. 이렇게 만들어두면 `extract_keywords_tfidf(data["원문"], top_n=5)` 형태로 원문 텍스트 하나만 넘겨도 핵심 키워드 목록을 얻을 수 있습니다.

---

### 페이지 10. 불용어 처리와 키워드 추출 결과 다듬기

키워드 품질을 높이는 후처리

- 불용어(Stopword) 목록: "등", "및", "수" 등 의미 없는 명사를 제외 목록으로 관리
- 최소 글자 수 제한: 한 글자 명사는 대부분 노이즈이므로 제외
- 상위 N개 제한: 실제 보도자료에는 5~10개 내외의 핵심 키워드만 필요

```python
stopwords = {"등", "및", "수", "것"}

def clean_keywords(keyword_scores, top_n=5):
    filtered = [(w, s) for w, s in keyword_scores if w not in stopwords and len(w) > 1]
    return sorted(filtered, key=lambda x: -x[1])[:top_n]
```

> **[Note]** TF-IDF로 계산한 결과를 그대로 사용하면 의미 없는 단어가 섞여 나올 수 있습니다. 불용어 목록으로 걸러내고, 한 글자 단어를 제외하고, 상위 개수를 제한하는 후처리를 거쳐야 실제 보도자료에 활용할 수 있는 깔끔한 키워드 목록이 완성됩니다.

> **[수정] 함수 배치 순서 안내**: `clean_keywords`는 앞 페이지의 `extract_keywords_tfidf` 함수 내부에서 이미 호출하고 있으므로, 실습 코드 파일에서는 `clean_keywords`를 `extract_keywords_tfidf`보다 먼저(위쪽에) 정의해야 합니다.

---

# 페이지 11. 소주제 2. 주요 문장 추출 기능 구현

---

### 페이지 12. 주요 문장 추출이 필요한 이유

키워드만으로는 부족한 이유

- 키워드는 단어 단위 정보만 제공하여, 문맥이나 인과관계를 알 수 없음
- 보도자료 원문이 길 경우, 핵심 내용이 담긴 문장 자체를 골라내는 것이 효율적
- 주요 문장을 먼저 추출하면, 이후 요약이나 리드문 작성 시 근거 문장으로 활용 가능

> **[Note]** 키워드 추출은 문서의 핵심 단어를 알려주지만, 문장 전체의 맥락까지는 담지 못합니다. 그래서 원문이 여러 문장으로 구성된 경우, 문서 전체에서 가장 중요한 의미를 담고 있는 문장 자체를 골라내는 주요 문장 추출 기법이 함께 필요합니다.

---

### 페이지 13. TextRank 알고리즘의 원리, 문장들의 인기 투표

TextRank 핵심 개념

- 문서 안의 모든 문장을 하나의 그래프의 노드(점)로 봄
- 문장과 문장 사이의 유사도를 계산하여 노드를 연결하는 선(엣지)의 굵기로 표현
- 다른 문장들과 유사한 내용을 많이 공유하는 문장일수록 중요한 문장으로 판단 (검색엔진의 페이지랭크 원리와 유사)

> **[Note]** TextRank는 검색엔진이 웹페이지의 중요도를 계산하는 방식을 문장 단위에 적용한 알고리즘입니다. 여러 문장과 공통된 단어를 많이 공유하는 문장일수록, 마치 여러 사람에게 인용되는 유명한 문장처럼 중요도가 높다고 판단합니다.

---

### 페이지 14. Python 코드, TextRank로 주요 문장 뽑아내기

> **[수정] summa 라이브러리 대신 직접 구현하는 이유**: 기존 문서는 `summa.summarizer.summarize(text, language="korean")`를 사용했습니다. 그러나 summa가 공식 지원하는 언어(영어, 독일어, 프랑스어 등 스노우볼 어간추출기가 있는 서구권 언어) 목록에 한국어가 없어, `language="korean"` 옵션은 정상 동작을 보장하지 않습니다. 그래서 이번 검토에서는 summa 없이, 이미 배운 `TfidfVectorizer`(문장 벡터화)와 `networkx`(그래프의 PageRank 계산)만으로 TextRank를 직접 구현하는 방식으로 대체합니다. 원리는 동일하며, 오히려 앞서 배운 TF-IDF 개념과 자연스럽게 이어집니다.

Python 코드, 직접 구현한 TextRank

```python
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx

def split_sentences(text: str) -> list:
    """마침표/느낌표/물음표 뒤 공백을 기준으로 문장을 분리한다."""
    text = text.strip()
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

def extract_main_sentences(sentences: list, ratio: float = 0.5) -> list:
    """문장 간 코사인 유사도 그래프에 PageRank를 적용해 주요 문장을 원문 순서 그대로 반환한다."""
    if len(sentences) <= 1:
        return sentences

    noun_docs = [" ".join(extract_nouns(s)) or s for s in sentences]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(noun_docs)
    similarity_matrix = cosine_similarity(tfidf_matrix)
    for i in range(len(similarity_matrix)):
        similarity_matrix[i, i] = 0  # 자기 자신과의 유사도(대각선=1.0)는 제거해 self-loop로 인한 점수 왜곡 방지

    graph = nx.from_numpy_array(similarity_matrix)
    scores = nx.pagerank(graph)

    top_n = max(1, round(len(sentences) * ratio))
    ranked_idx = sorted(scores, key=scores.get, reverse=True)[:top_n]
    selected_idx = sorted(ranked_idx)  # 원문에 등장하는 순서로 재정렬
    return [sentences[i] for i in selected_idx]

text = """2026년 1월 온라인쇼핑 거래액은 201,250억 원으로 전월 대비 1.5% 증가하였다. 전년동월대비로는 8.7% 증가한 수치이다. 이는 역대 1월 기준 최대치를 기록한 것이다. 모바일쇼핑 거래액 비중은 전체의 78%를 차지하며 꾸준한 증가세를 보이고 있다."""

sentences = split_sentences(text)
result = extract_main_sentences(sentences, ratio=0.5)
print(result)
```

> **[Note]** 문장을 노드로, 문장 간 TF-IDF 코사인 유사도를 엣지 가중치로 하는 그래프를 만든 뒤, `networkx.pagerank`로 각 문장의 중요도를 계산합니다. 점수가 높은 상위 문장을 원문에 등장한 순서 그대로 반환하도록 하여, 다음 페이지(원문 대조 검증)에서 "문장 순서가 원문과 같은가"를 확인하기 쉽게 만들었습니다. `ratio` 옵션으로 몇 퍼센트의 문장을 추출할지 조절하는 것은 기존과 동일합니다.

---

### 페이지 15. 문장 추출 결과와 원본 대조 확인

추출 결과 검증

- 추출된 문장이 원문에 실제로 존재하는 문장인지 반드시 확인 (문장을 새로 생성하지 않고 원문에서 그대로 선택)
- 추출된 문장 안의 숫자가 원본 수치와 정확히 일치하는지 재확인
- 핵심 특이사항(역대 최대 등)을 담은 문장이 우선적으로 뽑혔는지 확인

> **[Note]** 주요 문장 추출은 새로운 문장을 만드는 것이 아니라, 원문 안에 이미 존재하는 문장 중에서 고르는 방식입니다. 따라서 추출 결과가 원문과 정확히 일치하는지, 그리고 핵심 특이사항이 포함된 문장이 잘 선택되었는지 검증하는 과정이 중요합니다.

---

# 페이지 16. 소주제 3. 문서 주제 요약 기능 구현

---

### 페이지 17. 문서 주제 요약이란, 키워드와 문장의 결합

주제 요약의 구성 방식

- 키워드 추출 결과 + 주요 문장 추출 결과를 결합하여 문서의 핵심을 짧게 정리
- 규칙 기반 요약: "핵심 키워드가 포함된 주요 문장"만 골라 순서대로 나열하는 방식
- 이 결과는 다음 차시(4차시)의 LLM 기반 요약에서 참고 자료로 활용됨

> **[Note]** 지금까지 만든 키워드와 주요 문장은 각각 독립적인 결과물입니다. 이번 단계에서는 두 결과를 결합하여, 핵심 키워드를 포함하고 있는 주요 문장만 골라 문서 전체의 주제를 요약하는 규칙 기반 요약 기능을 만듭니다.

---

### 페이지 18. Python 코드, 키워드 기반 문장 필터링

키워드가 포함된 문장만 골라내는 함수

```python
def filter_sentences_by_keywords(sentences, keywords):
    keyword_set = set(keywords)
    result = []
    for sentence in sentences:
        if any(keyword in sentence for keyword in keyword_set):
            result.append(sentence)
    return result

sentences = ["온라인쇼핑 거래액은 201,250억 원으로 증가하였다.", "이는 역대 최대치이다."]
keywords = ["온라인쇼핑", "거래액", "최대"]
summary_candidates = filter_sentences_by_keywords(sentences, keywords)
```

> **[Note]** TextRank로 추출한 주요 문장 목록 중에서, 다시 한번 TF-IDF 키워드를 포함하고 있는지 확인하는 필터링 단계를 거칩니다. 이렇게 이중으로 검증된 문장은 문서의 핵심 주제를 담고 있을 가능성이 매우 높습니다.

---

### 페이지 19. NLP 분석 결과를 표준 데이터 구조에 통합하기

표준 JSON 확장, NLP분석결과 필드 추가

```json
{
  "문서정보": { "제목": "2026년 1월 온라인쇼핑 동향" },
  "계산지표": { "총거래액": 201250, "전월대비증감률": 1.5 },
  "핵심내용": ["온라인쇼핑 거래액 역대 최대 달성"],
  "NLP분석결과": {
    "핵심키워드": ["온라인쇼핑", "거래액", "역대", "최대"],
    "주요문장": ["온라인쇼핑 거래액은 201,250억 원으로 증가하였다.", "이는 역대 최대치이다."]
  }
}
```

> **[Note]** 2차시에서 만든 표준 데이터 구조에 NLP 분석 결과를 담을 새로운 필드를 추가합니다. 핵심 키워드와 주요 문장을 이 구조 안에 함께 저장해두면, 다음 차시부터 이어지는 모든 AI 작성 단계에서 참고 자료로 재사용할 수 있습니다.

---

### 페이지 20. 세 가지 NLP 기능을 하나로 묶는 파이프라인 함수

통합 함수 구조

```python
def analyze_document(raw_text: str, standard_data: dict) -> dict:
    keywords = [w for w, _ in extract_keywords_tfidf(raw_text)]
    sentences = split_sentences(raw_text)
    main_sentences = extract_main_sentences(sentences)
    summary_candidates = filter_sentences_by_keywords(main_sentences, keywords)

    standard_data["NLP분석결과"] = {
        "핵심키워드": keywords,
        "주요문장": summary_candidates
    }
    return standard_data
```

> **[Note]** 지금까지 따로 만들었던 명사 추출, 키워드 추출, 문장 추출, 필터링 함수를 하나의 analyze_document 함수로 통합합니다. 이렇게 하나의 함수로 정리해두면, 이후 실습에서 원문을 입력하기만 해도 NLP 분석 결과가 자동으로 표준 데이터에 채워집니다.

> **[수정] 호출부 정정**: `extract_keywords_tfidf`는 (앞서 수정한 대로) 명사 목록이 아니라 원문 텍스트를 직접 받아 내부에서 문장 분리·명사 추출까지 수행하므로 `extract_keywords_tfidf(raw_text)`로 호출합니다. 반환값이 `(단어, 점수)` 튜플 목록이므로 키워드 문자열만 필요하면 `[w for w, _ in ...]`로 추립니다.

---

### 페이지 21. 3차시 정리와 4차시 예고

3차시 핵심 요약

- 형태소 분석으로 명사를 추출하고, TF-IDF로 핵심 키워드에 점수를 매김
- TextRank로 문서 내 가장 중요한 문장을 원문 그대로 추출
- 키워드와 주요 문장을 결합하여 규칙 기반 주제 요약 결과를 표준 데이터에 저장

> **[Note]** 이번 시간에는 규칙과 통계에 기반한 전통적인 NLP 기법으로 키워드와 주요 문장을 뽑아내는 방법을 배웠습니다. 다음 4차시에서는 이렇게 정리된 결과를 참고 자료로 삼아, 생성형 AI(LLM)가 훨씬 자연스러운 문장으로 요약문을 작성하도록 프롬프트를 설계하는 방법을 배웁니다.
