import difflib


def compute_similarity(text1, text2):
    return difflib.SequenceMatcher(None, text1, text2).ratio()
