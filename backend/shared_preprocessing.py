"""
Shared text preprocessing for resume NLP.
Used by BOTH the training pipeline AND the backend inference to guarantee
identical token-level transformations.  Import from here to prevent drift.
"""

import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download required NLTK data (idempotent — skips if already present).
# Wrap in try/except so a network-restricted host cannot crash the app.
for _res in ("stopwords", "wordnet", "omw-1.4"):
    try:
        nltk.download(_res, quiet=True)
    except Exception as _exc:
        print(f"NLTK download notice for '{_res}': {_exc}")

_stop_words = set(stopwords.words("english"))
_lemmatizer = WordNetLemmatizer()


def clean_resume_text(text: str) -> str:
    """
    Preprocess resume text exactly as done during TF-IDF training:
      1. Lowercase
      2. Remove URLs, emails, long digit strings
      3. Remove punctuation
      4. Collapse whitespace
      5. Remove NLTK stopwords
      6. Lemmatize each remaining token
    """
    if not text:
        return ""
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"\S+@\S+", " ", text)
    text = re.sub(r"\d{10,}", " ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()
    words = [_lemmatizer.lemmatize(w) for w in text.split() if w not in _stop_words]
    return " ".join(words)
