"""3차시: 형태소 분석·TF-IDF·TextRank로 키워드와 주요 문장을 추출한다(생성형 AI 미사용)."""
import re

import networkx as nx
from kiwipiepy import Kiwi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_kiwi = Kiwi()
for _word in ["온라인쇼핑", "모바일쇼핑", "거래액", "역대급"]:
    _kiwi.add_user_word(_word, "NNP", 0.0)

STOPWORDS = {"등", "및", "수", "것"}


def extract_nouns(text: str) -> list:
    return [token.form for token in _kiwi.tokenize(text) if token.tag.startswith("NN")]


def split_sentences(text: str) -> list:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in sentences if s.strip()]


def clean_keywords(keyword_scores, top_n: int = 5) -> list:
    filtered = [(w, s) for w, s in keyword_scores if w not in STOPWORDS and len(w) > 1]
    return sorted(filtered, key=lambda x: -x[1])[:top_n]


def extract_keywords_tfidf(text: str, top_n: int = 5) -> list:
    sentences = split_sentences(text)
    noun_docs = [" ".join(extract_nouns(s)) for s in sentences]
    noun_docs = [doc for doc in noun_docs if doc.strip()]
    if not noun_docs:
        return []
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(noun_docs)
    terms = vectorizer.get_feature_names_out()
    max_scores = tfidf_matrix.toarray().max(axis=0)
    keyword_scores = [(str(t), round(float(s), 4)) for t, s in zip(terms, max_scores)]
    return clean_keywords(keyword_scores, top_n=top_n)


def extract_main_sentences(sentences: list, ratio: float = 0.5) -> list:
    if len(sentences) <= 1:
        return sentences
    noun_docs = [" ".join(extract_nouns(s)) or s for s in sentences]
    tfidf_matrix = TfidfVectorizer().fit_transform(noun_docs)
    similarity_matrix = cosine_similarity(tfidf_matrix)
    for i in range(len(similarity_matrix)):
        similarity_matrix[i, i] = 0
    scores = nx.pagerank(nx.from_numpy_array(similarity_matrix))
    top_n = max(1, round(len(sentences) * ratio))
    ranked_idx = sorted(scores, key=scores.get, reverse=True)[:top_n]
    return [sentences[i] for i in sorted(ranked_idx)]


def filter_sentences_by_keywords(sentences: list, keywords: list) -> list:
    keyword_set = set(keywords)
    return [s for s in sentences if any(k in s for k in keyword_set)]


def analyze_document(raw_text: str, standard_data: dict) -> dict:
    keywords = [w for w, _ in extract_keywords_tfidf(raw_text)]
    main_sentences = extract_main_sentences(split_sentences(raw_text))
    standard_data["NLP분석결과"] = {
        "핵심키워드": keywords,
        "주요문장": filter_sentences_by_keywords(main_sentences, keywords),
    }
    return standard_data
