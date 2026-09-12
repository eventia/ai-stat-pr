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

# 페이지 05. 소주제 1. 키워드 추출 기능 구현

---

### 페이지 06. 3차시 학습 목표와 전체 흐름

이번에 다룰 내용들

- 키워드 추출: 문서에서 가장 중요한 단어를 골라내는 기능
- 주요 문장 추출: 문서에서 핵심을 담고 있는 문장을 골라내는 기능
- 문서 주제 요약: 키워드와 주요 문장을 결합해 짧은 요약을 만드는 기능
- 2차시에서 완성한 표준 입력 데이터(JSON)의 비정형 원문을 입력값으로 사용

> **[Note]** 이전 시간에 데이터를 정제하고 표준 구조로 담아내는 방법을 배웠습니다. 이번에는 그 표준 데이터 안에 들어있는 비정형 문장을 실제로 분석하여, 핵심 단어와 핵심 문장을 자동으로 뽑아내는 세 가지 NLP 기능을 직접 구현합니다. 여기서 말씀드릴 것이 있습니다. 오늘 만드는 키워드와 주요 문장 결과는 보도자료의 최종 숫자나 사실을 확정하는 데 쓰이는 것이 아니라, 이후에 추가할 기능에서 AI가 요약문을 쓸 때 참고할 보조 자료라는 점입니다. 실제 보도자료의 숫자와 특이사항은 이후 다를 규칙 기반 계산 결과가 담당하고, 이번에 배우는 내용은 그 숫자들을 뒷받침하는 역할을 합니다.

---

### 페이지 07. 키워드 추출의 원리, 단어가 얼마나 중요한지 점수 매기기

키워드 추출의 핵심 아이디어

- 문서 안에서 자주 등장하는 단어일수록 중요할 가능성이 높음
- 그러나 조사, 어미처럼 모든 문서에 흔히 등장하는 단어는 제외해야 함
- TF-IDF: 한 문서에서는 자주 나오지만, 다른 문서에서는 드물게 나오는 단어에 높은 점수를 부여하는 계산 방식

> **[Note]** 키워드 추출은 단순히 자주 나오는 단어를 세는 것이 아닙니다. "이", "그", "있다"처럼 모든 문서에 흔한 단어는 제외하고, 해당 문서의 특징적인 단어를 찾아내야 합니다. 이를 위해 TF-IDF라는 계산 방식을 사용합니다. TF-IDF는 Term Frequency, IDF 는 Inverse Document Frequency 로 , TF는 한 문서 안에서 단어가 얼마나 자주 나오는지를 보는 것이고, IDF는 그 단어가 여러 문서에서 얼마나 드물게 나오는지를 보는 것입니다. 이 둘을 곱하면, 이 문서에서는 자주 나오지만 다른 문서에서는 흔하지 않은 단어일수록 높은 점수를 받게 됩니다. 예를 들어 "것", "수" 같은 단어는 어느 문서에나 흔하므로 낮은 점수를 받고, "온라인쇼핑", "거래액" 같은 단어는 이 문서의 주제를 잘 드러내므로 높은 점수를 받게 되는 원리입니다.

---

### 페이지 08. 한국어 형태소 분석기로 명사만 골라내기

형태소 분석기 활용

- 한국어는 조사와 어미가 단어에 붙어 있어, 영어처럼 공백만으로 단어를 나누기 어려움
- 형태소 분석기(Kiwi, KoNLPy 등)를 사용해 문장을 의미 단위로 쪼갬
- 키워드 후보로는 대부분 명사(NNG, NNP)만 추출하여 사용

```python
from kiwipiepy import Kiwi

_kiwi = Kiwi()  # 형태소 분석기는 초기화 비용이 크므로 모듈 전역에서 한 번만 생성

# 도메인 복합명사("온라인쇼핑", "거래액" 등)가 문맥에 따라 "온라인"+"쇼핑",
# "거래"+"액"처럼 둘로 쪼개지는 경우가 있어, 사용자 사전에 등록해 하나의
# 명사로 고정한다.
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

> **[Note]** 한국어 문장에서 바로 키워드를 뽑으면 조사나 어미까지 함께 섞여 나옵니다. 한국어는 영어와 달리 띄어쓰기만으로 단어를 나눌 수 없기 때문에, 먼저 형태소 분석기로 문장을 의미 단위로 쪼갠 뒤, 그중에서 명사에 해당하는 품사만 골라내는 전처리 과정이 필요합니다. 여기서는 Kiwi라는 형태소 분석기를 사용합니다. 한 가지 실무 팁을 말씀드리면, "온라인쇼핑"이나 "거래액" 같은 우리 도메인 특유의 복합명사는 기본 사전만으로는 "온라인"과 "쇼핑", "거래"와 "액"처럼 둘로 쪼개지는 경우가 실제로 있습니다. 그래서 코드에서 보시는 것처럼 add_user_word 함수로 이런 단어들을 사용자 사전에 미리 등록해서 하나의 명사로 고정해 둡니다. 이렇게 만든 extract_nouns 함수는 이후 실습에서 원문 전체를 넘기기만 하면 바로 재사용할 수 있습니다.

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

> **[Note]** 방금 본 코드에서 서로 다른 보도자료 여러건을 놓고 비교하면 TF-IDF가 잘 동작합니다. 그런데 우리가 실제로 다루는 상황은 아마도 보도자료 원문 딱 1건뿐일 경우가 많을겁니다. 문서가 1건뿐이면 IDF, 즉 "다른 문서에서 얼마나 드문가"를 계산할 대상 자체가 없어서 모든 단어의 점수가 똑같아져 버립니다. 그래서 아래 두 번째 코드에 있는 extract_keywords_tfidf 함수는 조금 다른 전략을 쓰도록 구현했씁니다. 보도자료 한 편을 문장 단위로 쪼갠 뒤, 각 문장 하나하나를 마치 독립된 문서처럼 취급해서 TF-IDF를 계산하는 것입니다. 이렇게 하면 여러 문장에 고르게 등장하는 흔한 단어보다, 특정 문장에 집중적으로 등장하는 단어에 더 높은 점수를 줄 수 있습니다. 

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

> **[Note]** TF-IDF로 점수를 계산했다고 해도 그 결과를 그대로 쓰면 의미 없는 단어가 섞여 나올 수 있습니다. 그래서 후처리를 거칩니다. 첫째, "등", "및", "수"처럼 의미 없는 명사를 불용어 목록으로 관리해서 걸러냅니다. 둘째, 한 글자짜리 명사는 대부분 노이즈이기 때문에 제외합니다. 셋째, 실제 보도자료에는 5개에서 10개 내외의 핵심 키워드만 있으면 충분하므로 상위 개수를 제한합니다. 코드에서 보시는 clean_keywords 함수가 바로 이 세 가지를 한 번에 처리합니다.

---

# 페이지 11. 소주제 2. 주요 문장 추출 기능 구현

---

### 페이지 12. 주요 문장 추출이 필요한 이유

키워드만으로는 부족한 이유

- 키워드는 단어 단위 정보만 제공하여, 문맥이나 인과관계를 알 수 없음
- 보도자료 원문이 길 경우, 핵심 내용이 담긴 문장 자체를 골라내는 것이 효율적
- 주요 문장을 먼저 추출하면, 이후 요약이나 리드문 작성 시 근거 문장으로 활용 가능

> **[Note]** 지금까지 단어 단위로 키워드를 뽑았습니다. 하지만 키워드만으로는 문장의 맥락이나 인과관계까지는 알 수 없습니다. 예를 들어 "거래액"과 "증가"라는 키워드만 봐서는 정확히 어떤 문장 안에서 어떻게 연결되어 있는지 알기 어렵습니다. 그래서 원문이 여러 문장으로 구성되어 있을 때는, 문서 전체에서 가장 중요한 의미를 담고 있는 문장 자체를 통째로 골라내는 기법이 함께 필요합니다. 이렇게 뽑아낸 주요 문장은 이후 4차시의 요약문 작성이나 7차시의 리드문 작성에서 근거 문장으로 활용할 수 있습니다.

---

### 페이지 13. TextRank 알고리즘의 원리, 문장들의 인기 투표

TextRank 핵심 개념

- 문서 안의 모든 문장을 하나의 그래프의 노드(점)로 봄
- 문장과 문장 사이의 유사도를 계산하여 노드를 연결하는 선(엣지)의 굵기로 표현
- 다른 문장들과 유사한 내용을 많이 공유하는 문장일수록 중요한 문장으로 판단 (검색엔진의 페이지랭크 원리와 유사)

> **[Note]** 주요 문장을 뽑아내는 대표적인 알고리즘이 TextRank입니다. 이 알고리즘은 검색엔진이 웹페이지의 중요도를 계산하는 페이지랭크 원리를 문장 단위에 그대로 적용한 것입니다. 원리를 설명드리면, 문서 안의 모든 문장을 하나의 점(노드)으로 보고, 문장과 문장 사이의 유사도를 계산해서, 그 유사도만큼 굵은 선(엣지)으로 두 점을 연결하여 그래프를 만듭니다. 그러면 다른 여러 문장들과 유사한 내용, 즉 비슷한 단어를 많이 공유하는 문장일수록 그래프 안에서 굵은 선을 많이 가지게 되고, 이런 문장이 마치 여러 사람에게 자주 인용되는 유명한 문장처럼 중요도가 높다고 판단됩니다.

---

### 페이지 14. Python 코드, TextRank로 주요 문장 뽑아내기

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

> **[Note]** TextRank 원리를 실제 코드로 구현해 보았습니다. 참고로 한국어 요약에 자주 쓰이는 summa라는 라이브러리도 있지만, 이 라이브러리가 공식 지원하는 언어 목록에는 한국어가 포함되어 있지 않아서 여기서는 직접 구현하는 방식을 썼습니다. 오히려 이 방식이 앞서 배운 TF-IDF 개념과 자연스럽게 이어지기 때문에 이해하기도 쉽습니다. 코드를 보면, split_sentences 함수로 먼저 문장을 나누고, extract_main_sentences 함수에서 각 문장을 벡터화한 뒤 코사인 유사도로 문장 간 유사도 행렬을 만듭니다. 이때 자기 자신과의 유사도인 대각선 값은 0으로 지워서, 문장이 스스로에게만 연결되어 점수가 왜곡되는 것을 방지합니다. 이렇게 만든 유사도 행렬을 networkx의 pagerank 함수에 넣으면 각 문장의 중요도 점수가 나오고, 점수가 높은 상위 문장들을 골라내되 원문에 등장한 순서 그대로 반환하도록 만들었습니다. 순서를 원문 그대로 유지하는 이유는, 다음 페이지에서 배울 "원문과 정확히 일치하는가"라는 검증을 쉽게 하기 위해서입니다. 수학적인 내용을 이해하지 못하셔도 괜찮습니다. 생성형 AI가 사용하는 대표 모델인 트랜스포머의 기본원리와 유사한 방식으로 문장간 유사도를 검사한다고 이해하시면 됩니다.

---

### 페이지 15. 문장 추출 결과와 원본 대조 확인

추출 결과 검증

- 추출된 문장이 원문에 실제로 존재하는 문장인지 반드시 확인 (문장을 새로 생성하지 않고 원문에서 그대로 선택)
- 추출된 문장 안의 숫자가 원본 수치와 정확히 일치하는지 재확인
- 핵심 특이사항(역대 최대 등)을 담은 문장이 우선적으로 뽑혔는지 확인

> **[Note]** 여기서 강조할 것은 주요 문장 추출시 AI가 새로운 문장을 만들어내는 것이 아니라, 원문 안에 이미 존재하는 문장 중에서 그대로 골라 오는 방식을 사용하고 있다는 점입니다. 그래서 검증할 때도, 추출된 문장이 원문과 다름 없이 실제로 존재하는지, 그 문장 안의 숫자가 원본 수치와 일치하는지, 그리고 "역대 최대" 같은 핵심 특이사항을 담은 문장이 잘 뽑혔는지를 확인합니다. 이렇게 원문 그대로를 사용하는 방식이기 때문에, 적어도 이 단계에서는 환각 문제가 발생할 수 없도록 방지했다는 점이 이 기법의 큰 장점입니다.

---

# 페이지 16. 소주제 3. 문서 주제 요약 기능 구현

---

### 페이지 17. 문서 주제 요약이란, 키워드와 문장의 결합

주제 요약의 구성 방식

- 키워드 추출 결과 + 주요 문장 추출 결과를 결합하여 문서의 핵심을 짧게 정리
- 규칙 기반 요약: "핵심 키워드가 포함된 주요 문장"만 골라 순서대로 나열하는 방식
- 이 결과는 다음 차시(4차시)의 LLM 기반 요약에서 참고 자료로 활용됨

> **[Note]** 지금까지 키워드 추출과 주요 문장 추출을 각각 따로 만들었는데, 이번 소주제에서는 이 둘을 결합해 보겠습니다. 방식은 간단합니다. 앞서 TextRank로 뽑은 주요 문장들 중에서, 다시 한번 TF-IDF로 뽑은 핵심 키워드를 포함하고 있는 문장만 골라 순서대로 나열하는 것입니다. 이렇게 키워드 기준과 문장 기준을 이중으로 통과한 문장은 문서의 핵심 주제를 담고 있을 가능성이 매우 높습니다. 이 규칙 기반 요약 결과는 아직 AI를 전혀 사용하지 않고 순수하게 통계와 규칙만으로 만든 것이며, 다음 4차시에서 생성형 AI가 실제 요약문을 작성할 때 참고 자료로 활용하게 됩니다.

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

> **[Note]** 방금 설명한 필터링 방식을 코드로 구현한 것이 filter_sentences_by_keywords 함수입니다. TextRank로 추출한 주요 문장 목록을 하나씩 확인하면서, 그 문장 안에 핵심 키워드 중 하나라도 포함되어 있으면 결과 목록에 추가하는 방식입니다. 화면의 예시를 보시면, "온라인쇼핑", "거래액", "최대"라는 키워드를 기준으로 두 문장을 걸러보면 둘 다 이 키워드 중 하나 이상을 포함하고 있어서 모두 통과하는 것을 확인할 수 있습니다. 이렇게 이중으로 검증된 문장들이 바로 문서의 핵심 주제를 요약하는 후보 문장이 됩니다.

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

> **[Note]** 지금까지 만든 핵심키워드와 주요문장 결과를 2차시에서 만든 표준 데이터 구조에 새로운 필드로 추가합니다. 화면에 보시는 것처럼 "NLP분석결과"라는 이름표 아래에 핵심키워드와 주요문장을 함께 저장해두면, 이후 4차시부터 이어지는 모든 AI 작성 단계에서 이 데이터를 참고 자료로 꺼내 쓸 수 있게 됩니다. 이렇게 표준 구조 안에 차곡차곡 필드를 쌓아가는 방식이, 앞으로 우리가 10차시까지 계속 반복하게 될 데이터 흐름의 기본 패턴이라는 것을 기억해 주세요.

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

> **[Note]** 마지막으로, 오늘 배운 명사 추출, 키워드 추출, 문장 추출, 필터링 기능을 하나의 analyze_document라는 통합 함수로 묶어보겠습니다. 이 함수는 원문 텍스트와 표준 데이터를 입력받아서, 내부적으로 extract_keywords_tfidf로 키워드를 뽑고, split_sentences와 extract_main_sentences로 주요 문장을 뽑고, filter_sentences_by_keywords로 최종 필터링까지 순서대로 실행한 뒤, 그 결과를 표준 데이터의 NLP분석결과 필드에 채워 넣습니다. 이렇게 하나의 함수로 정리해두면, 이후 실습에서는 원문 텍스트 하나만 이 함수에 넘겨도 세 가지 분석이 한 번에 자동으로 처리됩니다. 이 함수가 바로 10차시에서 완성할 전체 자동화 파이프라인의 두 번째 부품이 됩니다.

---

### 페이지 21. 3차시 정리와 4차시 예고

3차시 핵심 요약

- 형태소 분석으로 명사를 추출하고, TF-IDF로 핵심 키워드에 점수를 매김
- TextRank로 문서 내 가장 중요한 문장을 원문 그대로 추출
- 키워드와 주요 문장을 결합하여 규칙 기반 주제 요약 결과를 표준 데이터에 저장

> **[Note]** 오늘 배운 내용을 정리하면 이렇습니다. 형태소 분석으로 문장에서 명사만 뽑아내고, TF-IDF로 그 명사들에 중요도 점수를 매겨 핵심 키워드를 찾았습니다. 그다음 TextRank 알고리즘으로 문서 안에서 가장 중요한 문장을 원문 그대로, 새로 만들지 않고 추출했습니다. 마지막으로 이 키워드와 주요 문장을 결합해서 규칙 기반의 주제 요약 결과를 표준 데이터에 저장했습니다. 이 모든 과정은 아직 생성형 AI를 전혀 쓰지 않고, 순수하게 통계적 규칙만으로 이루어졌다는 점이 오늘의 핵심입니다. 다음 4차시에서는 이렇게 정리된 결과를 참고 자료로 삼아서, 생성형 AI, 즉 LLM이 훨씬 자연스러운 문장으로 요약문을 작성하도록 프롬프트를 설계하는 방법을 배우겠습니다.
