# 관찰 Ch03
import sys, json
sys.path.insert(0, ".")
from kiwipiepy import Kiwi
from sklearn.feature_extraction.text import TfidfVectorizer
from mywork.nlp import extract_nouns, split_sentences, extract_keywords_tfidf

with open("mywork/press_data.json", encoding="utf-8") as f:
    text = json.load(f)["원문"]

# ① 사용자 사전이 없으면 복합명사가 쪼개진다
기본 = Kiwi()
print("① 사전 없음:", [t.form for t in 기본.tokenize("온라인쇼핑 거래액") if t.tag.startswith("NN")])
print("① 사전 등록:", extract_nouns("온라인쇼핑 거래액"))

# ② 원문 전체를 문서 1건으로 넣으면 → 점수가 단순 빈도와 같아진다
v = TfidfVectorizer()
m = v.fit_transform([" ".join(extract_nouns(text))])
점수 = sorted(zip(v.get_feature_names_out(), m.toarray()[0]), key=lambda x: -x[1])[:4]
print("② 문서 1건:", [(str(w), round(float(s), 3)) for w, s in 점수])

# ③ 문장 단위로 나누면 → 특정 문장에만 나오는 단어가 높아지고, 여러 문장에 나오는 '거래액'은 낮아진다
for i, s in enumerate(split_sentences(text), 1):
    print(f"③ 문장{i}:", extract_nouns(s))
print("③ 문장 단위 상위 8:", extract_keywords_tfidf(text, top_n=8))
