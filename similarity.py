"""
Computes a semantic match score between a resume and a job description
using sentence embeddings (Sentence-BERT) - this is the key upgrade over
a plain keyword-overlap matcher, since it understands that "led a team
of 5 engineers" and "people management experience" are related ideas
even with zero shared words.
"""

import numpy as np
from sentence_transformers import SentenceTransformer

_model = SentenceTransformer("all-MiniLM-L6-v2")


def _cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    return float(
        np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b))
    )


def compute_match_score(resume_text: str, job_description: str) -> float:
    """
    Returns a 0-100 semantic match score between the resume and the
    job description.
    """
    embeddings = _model.encode([resume_text, job_description])
    raw_score = _cosine_similarity(embeddings[0], embeddings[1])

    # Cosine similarity for sentence embeddings typically falls in the
    # 0.2-0.9 range in practice, so we rescale to a friendlier 0-100 band.
    scaled = max(0.0, min(1.0, (raw_score - 0.2) / 0.6))
    return round(scaled * 100, 1)


def find_missing_keywords(resume_text: str, jd_keywords: list[str]) -> list[str]:
    """
    For each JD keyword, check whether it (or a close semantic match)
    appears in the resume. Returns the ones that don't.
    """
    resume_lower = resume_text.lower()
    missing = []

    # Pre-embed the resume once for the semantic fallback check.
    resume_embedding = _model.encode(resume_text)

    for keyword in jd_keywords:
        if keyword.lower() in resume_lower:
            continue  # exact substring match -> covered

        # Semantic fallback: is something *like* this keyword in the resume?
        keyword_embedding = _model.encode(keyword)
        similarity = _cosine_similarity(resume_embedding, keyword_embedding)

        if similarity < 0.35:  # below threshold -> treat as a real gap
            missing.append(keyword)

    return missing


if __name__ == "__main__":
    resume = "Built ML pipelines in Python using scikit-learn and pandas."
    jd = "Looking for a candidate skilled in Python, SQL, and AWS."
    keywords = ["python", "sql", "aws", "scikit-learn"]

    print("Match score:", compute_match_score(resume, jd))
    print("Missing keywords:", find_missing_keywords(resume, keywords))