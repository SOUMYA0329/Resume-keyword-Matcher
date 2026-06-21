"""
Extracts the most important skill/requirement keywords from a job
description using KeyBERT (keyword extraction via embeddings) layered
on top of spaCy for basic text cleanup and noun-phrase candidates.
"""

import re
import spacy
from keybert import KeyBERT

# Load once at import time - reused across every request.
_nlp = spacy.load("en_core_web_sm")
_kw_model = KeyBERT(model="all-MiniLM-L6-v2")

# Generic words that show up in every job post but carry no signal.
_STOPWORDS_EXTRA = {
    "team", "experience", "work", "role", "company", "ability",
    "skills", "years", "job", "candidate", "environment",
}


def _normalize(phrase: str) -> str:
    phrase = phrase.lower().strip()
    phrase = re.sub(r"[^a-z0-9\+\#\.\- ]", "", phrase)
    return phrase.strip()


def extract_keywords(text: str, top_n: int = 20) -> list[str]:
    """
    Return the top_n most relevant keyword/key-phrases from a job
    description, ranked by relevance (KeyBERT uses cosine similarity
    between the phrase embedding and the full-document embedding).
    """
    # KeyBERT extracts 1-3 word keyphrases and scores them.
    raw_keywords = _kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 3),
        stop_words="english",
        use_mmr=True,        # Maximal Marginal Relevance -> less redundant results
        diversity=0.6,
        top_n=top_n * 2,      # over-fetch, then filter down
    )

    cleaned = []
    seen = set()
    for phrase, score in raw_keywords:
        norm = _normalize(phrase)
        if not norm or norm in _STOPWORDS_EXTRA or len(norm) < 2:
            continue
        if norm in seen:
            continue
        seen.add(norm)
        cleaned.append(norm)
        if len(cleaned) >= top_n:
            break

    return cleaned


def extract_required_skills(text: str) -> list[str]:
    """
    A second pass focused specifically on the 'Requirements' /
    'Qualifications' section, since that's where the highest-signal
    skill keywords usually live.
    """
    section_match = re.search(
        r"(requirements|qualifications|what you.?ll need)(.*?)"
        r"(responsibilities|about us|benefits|$)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    section_text = section_match.group(2) if section_match else text

    doc = _nlp(section_text)
    noun_chunks = {chunk.text.lower().strip() for chunk in doc.noun_chunks}
    noun_chunks = {c for c in noun_chunks if 2 <= len(c) <= 40}

    return sorted(noun_chunks)


if __name__ == "__main__":
    sample_jd = """
    We are looking for a Data Scientist with strong experience in Python,
    SQL, and machine learning. Requirements: 3+ years experience with
    scikit-learn, pandas, and cloud platforms such as AWS or GCP.
    Experience with NLP and deep learning frameworks like PyTorch is a plus.
    """
    print(extract_keywords(sample_jd))