"""3차시: 키워드 추출, 주요 문장 추출, 문서 주제 요약."""
import re

import networkx as nx
from kiwipiepy import Kiwi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_kiwi = Kiwi()  # 형태소 분석기는 초기화 비용이 크므로 모듈 전역에서 한 번만 생성

# 실제 실행 결과, 기본 사전만으로는 "온라인쇼핑"이 "온라인"+"쇼핑"으로 분리되어
# 보도자료 핵심 소재가 쪼개지는 문제가 확인되었다. 도메인 복합명사는 사용자 사전에
# 등록해 하나의 명사로 유지한다.
for _word in ["온라인쇼핑", "모바일쇼핑", "거래액", "역대급"]:
    _kiwi.add_user_word(_word, "NNP", 0.0)

STOPWORDS = {"등", "및", "수", "것"}


def extract_nouns(text: str) -> list:
    """텍스트에서 명사(NNG, NNP 등 'NN'으로 시작하는 품사 태그)만 추출한다."""
    return [token.form for token in _kiwi.tokenize(text) if token.tag.startswith("NN")]


def clean_keywords(keyword_scores, top_n: int = 5) -> list:
    """불용어·한 글자 단어를 제외하고 상위 top_n개만 남긴다."""
    filtered = [(w, s) for w, s in keyword_scores if w not in STOPWORDS and len(w) > 1]
    return sorted(filtered, key=lambda x: -x[1])[:top_n]


def split_sentences(text: str) -> list:
    """마침표/느낌표/물음표 뒤 공백을 기준으로 문장을 분리한다."""
    text = text.strip()
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


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
    max_scores = tfidf_matrix.toarray().max(axis=0)

    keyword_scores = list(zip(terms, max_scores))
    return clean_keywords(keyword_scores, top_n=top_n)


def extract_main_sentences(sentences: list, ratio: float = 0.5) -> list:
    """문장 간 코사인 유사도 그래프에 PageRank를 적용해 주요 문장을 원문 순서 그대로 반환한다."""
    if len(sentences) <= 1:
        return sentences

    noun_docs = [" ".join(extract_nouns(s)) or s for s in sentences]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(noun_docs)
    similarity_matrix = cosine_similarity(tfidf_matrix)
    for i in range(len(similarity_matrix)):
        similarity_matrix[i, i] = 0  # 자기 자신과의 유사도(대각선=1.0) 제거로 self-loop 왜곡 방지

    graph = nx.from_numpy_array(similarity_matrix)
    scores = nx.pagerank(graph)

    top_n = max(1, round(len(sentences) * ratio))
    ranked_idx = sorted(scores, key=scores.get, reverse=True)[:top_n]
    selected_idx = sorted(ranked_idx)  # 원문 순서로 재정렬
    return [sentences[i] for i in selected_idx]


def filter_sentences_by_keywords(sentences: list, keywords: list) -> list:
    keyword_set = set(keywords)
    result = []
    for sentence in sentences:
        if any(keyword in sentence for keyword in keyword_set):
            result.append(sentence)
    return result


def analyze_document(raw_text: str, standard_data: dict) -> dict:
    keywords = [w for w, _ in extract_keywords_tfidf(raw_text)]
    sentences = split_sentences(raw_text)
    main_sentences = extract_main_sentences(sentences)
    summary_candidates = filter_sentences_by_keywords(main_sentences, keywords)

    standard_data["NLP분석결과"] = {
        "핵심키워드": keywords,
        "주요문장": summary_candidates,
    }
    return standard_data
