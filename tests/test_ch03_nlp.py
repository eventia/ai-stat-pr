from modules.nlp import (
    analyze_document,
    extract_keywords_tfidf,
    extract_main_sentences,
    extract_nouns,
    filter_sentences_by_keywords,
    split_sentences,
)


def test_extract_nouns_returns_only_nouns():
    text = "온라인쇼핑 거래액은 전월 대비 1.5% 증가하였다."
    nouns = extract_nouns(text)
    assert "온라인쇼핑" in nouns
    assert "거래액" in nouns
    # 조사/어미는 명사가 아니므로 포함되지 않아야 한다
    assert "증가하였다" not in nouns


def test_split_sentences_splits_on_punctuation():
    text = "첫 번째 문장이다. 두 번째 문장이다! 세 번째 문장인가?"
    sentences = split_sentences(text)
    assert len(sentences) == 3


def test_extract_keywords_tfidf_finds_domain_keywords(sample_data):
    keyword_scores = extract_keywords_tfidf(sample_data["원문"], top_n=5)
    keywords = [w for w, _ in keyword_scores]
    assert "온라인쇼핑" in keywords or "거래액" in keywords
    assert len(keywords) <= 5


def test_extract_main_sentences_preserves_original_order(sample_data):
    sentences = split_sentences(sample_data["원문"])
    main = extract_main_sentences(sentences, ratio=0.5)
    assert len(main) >= 1
    # 반환된 문장들이 실제로 원문에 존재해야 한다 (새로 생성하지 않음)
    for s in main:
        assert s in sentences
    # 원문 순서를 유지해야 한다
    indices = [sentences.index(s) for s in main]
    assert indices == sorted(indices)


def test_filter_sentences_by_keywords():
    sentences = ["온라인쇼핑 거래액은 201,250억 원으로 증가하였다.", "이는 역대 최대치이다."]
    keywords = ["온라인쇼핑", "거래액", "최대"]
    result = filter_sentences_by_keywords(sentences, keywords)
    assert len(result) == 2


def test_analyze_document_fills_nlp_result_field(sample_data):
    result = analyze_document(sample_data["원문"], sample_data)
    assert "NLP분석결과" in result
    assert len(result["NLP분석결과"]["핵심키워드"]) > 0
    assert len(result["NLP분석결과"]["주요문장"]) > 0
    # 주요문장은 원문에서 그대로 추출된 것이어야 한다
    original_sentences = split_sentences(sample_data["원문"])
    for s in result["NLP분석결과"]["주요문장"]:
        assert s in original_sentences
