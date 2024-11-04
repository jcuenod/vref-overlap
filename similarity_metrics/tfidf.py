from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer(ngram_range=(1, 5))


def compute_similarity(text1, text2):
    X = vectorizer.fit_transform([text1, text2])
    return (X * X.T).A[0, 1]
